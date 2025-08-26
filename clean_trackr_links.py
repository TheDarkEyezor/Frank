#!/usr/bin/env python3
"""
Clean and filter Trackr links
Remove duplicates, test prep sites, and internal links.
"""

import json
from urllib.parse import urlparse

def clean_trackr_links(input_file="trackr_links_enhanced.json", output_file="trackr_links_clean.json"):
    """Clean and filter Trackr links"""
    
    # Load links
    with open(input_file, 'r') as f:
        links = json.load(f)
    
    print(f"📋 Original links: {len(links)}")
    
    # Filter out unwanted links
    filtered_links = []
    seen_urls = set()
    
    # Domains to exclude (test prep, internal links, etc.)
    exclude_domains = [
        'jobtestprep.co.uk',  # Test prep sites
        'the-trackr.com',     # Internal Trackr links
        'app.the-trackr.com'  # Internal Trackr links
    ]
    
    for link in links:
        url = link['url']
        
        # Skip if already seen (duplicate)
        if url in seen_urls:
            continue
        
        # Parse URL
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Skip excluded domains
            if any(exclude_domain in domain for exclude_domain in exclude_domains):
                continue
            
            # Skip relative URLs
            if not parsed.scheme or not parsed.netloc:
                continue
            
            # Add to filtered list
            filtered_links.append(link)
            seen_urls.add(url)
            
        except Exception as e:
            print(f"⚠️ Error parsing URL {url}: {e}")
            continue
    
    print(f"✅ Cleaned links: {len(filtered_links)}")
    
    # Save cleaned links
    with open(output_file, 'w') as f:
        json.dump(filtered_links, f, indent=2)
    
    print(f"💾 Saved cleaned links to {output_file}")
    
    # Show sample of cleaned links
    print(f"\n📋 Sample cleaned links:")
    for i, link in enumerate(filtered_links[:10], 1):
        print(f"{i:2d}. {link['company']} - {link['url']}")
    
    if len(filtered_links) > 10:
        print(f"... and {len(filtered_links) - 10} more")
    
    return filtered_links

if __name__ == "__main__":
    clean_trackr_links()

