#!/usr/bin/env python3
"""
Enhanced Application Filler
Addresses common application barriers: cookie consent, apply buttons, external portals, and dynamic content.
"""

import sys
import os
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from urllib.parse import urlparse

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ApplicationFiller import responses, ApplicationFiller

class EnhancedApplicationFiller(ApplicationFiller):
    def __init__(self, link="", model="llama3.2", headless=False, slow_mode=False, 
                 resume_path="AdiPrabs_SWE.docx", reference_doc_path="Profile.txt", 
                 company_name="", job_title=""):
        # Initialize parent class
        super().__init__(link, model, headless, slow_mode, resume_path, reference_doc_path, company_name, job_title)
        
        # Ensure driver is initialized
        if not hasattr(self, 'driver') or self.driver is None:
            self.setup_driver()
        
        # Load enhanced configurations
        self.enhanced_configs = self._load_enhanced_configs()
        
    def _load_enhanced_configs(self):
        """Load enhanced configurations for different portals and patterns"""
        return {
            # Cookie consent patterns
            'cookie_consent': {
                'selectors': [
                    'button[data-testid="cookie-accept"]',
                    'button[data-testid="accept-cookies"]',
                    '.cookie-accept',
                    '.accept-cookies',
                    'button:contains("Accept")',
                    'button:contains("Accept All")',
                    'button:contains("I accept")',
                    'button:contains("Got it")',
                    'button:contains("Continue")',
                    'button:contains("OK")'
                ],
                'text_patterns': ['accept', 'agree', 'continue', 'ok', 'got it', 'i understand']
            },
            
            # Apply button patterns
            'apply_buttons': {
                'selectors': [
                    'button:contains("Apply")',
                    'button:contains("Apply Now")',
                    'button:contains("Submit Application")',
                    'button:contains("Start Application")',
                    'a:contains("Apply")',
                    'a:contains("Apply Now")',
                    '.apply-button',
                    '.btn-apply',
                    '[data-testid="apply-button"]'
                ],
                'text_patterns': ['apply', 'application', 'submit application', 'start application']
            },
            
            # Portal-specific configurations
            'portals': {
                'greenhouse': {
                    'cookie_selector': 'button[data-testid="cookie-accept"]',
                    'apply_selector': 'button[data-testid="apply-button"]',
                    'form_selector': '#application-form',
                    'wait_for_form': True,
                    'dynamic_content': True
                },
                'smartrecruiters': {
                    'cookie_selector': '.cookie-accept',
                    'apply_selector': '.apply-button',
                    'form_selector': '.application-form',
                    'wait_for_form': True,
                    'dynamic_content': True
                },
                'workday': {
                    'cookie_selector': '.cookie-accept',
                    'apply_selector': '[data-automation-id="apply-button"]',
                    'form_selector': '[data-automation-id="application-form"]',
                    'wait_for_form': True,
                    'dynamic_content': True
                },
                'lever': {
                    'cookie_selector': '.cookie-accept',
                    'apply_selector': '.apply-button',
                    'form_selector': '.application-form',
                    'wait_for_form': True,
                    'dynamic_content': True
                }
            }
        }
    
    def run_enhanced_application(self):
        """Run enhanced application process with barrier handling"""
        print(f"🚀 Starting enhanced application for: {self.company_name}")
        print(f"🔗 URL: {self.link}")
        
        try:
            # Navigate to the page
            self.driver.get(self.link)
            time.sleep(3)
            
            # Step 1: Handle cookie consent
            if self._handle_cookie_consent():
                print("✅ Cookie consent handled")
            
            # Step 2: Identify portal type
            portal_type = self._identify_portal_type()
            if portal_type:
                print(f"🌐 Detected portal: {portal_type}")
            
            # Step 3: Handle apply button if needed
            if self._handle_apply_button(portal_type):
                print("✅ Apply button handled")
            
            # Step 4: Wait for dynamic content
            if self._wait_for_dynamic_content(portal_type):
                print("✅ Dynamic content loaded")
            
            # Step 5: Fill the form
            if self._fill_enhanced_form(portal_type):
                print("✅ Form filled successfully")
            
            # Step 6: Submit the application
            if self._submit_enhanced_application(portal_type):
                print("✅ Application submitted successfully")
                return True
            else:
                print("❌ Application submission failed")
                return False
                
        except Exception as e:
            print(f"❌ Error during enhanced application: {e}")
            return False
    
    def _handle_cookie_consent(self):
        """Handle cookie consent banners"""
        print("🍪 Checking for cookie consent...")
        
        try:
            # Try portal-specific cookie selectors first
            portal_type = self._identify_portal_type()
            if portal_type and portal_type in self.enhanced_configs['portals']:
                portal_config = self.enhanced_configs['portals'][portal_type]
                if portal_config.get('cookie_selector'):
                    try:
                        cookie_button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, portal_config['cookie_selector']))
                        )
                        cookie_button.click()
                        time.sleep(2)
                        return True
                    except:
                        pass
            
            # Try general cookie consent patterns
            cookie_texts = self.enhanced_configs['cookie_consent']['text_patterns']
            
            for text in cookie_texts:
                try:
                    # Try button with text
                    buttons = self.driver.find_elements(By.XPATH, f"//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text}')]")
                    
                    for button in buttons:
                        if button.is_displayed() and button.is_enabled():
                            print(f"   Clicking cookie button: {button.text}")
                            button.click()
                            time.sleep(2)
                            return True
                            
                except Exception as e:
                    continue
            
            # Try CSS selectors
            for selector in self.enhanced_configs['cookie_consent']['selectors']:
                try:
                    cookie_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if cookie_button.is_displayed() and cookie_button.is_enabled():
                        print(f"   Clicking cookie button with selector: {selector}")
                        cookie_button.click()
                        time.sleep(2)
                        return True
                except:
                    continue
            
            print("   No cookie consent found or already handled")
            return False
            
        except Exception as e:
            print(f"   Error handling cookie consent: {e}")
            return False
    
    def _identify_portal_type(self):
        """Identify the type of application portal"""
        current_url = self.driver.current_url.lower()
        
        if 'greenhouse' in current_url:
            return 'greenhouse'
        elif 'smartrecruiters' in current_url:
            return 'smartrecruiters'
        elif 'workday' in current_url:
            return 'workday'
        elif 'lever' in current_url:
            return 'lever'
        elif 'bamboohr' in current_url:
            return 'bamboohr'
        else:
            return None
    
    def _handle_apply_button(self, portal_type):
        """Handle apply button if form is not immediately visible"""
        print("🎯 Checking for apply button...")
        
        try:
            # Check if form is already visible
            forms = self.driver.find_elements(By.TAG_NAME, "form")
            if forms:
                print("   Form already visible, no apply button needed")
                return True
            
            # Try portal-specific apply button
            if portal_type and portal_type in self.enhanced_configs['portals']:
                portal_config = self.enhanced_configs['portals'][portal_type]
                if portal_config.get('apply_selector'):
                    try:
                        apply_button = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, portal_config['apply_selector']))
                        )
                        print(f"   Clicking apply button: {apply_button.text}")
                        apply_button.click()
                        time.sleep(3)
                        return True
                    except:
                        pass
            
            # Try general apply button patterns
            apply_texts = self.enhanced_configs['apply_buttons']['text_patterns']
            
            for text in apply_texts:
                try:
                    # Try button with text
                    buttons = self.driver.find_elements(By.XPATH, f"//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text}')]")
                    
                    for button in buttons:
                        if button.is_displayed() and button.is_enabled():
                            print(f"   Clicking apply button: {button.text}")
                            button.click()
                            time.sleep(3)
                            return True
                            
                except Exception as e:
                    continue
            
            # Try links with apply text
            for text in apply_texts:
                try:
                    links = self.driver.find_elements(By.XPATH, f"//a[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text}')]")
                    
                    for link in links:
                        if link.is_displayed() and link.is_enabled():
                            print(f"   Clicking apply link: {link.text}")
                            link.click()
                            time.sleep(3)
                            return True
                            
                except Exception as e:
                    continue
            
            print("   No apply button found or form already visible")
            return False
            
        except Exception as e:
            print(f"   Error handling apply button: {e}")
            return False
    
    def _wait_for_dynamic_content(self, portal_type):
        """Wait for dynamic content to load"""
        print("⏳ Waiting for dynamic content...")
        
        try:
            # Portal-specific waiting
            if portal_type and portal_type in self.enhanced_configs['portals']:
                portal_config = self.enhanced_configs['portals'][portal_type]
                if portal_config.get('wait_for_form'):
                    try:
                        form_selector = portal_config.get('form_selector', 'form')
                        WebDriverWait(self.driver, 15).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, form_selector))
                        )
                        print(f"   Form loaded for {portal_type} portal")
                        return True
                    except:
                        pass
            
            # General waiting for forms
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.TAG_NAME, "form"))
                )
                print("   Form loaded")
                return True
            except:
                pass
            
            # Wait for any input fields
            try:
                WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.TAG_NAME, "input"))
                )
                print("   Input fields loaded")
                return True
            except:
                pass
            
            print("   No dynamic content detected or already loaded")
            return False
            
        except Exception as e:
            print(f"   Error waiting for dynamic content: {e}")
            return False
    
    def _fill_enhanced_form(self, portal_type):
        """Fill the form with enhanced field mapping"""
        print("📝 Filling enhanced form...")
        
        try:
            # Get all input fields
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            selects = self.driver.find_elements(By.TAG_NAME, "select")
            textareas = self.driver.find_elements(By.TAG_NAME, "textarea")
            
            print(f"   Found {len(inputs)} inputs, {len(selects)} selects, {len(textareas)} textareas")
            
            # Fill input fields
            filled_count = 0
            for input_field in inputs:
                if self._fill_input_field(input_field):
                    filled_count += 1
            
            # Fill select fields
            for select_field in selects:
                if self._fill_select_field(select_field):
                    filled_count += 1
            
            # Fill textarea fields
            for textarea_field in textareas:
                if self._fill_textarea_field(textarea_field):
                    filled_count += 1
            
            print(f"   Filled {filled_count} fields")
            return filled_count > 0
            
        except Exception as e:
            print(f"   Error filling form: {e}")
            return False
    
    def _fill_input_field(self, input_field):
        """Fill a single input field with enhanced mapping"""
        try:
            input_type = input_field.get_attribute('type')
            input_name = input_field.get_attribute('name') or ''
            input_id = input_field.get_attribute('id') or ''
            input_placeholder = input_field.get_attribute('placeholder') or ''
            
            # Skip hidden, submit, and button inputs
            if input_type in ['hidden', 'submit', 'button', 'image']:
                return False
            
            # Map field to response data
            field_mapping = self._map_field_to_response(input_name, input_id, input_placeholder)
            
            if field_mapping and field_mapping in responses:
                value = responses[field_mapping]
                
                # Clear and fill the field
                input_field.clear()
                input_field.send_keys(value)
                
                print(f"     Filled {input_name or input_id}: {field_mapping} = {value}")
                return True
            
            return False
            
        except Exception as e:
            return False
    
    def _fill_select_field(self, select_field):
        """Fill a single select field"""
        try:
            select_name = select_field.get_attribute('name') or ''
            select_id = select_field.get_attribute('id') or ''
            
            # Map field to response data
            field_mapping = self._map_field_to_response(select_name, select_id, '')
            
            if field_mapping and field_mapping in responses:
                value = responses[field_mapping]
                
                # Find and select the option
                options = select_field.find_elements(By.TAG_NAME, "option")
                for option in options:
                    option_text = option.text.strip()
                    if value.lower() in option_text.lower() or option_text.lower() in value.lower():
                        option.click()
                        print(f"     Selected {select_name or select_id}: {field_mapping} = {option_text}")
                        return True
            
            return False
            
        except Exception as e:
            return False
    
    def _fill_textarea_field(self, textarea_field):
        """Fill a single textarea field"""
        try:
            textarea_name = textarea_field.get_attribute('name') or ''
            textarea_id = textarea_field.get_attribute('id') or ''
            textarea_placeholder = textarea_field.get_attribute('placeholder') or ''
            
            # Map field to response data
            field_mapping = self._map_field_to_response(textarea_name, textarea_id, textarea_placeholder)
            
            if field_mapping and field_mapping in responses:
                value = responses[field_mapping]
                
                # Clear and fill the field
                textarea_field.clear()
                textarea_field.send_keys(value)
                
                print(f"     Filled {textarea_name or textarea_id}: {field_mapping} = {value}")
                return True
            
            return False
            
        except Exception as e:
            return False
    
    def _map_field_to_response(self, name, id, placeholder):
        """Map field attributes to response data"""
        field_text = f"{name} {id} {placeholder}".lower()
        
        # Enhanced field mappings based on analysis
        mappings = {
            'first name': 'first name',
            'firstname': 'first name',
            'fname': 'first name',
            'given name': 'first name',
            
            'last name': 'last name',
            'lastname': 'last name',
            'lname': 'last name',
            'surname': 'last name',
            'family name': 'last name',
            
            'full name': 'full name',
            'name': 'full name',
            
            'email': 'email',
            'email address': 'email',
            'e-mail': 'email',
            
            'phone': 'phone',
            'telephone': 'phone',
            'mobile': 'phone',
            'cell': 'phone',
            
            'university': 'university',
            'college': 'university',
            'school': 'university',
            'institution': 'university',
            
            'degree': 'degree',
            'qualification': 'degree',
            'education': 'degree',
            
            'major': 'major',
            'field of study': 'major',
            'subject': 'major',
            
            'graduation year': 'graduation year',
            'grad year': 'graduation year',
            'year of graduation': 'graduation year',
            
            'gpa': 'gpa',
            'grade point average': 'gpa',
            'grade': 'gpa',
            
            'linkedin': 'linkedin',
            'linkedin profile': 'linkedin',
            'linkedin url': 'linkedin',
            
            'github': 'github',
            'github profile': 'github',
            'github url': 'github',
            
            'city': 'city',
            'location': 'city',
            
            'country': 'country',
            'nation': 'country',
            
            'sponsorship': 'united kingdom need sponsorship',
            'work authorization': 'united kingdom need sponsorship',
            'visa': 'united kingdom need sponsorship'
        }
        
        for pattern, response_field in mappings.items():
            if pattern in field_text:
                return response_field
        
        return None
    
    def _submit_enhanced_application(self, portal_type):
        """Submit the application with enhanced handling"""
        print("📤 Submitting application...")
        
        try:
            # Try to find submit button
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:contains("Submit")',
                'button:contains("Submit Application")',
                'button:contains("Apply")',
                '.submit-button',
                '.btn-submit',
                '[data-testid="submit-button"]'
            ]
            
            for selector in submit_selectors:
                try:
                    submit_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if submit_button.is_displayed() and submit_button.is_enabled():
                        print(f"   Clicking submit button: {submit_button.text}")
                        submit_button.click()
                        time.sleep(5)
                        return True
                except:
                    continue
            
            # Try form submission
            forms = self.driver.find_elements(By.TAG_NAME, "form")
            if forms:
                try:
                    forms[0].submit()
                    print("   Form submitted")
                    time.sleep(5)
                    return True
                except:
                    pass
            
            print("   No submit button found")
            return False
            
        except Exception as e:
            print(f"   Error submitting application: {e}")
            return False

def test_enhanced_application():
    """Test the enhanced application filler"""
    print("🧪 Testing Enhanced Application Filler")
    print("=" * 50)
    
    # Test with a known failing application
    test_url = "https://job-boards.greenhouse.io/ctccampusboard/jobs/4577583005?utm_source=Trackr&utm_medium=tracker&utm_campaign=UK_Finance_2026&gh_src=Trackr"
    
    filler = None
    try:
        filler = EnhancedApplicationFiller(
            link=test_url,
            headless=False,
            slow_mode=True,
            company_name="CTC Campus",
            job_title="Quant Trading Internship"
        )
        
        success = filler.run_enhanced_application()
        
        if success:
            print("✅ Enhanced application test successful!")
        else:
            print("❌ Enhanced application test failed!")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
    finally:
        if filler and hasattr(filler, 'driver') and filler.driver:
            filler.driver.quit()

if __name__ == "__main__":
    test_enhanced_application()
