# OpenRouter PDF Question Extraction Integration

## Overview

The QuizBattle application now includes comprehensive OpenRouter integration for PDF question extraction, providing access to multiple AI models through a single API key. This system uses a cascading approach where it tries different models until successful extraction is achieved, with intelligent fallback to regex-based extraction.

## Architecture

### 1. OpenRouter Service (`openrouter_pdf_extractor.py`)

**Primary Components:**
- `OpenRouterExtractor`: Core class that handles API calls to multiple AI models
- `OpenRouterPDFExtractor`: Main service that manages extraction logic and fallback
- **24+ AI Models**: Including DeepSeek, Meta LLaMA, Mistral, OpenAI, Google Gemini, and more

**Key Features:**
- **Model Cascading**: Tries models in priority order until successful
- **Intelligent Prompting**: Specialized prompts for question extraction
- **Difficulty Classification**: Smart classification of questions as "easy" or "tough"
- **Hint Generation**: Contextual hints for tough questions
- **Format Detection**: Handles both Format A (Q→Options→Answer) and Format B (Questions then Answers)
- **Comprehensive Logging**: Detailed MongoDB logging for debugging

### 2. Integration with Existing System

The integration maintains **backward compatibility** with the existing PDF extraction system:

```python
# Primary extraction flow:
1. OpenRouter (24+ models) → Success: Return questions
2. Individual AI Providers (DeepSeek, SambaCloud, OpenAI) → Success: Return questions  
3. Regex Fallback → Always returns something
```

### 3. Enhanced Features

**Difficulty Mode Support:**
- **Easy Mode**: Filters for simple questions, excludes complex images
- **Tough Mode**: All questions, generates hints for complex ones
- **Mixed Mode**: 60% easy, 40% tough questions (configurable)

**Question Enhancement:**
- Automatic hint generation for tough questions
- Subject-specific hint strategies (Physics, Chemistry, Biology, Math)
- Image detection and handling
- Extraction method tracking

## API Models Available

### Free/Open Source Models (Priority)
1. **DeepSeek Models**: Excellent for code/text extraction
   - `deepseek/deepseek-r1`
   - `deepseek/deepseek-chat`
   - `deepseek/deepseek-coder`

2. **Qwen Models**: Strong multilingual capabilities
   - `qwen/qwen-2.5-72b-instruct`
   - `qwen/qwen-2.5-32b-instruct`
   - `qwen/qwen-2.5-14b-instruct`
   - `qwen/qwen-2.5-7b-instruct`
   - `qwen/qwen-2.5-coder-32b-instruct`

3. **Meta LLaMA Models**: Reliable general purpose
   - `meta-llama/llama-3.1-405b-instruct`
   - `meta-llama/llama-3.1-70b-instruct`
   - `meta-llama/llama-3.1-8b-instruct`
   - `meta-llama/llama-3.2-90b-vision-instruct`

### Premium Models (Fallback)
4. **Mistral Models**: Good balance of speed/quality
5. **OpenAI Models**: High quality (GPT-4o, GPT-3.5-turbo)
6. **Google Gemini**: Strong reasoning capabilities
7. **Anthropic Claude**: Excellent instruction following
8. **Other Models**: Nvidia, Microsoft, Cohere, Moonshot

## Configuration

### API Key Setup
```bash
# api_keys.txt
OpenRouter=sk-or-v1-your-api-key-here
```

### Environment Variables (Optional)
```bash
OPENROUTER_API_KEY=sk-or-v1-your-api-key-here
OPENROUTER_SITE_URL=https://quizbattle.com
OPENROUTER_APP_NAME=QuizBattle PDF Extractor
```

## Usage Examples

### 1. Direct OpenRouter Usage
```python
from app.services.openrouter_pdf_extractor import get_openrouter_extractor

extractor = get_openrouter_extractor()
questions = extractor.extract_questions_from_text(
    text="Your PDF content here",
    exam_type="CBSE 11 Physics",
    difficulty_mode="mixed"  # easy, tough, or mixed
)
```

### 2. Through Main PDF Extractor (Recommended)
```python
from app.services.pdf_extractor import get_extractor

extractor = get_extractor()
questions = extractor.extract_questions_from_text(
    text="Your PDF content here",
    exam_type="CBSE 11 Physics", 
    difficulty_mode="mixed"
)
```

### 3. Admin PDF Upload (Already Integrated)
The admin panel upload endpoint automatically uses the new system:
```
POST /admin/upload-pdf
- Form data: pdf file, exam_type, difficulty
- Returns: processed questions with extraction statistics
```

## Question Schema

Each extracted question follows this enhanced schema:

```json
{
  "question": "Complete question text",
  "options": ["Option A", "Option B", "Option C", "Option D"],
  "correct_answer": 0,  // Index (0-3)
  "difficulty": "easy",  // easy, tough
  "hint": "Helpful hint for tough questions",  // null for easy
  "has_image": false,
  "exam_type": "CBSE 11 Physics",
  "extraction_method": "openrouter_deepseek_deepseek_chat"
}
```

## Monitoring & Debugging

### 1. Extraction Logs Endpoint
```
GET /debug/extraction/logs?limit=50&service=openrouter&success_only=true
```
**Response includes:**
- Individual extraction attempts
- Success/failure rates by provider
- Questions extracted per session
- Error messages and timing

### 2. Model Statistics Endpoint  
```
GET /debug/extraction/models
```
**Response includes:**
- Model performance statistics
- Success rates by model
- Average questions per successful extraction
- Most/least reliable models
- Recent usage patterns

### 3. MongoDB Collections
- **extraction_logs**: Detailed extraction attempt logs
- **pdf_uploads**: PDF upload history and statistics

## Error Handling & Fallback

The system implements multiple levels of fallback:

1. **OpenRouter Model Cascading**: If one model fails, try the next
2. **Rate Limit Handling**: Automatically switches models on rate limits
3. **Individual Provider Fallback**: Falls back to original providers
4. **Regex Fallback**: Always provides basic extraction as last resort
5. **Graceful Degradation**: System continues working even with API issues

## Performance Optimizations

### 1. Model Priority Order
- Free models first to minimize costs
- Most successful models prioritized
- Vision models for image-heavy content

### 2. Request Optimization
- Truncated text input (3000 chars) for prompting
- Optimized timeout settings (60s)
- Efficient JSON parsing with multiple patterns

### 3. Caching & Logging
- Session-based tracking for debugging
- MongoDB logging for performance analysis
- Extraction method tracking for optimization

## Testing

### Comprehensive Test Suite
Run the test suite to verify integration:
```bash
python test_openrouter_extraction.py
```

**Tests include:**
- OpenRouter extractor initialization
- Easy/tough/mixed mode extraction
- Main extractor integration
- Error handling and fallbacks
- Performance timing

### Sample Results
```
OpenRouter PDF Extraction Test Suite
Generated at: 2024-01-15 10:30:45
============================================================
✅ OpenRouter initialized with 24 models
✅ Easy mode successful: 5 questions extracted
✅ Tough mode successful: 3 questions extracted  
✅ Mixed mode successful: 8 questions extracted
✅ Main extractor integration working
✅ Fallback systems operational

📋 TEST SUMMARY
============================================================
Total Tests: 3
Passed: 3  
Failed: 0
Success Rate: 100.0%
🎯 Overall Status: ✅ ALL TESTS PASSED
```

## Best Practices

### 1. API Usage
- Monitor rate limits through debug endpoints
- Use appropriate difficulty modes for content
- Check extraction logs for optimization opportunities

### 2. Content Preparation
- Ensure PDFs have text content (not just images)
- Use clear question formatting
- Include answer keys for Format B PDFs

### 3. Performance Monitoring
- Regular checks on model success rates
- Monitor extraction times through logs  
- Optimize based on session statistics

## Troubleshooting

### Common Issues

1. **No Questions Extracted**
   - Check API key validity in `api_keys.txt`
   - Verify PDF content has text (not just images)
   - Check extraction logs for specific errors

2. **Slow Extraction**
   - Check which models are being used
   - Monitor for rate limiting issues
   - Consider optimizing model priority order

3. **Poor Question Quality**
   - Adjust difficulty mode settings
   - Check if content matches expected format
   - Review hint generation for tough questions

### Debug Commands
```python
# Check extractor status
extractor = get_openrouter_extractor()
print(f"Models available: {len(extractor.openrouter.MODELS)}")

# View recent logs
GET /debug/extraction/logs?limit=10

# Check model performance  
GET /debug/extraction/models
```

## Future Enhancements

### Planned Features
1. **Dynamic Model Selection**: Choose models based on content type
2. **Custom Model Weights**: Adjust priority based on performance
3. **Batch Processing**: Handle multiple PDFs efficiently  
4. **Advanced Analytics**: Detailed extraction pattern analysis
5. **Model Fine-tuning**: Optimize prompts based on success rates

## Summary

This OpenRouter integration provides QuizBattle with:
- **Robust AI-powered extraction** using 24+ models
- **Intelligent fallback systems** ensuring reliability
- **Comprehensive monitoring** for optimization
- **Backward compatibility** with existing workflows
- **Enhanced question quality** with hints and classification

The system is production-ready and provides significant improvements over the previous single-provider approach, offering better reliability, more extraction options, and detailed analytics for continuous improvement.

---

**Technical Support**: Check debug endpoints and MongoDB logs for detailed troubleshooting information.
**API Documentation**: OpenRouter API docs at https://openrouter.ai/docs
**Model Updates**: The model list is automatically maintained and can be extended as needed.