#!/usr/bin/env python3

from ApplicationFiller_fixed import ApplicationFiller

def test_application_filler():
    """Test the ApplicationFiller with a sample job posting - VISIBLE MODE"""
    
    # Point72 job posting URL
    job_url = "https://job-boards.greenhouse.io/point72/jobs/8018862002?gh_jid=8018862002&gh_src=97fa02a42us&jobCode=CSS-0013383&location=New+York"
    
    print("🎬 Testing ApplicationFiller in VISIBLE MODE...")
    print(f"🌐 Target URL: {job_url}")
    print("👀 You will see the browser window and watch the form being filled!")
    print("-" * 70)
    
    # Create filler instance with visible browser and slow mode
    filler = ApplicationFiller(
        link=job_url, 
        headless=False,  # Show the browser window
        slow_mode=True   # Fill forms slowly for better visualization
    )
    
    # Attempt to fill and submit
    try:
        result = filler.submit()
        
        if isinstance(result, str):
            print(f"❌ Could not complete automation")
            print(f"📋 Please complete manually at: {result}")
        else:
            print("🎉 Application submitted successfully!")
            
    except Exception as e:
        print(f"❌ Error occurred: {e}")
    
    finally:
        # Always clean up
        filler.close_driver()

def test_headless_mode():
    """Test the ApplicationFiller in headless mode for comparison"""
    
    job_url = "https://job-boards.greenhouse.io/point72/jobs/8018862002?gh_jid=8018862002&gh_src=97fa02a42us&jobCode=CSS-0013383&location=New+York"
    
    print("\n" + "="*70)
    print("🥷 Testing ApplicationFiller in HEADLESS MODE...")
    print("💨 This will run quickly in the background")
    print("-" * 70)
    
    # Create filler instance with headless mode
    filler = ApplicationFiller(
        link=job_url, 
        headless=True,   # No browser window
        slow_mode=False  # Fast filling
    )
    
    try:
        result = filler.submit()
        
        if isinstance(result, str):
            print(f"❌ Could not complete automation")
            print(f"📋 Please complete manually at: {result}")
        else:
            print("🎉 Application submitted successfully!")
            
    except Exception as e:
        print(f"❌ Error occurred: {e}")
    
    finally:
        filler.close_driver()

if __name__ == "__main__":
    # Test visible mode first
    test_application_filler()
    
    # Uncomment the line below to also test headless mode
    # test_headless_mode()
