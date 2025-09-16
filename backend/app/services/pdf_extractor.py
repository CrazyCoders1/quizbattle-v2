"""
Advanced PDF Question Extraction with AI Integration
Supports multiple AI providers with fallback to regex
Now includes OpenRouter integration for multiple models
"""
import re
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from flask import current_app
import requests

# Import OpenRouter integration
from .openrouter_pdf_extractor import get_openrouter_extractor


class AIProvider:
    """Base class for AI providers"""
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def extract_questions(self, text: str, exam_type: str, difficulty_mode: str) -> Optional[List[Dict]]:
        raise NotImplementedError


class DeepSeekProvider(AIProvider):
    """DeepSeek API integration"""
    
    def extract_questions(self, text: str, exam_type: str, difficulty_mode: str) -> Optional[List[Dict]]:
        try:
            current_app.logger.info("🤖 Trying DeepSeek API for question extraction")
            
            prompt = self._create_extraction_prompt(text, exam_type, difficulty_mode)
            
            response = requests.post(
                'https://api.deepseek.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'deepseek-chat',
                    'messages': [{'role': 'user', 'content': prompt}],
                    'max_tokens': 4000,
                    'temperature': 0.1
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                questions = self._parse_ai_response(result['choices'][0]['message']['content'])
                current_app.logger.info(f"✅ DeepSeek extracted {len(questions)} questions")
                return questions
            else:
                current_app.logger.warning(f"⚠️ DeepSeek API error: {response.status_code}")
                return None
                
        except Exception as e:
            current_app.logger.error(f"❌ DeepSeek error: {str(e)}")
            return None
    
    def _create_extraction_prompt(self, text: str, exam_type: str, difficulty_mode: str) -> str:
        return f"""
Extract multiple choice questions from the following {exam_type} exam content.
Difficulty preference: {difficulty_mode}

IMPORTANT: Return ONLY valid JSON array format:
[
    {{
        "question": "Question text here",
        "options": ["Option A", "Option B", "Option C", "Option D"],
        "correct_answer": 0,
        "difficulty": "easy|tough",
        "has_image": false,
        "image_description": null
    }}
]

Rules:
1. Extract questions in both Format A (Question→Options→Answer) and Format B (Questions+Options first, Answers later)
2. For Format B, map answers correctly to questions by position
3. Mark questions with images as "tough", text-only as "easy"
4. If image is mentioned as [image: filename], set has_image=true and describe it
5. Only include well-formed questions with exactly 4 options
6. Maximum 20 questions per response

Text content (first 3000 chars):
{text[:3000]}
"""
    
    def _parse_ai_response(self, response_text: str) -> List[Dict]:
        try:
            # Try to extract JSON from response
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1
            
            if json_start != -1 and json_end != -1:
                json_text = response_text[json_start:json_end]
                questions = json.loads(json_text)
                
                # Validate and clean questions
                validated_questions = []
                for q in questions:
                    if self._validate_question(q):
                        validated_questions.append(q)
                
                return validated_questions
                
        except Exception as e:
            current_app.logger.error(f"Failed to parse AI response: {str(e)}")
        
        return []
    
    def _validate_question(self, question: Dict) -> bool:
        required_keys = ['question', 'options', 'correct_answer', 'difficulty']
        if not all(key in question for key in required_keys):
            return False
        
        if len(question['options']) != 4:
            return False
        
        if not (0 <= question['correct_answer'] <= 3):
            return False
        
        return True


class SambaCloudProvider(AIProvider):
    """SambaCloud API integration"""
    
    def extract_questions(self, text: str, exam_type: str, difficulty_mode: str) -> Optional[List[Dict]]:
        try:
            current_app.logger.info("🌩️ Trying SambaCloud API for question extraction")
            
            prompt = f"""Extract quiz questions from this {exam_type} content. Return JSON format with questions, options, and correct answers. Difficulty: {difficulty_mode}
            
Content: {text[:2000]}"""
            
            response = requests.post(
                'https://api.sambanova.ai/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'Meta-Llama-3.1-8B-Instruct',
                    'messages': [{'role': 'user', 'content': prompt}],
                    'max_tokens': 3000,
                    'temperature': 0.2
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                # Parse SambaCloud response (similar to DeepSeek)
                questions = self._parse_simple_response(result['choices'][0]['message']['content'])
                current_app.logger.info(f"✅ SambaCloud extracted {len(questions)} questions")
                return questions
            else:
                current_app.logger.warning(f"⚠️ SambaCloud API error: {response.status_code}")
                return None
                
        except Exception as e:
            current_app.logger.error(f"❌ SambaCloud error: {str(e)}")
            return None
    
    def _parse_simple_response(self, response_text: str) -> List[Dict]:
        # Enhanced parser for SambaCloud responses
        questions = []
        current_app.logger.info(f"🔍 Parsing SambaCloud response: {response_text[:200]}...")
        
        try:
            # Look for JSON patterns in markdown code blocks or direct JSON
            json_patterns = [
                r'```json\s*([\s\S]*?)\s*```',  # JSON in markdown code blocks
                r'\[\s*\{[\s\S]*?\}\s*\]',      # Direct JSON array
            ]
            
            json_text = None
            for pattern in json_patterns:
                import re
                match = re.search(pattern, response_text)
                if match:
                    json_text = match.group(1) if pattern.startswith(r'```') else match.group(0)
                    break
            
            if json_text:
                current_app.logger.info(f"📝 Found JSON: {json_text[:100]}...")
                parsed = json.loads(json_text)
                
                if isinstance(parsed, list):
                    for item in parsed:
                        if isinstance(item, dict) and 'question' in item:
                            # Convert SambaCloud format to our format
                            question_obj = {
                                'question': item['question'],
                                'options': [],
                                'correct_answer': 0,  # Default
                                'difficulty': 'tough',  # SambaCloud questions are tough
                                'has_image': False,
                                'extraction_method': 'sambacloud_ai'
                            }
                            
                            # Extract options from different possible formats
                            options = item.get('options', [])
                            if isinstance(options, list):
                                if all(isinstance(opt, dict) for opt in options):
                                    # Format: [{"A": "option1"}, {"B": "option2"}]
                                    question_obj['options'] = [list(opt.values())[0] for opt in options]
                                else:
                                    # Format: ["option1", "option2"]
                                    question_obj['options'] = options
                            
                            # Only add if we have 4 options
                            if len(question_obj['options']) == 4:
                                questions.append(question_obj)
                                current_app.logger.info(f"✅ Parsed question: {question_obj['question'][:50]}...")
                            else:
                                current_app.logger.warning(f"⚠️ Skipping question with {len(question_obj['options'])} options")
                
                current_app.logger.info(f"📊 SambaCloud parsed {len(questions)} questions")
            else:
                current_app.logger.warning("⚠️ No JSON found in SambaCloud response")
                
        except json.JSONDecodeError as e:
            current_app.logger.error(f"❌ JSON decode error: {e}")
        except Exception as e:
            current_app.logger.error(f"❌ SambaCloud parsing error: {e}")
        
        return questions


class OpenAIProvider(AIProvider):
    """OpenAI GPT integration"""
    
    def extract_questions(self, text: str, exam_type: str, difficulty_mode: str) -> Optional[List[Dict]]:
        try:
            current_app.logger.info("🤖 Trying OpenAI API for question extraction")
            
            prompt = f"""Extract multiple choice questions from this {exam_type} exam content.

Return only valid JSON array:
[{{"question": "text", "options": ["A", "B", "C", "D"], "correct_answer": 0, "difficulty": "easy"}}]

Content: {text[:2500]}"""
            
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'gpt-3.5-turbo',
                    'messages': [{'role': 'user', 'content': prompt}],
                    'max_tokens': 3000,
                    'temperature': 0.1
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                questions = self._parse_openai_response(result['choices'][0]['message']['content'])
                current_app.logger.info(f"✅ OpenAI extracted {len(questions)} questions")
                return questions
            else:
                current_app.logger.warning(f"⚠️ OpenAI API error: {response.status_code}")
                return None
                
        except Exception as e:
            current_app.logger.error(f"❌ OpenAI error: {str(e)}")
            return None
    
    def _parse_openai_response(self, response_text: str) -> List[Dict]:
        try:
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1
            
            if json_start != -1 and json_end != -1:
                json_text = response_text[json_start:json_end]
                return json.loads(json_text)
        except:
            pass
        
        return []


class LLaVAProvider(AIProvider):
    """LLaVA API integration for image-heavy content"""
    
    def extract_questions(self, text: str, exam_type: str, difficulty_mode: str) -> Optional[List[Dict]]:
        try:
            current_app.logger.info("👁️ Trying LLaVA API for question extraction")
            
            # LLaVA would be used for image processing
            # For now, return None to fallback to regex
            return None
            
        except Exception as e:
            current_app.logger.error(f"❌ LLaVA error: {str(e)}")
            return None


class PDFQuestionExtractor:
    """Main PDF question extraction service"""
    
    def __init__(self, api_keys_file: str = None):
        self.api_keys = self._load_api_keys(api_keys_file)
        self.providers = []
        self._initialize_providers()
    
    def _load_api_keys(self, api_keys_file: str) -> Dict[str, str]:
        """Load API keys from environment variables or file"""
        keys = {}
        
        # First try environment variables (production-safe)
        import os
        env_keys = {
            'DeepSeek': os.environ.get('DEEPSEEK_API_KEY'),
            'SambaCloud': os.environ.get('SAMBACLOUD_API_KEY'),
            'OpenAI': os.environ.get('OPENAI_API_KEY'),
            'LLAVA': os.environ.get('LLAVA_API_KEY'),
            'OpenRouter': os.environ.get('OPENROUTER_API_KEY')
        }
        
        # Add environment keys if they exist
        for key, value in env_keys.items():
            if value and value.strip():
                keys[key] = value.strip()
                if current_app:
                    current_app.logger.info(f"✅ Loaded {key} API key from environment")
        
        # If no environment keys found, try file fallback
        if not keys and api_keys_file:
            try:
                if api_keys_file is None:
                    # Default to backend directory
                    api_keys_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'api_keys.txt')
                
                if current_app:
                    current_app.logger.info(f"🔑 Loading API keys from file: {api_keys_file}")
                
                if os.path.exists(api_keys_file):
                    with open(api_keys_file, 'r') as f:
                        for line in f:
                            line = line.strip()
                            if '=' in line and not line.startswith('#'):
                                key, value = line.split('=', 1)
                                keys[key.strip()] = value.strip()
                    
                    if current_app:
                        current_app.logger.info(f"✅ Loaded {len(keys)} API keys from file")
                else:
                    if current_app:
                        current_app.logger.warning(f"⚠️ API keys file not found: {api_keys_file}")
                        
            except Exception as e:
                if current_app:
                    current_app.logger.error(f"❌ Error loading API keys from file: {str(e)}")
        
        # Log final status
        if keys:
            if current_app:
                current_app.logger.info(f"✅ Total API keys loaded: {len(keys)} providers available")
        else:
            if current_app:
                current_app.logger.warning("⚠️ No API keys found - will use regex fallback only")
        
        return keys
    
    def _initialize_providers(self):
        """Initialize AI providers in order of preference"""
        provider_configs = [
            ('DeepSeek', DeepSeekProvider),
            ('SambaCloud', SambaCloudProvider), 
            ('OpenAI', OpenAIProvider),
            ('LLAVA', LLaVAProvider)
        ]
        
        for name, provider_class in provider_configs:
            if name in self.api_keys:
                try:
                    provider = provider_class(self.api_keys[name])
                    self.providers.append((name, provider))
                    if current_app:
                        current_app.logger.info(f"✅ Initialized {name} provider")
                    else:
                        print(f"✅ Initialized {name} provider")
                except Exception as e:
                    if current_app:
                        current_app.logger.warning(f"⚠️ Failed to initialize {name}: {str(e)}")
                    else:
                        print(f"⚠️ Failed to initialize {name}: {str(e)}")
    
    def extract_questions_from_text(self, text: str, exam_type: str, difficulty_mode: str = 'mixed') -> List[Dict]:
        """Extract questions using AI providers with fallback to regex"""
        current_app.logger.info(f"📄 Starting question extraction: {len(text)} chars, exam_type={exam_type}, mode={difficulty_mode}")
        
        # Generate session ID for tracking
        import uuid
        session_id = str(uuid.uuid4())[:8]
        current_app._extraction_session_id = session_id
        current_app.logger.info(f"🔍 Extraction session ID: {session_id}")
        
        # Detect PDF format
        pdf_format = self._detect_pdf_format(text)
        current_app.logger.info(f"📋 Detected PDF format: {pdf_format}")
        
        # 1. Try OpenRouter first (all models with single API key)
        try:
            current_app.logger.info("🚀 Trying OpenRouter with multiple AI models...")
            openrouter_extractor = get_openrouter_extractor()
            questions = openrouter_extractor.extract_questions_from_text(text, exam_type, difficulty_mode)
            
            if questions and len(questions) > 0:
                current_app.logger.info(f"✅ OpenRouter succeeded: {len(questions)} questions extracted")
                self._log_extraction('OpenRouter_Multi_Model', len(questions), exam_type, True, None, difficulty_mode)
                return questions
            else:
                current_app.logger.warning("⚠️ OpenRouter returned no questions, trying individual providers...")
                
        except Exception as e:
            current_app.logger.error(f"❌ OpenRouter failed: {str(e)}")
            self._log_extraction('OpenRouter_Multi_Model', 0, exam_type, False, str(e), difficulty_mode)
        
        # 2. Try individual AI providers in order (fallback from original system)
        for provider_name, provider in self.providers:
            try:
                current_app.logger.info(f"🤖 Trying {provider_name} for extraction...")
                questions = provider.extract_questions(text, exam_type, difficulty_mode)
                
                if questions and len(questions) > 0:
                    # Apply difficulty filtering
                    filtered_questions = self._apply_difficulty_rules(questions, difficulty_mode)
                    current_app.logger.info(f"✅ {provider_name} extracted {len(filtered_questions)} questions")
                    
                    # Log to MongoDB
                    self._log_extraction(provider_name, len(filtered_questions), exam_type, True, None, difficulty_mode)
                    
                    return filtered_questions
                    
            except Exception as e:
                current_app.logger.error(f"❌ {provider_name} failed: {str(e)}")
                self._log_extraction(provider_name, 0, exam_type, False, str(e), difficulty_mode)
        
        # 3. Final fallback to regex
        current_app.logger.info("🔄 All AI providers failed, falling back to regex extraction")
        questions = self._extract_with_regex(text, exam_type, difficulty_mode, pdf_format)
        
        self._log_extraction('Regex_Fallback', len(questions), exam_type, True, None, difficulty_mode)
        
        return questions
    
    def _detect_pdf_format(self, text: str) -> str:
        """Detect if PDF is Format A or Format B"""
        # Format A: Questions with immediate options
        format_a_pattern = r'(?i)(question|q\.?\s*\d+).*?\n.*?[abcd][.):]'
        
        # Format B: Questions first, then answers section
        format_b_indicators = [
            'answer key', 'answers:', 'correct answers', 'solution:',
            'answer sheet', 'marking scheme'
        ]
        
        format_a_matches = len(re.findall(format_a_pattern, text, re.MULTILINE))
        format_b_matches = sum(1 for indicator in format_b_indicators if indicator in text.lower())
        
        if format_a_matches > format_b_matches:
            return 'Format_A'
        elif format_b_matches > 0:
            return 'Format_B'
        else:
            return 'Unknown'
    
    def _extract_with_regex(self, text: str, exam_type: str, difficulty_mode: str, pdf_format: str) -> List[Dict]:
        """Enhanced regex extraction supporting both PDF formats"""
        questions = []
        
        if pdf_format == 'Format_A':
            questions = self._extract_format_a(text, exam_type, difficulty_mode)
        elif pdf_format == 'Format_B':
            questions = self._extract_format_b(text, exam_type, difficulty_mode)
        else:
            # Try both formats
            questions_a = self._extract_format_a(text, exam_type, difficulty_mode)
            questions_b = self._extract_format_b(text, exam_type, difficulty_mode)
            questions = questions_a if len(questions_a) >= len(questions_b) else questions_b
        
        current_app.logger.info(f"📝 Regex extraction completed: {len(questions)} questions from {pdf_format}")
        return questions
    
    def _extract_format_a(self, text: str, exam_type: str, difficulty_mode: str) -> List[Dict]:
        """Extract Format A: Question → Options → Answer"""
        questions = []
        
        # Enhanced regex patterns for Format A
        patterns = [
            # Pattern 1: Question N. text \n A) option \n B) option...
            r'(?:Question\s*(\d+)[.:]?\s*)?([^\n]+(?:\n[^\n]+)*?)\n\s*[Aa][.):]?\s*([^\n]+)\n\s*[Bb][.):]?\s*([^\n]+)\n\s*[Cc][.):]?\s*([^\n]+)\n\s*[Dd][.):]?\s*([^\n]+)',
            
            # Pattern 2: N. text \n (A) option \n (B) option...
            r'(\d+\.\s*[^\n]+(?:\n[^\n]+)*?)\n\s*\([Aa]\)\s*([^\n]+)\n\s*\([Bb]\)\s*([^\n]+)\n\s*\([Cc]\)\s*([^\n]+)\n\s*\([Dd]\)\s*([^\n]+)',
            
            # Pattern 3: Question? \n A. option \n B. option...  
            r'([^\n]+\?)\n\s*[Aa]\.?\s*([^\n]+)\n\s*[Bb]\.?\s*([^\n]+)\n\s*[Cc]\.?\s*([^\n]+)\n\s*[Dd]\.?\s*([^\n]+)'
        ]
        
        for pattern_idx, pattern in enumerate(patterns):
            matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
            
            for match in matches:
                try:
                    question_data = self._parse_format_a_match(match, exam_type, difficulty_mode)
                    if question_data:
                        questions.append(question_data)
                        
                    # Limit questions
                    if len(questions) >= 30:
                        break
                        
                except Exception as e:
                    current_app.logger.debug(f"Error parsing match: {str(e)}")
                    
            if len(questions) >= 30:
                break
        
        return questions
    
    def _parse_format_a_match(self, match, exam_type: str, difficulty_mode: str) -> Optional[Dict]:
        """Parse a regex match from Format A"""
        groups = match.groups()
        
        # Extract question text and options based on match pattern
        if len(groups) == 6:  # Full format with question number
            question_text = groups[1].strip()
            options = [groups[j].strip() for j in range(2, 6)]
        elif len(groups) == 5:  # Format without explicit question number
            question_text = groups[0].strip()
            options = [groups[j].strip() for j in range(1, 5)]
        else:
            return None
        
        # Validate
        if len(question_text) < 10 or len(options) != 4:
            return None
        
        if any(len(opt) < 2 for opt in options):
            return None
        
        # Classify difficulty
        difficulty = self._classify_question_difficulty(question_text, difficulty_mode)
        
        # Apply filtering rules
        if not self._should_include_question(question_text, difficulty, difficulty_mode):
            return None
        
        # Generate hint for tough questions
        hint = None
        if difficulty == 'tough':
            hint = self._generate_hint(question_text)
        
        # Default answer (would need answer extraction in practice)
        correct_answer = 0
        
        return {
            'question': question_text,
            'options': options,
            'correct_answer': correct_answer,
            'difficulty': difficulty,
            'exam_type': exam_type,
            'hint': hint,
            'has_image': '[image:' in question_text.lower(),
            'image_description': None,
            'extraction_method': 'regex_format_a'
        }
    
    def _extract_format_b(self, text: str, exam_type: str, difficulty_mode: str) -> List[Dict]:
        """Extract Format B: Questions first, answers later"""
        questions = []
        
        try:
            # Split text into questions section and answers section
            answer_keywords = ['answer key', 'answers:', 'correct answers', 'solution:', 'answer sheet']
            
            split_point = -1
            for keyword in answer_keywords:
                pos = text.lower().find(keyword)
                if pos != -1:
                    split_point = pos
                    break
            
            if split_point == -1:
                current_app.logger.warning("Could not find answer section in Format B")
                return []
            
            questions_section = text[:split_point]
            answers_section = text[split_point:]
            
            # Extract questions from questions section
            question_matches = self._extract_questions_only(questions_section)
            
            # Extract answers from answers section  
            answers = self._extract_answers_only(answers_section)
            
            # Map answers to questions
            questions = self._map_answers_to_questions(question_matches, answers, exam_type, difficulty_mode)
            
            current_app.logger.info(f"Format B: {len(question_matches)} questions, {len(answers)} answers, {len(questions)} mapped")
            
        except Exception as e:
            current_app.logger.error(f"Format B extraction error: {str(e)}")
        
        return questions
    
    def _extract_questions_only(self, text: str) -> List[Dict]:
        """Extract questions and options (without answers) from Format B"""
        questions = []
        
        # Pattern for questions with options
        pattern = r'(\d+\.?\s*[^\n]+(?:\n[^\n]*)*?)(?=\n\s*\d+\.|\Z)'
        matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            question_block = match.group(1).strip()
            
            # Extract question and options from block
            lines = [line.strip() for line in question_block.split('\n') if line.strip()]
            
            if len(lines) < 5:  # Need at least question + 4 options
                continue
            
            question_text = lines[0]
            options = []
            
            # Look for options marked with A, B, C, D
            for line in lines[1:]:
                if re.match(r'^[ABCD][.):]', line):
                    options.append(re.sub(r'^[ABCD][.):]\s*', '', line))
            
            if len(options) == 4:
                questions.append({
                    'question': question_text,
                    'options': options,
                    'question_number': len(questions) + 1
                })
        
        return questions
    
    def _extract_answers_only(self, text: str) -> List[int]:
        """Extract answer indices from Format B answer section"""
        answers = []
        
        # Look for patterns like "1. A", "2. B", etc.
        pattern = r'(\d+)[.):\s]*([ABCD])'
        matches = re.finditer(pattern, text)
        
        answer_map = {'A': 0, 'B': 1, 'C': 2, 'D': 3}
        
        for match in matches:
            question_num = int(match.group(1))
            answer_letter = match.group(2)
            answer_index = answer_map.get(answer_letter, 0)
            
            # Ensure answers list is long enough
            while len(answers) < question_num:
                answers.append(0)
            
            answers[question_num - 1] = answer_index
        
        return answers
    
    def _map_answers_to_questions(self, question_data: List[Dict], answers: List[int], exam_type: str, difficulty_mode: str) -> List[Dict]:
        """Map extracted answers to questions for Format B"""
        mapped_questions = []
        
        for i, q_data in enumerate(question_data):
            if i < len(answers):
                correct_answer = answers[i]
            else:
                correct_answer = 0  # Default if no answer found
            
            question_text = q_data['question']
            difficulty = self._classify_question_difficulty(question_text, difficulty_mode)
            
            if self._should_include_question(question_text, difficulty, difficulty_mode):
                hint = None
                if difficulty == 'tough':
                    hint = self._generate_hint(question_text)
                
                mapped_questions.append({
                    'question': question_text,
                    'options': q_data['options'],
                    'correct_answer': correct_answer,
                    'difficulty': difficulty,
                    'exam_type': exam_type,
                    'hint': hint,
                    'has_image': '[image:' in question_text.lower(),
                    'image_description': None,
                    'extraction_method': 'regex_format_b'
                })
        
        return mapped_questions
    
    def _apply_difficulty_rules(self, questions: List[Dict], difficulty_mode: str) -> List[Dict]:
        """Apply difficulty-based filtering rules"""
        filtered = []
        
        # First ensure all questions have difficulty classification
        for q in questions:
            if 'difficulty' not in q or not q['difficulty']:
                q['difficulty'] = self._classify_question_difficulty(q.get('question', ''), difficulty_mode)
        
        if difficulty_mode == 'easy':
            # Easy mode: prefer easy questions, exclude complex images
            filtered = [q for q in questions if not q.get('has_image', False)]
            # If we have too many, prefer easy ones
            if len(filtered) > 15:
                easy_questions = [q for q in filtered if q.get('difficulty') == 'easy']
                if len(easy_questions) >= 10:
                    filtered = easy_questions[:15]
        elif difficulty_mode == 'tough':
            # Tough mode: all questions, prefer tough ones
            filtered = questions
        elif difficulty_mode == 'mixed':
            # Mixed mode: 60% easy, 40% tough - but be flexible
            easy_questions = [q for q in questions if q.get('difficulty') == 'easy']
            tough_questions = [q for q in questions if q.get('difficulty') == 'tough']
            
            # Calculate 60/40 split but be flexible if we don't have enough of one type
            total_wanted = min(len(questions), 20)  # Limit total
            easy_count = max(1, int(total_wanted * 0.6))  # At least 1 easy
            tough_count = max(1, total_wanted - easy_count)  # At least 1 tough
            
            # Add easy questions first
            filtered.extend(easy_questions[:easy_count])
            
            # Add tough questions
            filtered.extend(tough_questions[:tough_count])
            
            # If we still have space and one category was insufficient, fill with the other
            remaining_space = total_wanted - len(filtered)
            if remaining_space > 0:
                if len(easy_questions) > easy_count:
                    filtered.extend(easy_questions[easy_count:easy_count + remaining_space])
                elif len(tough_questions) > tough_count:
                    filtered.extend(tough_questions[tough_count:tough_count + remaining_space])
        
        # If no questions passed filtering, return all questions (fallback)
        if not filtered:
            current_app.logger.warning(f"Difficulty filtering returned 0 questions, returning all {len(questions)} questions")
            filtered = questions
        
        return filtered[:30]  # Maximum 30 questions
    
    def _classify_question_difficulty(self, question_text: str, difficulty_mode: str) -> str:
        """Classify question difficulty"""
        if difficulty_mode in ['easy', 'tough']:
            return difficulty_mode
        
        # Smart classification for mixed mode
        text_lower = question_text.lower()
        
        # Tough indicators
        tough_keywords = [
            'calculate', 'derive', 'prove', 'analyze', 'evaluate', 
            'compare', 'explain why', 'determine', 'find the value',
            'solve for', 'show that', 'verify', 'demonstrate'
        ]
        
        # Easy indicators
        easy_keywords = [
            'what is', 'which of', 'identify', 'name', 'state',
            'define', 'list', 'choose', 'select'
        ]
        
        if any(keyword in text_lower for keyword in tough_keywords):
            return 'tough'
        elif any(keyword in text_lower for keyword in easy_keywords):
            return 'easy'
        else:
            return 'easy'  # Default
    
    def _should_include_question(self, question_text: str, difficulty: str, difficulty_mode: str) -> bool:
        """Determine if question should be included based on filtering rules"""
        has_complex_image = self._has_complex_image(question_text)
        
        if has_complex_image:
            # Skip unexplainable complex images
            return False
        
        return True
    
    def _has_complex_image(self, question_text: str) -> bool:
        """Check if question has complex unexplainable images"""
        complex_indicators = [
            'complex diagram', 'detailed figure', 'microscopic image',
            'x-ray', 'satellite image', 'complex circuit',
            'detailed map', 'molecular structure', 'complex graph',
            'microscopy', 'histology', 'radiograph'
        ]
        return any(indicator in question_text.lower() for indicator in complex_indicators)
    
    def _generate_hint(self, question_text: str) -> str:
        """Generate hint for tough questions"""
        text_lower = question_text.lower()
        
        if any(word in text_lower for word in ['calculate', 'compute', 'find']):
            return 'Remember to check units and use appropriate formulas.'
        elif any(word in text_lower for word in ['analyze', 'examine', 'evaluate']):
            return 'Break down the problem into smaller components.'
        elif any(word in text_lower for word in ['compare', 'contrast']):
            return 'Look for similarities and differences between the options.'
        elif any(word in text_lower for word in ['derive', 'prove', 'show']):
            return 'Start with fundamental principles and work step by step.'
        elif any(word in text_lower for word in ['physics', 'force', 'energy', 'motion']):
            return 'Apply relevant physics laws and conservation principles.'
        elif any(word in text_lower for word in ['chemistry', 'reaction', 'molecule', 'bond']):
            return 'Consider electronic structure and chemical bonding concepts.'
        elif any(word in text_lower for word in ['mathematics', 'equation', 'function']):
            return 'Use appropriate mathematical methods and check your work.'
        else:
            return 'Consider the key concepts and relationships involved.'
    
    def _log_extraction(self, provider: str, questions_count: int, exam_type: str, success: bool, error: str, difficulty_mode: str = 'mixed'):
        """Log extraction attempt to MongoDB"""
        try:
            log_entry = {
                'provider': provider,
                'questions_extracted': questions_count,
                'exam_type': exam_type,
                'difficulty_mode': difficulty_mode,
                'success': success,
                'error': error,
                'timestamp': datetime.utcnow(),
                'session_id': getattr(current_app, '_extraction_session_id', 'unknown'),
                'service': 'pdf_extractor'
            }
            
            if hasattr(current_app, 'mongo_db'):
                current_app.mongo_db.extraction_logs.insert_one(log_entry)
            else:
                current_app.logger.warning("MongoDB not available for logging")
            
        except Exception as e:
            current_app.logger.error(f"Failed to log extraction: {str(e)}")


# Global extractor instance
_extractor_instance = None

def get_extractor():
    """Get singleton extractor instance"""
    global _extractor_instance
    if _extractor_instance is None:
        _extractor_instance = PDFQuestionExtractor()
    return _extractor_instance