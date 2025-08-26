#!/usr/bin/env python3
"""
Sample Trackr Application Testing
Test form filling with just a few Trackr applications to verify functionality.
"""

import sys
import os
import json
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ApplicationFiller import ApplicationFiller

def test_sample_applications():
    """Test form filling with a sample of Trackr applications"""
    
    # Load cleaned links
    try:
        with open("trackr_links_clean.json", 'r') as f:
            all_links = json.load(f)
    except FileNotFoundError:
        print("❌ No cleaned links found. Run clean_trackr_links.py first.")
        return
    
    # Select a small sample for testing (first 3)
    sample_links = all_links[:3]
    
    print(f"🧪 Testing sample of {len(sample_links)} applications")
    print("=" * 60)
    
    results = []
    
    for i, link_info in enumerate(sample_links, 1):
        url = link_info['url']
        company = link_info.get('company', 'Unknown Company')
        
        print(f"\n📋 Test {i}/{len(sample_links)}: {company}")
        print(f"🔗 URL: {url}")
        
        try:
            # Determine job type
            job_type = determine_job_type(company, url)
            resume_path = get_resume_path(job_type)
            
            print(f"📄 Using {job_type} resume: {resume_path}")
            
            # Create ApplicationFiller instance
            filler = ApplicationFiller(
                link=url,
                headless=False,  # Use visible browser for testing
                slow_mode=True,  # Slow mode for better visualization
                model="llama3.2",
                resume_path=resume_path,
                company_name=company,
                job_title=link_info.get('text', '')
            )
            
            # Attempt to submit the application
            result = filler.submit(multi_url_mode=True)
            
            # Check result
            if isinstance(result, str):
                status = "partial"
                message = f"Form filled but submission failed: {result}"
                print(f"⚠️ {message}")
            elif result:
                status = "success"
                message = "Application submitted successfully"
                print(f"✅ {message}")
            else:
                status = "error"
                message = "Application failed"
                print(f"❌ {message}")
            
            # Close driver
            filler.close_driver()
            
            results.append({
                'url': url,
                'company': company,
                'job_type': job_type,
                'status': status,
                'message': message,
                'timestamp': datetime.now().isoformat()
            })
            
        except Exception as e:
            print(f"❌ Error testing {company}: {str(e)}")
            results.append({
                'url': url,
                'company': company,
                'job_type': 'unknown',
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            })
    
    # Generate summary
    print(f"\n{'='*60}")
    print(f"📊 SAMPLE TEST RESULTS")
    print(f"{'='*60}")
    
    success_count = sum(1 for r in results if r['status'] == 'success')
    partial_count = sum(1 for r in results if r['status'] == 'partial')
    error_count = sum(1 for r in results if r['status'] == 'error')
    
    print(f"✅ Success: {success_count}/{len(results)}")
    print(f"⚠️ Partial: {partial_count}/{len(results)}")
    print(f"❌ Error: {error_count}/{len(results)}")
    
    for result in results:
        if result['status'] == 'success':
            status_icon = "✅"
        elif result['status'] == 'partial':
            status_icon = "⚠️"
        else:
            status_icon = "❌"
        
        print(f"{status_icon} {result['company']} ({result['job_type']}) - {result['status']}")
    
    return results

def determine_job_type(company, url):
    """Determine job type for resume selection"""
    company_lower = company.lower()
    url_lower = url.lower()
    
    # Quant/Finance companies
    quant_keywords = ['quant', 'trading', 'hedge', 'investment', 'capital', 'asset', 'fund', 'deshaw', 'citadel', 'point72', 'virtu', 'jane street', 'jump trading', 'drw', 'gsa']
    if any(keyword in company_lower or keyword in url_lower for keyword in quant_keywords):
        return 'quant'
    
    # Communication/Marketing companies
    comm_keywords = ['marketing', 'communication', 'media', 'advertising', 'pr', 'public', 'sky', 'revolut']
    if any(keyword in company_lower or keyword in url_lower for keyword in comm_keywords):
        return 'communication'
    
    return 'swe'

def get_resume_path(job_type):
    """Get resume path for job type"""
    resume_paths = {
        'swe': "AdiPrabs_SWE.docx",
        'quant': "AdiPrabs_Quant.docx", 
        'communication': "AdiPrabs_Cons.docx"
    }
    
    resume_path = resume_paths.get(job_type, "AdiPrabs_SWE.docx")
    
    if not os.path.exists(resume_path):
        print(f"⚠️ Resume file not found: {resume_path}, using default")
        return "AdiPrabs_SWE.docx"
    
    return resume_path

if __name__ == "__main__":
    test_sample_applications()

