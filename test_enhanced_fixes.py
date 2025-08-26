#!/usr/bin/env python3
"""
Test Enhanced Application Fixes
Tests the enhanced application filler with focus on barrier handling.
"""

import sys
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ApplicationFiller import responses

class TestEnhancedFixes:
    def __init__(self, headless=False):
        self.headless = headless
        self.driver = None
        self.setup_driver()
        
    def setup_driver(self):
        """Setup Chrome driver"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        return self.driver
    
    def test_cookie_consent_fix(self):
        """Test cookie consent handling"""
        print("🍪 Testing Cookie Consent Fix")
        print("=" * 40)
        
        # Test with a page that has cookie consent
        test_url = "https://job-boards.greenhouse.io/ctccampusboard/jobs/4577583005?utm_source=Trackr&utm_medium=tracker&utm_campaign=UK_Finance_2026&gh_src=Trackr"
        
        try:
            self.driver.get(test_url)
            time.sleep(3)
            
            # Try to handle cookie consent
            success = self._handle_cookie_consent()
            
            if success:
                print("✅ Cookie consent handled successfully")
                return True
            else:
                print("❌ Cookie consent handling failed")
                return False
                
        except Exception as e:
            print(f"❌ Error testing cookie consent: {e}")
            return False
    
    def test_apply_button_fix(self):
        """Test apply button handling"""
        print("\n🎯 Testing Apply Button Fix")
        print("=" * 40)
        
        # Test with a page that requires clicking apply first
        test_url = "https://job-boards.greenhouse.io/ctccampusboard/jobs/4577583005?utm_source=Trackr&utm_medium=tracker&utm_campaign=UK_Finance_2026&gh_src=Trackr"
        
        try:
            self.driver.get(test_url)
            time.sleep(3)
            
            # Handle cookie consent first
            self._handle_cookie_consent()
            
            # Try to handle apply button
            success = self._handle_apply_button()
            
            if success:
                print("✅ Apply button handled successfully")
                return True
            else:
                print("❌ Apply button handling failed")
                return False
                
        except Exception as e:
            print(f"❌ Error testing apply button: {e}")
            return False
    
    def test_form_filling_fix(self):
        """Test enhanced form filling"""
        print("\n📝 Testing Form Filling Fix")
        print("=" * 40)
        
        # Test with a page that has a form
        test_url = "https://job-boards.greenhouse.io/ctccampusboard/jobs/4577583005?utm_source=Trackr&utm_medium=tracker&utm_campaign=UK_Finance_2026&gh_src=Trackr"
        
        try:
            self.driver.get(test_url)
            time.sleep(3)
            
            # Handle cookie consent
            self._handle_cookie_consent()
            
            # Handle apply button
            self._handle_apply_button()
            
            # Wait for form to load
            time.sleep(5)
            
            # Try to fill the form
            success = self._fill_form()
            
            if success:
                print("✅ Form filling successful")
                return True
            else:
                print("❌ Form filling failed")
                return False
                
        except Exception as e:
            print(f"❌ Error testing form filling: {e}")
            return False
    
    def _handle_cookie_consent(self):
        """Handle cookie consent banners"""
        try:
            cookie_texts = ['accept', 'agree', 'continue', 'ok', 'got it', 'i understand']
            
            for text in cookie_texts:
                try:
                    buttons = self.driver.find_elements(By.XPATH, f"//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text}')]")
                    
                    for button in buttons:
                        if button.is_displayed() and button.is_enabled():
                            print(f"   Clicking cookie button: {button.text}")
                            button.click()
                            time.sleep(2)
                            return True
                            
                except Exception as e:
                    continue
            
            return False
            
        except Exception as e:
            return False
    
    def _handle_apply_button(self):
        """Handle apply button if form is not immediately visible"""
        try:
            # Check if form is already visible
            forms = self.driver.find_elements(By.TAG_NAME, "form")
            if forms:
                print("   Form already visible, no apply button needed")
                return True
            
            # Try to find apply button
            apply_texts = ['apply', 'application', 'submit application', 'start application']
            
            for text in apply_texts:
                try:
                    buttons = self.driver.find_elements(By.XPATH, f"//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text}')]")
                    
                    for button in buttons:
                        if button.is_displayed() and button.is_enabled():
                            print(f"   Clicking apply button: {button.text}")
                            button.click()
                            time.sleep(3)
                            return True
                            
                except Exception as e:
                    continue
            
            return False
            
        except Exception as e:
            return False
    
    def _fill_form(self):
        """Fill the form with enhanced field mapping"""
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
        """Fill a single input field"""
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
        
        # Enhanced field mappings
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
    
    def run_all_tests(self):
        """Run all tests"""
        print("🧪 Running Enhanced Fixes Tests")
        print("=" * 50)
        
        results = {
            'cookie_consent': self.test_cookie_consent_fix(),
            'apply_button': self.test_apply_button_fix(),
            'form_filling': self.test_form_filling_fix()
        }
        
        print(f"\n📊 Test Results:")
        print(f"   Cookie Consent: {'✅ PASS' if results['cookie_consent'] else '❌ FAIL'}")
        print(f"   Apply Button: {'✅ PASS' if results['apply_button'] else '❌ FAIL'}")
        print(f"   Form Filling: {'✅ PASS' if results['form_filling'] else '❌ FAIL'}")
        
        passed = sum(results.values())
        total = len(results)
        
        print(f"\n🎯 Overall: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All tests passed! Enhanced fixes are working.")
        else:
            print("⚠️ Some tests failed. Further investigation needed.")
        
        return results
    
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()

def main():
    """Main function"""
    tester = TestEnhancedFixes(headless=False)
    
    try:
        results = tester.run_all_tests()
    finally:
        tester.cleanup()
    
    return results

if __name__ == "__main__":
    main()

