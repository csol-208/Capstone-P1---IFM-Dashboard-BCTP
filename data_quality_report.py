"""
Data Quality Report Generator for Voluntary Carbon Offsets Database
This script generates a comprehensive data quality report including:
- Overall statistics
- Missing data analysis
- Data integrity issues
- Problematic records
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json

class DataQualityReport:
    def __init__(self, parquet_path):
        """Initialize the report generator with data"""
        self.parquet_path = parquet_path
        self.df = None
        self.report = {}
        self.load_and_prepare_data()
    
    def load_and_prepare_data(self):
        """Load and prepare the data"""
        try:
            self.df = pd.read_parquet(self.parquet_path)
            self.df = self.df.replace("nan", None)
            
            # Convert numeric columns
            numeric_cols = [col for col in self.df.columns if any(str(year) in col for year in range(1996, 2026))]
            for col in numeric_cols:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
        except Exception as e:
            print(f"Error loading data: {e}")
            raise
    
    def generate_report(self):
        """Generate the complete data quality report"""
        self.report = {
            'timestamp': datetime.now().isoformat(),
            'overall_statistics': self._overall_statistics(),
            'missing_data': self._missing_data_analysis(),
            'data_integrity': self._data_integrity_check(),
            'problematic_records': self._find_problematic_records(),
        }
        # Summary must be generated after other sections
        self.report['summary'] = self._generate_summary()
        return self.report
    
    def _overall_statistics(self):
        """Generate overall dataset statistics"""
        issued_col = "Total Credits \nIssued"
        retired_col = "Total Credits \nRetired"
        remaining_col = "Total Credits Remaining"
        
        stats = {
            'total_records': len(self.df),
            'total_columns': len(self.df.columns),
            'unique_registries': self.df["Voluntary Registry"].nunique(),
            'unique_countries': self.df["Country"].nunique(),
            'unique_project_types': self.df["Type"].nunique(),
            'unique_statuses': self.df["Voluntary Status"].nunique(),
        }
        
        if issued_col in self.df.columns:
            stats['total_credits_issued'] = float(self.df[issued_col].sum())
        if retired_col in self.df.columns:
            stats['total_credits_retired'] = float(self.df[retired_col].sum())
        if remaining_col in self.df.columns:
            stats['total_credits_remaining'] = float(self.df[remaining_col].sum())
        
        return stats
    
    def _missing_data_analysis(self):
        """Analyze missing data"""
        missing_data = {}
        critical_columns = [
            "Project ID", "Project Name", "Voluntary Registry", 
            "Country", "Type", "Voluntary Status",
            "Total Credits \nIssued", "Total Credits \nRetired", "Total Credits Remaining"
        ]
        
        for col in critical_columns:
            if col in self.df.columns:
                null_count = self.df[col].isna().sum()
                null_pct = (null_count / len(self.df)) * 100
                missing_data[col] = {
                    'null_count': int(null_count),
                    'null_percentage': round(null_pct, 2)
                }
        
        return missing_data
    
    def _data_integrity_check(self):
        """Check data integrity"""
        integrity_issues = {}
        
        issued_col = "Total Credits \nIssued"
        retired_col = "Total Credits \nRetired"
        remaining_col = "Total Credits Remaining"
        
        # Check for negative credits
        if issued_col in self.df.columns:
            negative_issued = (self.df[issued_col] < 0).sum()
            integrity_issues['negative_issued_credits'] = int(negative_issued)
        
        if retired_col in self.df.columns:
            negative_retired = (self.df[retired_col] < 0).sum()
            integrity_issues['negative_retired_credits'] = int(negative_retired)
        
        if remaining_col in self.df.columns:
            negative_remaining = (self.df[remaining_col] < 0).sum()
            integrity_issues['negative_remaining_credits'] = int(negative_remaining)
        
        # Check for duplicate project IDs
        if "Project ID" in self.df.columns:
            duplicate_ids = self.df["Project ID"].duplicated().sum()
            integrity_issues['duplicate_project_ids'] = int(duplicate_ids)
        
        # Check math consistency (issued = retired + remaining)
        if all(col in self.df.columns for col in [issued_col, retired_col, remaining_col]):
            calculated_remaining = self.df[issued_col] - self.df[retired_col]
            mismatches = (abs(self.df[remaining_col] - calculated_remaining) > 0.01).sum()
            integrity_issues['credit_calculation_mismatches'] = int(mismatches)
        
        return integrity_issues
    
    def _find_problematic_records(self):
        """Find and detail problematic records"""
        problematic = {
            'negative_remaining_credits': [],
            'retired_exceeds_issued': []
        }
        
        issued_col = "Total Credits \nIssued"
        retired_col = "Total Credits \nRetired"
        remaining_col = "Total Credits Remaining"
        
        # Find projects with negative remaining credits
        if remaining_col in self.df.columns:
            negative_df = self.df[self.df[remaining_col] < 0]
            problematic['negative_remaining_credits'] = [
                {
                    'project_id': row.get('Project ID', 'N/A'),
                    'project_name': row.get('Project Name', 'N/A'),
                    'issued': float(row.get(issued_col, 0)) if pd.notna(row.get(issued_col)) else None,
                    'retired': float(row.get(retired_col, 0)) if pd.notna(row.get(retired_col)) else None,
                    'remaining': float(row.get(remaining_col, 0)) if pd.notna(row.get(remaining_col)) else None,
                    'difference': float(row.get(issued_col, 0) - row.get(retired_col, 0)) if all(pd.notna(row.get(col)) for col in [issued_col, retired_col]) else None
                }
                for _, row in negative_df.iterrows()
            ]
        
        return problematic
    
    def _generate_summary(self):
        """Generate a summary of findings"""
        summary = {
            'status': 'PASS',
            'issues_found': [],
            'warnings': []
        }
        
        integrity = self.report['data_integrity']
        
        # Check for critical issues
        if integrity['negative_remaining_credits'] > 0:
            summary['status'] = 'WARNING'
            summary['issues_found'].append(
                f"{integrity['negative_remaining_credits']} projects have more credits retired than issued"
            )
        
        if integrity['duplicate_project_ids'] > 0:
            summary['status'] = 'ERROR'
            summary['issues_found'].append(
                f"{integrity['duplicate_project_ids']} duplicate Project IDs found"
            )
        
        if integrity['credit_calculation_mismatches'] > 0:
            summary['warnings'].append(
                f"{integrity['credit_calculation_mismatches']} inconsistencies in credit math (issued ≠ retired + remaining)"
            )
        
        # Check for missing critical data
        missing = self.report['missing_data']
        for col, data in missing.items():
            if data['null_percentage'] > 5:
                summary['warnings'].append(
                    f"{data['null_percentage']}% of {col} values are missing"
                )
        
        if not summary['issues_found']:
            summary['issues_found'].append("None - Data integrity checks passed")
        
        return summary
    
    def print_report(self):
        """Print the report in a readable format"""
        if not self.report:
            self.generate_report()
        
        print("\n" + "="*80)
        print("VOLUNTARY CARBON OFFSETS DATABASE - DATA QUALITY REPORT")
        print("="*80)
        print(f"Generated: {self.report['timestamp']}\n")
        
        # Overall Statistics
        print("\n--- OVERALL STATISTICS ---")
        stats = self.report['overall_statistics']
        print(f"Total Records: {stats['total_records']:,}")
        print(f"Total Columns: {stats['total_columns']}")
        print(f"Unique Registries: {stats['unique_registries']}")
        print(f"Unique Countries: {stats['unique_countries']}")
        print(f"Project Types: {stats['unique_project_types']}")
        print(f"Status Categories: {stats['unique_statuses']}")
        if 'total_credits_issued' in stats:
            print(f"Total Credits Issued: {stats['total_credits_issued']:,.0f}")
        if 'total_credits_retired' in stats:
            print(f"Total Credits Retired: {stats['total_credits_retired']:,.0f}")
        if 'total_credits_remaining' in stats:
            print(f"Total Credits Remaining: {stats['total_credits_remaining']:,.0f}")
        
        # Missing Data
        print("\n--- MISSING DATA ANALYSIS ---")
        missing = self.report['missing_data']
        critical_missing = {k: v for k, v in missing.items() if v['null_percentage'] > 0}
        if critical_missing:
            for col, data in critical_missing.items():
                print(f"{col}: {data['null_count']} missing ({data['null_percentage']:.2f}%)")
        else:
            print("No missing critical data found")
        
        # Data Integrity
        print("\n--- DATA INTEGRITY CHECK ---")
        integrity = self.report['data_integrity']
        for issue, count in integrity.items():
            status = "✓" if count == 0 else "✗"
            issue_name = issue.replace('_', ' ').title()
            print(f"{status} {issue_name}: {count}")
        
        # Problematic Records
        print("\n--- PROBLEMATIC RECORDS ---")
        problematic = self.report['problematic_records']
        negative_records = problematic['negative_remaining_credits']
        
        if negative_records:
            print(f"Found {len(negative_records)} projects with negative remaining credits:\n")
            for i, record in enumerate(negative_records, 1):
                print(f"{i}. {record['project_id']}: {record['project_name']}")
                print(f"   Issued: {record['issued']:,.0f} | Retired: {record['retired']:,.0f} | Remaining: {record['remaining']:,.0f}")
                print()
        else:
            print("✓ No projects with negative remaining credits found")
        
        # Summary
        print("\n--- SUMMARY ---")
        summary = self.report['summary']
        print(f"Status: {summary['status']}")
        print(f"\nIssues Found:")
        for issue in summary['issues_found']:
            print(f"  • {issue}")
        if summary['warnings']:
            print(f"\nWarnings:")
            for warning in summary['warnings']:
                print(f"  ⚠ {warning}")
        
        print("\n" + "="*80 + "\n")
    
    def save_json_report(self, filename='data_quality_report.json'):
        """Save the report as JSON"""
        if not self.report:
            self.generate_report()
        
        # Convert numpy types to Python types for JSON serialization
        def convert_types(obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            elif isinstance(obj, dict):
                return {k: convert_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_types(item) for item in obj]
            return obj
        
        report_to_save = convert_types(self.report)
        
        with open(filename, 'w') as f:
            json.dump(report_to_save, f, indent=2)
        
        return filename
    
    def save_csv_problematic_records(self, filename='problematic_records.csv'):
        """Save problematic records to CSV"""
        problematic = self.report['problematic_records']['negative_remaining_credits']
        if problematic:
            problematic_df = pd.DataFrame(problematic)
            problematic_df.to_csv(filename, index=False)
            return filename
        return None


def main():
    """Main function to run the report"""
    report_gen = DataQualityReport("Voluntary-Registry-Offsets-Database--v2025-12-year-end.parquet")
    
    # Generate the report
    report_gen.generate_report()
    
    # Print to console
    report_gen.print_report()
    
    # Save JSON report
    json_file = report_gen.save_json_report()
    print(f"✓ JSON report saved to: {json_file}")
    
    # Save problematic records CSV
    csv_file = report_gen.save_csv_problematic_records()
    if csv_file:
        print(f"✓ Problematic records saved to: {csv_file}")
    
    print("\nReport generation complete!")


if __name__ == '__main__':
    main()
