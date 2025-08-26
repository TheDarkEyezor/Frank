#!/usr/bin/env python3
"""
Comprehensive Trackr Application Runner
Run applications on all Trackr links with improved resume customization and robust error handling.
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

class ComprehensiveTrackrApplicationRunner:
    def __init__(self, headless=False, slow_mode=True):
        self.headless = headless
        self.slow_mode = slow_mode
        self.results = []
        self.open_tabs = []
        self.failed_urls = []
        self.problematic_urls = []
        self.successful_urls = []
        self.skipped_urls = []
        
        # Use EnhancedApplicationFiller if available
        try:
            self.ApplicationFillerClass = EnhancedApplicationFiller
        except NameError:
            self.ApplicationFillerClass = ApplicationFiller
        
        # Create results directory
        self.results_dir = "application_results"
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)
    
    def filter_and_validate_urls(self, links):
        """Filter and validate URLs, removing problematic ones"""
        filtered_links = []
        skipped_links = []
        
        for link in links:
            url = link['url']
            company = link['company']
            
            # Skip invalid URLs
            if not url or url == "data" or url.startswith("data:"):
                skipped_links.append({
                    'url': url,
                    'company': company,
                    'reason': 'Invalid URL format'
                })
                continue
            
            # Skip test sites
            if 'jobtestprep.co.uk' in url:
                skipped_links.append({
                    'url': url,
                    'company': company,
                    'reason': 'Test site - not real application'
                })
                continue
            
            # Skip problematic portals for now
            if any(domain in url for domain in ['tal.net', 'apptrkr.io']):
                skipped_links.append({
                    'url': url,
                    'company': company,
                    'reason': 'Complex portal - needs manual handling'
                })
                continue
            
            # Skip URLs that are just navigation pages
            if any(pattern in url.lower() for pattern in ['/careers', '/jobs', '/opportunities']):
                if not any(pattern in url.lower() for pattern in ['job', 'position', 'role', 'intern']):
                    skipped_links.append({
                        'url': url,
                        'company': company,
                        'reason': 'Navigation page - no specific job'
                    })
                    continue
            
            filtered_links.append(link)
        
        print(f"📊 Filtered {len(links)} links to {len(filtered_links)} processable links")
        print(f"⏭️ Skipped {len(skipped_links)} problematic links")
        
        # Save skipped links
        if skipped_links:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            skipped_file = os.path.join(self.results_dir, f"skipped_urls_{timestamp}.json")
            with open(skipped_file, 'w') as f:
                json.dump(skipped_links, f, indent=2)
            print(f"💾 Skipped URLs saved to: {skipped_file}")
        
        return filtered_links
    
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
    
    def get_customized_resume_path(self, job_type, company_name, job_title, url):
        """Get customized resume path with actual company and job data"""
        resume_paths = {
            "swe": "AdiPrabs_SWE.docx",
            "quant": "AdiPrabs_Quant.docx",
            "communication": "AdiPrabs_Cons.docx"
        }
        
        base_resume = resume_paths.get(job_type, "AdiPrabs_SWE.docx")
        
        # Check if customized version exists
        customized_folder = "customized_resumes"
        base_name = base_resume.replace('.docx', '')
        
        # Extract actual company and job from URL
        actual_company, actual_job_title = self.extract_company_and_job_from_url(url, company_name, job_title)
        
        if actual_company:
            safe_company_name = actual_company.replace(' ', '').replace('/', '_').replace('\\', '_')[:30]
            safe_job_title = actual_job_title.replace(' ', '').replace('/', '_').replace('\\', '_')[:30] if actual_job_title else ''
            
            if safe_job_title:
                customized_filename = f"{base_name}_{safe_company_name}_{safe_job_title}.docx"
            else:
                customized_filename = f"{base_name}_{safe_company_name}.docx"
            
            customized_path = os.path.join(customized_folder, customized_filename)
            
            if os.path.exists(customized_path):
                return customized_path
        
        return base_resume
    
    def extract_company_and_job_from_url(self, url, company_name, job_title):
        """Extract actual company name and job title from URL"""
        import re
        
        # Parse company name from URL or use provided company name
        actual_company = company_name
        
        # Extract company from common URL patterns
        if 'greenhouse.io' in url:
            match = re.search(r'greenhouse\.io/([^/]+)', url)
            if match:
                actual_company = match.group(1).replace('-', ' ').title()
        
        elif 'smartrecruiters.com' in url:
            match = re.search(r'smartrecruiters\.com/([^/]+)', url)
            if match:
                actual_company = match.group(1).replace('-', ' ').title()
        
        elif 'workdayjobs.com' in url:
            match = re.search(r'workdayjobs\.com/[^/]+/([^/]+)', url)
            if match:
                actual_company = match.group(1).replace('_', ' ').title()
        
        elif 'lever.co' in url:
            match = re.search(r'lever\.co/([^/?]+)', url)
            if match:
                actual_company = match.group(1).replace('-', ' ').title()
        
        elif 'jobs.' in url:
            match = re.search(r'jobs\.([^/]+)', url)
            if match:
                actual_company = match.group(1).replace('.com', '').replace('.co.uk', '').title()
        
        # Clean up company name
        actual_company = re.sub(r'[^\w\s]', '', actual_company).strip()
        
        # Extract job title from job_title or URL
        actual_job_title = job_title
        
        # Clean up job title
        if actual_job_title:
            actual_job_title = re.sub(r'\s*\([^)]*\)\s*', '', actual_job_title)
            actual_job_title = re.sub(r'\s*-\s*[^-]*$', '', actual_job_title)
            actual_job_title = actual_job_title.strip()
        
        return actual_company, actual_job_title
    
    def run_comprehensive_application(self, link_data):
        """Run application with comprehensive error handling"""
        url = link_data['url']
        company = link_data['company']
        job_title = link_data.get('text', '')
        
        print(f"\n🚀 Processing: {company}")
        print(f"🔗 URL: {url}")
        print(f"📋 Job: {job_title}")
        
        # Determine job type and resume
        job_type = self.determine_job_type(job_title, company)
        resume_path = self.get_customized_resume_path(job_type, company, job_title, url)
        
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
                # Failed - store URL for later analysis
                print(f"⚠️ Application failed - storing URL for analysis")
                self.failed_urls.append({
                    'url': url,
                    'company': company,
                    'job_title': job_title,
                    'reason': result,
                    'timestamp': datetime.now().isoformat()
                })
                
                # Keep browser open if driver is available
                if hasattr(filler, 'driver') and filler.driver:
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
                    'status': 'failed',
                    'reason': result
                }
            else:
                # Success
                print(f"✅ Application submitted successfully!")
                self.successful_urls.append({
                    'url': url,
                    'company': company,
                    'job_title': job_title,
                    'timestamp': datetime.now().isoformat()
                })
                if hasattr(filler, 'close_driver'):
                    filler.close_driver()
                return {
                    'url': url,
                    'company': company,
                    'status': 'success'
                }
                
        except Exception as e:
            print(f"❌ Error processing {company}: {e}")
            
            # Store problematic URL
            self.problematic_urls.append({
                'url': url,
                'company': company,
                'job_title': job_title,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            
            return {
                'url': url,
                'company': company,
                'status': 'error',
                'error': str(e)
            }
    
    def run_all_applications(self, max_applications=None):
        """Run applications for all Trackr links with comprehensive handling"""
        print("🚀 Starting Comprehensive Trackr Application Runner")
        print("=" * 60)
        
        # Load links
        links = self.load_trackr_links()
        if not links:
            print("❌ No links found")
            return
        
        # Filter and validate URLs
        filtered_links = self.filter_and_validate_urls(links)
        
        # Limit if specified
        if max_applications:
            filtered_links = filtered_links[:max_applications]
            print(f"📊 Processing first {len(filtered_links)} applications")
        
        print(f"🎯 Total applications to process: {len(filtered_links)}")
        
        # Process each application
        for i, link_data in enumerate(filtered_links, 1):
            print(f"\n{'='*60}")
            print(f"📋 Application {i}/{len(filtered_links)}")
            print(f"{'='*60}")
            
            try:
                result = self.run_comprehensive_application(link_data)
                self.results.append(result)
                
                # Save progress after each application
                self.save_progress()
                
            except KeyboardInterrupt:
                print(f"\n⚠️ Interrupted by user at application {i}")
                break
            except Exception as e:
                print(f"❌ Unexpected error at application {i}: {e}")
                # Continue with next application
                continue
            
            # Add delay between applications
            if i < len(filtered_links):
                print(f"⏳ Waiting 3 seconds before next application...")
                time.sleep(3)
        
        # Generate final report
        self.generate_final_report()
        
        # Handle open tabs
        if self.open_tabs:
            self.handle_open_tabs()
    
    def save_progress(self):
        """Save current progress to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save results
        results_file = os.path.join(self.results_dir, f"comprehensive_results_{timestamp}.json")
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # Save successful URLs
        if self.successful_urls:
            success_file = os.path.join(self.results_dir, f"successful_urls_{timestamp}.json")
            with open(success_file, 'w') as f:
                json.dump(self.successful_urls, f, indent=2)
        
        # Save failed URLs
        if self.failed_urls:
            failed_file = os.path.join(self.results_dir, f"failed_urls_{timestamp}.json")
            with open(failed_file, 'w') as f:
                json.dump(self.failed_urls, f, indent=2)
        
        # Save problematic URLs
        if self.problematic_urls:
            problematic_file = os.path.join(self.results_dir, f"problematic_urls_{timestamp}.json")
            with open(problematic_file, 'w') as f:
                json.dump(self.problematic_urls, f, indent=2)
    
    def generate_final_report(self):
        """Generate final application report"""
        print(f"\n{'='*60}")
        print("📊 COMPREHENSIVE APPLICATION RESULTS REPORT")
        print(f"{'='*60}")
        
        success_count = sum(1 for r in self.results if r['status'] == 'success')
        failed_count = sum(1 for r in self.results if r['status'] == 'failed')
        error_count = sum(1 for r in self.results if r['status'] == 'error')
        total_count = len(self.results)
        
        print(f"✅ Successful: {success_count}/{total_count}")
        print(f"⚠️ Failed (stored for analysis): {failed_count}/{total_count}")
        print(f"❌ Errors (stored for analysis): {error_count}/{total_count}")
        
        # Save comprehensive results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_results_file = os.path.join(self.results_dir, f"final_comprehensive_results_{timestamp}.json")
        
        with open(final_results_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_applications': total_count,
                'success_count': success_count,
                'failed_count': failed_count,
                'error_count': error_count,
                'results': self.results,
                'successful_urls': self.successful_urls,
                'failed_urls': self.failed_urls,
                'problematic_urls': self.problematic_urls
            }, f, indent=2)
        
        print(f"💾 Comprehensive results saved to: {final_results_file}")
        
        # Show successful applications
        if success_count > 0:
            print(f"\n✅ Successfully completed applications:")
            for result in self.results:
                if result['status'] == 'success':
                    print(f"   • {result['company']}")
        
        # Show failed applications
        if failed_count > 0:
            print(f"\n⚠️ Failed applications (stored for analysis):")
            for result in self.results:
                if result['status'] == 'failed':
                    print(f"   • {result['company']}: {result['reason']}")
        
        # Show problematic applications
        if error_count > 0:
            print(f"\n❌ Problematic applications (stored for analysis):")
            for result in self.results:
                if result['status'] == 'error':
                    print(f"   • {result['company']}: {result['error']}")
    
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
    print("🎯 Comprehensive Trackr Application Runner")
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
    runner = ComprehensiveTrackrApplicationRunner(
        headless=headless,
        slow_mode=True
    )
    
    # Run applications
    runner.run_all_applications(max_applications=max_apps)

if __name__ == "__main__":
    main()

