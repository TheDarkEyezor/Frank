#!/usr/bin/env python3
"""
Application Barrier Analysis
Analyzes common barriers that prevent automatic applications and provides insights for improvement.
"""

import json
from urllib.parse import urlparse
from datetime import datetime
import re

class ApplicationBarrierAnalyzer:
    def __init__(self):
        self.barriers_file = "application_barriers_analysis.json"
        self.all_links_file = "all_trackr_links.json"
        self.visited_websites_file = "visited_websites.json"
        
    def load_data(self):
        """Load all relevant data files"""
        data = {}
        
        # Load all Trackr links
        try:
            with open(self.all_links_file, 'r') as f:
                data['all_links'] = json.load(f)
        except FileNotFoundError:
            print(f"❌ {self.all_links_file} not found")
            data['all_links'] = None
        
        # Load barrier analysis
        try:
            with open(self.barriers_file, 'r') as f:
                data['barriers'] = json.load(f)
        except FileNotFoundError:
            print(f"❌ {self.barriers_file} not found")
            data['barriers'] = None
        
        # Load visited websites
        try:
            with open(self.visited_websites_file, 'r') as f:
                data['visited'] = json.load(f)
        except FileNotFoundError:
            print(f"❌ {self.visited_websites_file} not found")
            data['visited'] = None
        
        return data
    
    def analyze_barriers(self, links):
        """Analyze barriers for a list of links"""
        barriers = {
            'account_required': [],
            'external_portals': [],
            'test_required': [],
            'complex_forms': [],
            'manual_process': [],
            'unknown': []
        }
        
        for link in links:
            url = link['url']
            company = link['company']
            tracker = link.get('tracker', 'Unknown')
            
            barrier = self._identify_barrier(url, company, tracker)
            barriers[barrier].append(link)
        
        return barriers
    
    def _identify_barrier(self, url, company, tracker):
        """Identify what prevents automatic application for a given URL"""
        url_lower = url.lower()
        company_lower = company.lower()
        tracker_lower = tracker.lower()
        
        # Account creation required
        account_keywords = ['login', 'signin', 'register', 'account', 'profile', 'myworkday', 'taleo']
        if any(keyword in url_lower for keyword in account_keywords):
            return 'account_required'
        
        # External application portals
        portal_keywords = ['workday', 'greenhouse', 'lever', 'bamboohr', 'smartrecruiters', 'icims', 'taleo', 'successfactors', 'brassring']
        if any(keyword in url_lower for keyword in portal_keywords):
            return 'external_portals'
        
        # Test requirements
        test_keywords = ['test', 'assessment', 'hirevue', 'pymetrics', 'cut-e', 'cappfinity', 'jobtestprep']
        if any(keyword in url_lower for keyword in test_keywords):
            return 'test_required'
        
        # Complex forms (heuristic)
        if len(url) > 200 or ('?' in url and url.count('&') > 5):
            return 'complex_forms'
        
        # Manual process indicators
        manual_keywords = ['email', 'contact', 'phone', 'call', 'manual', 'apply@', 'careers@']
        if any(keyword in url_lower for keyword in manual_keywords):
            return 'manual_process'
        
        return 'unknown'
    
    def generate_detailed_analysis(self):
        """Generate detailed barrier analysis"""
        print("🔍 Generating Detailed Application Barrier Analysis")
        print("=" * 60)
        
        data = self.load_data()
        
        if not data['all_links']:
            print("❌ No Trackr links data found")
            return
        
        links = data['all_links']['links']
        print(f"📊 Analyzing {len(links)} application links...")
        
        # Analyze barriers
        barriers = self.analyze_barriers(links)
        
        # Print comprehensive analysis
        print(f"\n📊 APPLICATION BARRIER ANALYSIS")
        print(f"{'='*60}")
        
        total_links = len(links)
        
        for barrier_type, link_list in barriers.items():
            if link_list:
                percentage = (len(link_list) / total_links) * 100
                print(f"\n🔴 {barrier_type.upper().replace('_', ' ')}: {len(link_list)} applications ({percentage:.1f}%)")
                
                # Show examples
                for link in link_list[:3]:
                    print(f"   • {link['company']} - {link['url']}")
                    print(f"     Tracker: {link.get('tracker', 'Unknown')}")
                
                if len(link_list) > 3:
                    print(f"   ... and {len(link_list) - 3} more")
        
        # Analyze by tracker
        print(f"\n📊 BARRIERS BY TRACKER")
        print(f"{'='*60}")
        
        tracker_barriers = {}
        for link in links:
            tracker = link.get('tracker', 'Unknown')
            barrier = self._identify_barrier(link['url'], link['company'], tracker)
            
            if tracker not in tracker_barriers:
                tracker_barriers[tracker] = {}
            
            if barrier not in tracker_barriers[tracker]:
                tracker_barriers[tracker][barrier] = 0
            
            tracker_barriers[tracker][barrier] += 1
        
        for tracker, barrier_counts in tracker_barriers.items():
            total = sum(barrier_counts.values())
            print(f"\n📋 {tracker}: {total} applications")
            for barrier, count in barrier_counts.items():
                percentage = (count / total) * 100
                print(f"   • {barrier.replace('_', ' ')}: {count} ({percentage:.1f}%)")
        
        # Analyze by company type
        print(f"\n📊 BARRIERS BY COMPANY TYPE")
        print(f"{'='*60}")
        
        company_types = {
            'quant_trading': ['deshaw', 'citadel', 'point72', 'virtu', 'jane street', 'jump trading', 'drw', 'gsa'],
            'investment_banking': ['evercore', 'moelis', 'bnp', 'blackstone', 'goldman', 'morgan stanley'],
            'tech': ['google', 'apple', 'microsoft', 'amazon', 'meta', 'netflix'],
            'consulting': ['mckinsey', 'bain', 'bcg', 'deloitte', 'pwc', 'ey']
        }
        
        for company_type, keywords in company_types.items():
            matching_links = [link for link in links if any(keyword in link['company'].lower() for keyword in keywords)]
            
            if matching_links:
                print(f"\n🏢 {company_type.replace('_', ' ').title()}: {len(matching_links)} applications")
                type_barriers = self.analyze_barriers(matching_links)
                
                for barrier_type, link_list in type_barriers.items():
                    if link_list:
                        percentage = (len(link_list) / len(matching_links)) * 100
                        print(f"   • {barrier_type.replace('_', ' ')}: {len(link_list)} ({percentage:.1f}%)")
        
        # Generate recommendations
        self._generate_recommendations(barriers, links)
        
        # Save detailed analysis
        self._save_detailed_analysis(barriers, tracker_barriers, links)
    
    def _generate_recommendations(self, barriers, links):
        """Generate recommendations based on barrier analysis"""
        print(f"\n💡 RECOMMENDATIONS FOR IMPROVEMENT")
        print(f"{'='*60}")
        
        total_links = len(links)
        
        # Account required recommendations
        if barriers['account_required']:
            account_count = len(barriers['account_required'])
            account_percentage = (account_count / total_links) * 100
            print(f"\n🔐 ACCOUNT CREATION REQUIRED ({account_percentage:.1f}% of applications)")
            print("   Recommendations:")
            print("   • Implement account creation automation")
            print("   • Add support for common email providers")
            print("   • Create reusable account templates")
            print("   • Add account verification handling")
        
        # External portals recommendations
        if barriers['external_portals']:
            portal_count = len(barriers['external_portals'])
            portal_percentage = (portal_count / total_links) * 100
            print(f"\n🌐 EXTERNAL PORTALS ({portal_percentage:.1f}% of applications)")
            print("   Recommendations:")
            print("   • Add specific configurations for Workday, Greenhouse, Lever")
            print("   • Implement portal-specific form field mappings")
            print("   • Add support for multi-step application processes")
            print("   • Handle portal-specific validation rules")
        
        # Test requirements recommendations
        if barriers['test_required']:
            test_count = len(barriers['test_required'])
            test_percentage = (test_count / total_links) * 100
            print(f"\n🧪 TEST REQUIREMENTS ({test_percentage:.1f}% of applications)")
            print("   Recommendations:")
            print("   • Implement test scheduling automation")
            print("   • Add support for common test platforms (HireVue, Pymetrics)")
            print("   • Create test preparation strategies")
            print("   • Add test result tracking")
        
        # Complex forms recommendations
        if barriers['complex_forms']:
            complex_count = len(barriers['complex_forms'])
            complex_percentage = (complex_count / total_links) * 100
            print(f"\n📝 COMPLEX FORMS ({complex_percentage:.1f}% of applications)")
            print("   Recommendations:")
            print("   • Improve form field detection algorithms")
            print("   • Add support for dynamic form elements")
            print("   • Implement better error handling")
            print("   • Add form validation support")
        
        # Manual process recommendations
        if barriers['manual_process']:
            manual_count = len(barriers['manual_process'])
            manual_percentage = (manual_count / total_links) * 100
            print(f"\n📧 MANUAL PROCESSES ({manual_percentage:.1f}% of applications)")
            print("   Recommendations:")
            print("   • Implement email automation")
            print("   • Add cover letter generation")
            print("   • Create follow-up scheduling")
            print("   • Add application tracking")
        
        # Overall recommendations
        print(f"\n🎯 OVERALL STRATEGY")
        print("   • Focus on external portals first (highest impact)")
        print("   • Implement account creation for major platforms")
        print("   • Add company-specific configurations")
        print("   • Improve form detection for complex applications")
        print("   • Create manual process automation where possible")
    
    def _save_detailed_analysis(self, barriers, tracker_barriers, links):
        """Save detailed analysis to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"detailed_barrier_analysis_{timestamp}.json"
        
        analysis_data = {
            'analysis_date': datetime.now().isoformat(),
            'total_applications': len(links),
            'barriers': barriers,
            'tracker_barriers': tracker_barriers,
            'barrier_summary': {k: len(v) for k, v in barriers.items()},
            'recommendations': {
                'account_required': 'Implement account creation automation',
                'external_portals': 'Add portal-specific configurations',
                'test_required': 'Implement test scheduling automation',
                'complex_forms': 'Improve form field detection',
                'manual_process': 'Implement email automation',
                'unknown': 'Investigate further'
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(analysis_data, f, indent=2)
        
        print(f"\n💾 Detailed analysis saved to: {filename}")
    
    def show_visit_statistics(self):
        """Show visit tracking statistics"""
        try:
            with open(self.visited_websites_file, 'r') as f:
                visited_data = json.load(f)
            
            print(f"\n📊 VISIT TRACKING STATISTICS")
            print(f"{'='*60}")
            print(f"   Total applications attempted: {visited_data['total_applications']}")
            print(f"   Successful applications: {visited_data['successful_applications']}")
            print(f"   Failed applications: {visited_data['failed_applications']}")
            print(f"   Unique domains visited: {len(visited_data['visited_domains'])}")
            print(f"   Last updated: {visited_data['last_updated']}")
            
            if visited_data['total_applications'] > 0:
                success_rate = (visited_data['successful_applications'] / visited_data['total_applications']) * 100
                print(f"   Overall success rate: {success_rate:.1f}%")
        
        except FileNotFoundError:
            print("❌ No visit tracking data found")

def main():
    """Main function to run the barrier analysis"""
    print("🔍 Application Barrier Analysis")
    print("=" * 40)
    
    analyzer = ApplicationBarrierAnalyzer()
    
    # Generate detailed analysis
    analyzer.generate_detailed_analysis()
    
    # Show visit statistics
    analyzer.show_visit_statistics()
    
    print(f"\n🎉 Analysis completed!")

if __name__ == "__main__":
    main()

