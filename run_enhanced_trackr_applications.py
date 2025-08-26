#!/usr/bin/env python3
"""
Run Enhanced Trackr Applications
Run the enhanced ApplicationFiller with all fixes on all Trackr links.
"""

import json
import time
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.append('.')

# Import the enhanced ApplicationFiller
try:
    from enhanced_application_filler import EnhancedApplicationFiller
    from ApplicationFiller import responses
    print("✅ Using Enhanced ApplicationFiller")
except ImportError:
    from ApplicationFiller import ApplicationFiller, responses
    print("⚠️ Using standard ApplicationFiller (enhanced version not available)")

class EnhancedTrackrApplicationRunner:
    def __init__(self, headless=False, slow_mode=True):
        self.headless = headless
        self.slow_mode = slow_mode
        self.results = []
        self.open_tabs = []
        
        # Use EnhancedApplicationFiller if available
        try:
            self.ApplicationFillerClass = EnhancedApplicationFiller
        except NameError:
            self.ApplicationFillerClass = ApplicationFiller
        
    def load_trackr_links(self):
        """Load all Trackr links from the JSON file"""
        try:
            with open("all_trackr_links.json", 'r') as f:
                data = json.load(f)
                links = data.get('links', [])
                print(f"📊 Loaded {len(links)} Trackr links")
                return links
        except Exception as e:
            print(f"❌ Error loading Trackr links: {e}")
            return []
    
    def determine_job_type(self, job_title, company_name):
        """Determine job type for resume selection"""
        text = f"{job_title} {company_name}".lower()
        
        # Quant keywords
        quant_keywords = ["quant", "quantitative", "trading", "trader", "portfolio", "risk", "investment", "hedge fund", "alpha", "signals"]
        if any(keyword in text for keyword in quant_keywords):
            return "quant"
        
        # Communication keywords
        comm_keywords = ["receptionist", "consulting", "consultant", "business", "marketing", "sales", "customer", "client", "communication"]
        if any(keyword in text for keyword in comm_keywords):
            return "communication"
        
        # Default to SWE
        return "swe"
    
    def get_resume_path(self, job_type):
        """Get the appropriate resume path based on job type"""
        resume_paths = {
            "swe": "AdiPrabs_SWE.docx",
            "quant": "AdiPrabs_Quant.docx",
            "communication": "AdiPrabs_Cons.docx"
        }
        return resume_paths.get(job_type, "AdiPrabs_SWE.docx")
    
    def get_customized_resume_path(self, job_type, company_name):
        """Get customized resume path if it exists, otherwise return original"""
        resume_paths = {
            "swe": "AdiPrabs_SWE.docx",
            "quant": "AdiPrabs_Quant.docx",
            "communication": "AdiPrabs_Cons.docx"
        }
        
        customized_folder = "customized_resumes"
        base_name = resume_paths.get(job_type, "AdiPrabs_SWE.docx").replace('.docx', '')
        safe_company_name = company_name.replace(' ', '').replace('/', '_').replace('\\', '_')
        customized_path = os.path.join(customized_folder, f"{base_name}_{safe_company_name}.docx")
        
        if os.path.exists(customized_path):
            return customized_path
        else:
            return resume_paths.get(job_type, "AdiPrabs_SWE.docx")
    
    def run_enhanced_application(self, link_data):
        """Run enhanced application with all fixes"""
        url = link_data['url']
        company = link_data['company']
        job_title = link_data.get('text', '')
        
        print(f"\n🚀 Processing: {company}")
        print(f"🔗 URL: {url}")
        print(f"📋 Job: {job_title}")
        
        # Determine job type and resume
        job_type = self.determine_job_type(job_title, company)
        resume_path = self.get_customized_resume_path(job_type, company)
        
        print(f"🎯 Job type: {job_type}, Resume: {resume_path}")
        
        try:
            # Create ApplicationFiller instance with enhanced features
            filler = self.ApplicationFillerClass(
                link=url,
                headless=self.headless,
                slow_mode=self.slow_mode,
                model="llama3.2",
                resume_path=resume_path,
                reference_doc_path="Profile.txt",
                company_name=company,
                job_title=job_title
            )
            
            # Run the application using enhanced submit method if available
            if hasattr(filler, 'submit_enhanced'):
                print("🎯 Using enhanced submit method")
                result = filler.submit_enhanced(multi_url_mode=True)
            else:
                print("⚠️ Using standard submit method")
                result = filler.submit(multi_url_mode=True)
            
            # Check result
            if isinstance(result, str):
                # Failed - keep browser open
                print(f"⚠️ Application failed - keeping browser open")
                self.open_tabs.append({
                    'url': url,
                    'company': company,
                    'job_title': job_title,
                    'driver': filler.driver,
                    'filler': filler,
                    'reason': result
                })
                return {
                    'url': url,
                    'company': company,
                    'status': 'partial',
                    'reason': result
                }
            else:
                # Success
                print(f"✅ Application submitted successfully!")
                filler.close_driver()
                return {
                    'url': url,
                    'company': company,
                    'status': 'success'
                }
                
        except Exception as e:
            print(f"❌ Error processing {company}: {e}")
            return {
                'url': url,
                'company': company,
                'status': 'error',
                'error': str(e)
            }
    
    def run_all_applications(self, max_applications=None):
        """Run applications for all Trackr links"""
        print("🚀 Starting Enhanced Trackr Application Runner")
        print("=" * 60)
        
        # Load links
        links = self.load_trackr_links()
        if not links:
            print("❌ No links found")
            return
        
        # Limit if specified
        if max_applications:
            links = links[:max_applications]
            print(f"📊 Processing first {len(links)} applications")
        
        print(f"🎯 Total applications to process: {len(links)}")
        
        # Process each application
        for i, link_data in enumerate(links, 1):
            print(f"\n{'='*60}")
            print(f"📋 Application {i}/{len(links)}")
            print(f"{'='*60}")
            
            result = self.run_enhanced_application(link_data)
            self.results.append(result)
            
            # Add delay between applications
            if i < len(links):
                print(f"⏳ Waiting 5 seconds before next application...")
                time.sleep(5)
        
        # Generate report
        self.generate_report()
        
        # Handle open tabs
        if self.open_tabs:
            self.handle_open_tabs()
    
    def generate_report(self):
        """Generate application report"""
        print(f"\n{'='*60}")
        print("📊 APPLICATION RESULTS REPORT")
        print(f"{'='*60}")
        
        success_count = sum(1 for r in self.results if r['status'] == 'success')
        partial_count = sum(1 for r in self.results if r['status'] == 'partial')
        error_count = sum(1 for r in self.results if r['status'] == 'error')
        total_count = len(self.results)
        
        print(f"✅ Successful: {success_count}/{total_count}")
        print(f"⚠️ Partial (manual completion needed): {partial_count}/{total_count}")
        print(f"❌ Failed: {error_count}/{total_count}")
        
        # Save detailed results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"enhanced_trackr_application_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_applications': total_count,
                'success_count': success_count,
                'partial_count': partial_count,
                'error_count': error_count,
                'results': self.results
            }, f, indent=2)
        
        print(f"💾 Detailed results saved to: {results_file}")
        
        # Show partial applications
        if partial_count > 0:
            print(f"\n⚠️ Applications requiring manual completion:")
            for result in self.results:
                if result['status'] == 'partial':
                    print(f"   • {result['company']}: {result['reason']}")
    
    def handle_open_tabs(self):
        """Handle open browser tabs for manual completion"""
        print(f"\n{'='*60}")
        print(f"🌐 {len(self.open_tabs)} BROWSER TABS REMAIN OPEN")
        print(f"{'='*60}")
        
        print("📋 Tabs open for manual completion:")
        for i, tab in enumerate(self.open_tabs, 1):
            print(f"   {i}. {tab['company']} - {tab['job_title']}")
            print(f"      URL: {tab['url']}")
            print(f"      Reason: {tab['reason']}")
        
        print(f"\n⏰ All tabs will remain open for manual completion.")
        print(f"   Complete the applications manually and close tabs when done.")
        print(f"   Press Ctrl+C to close all remaining tabs and exit.")
        
        # Keep script running so tabs stay open
        try:
            while self.open_tabs:
                time.sleep(10)
                # Check if any tabs were manually closed
                remaining_tabs = []
                for tab in self.open_tabs:
                    try:
                        # Test if driver is still active
                        tab['driver'].current_url
                        remaining_tabs.append(tab)
                    except:
                        # Tab was closed
                        print(f"✓ Tab closed for {tab['company']}")
                self.open_tabs = remaining_tabs
                
        except KeyboardInterrupt:
            print(f"\n👋 Closing all remaining tabs...")
            for tab in self.open_tabs:
                try:
                    tab['filler'].close_driver()
                except:
                    pass

def main():
    """Main function"""
    print("🎯 Enhanced Trackr Application Runner")
    print("=" * 50)
    
    # Check if we should run in headless mode
    headless = "--headless" in sys.argv
    if headless:
        print("🔍 Running in headless mode")
    else:
        print("👁️ Running with visible browser windows")
    
    # Check for max applications limit
    max_apps = None
    if "--max" in sys.argv:
        try:
            max_index = sys.argv.index("--max")
            if max_index + 1 < len(sys.argv):
                max_apps = int(sys.argv[max_index + 1])
        except:
            pass
    
    # Create runner
    runner = EnhancedTrackrApplicationRunner(
        headless=headless,
        slow_mode=True
    )
    
    # Run applications
    runner.run_all_applications(max_applications=max_apps)

if __name__ == "__main__":
    main()

