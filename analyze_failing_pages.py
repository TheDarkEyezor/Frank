#!/usr/bin/env python3
"""
Analyze Failing Pages
Curls HTML content of failing application pages and analyzes structure to identify patterns.
"""

import requests
import json
import time
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
from datetime import datetime
import os

class FailingPageAnalyzer:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
    def analyze_failing_pages(self):
        """Analyze failing application pages to identify patterns"""
        print("🔍 Analyzing Failing Application Pages")
        print("=" * 60)
        
        # Load failing applications from previous test results
        failing_applications = self._get_failing_applications()
        
        if not failing_applications:
            print("❌ No failing applications found. Run tests first.")
            return
        
        print(f"📊 Found {len(failing_applications)} failing applications to analyze")
        
        analysis_results = []
        
        for i, app in enumerate(failing_applications, 1):
            print(f"\n📋 Analyzing {i}/{len(failing_applications)}: {app['company']}")
            print(f"🔗 URL: {app['url']}")
            
            try:
                # Curl the HTML content
                html_content = self._curl_page(app['url'])
                
                if html_content:
                    # Analyze the page structure
                    analysis = self._analyze_page_structure(html_content, app['url'], app['company'])
                    analysis['original_app'] = app
                    analysis_results.append(analysis)
                    
                    # Save individual analysis
                    self._save_individual_analysis(analysis)
                    
                    # Add delay between requests
                    time.sleep(2)
                else:
                    print(f"   ❌ Failed to curl page")
                    
            except Exception as e:
                print(f"   ❌ Error analyzing {app['company']}: {e}")
        
        # Generate comprehensive analysis
        self._generate_comprehensive_analysis(analysis_results)
        
        # Generate fixes
        self._generate_fixes(analysis_results)
    
    def _get_failing_applications(self):
        """Get failing applications from test results"""
        failing_apps = []
        
        # Sample failing applications from previous tests
        sample_failures = [
            {
                "url": "https://www.deshaw.com/careers/trader-analyst-intern-london-summer-2026-5465?utm_source=Trackr&utm_medium=tracker&utm_campaign=UK_Finance_2026",
                "company": "D.E. Shaw",
                "status": "partial",
                "message": "Form filled but submission failed"
            },
            {
                "url": "https://jobs.smartrecruiters.com/Wiser/744000076772605-advisory-summer-internship-2026-evercore?utm_source=Trackr&utm_medium=tracker&utm_campaign=UK_Finance_2026&trid=Trackr&dcr_ci=Trackr",
                "company": "Evercore",
                "status": "partial",
                "message": "Form filled but submission failed"
            },
            {
                "url": "https://moelis-careers.tal.net/vx/lang-en-GB/mobile-0/appcentre-1/brand-4/xf-b99e124a669c/candidate/so/pm/1/pl/2/opp/260-2026-Summer-Analyst-Investment-Banking-London/en-GB?utm_source=Trackr&utm_medium=tracker&utm_campaign=UK_Finance_2026",
                "company": "Moelis",
                "status": "success",
                "message": "Application submitted successfully"
            }
        ]
        
        # Add more from the barrier analysis
        try:
            with open("all_trackr_links.json", 'r') as f:
                data = json.load(f)
                links = data.get('links', [])
                
                # Add some external portal examples
                for link in links:
                    if any(keyword in link['url'].lower() for keyword in ['workday', 'greenhouse', 'lever', 'smartrecruiters']):
                        failing_apps.append({
                            "url": link['url'],
                            "company": link['company'],
                            "status": "unknown",
                            "message": "External portal - needs analysis"
                        })
                        if len(failing_apps) >= 10:  # Limit for analysis
                            break
        except:
            pass
        
        return sample_failures + failing_apps[:5]  # Combine with sample failures
    
    def _curl_page(self, url):
        """Curl the HTML content of a page"""
        try:
            print(f"   🌐 Curling page...")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            print(f"   ✅ Successfully curled page ({len(response.content)} bytes)")
            return response.text
            
        except Exception as e:
            print(f"   ❌ Failed to curl page: {e}")
            return None
    
    def _analyze_page_structure(self, html_content, url, company):
        """Analyze the structure of a page"""
        print(f"   📄 Analyzing page structure...")
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        analysis = {
            'url': url,
            'company': company,
            'analysis_date': datetime.now().isoformat(),
            'page_title': soup.title.string if soup.title else 'No title',
            'issues': [],
            'patterns': {},
            'recommendations': []
        }
        
        # Analyze page structure
        self._analyze_cookie_consent(soup, analysis)
        self._analyze_apply_buttons(soup, analysis)
        self._analyze_form_structure(soup, analysis)
        self._analyze_input_fields(soup, analysis)
        self._analyze_dynamic_content(soup, analysis)
        self._analyze_external_portals(soup, analysis)
        
        return analysis
    
    def _analyze_cookie_consent(self, soup, analysis):
        """Analyze cookie consent patterns"""
        print(f"     🍪 Analyzing cookie consent...")
        
        cookie_patterns = {
            'buttons': [],
            'text_patterns': [],
            'selectors': []
        }
        
        # Look for cookie-related buttons
        cookie_keywords = ['accept', 'agree', 'continue', 'ok', 'got it', 'i understand']
        
        buttons = soup.find_all('button')
        for button in buttons:
            button_text = button.get_text().lower()
            if any(keyword in button_text for keyword in cookie_keywords):
                cookie_patterns['buttons'].append({
                    'text': button.get_text().strip(),
                    'id': button.get('id', ''),
                    'class': button.get('class', []),
                    'selector': self._generate_selector(button)
                })
        
        # Look for cookie-related text
        page_text = soup.get_text().lower()
        if any(keyword in page_text for keyword in ['cookie', 'privacy', 'consent']):
            cookie_patterns['text_patterns'].append('Cookie consent detected')
        
        if cookie_patterns['buttons'] or cookie_patterns['text_patterns']:
            analysis['patterns']['cookie_consent'] = cookie_patterns
            analysis['issues'].append('Cookie consent required')
            analysis['recommendations'].append('Add cookie consent handling before form access')
    
    def _analyze_apply_buttons(self, soup, analysis):
        """Analyze apply button patterns"""
        print(f"     🎯 Analyzing apply buttons...")
        
        apply_patterns = {
            'buttons': [],
            'links': [],
            'text_patterns': []
        }
        
        # Look for apply buttons
        apply_keywords = ['apply', 'application', 'submit application', 'start application']
        
        buttons = soup.find_all('button')
        for button in buttons:
            button_text = button.get_text().lower()
            if any(keyword in button_text for keyword in apply_keywords):
                apply_patterns['buttons'].append({
                    'text': button.get_text().strip(),
                    'id': button.get('id', ''),
                    'class': button.get('class', []),
                    'selector': self._generate_selector(button)
                })
        
        # Look for apply links
        links = soup.find_all('a')
        for link in links:
            link_text = link.get_text().lower()
            if any(keyword in link_text for keyword in apply_keywords):
                apply_patterns['links'].append({
                    'text': link.get_text().strip(),
                    'href': link.get('href', ''),
                    'id': link.get('id', ''),
                    'class': link.get('class', []),
                    'selector': self._generate_selector(link)
                })
        
        if apply_patterns['buttons'] or apply_patterns['links']:
            analysis['patterns']['apply_buttons'] = apply_patterns
            analysis['issues'].append('Apply button required before form access')
            analysis['recommendations'].append('Click apply button before attempting form filling')
    
    def _analyze_form_structure(self, soup, analysis):
        """Analyze form structure"""
        print(f"     📝 Analyzing form structure...")
        
        forms = soup.find_all('form')
        form_patterns = {
            'forms': [],
            'form_count': len(forms),
            'has_forms': len(forms) > 0
        }
        
        for i, form in enumerate(forms):
            form_info = {
                'index': i,
                'action': form.get('action', ''),
                'method': form.get('method', ''),
                'id': form.get('id', ''),
                'class': form.get('class', []),
                'selector': self._generate_selector(form),
                'input_count': len(form.find_all('input')),
                'select_count': len(form.find_all('select')),
                'textarea_count': len(form.find_all('textarea'))
            }
            form_patterns['forms'].append(form_info)
        
        analysis['patterns']['form_structure'] = form_patterns
        
        if not form_patterns['has_forms']:
            analysis['issues'].append('No forms found on page')
            analysis['recommendations'].append('Form may be loaded dynamically or in iframe')
    
    def _analyze_input_fields(self, soup, analysis):
        """Analyze input field patterns"""
        print(f"     🔤 Analyzing input fields...")
        
        input_patterns = {
            'input_types': {},
            'field_mappings': {},
            'custom_fields': []
        }
        
        # Analyze all input fields
        inputs = soup.find_all('input')
        for input_field in inputs:
            input_type = input_field.get('type', 'text')
            input_name = input_field.get('name', '')
            input_id = input_field.get('id', '')
            input_placeholder = input_field.get('placeholder', '')
            
            # Count input types
            if input_type not in input_patterns['input_types']:
                input_patterns['input_types'][input_type] = 0
            input_patterns['input_types'][input_type] += 1
            
            # Try to map to our response fields
            field_mapping = self._map_input_to_response(input_name, input_id, input_placeholder)
            if field_mapping:
                input_patterns['field_mappings'][f"{input_name or input_id}"] = field_mapping
        
        # Analyze select fields
        selects = soup.find_all('select')
        for select in selects:
            select_name = select.get('name', '')
            select_id = select.get('id', '')
            options = [opt.get_text().strip() for opt in select.find_all('option')]
            
            field_mapping = self._map_select_to_response(select_name, select_id, options)
            if field_mapping:
                input_patterns['field_mappings'][f"{select_name or select_id}"] = field_mapping
        
        analysis['patterns']['input_fields'] = input_patterns
    
    def _analyze_dynamic_content(self, soup, analysis):
        """Analyze dynamic content patterns"""
        print(f"     ⚡ Analyzing dynamic content...")
        
        dynamic_patterns = {
            'javascript_files': [],
            'ajax_calls': [],
            'dynamic_selectors': []
        }
        
        # Look for JavaScript files
        scripts = soup.find_all('script', src=True)
        for script in scripts:
            src = script.get('src', '')
            if any(keyword in src.lower() for keyword in ['ajax', 'api', 'dynamic']):
                dynamic_patterns['javascript_files'].append(src)
        
        # Look for dynamic content indicators
        page_text = soup.get_text()
        if any(keyword in page_text.lower() for keyword in ['loading', 'please wait', 'fetching']):
            dynamic_patterns['dynamic_selectors'].append('Loading indicators found')
        
        if dynamic_patterns['javascript_files'] or dynamic_patterns['dynamic_selectors']:
            analysis['patterns']['dynamic_content'] = dynamic_patterns
            analysis['issues'].append('Dynamic content loading')
            analysis['recommendations'].append('Wait for dynamic content to load before form filling')
    
    def _analyze_external_portals(self, soup, analysis):
        """Analyze external portal patterns"""
        print(f"     🌐 Analyzing external portals...")
        
        portal_patterns = {
            'portal_type': None,
            'portal_indicators': []
        }
        
        # Check for external portal indicators
        page_text = soup.get_text().lower()
        current_url = analysis['url'].lower()
        
        if 'workday' in current_url:
            portal_patterns['portal_type'] = 'workday'
            portal_patterns['portal_indicators'].append('Workday portal detected')
        elif 'greenhouse' in current_url:
            portal_patterns['portal_type'] = 'greenhouse'
            portal_patterns['portal_indicators'].append('Greenhouse portal detected')
        elif 'lever' in current_url:
            portal_patterns['portal_type'] = 'lever'
            portal_patterns['portal_indicators'].append('Lever portal detected')
        elif 'smartrecruiters' in current_url:
            portal_patterns['portal_type'] = 'smartrecruiters'
            portal_patterns['portal_indicators'].append('SmartRecruiters portal detected')
        
        if portal_patterns['portal_type']:
            analysis['patterns']['external_portal'] = portal_patterns
            analysis['issues'].append(f'External portal: {portal_patterns["portal_type"]}')
            analysis['recommendations'].append(f'Add specific handling for {portal_patterns["portal_type"]} portal')
    
    def _map_input_to_response(self, name, id, placeholder):
        """Map input field to our response data"""
        field_text = f"{name} {id} {placeholder}".lower()
        
        # Common field mappings
        mappings = {
            'first name': 'first name',
            'firstname': 'first name',
            'fname': 'first name',
            'given name': 'first name',
            
            'last name': 'last name',
            'lastname': 'last name',
            'lname': 'last name',
            'surname': 'last name',
            'family name': 'last name',
            
            'full name': 'full name',
            'name': 'full name',
            
            'email': 'email',
            'email address': 'email',
            'e-mail': 'email',
            
            'phone': 'phone',
            'telephone': 'phone',
            'mobile': 'phone',
            'cell': 'phone',
            
            'university': 'university',
            'college': 'university',
            'school': 'university',
            'institution': 'university',
            
            'degree': 'degree',
            'qualification': 'degree',
            'education': 'degree',
            
            'major': 'major',
            'field of study': 'major',
            'subject': 'major',
            
            'graduation year': 'graduation year',
            'grad year': 'graduation year',
            'year of graduation': 'graduation year',
            
            'gpa': 'gpa',
            'grade point average': 'gpa',
            'grade': 'gpa',
            
            'linkedin': 'linkedin',
            'linkedin profile': 'linkedin',
            'linkedin url': 'linkedin',
            
            'github': 'github',
            'github profile': 'github',
            'github url': 'github',
            
            'city': 'city',
            'location': 'city',
            
            'country': 'country',
            'nation': 'country',
            
            'sponsorship': 'united kingdom need sponsorship',
            'work authorization': 'united kingdom need sponsorship',
            'visa': 'united kingdom need sponsorship'
        }
        
        for pattern, response_field in mappings.items():
            if pattern in field_text:
                return response_field
        
        return None
    
    def _map_select_to_response(self, name, id, options):
        """Map select field to our response data"""
        field_text = f"{name} {id}".lower()
        
        # Common select field mappings
        mappings = {
            'country': 'country',
            'nation': 'country',
            'location': 'country',
            
            'degree': 'degree',
            'education': 'degree',
            'qualification': 'degree',
            
            'major': 'major',
            'field': 'major',
            'subject': 'major',
            
            'graduation year': 'graduation year',
            'grad year': 'graduation year',
            'year': 'graduation year',
            
            'sponsorship': 'united kingdom need sponsorship',
            'work authorization': 'united kingdom need sponsorship',
            'visa': 'united kingdom need sponsorship'
        }
        
        for pattern, response_field in mappings.items():
            if pattern in field_text:
                return response_field
        
        return None
    
    def _generate_selector(self, element):
        """Generate a CSS selector for an element"""
        selectors = []
        
        if element.get('id'):
            selectors.append(f"#{element['id']}")
        
        if element.get('class'):
            classes = ' '.join(element['class'])
            selectors.append(f".{classes}")
        
        if element.name:
            selectors.append(element.name)
        
        return ' '.join(selectors) if selectors else None
    
    def _save_individual_analysis(self, analysis):
        """Save individual page analysis"""
        filename = f"page_analysis_{analysis['company'].replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(analysis, f, indent=2)
        
        print(f"     💾 Saved analysis to {filename}")
    
    def _generate_comprehensive_analysis(self, analysis_results):
        """Generate comprehensive analysis report"""
        print(f"\n📊 Generating comprehensive analysis...")
        
        comprehensive_analysis = {
            'analysis_date': datetime.now().isoformat(),
            'total_pages_analyzed': len(analysis_results),
            'common_issues': {},
            'common_patterns': {},
            'recommendations': []
        }
        
        # Aggregate common issues
        for analysis in analysis_results:
            for issue in analysis.get('issues', []):
                if issue not in comprehensive_analysis['common_issues']:
                    comprehensive_analysis['common_issues'][issue] = 0
                comprehensive_analysis['common_issues'][issue] += 1
        
        # Aggregate common patterns
        for analysis in analysis_results:
            for pattern_type, pattern_data in analysis.get('patterns', {}).items():
                if pattern_type not in comprehensive_analysis['common_patterns']:
                    comprehensive_analysis['common_patterns'][pattern_type] = []
                comprehensive_analysis['common_patterns'][pattern_type].append(pattern_data)
        
        # Generate recommendations
        all_recommendations = []
        for analysis in analysis_results:
            all_recommendations.extend(analysis.get('recommendations', []))
        
        # Count and deduplicate recommendations
        recommendation_counts = {}
        for rec in all_recommendations:
            if rec not in recommendation_counts:
                recommendation_counts[rec] = 0
            recommendation_counts[rec] += 1
        
        comprehensive_analysis['recommendations'] = [
            {'recommendation': rec, 'frequency': count}
            for rec, count in sorted(recommendation_counts.items(), key=lambda x: x[1], reverse=True)
        ]
        
        # Save comprehensive analysis
        filename = f"comprehensive_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(comprehensive_analysis, f, indent=2)
        
        print(f"💾 Saved comprehensive analysis to {filename}")
        
        # Print summary
        print(f"\n📊 ANALYSIS SUMMARY:")
        print(f"   Pages analyzed: {comprehensive_analysis['total_pages_analyzed']}")
        print(f"   Common issues: {len(comprehensive_analysis['common_issues'])}")
        print(f"   Common patterns: {len(comprehensive_analysis['common_patterns'])}")
        print(f"   Recommendations: {len(comprehensive_analysis['recommendations'])}")
        
        print(f"\n🔴 TOP ISSUES:")
        for issue, count in sorted(comprehensive_analysis['common_issues'].items(), key=lambda x: x[1], reverse=True):
            print(f"   • {issue}: {count} pages")
        
        print(f"\n💡 TOP RECOMMENDATIONS:")
        for rec in comprehensive_analysis['recommendations'][:5]:
            print(f"   • {rec['recommendation']} (frequency: {rec['frequency']})")
    
    def _generate_fixes(self, analysis_results):
        """Generate fixes for the ApplicationFiller"""
        print(f"\n🔧 Generating fixes for ApplicationFiller...")
        
        fixes = {
            'cookie_handling': [],
            'apply_button_handling': [],
            'field_mappings': {},
            'portal_configurations': {},
            'dynamic_content_handling': []
        }
        
        # Extract cookie handling patterns
        for analysis in analysis_results:
            if 'cookie_consent' in analysis.get('patterns', {}):
                cookie_data = analysis['patterns']['cookie_consent']
                for button in cookie_data.get('buttons', []):
                    fixes['cookie_handling'].append({
                        'company': analysis['company'],
                        'selector': button['selector'],
                        'text': button['text']
                    })
        
        # Extract apply button patterns
        for analysis in analysis_results:
            if 'apply_buttons' in analysis.get('patterns', {}):
                apply_data = analysis['patterns']['apply_buttons']
                for button in apply_data.get('buttons', []):
                    fixes['apply_button_handling'].append({
                        'company': analysis['company'],
                        'selector': button['selector'],
                        'text': button['text']
                    })
        
        # Extract field mappings
        for analysis in analysis_results:
            if 'input_fields' in analysis.get('patterns', {}):
                field_data = analysis['patterns']['input_fields']
                company = analysis['company']
                if company not in fixes['field_mappings']:
                    fixes['field_mappings'][company] = {}
                fixes['field_mappings'][company].update(field_data.get('field_mappings', {}))
        
        # Extract portal configurations
        for analysis in analysis_results:
            if 'external_portal' in analysis.get('patterns', {}):
                portal_data = analysis['patterns']['external_portal']
                portal_type = portal_data.get('portal_type')
                if portal_type:
                    fixes['portal_configurations'][analysis['company']] = portal_type
        
        # Save fixes
        filename = f"application_filler_fixes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(fixes, f, indent=2)
        
        print(f"💾 Saved fixes to {filename}")
        
        # Print fix summary
        print(f"\n🔧 FIXES SUMMARY:")
        print(f"   Cookie handling patterns: {len(fixes['cookie_handling'])}")
        print(f"   Apply button patterns: {len(fixes['apply_button_handling'])}")
        print(f"   Field mappings: {len(fixes['field_mappings'])} companies")
        print(f"   Portal configurations: {len(fixes['portal_configurations'])}")
        
        print(f"\n📝 NEXT STEPS:")
        print(f"   1. Review the generated fixes")
        print(f"   2. Update ApplicationFiller.py with new patterns")
        print(f"   3. Add cookie consent handling")
        print(f"   4. Add apply button detection and clicking")
        print(f"   5. Add dynamic content waiting")
        print(f"   6. Add portal-specific configurations")

def main():
    """Main function to analyze failing pages"""
    print("🔍 Failing Page Analyzer")
    print("=" * 40)
    
    analyzer = FailingPageAnalyzer()
    analyzer.analyze_failing_pages()
    
    print(f"\n🎉 Analysis completed!")

if __name__ == "__main__":
    main()

