#!/usr/bin/env python3
"""
Fix Browser Driver Issues
Ensure Chrome/Firefox drivers work properly for the application filler.
"""

import os
import subprocess
import sys

def check_chrome_installation():
    """Check if Chrome is properly installed"""
    print("🔍 Checking Chrome installation...")
    
    # Check common Chrome locations on macOS
    chrome_paths = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/usr/bin/google-chrome",
        "/usr/bin/chromium-browser"
    ]
    
    for path in chrome_paths:
        if os.path.exists(path):
            print(f"✅ Chrome found at: {path}")
            return path
    
    print("❌ Chrome not found in common locations")
    return None

def install_chrome_driver():
    """Install/update ChromeDriver"""
    print("🔧 Installing/updating ChromeDriver...")
    
    try:
        # Install webdriver-manager if not already installed
        subprocess.run([sys.executable, "-m", "pip", "install", "webdriver-manager"], check=True)
        print("✅ webdriver-manager installed")
        
        # Test ChromeDriver installation
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--headless")  # Test in headless mode first
        
        # Install ChromeDriver
        driver_path = ChromeDriverManager().install()
        print(f"✅ ChromeDriver installed at: {driver_path}")
        
        # Test driver
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://www.google.com")
        print("✅ ChromeDriver test successful")
        driver.quit()
        
        return True
        
    except Exception as e:
        print(f"❌ ChromeDriver installation failed: {e}")
        return False

def fix_encoding_issues():
    """Fix encoding issues in profile and resume files"""
    print("🔧 Fixing encoding issues...")
    
    files_to_fix = [
        "Profile.txt",
        "AdiPrabs_SWE.docx",
        "AdiPrabs_Quant.docx", 
        "AdiPrabs_Cons.docx"
    ]
    
    for filename in files_to_fix:
        if os.path.exists(filename):
            print(f"📄 Processing: {filename}")
            
            if filename.endswith('.txt'):
                # Fix text file encoding
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Save with proper encoding
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"✅ Fixed encoding for {filename}")
                    
                except UnicodeDecodeError:
                    # Try different encodings
                    for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                        try:
                            with open(filename, 'r', encoding=encoding) as f:
                                content = f.read()
                            
                            with open(filename, 'w', encoding='utf-8') as f:
                                f.write(content)
                            print(f"✅ Fixed encoding for {filename} using {encoding}")
                            break
                        except:
                            continue
            else:
                print(f"⚠️ Skipping binary file: {filename}")

def create_enhanced_driver_setup():
    """Create enhanced driver setup with better error handling"""
    print("🔧 Creating enhanced driver setup...")
    
    enhanced_code = '''
def initialize_driver_enhanced(self):
    """Enhanced driver initialization with better error handling"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.service import Service
        import time
        
        print("🔧 Initializing enhanced Chrome driver...")
        
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--remote-debugging-port=9222")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        
        # Only add headless mode if requested
        if self.headless:
            chrome_options.add_argument("--headless")
            print("🔍 Running in headless mode")
        else:
            print("👁️ Running with visible browser window")
        
        # Try multiple ChromeDriver installation methods
        driver = None
        methods = [
            lambda: webdriver.Chrome(options=chrome_options),
            lambda: webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options),
            lambda: webdriver.Chrome(service=Service("/usr/local/bin/chromedriver"), options=chrome_options)
        ]
        
        for i, method in enumerate(methods, 1):
            try:
                print(f"🔄 Trying Chrome driver method {i}...")
                driver = method()
                print(f"✅ Chrome driver method {i} successful")
                break
            except Exception as e:
                print(f"❌ Chrome driver method {i} failed: {e}")
                if driver:
                    try:
                        driver.quit()
                    except:
                        pass
                driver = None
        
        if not driver:
            print("❌ All Chrome driver methods failed")
            return False
        
        # Test the driver
        try:
            driver.get("https://www.google.com")
            time.sleep(2)
            print("✅ Driver test successful")
            self.driver = driver
            return True
        except Exception as e:
            print(f"❌ Driver test failed: {e}")
            if driver:
                driver.quit()
            return False
            
    except Exception as e:
        print(f"❌ Enhanced driver initialization failed: {e}")
        return False
'''
    
    # Save the enhanced code
    with open("enhanced_driver_setup.py", "w") as f:
        f.write(enhanced_code)
    
    print("✅ Enhanced driver setup code saved to: enhanced_driver_setup.py")

def main():
    """Main function to fix all issues"""
    print("🔧 Fixing Browser Driver and Encoding Issues")
    print("=" * 50)
    
    # Check Chrome installation
    chrome_path = check_chrome_installation()
    if not chrome_path:
        print("⚠️ Chrome not found. Please install Google Chrome.")
        return False
    
    # Install ChromeDriver
    if not install_chrome_driver():
        print("⚠️ ChromeDriver installation failed.")
        return False
    
    # Fix encoding issues
    fix_encoding_issues()
    
    # Create enhanced driver setup
    create_enhanced_driver_setup()
    
    print("\n✅ All fixes completed!")
    print("🚀 Ready to run applications with enhanced driver setup")
    
    return True

if __name__ == "__main__":
    main()

