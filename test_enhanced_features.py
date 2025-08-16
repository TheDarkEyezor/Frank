#!/usr/bin/env python3
"""
Test script for enhanced ApplicationFiller with cookie handling and early job extraction
"""

from ApplicationFiller import ApplicationFiller

def test_revolut_application():
    """Test the Revolut application with new features"""
    
    print("🚀 Testing Enhanced ApplicationFiller with Revolut")
    print("=" * 60)
    
    # Revolut job application URL
    revolut_url = "https://revolut.com/careers/apply/f82b7f48-1185-4be1-b004-5131fe0ca519/"
    
    print(f"🎯 Target: Revolut - Marketing Manager")
    print(f"🔗 URL: {revolut_url}")
    print()
    
    print("🔧 New features being tested:")
    print("  ✅ Cookie consent handling")
    print("  ✅ Early job information extraction")
    print("  ✅ Redirect handling")
    print("  ✅ Website-specific field mappings")
    print("  ✅ Enhanced form filling order")
    print()
    
    # Create enhanced ApplicationFiller instance
    filler = ApplicationFiller(
        link=revolut_url,
        headless=False,  # Live mode to see what's happening
        slow_mode=True,  # Visual effects
        model="llama3.2",
        company_name="Revolut",
        job_title="Marketing Manager"
    )
    
    print("🚀 Starting application process...")
    print("📋 Process order:")
    print("  1. Navigate to URL")
    print("  2. Handle cookie consent")
    print("  3. Handle redirects")
    print("  4. Extract job information EARLY")
    print("  5. Analyze job for resume selection")
    print("  6. Handle account creation if needed")
    print("  7. Handle Apply button if needed")
    print("  8. Handle cookies again (if new page)")
    print("  9. Fill form with website-specific responses")
    print("  10. Submit application")
    print()
    
    try:
        result = filler.submit()
        
        if isinstance(result, str):
            print(f"\n⚠️ Manual completion required at: {result}")
            print("🔄 Browser will stay open for manual completion")
            print("🔍 Check for any issues with:")
            print("  - Cookie consent (should be automatically accepted)")
            print("  - Job information extraction (check console output)")
            print("  - Website-specific fields (pronouns, F1 experience, etc.)")
        else:
            print("\n🎉 Application submitted successfully!")
            
    except KeyboardInterrupt:
        print("\n⏹️ Process interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        print("\n🔧 Cleanup will happen when you close the browser")
        print("📋 Check the console output for:")
        print("  - Cookie handling messages")
        print("  - Job information extraction")
        print("  - Website-specific field responses")
        print("  - Any redirect notifications")

def test_multiple_sites():
    """Test multiple websites to verify improvements"""
    
    websites = [
        {
            "name": "Revolut (Enhanced)",
            "url": "https://revolut.com/careers/apply/f82b7f48-1185-4be1-b004-5131fe0ca519/",
            "company": "Revolut",
            "title": "Marketing Manager",
            "features": ["Cookie handling", "Early job extraction", "Website-specific fields"]
        },
        {
            "name": "Helsing AI",
            "url": "https://helsing.ai/jobs/4489089101",
            "company": "Helsing",
            "title": "AI Research Intern",
            "features": ["Direct form", "Early job extraction"]
        }
    ]
    
    print("🧪 Multi-site testing mode")
    print("=" * 60)
    
    for i, site in enumerate(websites):
        print(f"\n{i+1}. {site['name']}")
        print(f"   Features: {', '.join(site['features'])}")
    
    try:
        choice = input("\nSelect site (1-2) or press Enter for Revolut: ").strip()
        if not choice:
            choice = "1"
        
        selected_idx = int(choice) - 1
        if selected_idx < 0 or selected_idx >= len(websites):
            selected_idx = 0
            
    except (ValueError, KeyboardInterrupt):
        print("Using default: Revolut")
        selected_idx = 0
    
    selected_site = websites[selected_idx]
    
    print(f"\n🎯 Testing: {selected_site['name']}")
    
    filler = ApplicationFiller(
        link=selected_site["url"],
        headless=False,
        slow_mode=True,
        model="llama3.2",
        company_name=selected_site["company"],
        job_title=selected_site["title"]
    )
    
    try:
        result = filler.submit()
        print(f"\n✅ Test completed for {selected_site['name']}")
    except Exception as e:
        print(f"\n❌ Test failed for {selected_site['name']}: {e}")

if __name__ == "__main__":
    print("Choose test mode:")
    print("1. Test Revolut specifically (recommended)")
    print("2. Test multiple sites")
    
    try:
        mode = input("Enter choice (1-2): ").strip()
        if mode == "2":
            test_multiple_sites()
        else:
            test_revolut_application()
    except KeyboardInterrupt:
        print("\n👋 Exiting...")
