#!/usr/bin/env python3
"""
Test script for the enhanced ApplicationFiller with Ollama integration
"""

import os
import sys
from ApplicationFiller_enhanced import ApplicationFiller

def test_enhanced_features():
    """Test the enhanced features including dropdown handling and Ollama integration"""
    
    # Point72 job application URL for testing
    job_url = "https://job-boards.greenhouse.io/point72/jobs/8018862002?gh_jid=8018862002&gh_src=97fa02a42us&jobCode=CSS-0013383&location=New+York"
    
    print("🚀 Testing Enhanced ApplicationFiller Features")
    print("=" * 60)
    
    # Test configuration
    print("\n📋 Test Configuration:")
    print(f"- Job URL: {job_url}")
    print(f"- Visual Mode: Enabled (headless=False)")
    print(f"- Slow Mode: Enabled for demonstration")
    print(f"- Ollama Model: llama3.2")
    print(f"- Dropdown Handling: Enhanced with option matching")
    print(f"- LLM Integration: Enabled for unknown questions")
    
    # Check if Ollama is running
    print("\n🔍 Checking Ollama availability...")
    try:
        import requests
        response = requests.get("http://localhost:11434/api/version", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama is running and accessible")
        else:
            print("⚠️ Ollama is not responding properly")
    except:
        print("❌ Ollama is not running. Start it with: ollama serve")
        print("   Then run: ollama pull llama3.2")
    
    # Create enhanced filler instance
    print("\n🛠️ Initializing Enhanced ApplicationFiller...")
    filler = ApplicationFiller(
        link=job_url,
        model="llama3.2",
        headless=False,          # Show browser for demo
        slow_mode=True,          # Enable slow mode for visual effects
        ollama_base_url="http://localhost:11434",
        resume_path=None,        # Set path to your resume if available
        reference_doc_path=None  # Set path to reference document if available
    )
    
    print("✅ ApplicationFiller initialized with enhanced features")
    
    # Test the form filling
    print("\n🔄 Starting form filling process...")
    try:
        result = filler.submit()
        
        if result == True:
            print("\n🎉 SUCCESS: Form was filled and submitted successfully!")
        elif isinstance(result, str):
            print(f"\n⚠️ PARTIAL SUCCESS: Form filled but needs manual completion")
            print(f"   Please visit: {result}")
        else:
            print("\n❌ FAILED: Could not complete the form")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
    finally:
        # Clean up
        print("\n🧹 Cleaning up...")
        filler.close_driver()
    
    print("\n✅ Test completed!")

def test_ollama_only():
    """Test just the Ollama LLM integration without browser automation"""
    
    print("🤖 Testing Ollama LLM Integration Only")
    print("=" * 50)
    
    # Create a minimal filler instance for testing Ollama
    filler = ApplicationFiller(
        link="",
        model="llama3.2",
        headless=True
    )
    
    # Test questions that should trigger Ollama
    test_questions = [
        "What interests you about this role?",
        "Why do you want to work at our company?", 
        "Describe your experience with machine learning",
        "What are your salary expectations?",
        "How many years of Python experience do you have?",
        "Are you willing to relocate?",
        "What is your availability to start?",
        "Do you have experience with cloud platforms?"
    ]
    
    print(f"\n🧪 Testing {len(test_questions)} sample questions...")
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{i}. Question: {question}")
        response = filler.query_ollama(question)
        print(f"   Response: {response if response else 'No response generated'}")
    
    print("\n✅ Ollama testing completed!")

def main():
    """Main function to run tests"""
    
    print("Enhanced ApplicationFiller Test Suite")
    print("=" * 40)
    
    # Ask user which test to run
    print("\nSelect test to run:")
    print("1. Full enhanced form filling test (with browser)")
    print("2. Ollama LLM integration test only")
    print("3. Both tests")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == "1":
        test_enhanced_features()
    elif choice == "2":
        test_ollama_only()
    elif choice == "3":
        test_ollama_only()
        print("\n" + "="*60)
        test_enhanced_features()
    else:
        print("Invalid choice. Running Ollama test only...")
        test_ollama_only()

if __name__ == "__main__":
    main()
