#!/usr/bin/env python3
"""
Fix Website-Specific Issues
Analyze and fix issues for specific websites that were causing problems.
"""

import json
import requests
from bs4 import BeautifulSoup
import time

def analyze_website_issues():
    """Analyze specific websites that had issues"""
    print("🔍 Analyzing Website-Specific Issues")
    print("=" * 50)
    
    # Websites that had issues
    problem_sites = [
        {
            "name": "D.E. Shaw",
            "url": "https://www.deshaw.com/careers/trader-analyst-intern-london-summer-2026-5465",
            "issue": "No form fields found - likely requires Apply button click"
        },
        {
            "name": "Evercore (SmartRecruiters)",
            "url": "https://jobs.smartrecruiters.com/Wiser/744000076772605-advisory-summer-internship-2026-evercore",
            "issue": "SmartRecruiters portal - needs specific handling"
        },
        {
            "name": "Blackstone (Workday)",
            "url": "https://blackstone.wd1.myworkdayjobs.com/en-US/Blackstone_Campus_Careers/jobs",
            "issue": "Workday portal - needs specific handling"
        },
        {
            "name": "Citadel",
            "url": "https://www.citadel.com/careers/details/international-equities-associate-intern-europe/",
            "issue": "Career site - needs Apply button handling"
        }
    ]
    
    enhanced_configs = {}
    
    for site in problem_sites:
        print(f"\n🔍 Analyzing: {site['name']}")
        print(f"🔗 URL: {site['url']}")
        print(f"⚠️ Issue: {site['issue']}")
        
        # Analyze the site and create enhanced config
        config = analyze_site_structure(site)
        enhanced_configs[site['name']] = config
        
        time.sleep(1)  # Be respectful
    
    # Save enhanced configurations
    with open("enhanced_website_configs.json", "w") as f:
        json.dump(enhanced_configs, f, indent=2)
    
    print(f"\n✅ Enhanced configurations saved to: enhanced_website_configs.json")
    return enhanced_configs

def analyze_site_structure(site):
    """Analyze a specific site's structure"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(site['url'], headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        config = {
            "type": "unknown",
            "requires_account": False,
            "apply_button_required": True,  # Most career sites need this
            "has_cookies": True,
            "cookie_button_text": "Accept All",
            "extract_job_info_early": True,
            "specific_selectors": {},
            "portal_handling": {}
        }
        
        # Analyze based on domain
        if "deshaw.com" in site['url']:
            config.update({
                "type": "career_site",
                "apply_button_selector": "a[href*='apply'], button:contains('Apply'), .apply-button",
                "form_wait_time": 5,
                "specific_selectors": {
                    "apply_button": "a[href*='apply'], button:contains('Apply')",
                    "cookie_button": "button:contains('Accept')"
                }
            })
        
        elif "smartrecruiters.com" in site['url']:
            config.update({
                "type": "smartrecruiters",
                "portal_handling": {
                    "iframe_detection": True,
                    "apply_button_selector": "button[data-qa='apply-button'], a[href*='apply']",
                    "form_selector": "form[data-qa='application-form']"
                },
                "specific_selectors": {
                    "apply_button": "button[data-qa='apply-button']",
                    "cookie_button": "button:contains('Accept')"
                }
            })
        
        elif "workdayjobs.com" in site['url']:
            config.update({
                "type": "workday",
                "portal_handling": {
                    "iframe_detection": True,
                    "apply_button_selector": "button[data-automation-id='apply-button']",
                    "form_selector": "form[data-automation-id='application-form']"
                },
                "specific_selectors": {
                    "apply_button": "button[data-automation-id='apply-button']",
                    "cookie_button": "button:contains('Accept')"
                }
            })
        
        elif "citadel.com" in site['url']:
            config.update({
                "type": "career_site",
                "apply_button_selector": "a[href*='apply'], button:contains('Apply'), .apply-button",
                "specific_selectors": {
                    "apply_button": "a[href*='apply'], button:contains('Apply')",
                    "cookie_button": "button:contains('Accept All Cookies')"
                }
            })
        
        print(f"   ✅ Configuration created for {site['name']}")
        return config
        
    except Exception as e:
        print(f"   ❌ Error analyzing {site['name']}: {e}")
        return {
            "type": "unknown",
            "apply_button_required": True,
            "has_cookies": True
        }

def create_enhanced_application_filler():
    """Create enhanced ApplicationFiller with website-specific fixes"""
    print("\n🔧 Creating Enhanced ApplicationFiller...")
    
    enhanced_code = '''
class EnhancedApplicationFiller(ApplicationFiller):
    """Enhanced ApplicationFiller with website-specific fixes"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.load_enhanced_configs()
    
    def load_enhanced_configs(self):
        """Load enhanced website configurations"""
        try:
            with open("enhanced_website_configs.json", "r") as f:
                self.enhanced_configs = json.load(f)
        except:
            self.enhanced_configs = {}
    
    def get_enhanced_config(self, url):
        """Get enhanced configuration for a specific URL"""
        for site_name, config in self.enhanced_configs.items():
            if site_name.lower() in url.lower():
                return config
        return None
    
    def handle_apply_button_enhanced(self):
        """Enhanced apply button handling with site-specific logic"""
        try:
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            if not self.driver:
                return True
            
            # Get enhanced config
            enhanced_config = self.get_enhanced_config(self.driver.current_url)
            if not enhanced_config:
                return self.handle_apply_button()  # Use original method
            
            print(f"🎯 Using enhanced apply button handling for {enhanced_config.get('type', 'unknown')}")
            
            # Wait for page to load
            time.sleep(3)
            
            # Try site-specific selectors
            apply_selectors = enhanced_config.get("specific_selectors", {}).get("apply_button", [])
            if isinstance(apply_selectors, str):
                apply_selectors = [apply_selectors]
            
            # Add generic selectors
            apply_selectors.extend([
                "a[href*='apply']",
                "button:contains('Apply')",
                ".apply-button",
                "#apply-button",
                "[data-qa*='apply']"
            ])
            
            apply_button = None
            for selector in apply_selectors:
                try:
                    if ":contains" in selector:
                        # Use XPath for text-based selectors
                        xpath_selector = f"//*[contains(text(), 'Apply') and (self::button or self::a)]"
                        apply_button = self.driver.find_element(By.XPATH, xpath_selector)
                    else:
                        apply_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if apply_button and apply_button.is_displayed() and apply_button.is_enabled():
                        break
                except:
                    continue
            
            if apply_button:
                print("🎯 Found apply button - clicking...")
                if not self.headless:
                    self.driver.execute_script("arguments[0].style.border='3px solid blue'", apply_button)
                    time.sleep(1)
                
                apply_button.click()
                print("✅ Apply button clicked")
                time.sleep(5)  # Wait longer for form to load
                return True
            else:
                print("⚠️ Apply button not found - continuing anyway")
                return True
                
        except Exception as e:
            print(f"⚠️ Error in enhanced apply button handling: {e}")
            return True
    
    def handle_portal_specific_logic(self):
        """Handle portal-specific logic (SmartRecruiters, Workday, etc.)"""
        try:
            enhanced_config = self.get_enhanced_config(self.driver.current_url)
            if not enhanced_config:
                return True
            
            portal_handling = enhanced_config.get("portal_handling", {})
            
            # Handle iframes
            if portal_handling.get("iframe_detection"):
                print("🖼️ Checking for iframes...")
                iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                for iframe in iframes:
                    try:
                        self.driver.switch_to.frame(iframe)
                        # Look for apply button in iframe
                        apply_button = self.driver.find_element(By.CSS_SELECTOR, portal_handling.get("apply_button_selector", "button:contains('Apply')"))
                        if apply_button:
                            apply_button.click()
                            print("✅ Found and clicked apply button in iframe")
                            time.sleep(3)
                        self.driver.switch_to.default_content()
                    except:
                        self.driver.switch_to.default_content()
                        continue
            
            return True
            
        except Exception as e:
            print(f"⚠️ Error in portal-specific handling: {e}")
            return True
    
    def submit_enhanced(self, multi_url_mode=False):
        """Enhanced submit method with portal-specific handling"""
        try:
            # First, initialize driver if needed
            if not self.driver:
                if not self.initialize_driver():
                    return self.link
            
            if not self.driver:
                print("❌ Failed to initialize driver")
                return self.link
            
            print(f"🌐 Navigating to: {self.link}")
            self.driver.get(self.link)
            time.sleep(3)
            
            # Step 1: Handle cookie consent banners FIRST
            self.handle_cookies()
            
            # Step 2: Handle portal-specific logic
            self.handle_portal_specific_logic()
            
            # Step 3: Handle Apply button with enhanced logic
            self.handle_apply_button_enhanced()
            
            # Step 4: Handle cookies again in case Apply button led to new page
            self.handle_cookies()
            
            # Step 5: Fill the form
            if self.fill_form():
                # After filling, attempt to detect and refill any missing/invalid fields
                try:
                    print("🔁 Running post-fill validation and refill pass...")
                    self.report_and_refill_missing_fields()
                    time.sleep(0.6)
                    # Second quick pass
                    self.report_and_refill_missing_fields()
                except Exception as e:
                    print(f"⚠️ Post-fill refill pass encountered an error: {e}")
                
                # Find and click submit button
                from selenium.webdriver.common.by import By
                
                if not self.driver:
                    print("❌ Driver not initialized")
                    if multi_url_mode:
                        return self.link
                    else:
                        self.keep_browser_open("Driver not initialized", multi_url_mode)
                        return self.link
                
                print("🔍 Looking for submit button...")
                
                # Store original URL to compare later
                original_url = self.driver.current_url
                
                # Try different submit button selectors
                submit_selectors = [
                    "button[type='submit']",
                    "input[type='submit']",
                    "button:contains('Submit')",
                    "button:contains('Apply')",
                    "[data-testid*='submit']",
                    ".submit-button",
                    "#submit",
                    "input[value*='Submit']",
                    "input[value*='Apply']"
                ]
                
                submit_button = None
                for selector in submit_selectors:
                    try:
                        submit_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if submit_button.is_displayed() and submit_button.is_enabled():
                            break
                    except:
                        continue
                
                if submit_button and submit_button.is_displayed() and submit_button.is_enabled():
                    if not self.headless and self.driver:
                        # Highlight submit button
                        self.driver.execute_script("arguments[0].style.border='3px solid blue'", submit_button)
                        print("🎯 Found submit button - clicking in 3 seconds...")
                        time.sleep(3)
                    
                    # Try multiple methods to click the submit button
                    click_success = False
                    methods_tried = []
                    
                    # Method 1: Regular click
                    try:
                        submit_button.click()
                        print("✅ Submit button clicked successfully")
                        click_success = True
                    except Exception as e1:
                        methods_tried.append(f"regular_click: {str(e1)[:50]}")
                        
                        # Method 2: JavaScript click
                        try:
                            if self.driver:
                                self.driver.execute_script("arguments[0].click();", submit_button)
                                print("✅ Form submitted successfully with JavaScript click")
                                click_success = True
                        except Exception as e2:
                            methods_tried.append(f"js_click: {str(e2)[:50]}")
                            
                            # Method 3: Scroll into view and click
                            try:
                                if self.driver:
                                    self.driver.execute_script("arguments[0].scrollIntoView(true);", submit_button)
                                    time.sleep(1)
                                    submit_button.click()
                                    print("✅ Form submitted successfully after scrolling")
                                    click_success = True
                            except Exception as e3:
                                methods_tried.append(f"scroll_click: {str(e3)[:50]}")
                                
                                # Method 4: Move to element and click
                                try:
                                    from selenium.webdriver.common.action_chains import ActionChains
                                    actions = ActionChains(self.driver)
                                    actions.move_to_element(submit_button).click().perform()
                                    print("✅ Form submitted successfully with ActionChains")
                                    click_success = True
                                except Exception as e4:
                                    methods_tried.append(f"action_click: {str(e4)[:50]}")
                    
                    if click_success:
                        # Wait and check if submission was actually successful
                        print("⏳ Waiting to verify submission...")
                        time.sleep(3)
                        
                        # Check for submission success indicators
                        submission_success = self.check_submission_success(original_url)
                        
                        if submission_success:
                            print("🎉 Application submitted successfully!")
                            if not self.headless:
                                time.sleep(5)  # Show success for a bit
                            return True
                        else:
                            print("⚠️ Submission may have failed - keeping browser open for manual completion")
                            self.keep_browser_open("Submission verification failed", multi_url_mode)
                            return self.link
                    else:
                        print(f"❌ All submit methods failed: {', '.join(methods_tried)}")
                        self.keep_browser_open(f"Submit failed: {', '.join(methods_tried)}", multi_url_mode)
                        return self.link
                      
                else:
                    print("⚠️ Submit button not found or not clickable")
                    self.keep_browser_open("Submit button not found", multi_url_mode)
                    return self.link
            else:
                print("❌ Form filling failed")
                self.keep_browser_open("Form filling failed", multi_url_mode)
                return self.link
            
        except Exception as e:
            print(f"❌ Error during enhanced submission: {e}")
            self.keep_browser_open(f"Enhanced submission error: {e}", multi_url_mode)
            return self.link
'''
    
    # Save the enhanced code
    with open("enhanced_application_filler.py", "w") as f:
        f.write(enhanced_code)
    
    print("✅ Enhanced ApplicationFiller code saved to: enhanced_application_filler.py")

def main():
    """Main function"""
    print("🔧 Fixing Website-Specific Issues")
    print("=" * 50)
    
    # Analyze website issues
    enhanced_configs = analyze_website_issues()
    
    # Create enhanced ApplicationFiller
    create_enhanced_application_filler()
    
    print("\n✅ All website-specific fixes completed!")
    print("🚀 Ready to use enhanced ApplicationFiller")

if __name__ == "__main__":
    main()

