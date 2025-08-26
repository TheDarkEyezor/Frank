#!/usr/bin/env python3
"""
Master Trackr Scraper
Scrapes all Trackr tables and maintains a record of visited websites to avoid re-applying.
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

class TrackrMasterScraper:
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
    
    def load_visited_websites(self):
        """Load list of previously visited websites"""
        try:
            with open(self.visited_websites_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                'visited_urls': [],
                'visited_domains': [],
                'last_updated': datetime.now().isoformat(),
                'total_applications': 0,
                'successful_applications': 0,
                'failed_applications': 0
            }
    
    def save_visited_websites(self, visited_data):
        """Save visited websites data"""
        with open(self.visited_websites_file, 'w') as f:
            json.dump(visited_data, f, indent=2)
    
    def mark_website_visited(self, url, status="visited"):
        """Mark a website as visited"""
        visited_data = self.load_visited_websites()
        
        # Add URL
        if url not in visited_data['visited_urls']:
            visited_data['visited_urls'].append(url)
        
        # Add domain
        domain = urlparse(url).netloc
        if domain not in visited_data['visited_domains']:
            visited_data['visited_domains'].append(domain)
        
        # Update counters
        visited_data['total_applications'] += 1
        if status == "success":
            visited_data['successful_applications'] += 1
        elif status == "failed":
            visited_data['failed_applications'] += 1
        
        visited_data['last_updated'] = datetime.now().isoformat()
        
        self.save_visited_websites(visited_data)
    
    def is_website_visited(self, url):
        """Check if a website has been visited"""
        visited_data = self.load_visited_websites()
        return url in visited_data['visited_urls']
    
    def get_all_trackr_tables(self):
        """Get all available Trackr tables/trackers"""
        print("🔍 Discovering all Trackr tables...")
        
        try:
            if not self.driver:
                self.setup_driver()
            
            # Navigate to main Trackr page
            self.driver.get("https://the-trackr.com/trackers/")
            print("📄 Loading Trackr main page...")
            
            time.sleep(5)
            self._handle_cookies_and_popups()
            time.sleep(3)
            
            # Find all tracker links
            tracker_links = []
            
            # Look for links that contain tracker information
            all_links = self.driver.find_elements(By.TAG_NAME, "a")
            
            for link in all_links:
                try:
                    href = link.get_attribute('href')
                    text = link.text.strip()
                    
                    if href and text:
                        # Look for tracker-related links
                        if any(keyword in href.lower() for keyword in ['tracker', 'trackers', 'app.the-trackr.com']):
                            tracker_links.append({
                                'url': href,
                                'title': text,
                                'type': self._categorize_tracker(text, href)
                            })
                except Exception as e:
                    continue
            
            # Remove duplicates
            unique_trackers = []
            seen_urls = set()
            for tracker in tracker_links:
                if tracker['url'] not in seen_urls:
                    unique_trackers.append(tracker)
                    seen_urls.add(tracker['url'])
            
            print(f"📊 Found {len(unique_trackers)} unique trackers")
            
            return unique_trackers
            
        except Exception as e:
            print(f"❌ Error discovering trackers: {e}")
            return []
    
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
    
    def scrape_all_trackers(self):
        """Scrape all trackers and collect all application links"""
        print("🚀 Starting comprehensive Trackr scraping...")
        
        # Get all trackers
        trackers = self.get_all_trackr_tables()
        
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
    
    def analyze_application_barriers(self, links):
        """Analyze common barriers that prevent automatic applications"""
        print("\n🔍 Analyzing application barriers...")
        
        barriers = {
            'account_required': [],
            'complex_forms': [],
            'external_portals': [],
            'test_required': [],
            'manual_process': [],
            'unknown': []
        }
        
        for link in links:
            url = link['url']
            company = link['company']
            
            barrier = self._identify_barrier(url, company)
            barriers[barrier].append(link)
        
        # Print analysis
        print(f"\n📊 APPLICATION BARRIER ANALYSIS:")
        print(f"{'='*60}")
        
        for barrier_type, link_list in barriers.items():
            if link_list:
                print(f"\n🔴 {barrier_type.upper().replace('_', ' ')}: {len(link_list)} applications")
                for link in link_list[:5]:  # Show first 5 examples
                    print(f"   • {link['company']} - {link['url']}")
                if len(link_list) > 5:
                    print(f"   ... and {len(link_list) - 5} more")
        
        # Save analysis
        with open("application_barriers_analysis.json", 'w') as f:
            json.dump({
                'analysis_date': datetime.now().isoformat(),
                'barriers': barriers,
                'summary': {k: len(v) for k, v in barriers.items()}
            }, f, indent=2)
        
        return barriers
    
    def _identify_barrier(self, url, company):
        """Identify what prevents automatic application for a given URL"""
        url_lower = url.lower()
        company_lower = company.lower()
        
        # Account creation required
        account_keywords = ['login', 'signin', 'register', 'account', 'profile']
        if any(keyword in url_lower for keyword in account_keywords):
            return 'account_required'
        
        # External application portals
        portal_keywords = ['workday', 'greenhouse', 'lever', 'bamboohr', 'smartrecruiters', 'icims', 'taleo']
        if any(keyword in url_lower for keyword in portal_keywords):
            return 'external_portals'
        
        # Test requirements
        test_keywords = ['test', 'assessment', 'hirevue', 'pymetrics', 'cut-e', 'cappfinity']
        if any(keyword in url_lower for keyword in test_keywords):
            return 'test_required'
        
        # Complex forms (heuristic)
        if len(url) > 200 or '?' in url and url.count('&') > 5:
            return 'complex_forms'
        
        # Manual process indicators
        manual_keywords = ['email', 'contact', 'phone', 'call', 'manual']
        if any(keyword in url_lower for keyword in manual_keywords):
            return 'manual_process'
        
        return 'unknown'
    
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
        
        text = text.strip()
        words = text.split()
        if len(words) <= 3:
            return text
        else:
            return ' '.join(words[:3])
    
    def close_driver(self):
        """Close the browser driver"""
        if self.driver:
            self.driver.quit()
            self.driver = None

def main():
    """Main function to run the master scraper"""
    print("🎯 Trackr Master Scraper")
    print("=" * 50)
    
    scraper = TrackrMasterScraper(headless=False)  # Use visible browser for debugging
    
    try:
        # Scrape all trackers
        all_links = scraper.scrape_all_trackers()
        
        if all_links:
            # Analyze barriers
            barriers = scraper.analyze_application_barriers(all_links)
            
            print(f"\n🎉 Scraping completed!")
            print(f"📊 Total applications found: {len(all_links)}")
            print(f"📁 Results saved to: {scraper.all_links_file}")
            print(f"📁 Barrier analysis saved to: application_barriers_analysis.json")
            print(f"📁 Visited websites tracked in: {scraper.visited_websites_file}")
        
    except Exception as e:
        print(f"❌ Scraping failed: {e}")
    
    finally:
        scraper.close_driver()

if __name__ == "__main__":
    main()
