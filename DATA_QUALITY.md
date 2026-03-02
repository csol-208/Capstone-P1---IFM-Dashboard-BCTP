# Data Quality Documentation

## Overview
This document details the data quality findings from the Voluntary Carbon Offsets Database analysis and the validation checks implemented in the application.

## Key Findings

### Overall Dataset Statistics
- **Total Records**: 10,975 projects
- **Total Columns**: 168 data fields
- **Unique Registries**: 5 (ACR, CAR, GS, VCS, Verra)
- **Unique Countries**: 147
- **Project Types**: 82 different types
- **Status Categories**: 25

### Credits Overview
- **Total Credits Issued**: 2,554,813,143
- **Total Credits Retired**: 1,462,296,090
- **Total Credits Remaining**: 1,092,517,053

---

## Data Quality Issues Identified

### ⚠️ Issue 1: Negative Remaining Credits (15 projects)

**Severity**: WARNING  
**Count**: 15 projects  
**Impact**: Medium - Affects less than 0.14% of dataset

#### What This Means
15 projects have more credits retired than issued, resulting in negative remaining credits. This violates the logical constraint that remaining = issued - retired should be ≥ 0.

#### Affected Projects
1. **ACR212** - UPM Blandin Native American Hardwoods: Issued 1,387,888 | Retired 1,531,480 | Remaining: -143,592
2. **ACR272** - Bear Creek Watershed: Issued 375,650 | Retired 411,399 | Remaining: -35,749
3. **ACR420** - Finite Carbon Sealaska 2: Issued 2,153,385 | Retired 2,333,929 | Remaining: -180,544
4. **ACR425** - Bluesource Goldbelt: Issued 394,194 | Retired 425,491 | Remaining: -31,297
5. **CAR660** - Gualala River Forest: Issued 487,865 | Retired 537,344 | Remaining: -49,479
6. **CAR1013** - Buckeye Forest Project: Issued 913,550 | Retired 942,018 | Remaining: -28,468
7. **CAR1035** - Scenic View Dairy: Issued 161,083 | Retired 179,950 | Remaining: -18,867
8. **CAR1123** - Central Sands Dairy: Issued 74,829 | Retired 78,839 | Remaining: -4,010
9. **GS440** - Mamak Landfill, Turkey: Issued 3,192,403 | Retired 3,192,998 | Remaining: -595
10. **GS2913** - BaumInvest Reforestation: Issued 48,801 | Retired 161,551 | Remaining: -112,750
11. **GS2951** - ArBolivia Phase II: Issued 133,691 | Retired 215,438 | Remaining: -81,747
12. **GS3007** - Sodo Ethiopia: Issued 116,275 | Retired 153,176 | Remaining: -36,901
13. **GS3039** - Australian Yarra Yarra: Issued 175,837 | Retired 193,202 | Remaining: -17,365
14. **VCS67** - Ratchaburi Farms Biogas: Issued 32,969 | Retired 33,353 | Remaining: -384
15. **VCS144** - Gunung Salak Geothermal, Indonesia: Issued 1,499,246 | Retired 1,594,793 | Remaining: -95,547

#### Possible Causes
1. **Credits from other sources**: Credits may have been issued through mechanisms not captured in this column
2. **Data entry timing**: Retirements may have been recorded before associated issuances
3. **Historical corrections**: Previous year adjustments or corrections in the data
4. **Data consolidation**: Multiple project phases may not be properly separated

#### Recommended Actions
- See "Handling in the Application" section below
- For analysis, consider using the "Exclude problematic records" filter (enabled by default)
- For detailed analysis of these projects, see `problematic_records.csv`

---

### ✓ Data Integrity Checks Passed

All other data integrity checks have passed:
- ✓ **No negative issued credits**: All projects have issued ≥ 0 credits
- ✓ **No negative retired credits**: All projects have retired ≥ 0 credits
- ✓ **No duplicate Project IDs**: All 10,975 projects have unique identifiers
- ✓ **Credit math consistency**: All remaining credits correctly calculate as (Issued - Retired)

---

### Missing Data

**Voluntary Status**: 366 missing values (3.33%)
- This is minor and doesn't significantly impact analysis
- The app handles missing values gracefully

---

## Handling in the Application

### Data Quality Filter (Sidebar)
The application includes a **"Exclude projects with negative remaining credits"** checkbox in the Filters section.

**Default Setting**: ✓ CHECKED (enabled)  
**Rationale**: Improves data integrity and prevents misleading visualizations

### When This Filter is Enabled
- The 15 problematic projects are removed from all analysis
- All metrics, charts, and tables only include clean data
- The display shows how many records were filtered out

### When This Filter is Disabled
- All 10,975 projects are included
- A warning banner displays at the top of the app
- Users can view the problematic projects in detail (click "View Problematic Projects Details")

### Why Filter by Default?
1. **Data Integrity**: Prevents logically impossible negative values from skewing analysis
2. **User Experience**: Most users want clean data without anomalies
3. **Transparency**: Warning banner and expander clearly show what was filtered
4. **Flexibility**: Users can disable the filter if they need the complete raw dataset

---

## Data Quality Reports

### 1. HTML/Web Dashboard (app.py)
Run the Streamlit app to see:
- Data quality warning banner
- Problematic records detail view
- Expandable section for manual review
- All charts and metrics with quality filter applied

### 2. JSON Report (data_quality_report.json)
Generated by running `python data_quality_report.py`

Contains:
- Overall statistics
- Missing data analysis
- All data integrity check results
- Detailed problematic records
- Summary status and issues

### 3. CSV Export (problematic_records.csv)
Generated by running `python data_quality_report.py`

Includes:
- Project ID and Name
- Credits Issued, Retired, and Remaining
- Calculated vs. Actual remaining

---

## Running Data Quality Reports

### Generate/Update Reports
```bash
# In the capstone-module-zoebhall-28 directory
python data_quality_report.py
```

This creates:
- `data_quality_report.json` - Machine-readable report
- `problematic_records.csv` - Problematic records spreadsheet
- Console output with formatted report

### View Reports
1. **In-App**: Open the Streamlit app and check the banner
2. **JSON**: Open `data_quality_report.json` in any text editor
3. **CSV**: Open `problematic_records.csv` in Excel or similar

---

## Unit Tests

Comprehensive unit tests validate the data and app functionality.

### Run Tests
```bash
python test_app.py
```

### Test Coverage
- **Data Loading**: File existence, non-empty data, required columns
- **Data Types**: Numeric conversion, string validation
- **Data Integrity**: Positive values, unique IDs, credit math
- **Filtering**: Registry, country, status, type filters
- **Aggregations**: Groupby, value counts, sum calculations

### Test Results Summary
- ✓ 17 tests PASSED
- ⚠ 1 test FAILED (negative remaining credits - now documented and filtered)

---

## Recommendations for Users

### For General Analysis (Default)
✓ Keep "Exclude projects with negative remaining credits" **CHECKED**
- Cleaner visualizations
- More reliable metrics
- Recommended for presentations

### For Comprehensive Analysis
Uncheck the filter to:
- Include all 10,975 projects
- Analyze the problematic records in detail
- Understand the full dataset scope
- Research specific projects with data issues

### For Data Science/Research
1. Use the JSON report for programmatic analysis
2. Export problematic records CSV for detailed review
3. Review the test suite to understand data characteristics
4. Consider filtering the source data or obtaining corrections from registries

---

## Future Improvements

### Potential Enhancements
1. **Contact Registries**: Reach out to ACR, CAR, GS, VCS to clarify negative remaining records
2. **Data Versioning**: Track how many issues exist in each database version
3. **Automated Corrections**: Implement rules to auto-correct common issues
4. **More Granular Filtering**: Filter by issue type or severity
5. **Historical Tracking**: Monitor how data quality improves over time

### Contributing to Data Quality
If you identify additional issues:
1. Document them with specific project IDs
2. Add test cases to `test_app.py`
3. Update this documentation
4. Consider submitting findings to registry maintainers

---

## References

- **Test File**: `test_app.py` - Unit tests for data validation
- **Report Generator**: `data_quality_report.py` - Generates QA reports
- **Generated Reports**: 
  - `data_quality_report.json` - JSON format
  - `problematic_records.csv` - CSV format
- **Main Application**: `app.py` - Streamlit dashboard

---

## Questions?

For questions about data quality:
1. Check "View Problematic Projects Details" in the app
2. Review the JSON report for technical details
3. Check the test results with `python test_app.py`
4. Contact the database administrators or registry maintainers

---

**Last Updated**: February 25, 2026  
**Database Version**: v2025-12-year-end  
**Report Status**: WARNING - 15 projects with integrity issues (documented and filtered)
