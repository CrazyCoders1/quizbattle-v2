"""
OpenRouter-based PDF Question Extraction with Multiple AI Models
Supports all available models through single OpenRouter API key
"""
import re
import json
import logging
import requests
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from flask import current_app


class OpenRouterExtractor:
    """OpenRouter API integration with multiple models and fallback"""
    
    # Model priority list - best free models first, then premium models
    MODELS = [
        # DeepSeek Models (excellent for code/text extraction)
        "deepseek/deepseek-r1",
        "deepseek/deepseek-chat",
        "deepseek/deepseek-coder",
        
        # Quen Models (strong multilingual capabilities)
        "qwen/qwen-2.5-72b-instruct",
        "qwen/qwen-2.5-32b-instruct", 
        "qwen/qwen-2.5-14b-instruct",
        "qwen/qwen-2.5-7b-instruct",
        "qwen/qwen-2.5-coder-32b-instruct",
        
        # Meta LLAMA Models (reliable general purpose)
        "meta-llama/llama-3.1-405b-instruct",
        "meta-llama/llama-3.1-70b-instruct",
        "meta-llama/llama-3.1-8b-instruct",
        "meta-llama/llama-3.2-90b-vision-instruct",
        
        # Mistral Models (good balance of speed/quality)
        "mistralai/mistral-large",
        "mistralai/mistral-medium",
        "mistralai/mistral-small",
        
        # OpenAI Models (high quality)
        "openai/gpt-4o",
        "openai/gpt-4o-mini",
        "openai/gpt-3.5-turbo",
        
        # Google Gemini (strong reasoning)
        "google/gemini-pro-1.5",
        "google/gemini-flash-1.5",
        
        # Moonshot AI
        "moonshot/moonshot-v1-8k",
        "moonshot/moonshot-v1-32k",
        
        # Anthropic Claude (excellent instruction following)
        "anthropic/claude-3.5-sonnet",
        "anthropic/claude-3-haiku",
        
        # Other capable models
        "nvidia/llama-3.1-nemotron-70b-instruct",
        "microsoft/wizardlm-2-8x22b",
        "cohere/command-r-plus",
    ]
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://quizbattle.com",
            "X-Title": "QuizBattle PDF Extractor"
        })
    
    def extract_questions(self, text: str, exam_type: str, difficulty_mode: str) -> List[Dict]:
        """Extract questions using OpenRouter models with fallback"""
        current_app.logger.info(f"🚀 Starting OpenRouter extraction with {len(self.MODELS)} models")
        current_app.logger.info(f"📋 Text length: {len(text)} chars, exam_type: {exam_type}, difficulty: {difficulty_mode}")
        
        for i, model in enumerate(self.MODELS, 1):
            current_app.logger.info(f"🤖 Trying model {i}/{len(self.MODELS)}: {model}")
            
            try:
                questions = self._try_model(model, text, exam_type, difficulty_mode)
                
                if questions and len(questions) > 0:
                    current_app.logger.info(f"✅ Model {model} succeeded: {len(questions)} questions extracted")
                    
                    # Apply difficulty filtering
                    filtered_questions = self._apply_difficulty_rules(questions, difficulty_mode)
                    current_app.logger.info(f"📊 After filtering: {len(filtered_questions)} questions")
                    
                    # Log successful extraction
                    self._log_extraction(model, len(filtered_questions), exam_type, difficulty_mode, True, None)
                    
                    return filtered_questions
                else:
                    current_app.logger.warning(f"⚠️ Model {model} returned empty results")
                    self._log_extraction(model, 0, exam_type, difficulty_mode, False, "Empty results")
                    
            except Exception as e:
                error_msg = str(e)
                current_app.logger.error(f"❌ Model {model} failed: {error_msg}")
                self._log_extraction(model, 0, exam_type, difficulty_mode, False, error_msg)
                
                # If it's a rate limit or quota error, continue to next model
                if any(code in error_msg.lower() for code in ['429', 'rate', 'quota', 'limit']):
                    current_app.logger.info(f"⏰ Rate limited on {model}, trying next model...")
                    continue
        
        # All models failed
        current_app.logger.warning("⚠️ All OpenRouter models failed, this should fallback to regex")
        return []
    
    def _try_model(self, model: str, text: str, exam_type: str, difficulty_mode: str) -> List[Dict]:
        """Try extraction with a specific model"""
        prompt = self._create_extraction_prompt(text, exam_type, difficulty_mode)
        
        try:
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 4000,
                    "temperature": 0.1,
                    "top_p": 0.9,
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                questions = self._parse_ai_response(content)
                
                # Add model info to questions
                for q in questions:
                    q["extraction_method"] = f"openrouter_{model.replace('/', '_')}"
                
                return questions
            else:
                current_app.logger.error(f"API Error {response.status_code}: {response.text}")
                return []
                
        except requests.exceptions.Timeout:
            current_app.logger.error(f"Timeout for model {model}")
            return []
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Request error for model {model}: {e}")
            return []
    
    def _create_extraction_prompt(self, text: str, exam_type: str, difficulty_mode: str) -> str:
        """Create extraction prompt optimized for new PDF format with content cleaning"""
        # Clean the input text first
        cleaned_text = self._clean_pdf_content(text[:3000])
        
        return f"""
You are an expert PDF Question Extractor and Content Cleaner AI. Extract multiple choice questions from the provided {exam_type} exam content.

PDF FORMAT SPECIFICATION:
- Questions start with "Question: " followed by question text (no numbering)
- Options listed under "Options:" as:
    (a) Option text
    (b) Option text  
    (c) Option text
    (d) Option text
- Correct answer indicated by "Answer: " followed by option letter (a/b/c/d)
- Images may be present but have no explanation in PDF

CONTENT CLEANING RULES:
1. IGNORE and SKIP:
   - Headers, footers, and advertisements
   - Text containing "www.", "Download", "App", "FREE EDUCATION", "Visit"
   - Website URLs, social media handles, app promotions
   - Copyright notices, publication info
   - Page numbers, chapter headings

2. CLEAN OPTIONS:
   - If option text contains merged next question text, extract only the option part
   - Remove any advertising text appended to options
   - If cleaning results in less than 4 valid options, SKIP the question

EXTRACTION RULES:
1. ONLY process multiple-choice questions (MCQs) with EXACTLY 4 clean options
2. SKIP questions that are:
   - Numeric/integer answer type ("Calculate the value", "Find the number")
   - Match-the-following type ("Match Column A with Column B")
   - Without proper (a)(b)(c)(d) options
   - Malformed or incomplete after cleaning
   - Questions where options contain website URLs or ads

3. For each valid MCQ extract:
   - Clean question text from "Question: ..."
   - Clean options array from (a), (b), (c), (d)
   - Correct answer from "Answer: (x)"

DIFFICULTY ASSIGNMENT:
- Upload difficulty = "easy":
  * Text-only MCQs → "easy"
  * Image-based MCQs → "tough"
- Upload difficulty = "tough" → ALL questions → "tough"
- Upload difficulty = "mixed" → BALANCE questions:
  * Text-only/Simple MCQs → "easy"
  * Complex/Calculation/Image-based MCQs → "tough"
  * Ensure roughly 50-60% easy and 40-50% tough questions
- Current upload difficulty: {difficulty_mode}

IMAGE HANDLING:
- If question contains an image (detect context clues like "in the figure", "diagram shows"):
  * Set "has_image": true
  * Generate helpful hint explaining the image concept
  * Add image description in "image_description"
- If no image detected:
  * Set "has_image": false
  * Generate hint only for tough questions

REQUIRED JSON FORMAT:
[
  {{
    "question": "Clean question text from PDF",
    "options": ["Clean Option A", "Clean Option B", "Clean Option C", "Clean Option D"],
    "correct_answer": 0,  // index 0-3 based on (a)(b)(c)(d)
    "difficulty": "easy" or "tough",
    "hint": "AI-generated hint or image explanation",
    "has_image": true/false,
    "image_description": "AI explanation of image if present, empty if none",
    "exam_type": "{exam_type}"
  }}
]

HINT GENERATION:
- For tough questions: Provide method/approach guidance
- For image questions: Explain what the image likely shows and how to interpret it
- For complex calculations: Give step-by-step approach hints

Extract from this cleaned PDF content:
{cleaned_text}

Return ONLY the JSON array with valid, cleaned MCQs, no other text:
"""
    
    def _parse_ai_response(self, response_text: str) -> List[Dict]:
        """Parse AI response to extract questions"""
        questions = []
        
        try:
            # Look for JSON in various formats
            json_patterns = [
                r'```json\s*([\s\S]*?)\s*```',  # JSON in code blocks
                r'```\s*([\s\S]*?)\s*```',       # Generic code blocks
                r'\[\s*\{[\s\S]*?\}\s*\]',       # Direct JSON array
            ]
            
            json_text = None
            for pattern in json_patterns:
                match = re.search(pattern, response_text, re.DOTALL)
                if match:
                    json_text = match.group(1) if '```' in pattern else match.group(0)
                    break
            
            if not json_text:
                # Try to find any JSON-like structure
                start = response_text.find('[')
                end = response_text.rfind(']')
                if start != -1 and end != -1 and end > start:
                    json_text = response_text[start:end+1]
            
            if json_text:
                # Clean and parse JSON
                json_text = json_text.strip()
                parsed = json.loads(json_text)
                
                if isinstance(parsed, list):
                    for item in parsed:
                        if self._validate_mcq_question(item):
                            # Ensure all required fields for new PDF format
                            question = {
                                "question": item["question"],
                                "options": item["options"],
                                "correct_answer": item["correct_answer"],
                                "difficulty": item.get("difficulty", "easy"),
                                "hint": item.get("hint", ""),
                                "has_image": item.get("has_image", False),
                                "image_description": item.get("image_description", ""),
                                "exam_type": item.get("exam_type", "General"),
                                "extraction_method": "openrouter_ai"
                            }
                            questions.append(question)
                
        except json.JSONDecodeError as e:
            current_app.logger.error(f"JSON parse error: {e}")
            current_app.logger.debug(f"Attempted to parse: {json_text[:200] if json_text else 'None'}...")
        except Exception as e:
            current_app.logger.error(f"Response parsing error: {e}")
        
        return questions
    
    def _clean_pdf_content(self, text: str) -> str:
        """Clean PDF content by removing ads, headers, footers, and irrelevant content"""
        lines = text.split('\n')
        cleaned_lines = []
        
        # Patterns to identify and skip unwanted content
        skip_patterns = [
            r'www\.',  # Website URLs
            r'Download',  # Download links
            r'App',  # App promotions
            r'FREE EDUCATION',  # Educational ads
            r'Visit',  # Visit prompts
            r'@[\w]+',  # Social media handles
            r'\bPage \d+\b',  # Page numbers
            r'Chapter \d+',  # Chapter headings
            r'Copyright',  # Copyright notices
            r'\bAll rights reserved\b',  # Rights notices
            r'Published by',  # Publication info
            r'Available on',  # Availability info
            r'Get more',  # Promotional text
            r'Subscribe',  # Subscription prompts
            r'Follow us',  # Social media prompts
            r'\b(?:Android|iOS|Play Store|App Store)\b',  # App store references
        ]
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip lines matching unwanted patterns
            should_skip = False
            for pattern in skip_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    should_skip = True
                    break
            
            if not should_skip:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _clean_question_text(self, question_text: str) -> str:
        """Clean question text by removing ads and unwanted content"""
        # Remove common ad patterns from question text
        unwanted_patterns = [
            r'Download.*?App',  # Download app promotions
            r'Visit.*?website',  # Website visits
            r'www\.\S+',  # URLs
            r'Available on.*?Store',  # App store promotions
            r'Get more questions.*?',  # Question promotions
            r'\bFREE\b.*?education',  # Free education ads
        ]
        
        cleaned_text = question_text
        for pattern in unwanted_patterns:
            cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.IGNORECASE)
        
        # Clean up extra whitespace
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        
        return cleaned_text
    
    def _clean_option_text(self, option_text: str) -> str:
        """Clean option text and handle merged content"""
        # Remove common ad patterns
        unwanted_patterns = [
            r'Download.*',  # Download promotions at end
            r'Visit.*',  # Visit promotions
            r'www\.\S+.*',  # URLs and following content
            r'App Store.*',  # App store references
            r'Play Store.*',  # Play store references
            r'Question \d+:.*',  # Merged next question
            r'\bFREE\b.*',  # Free promotions
        ]
        
        cleaned_option = option_text.strip()
        
        for pattern in unwanted_patterns:
            # Find the match and truncate at that point
            match = re.search(pattern, cleaned_option, flags=re.IGNORECASE)
            if match:
                cleaned_option = cleaned_option[:match.start()].strip()
                break
        
        # Remove trailing punctuation that might be left from truncation
        cleaned_option = re.sub(r'[,\s]+$', '', cleaned_option)
        
        # Ensure minimum length
        if len(cleaned_option.strip()) < 2:
            return ""
        
        return cleaned_option.strip()
    
    def _validate_mcq_question(self, question: Dict) -> bool:
        """Validate extracted MCQ question format for new PDF format"""
        required_keys = ["question", "options", "correct_answer"]
        
        # Check required keys exist
        if not all(key in question for key in required_keys):
            return False
        
        # Check question text
        if not question["question"] or len(question["question"].strip()) < 5:
            return False
        
        # Skip numeric/integer questions (detect numeric patterns)
        question_text = question["question"].lower()
        numeric_indicators = [
            "calculate the value", "find the number", "what is the value",
            "numerical answer", "integer answer", "decimal answer"
        ]
        if any(indicator in question_text for indicator in numeric_indicators):
            return False
        
        # Skip match-the-following questions
        match_indicators = [
            "match the following", "match column", "match list",
            "column a", "column b", "list i", "list ii"
        ]
        if any(indicator in question_text for indicator in match_indicators):
            return False
        
        # Check options - must be exactly 4 for MCQ
        options = question["options"]
        if not isinstance(options, list) or len(options) != 4:
            return False
        
        if any(not option or len(str(option).strip()) < 1 for option in options):
            return False
        
        # Check correct answer
        correct_answer = question["correct_answer"]
        if not isinstance(correct_answer, int) or not (0 <= correct_answer <= 3):
            return False
        
        return True
    
    def _apply_difficulty_rules(self, questions: List[Dict], difficulty_mode: str) -> List[Dict]:
        """Apply difficulty filtering rules"""
        filtered = []
        
        # Ensure all questions have difficulty classification
        for q in questions:
            if not q.get("difficulty"):
                q["difficulty"] = self._classify_question_difficulty(q.get("question", ""), difficulty_mode)
        
        if difficulty_mode == "easy":
            # Easy mode: prefer text-only easy questions
            filtered = [q for q in questions if not q.get("has_image", False)]
            easy_questions = [q for q in filtered if q.get("difficulty") == "easy"]
            if len(easy_questions) >= 5:
                filtered = easy_questions[:15]
        
        elif difficulty_mode == "tough":
            # Tough mode: all questions, generate hints for tough ones
            filtered = questions
            for q in filtered:
                if q.get("difficulty") == "tough" and not q.get("hint"):
                    q["hint"] = self._generate_hint(q["question"])
        
        elif difficulty_mode == "mixed":
            # Mixed mode: 60% easy, 40% tough
            easy_questions = [q for q in questions if q.get("difficulty") == "easy"]
            tough_questions = [q for q in questions if q.get("difficulty") == "tough"]
            
            total_wanted = min(len(questions), 20)
            easy_count = max(1, int(total_wanted * 0.6))
            tough_count = max(1, total_wanted - easy_count)
            
            filtered.extend(easy_questions[:easy_count])
            filtered.extend(tough_questions[:tough_count])
            
            # Generate hints for tough questions
            for q in filtered:
                if q.get("difficulty") == "tough" and not q.get("hint"):
                    q["hint"] = self._generate_hint(q["question"])
        
        return filtered[:30]  # Maximum 30 questions
    
    def _classify_question_difficulty(self, question_text: str, difficulty_mode: str) -> str:
        """Classify question difficulty based on content with enhanced logic"""
        if difficulty_mode in ["easy", "tough"]:
            return difficulty_mode
        
        text_lower = question_text.lower()
        
        # Complex/Tough indicators (higher weight)
        tough_keywords = [
            'calculate', 'derive', 'prove', 'analyze', 'evaluate', 
            'determine', 'find the value', 'solve for', 'show that', 'verify',
            'demonstrate', 'compute', 'deduce', 'infer', 'justify',
            'ratio', 'proportion', 'percentage', 'formula', 'equation',
            'coefficient', 'factor', 'variable', 'function', 'graph',
            'magnetic field', 'electric field', 'acceleration', 'velocity',
            'frequency', 'wavelength', 'amplitude', 'potential difference',
            'kinetic energy', 'potential energy', 'momentum', 'force',
            'pressure', 'temperature', 'volume', 'concentration',
            'equilibrium', 'reaction rate', 'half-life', 'decay',
            'oscillation', 'pendulum', 'spring constant', 'resonance'
        ]
        
        # Simple/Easy indicators
        easy_keywords = [
            'what is', 'which of the following', 'identify', 'name', 'state',
            'define', 'list', 'choose', 'select', 'who', 'when', 'where',
            'true or false', 'correct statement', 'incorrect statement',
            'property of', 'characteristic of', 'example of', 'type of',
            'unit of measurement', 'symbol for', 'abbreviation'
        ]
        
        # Mathematical complexity indicators (tough)
        math_patterns = [
            r'\d+\s*[×*/÷]\s*\d+',  # Basic math operations
            r'\d+\s*\^\s*\d+',      # Exponents
            r'√\(.*?\)',            # Square roots
            r'\d+\.\d+',            # Decimals
            r'\d+/\d+',             # Fractions
            r'\d+:\d+',             # Ratios
        ]
        
        # Count indicators
        tough_score = sum(1 for keyword in tough_keywords if keyword in text_lower)
        easy_score = sum(1 for keyword in easy_keywords if keyword in text_lower)
        
        # Check for mathematical patterns
        import re
        math_score = sum(1 for pattern in math_patterns if re.search(pattern, question_text))
        
        # Length and complexity heuristics
        if len(question_text) > 150:  # Long questions tend to be tougher
            tough_score += 1
        
        if len(question_text.split()) > 25:  # Many words = complex
            tough_score += 1
        
        # Final classification
        if tough_score + math_score > easy_score:
            return 'tough'
        elif easy_score > 0:
            return 'easy'
        else:
            # Default classification based on length for mixed mode
            return 'tough' if len(question_text) > 100 else 'easy'
    
    def _generate_hint(self, question_text: str) -> str:
        """Generate contextual hints for tough questions"""
        text_lower = question_text.lower()
        
        # Mathematical/calculation hints
        if any(word in text_lower for word in ['calculate', 'compute', 'find the value']):
            return "Remember to identify the given values and choose the appropriate formula. Check your units!"
        
        # Analysis hints
        elif any(word in text_lower for word in ['analyze', 'examine', 'evaluate']):
            return "Break down the problem into smaller parts and consider each component systematically."
        
        # Comparison hints
        elif any(word in text_lower for word in ['compare', 'contrast', 'difference']):
            return "Look for key similarities and differences. Consider the underlying principles."
        
        # Derivation/proof hints
        elif any(word in text_lower for word in ['derive', 'prove', 'show that']):
            return "Start with fundamental principles and work step by step. Each step should follow logically."
        
        # Subject-specific hints
        elif any(word in text_lower for word in ['physics', 'force', 'energy', 'motion']):
            return "Apply relevant physics laws. Consider conservation principles and vector directions."
        
        elif any(word in text_lower for word in ['chemistry', 'reaction', 'molecule', 'bond']):
            return "Think about electron configuration, molecular geometry, and reaction mechanisms."
        
        elif any(word in text_lower for word in ['biology', 'cell', 'organism', 'genetics']):
            return "Consider the biological processes involved and their interconnections."
        
        elif any(word in text_lower for word in ['mathematics', 'equation', 'function']):
            return "Use appropriate mathematical methods. Check your work and consider special cases."
        
        else:
            return "Consider the key concepts involved and their relationships. Think step by step."
    
    def _log_extraction(self, provider: str, questions_count: int, exam_type: str, 
                       difficulty_mode: str, success: bool, error: str):
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
                'session_id': getattr(current_app, '_extraction_session_id', 'openrouter_session'),
                'service': 'openrouter'
            }
            
            if hasattr(current_app, 'mongo_db'):
                current_app.mongo_db.extraction_logs.insert_one(log_entry)
            else:
                current_app.logger.warning("MongoDB not available for logging")
                
        except Exception as e:
            current_app.logger.error(f"Failed to log extraction: {str(e)}")


class OpenRouterPDFExtractor:
    """Main PDF extractor using OpenRouter API with regex fallback"""
    
    def __init__(self, api_keys_file: str = None):
        self.api_keys = self._load_api_keys(api_keys_file)
        self.openrouter = None
        self._initialize_openrouter()
    
    def _load_api_keys(self, api_keys_file: str) -> Dict[str, str]:
        """Load API keys from file"""
        keys = {}
        try:
            if api_keys_file is None:
                import os
                api_keys_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '..', 'api_keys.txt')
            
            current_app.logger.info(f"🔑 Loading API keys from: {api_keys_file}")
            
            with open(api_keys_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        keys[key.strip()] = value.strip()
            
            current_app.logger.info(f"✅ Loaded {len(keys)} API keys")
            
        except FileNotFoundError:
            current_app.logger.warning("⚠️ API keys file not found")
        except Exception as e:
            current_app.logger.error(f"❌ Error loading API keys: {str(e)}")
        
        return keys
    
    def _initialize_openrouter(self):
        """Initialize OpenRouter client"""
        if 'OpenRouter' in self.api_keys:
            try:
                self.openrouter = OpenRouterExtractor(self.api_keys['OpenRouter'])
                current_app.logger.info(f"✅ OpenRouter initialized with {len(self.openrouter.MODELS)} models")
            except Exception as e:
                current_app.logger.error(f"❌ Failed to initialize OpenRouter: {str(e)}")
        else:
            current_app.logger.warning("⚠️ OpenRouter API key not found")
    
    def extract_questions_from_text(self, text: str, exam_type: str, difficulty_mode: str = 'mixed') -> List[Dict]:
        """Extract questions using OpenRouter with fallback to regex"""
        current_app.logger.info(f"📄 Starting extraction: {len(text)} chars, exam_type={exam_type}, mode={difficulty_mode}")
        
        # Detect PDF format
        pdf_format = self._detect_pdf_format(text)
        current_app.logger.info(f"📋 Detected PDF format: {pdf_format}")
        
        # Try OpenRouter first
        if self.openrouter:
            current_app.logger.info("🚀 Attempting OpenRouter extraction...")
            questions = self.openrouter.extract_questions(text, exam_type, difficulty_mode)
            
            if questions and len(questions) > 0:
                current_app.logger.info(f"✅ OpenRouter succeeded: {len(questions)} questions")
                return questions
            else:
                current_app.logger.warning("⚠️ OpenRouter failed or returned no questions")
        else:
            current_app.logger.warning("⚠️ OpenRouter not available")
        
        # Fallback to regex
        current_app.logger.info("🔄 Falling back to regex extraction")
        questions = self._extract_with_regex(text, exam_type, difficulty_mode, pdf_format)
        
        # Log regex fallback
        try:
            log_entry = {
                'provider': 'Regex_Fallback',
                'questions_extracted': len(questions),
                'exam_type': exam_type,
                'difficulty_mode': difficulty_mode,
                'success': True,
                'error': None,
                'timestamp': datetime.utcnow(),
                'session_id': getattr(current_app, '_extraction_session_id', 'regex_session'),
                'service': 'regex'
            }
            
            if hasattr(current_app, 'mongo_db'):
                current_app.mongo_db.extraction_logs.insert_one(log_entry)
        except Exception as e:
            current_app.logger.error(f"Failed to log regex extraction: {str(e)}")
        
        return questions
    
    def _detect_pdf_format(self, text: str) -> str:
        """Detect PDF format - prioritize new format detection"""
        # New Format: Question: ... Options: (a) ... Answer: (x)
        new_format_pattern = r'Question:\s*.*?\n\s*Options:\s*\n\s*\(a\).*?\n\s*\(b\).*?\n\s*\(c\).*?\n\s*\(d\).*?\n\s*Answer:\s*\([a-d]\)'
        new_format_matches = len(re.findall(new_format_pattern, text, re.MULTILINE | re.DOTALL))
        
        # Legacy Format A: Questions with immediate options
        format_a_pattern = r'(?i)(question|q\.?\s*\d+).*?\n.*?[abcd][.):]'
        format_a_matches = len(re.findall(format_a_pattern, text, re.MULTILINE))
        
        # Legacy Format B: Questions first, then answers section
        format_b_indicators = [
            'answer key', 'answers:', 'correct answers', 'solution:',
            'answer sheet', 'marking scheme'
        ]
        format_b_matches = sum(1 for indicator in format_b_indicators if indicator in text.lower())
        
        if new_format_matches > 0:
            current_app.logger.info(f"✅ Detected NEW PDF Format: {new_format_matches} questions")
            return 'New_Format'
        elif format_a_matches > format_b_matches:
            return 'Format_A'
        elif format_b_matches > 0:
            return 'Format_B'
        else:
            return 'Unknown'
    
    def _extract_with_regex(self, text: str, exam_type: str, difficulty_mode: str, pdf_format: str) -> List[Dict]:
        """Regex extraction for new PDF format as final fallback"""
        questions = []
        
        if pdf_format == 'New_Format':
            # Extract questions using new PDF format
            questions = self._extract_new_format_regex(text, exam_type, difficulty_mode)
        else:
            # Legacy format extraction
            questions = self._extract_legacy_format_regex(text, exam_type, difficulty_mode)
        
        current_app.logger.info(f"📝 Regex extraction completed: {len(questions)} questions from {pdf_format}")
        return questions[:30]
    
    def _extract_new_format_regex(self, text: str, exam_type: str, difficulty_mode: str) -> List[Dict]:
        """Extract questions from new PDF format using regex with content cleaning"""
        questions = []
        
        # Clean the text first
        cleaned_text = self._clean_pdf_content(text)
        
        # Comprehensive pattern for new format
        new_format_pattern = r'Question:\s*(.+?)\s*Options:\s*\n\s*\(a\)\s*(.+?)\s*\n\s*\(b\)\s*(.+?)\s*\n\s*\(c\)\s*(.+?)\s*\n\s*\(d\)\s*(.+?)\s*\n\s*Answer:\s*\(([a-d])\)'
        
        matches = re.finditer(new_format_pattern, cleaned_text, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            try:
                question_text = match.group(1).strip()
                option_a = match.group(2).strip()
                option_b = match.group(3).strip()
                option_c = match.group(4).strip()
                option_d = match.group(5).strip()
                answer_letter = match.group(6).lower()
                
                # Clean up multiline question text
                question_text = re.sub(r'\s+', ' ', question_text).strip()
                question_text = self._clean_question_text(question_text)
                
                # Skip invalid questions
                if len(question_text) < 5:
                    continue
                
                # Clean and validate options
                raw_options = [option_a, option_b, option_c, option_d]
                cleaned_options = []
                
                for opt in raw_options:
                    cleaned_opt = self._clean_option_text(opt)
                    if cleaned_opt and len(cleaned_opt.strip()) > 0:
                        cleaned_options.append(cleaned_opt)
                
                # Must have exactly 4 valid options after cleaning
                if len(cleaned_options) != 4:
                    current_app.logger.debug(f"Skipping question with {len(cleaned_options)} valid options after cleaning")
                    continue
                
                options = cleaned_options
                
                # Skip numeric/integer questions
                if self._is_numeric_question(question_text):
                    current_app.logger.debug(f"Skipping numeric question: {question_text[:50]}...")
                    continue
                
                # Skip match-the-following questions
                if self._is_match_question(question_text):
                    current_app.logger.debug(f"Skipping match question: {question_text[:50]}...")
                    continue
                
                # Map answer letter to index
                answer_map = {'a': 0, 'b': 1, 'c': 2, 'd': 3}
                correct_answer = answer_map.get(answer_letter, 0)
                
                # Determine difficulty based on upload setting and content
                if difficulty_mode == 'tough':
                    difficulty = 'tough'
                elif difficulty_mode == 'easy':
                    # Check for image indicators
                    has_image = self._detect_image_in_text(question_text)
                    difficulty = 'tough' if has_image else 'easy'
                else:  # mixed
                    difficulty = self._classify_difficulty_new_format(question_text)
                
                # Generate hints
                hint = ""
                image_description = ""
                has_image = self._detect_image_in_text(question_text)
                
                if has_image:
                    hint = self._generate_image_hint(question_text)
                    image_description = self._generate_image_description(question_text)
                elif difficulty == 'tough':
                    hint = self._generate_concept_hint(question_text)
                
                question = {
                    'question': question_text,
                    'options': options,
                    'correct_answer': correct_answer,
                    'difficulty': difficulty,
                    'hint': hint,
                    'has_image': has_image,
                    'image_description': image_description,
                    'exam_type': exam_type,
                    'extraction_method': 'regex_new_format'
                }
                
                questions.append(question)
                current_app.logger.debug(f"Extracted question: {question_text[:50]}... (difficulty: {difficulty})")
                
            except Exception as e:
                current_app.logger.debug(f"Error parsing new format match: {str(e)}")
                continue
        
        return questions
    
    def _extract_legacy_format_regex(self, text: str, exam_type: str, difficulty_mode: str) -> List[Dict]:
        """Extract questions from legacy PDF formats using regex"""
        questions = []
        
        # Legacy regex patterns
        patterns = [
            r'(?:Question\s*(\d+)[.:]?\s*)?([^\n]+(?:\n[^\n]+)*?)\n\s*[Aa][.):]?\s*([^\n]+)\n\s*[Bb][.):]?\s*([^\n]+)\n\s*[Cc][.):]?\s*([^\n]+)\n\s*[Dd][.):]?\s*([^\n]+)',
            r'(\d+\.\s*[^\n]+(?:\n[^\n]+)*?)\n\s*\([Aa]\)\s*([^\n]+)\n\s*\([Bb]\)\s*([^\n]+)\n\s*\([Cc]\)\s*([^\n]+)\n\s*\([Dd]\)\s*([^\n]+)'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
            
            for match in matches:
                try:
                    groups = match.groups()
                    
                    if len(groups) == 6:  # Full format
                        question_text = groups[1].strip()
                        options = [groups[j].strip() for j in range(2, 6)]
                    elif len(groups) == 5:  # No question number
                        question_text = groups[0].strip()
                        options = [groups[j].strip() for j in range(1, 5)]
                    else:
                        continue
                    
                    # Basic validation
                    if len(question_text) < 10 or len(options) != 4:
                        continue
                    
                    if any(len(opt) < 2 for opt in options):
                        continue
                    
                    difficulty = self._classify_difficulty(question_text, difficulty_mode)
                    hint = self._generate_hint(question_text) if difficulty == 'tough' else ""
                    
                    question = {
                        'question': question_text,
                        'options': options,
                        'correct_answer': 0,  # Default for legacy
                        'difficulty': difficulty,
                        'hint': hint,
                        'has_image': '[image:' in question_text.lower(),
                        'image_description': "",
                        'exam_type': exam_type,
                        'extraction_method': 'regex_legacy'
                    }
                    
                    questions.append(question)
                    
                except Exception as e:
                    current_app.logger.debug(f"Error parsing legacy format match: {str(e)}")
                    continue
        
        return questions
    
    def _clean_pdf_content(self, text: str) -> str:
        """Clean PDF content by removing ads, headers, footers, and irrelevant content"""
        lines = text.split('\n')
        cleaned_lines = []
        
        # Patterns to identify and skip unwanted content
        skip_patterns = [
            r'www\.',  # Website URLs
            r'Download',  # Download links
            r'App',  # App promotions
            r'FREE EDUCATION',  # Educational ads
            r'Visit',  # Visit prompts
            r'@[\w]+',  # Social media handles
            r'\bPage \d+\b',  # Page numbers
            r'Chapter \d+',  # Chapter headings
            r'Copyright',  # Copyright notices
            r'\bAll rights reserved\b',  # Rights notices
            r'Published by',  # Publication info
            r'Available on',  # Availability info
            r'Get more',  # Promotional text
            r'Subscribe',  # Subscription prompts
            r'Follow us',  # Social media prompts
            r'\b(?:Android|iOS|Play Store|App Store)\b',  # App store references
        ]
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip lines matching unwanted patterns
            should_skip = False
            for pattern in skip_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    should_skip = True
                    break
            
            if not should_skip:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _clean_question_text(self, question_text: str) -> str:
        """Clean question text by removing ads and unwanted content"""
        # Remove common ad patterns from question text
        unwanted_patterns = [
            r'Download.*?App',  # Download app promotions
            r'Visit.*?website',  # Website visits
            r'www\.\S+',  # URLs
            r'Available on.*?Store',  # App store promotions
            r'Get more questions.*?',  # Question promotions
            r'\bFREE\b.*?education',  # Free education ads
        ]
        
        cleaned_text = question_text
        for pattern in unwanted_patterns:
            cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.IGNORECASE)
        
        # Clean up extra whitespace
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        
        return cleaned_text
    
    def _clean_option_text(self, option_text: str) -> str:
        """Clean option text and handle merged content"""
        # Remove common ad patterns
        unwanted_patterns = [
            r'Download.*',  # Download promotions at end
            r'Visit.*',  # Visit promotions
            r'www\.\S+.*',  # URLs and following content
            r'App Store.*',  # App store references
            r'Play Store.*',  # Play store references
            r'Question \d+:.*',  # Merged next question
            r'\bFREE\b.*',  # Free promotions
        ]
        
        cleaned_option = option_text.strip()
        
        for pattern in unwanted_patterns:
            # Find the match and truncate at that point
            match = re.search(pattern, cleaned_option, flags=re.IGNORECASE)
            if match:
                cleaned_option = cleaned_option[:match.start()].strip()
                break
        
        # Remove trailing punctuation that might be left from truncation
        cleaned_option = re.sub(r'[,\s]+$', '', cleaned_option)
        
        # Ensure minimum length
        if len(cleaned_option.strip()) < 2:
            return ""
        
        return cleaned_option.strip()
    
    def _is_numeric_question(self, question_text: str) -> bool:
        """Check if question expects numeric/integer answer"""
        text_lower = question_text.lower()
        numeric_indicators = [
            "calculate the value", "find the number", "what is the value",
            "numerical answer", "integer answer", "decimal answer",
            "how much", "how many", "what percentage", "find the result"
        ]
        return any(indicator in text_lower for indicator in numeric_indicators)
    
    def _is_match_question(self, question_text: str) -> bool:
        """Check if question is match-the-following type"""
        text_lower = question_text.lower()
        match_indicators = [
            "match the following", "match column", "match list",
            "column a", "column b", "list i", "list ii",
            "pair the following", "connect the following"
        ]
        return any(indicator in text_lower for indicator in match_indicators)
    
    def _detect_image_in_text(self, question_text: str) -> bool:
        """Detect if question likely contains an image"""
        text_lower = question_text.lower()
        image_indicators = [
            "in the figure", "in the diagram", "shown in figure",
            "as shown", "in the image", "from the graph",
            "in the circuit", "the diagram shows", "figure shows",
            "observe the", "look at the", "given below", "shown below"
        ]
        return any(indicator in text_lower for indicator in image_indicators)
    
    def _classify_difficulty_new_format(self, question_text: str) -> str:
        """Classify question difficulty for new format"""
        text_lower = question_text.lower()
        
        # Tough indicators
        tough_keywords = [
            'calculate', 'derive', 'prove', 'analyze', 'evaluate', 
            'compare', 'explain why', 'determine', 'find the value',
            'solve for', 'show that', 'verify', 'demonstrate',
            'compute', 'deduce', 'infer', 'justify'
        ]
        
        # Check for complex physics/math terms
        complex_terms = [
            'eigenvalue', 'wavelength', 'polarizer', 'pendulum',
            'oscillator', 'harmonic', 'momentum', 'entropy',
            'derivative', 'integral', 'matrix', 'quantum'
        ]
        
        if (any(keyword in text_lower for keyword in tough_keywords) or 
            any(term in text_lower for term in complex_terms)):
            return 'tough'
        else:
            return 'easy'
    
    def _generate_image_hint(self, question_text: str) -> str:
        """Generate hint for image-based questions"""
        text_lower = question_text.lower()
        
        if 'circuit' in text_lower:
            return "Analyze the circuit components and their connections. Apply Ohm's law and circuit analysis principles."
        elif 'graph' in text_lower or 'plot' in text_lower:
            return "Examine the axes, scales, and trends in the graph. Look for key points and relationships."
        elif 'diagram' in text_lower:
            return "Study the diagram carefully. Identify all components and their relationships."
        elif 'figure' in text_lower:
            return "Observe all elements in the figure. Consider physical principles that apply to the scenario shown."
        else:
            return "Examine the visual information provided. Relate it to the theoretical concepts being tested."
    
    def _generate_image_description(self, question_text: str) -> str:
        """Generate description of what image likely shows"""
        text_lower = question_text.lower()
        
        if 'polarizer' in text_lower:
            return "Diagram showing light passing through polarizing filters at different angles"
        elif 'pendulum' in text_lower:
            return "Diagram of a simple pendulum showing its motion at different heights"
        elif 'circuit' in text_lower:
            return "Electrical circuit diagram with components like resistors, capacitors, or voltage sources"
        elif 'wave' in text_lower:
            return "Wave diagram showing amplitude, frequency, or interference patterns"
        elif 'force' in text_lower:
            return "Force diagram showing vectors and their directions"
        else:
            return "Visual representation supporting the question context"
    
    def _generate_concept_hint(self, question_text: str) -> str:
        """Generate conceptual hint for tough questions"""
        text_lower = question_text.lower()
        
        # Physics-specific hints
        if 'polarizer' in text_lower or 'polarization' in text_lower:
            return "Apply Malus's law: I = I₀cos²θ. Consider the intensity reduction at each polarizer."
        elif 'pendulum' in text_lower:
            return "Use T = 2π√(l/g). Consider how gravity changes with height above Earth's surface."
        elif 'oscillator' in text_lower or 'harmonic' in text_lower:
            return "Apply principles of simple harmonic motion. Consider energy conservation and restoring forces."
        elif 'quantum' in text_lower or 'eigenvalue' in text_lower:
            return "Use quantum mechanical principles. Consider boundary conditions and wave functions."
        
        # General hints based on question type
        elif any(word in text_lower for word in ['calculate', 'compute', 'find']):
            return "Identify given values and required formula. Check units and significant figures."
        elif any(word in text_lower for word in ['analyze', 'examine', 'evaluate']):
            return "Break down the problem systematically. Consider all relevant physical principles."
        elif any(word in text_lower for word in ['compare', 'contrast']):
            return "Look for key similarities and differences. Consider underlying physical mechanisms."
        else:
            return "Apply fundamental principles step by step. Consider conservation laws and symmetries."
    
    def _classify_difficulty(self, question_text: str, difficulty_mode: str) -> str:
        """Simple difficulty classification for regex fallback"""
        if difficulty_mode in ['easy', 'tough']:
            return difficulty_mode
        
        text_lower = question_text.lower()
        tough_keywords = ['calculate', 'derive', 'prove', 'analyze', 'determine']
        
        if any(keyword in text_lower for keyword in tough_keywords):
            return 'tough'
        else:
            return 'easy'
    
    def _generate_hint(self, question_text: str) -> str:
        """Simple hint generation for regex fallback"""
        text_lower = question_text.lower()
        
        if 'calculate' in text_lower or 'compute' in text_lower:
            return 'Check your calculations and units carefully.'
        elif 'analyze' in text_lower:
            return 'Break down the problem step by step.'
        elif 'compare' in text_lower:
            return 'Look for key similarities and differences.'
        else:
            return 'Think about the underlying concepts involved.'


# Global extractor instance
_extractor_instance = None

def get_openrouter_extractor():
    """Get singleton OpenRouter extractor instance"""
    global _extractor_instance
    if _extractor_instance is None:
        _extractor_instance = OpenRouterPDFExtractor()
    return _extractor_instance