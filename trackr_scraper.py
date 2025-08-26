#!/usr/bin/env python3
"""
Trackr Website Scraper
Scrapes the Trackr website to extract all application links for UK finance summer internships.
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urljoin, urlparse
import re

class TrackrScraper:
    def __init__(self):
        self.base_url = "https://app.the-trackr.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        
    def get_internship_links(self, url="https://app.the-trackr.com/uk-finance/summer-internships"):
        """Extract all internship application links from Trackr"""
        print(f"🔍 Scraping Trackr website: {url}")
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all links that might be application links
            links = []
            
            # Look for various patterns that might contain application links
            # This is a heuristic approach since we need to identify the actual structure
            
            # Method 1: Look for links with common application keywords
            application_keywords = ['apply', 'application', 'careers', 'jobs', 'internship']
            
            for link in soup.find_all('a', href=True):
                href = link.get('href', '').lower()
                text = link.get_text().lower()
                
                # Check if link contains application-related keywords
                if any(keyword in href or keyword in text for keyword in application_keywords):
                    full_url = urljoin(url, link['href'])
                    if self._is_external_application_link(full_url):
                        links.append({
                            'url': full_url,
                            'text': link.get_text().strip(),
                            'company': self._extract_company_name(link.get_text()),
                            'source': 'keyword_match'
                        })
            
            # Method 2: Look for buttons or elements with application text
            buttons = soup.find_all(['button', 'div', 'span'], string=re.compile(r'apply|application', re.I))
            for button in buttons:
                # Look for parent links or onclick handlers
                parent_link = button.find_parent('a')
                if parent_link and parent_link.get('href'):
                    full_url = urljoin(url, parent_link['href'])
                    if self._is_external_application_link(full_url):
                        links.append({
                            'url': full_url,
                            'text': button.get_text().strip(),
                            'company': self._extract_company_name(button.get_text()),
                            'source': 'button_text'
                        })
            
            # Method 3: Look for any external links (heuristic)
            external_links = []
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                if href and not href.startswith('#') and not href.startswith('/'):
                    # Check if it's an external link that might be an application
                    if self._looks_like_application_link(href):
                        links.append({
                            'url': href,
                            'text': link.get_text().strip(),
                            'company': self._extract_company_name(link.get_text()),
                            'source': 'external_link'
                        })
            
            # Remove duplicates based on URL
            unique_links = []
            seen_urls = set()
            for link in links:
                if link['url'] not in seen_urls:
                    unique_links.append(link)
                    seen_urls.add(link['url'])
            
            print(f"📊 Found {len(unique_links)} potential application links")
            
            return unique_links
            
        except Exception as e:
            print(f"❌ Error scraping Trackr: {e}")
            return []
    
    def _is_external_application_link(self, url):
        """Check if URL looks like an external application link"""
        if not url:
            return False
            
        # Skip internal Trackr links
        if 'the-trackr.com' in url:
            return False
            
        # Skip common non-application domains
        skip_domains = ['google.com', 'facebook.com', 'twitter.com', 'linkedin.com', 'youtube.com']
        domain = urlparse(url).netloc.lower()
        if any(skip_domain in domain for skip_domain in skip_domains):
            return False
            
        return True
    
    def _looks_like_application_link(self, url):
        """Heuristic to determine if a URL looks like an application link"""
        url_lower = url.lower()
        
        # Common application-related patterns
        application_patterns = [
            'apply', 'application', 'careers', 'jobs', 'internship', 'position',
            'workday', 'greenhouse', 'lever', 'bamboohr', 'smartrecruiters',
            'icims', 'taleo', 'successfactors', 'brassring', 'hirevue'
        ]
        
        return any(pattern in url_lower for pattern in application_patterns)
    
    def _extract_company_name(self, text):
        """Extract company name from link text"""
        # Simple heuristic - take first few words
        words = text.strip().split()
        if len(words) <= 3:
            return text.strip()
        else:
            return ' '.join(words[:3])
    
    def save_links(self, links, filename="trackr_links.json"):
        """Save extracted links to JSON file"""
        with open(filename, 'w') as f:
            json.dump(links, f, indent=2)
        print(f"💾 Saved {len(links)} links to {filename}")
    
    def load_links(self, filename="trackr_links.json"):
        """Load links from JSON file"""
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"📁 No saved links found in {filename}")
            return []

def main():
    scraper = TrackrScraper()
    
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
            print(f"    Source: {link['source']}")
            print()
        
        return links
    else:
        print("❌ No links found. The website structure might have changed.")
        return []

if __name__ == "__main__":
    main()

