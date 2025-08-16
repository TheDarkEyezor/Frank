#!/usr/bin/env python3
"""
Test script for the specific fixes: dropdown Enter key, LLM prompting, and file upload
"""

from ApplicationFiller import ApplicationFiller
import time

def test_dropdown_and_llm_fixes():
    """Test the specific fixes made to the ApplicationFiller"""
    
    print("🧪 Testing Specific Fixes")
    print("=" * 50)
    
    job_url = "https://job-boards.greenhouse.io/point72/jobs/8018862002?gh_jid=8018862002&gh_src=97fa02a42us&jobCode=CSS-0013383&location=New+York"
    
    print("\n🔧 Testing these specific fixes:")
    print("✅ Dropdown selection with Enter key press")
    print("✅ Proper LLM question passing (no more 'ready to assist')")
    print("✅ Enhanced file upload with multiple methods")
    print("✅ Privacy consent handling")
    
    # Create filler instance
    filler = ApplicationFiller(
        link=job_url,
        model="llama3.2",
        headless=False,          # Live mode to see the fixes
        slow_mode=True,          # Slow mode for better observation
        resume_path="sample_resume.txt",
        company_name="Point72",
        job_title="Quantitative Research Intern (NLP)"
    )
    
    print("\n🎬 Starting test...")
    print("👀 Watch for:")
    print("  - Dropdown selections followed by Enter key press")
    print("  - Textarea getting actual question content (not 'ready to assist')")
    print("  - File upload attempts with fallback methods")
    
    try:
        # Test the specific fixes
        result = filler.submit()
        
        if result == True:
            print("\n🎉 SUCCESS: All fixes working properly!")
        elif isinstance(result, str):
            print(f"\n✅ PARTIAL SUCCESS: Fixes applied, manual completion needed")
        else:
            print("\n⚠️ Some issues may remain")
            
    except KeyboardInterrupt:
        print("\n⏸️ Test interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        print("\n🧹 Test completed")

def test_llm_question_handling():
    """Test that LLM gets proper questions instead of 'ready to assist'"""
    
    print("\n🤖 Testing LLM Question Handling")
    print("=" * 40)
    
    filler = ApplicationFiller(
        company_name="Point72",
        job_title="Quantitative Research Intern"
    )
    
    # Test questions that should NOT result in "ready to assist"
    test_questions = [
        "Note to Hiring Manager:",
        "Why do you want to work at Point72?",
        "Tell us about your interest in quantitative research",
        "What makes you a good fit for this role?",
        "Additional comments or information"
    ]
    
    print("Testing that LLM receives actual questions...")
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. Testing: {question}")
        response = filler.query_ollama(question)
        
        # Check if response is the problematic "ready to assist" message
        if "ready to assist" in response.lower() or "what is the question" in response.lower():
            print(f"   ❌ ISSUE: Got 'ready to assist' response: {response[:100]}...")
        else:
            print(f"   ✅ GOOD: Got proper response: {response[:100]}...")

if __name__ == "__main__":
    print("ApplicationFiller Fixes Test Suite")
    print("=" * 40)
    
    choice = input("\nSelect test:\n1. Full form test (with fixes)\n2. LLM question handling only\n3. Both\nChoice (1-3): ").strip()
    
    if choice == "1":
        test_dropdown_and_llm_fixes()
    elif choice == "2":
        test_llm_question_handling()
    elif choice == "3":
        test_llm_question_handling()
        print("\n" + "="*60)
        test_dropdown_and_llm_fixes()
    else:
        print("Running full test with fixes...")
        test_dropdown_and_llm_fixes()
