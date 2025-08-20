#!/usr/bin/env python3
"""
Test script for multi-URL functionality
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ApplicationFiller import ApplicationFiller

def test_multi_url():
    """Test the multi-URL processing functionality"""
    
    # Test URLs (using shorter test list)
    test_urls = [
        "https://helsing.ai/jobs/4489089101",
        "https://job-boards.greenhouse.io/point72/jobs/8018862002"
    ]
    
    print("🚀 Testing Multi-URL Application Processing...")
    print(f"📝 Processing {len(test_urls)} URLs")
    
    # Create instance for multi-URL processing
    filler = ApplicationFiller(
        link="",  # Will be set for each URL
        headless=False,  # Use visible browser for testing
        slow_mode=False,  # Faster for testing
        model="llama3.2",
        resume_path="AdiPrabs_SWE.docx"
    )
    
    try:
        # Test the multi-URL processing
        results = filler.run_multiple_applications(test_urls)
        
        print(f"\n📊 TEST RESULTS:")
        success_count = sum(1 for r in results if r['status'] == 'success')
        partial_count = sum(1 for r in results if r['status'] == 'partial')
        error_count = sum(1 for r in results if r['status'] == 'error')
        
        print(f"✅ Fully completed: {success_count}/{len(results)}")
        print(f"⚠️ Partially completed (manual finish needed): {partial_count}/{len(results)}")
        print(f"❌ Failed: {error_count}/{len(results)}")
        
        for result in results:
            if result['status'] == 'success':
                status_icon = "✅"
            elif result['status'] == 'partial':
                status_icon = "⚠️"
            else:
                status_icon = "❌"
            
            print(f"{status_icon} {result['url']}")
            if result['status'] == 'error':
                print(f"   Error: {result['error']}")
            elif result['status'] == 'partial':
                print(f"   Needs manual completion")
                
        return results
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return []

if __name__ == "__main__":
    test_multi_url()
