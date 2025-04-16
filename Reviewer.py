import requests
import os
import json
from typing import Optional, Dict, Any

class Reviewer:
  def __init__(self, model_name="llama3", base_url=None):
    """Initialize the reviewer with an Ollama model name.
    
    Args:
        model_name: Name of the Ollama model to use (default: "llama3")
        base_url: Base URL for Ollama API (default: http://localhost:11434)
    """
    self.model_name = model_name
    self.ollama_base_url = base_url or os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    self.original_prompt = None  # Store the original prompt
    print(f"Initialized Reviewer with Ollama model: {model_name}")
    
  def changeModel(self, model_name, **kwargs):
    """Change the Ollama model being used.
    
    Args:
        model_name: Name of the Ollama model to use
    """
    print(f"Changing model to {model_name}")
    self.model_name = model_name
    
  def set_original_prompt(self, prompt):
    """Set the original prompt for future review context.
    
    Args:
        prompt: The original prompt/request that led to the code being reviewed
    """
    self.original_prompt = prompt
    print("Original prompt has been set for future reviews")
    
  def review(self, test_output, prompt=None, context=""):
    """Review test output using Ollama.
    
    Args:
        test_output: Output from tests to analyze (can be text or path to screenshot)
        prompt: Custom prompt to use for analysis (optional)
        context: Additional context about the tests or project
        
    Returns:
        Analysis from the LLM
    """
    try:
      # If test_output is a file path, read the file content or use it for context
      if isinstance(test_output, str) and os.path.exists(test_output):
        context += f"\nScreenshot taken: {test_output}"
        test_output = f"Screenshot available at {test_output}"
      
      # Construct the prompt for Ollama
      if prompt is None:
        prompt = "Analyze this test output and identify any issues."
      
      full_prompt = self._construct_review_prompt(test_output, prompt, context)
      
      payload = {
        "model": self.model_name,
        "prompt": full_prompt,
        "stream": False
      }
      
      print(f"Sending request to Ollama ({self.model_name})...")
      response = requests.post(
        f"{self.ollama_base_url}/api/generate",
        json=payload
      )
      
      if response.status_code != 200:
        return f"Error: Ollama API returned status code {response.status_code}: {response.text}"
      
      result = response.json()
      return result.get("response", "No response received from model")
      
    except Exception as e:
      print(f"ERROR: Failed to get response from Ollama: {e}")
      return f"Error: Could not get response from Ollama: {e}"
  
  def _construct_review_prompt(self, test_output, prompt, context=""):
    """Construct a prompt for the LLM to analyze test output."""
    full_prompt = "You're a code review assistant analyzing test results.\n\n"
    
    # Add specific instructions for line range formatting and test command formulation
    # Make the instructions more prominent with stronger emphasis
    full_prompt += """CRITICAL FORMATTING REQUIREMENT - MUST FOLLOW:
    
ALWAYS include line numbers in your suggestions using one of these precise formats:
- "Line X: Your comment" (for a single line)
- "Lines X-Y: Your comment" (for a range of lines)

For example:
- "Line 15: Fix the variable declaration to use proper type"
- "Lines 25-30: Replace this loop with a more efficient implementation"

THIS IS MANDATORY: Any code change suggestion WITHOUT line numbers will cause INCORRECT MODIFICATIONS.

Other formatting requirements:
1. Test commands should be carefully constructed to avoid syntax errors:
   - Use proper escaping for special characters
   - Ensure all quotes are properly balanced
   - Avoid characters that need special escaping in the CLI

2. When providing code examples, always indicate the specific lines they should replace.

EXAMPLE REVIEW FORMAT:
```
ISSUE: Description of the issue

Line 42: This function has a bug in the calculation

SUGGESTION: Use this implementation instead:
```python
def fixed_function(x, y):
    return x + y  # Fixed calculation
```
"""
    
    # Include the original prompt if available
    if self.original_prompt:
      full_prompt += "ORIGINAL REQUEST/PROMPT:\n"
      full_prompt += f"{self.original_prompt}\n\n"
      full_prompt += "When reviewing, consider how well the implementation satisfies this original request.\n\n"
    
    if context:
      full_prompt += f"Context: {context}\n\n"
      
    full_prompt += f"{prompt}\n\n"
    full_prompt += "Test output:\n```\n"
    full_prompt += str(test_output)
    full_prompt += "\n```\n\n"
    full_prompt += "Your analysis should include SPECIFIC LINE NUMBERS for any suggested changes:"
    
    return full_prompt

  def get_line_range_format_instructions(self):
    """Returns instructions on how to format line ranges in review comments."""
    return """
CRITICAL - LINE NUMBER FORMAT REQUIREMENT:

When suggesting code changes, you MUST specify exact line numbers using one of these formats:

1. For a single line:
   Line X: [your comment]
   Example: "Line 42: Fix the variable initialization"

2. For a range of lines:
   Lines X-Y: [your comment]
   Example: "Lines 15-20: Refactor this loop for better performance"

ANY CODE SUGGESTION WITHOUT LINE NUMBERS WILL CAUSE ENTIRE FILE REPLACEMENT instead of targeted fixes.

For test commands, ensure they are properly formatted:
   Test command: [command with proper escaping]
   Example: "Test command: python -m pytest test_file.py -v"
   
This precise formatting is required for automated processing of your feedback.
"""

# For backward compatibility with existing code
class ImageReviewer(Reviewer):
  pass

if __name__ == "__main__":
  reviewer = Reviewer("llama3")
  
  # Example of setting and using an original prompt
  reviewer.set_original_prompt("Create a function that validates user credentials")
  
  test_output = """
Running test_user_login... FAILED
Error: AuthenticationError: Invalid credentials
    at auth.py:45 in authenticate_user
    at test_auth.py:23 in test_user_login

Running test_data_retrieval... PASSED
"""
  print(reviewer.review(test_output, "Could you describe the issues in these test results?"))