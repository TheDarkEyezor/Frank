# ApplicationFiller

A Python class that automates job application form filling using Selenium WebDriver and intelligent field mapping.

## Features

### ✅ Completed Features

1. **Automated Form Detection & Filling**
   - Automatically detects common form fields (first name, last name, email, phone, etc.)
   - Maps form fields to predefined responses from the `responses` dictionary
   - Handles text inputs, select dropdowns, and textarea fields

2. **Intelligent Field Mapping**
   - Maps common field patterns to appropriate responses
   - Handles sponsorship questions based on country
   - Processes military service, work authorization, and privacy consent questions

3. **Robust Browser Support**
   - Primary support for Chrome with automatic ChromeDriver management
   - Firefox fallback support if Chrome is unavailable
   - Headless mode for background automation

4. **Error Handling & Fallback**
   - Graceful error handling for missing browsers or failed automation
   - Returns the job application link if automation fails
   - Proper cleanup of browser resources

### 🔄 Pre-configured Response Mapping

The class uses the `responses` dictionary to fill forms with your personal information:

```python
responses = {
  "first name": "Aditya",
  "last name": "Prabakaran", 
  "email": "aditya.prabakaran@gmail.com",
  "phone": "+447587460771/+44 (0) 7587460771/7587460771",
  "city": "London",
  "country": "United Kingdom",
  "school": "Imperial College London",
  "degree": "MEng/ Master of Engineering",
  "major": "Computer Science",
  "linkedin": "https://www.linkedin.com/in/adiprabs",
  "github": "https://github.com/TheDarkEyezor",
  "profile": "https://adiprabs.vercel.app/",
  "united states need sponsorship": "yes",
  "united kingdom need sponsorship": "no",
  "military service": "none",
  # ... more fields
}
```

## Usage

### Basic Usage

```python
from ApplicationFiller import ApplicationFiller

# Create an instance with a job application URL
job_url = "https://job-boards.greenhouse.io/point72/jobs/8018862002"
filler = ApplicationFiller(link=job_url)

# Attempt to fill and submit the form
result = filler.submit()

if isinstance(result, str):
    print(f"Please complete manually at: {result}")
else:
    print("Application submitted successfully!")

# Clean up
filler.close_driver()
```

### Advanced Usage

```python
# Custom model specification (for future RAG integration)
filler = ApplicationFiller(link=job_url, model="gpt-4")

# Fill form without submitting
filler.fill_form()

# Manual cleanup
filler.close_driver()
```

## Requirements

Install the required dependencies:

```bash
pip install selenium webdriver-manager
```

## Architecture

### Class Structure

```
ApplicationFiller
├── __init__(link, model)
├── initialize_driver()           # Set up Chrome/Firefox WebDriver
├── find_matching_response()      # Map form fields to responses
├── fill_response(element)        # Fill individual form elements
├── use_rag_agent()              # Placeholder for AI-powered responses
├── fill_form()                  # Fill entire form
├── submit()                     # Main method - fill and submit
└── close_driver()               # Cleanup resources
```

### Field Mapping Logic

1. **Direct Pattern Matching**: Common fields like "first name", "email", etc.
2. **Contextual Mapping**: Sponsorship questions based on country context
3. **Default Responses**: Standard answers for common questions
4. **RAG Fallback**: Placeholder for AI-powered custom question handling

## Tested Compatibility

- ✅ Greenhouse.io job application forms (Point72 example)
- ✅ Standard HTML form elements (input, select, textarea)
- ✅ Chrome and Firefox browsers
- ✅ macOS environment

## Future Enhancements (TODO)

### 🚧 Planned Features

1. **RAG Agent Integration**
   - AI-powered responses for custom questions
   - Context-aware form field interpretation
   - Integration with language models for intelligent responses

2. **Resume Upload Automation**
   - Automatic file upload handling
   - Support for multiple file formats (PDF, DOC, etc.)
   - Resume parsing and field extraction

3. **Enhanced Form Detection**
   - Support for more job board platforms
   - Dynamic form field discovery
   - CAPTCHA handling

4. **Configuration Management**
   - External configuration files
   - Multiple profile support
   - Field mapping customization

## Error Handling

The class includes comprehensive error handling:

- **Browser Issues**: Fallback to Firefox if Chrome fails
- **Missing Elements**: Graceful skipping of unavailable fields  
- **Network Issues**: Timeout handling and retries
- **Automation Failures**: Returns manual completion link

## Security Considerations

- Runs in headless mode by default for privacy
- Sensitive information stored in local variables only
- Proper cleanup of browser sessions
- No data persistence or logging of personal information

## Example Output

```
Testing ApplicationFiller...
Target URL: https://job-boards.greenhouse.io/point72/jobs/8018862002
--------------------------------------------------
Successfully filled 8 fields
Form submitted successfully
✅ Application submitted successfully!
```

This ApplicationFiller class provides a solid foundation for automating job applications while maintaining the flexibility to handle edge cases and custom requirements.
