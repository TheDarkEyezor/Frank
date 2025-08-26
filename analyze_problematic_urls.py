#!/usr/bin/env python3
"""
Analyze Problematic URLs
Analyze the failed URLs to understand specific issues and create targeted fixes.
"""

import json
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urlparse
import re

def load_failed_urls():
    """Load failed URLs from the results file"""
    try:
        with open("application_results/failed_urls_20250821_201354.json", 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading failed URLs: {e}")
        return []

def analyze_url_structure(url_data):
    """Analyze the structure of a problematic URL"""
    url = url_data['url']
    company = url_data['company']
    job_title = url_data['job_title']
    
    print(f"\n🔍 Analyzing: {company}")
    print(f"🔗 URL: {url}")
    print(f"📋 Job: {job_title}")
    
    # Parse URL
    parsed_url = urlparse(url)
    domain = parsed_url.netloc
    
    analysis = {
        'company': company,
        'url': url,
        'domain': domain,
        'issues': [],
        'recommendations': []
    }
    
    # Analyze based on domain patterns
    if 'deshaw.com' in domain:
        analysis['issues'].append('Career site - requires Apply button click')
        analysis['issues'].append('No form fields found on initial page')
        analysis['recommendations'].append('Implement Apply button detection and clicking')
        analysis['recommendations'].append('Wait for form to load after Apply button')
        
    elif 'smartrecruiters.com' in domain:
        analysis['issues'].append('SmartRecruiters portal - complex form structure')
        analysis['issues'].append('May require iframe handling')
        analysis['recommendations'].append('Add SmartRecruiters-specific form detection')
        analysis['recommendations'].append('Handle iframes and dynamic content')
        
    elif 'tal.net' in domain:
        analysis['issues'].append('TAL.net portal - specialized application system')
        analysis['issues'].append('May require account creation or login')
        analysis['recommendations'].append('Implement TAL.net portal handling')
        analysis['recommendations'].append('Add account creation/login logic')
        
    elif 'jobtestprep.co.uk' in domain:
        analysis['issues'].append('Test preparation site - not actual application')
        analysis['issues'].append('This is a practice/test site, not real application')
        analysis['recommendations'].append('Skip these URLs - they are test sites')
        analysis['recommendations'].append('Filter out jobtestprep.co.uk URLs')
        
    elif 'apptrkr.io' in domain:
        analysis['issues'].append('AppTrkr portal - specialized application system')
        analysis['issues'].append('May require specific form handling')
        analysis['recommendations'].append('Implement AppTrkr-specific handling')
        analysis['recommendations'].append('Add portal-specific form detection')
        
    elif 'bnpparibas.co.uk' in domain:
        analysis['issues'].append('BNP Paribas career site - requires navigation')
        analysis['issues'].append('May need to find specific job posting')
        analysis['recommendations'].append('Implement job search and navigation')
        analysis['recommendations'].append('Add BNP Paribas-specific handling')
        
    elif 'temasek.com.sg' in domain:
        analysis['issues'].append('Temasek career portal - may require login')
        analysis['issues'].append('Could be account-based application system')
        analysis['recommendations'].append('Implement Temasek portal handling')
        analysis['recommendations'].append('Add account creation/login logic')
        
    elif 'mlp.com' in domain:
        analysis['issues'].append('MLP career site - may require job search')
        analysis['issues'].append('Could need to navigate to specific position')
        analysis['recommendations'].append('Implement MLP-specific navigation')
        analysis['recommendations'].append('Add job search functionality')
        
    else:
        analysis['issues'].append('Unknown domain - needs investigation')
        analysis['recommendations'].append('Manual investigation required')
    
    return analysis

def test_url_accessibility(url_data):
    """Test if the URL is accessible and analyze its content"""
    url = url_data['url']
    company = url_data['company']
    
    print(f"🌐 Testing accessibility for {company}...")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ URL accessible (Status: {response.status_code})")
            
            # Analyze content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for common patterns
            analysis = {
                'accessible': True,
                'status_code': response.status_code,
                'content_length': len(response.content),
                'has_forms': len(soup.find_all('form')) > 0,
                'has_apply_button': bool(soup.find_all(text=re.compile(r'apply', re.I))),
                'has_login': bool(soup.find_all(text=re.compile(r'login|sign in', re.I))),
                'has_cookies': bool(soup.find_all(text=re.compile(r'cookie|privacy', re.I))),
                'title': soup.title.string if soup.title else 'No title'
            }
            
            print(f"   📄 Content length: {analysis['content_length']} bytes")
            print(f"   📝 Title: {analysis['title']}")
            print(f"   📋 Forms found: {analysis['has_forms']}")
            print(f"   🎯 Apply button found: {analysis['has_apply_button']}")
            print(f"   🔐 Login required: {analysis['has_login']}")
            print(f"   🍪 Cookie notice: {analysis['has_cookies']}")
            
            return analysis
            
        else:
            print(f"❌ URL not accessible (Status: {response.status_code})")
            return {
                'accessible': False,
                'status_code': response.status_code,
                'error': f'HTTP {response.status_code}'
            }
            
    except Exception as e:
        print(f"❌ Error accessing URL: {e}")
        return {
            'accessible': False,
            'error': str(e)
        }

def categorize_issues(failed_urls):
    """Categorize issues by type"""
    categories = {
        'apply_button_required': [],
        'portal_specific': [],
        'test_sites': [],
        'login_required': [],
        'navigation_required': [],
        'unknown': []
    }
    
    for url_data in failed_urls:
        url = url_data['url']
        domain = urlparse(url).netloc
        
        if 'jobtestprep.co.uk' in domain:
            categories['test_sites'].append(url_data)
        elif 'smartrecruiters.com' in domain or 'tal.net' in domain or 'apptrkr.io' in domain:
            categories['portal_specific'].append(url_data)
        elif 'deshaw.com' in domain:
            categories['apply_button_required'].append(url_data)
        elif 'temasek.com.sg' in domain:
            categories['login_required'].append(url_data)
        elif 'bnpparibas.co.uk' in domain or 'mlp.com' in domain:
            categories['navigation_required'].append(url_data)
        else:
            categories['unknown'].append(url_data)
    
    return categories

def generate_fixes_report(categories, analyses):
    """Generate a report with specific fixes for each category"""
    print(f"\n{'='*60}")
    print("🔧 ISSUE ANALYSIS AND FIXES REPORT")
    print(f"{'='*60}")
    
    for category, urls in categories.items():
        if urls:
            print(f"\n📋 {category.upper().replace('_', ' ')} ({len(urls)} URLs):")
            
            for url_data in urls:
                company = url_data['company']
                url = url_data['url']
                print(f"   • {company}: {url}")
            
            # Get analysis for this category
            if category in analyses:
                analysis = analyses[category]
                print(f"   🔧 Fixes needed:")
                for rec in analysis.get('recommendations', []):
                    print(f"      - {rec}")

def main():
    """Main function"""
    print("🔍 Analyzing Problematic URLs")
    print("=" * 50)
    
    # Load failed URLs
    failed_urls = load_failed_urls()
    if not failed_urls:
        print("❌ No failed URLs found")
        return
    
    print(f"📊 Found {len(failed_urls)} failed URLs to analyze")
    
    # Analyze each URL
    analyses = {}
    accessibility_results = {}
    
    for url_data in failed_urls:
        # Analyze URL structure
        analysis = analyze_url_structure(url_data)
        
        # Test accessibility
        accessibility = test_url_accessibility(url_data)
        accessibility_results[url_data['url']] = accessibility
        
        # Store analysis
        domain = urlparse(url_data['url']).netloc
        if domain not in analyses:
            analyses[domain] = analysis
        
        time.sleep(1)  # Be respectful
    
    # Categorize issues
    categories = categorize_issues(failed_urls)
    
    # Generate fixes report
    generate_fixes_report(categories, analyses)
    
    # Save analysis results
    with open("url_analysis_results.json", "w") as f:
        json.dump({
            'failed_urls': failed_urls,
            'categories': categories,
            'analyses': analyses,
            'accessibility_results': accessibility_results
        }, f, indent=2)
    
    print(f"\n💾 Analysis results saved to: url_analysis_results.json")
    
    # Summary
    print(f"\n📊 SUMMARY:")
    total_urls = len(failed_urls)
    for category, urls in categories.items():
        if urls:
            percentage = (len(urls) / total_urls) * 100
            print(f"   {category.replace('_', ' ').title()}: {len(urls)} URLs ({percentage:.1f}%)")

if __name__ == "__main__":
    main()

