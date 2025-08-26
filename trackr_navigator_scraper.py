#!/usr/bin/env python3
"""
Trackr Navigator Scraper
Navigates through Trackr to find individual tracker pages and extract application links.
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
from datetime import datetime
import os

class TrackrNavigatorScraper:
    def __init__(self, headless=False):
        self.base_url = "https://the-trackr.com"
        self.headless = headless
        self.driver = None
        self.visited_websites_file = "visited_websites.json"
        self.all_links_file = "all_trackr_links.json"
        
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
    
    def discover_tracker_pages(self):
        """Discover all individual tracker pages"""
        print("🔍 Discovering individual tracker pages...")
        
        try:
            if not self.driver:
                self.setup_driver()
            
            # Navigate to main Trackr page
            self.driver.get("https://the-trackr.com/trackers/")
            print("📄 Loading Trackr main page...")
            
            time.sleep(5)
            self._handle_cookies_and_popups()
            time.sleep(3)
            
            # Look for links to individual trackers
            tracker_links = []
            
            # Method 1: Look for links that contain tracker information
            all_links = self.driver.find_elements(By.TAG_NAME, "a")
            
            for link in all_links:
                try:
                    href = link.get_attribute('href')
                    text = link.text.strip()
                    
                    if href and text:
                        # Look for links that might be individual trackers
                        if self._looks_like_tracker_link(href, text):
                            tracker_links.append({
                                'url': href,
                                'title': text,
                                'type': self._categorize_tracker(text, href)
                            })
                except Exception as e:
                    continue
            
            # Method 2: Look for specific patterns in the page
            page_source = self.driver.page_source
            
            # Look for app.the-trackr.com links
            app_links = re.findall(r'https://app\.the-trackr\.com/[^"\']+', page_source)
            for app_link in app_links:
                tracker_links.append({
                    'url': app_link,
                    'title': self._extract_title_from_url(app_link),
                    'type': self._categorize_tracker_from_url(app_link)
                })
            
            # Remove duplicates
            unique_trackers = []
            seen_urls = set()
            for tracker in tracker_links:
                if tracker['url'] not in seen_urls:
                    unique_trackers.append(tracker)
                    seen_urls.add(tracker['url'])
            
            print(f"📊 Found {len(unique_trackers)} unique tracker pages")
            
            # Show discovered trackers
            for i, tracker in enumerate(unique_trackers, 1):
                print(f"{i:2d}. {tracker['title']} ({tracker['type']})")
                print(f"    URL: {tracker['url']}")
            
            return unique_trackers
            
        except Exception as e:
            print(f"❌ Error discovering trackers: {e}")
            return []
    
    def _looks_like_tracker_link(self, href, text):
        """Check if a link looks like it leads to a tracker page"""
        if not href or not text:
            return False
        
        # Look for app.the-trackr.com links
        if 'app.the-trackr.com' in href:
            return True
        
        # Look for tracker-related keywords
        tracker_keywords = ['tracker', 'internship', 'graduate', 'career', 'job']
        if any(keyword in text.lower() for keyword in tracker_keywords):
            return True
        
        # Look for specific patterns
        if '/uk-' in href or '/us-' in href or '/europe-' in href:
            return True
        
        return False
    
    def _extract_title_from_url(self, url):
        """Extract a readable title from a URL"""
        # Remove base URL and clean up
        if 'app.the-trackr.com' in url:
            path = url.split('app.the-trackr.com/')[-1]
            # Convert path to readable title
            title = path.replace('-', ' ').replace('/', ' ').title()
            return title
        return "Unknown Tracker"
    
    def _categorize_tracker_from_url(self, url):
        """Categorize tracker based on URL"""
        url_lower = url.lower()
        
        categories = {
            'finance': ['finance', 'banking', 'investment', 'trading', 'quant', 'hedge'],
            'tech': ['tech', 'software', 'engineering', 'developer', 'programmer'],
            'consulting': ['consulting', 'strategy', 'advisory'],
            'marketing': ['marketing', 'advertising', 'media', 'communication'],
            'general': ['internship', 'graduate', 'career']
        }
        
        for category, keywords in categories.items():
            if any(keyword in url_lower for keyword in keywords):
                return category
        
        return 'general'
    
    def _categorize_tracker(self, title, url):
        """Categorize tracker by type"""
        title_lower = title.lower()
        url_lower = url.lower()
        
        categories = {
            'finance': ['finance', 'banking', 'investment', 'trading', 'quant', 'hedge'],
            'tech': ['tech', 'software', 'engineering', 'developer', 'programmer'],
            'consulting': ['consulting', 'strategy', 'advisory'],
            'marketing': ['marketing', 'advertising', 'media', 'communication'],
            'general': ['internship', 'graduate', 'career']
        }
        
        for category, keywords in categories.items():
            if any(keyword in title_lower or keyword in url_lower for keyword in keywords):
                return category
        
        return 'general'
    
    def scrape_tracker_links(self, tracker_url, tracker_title):
        """Scrape application links from a specific tracker"""
        print(f"🔍 Scraping tracker: {tracker_title}")
        print(f"🔗 URL: {tracker_url}")
        
        try:
            # Navigate to tracker page
            self.driver.get(tracker_url)
            print("📄 Page loaded, waiting for content...")
            
            time.sleep(5)
            self._handle_cookies_and_popups()
            time.sleep(3)
            
            # Get page source after JavaScript execution
            page_source = self.driver.page_source
            print(f"📄 Page source length: {len(page_source)} characters")
            
            # Look for application links
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
                                'source': 'direct_link',
                                'tracker': tracker_title,
                                'tracker_url': tracker_url
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
                                    'source': 'button_parent',
                                    'tracker': tracker_title,
                                    'tracker_url': tracker_url
                                })
                except Exception as e:
                    continue
            
            # Method 3: Look for specific patterns in the page source
            # This is a fallback method
            source_links = self._extract_links_from_source(page_source, tracker_title, tracker_url)
            links.extend(source_links)
            
            # Remove duplicates
            unique_links = []
            seen_urls = set()
            for link in links:
                if link['url'] not in seen_urls:
                    unique_links.append(link)
                    seen_urls.add(link['url'])
            
            print(f"📊 Found {len(unique_links)} unique application links from {tracker_title}")
            
            return unique_links
            
        except Exception as e:
            print(f"❌ Error scraping tracker {tracker_title}: {e}")
            return []
    
    def _extract_links_from_source(self, page_source, tracker_title, tracker_url):
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
                    'source': 'source_regex',
                    'tracker': tracker_title,
                    'tracker_url': tracker_url
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
    
    def scrape_all_trackers(self):
        """Scrape all trackers and collect all application links"""
        print("🚀 Starting comprehensive Trackr scraping...")
        
        # Discover tracker pages
        trackers = self.discover_tracker_pages()
        
        if not trackers:
            print("❌ No trackers found")
            return []
        
        all_links = []
        
        for i, tracker in enumerate(trackers, 1):
            print(f"\n📋 Processing tracker {i}/{len(trackers)}: {tracker['title']}")
            
            links = self.scrape_tracker_links(tracker['url'], tracker['title'])
            all_links.extend(links)
            
            # Add delay between trackers
            if i < len(trackers):
                print("⏳ Waiting 10 seconds before next tracker...")
                time.sleep(10)
        
        # Remove duplicates across all trackers
        unique_links = []
        seen_urls = set()
        for link in all_links:
            if link['url'] not in seen_urls:
                unique_links.append(link)
                seen_urls.add(link['url'])
        
        print(f"\n📊 Total unique application links found: {len(unique_links)}")
        
        # Save all links
        self.save_all_links(unique_links)
        
        return unique_links
    
    def save_all_links(self, links):
        """Save all collected links"""
        with open(self.all_links_file, 'w') as f:
            json.dump({
                'scraped_at': datetime.now().isoformat(),
                'total_links': len(links),
                'links': links
            }, f, indent=2)
        print(f"💾 Saved {len(links)} links to {self.all_links_file}")
    
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
    
    def _handle_cookies_and_popups(self):
        """Handle cookie consent and popup dialogs"""
        try:
            cookie_texts = ['accept', 'accept all', 'continue', 'ok', 'got it', 'i agree']
            
            for text in cookie_texts:
                try:
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
    
    def close_driver(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()
            self.driver = None

def main():
    """Main function to run the navigator scraper"""
    print("🎯 Trackr Navigator Scraper")
    print("=" * 50)
    
    scraper = TrackrNavigatorScraper(headless=False)  # Use visible browser for debugging
    
    try:
        # Scrape all trackers
        all_links = scraper.scrape_all_trackers()
        
        if all_links:
            print(f"\n🎉 Scraping completed!")
            print(f"📊 Total applications found: {len(all_links)}")
            print(f"📁 Results saved to: {scraper.all_links_file}")
        
    except Exception as e:
        print(f"❌ Scraping failed: {e}")
    
    finally:
        scraper.close_driver()

if __name__ == "__main__":
    main()

