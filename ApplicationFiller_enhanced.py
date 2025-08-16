responses = {
  "first name": "Aditya",
  "last name": "Prabakaran",
  "email": "aditya.prabakaran@gmail.com",
  "phone": "+447587460771/+44 (0) 7587460771/7587460771",
  "preferred contact method": "email",
  "preferred name": "Adi",
  "school": "Imperial College London",
  "degree": "MEng/ Master of Engineering",
  "city": "London",
  "country": "United Kingdom",
  "major": "Computer Science",
  "start date": "2020-09-01",
  "end date": "2024-05-15",
  "linkedin": "https://www.linkedin.com/in/adiprabs",
  "github": "https://github.com/TheDarkEyezor",
  "profile": "https://adiprabs.vercel.app/",
  "united states need sponsorship": "yes",
  "united kingdom need sponsorship": "no",
  "military service": "none",
  "disability": "none",
  "gender": "male",
  "sexuality": "straight/cis",
}

import os
import json
import requests
from pathlib import Path

class ApplicationFiller:
  """
  Enhanced automated job application form filler with intelligent dropdown handling,
  Ollama LLM integration for RAG-based responses, and automatic file upload capabilities.
  
  Features:
  - Smart dropdown option matching
  - Ollama LLM integration for unknown questions
  - RAG document support
  - Automatic resume/CV file upload
  - Visual form filling with real-time feedback
  """
  
  def __init__(self, link="", model="llama3.2", headless=True, slow_mode=False, 
               ollama_base_url="http://localhost:11434", resume_path=None, 
               reference_doc_path=None):
    self.link = link
    self.model = model
    self.driver = None
    self.headless = headless
    self.slow_mode = slow_mode
    self.ollama_base_url = ollama_base_url
    self.resume_path = resume_path
    self.reference_doc_path = reference_doc_path
    self.reference_content = self._load_reference_document()
    
  def _load_reference_document(self):
    """Load reference document for RAG context"""
    if self.reference_doc_path and os.path.exists(self.reference_doc_path):
      try:
        with open(self.reference_doc_path, 'r', encoding='utf-8') as f:
          content = f.read()
        print(f"📄 Loaded reference document: {self.reference_doc_path}")
        return content
      except Exception as e:
        print(f"❌ Error loading reference document: {e}")
    return ""
    
  def initialize_driver(self):
    """Initialize the web driver for browser automation"""
    try:
      from selenium import webdriver
      from selenium.webdriver.chrome.options import Options
      from webdriver_manager.chrome import ChromeDriverManager
      from selenium.webdriver.chrome.service import Service
      
      chrome_options = Options()
      chrome_options.add_argument("--no-sandbox")
      chrome_options.add_argument("--disable-dev-shm-usage")
      chrome_options.add_argument("--disable-gpu")
      chrome_options.add_argument("--remote-debugging-port=9222")
      
      # Only add headless mode if requested
      if self.headless:
        chrome_options.add_argument("--headless")
        print("Running in headless mode (no browser window)")
      else:
        print("Running with visible browser window")
      
      service = Service(ChromeDriverManager().install())
      self.driver = webdriver.Chrome(service=service, options=chrome_options)
      return True
    except Exception as chrome_error:
      print(f"Chrome driver failed: {chrome_error}")
      
      # Try Firefox as fallback
      try:
        from selenium import webdriver
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
        from webdriver_manager.firefox import GeckoDriverManager
        from selenium.webdriver.firefox.service import Service as FirefoxService
        
        firefox_options = FirefoxOptions()
        if self.headless:
          firefox_options.add_argument("--headless")
          print("Using Firefox in headless mode")
        else:
          print("Using Firefox with visible browser window")
        
        service = FirefoxService(GeckoDriverManager().install())
        self.driver = webdriver.Firefox(service=service, options=firefox_options)
        print("Using Firefox driver as fallback")
        return True
      except Exception as firefox_error:
        print(f"Firefox driver also failed: {firefox_error}")
        print("Please install Chrome or Firefox browser")
        return False

  def get_dropdown_options(self, select_element):
    """Extract all available options from a dropdown element"""
    try:
      from selenium.webdriver.support.ui import Select
      select = Select(select_element)
      options = []
      for option in select.options:
        option_text = option.text.strip()
        option_value = option.get_attribute("value")
        if option_text and option_text.lower() not in ["select...", "choose...", "select one", ""]:
          options.append({
            "text": option_text,
            "value": option_value,
            "element": option
          })
      return options
    except Exception as e:
      print(f"❌ Error getting dropdown options: {e}")
      return []

  def find_best_dropdown_match(self, question_text, options, response_value):
    """Find the best matching option in a dropdown based on response value and question context"""
    if not options or not response_value:
      return None
    
    response_lower = response_value.lower()
    question_lower = question_text.lower()
    
    # Exact matches first
    for option in options:
      if option["text"].lower() == response_lower:
        return option
    
    # Partial matches
    for option in options:
      option_text_lower = option["text"].lower()
      if response_lower in option_text_lower or option_text_lower in response_lower:
        return option
    
    # Context-based matching for specific question types
    if "sponsorship" in question_lower:
      if response_value.lower() == "yes":
        for option in options:
          if any(word in option["text"].lower() for word in ["yes", "required", "need", "true"]):
            return option
      elif response_value.lower() == "no":
        for option in options:
          if any(word in option["text"].lower() for word in ["no", "not required", "false", "don't"]):
            return option
    
    # For military service
    if "military" in question_lower:
      if response_value.lower() == "no":
        for option in options:
          if any(word in option["text"].lower() for word in ["no", "never", "not served", "none"]):
            return option
    
    # Generic Yes/No matching
    if response_value.lower() in ["yes", "no"]:
      for option in options:
        if option["text"].lower().startswith(response_value.lower()):
          return option
    
    return None

  def query_ollama(self, question_text, context=""):
    """Query Ollama LLM for generating responses to unknown questions"""
    try:
      # Prepare the prompt with context
      system_prompt = f"""You are helping fill out a job application form. 
      
User Profile:
- Name: Aditya Prabakaran
- Education: MEng Computer Science from Imperial College London (2020-2024)
- Location: London, UK
- Email: aditya.prabakaran@gmail.com
- LinkedIn: https://www.linkedin.com/in/adiprabs
- GitHub: https://github.com/TheDarkEyezor
- Portfolio: https://adiprabs.vercel.app/
- US Work Authorization: Requires sponsorship
- UK Work Authorization: No sponsorship needed
- Military Service: None

{f'Reference Document Context: {context}' if context else ''}

Answer the following job application question concisely and professionally. 
If it's a yes/no question, respond with just "Yes" or "No".
If it's asking for specific information, provide a brief, relevant answer.
If you need to make assumptions, make reasonable ones based on the profile above.

Question: {question_text}

Response:"""

      payload = {
        "model": self.model,
        "prompt": system_prompt,
        "stream": False,
        "options": {
          "temperature": 0.1,  # Low temperature for consistent answers
          "top_p": 0.9
        }
      }
      
      response = requests.post(
        f"{self.ollama_base_url}/api/generate",
        json=payload,
        timeout=30
      )
      
      if response.status_code == 200:
        result = response.json()
        answer = result.get("response", "").strip()
        print(f"🤖 Ollama generated response for '{question_text}': {answer}")
        return answer
      else:
        print(f"❌ Ollama API error: {response.status_code}")
        return ""
        
    except requests.exceptions.ConnectionError:
      print("❌ Could not connect to Ollama. Is it running? Start with: ollama serve")
      return ""
    except Exception as e:
      print(f"❌ Error querying Ollama: {e}")
      return ""

  def handle_file_upload(self, element, field_text):
    """Handle file upload fields, specifically for resume/CV"""
    try:
      field_lower = field_text.lower()
      
      # Check if this is a resume/CV upload field
      if any(keyword in field_lower for keyword in ["resume", "cv", "curriculum", "upload"]):
        if self.resume_path and os.path.exists(self.resume_path):
          print(f"📎 Uploading resume: {self.resume_path}")
          element.send_keys(os.path.abspath(self.resume_path))
          return True
        else:
          print(f"❌ Resume path not provided or file not found: {self.resume_path}")
          return False
      
      return False
    except Exception as e:
      print(f"❌ Error handling file upload: {e}")
      return False

  def find_matching_response(self, field_text):
    """Find matching response from the responses dictionary"""
    field_text_lower = field_text.lower()
    
    # Direct mapping for common fields
    field_mappings = {
      "first name": "first name",
      "last name": "last name", 
      "email": "email",
      "phone": "phone",
      "location": "city",
      "city": "city",
      "country": "country",
      "school": "school",
      "degree": "degree",
      "major": "major",
      "linkedin": "linkedin",
      "github": "github",
      "profile": "profile"
    }
    
    # Check for direct matches
    for key, response_key in field_mappings.items():
      if key in field_text_lower:
        return responses.get(response_key, "")
    
    # Check for sponsorship questions
    if "sponsorship" in field_text_lower and "united states" in field_text_lower:
      return "Yes" if responses.get("united states need sponsorship") == "yes" else "No"
    
    if "sponsorship" in field_text_lower and "united kingdom" in field_text_lower:
      return "Yes" if responses.get("united kingdom need sponsorship") == "yes" else "No"
    
    # Check for military service
    if "military" in field_text_lower:
      return "No" if responses.get("military service") == "none" else "Yes"
    
    # Check for work authorization
    if "authorized" in field_text_lower and "work" in field_text_lower:
      if "united states" in field_text_lower:
        return "No" if responses.get("united states need sponsorship") == "yes" else "Yes"
      return "Yes"  # Default for other countries
    
    # Check for privacy/consent questions
    if "privacy" in field_text_lower or "consent" in field_text_lower:
      return "Yes"
    
    # Check for previous application
    if "previously applied" in field_text_lower:
      return "No"  # Default assumption
    
    return None
  
  def fill_response(self, element):
    """Fill a form element with appropriate response using enhanced logic"""
    try:
      import time
      from selenium.webdriver.common.by import By
      from selenium.webdriver.support.ui import Select
      from selenium.webdriver.support.ui import WebDriverWait
      from selenium.webdriver.support import expected_conditions as EC
      
      if not self.driver:
        print("❌ Driver not initialized")
        return False
      
      # Get the label or placeholder text to determine what to fill
      label_text = ""
      
      # Try to find associated label
      try:
        label_element = element.find_element(By.XPATH, ".//preceding::label[1]")
        label_text = label_element.text
      except:
        try:
          # Try aria-labelledby
          aria_labelledby = element.get_attribute("aria-labelledby")
          if aria_labelledby:
            label_element = self.driver.find_element(By.ID, aria_labelledby)
            label_text = label_element.text
        except:
          try:
            # Try placeholder
            label_text = element.get_attribute("placeholder") or ""
          except:
            try:
              # Try aria-label
              label_text = element.get_attribute("aria-label") or ""
            except:
              try:
                # Try nearby text
                label_text = element.get_attribute("name") or ""
              except:
                pass
      
      if not label_text:
        print("⚠️ Could not determine field label")
        return False
      
      # Handle file upload fields first
      input_type = element.get_attribute("type")
      if input_type == "file":
        return self.handle_file_upload(element, label_text)
      
      # Find matching response from predefined responses
      response_value = self.find_matching_response(label_text)
      
      # If no predefined response found, use Ollama LLM
      if response_value is None:
        response_value = self.query_ollama(label_text, self.reference_content)
      
      if response_value:
        # Highlight the field before filling (visual feedback)
        original_style = ""
        if not self.headless and self.driver:
          original_style = element.get_attribute("style") or ""
          self.driver.execute_script("arguments[0].style.border='3px solid red'", element)
          print(f"🔍 Filling field '{label_text}' with: {response_value}")
        
        # Add delay for visual effect if in slow mode
        if self.slow_mode and not self.headless:
          time.sleep(1)
        
        # Handle different input types
        tag_name = element.tag_name.lower()
        
        if tag_name == "select":
          # Enhanced dropdown handling
          options = self.get_dropdown_options(element)
          if options:
            print(f"📋 Found {len(options)} dropdown options: {[opt['text'] for opt in options[:5]]}")
            
            best_match = self.find_best_dropdown_match(label_text, options, response_value)
            if best_match:
              select = Select(element)
              try:
                select.select_by_visible_text(best_match["text"])
                print(f"✅ Selected dropdown option: {best_match['text']}")
              except:
                try:
                  select.select_by_value(best_match["value"])
                  print(f"✅ Selected dropdown option by value: {best_match['value']}")
                except:
                  print(f"❌ Could not select dropdown option: {best_match['text']}")
            else:
              print(f"❌ No matching dropdown option found for: {response_value}")
              # List available options for debugging
              print(f"Available options: {[opt['text'] for opt in options]}")
          
        elif tag_name == "input" and input_type in ["text", "email", "tel"]:
          element.clear()
          if self.slow_mode and not self.headless:
            # Type character by character for visual effect
            for char in response_value:
              element.send_keys(char)
              time.sleep(0.1)
          else:
            element.send_keys(response_value)
            
        elif tag_name == "textarea":
          element.clear()
          if self.slow_mode and not self.headless:
            # Type character by character for visual effect
            for char in response_value:
              element.send_keys(char)
              time.sleep(0.05)
          else:
            element.send_keys(response_value)
        
        # Restore original border style and add completion indicator
        if not self.headless and self.driver:
          time.sleep(0.5)  # Brief pause to show completion
          self.driver.execute_script("arguments[0].style.border='3px solid green'", element)
          time.sleep(0.5)
          self.driver.execute_script(f"arguments[0].style='{original_style}'", element)
          print(f"✅ Completed field: {label_text}")
        
        return True
      else:
        print(f"⚠️ No response generated for field: {label_text}")
      
    except Exception as e:
      print(f"❌ Error filling element: {e}")
      return False
    
    return False
  
  def fill_form(self):
    """Fill the entire form on the current page"""
    try:
      from selenium.webdriver.common.by import By
      
      if not self.driver:
        if not self.initialize_driver():
          return False
      
      if not self.driver:
        print("❌ Failed to initialize driver")
        return False
      
      print(f"🌐 Navigating to: {self.link}")
      self.driver.get(self.link)
      
      # Add a small delay to let the page load
      import time
      time.sleep(3)
      
      print("🔍 Searching for form fields...")
      # Find all form elements
      input_fields = self.driver.find_elements(By.TAG_NAME, "input")
      select_fields = self.driver.find_elements(By.TAG_NAME, "select")
      textarea_fields = self.driver.find_elements(By.TAG_NAME, "textarea")
      
      filled_count = 0
      
      print(f"Found {len(input_fields)} input fields, {len(select_fields)} select fields, {len(textarea_fields)} textarea fields")
      
      # Fill input fields (including file uploads)
      for i, field in enumerate(input_fields):
        field_type = field.get_attribute("type")
        if field.is_displayed() and field_type in ["text", "email", "tel", "file"]:
          if self.fill_response(field):
            filled_count += 1
          if self.slow_mode and not self.headless:
            time.sleep(0.5)  # Pause between fields
      
      # Fill select fields (dropdowns)
      for field in select_fields:
        if field.is_displayed():
          if self.fill_response(field):
            filled_count += 1
          if self.slow_mode and not self.headless:
            time.sleep(0.5)
      
      # Fill textarea fields
      for field in textarea_fields:
        if field.is_displayed():
          if self.fill_response(field):
            filled_count += 1
          if self.slow_mode and not self.headless:
            time.sleep(0.5)
      
      print(f"✅ Successfully filled {filled_count} fields")
      
      if not self.headless:
        print("⏸️  Pausing for 3 seconds to review filled form...")
        time.sleep(3)
      
      return True
      
    except Exception as e:
      print(f"❌ Error filling form: {e}")
      return False
  
  def submit(self):
    """Submit the form or return the link if unable to complete"""
    try:
      if self.fill_form():
        # Find and click submit button
        from selenium.webdriver.common.by import By
        
        if not self.driver:
          print("❌ Driver not initialized")
          return self.link
        
        print("🔍 Looking for submit button...")
        submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        if submit_button.is_displayed() and submit_button.is_enabled():
          if not self.headless and self.driver:
            # Highlight submit button
            self.driver.execute_script("arguments[0].style.border='3px solid blue'", submit_button)
            print("🎯 Found submit button - clicking in 2 seconds...")
            import time
            time.sleep(2)
          
          submit_button.click()
          print("✅ Form submitted successfully")
          return True
      
    except Exception as e:
      print(f"❌ Error during submission: {e}")
    
    finally:
      if self.driver and not self.headless:
        print("⏸️  Keeping browser open for 5 seconds to see results...")
        import time
        time.sleep(5)
      if self.driver:
        self.driver.quit()
    
    # Return the link if unable to complete the process
    print(f"❌ Unable to complete form automatically. Please visit: {self.link}")
    return self.link
  
  def close_driver(self):
    """Clean up the web driver"""
    if self.driver:
      self.driver.quit()
      self.driver = None


if __name__ == "__main__":
  # Example usage with enhanced features
  job_url = "https://job-boards.greenhouse.io/point72/jobs/8018862002?gh_jid=8018862002&gh_src=97fa02a42us&jobCode=CSS-0013383&location=New+York"
  
  # Create an instance with enhanced features
  print("🚀 Starting Enhanced ApplicationFiller...")
  filler = ApplicationFiller(
    link=job_url,
    headless=False,          # Show browser for demo
    slow_mode=True,          # Slow mode for visual effects
    model="llama3.2",        # Ollama model to use
    resume_path=None,        # Path to resume file (set later)
    reference_doc_path=None  # Path to reference document (set later)
  )
  
  # Try to fill and submit the form
  result = filler.submit()
  
  if isinstance(result, str):
    print(f"📋 Please complete the application manually at: {result}")
  else:
    print("🎉 Application submitted successfully!")
  
  # Clean up
  filler.close_driver()
