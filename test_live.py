#!/usr/bin/env python3
"""
Quick test script for the enhanced ApplicationFiller
"""

from ApplicationFiller import ApplicationFiller

def test_enhanced_features():
    """Test the enhanced ApplicationFiller with all new features"""
    
    print("🚀 Testing Enhanced ApplicationFiller Features")
    print("=" * 60)
    
    # Test configuration
    job_url = "https://job-boards.greenhouse.io/point72/jobs/8018862002?gh_jid=8018862002&gh_src=97fa02a42us&jobCode=CSS-0013383&location=New+York"
    
    print("\n📋 Enhanced Features:")
    print("✅ Live Mode (visible browser) - DEFAULT")
    print("✅ Smart dropdown handling with proper selection")
    print("✅ LLM integration for unknown questions")
    print("✅ Automatic file upload")
    print("✅ Visual feedback with color coding")
    print("✅ Customized responses for company-specific questions")
    
    # Create enhanced filler instance
    print("\n🛠️ Initializing Enhanced ApplicationFiller...")
    filler = ApplicationFiller(
        link=job_url,
        model="llama3.2",
        headless=False,          # LIVE MODE - show browser
        slow_mode=True,          # Visual effects enabled
        ollama_base_url="http://localhost:11434",
        resume_path="sample_resume.txt",  # Auto file upload
        company_name="Point72",   # For customized responses
        job_title="Software Engineer"
    )
    
    print("✅ Enhanced ApplicationFiller initialized")
    print("\n🎬 Starting live demonstration...")
    print("👁️ Watch the browser window for real-time form filling!")
    
    # Test the form filling
    try:
        result = filler.submit()
        
        if result == True:
            print("\n🎉 SUCCESS: Form was filled and submitted successfully!")
        elif isinstance(result, str):
            print(f"\n⚠️ PARTIAL SUCCESS: Form filled but needs manual completion")
            print(f"   Browser will remain open for manual review")
        else:
            print("\n❌ FAILED: Could not complete the form")
            
    except KeyboardInterrupt:
        print("\n⏸️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
    finally:
        print("\n🧹 Test completed!")

def test_ollama_responses():
    """Test Ollama LLM responses"""
    print("\n🤖 Testing Ollama LLM Integration")
    print("=" * 40)
    
    filler = ApplicationFiller(
        company_name="Point72",
        job_title="Software Engineer"
    )
    
    test_questions = [
        "Why do you want to work at Point72?",
        "What interests you about this role?",
        "Describe your experience with financial technology",
        "Do you require visa sponsorship for the US?",
        "How many years of Python experience do you have?"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. Testing: {question}")
        response = filler.query_ollama(question)
        print(f"   Response: {response[:100]}...")

if __name__ == "__main__":
    print("Enhanced ApplicationFiller Test Suite")
    print("=" * 40)
    
    choice = input("\nSelect test:\n1. Full form filling demo (LIVE)\n2. LLM responses only\n3. Both\nChoice (1-3): ").strip()
    
    if choice == "1":
        test_enhanced_features()
    elif choice == "2":
        test_ollama_responses()
    elif choice == "3":
        test_ollama_responses()
        print("\n" + "="*60)
        test_enhanced_features()
    else:
        print("Running full demo...")
        test_enhanced_features()
