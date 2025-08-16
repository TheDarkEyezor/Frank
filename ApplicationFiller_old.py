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
  Automated job application form filler.
  
  This class automates the process of filling out job application forms
  by matching form fields with predefined responses and using a RAG agent
  for custom questions.
  
  Attributes:
      link (str): URL of the job application page
      model (str): AI model to use for RAG agent (default: "llama3.2")
      driver: Selenium WebDriver instance
  """
  
  def __init__(self, link="", model="llama3.2", headless=True, slow_mode=False):
    self.link = link
    self.model = model
    self.driver = None
    self.headless = headless
    self.slow_mode = slow_mode
    
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
    """Fill a form element with appropriate response"""
    try:
      import time
      from selenium.webdriver.common.by import By
      from selenium.webdriver.support.ui import Select
      from selenium.webdriver.support.ui import WebDriverWait
      from selenium.webdriver.support import expected_conditions as EC
      
      # Get the label or placeholder text to determine what to fill
      label_text = ""
      
      # Try to find associated label
      try:
        label_element = element.find_element(By.XPATH, ".//preceding::label[1]")
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
            pass
      
      # Find matching response
      response_value = self.find_matching_response(label_text)
      
      if response_value is None:
        # Use RAG agent for custom questions (placeholder for now)
        response_value = self.use_rag_agent(label_text)
      
      if response_value:
        # Highlight the field before filling (visual feedback)
        if not self.headless:
          original_style = element.get_attribute("style")
          self.driver.execute_script("arguments[0].style.border='3px solid red'", element)
          print(f"Filling field '{label_text}' with: {response_value}")
        
        # Add delay for visual effect if in slow mode
        if self.slow_mode and not self.headless:
          time.sleep(1)
        
        # Handle different input types
        tag_name = element.tag_name.lower()
        input_type = element.get_attribute("type")
        
        if tag_name == "input" and input_type in ["text", "email", "tel"]:
          element.clear()
          if self.slow_mode and not self.headless:
            # Type character by character for visual effect
            for char in response_value:
              element.send_keys(char)
              time.sleep(0.1)
          else:
            element.send_keys(response_value)
        elif tag_name == "select":
          select = Select(element)
          # Try to select by visible text first, then by value
          try:
            select.select_by_visible_text(response_value)
          except:
            try:
              select.select_by_value(response_value)
            except:
              pass
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
        if not self.headless:
          time.sleep(0.5)  # Brief pause to show completion
          self.driver.execute_script("arguments[0].style.border='3px solid green'", element)
          time.sleep(0.5)
          self.driver.execute_script(f"arguments[0].style='{original_style or ''}'", element)
        
        return True
      
    except Exception as e:
      print(f"Error filling element: {e}")
      return False
    
    return False
  
  def use_rag_agent(self, question_text):
    """Placeholder for RAG agent to handle custom questions"""
    # TODO: Implement RAG agent integration
    # For now, return empty string for unknown questions
    print(f"RAG agent needed for: {question_text}")
    return ""
  
  def fill_form(self):
    """Fill the entire form on the current page"""
    try:
      from selenium.webdriver.common.by import By
      
      if not self.driver:
        if not self.initialize_driver():
          return False
      
      # Navigate to the job application page
      self.driver.get(self.link)
      
      # Find all input fields
      input_fields = self.driver.find_elements(By.TAG_NAME, "input")
      select_fields = self.driver.find_elements(By.TAG_NAME, "select")
      textarea_fields = self.driver.find_elements(By.TAG_NAME, "textarea")
      
      filled_count = 0
      
      # Fill input fields
      for field in input_fields:
        field_type = field.get_attribute("type")
        if field_type in ["text", "email", "tel"] and field.is_displayed():
          if self.fill_response(field):
            filled_count += 1
      
      # Fill select fields
      for field in select_fields:
        if field.is_displayed():
          if self.fill_response(field):
            filled_count += 1
      
      # Fill textarea fields
      for field in textarea_fields:
        if field.is_displayed():
          if self.fill_response(field):
            filled_count += 1
      
      print(f"Successfully filled {filled_count} fields")
      return True
      
    except Exception as e:
      print(f"Error filling form: {e}")
      return False
  
  def submit(self):
    """Submit the form or return the link if unable to complete"""
    try:
      if self.fill_form():
        # Find and click submit button
        from selenium.webdriver.common.by import By
        
        submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        if submit_button.is_displayed() and submit_button.is_enabled():
          submit_button.click()
          print("Form submitted successfully")
          return True
      
    except Exception as e:
      print(f"Error during submission: {e}")
    
    finally:
      if self.driver:
        self.driver.quit()
    
    # Return the link if unable to complete the process
    print(f"Unable to complete form automatically. Please visit: {self.link}")
    return self.link
  
  def close_driver(self):
    """Clean up the web driver"""
    if self.driver:
      self.driver.quit()
      self.driver = None


if __name__ == "__main__":
  # Example usage
  job_url = "https://job-boards.greenhouse.io/axon/jobs/6684077003"
  
  # Create an instance of ApplicationFiller
  filler = ApplicationFiller(link=job_url)
  
  # Try to fill and submit the form
  result = filler.submit()
  
  if isinstance(result, str):
    print(f"Please complete the application manually at: {result}")
  else:
    print("Application submitted successfully!")
  
  # Clean up
  filler.close_driver()
  filler.close_driver()
