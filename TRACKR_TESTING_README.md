# Trackr Application Form Filler Testing

This system allows you to test your automated form filling functionality with all the UK finance summer internship applications listed on Trackr.

## Overview

The system consists of several components:

1. **Trackr Scraper** - Extracts application links from the Trackr website
2. **Link Cleaner** - Filters and cleans the extracted links
3. **Application Tester** - Tests form filling with all the links
4. **Sample Tester** - Tests with a small sample for verification

## Quick Start

### 1. Scrape Trackr Links

First, extract all application links from Trackr:

```bash
python trackr_scraper_enhanced.py
```

This will:
- Navigate to the Trackr UK finance summer internships page
- Extract all application links using Selenium
- Save the links to `trackr_links_enhanced.json`

### 2. Clean the Links

Filter out test prep sites and duplicates:

```bash
python clean_trackr_links.py
```

This will:
- Remove test prep sites (jobtestprep.co.uk)
- Remove internal Trackr links
- Remove duplicates
- Save cleaned links to `trackr_links_clean.json`

### 3. Test Sample Applications

Test with a small sample first to verify everything works:

```bash
python test_trackr_sample.py
```

This will test the first 3 applications to ensure your form filler works correctly.

### 4. Test All Applications

Once you're satisfied with the sample test, run the full test:

```bash
python test_trackr_applications.py
```

This will:
- Test all 47+ applications
- Generate detailed reports
- Save results to timestamped JSON files

## Configuration Options

### Test Settings

When running the full test, you can configure:

- **Headless mode**: Run without visible browser (faster but no visual feedback)
- **Slow mode**: Add delays for better visualization
- **Max applications**: Limit the number of applications to test

### Resume Selection

The system automatically selects the appropriate resume based on the company:

- **Quant resume**: For trading, hedge fund, and quantitative companies
- **SWE resume**: For software engineering and tech companies  
- **Communication resume**: For marketing, media, and communication companies

## File Structure

```
Frank/
├── trackr_scraper_enhanced.py      # Enhanced scraper with Selenium
├── clean_trackr_links.py           # Link filtering and cleaning
├── test_trackr_sample.py           # Sample testing (3 applications)
├── test_trackr_applications.py     # Full testing (all applications)
├── trackr_links_enhanced.json      # Raw scraped links
├── trackr_links_clean.json         # Cleaned and filtered links
└── trackr_test_results_*.json      # Test results (timestamped)
```

## Sample Companies Tested

The system will test applications from companies like:

- **Quant/Trading**: D.E. Shaw, Citadel, Point72, Virtu, Jane Street, Jump Trading
- **Investment Banking**: Evercore, Moelis, BNP Paribas, Blackstone
- **Asset Management**: BlackRock, MLP, Capula Investment Management
- **Tech/Finance**: Apple, Revolut, Sky

## Test Results

The system generates comprehensive reports including:

- **Success rate**: Percentage of successfully submitted applications
- **Results by job type**: Breakdown by quant/SWE/communication roles
- **Detailed results**: Status and error messages for each application
- **Recommendations**: Suggestions for improving success rate

### Result Categories

- **✅ Success**: Application submitted successfully
- **⚠️ Partial**: Form filled but submission failed (needs manual completion)
- **❌ Error**: Application failed completely

## Troubleshooting

### Common Issues

1. **No links found**: The Trackr website structure may have changed
2. **Low success rate**: Add more website configurations to ApplicationFiller
3. **Browser errors**: Ensure Chrome/ChromeDriver is installed
4. **Resume file missing**: Check that all resume files exist

### Improving Success Rate

To improve the success rate:

1. **Add website configurations**: Update the `website_configs` in ApplicationFiller.py
2. **Improve form detection**: Enhance field detection algorithms
3. **Add company-specific handling**: Create custom handlers for specific companies
4. **Update resume files**: Ensure resumes are current and relevant

## Dependencies

Make sure you have the required dependencies:

```bash
pip install beautifulsoup4 requests selenium
```

Also ensure you have:
- Chrome browser installed
- ChromeDriver installed and in PATH
- All resume files (AdiPrabs_SWE.docx, AdiPrabs_Quant.docx, AdiPrabs_Cons.docx)

## Usage Examples

### Test Just Quant Companies

```python
# Modify test_trackr_applications.py to filter for quant companies
quant_links = [link for link in links if 'quant' in link['company'].lower()]
```

### Test Specific Companies

```python
# Test only specific companies
target_companies = ['Citadel', 'Point72', 'Jane Street']
filtered_links = [link for link in links if any(company in link['company'] for company in target_companies)]
```

### Run in Headless Mode

```bash
# For faster testing without visual feedback
python test_trackr_applications.py
# Answer 'y' to headless mode
```

## Monitoring and Logging

The system provides detailed logging:

- Real-time progress updates
- Error messages and stack traces
- Success/failure statistics
- Detailed JSON reports

Check the generated JSON files for complete test results and analysis.

## Next Steps

After running the tests:

1. **Review failed applications**: Check error messages and fix issues
2. **Complete partial applications**: Manually finish applications that were partially filled
3. **Update configurations**: Add new website configurations based on failures
4. **Improve resumes**: Update resume files based on application requirements
5. **Re-run tests**: Test again after making improvements

This system provides a comprehensive way to ensure your form filling functionality works with all the major UK finance summer internship applications available on Trackr.

