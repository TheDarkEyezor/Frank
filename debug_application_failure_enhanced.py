#!/usr/bin/env python3
"""
Enhanced Application Failure Debugger
Investigates why applications are failing, including iframe content and complex forms.
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

class EnhancedApplicationDebugger:
    def __init__(self, headless=False):
        self.headless = headless
        self.driver = None
        
    def setup_driver(self):
        """Setup Chrome driver with debugging options"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument("--headless")
        
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Add debugging options
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        return self.driver
    
    def debug_application(self, url, company_name):
        """Debug a specific application to identify failure causes"""
        print(f"🔍 Debugging application: {company_name}")
        print(f"🔗 URL: {url}")
        print("=" * 80)
        
        try:
            if not self.driver:
                self.setup_driver()
            
            # Navigate to the application page
            print("🌐 Navigating to application page...")
            self.driver.get(url)
            
            # Wait for page to load
            time.sleep(5)
            
            # Handle cookies
            self._handle_cookies()
            
            # Analyze the page structure
            self._analyze_page_structure(url)
            
            # Look for form elements
            self._analyze_form_elements()
            
            # Look for application barriers
            self._identify_barriers()
            
            # Try to find the application form
            self._find_application_form()
            
            # Check for iframe content
            self._analyze_iframes()
            
            # Check for common issues
            self._check_common_issues()
            
            # Try to find application button/link
            self._find_application_action()
            
            print("\n✅ Debug analysis completed!")
            
        except Exception as e:
            print(f"❌ Error during debugging: {e}")
        finally:
            if self.driver:
                self.driver.quit()
    
    def _handle_cookies(self):
        """Handle cookie consent banners"""
        print("\n🍪 Checking for cookie consent...")
        
        try:
            cookie_texts = ['accept', 'accept all', 'continue', 'ok', 'got it', 'i agree']
            
            for text in cookie_texts:
                try:
                    buttons = self.driver.find_elements(By.XPATH, f"//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text}')]")
                    
                    for button in buttons:
                        if button.is_displayed():
                            print(f"   Clicking cookie button: {button.text}")
                            button.click()
                            time.sleep(2)
                            break
                except:
                    continue
            
            print("   Cookie handling completed")
            
        except Exception as e:
            print(f"   Error handling cookies: {e}")
    
    def _analyze_page_structure(self, original_url):
        """Analyze the overall page structure"""
        print("\n📄 Analyzing page structure...")
        
        try:
            # Get page title
            title = self.driver.title
            print(f"   Page title: {title}")
            
            # Get current URL
            current_url = self.driver.current_url
            print(f"   Current URL: {current_url}")
            
            # Check if redirected
            if current_url != original_url:
                print(f"   ⚠️ Page redirected from original URL")
            
            # Count different element types
            links = self.driver.find_elements(By.TAG_NAME, "a")
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            forms = self.driver.find_elements(By.TAG_NAME, "form")
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            selects = self.driver.find_elements(By.TAG_NAME, "select")
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            
            print(f"   Links: {len(links)}")
            print(f"   Buttons: {len(buttons)}")
            print(f"   Forms: {len(forms)}")
            print(f"   Input fields: {len(inputs)}")
            print(f"   Select dropdowns: {len(selects)}")
            print(f"   Iframes: {len(iframes)}")
            
        except Exception as e:
            print(f"   Error analyzing page structure: {e}")
    
    def _analyze_form_elements(self):
        """Analyze form elements in detail"""
        print("\n📝 Analyzing form elements...")
        
        try:
            # Look for forms
            forms = self.driver.find_elements(By.TAG_NAME, "form")
            print(f"   Found {len(forms)} forms")
            
            for i, form in enumerate(forms, 1):
                print(f"   Form {i}:")
                print(f"     Action: {form.get_attribute('action')}")
                print(f"     Method: {form.get_attribute('method')}")
                print(f"     ID: {form.get_attribute('id')}")
                print(f"     Class: {form.get_attribute('class')}")
                
                # Look for form fields
                inputs = form.find_elements(By.TAG_NAME, "input")
                selects = form.find_elements(By.TAG_NAME, "select")
                textareas = form.find_elements(By.TAG_NAME, "textarea")
                
                print(f"     Input fields: {len(inputs)}")
                print(f"     Select dropdowns: {len(selects)}")
                print(f"     Textareas: {len(textareas)}")
                
                # Show input field details
                for j, input_field in enumerate(inputs[:5], 1):  # Show first 5
                    input_type = input_field.get_attribute('type')
                    input_name = input_field.get_attribute('name')
                    input_id = input_field.get_attribute('id')
                    input_placeholder = input_field.get_attribute('placeholder')
                    
                    print(f"       Input {j}: type={input_type}, name={input_name}, id={input_id}, placeholder={input_placeholder}")
                
                if len(inputs) > 5:
                    print(f"       ... and {len(inputs) - 5} more input fields")
            
            # Look for standalone input fields (not in forms)
            all_inputs = self.driver.find_elements(By.TAG_NAME, "input")
            form_inputs = []
            for form in forms:
                form_inputs.extend(form.find_elements(By.TAG_NAME, "input"))
            
            standalone_inputs = [inp for inp in all_inputs if inp not in form_inputs]
            if standalone_inputs:
                print(f"   Found {len(standalone_inputs)} standalone input fields")
                
        except Exception as e:
            print(f"   Error analyzing form elements: {e}")
    
    def _analyze_iframes(self):
        """Analyze iframe content"""
        print("\n🖼️ Analyzing iframe content...")
        
        try:
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            print(f"   Found {len(iframes)} iframes")
            
            for i, iframe in enumerate(iframes, 1):
                print(f"   Iframe {i}:")
                print(f"     Src: {iframe.get_attribute('src')}")
                print(f"     ID: {iframe.get_attribute('id')}")
                print(f"     Name: {iframe.get_attribute('name')}")
                print(f"     Class: {iframe.get_attribute('class')}")
                
                # Try to switch to iframe and analyze content
                try:
                    self.driver.switch_to.frame(iframe)
                    
                    # Count elements in iframe
                    iframe_links = self.driver.find_elements(By.TAG_NAME, "a")
                    iframe_buttons = self.driver.find_elements(By.TAG_NAME, "button")
                    iframe_forms = self.driver.find_elements(By.TAG_NAME, "form")
                    iframe_inputs = self.driver.find_elements(By.TAG_NAME, "input")
                    
                    print(f"     Iframe content:")
                    print(f"       Links: {len(iframe_links)}")
                    print(f"       Buttons: {len(iframe_buttons)}")
                    print(f"       Forms: {len(iframe_forms)}")
                    print(f"       Input fields: {len(iframe_inputs)}")
                    
                    # Look for application-related content in iframe
                    application_keywords = ['apply', 'application', 'submit', 'careers', 'jobs']
                    
                    for button in iframe_buttons:
                        button_text = button.text.lower()
                        if any(keyword in button_text for keyword in application_keywords):
                            print(f"       ✅ Found application button: {button.text}")
                    
                    for link in iframe_links:
                        link_text = link.text.lower()
                        if any(keyword in link_text for keyword in application_keywords):
                            print(f"       ✅ Found application link: {link.text}")
                    
                    # Switch back to main content
                    self.driver.switch_to.default_content()
                    
                except Exception as e:
                    print(f"     Error analyzing iframe content: {e}")
                    # Switch back to main content
                    self.driver.switch_to.default_content()
                
        except Exception as e:
            print(f"   Error analyzing iframes: {e}")
    
    def _identify_barriers(self):
        """Identify potential barriers to application"""
        print("\n🚧 Identifying application barriers...")
        
        try:
            page_source = self.driver.page_source.lower()
            current_url = self.driver.current_url.lower()
            
            barriers = []
            
            # Check for login/account requirements
            if any(keyword in current_url or keyword in page_source for keyword in ['login', 'signin', 'register', 'account']):
                barriers.append("Account creation/login required")
            
            # Check for external portals
            if any(keyword in current_url for keyword in ['workday', 'greenhouse', 'lever', 'bamboohr', 'smartrecruiters']):
                barriers.append("External application portal")
            
            # Check for test requirements
            if any(keyword in current_url or keyword in page_source for keyword in ['test', 'assessment', 'hirevue', 'pymetrics']):
                barriers.append("Test/assessment required")
            
            # Check for email applications
            if any(keyword in current_url or keyword in page_source for keyword in ['email', 'contact', 'apply@']):
                barriers.append("Email application required")
            
            # Check for complex forms
            if len(current_url) > 200 or current_url.count('&') > 5:
                barriers.append("Complex multi-step form")
            
            # Check for iframe content
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            if iframes:
                barriers.append(f"Content in {len(iframes)} iframes")
            
            if barriers:
                print("   Identified barriers:")
                for barrier in barriers:
                    print(f"     • {barrier}")
            else:
                print("   No obvious barriers identified")
                
        except Exception as e:
            print(f"   Error identifying barriers: {e}")
    
    def _find_application_form(self):
        """Try to find the actual application form"""
        print("\n🎯 Looking for application form...")
        
        try:
            # Look for common application form indicators
            application_keywords = ['apply', 'application', 'submit', 'careers', 'jobs']
            
            # Check page title
            title = self.driver.title.lower()
            if any(keyword in title for keyword in application_keywords):
                print(f"   ✅ Application keywords found in title: {self.driver.title}")
            
            # Look for buttons with application text
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            application_buttons = []
            
            for button in buttons:
                button_text = button.text.lower()
                if any(keyword in button_text for keyword in application_keywords):
                    application_buttons.append(button)
            
            if application_buttons:
                print(f"   ✅ Found {len(application_buttons)} application-related buttons:")
                for button in application_buttons:
                    print(f"     • {button.text}")
            else:
                print("   ❌ No application buttons found")
            
            # Look for links with application text
            links = self.driver.find_elements(By.TAG_NAME, "a")
            application_links = []
            
            for link in links:
                link_text = link.text.lower()
                if any(keyword in link_text for keyword in application_keywords):
                    application_links.append(link)
            
            if application_links:
                print(f"   ✅ Found {len(application_links)} application-related links:")
                for link in application_links[:5]:  # Show first 5
                    print(f"     • {link.text} -> {link.get_attribute('href')}")
                if len(application_links) > 5:
                    print(f"     ... and {len(application_links) - 5} more")
            else:
                print("   ❌ No application links found")
                
        except Exception as e:
            print(f"   Error finding application form: {e}")
    
    def _find_application_action(self):
        """Try to find the actual application action (button/link to click)"""
        print("\n🎯 Looking for application action...")
        
        try:
            # Look for any clickable elements that might start the application
            all_clickable = []
            
            # Buttons
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                if button.is_displayed() and button.is_enabled():
                    all_clickable.append({
                        'element': button,
                        'text': button.text,
                        'type': 'button',
                        'tag': 'button'
                    })
            
            # Links
            links = self.driver.find_elements(By.TAG_NAME, "a")
            for link in links:
                if link.is_displayed() and link.is_enabled():
                    all_clickable.append({
                        'element': link,
                        'text': link.text,
                        'type': 'link',
                        'tag': 'a',
                        'href': link.get_attribute('href')
                    })
            
            # Divs that might be clickable
            clickable_divs = self.driver.find_elements(By.XPATH, "//div[@onclick or @role='button' or contains(@class, 'button') or contains(@class, 'clickable')]")
            for div in clickable_divs:
                if div.is_displayed():
                    all_clickable.append({
                        'element': div,
                        'text': div.text,
                        'type': 'div',
                        'tag': 'div'
                    })
            
            # Filter for application-related actions
            application_keywords = ['apply', 'application', 'submit', 'start', 'begin', 'continue', 'next']
            application_actions = []
            
            for item in all_clickable:
                text_lower = item['text'].lower()
                if any(keyword in text_lower for keyword in application_keywords):
                    application_actions.append(item)
            
            if application_actions:
                print(f"   ✅ Found {len(application_actions)} potential application actions:")
                for action in application_actions:
                    print(f"     • {action['text']} ({action['type']})")
                    if 'href' in action:
                        print(f"       URL: {action['href']}")
            else:
                print("   ❌ No application actions found")
                
                # Show all clickable elements for debugging
                print("   📋 All clickable elements:")
                for item in all_clickable[:10]:  # Show first 10
                    print(f"     • {item['text']} ({item['type']})")
                if len(all_clickable) > 10:
                    print(f"     ... and {len(all_clickable) - 10} more")
                
        except Exception as e:
            print(f"   Error finding application action: {e}")
    
    def _check_common_issues(self):
        """Check for common issues that cause failures"""
        print("\n🔍 Checking for common issues...")
        
        try:
            issues = []
            
            # Check for JavaScript errors
            try:
                logs = self.driver.get_log('browser')
                if logs:
                    js_errors = [log for log in logs if log['level'] == 'SEVERE']
                    if js_errors:
                        issues.append(f"JavaScript errors: {len(js_errors)}")
            except:
                pass
            
            # Check for loading issues
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except TimeoutException:
                issues.append("Page loading timeout")
            
            # Check for iframe content
            iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
            if iframes:
                issues.append(f"Content in {len(iframes)} iframes (may need to switch context)")
            
            # Check for dynamic content
            try:
                # Wait a bit for dynamic content
                time.sleep(3)
                initial_elements = len(self.driver.find_elements(By.TAG_NAME, "input"))
                time.sleep(2)
                final_elements = len(self.driver.find_elements(By.TAG_NAME, "input"))
                
                if final_elements > initial_elements:
                    issues.append("Dynamic content loading detected")
            except:
                pass
            
            # Check for CAPTCHA
            captcha_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'captcha') or contains(@class, 'captcha') or contains(@id, 'captcha')]")
            if captcha_elements:
                issues.append("CAPTCHA detected")
            
            if issues:
                print("   Found issues:")
                for issue in issues:
                    print(f"     • {issue}")
            else:
                print("   No common issues detected")
                
        except Exception as e:
            print(f"   Error checking common issues: {e}")

def main():
    """Main function to debug a specific application"""
    print("🔍 Enhanced Application Failure Debugger")
    print("=" * 50)
    
    # Test cases - applications that failed in previous tests
    test_cases = [
        {
            "url": "https://www.deshaw.com/careers/trader-analyst-intern-london-summer-2026-5465?utm_source=Trackr&utm_medium=tracker&utm_campaign=UK_Finance_2026",
            "company": "D.E. Shaw"
        },
        {
            "url": "https://jobs.smartrecruiters.com/Wiser/744000076772605-advisory-summer-internship-2026-evercore?utm_source=Trackr&utm_medium=tracker&utm_campaign=UK_Finance_2026&trid=Trackr&dcr_ci=Trackr",
            "company": "Evercore"
        }
    ]
    
    print("Available test cases:")
    for i, case in enumerate(test_cases, 1):
        print(f"{i}. {case['company']}")
    
    choice = input("\nSelect a test case (1-2): ").strip()
    
    try:
        choice_idx = int(choice) - 1
        if 0 <= choice_idx < len(test_cases):
            test_case = test_cases[choice_idx]
            
            debugger = EnhancedApplicationDebugger(headless=False)
            debugger.debug_application(test_case['url'], test_case['company'])
        else:
            print("Invalid choice")
    except ValueError:
        print("Invalid input")

if __name__ == "__main__":
    main()

