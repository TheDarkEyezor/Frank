#!/usr/bin/env python3
"""
Demo script showing multi-website support with enhanced dropdown handling
"""

from ApplicationFiller import ApplicationFiller

def demo_multi_site_support():
    """Demonstrate the enhanced ApplicationFiller with multi-website support"""
    
    print("🚀 Enhanced ApplicationFiller - Multi-Website Support Demo")
    print("=" * 60)
    
    # Available test websites
    websites = [
        {
            "name": "Point72 (Greenhouse)",
            "url": "https://job-boards.greenhouse.io/point72/jobs/8018862002",
            "company": "Point72",
            "title": "Software Engineer",
            "features": ["Greenhouse dropdowns", "Enter key handling", "File upload"]
        },
        {
            "name": "Helsing AI",
            "url": "https://helsing.ai/jobs/4489089101", 
            "company": "Helsing",
            "title": "AI Research Intern",
            "features": ["Direct form", "Custom fields", "PDF upload"]
        },
        {
            "name": "Revolut",
            "url": "https://www.revolut.com/careers/position/marketing-manager-f82b7f48-1185-4be1-b004-5131fe0ca519/",
            "company": "Revolut",
            "title": "Marketing Manager", 
            "features": ["Apply button", "Account creation", "Modern UI"]
        },
        {
            "name": "Da Vinci Trading",
            "url": "https://davincitrading.com/job/quant-trading-intern/",
            "company": "Da Vinci",
            "title": "Quant Trading Intern",
            "features": ["Career portal", "Quant resume selection", "Apply button"]
        }
    ]
    
    print("Available websites:")
    for i, site in enumerate(websites):
        print(f"  {i+1}. {site['name']} - {site['title']}")
        print(f"     Features: {', '.join(site['features'])}")
        print()
    
    # Get user selection
    try:
        choice = input("Select website (1-4) or press Enter for Point72: ").strip()
        if not choice:
            choice = "1"
        
        selected_idx = int(choice) - 1
        if selected_idx < 0 or selected_idx >= len(websites):
            selected_idx = 0
            
    except (ValueError, KeyboardInterrupt):
        print("Using default: Point72")
        selected_idx = 0
    
    selected_site = websites[selected_idx]
    
    print(f"\n🎯 Selected: {selected_site['name']}")
    print(f"🏢 Company: {selected_site['company']}")
    print(f"💼 Position: {selected_site['title']}")
    print(f"🔧 Features: {', '.join(selected_site['features'])}")
    print()
    
    print("🚀 Starting ApplicationFiller...")
    print("📋 Features enabled:")
    print("  ✅ Smart dropdown handling with Enter key support")
    print("  ✅ Multi-resume selection (SWE/Quant/Communication)")
    print("  ✅ Account creation for applicable sites")
    print("  ✅ Apply button detection")
    print("  ✅ Browser persistence on errors")
    print("  ✅ Ollama LLM integration")
    print("  ✅ Live visual feedback")
    print()
    
    # Create enhanced ApplicationFiller instance
    filler = ApplicationFiller(
        link=selected_site["url"],
        headless=False,  # Live mode for demonstration
        slow_mode=True,  # Visual effects
        model="llama3.2",
        company_name=selected_site["company"],
        job_title=selected_site["title"]
    )
    
    # Run the application process
    try:
        result = filler.submit()
        
        if isinstance(result, str):
            print(f"\n⚠️ Manual completion required at: {result}")
            print("🔄 Browser will stay open for manual completion")
        else:
            print("\n🎉 Application submitted successfully!")
            
    except KeyboardInterrupt:
        print("\n⏹️ Process interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        # Cleanup
        try:
            filler.close_driver()
        except:
            pass
    
    print("\n" + "=" * 60)
    print("✨ Demo completed!")
    print("🔧 Key improvements implemented:")
    print("  • Fixed dropdown Enter key issue for Greenhouse forms")
    print("  • Added multi-website support with site-specific handling")
    print("  • Enhanced job analysis for automatic resume selection")
    print("  • Improved error handling with browser persistence")
    print("  • Added account creation capabilities")
    print("=" * 60)

if __name__ == "__main__":
    demo_multi_site_support()
