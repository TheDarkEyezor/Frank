#!/usr/bin/env python3
"""
Simple test script for Trackr scraper
"""

from trackr_scraper import TrackrScraper

def test_scraper():
    """Test the Trackr scraper functionality"""
    print("🧪 Testing Trackr Scraper...")
    
    scraper = TrackrScraper()
    
    # Test scraping
    links = scraper.get_internship_links()
    
    if links:
        print(f"✅ Successfully found {len(links)} links")
        print("\n📋 Sample links:")
        for i, link in enumerate(links[:5], 1):  # Show first 5
            print(f"{i}. {link['company']} - {link['url']}")
            print(f"   Source: {link['source']}")
        
        if len(links) > 5:
            print(f"... and {len(links) - 5} more")
        
        # Save links
        scraper.save_links(links)
        print(f"\n💾 Links saved to trackr_links.json")
        
        return links
    else:
        print("❌ No links found")
        return []

if __name__ == "__main__":
    test_scraper()

