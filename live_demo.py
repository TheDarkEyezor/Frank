#!/usr/bin/env python3

"""
Live Demo - Watch the ApplicationFiller fill a webpage in real-time!
Run this to see the browser window open and forms being filled automatically.
"""

from ApplicationFiller_fixed import ApplicationFiller

def live_demo():
    """
    Live demonstration of webpage filling in real-time.
    You will see the browser window open and watch as each field gets filled!
    """
    
    print("🎬 LIVE DEMO - Real-time Webpage Filling")
    print("=" * 60)
    print()
    print("👀 GET READY! You will see:")
    print("   🌐 Chrome browser window opening")
    print("   📄 Job application page loading")
    print("   🔴 Fields highlighted in RED as they're being filled")
    print("   ⌨️  Text being typed character by character")
    print("   🟢 Fields turning GREEN when completed")
    print("   🔵 Submit button highlighted in BLUE before clicking")
    print()
    
    # Job URL for demo
    job_url = "https://job-boards.greenhouse.io/point72/jobs/8018862002?gh_jid=8018862002&gh_src=97fa02a42us&jobCode=CSS-0013383&location=New+York"
    
    print(f"🎯 Target webpage: Point72 Job Application")
    print(f"🔗 URL: {job_url}")
    print()
    
    input("⏳ Press ENTER when you're ready to start the demo...")
    print()
    
    # Create filler with MAXIMUM visual effects
    print("🚀 Initializing ApplicationFiller...")
    filler = ApplicationFiller(
        link=job_url,
        headless=False,     # SHOW the browser window
        slow_mode=True      # SLOW mode for maximum visual effect
    )
    
    print("📱 Starting the live demonstration...")
    print("🎥 Watch your screen - the browser should appear any moment!")
    print()
    
    try:
        # This will open the browser and you'll see everything happen!
        result = filler.submit()
        
        if isinstance(result, str):
            print(f"❌ Demo completed - manual completion needed")
            print(f"🔗 Continue at: {result}")
        else:
            print("🎉 DEMO SUCCESSFUL! Form was filled and submitted!")
            
    except Exception as e:
        print(f"❌ Demo error: {e}")
    
    finally:
        print("🧹 Cleaning up...")
        filler.close_driver()
        print("✅ Demo complete!")

def quick_demo():
    """Quick version without slow mode for faster demonstration"""
    
    print("⚡ QUICK DEMO - Fast webpage filling")
    print("=" * 50)
    
    job_url = "https://job-boards.greenhouse.io/point72/jobs/8018862002?gh_jid=8018862002&gh_src=97fa02a42us&jobCode=CSS-0013383&location=New+York"
    
    filler = ApplicationFiller(
        link=job_url,
        headless=False,     # SHOW the browser 
        slow_mode=False     # Normal speed
    )
    
    try:
        result = filler.submit()
        if isinstance(result, str):
            print(f"Quick demo completed - continue manually at: {result}")
        else:
            print("✅ Quick demo successful!")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        filler.close_driver()

if __name__ == "__main__":
    print("🎭 CHOOSE YOUR DEMO:")
    print("1. 🐌 SLOW DEMO - Maximum visual effects (recommended)")
    print("2. ⚡ QUICK DEMO - Normal speed")
    print("3. ❌ Exit")
    print()
    
    choice = input("Enter your choice (1, 2, or 3): ").strip()
    
    if choice == "1":
        live_demo()
    elif choice == "2":
        quick_demo()
    elif choice == "3":
        print("👋 Goodbye!")
    else:
        print("🤔 Invalid choice. Running slow demo by default...")
        live_demo()
