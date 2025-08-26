#!/usr/bin/env python3
"""
Enhanced Trackr Website Scraper
Uses Selenium to handle dynamic content and better extract application links.
"""

import json
import time
from urllib.parse import urljoin, urlparse
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class EnhancedTrackrScraper:
    def __init__(self, headless=False):
        self.base_url = "https://app.the-trackr.com"
        self.headless = headless
        self.driver = None
        
    def setup_driver(self):
        """Setup Chrome driver with appropriate options"""
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
    
    def get_internship_links(self, url="https://app.the-trackr.com/uk-finance/summer-internships"):
        """Extract all internship application links from Trackr using Selenium"""
        print(f"🔍 Scraping Trackr website: {url}")
        
        try:
            if not self.driver:
                self.setup_driver()
            
            # Navigate to the page
            self.driver.get(url)
            print("📄 Page loaded, waiting for content...")
            
            # Wait for page to load
            time.sleep(5)
            
            # Try to find and click any "Accept" or "Continue" buttons
            self._handle_cookies_and_popups()
            
            # Wait for content to load
            time.sleep(3)
            
            # Get page source after JavaScript execution
            page_source = self.driver.page_source
            print(f"📄 Page source length: {len(page_source)} characters")
            
            # Look for various patterns in the page
            links = []
            
            # Method 1: Look for all links on the page
            all_links = self.driver.find_elements(By.TAG_NAME, "a")
            print(f"🔗 Found {len(all_links)} total links on page")
            
            for link in all_links:
                try:
                    href = link.get_attribute('href')
                    text = link.text.strip()
                    
                    if href and text:
                        # Check if it's an external application link
                        if self._is_external_application_link(href):
                            links.append({
                                'url': href,
                                'text': text,
                                'company': self._extract_company_name(text),
                                'source': 'direct_link'
                            })
                except Exception as e:
                    continue
            
            # Method 2: Look for buttons that might be application links
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            print(f"🔘 Found {len(buttons)} buttons on page")
            
            for button in buttons:
                try:
                    text = button.text.strip()
                    if text and any(keyword in text.lower() for keyword in ['apply', 'application', 'careers']):
                        # Look for parent link or onclick handler
                        parent = button.find_element(By.XPATH, "./..")
                        parent_links = parent.find_elements(By.TAG_NAME, "a")
                        
                        for parent_link in parent_links:
                            href = parent_link.get_attribute('href')
                            if href and self._is_external_application_link(href):
                                links.append({
                                    'url': href,
                                    'text': text,
                                    'company': self._extract_company_name(text),
                                    'source': 'button_parent'
                                })
                except Exception as e:
                    continue
            
            # Method 3: Look for specific patterns in the page source
            # This is a fallback method
            source_links = self._extract_links_from_source(page_source)
            links.extend(source_links)
            
            # Remove duplicates
            unique_links = []
            seen_urls = set()
            for link in links:
                if link['url'] not in seen_urls:
                    unique_links.append(link)
                    seen_urls.add(link['url'])
            
            print(f"📊 Found {len(unique_links)} unique application links")
            
            # Debug: Print some page info
            print(f"📄 Page title: {self.driver.title}")
            print(f"🔗 Current URL: {self.driver.current_url}")
            
            return unique_links
            
        except Exception as e:
            print(f"❌ Error scraping Trackr: {e}")
            return []
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None
    
    def _handle_cookies_and_popups(self):
        """Handle cookie consent and popup dialogs"""
        try:
            # Common cookie button texts
            cookie_texts = ['accept', 'accept all', 'continue', 'ok', 'got it', 'i agree']
            
            for text in cookie_texts:
                try:
                    # Look for buttons with cookie-related text
                    buttons = self.driver.find_elements(By.XPATH, f"//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text}')]")
                    
                    for button in buttons:
                        if button.is_displayed():
                            print(f"🍪 Clicking cookie button: {button.text}")
                            button.click()
                            time.sleep(1)
                            break
                except:
                    continue
                    
        except Exception as e:
            print(f"⚠️ Error handling cookies: {e}")
    
    def _extract_links_from_source(self, page_source):
        """Extract links from page source using regex patterns"""
        links = []
        
        # Look for href patterns
        href_pattern = r'href=["\']([^"\']+)["\']'
        href_matches = re.findall(href_pattern, page_source)
        
        for href in href_matches:
            if self._is_external_application_link(href):
                # Try to find associated text
                text = self._extract_text_near_href(page_source, href)
                links.append({
                    'url': href,
                    'text': text,
                    'company': self._extract_company_name(text),
                    'source': 'source_regex'
                })
        
        return links
    
    def _extract_text_near_href(self, source, href):
        """Extract text near an href attribute"""
        try:
            # Look for text within the same element
            pattern = rf'<[^>]*href=["\']{re.escape(href)}["\'][^>]*>([^<]+)</a>'
            match = re.search(pattern, source)
            if match:
                return match.group(1).strip()
        except:
            pass
        
        return "Application Link"
    
    def _is_external_application_link(self, url):
        """Check if URL looks like an external application link"""
        if not url:
            return False
            
        # Skip internal Trackr links
        if 'the-trackr.com' in url:
            return False
            
        # Skip common non-application domains
        skip_domains = ['google.com', 'facebook.com', 'twitter.com', 'linkedin.com', 'youtube.com', 'instagram.com']
        domain = urlparse(url).netloc.lower()
        if any(skip_domain in domain for skip_domain in skip_domains):
            return False
            
        # Look for application-related patterns
        application_patterns = [
            'apply', 'application', 'careers', 'jobs', 'internship', 'position',
            'workday', 'greenhouse', 'lever', 'bamboohr', 'smartrecruiters',
            'icims', 'taleo', 'successfactors', 'brassring', 'hirevue'
        ]
        
        url_lower = url.lower()
        return any(pattern in url_lower for pattern in application_patterns)
    
    def _extract_company_name(self, text):
        """Extract company name from link text"""
        if not text:
            return "Unknown Company"
        
        # Clean up the text
        text = text.strip()
        
        # Simple heuristic - take first few words
        words = text.split()
        if len(words) <= 3:
            return text
        else:
            return ' '.join(words[:3])
    
    def save_links(self, links, filename="trackr_links_enhanced.json"):
        """Save extracted links to JSON file"""
        with open(filename, 'w') as f:
            json.dump(links, f, indent=2)
        print(f"💾 Saved {len(links)} links to {filename}")
    
    def load_links(self, filename="trackr_links_enhanced.json"):
        """Load links from JSON file"""
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"📁 No saved links found in {filename}")
            return []

def main():
    scraper = EnhancedTrackrScraper(headless=False)  # Use visible browser for debugging
    
    # Try to load existing links first
    existing_links = scraper.load_links()
    if existing_links:
        print(f"📋 Found {len(existing_links)} existing links")
        use_existing = input("Use existing links? (y/n): ").lower().strip()
        if use_existing == 'y':
            return existing_links
    
    # Scrape new links
    links = scraper.get_internship_links()
    
    if links:
        scraper.save_links(links)
        
        print(f"\n📋 Extracted Links:")
        for i, link in enumerate(links, 1):
            print(f"{i:2d}. {link['company']} - {link['url']}")
            print(f"    Text: {link['text']}")
            print(f"    Source: {link['source']}")
            print()
        
        return links
    else:
        print("❌ No links found. The website structure might have changed.")
        return []

if __name__ == "__main__":
    main()

