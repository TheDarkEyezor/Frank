#!/usr/bin/env python3
"""
Trackr Application Testing Script
Tests form filling functionality with all Trackr UK finance summer internship links.
"""

import sys
import os
import json
import time
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ApplicationFiller import ApplicationFiller

class TrackrApplicationTester:
    def __init__(self, headless=False, slow_mode=True, max_applications=None):
        self.headless = headless
        self.slow_mode = slow_mode
        self.max_applications = max_applications
        self.results = []
        
    def load_trackr_links(self, filename="trackr_links_clean.json"):
        """Load cleaned Trackr links"""
        try:
            with open(filename, 'r') as f:
                links = json.load(f)
            print(f"📋 Loaded {len(links)} Trackr application links")
            return links
        except FileNotFoundError:
            print(f"❌ No cleaned links found in {filename}")
            print("💡 Run clean_trackr_links.py first to generate cleaned links")
            return []
    
    def test_single_application(self, link_info):
        """Test form filling for a single application link"""
        url = link_info['url']
        company = link_info.get('company', 'Unknown Company')
        
        print(f"\n{'='*80}")
        print(f"🧪 Testing: {company}")
        print(f"🔗 URL: {url}")
        print(f"{'='*80}")
        
        try:
            # Determine job type for resume selection
            job_type = self._determine_job_type(company, url)
            resume_path = self._get_resume_path(job_type)
            
            print(f"📄 Using {job_type} resume: {resume_path}")
            
            # Create ApplicationFiller instance
            filler = ApplicationFiller(
                link=url,
                headless=self.headless,
                slow_mode=self.slow_mode,
                model="llama3.2",
                resume_path=resume_path,
                company_name=company,
                job_title=link_info.get('text', '')
            )
            
            # Attempt to submit the application
            result = filler.submit(multi_url_mode=True)
            
            # Check result
            if isinstance(result, str):
                # Partial success - form filled but submission failed
                status = "partial"
                message = f"Form filled but submission failed: {result}"
                print(f"⚠️ {message}")
            elif result:
                status = "success"
                message = "Application submitted successfully"
                print(f"✅ {message}")
            else:
                status = "error"
                message = "Application failed"
                print(f"❌ {message}")
            
            # Close driver
            filler.close_driver()
            
            return {
                'url': url,
                'company': company,
                'job_type': job_type,
                'status': status,
                'message': message,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error testing {company}: {str(e)}")
            return {
                'url': url,
                'company': company,
                'job_type': 'unknown',
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _determine_job_type(self, company, url):
        """Determine the appropriate job type for resume selection"""
        company_lower = company.lower()
        url_lower = url.lower()
        
        # Quant/Finance companies
        quant_keywords = ['quant', 'trading', 'hedge', 'investment', 'capital', 'asset', 'fund', 'deshaw', 'citadel', 'point72', 'virtu', 'jane street', 'jump trading', 'drw', 'gsa']
        if any(keyword in company_lower or keyword in url_lower for keyword in quant_keywords):
            return 'quant'
        
        # Communication/Marketing companies
        comm_keywords = ['marketing', 'communication', 'media', 'advertising', 'pr', 'public', 'sky', 'revolut']
        if any(keyword in company_lower or keyword in url_lower for keyword in comm_keywords):
            return 'communication'
        
        # Default to SWE for tech companies
        return 'swe'
    
    def _get_resume_path(self, job_type):
        """Get the appropriate resume path for the job type"""
        resume_paths = {
            'swe': "AdiPrabs_SWE.docx",
            'quant': "AdiPrabs_Quant.docx", 
            'communication': "AdiPrabs_Cons.docx"
        }
        
        resume_path = resume_paths.get(job_type, "AdiPrabs_SWE.docx")
        
        # Check if file exists
        if not os.path.exists(resume_path):
            print(f"⚠️ Resume file not found: {resume_path}, using default")
            return "AdiPrabs_SWE.docx"
        
        return resume_path
    
    def test_all_applications(self):
        """Test form filling for all Trackr application links"""
        print("🚀 Starting Trackr Application Testing")
        print(f"📊 Headless mode: {self.headless}")
        print(f"🐌 Slow mode: {self.slow_mode}")
        if self.max_applications:
            print(f"📝 Max applications: {self.max_applications}")
        
        # Load links
        links = self.load_trackr_links()
        
        if not links:
            print("❌ No links to test")
            return []
        
        # Limit number of applications if specified
        if self.max_applications:
            links = links[:self.max_applications]
            print(f"📝 Testing first {len(links)} applications")
        
        print(f"\n🎯 Testing {len(links)} applications...")
        
        # Test each application
        for i, link_info in enumerate(links, 1):
            print(f"\n📋 Progress: {i}/{len(links)}")
            
            result = self.test_single_application(link_info)
            self.results.append(result)
            
            # Add delay between applications
            if i < len(links):
                print("⏳ Waiting 15 seconds before next application...")
                time.sleep(15)
        
        # Generate report
        self.generate_report()
        
        return self.results
    
    def generate_report(self):
        """Generate a comprehensive test report"""
        if not self.results:
            print("❌ No results to report")
            return
        
        print(f"\n{'='*80}")
        print(f"📊 TRACKR APPLICATION TESTING REPORT")
        print(f"{'='*80}")
        
        # Count results by status
        success_count = sum(1 for r in self.results if r['status'] == 'success')
        partial_count = sum(1 for r in self.results if r['status'] == 'partial')
        error_count = sum(1 for r in self.results if r['status'] == 'error')
        
        print(f"✅ Successfully submitted: {success_count}/{len(self.results)}")
        print(f"⚠️ Partially completed: {partial_count}/{len(self.results)}")
        print(f"❌ Failed: {error_count}/{len(self.results)}")
        
        # Success rate
        success_rate = (success_count / len(self.results)) * 100
        print(f"📈 Success rate: {success_rate:.1f}%")
        
        # Results by job type
        job_type_results = {}
        for result in self.results:
            job_type = result.get('job_type', 'unknown')
            if job_type not in job_type_results:
                job_type_results[job_type] = {'success': 0, 'partial': 0, 'error': 0, 'total': 0}
            
            job_type_results[job_type][result['status']] += 1
            job_type_results[job_type]['total'] += 1
        
        print(f"\n📊 RESULTS BY JOB TYPE:")
        for job_type, counts in job_type_results.items():
            success_rate = (counts['success'] / counts['total']) * 100 if counts['total'] > 0 else 0
            print(f"   {job_type.upper()}: {counts['success']}/{counts['total']} ({success_rate:.1f}%)")
        
        # Detailed results
        print(f"\n📋 DETAILED RESULTS:")
        print(f"{'='*80}")
        
        for result in self.results:
            if result['status'] == 'success':
                status_icon = "✅"
            elif result['status'] == 'partial':
                status_icon = "⚠️"
            else:
                status_icon = "❌"
            
            print(f"{status_icon} {result['company']} ({result['job_type']})")
            print(f"   URL: {result['url']}")
            print(f"   Status: {result['status']}")
            print(f"   Message: {result['message']}")
            print()
        
        # Save results to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"trackr_test_results_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump({
                'test_info': {
                    'timestamp': datetime.now().isoformat(),
                    'headless': self.headless,
                    'slow_mode': self.slow_mode,
                    'total_applications': len(self.results)
                },
                'summary': {
                    'success_count': success_count,
                    'partial_count': partial_count,
                    'error_count': error_count,
                    'success_rate': success_rate,
                    'job_type_results': job_type_results
                },
                'results': self.results
            }, f, indent=2)
        
        print(f"💾 Detailed results saved to: {filename}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        print(f"{'='*80}")
        
        if error_count > 0:
            print(f"🔧 {error_count} applications failed - review error messages above")
        
        if partial_count > 0:
            print(f"📝 {partial_count} applications need manual completion")
        
        if success_count > 0:
            print(f"🎉 {success_count} applications were successfully submitted!")
        
        # Suggest improvements
        if success_rate < 50:
            print(f"⚠️ Low success rate ({success_rate:.1f}%) - consider:")
            print(f"   - Adding more website configurations")
            print(f"   - Improving form field detection")
            print(f"   - Adding company-specific handling")
        
        print(f"\n🎯 Next steps:")
        print(f"   1. Review failed applications manually")
        print(f"   2. Complete partial applications")
        print(f"   3. Add new website configurations as needed")

def main():
    """Main function to run the Trackr application testing"""
    print("🎯 Trackr Application Form Filler Testing")
    print("=" * 50)
    
    # Get user preferences
    headless = input("Run in headless mode? (y/n, default: n): ").lower().strip() == 'y'
    slow_mode = input("Run in slow mode? (y/n, default: y): ").lower().strip() != 'n'
    
    max_applications_input = input("Max number of applications to test (default: all): ").strip()
    max_applications = int(max_applications_input) if max_applications_input.isdigit() else None
    
    # Create tester
    tester = TrackrApplicationTester(
        headless=headless,
        slow_mode=slow_mode,
        max_applications=max_applications
    )
    
    # Run tests
    try:
        results = tester.test_all_applications()
        print(f"\n🎉 Testing completed! Check the report above for details.")
        
    except KeyboardInterrupt:
        print(f"\n⏹️ Testing interrupted by user")
        if tester.results:
            print(f"📊 Partial results available for {len(tester.results)} applications")
            tester.generate_report()
    
    except Exception as e:
        print(f"\n❌ Testing failed with error: {e}")
        if tester.results:
            print(f"📊 Partial results available for {len(tester.results)} applications")
            tester.generate_report()

if __name__ == "__main__":
    main()
