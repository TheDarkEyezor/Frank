#!/usr/bin/env python3
"""
Setup script for enhanced ApplicationFiller with Ollama integration
"""

import os
import subprocess
import sys
import requests
import time

def check_ollama_installed():
    """Check if Ollama is installed"""
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Ollama is installed: {result.stdout.strip()}")
            return True
        else:
            print("❌ Ollama is not installed")
            return False
    except FileNotFoundError:
        print("❌ Ollama is not installed")
        return False

def install_ollama():
    """Install Ollama using the official installer"""
    print("📦 Installing Ollama...")
    
    try:
        # Download and run the Ollama installer
        install_command = "curl -fsSL https://ollama.ai/install.sh | sh"
        result = subprocess.run(install_command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Ollama installed successfully")
            return True
        else:
            print(f"❌ Failed to install Ollama: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error installing Ollama: {e}")
        return False

def start_ollama_service():
    """Start the Ollama service"""
    print("🚀 Starting Ollama service...")
    
    try:
        # Start Ollama in the background
        subprocess.Popen(['ollama', 'serve'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait a moment for the service to start
        time.sleep(3)
        
        # Check if the service is running
        response = requests.get("http://localhost:11434/api/version", timeout=10)
        if response.status_code == 200:
            print("✅ Ollama service is running")
            return True
        else:
            print("❌ Ollama service failed to start properly")
            return False
            
    except Exception as e:
        print(f"❌ Error starting Ollama service: {e}")
        return False

def pull_ollama_model(model_name="llama3.2"):
    """Pull the specified Ollama model"""
    print(f"📥 Pulling Ollama model: {model_name}")
    
    try:
        result = subprocess.run(['ollama', 'pull', model_name], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Model {model_name} pulled successfully")
            return True
        else:
            print(f"❌ Failed to pull model {model_name}: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error pulling model: {e}")
        return False

def check_python_packages():
    """Check and install required Python packages"""
    print("📋 Checking Python packages...")
    
    required_packages = [
        'selenium',
        'webdriver-manager',
        'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing_packages, check=True)
            print("✅ All packages installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install packages: {e}")
            return False
    
    return True

def test_ollama_connection():
    """Test the connection to Ollama"""
    print("🔍 Testing Ollama connection...")
    
    try:
        # Test basic API connection
        response = requests.get("http://localhost:11434/api/version", timeout=5)
        if response.status_code == 200:
            version_info = response.json()
            print(f"✅ Ollama API is accessible - Version: {version_info.get('version', 'unknown')}")
            
            # Test a simple generation
            print("🧪 Testing model generation...")
            test_payload = {
                "model": "llama3.2",
                "prompt": "Hello, respond with just 'Hello world!'",
                "stream": False
            }
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json=test_payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get("response", "").strip()
                print(f"✅ Model generation test successful: {generated_text}")
                return True
            else:
                print(f"❌ Model generation test failed: {response.status_code}")
                return False
        else:
            print(f"❌ Ollama API not accessible: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Ollama. Make sure it's running with: ollama serve")
        return False
    except Exception as e:
        print(f"❌ Error testing Ollama: {e}")
        return False

def create_sample_files():
    """Create sample resume and reference document files"""
    print("📄 Creating sample files...")
    
    # Sample resume content
    resume_content = """Aditya Prabakaran
Software Engineer

Email: aditya.prabakaran@gmail.com
Phone: +447587460771
Location: London, UK
LinkedIn: https://www.linkedin.com/in/adiprabs
GitHub: https://github.com/TheDarkEyezor
Portfolio: https://adiprabs.vercel.app/

EDUCATION
Imperial College London
MEng Computer Science
2020 - 2024

EXPERIENCE
- Full-stack development with Python, JavaScript, React
- Machine learning and data science projects
- Cloud platforms (AWS, GCP)
- DevOps and automation tools

SKILLS
- Programming: Python, JavaScript, TypeScript, Java, C++
- Web Development: React, Node.js, Express, FastAPI
- Databases: PostgreSQL, MongoDB, Redis
- Cloud: AWS, GCP, Docker, Kubernetes
- ML/AI: TensorFlow, PyTorch, scikit-learn
"""
    
    # Sample reference document
    reference_content = """Professional Reference Document - Aditya Prabakaran

CAREER OBJECTIVES
Seeking challenging software engineering roles in fintech, AI/ML, or cloud infrastructure
Interested in full-stack development, systems architecture, and machine learning applications

TECHNICAL EXPERTISE
- 4+ years experience with Python development
- Strong background in web development with modern frameworks
- Experience with cloud-native applications and microservices
- Familiar with financial systems and trading applications
- Active in open-source projects and technical communities

PREFERENCES
- Work Authorization: UK citizen, requires US sponsorship
- Relocation: Open to relocation for the right opportunity
- Start Date: Available immediately or with 2 weeks notice
- Salary Range: Competitive market rates based on role and location

ADDITIONAL CONTEXT
- Graduated with honors from Imperial College London
- Strong problem-solving and analytical skills
- Experience working in agile development environments
- Passionate about emerging technologies and continuous learning
"""
    
    try:
        # Create sample resume file
        with open("sample_resume.txt", "w") as f:
            f.write(resume_content)
        print("✅ Created sample_resume.txt")
        
        # Create sample reference document
        with open("reference_document.txt", "w") as f:
            f.write(reference_content)
        print("✅ Created reference_document.txt")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating sample files: {e}")
        return False

def main():
    """Main setup function"""
    print("Enhanced ApplicationFiller Setup Script")
    print("=" * 45)
    print("This script will set up Ollama LLM integration for the ApplicationFiller")
    
    success = True
    
    # Step 1: Check and install Python packages
    print("\n1️⃣ Checking Python packages...")
    if not check_python_packages():
        success = False
    
    # Step 2: Check and install Ollama
    print("\n2️⃣ Checking Ollama installation...")
    if not check_ollama_installed():
        print("   Ollama needs to be installed. Install manually with:")
        print("   curl -fsSL https://ollama.ai/install.sh | sh")
        print("   Or visit: https://ollama.ai/download")
        success = False
    
    # Step 3: Start Ollama service
    print("\n3️⃣ Starting Ollama service...")
    if not start_ollama_service():
        print("   Try manually: ollama serve")
        success = False
    
    # Step 4: Pull model
    print("\n4️⃣ Pulling Ollama model...")
    if not pull_ollama_model("llama3.2"):
        print("   Try manually: ollama pull llama3.2")
        success = False
    
    # Step 5: Test connection
    print("\n5️⃣ Testing Ollama connection...")
    if not test_ollama_connection():
        success = False
    
    # Step 6: Create sample files
    print("\n6️⃣ Creating sample files...")
    create_sample_files()
    
    # Summary
    print("\n" + "=" * 45)
    if success:
        print("🎉 Setup completed successfully!")
        print("\nNext steps:")
        print("1. Run the test script: python test_enhanced.py")
        print("2. Customize the resume path and reference document in your code")
        print("3. Update the responses dictionary with your information")
    else:
        print("⚠️ Setup completed with some issues")
        print("Please resolve the issues above before running the enhanced features")
    
    print("\nUseful commands:")
    print("- Start Ollama: ollama serve")
    print("- Pull models: ollama pull llama3.2")
    print("- List models: ollama list")
    print("- Test ApplicationFiller: python test_enhanced.py")

if __name__ == "__main__":
    main()
