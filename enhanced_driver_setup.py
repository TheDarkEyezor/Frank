
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
