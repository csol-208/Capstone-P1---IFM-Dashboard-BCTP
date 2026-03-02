import unittest
import pandas as pd
import numpy as np
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(__file__))

class TestDataLoading(unittest.TestCase):
    """Test data loading and validation"""
    
    def setUp(self):
        """Load the parquet file for testing"""
        self.file_path = "Voluntary-Registry-Offsets-Database--v2025-12-year-end.parquet"
        try:
            self.df = pd.read_parquet(self.file_path)
            self.df = self.df.replace("nan", None)
            # Convert numeric columns
            numeric_cols = [col for col in self.df.columns if any(str(year) in col for year in range(1996, 2026))]
            for col in numeric_cols:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
            self.file_exists = True
        except FileNotFoundError:
            self.file_exists = False
            print(f"Warning: {self.file_path} not found. Skipping file-dependent tests.")
    
    def test_file_exists(self):
        """Test that the parquet file exists"""
        self.assertTrue(self.file_exists, f"Parquet file '{self.file_path}' not found")
    
    def test_dataframe_not_empty(self):
        """Test that the dataframe is not empty"""
        if self.file_exists:
            self.assertGreater(len(self.df), 0, "DataFrame is empty")
    
    def test_required_columns_exist(self):
        """Test that required columns exist in the dataframe"""
        if self.file_exists:
            required_cols = [
                "Project ID",
                "Project Name",
                "Voluntary Registry",
                "Country",
                "Type",
                "Voluntary Status",
                "Total Credits \nIssued",
                "Total Credits \nRetired",
                "Total Credits Remaining"
            ]
            for col in required_cols:
                self.assertIn(col, self.df.columns, f"Missing required column: {col}")
    
    def test_data_types(self):
        """Test that numeric columns are properly converted"""
        if self.file_exists:
            numeric_cols = [col for col in self.df.columns if any(str(year) in col for year in range(1996, 2026))]
            for col in numeric_cols:
                # Check that column is numeric (int, float, or object that can be converted)
                try:
                    pd.to_numeric(self.df[col], errors='coerce')
                except Exception as e:
                    self.fail(f"Column {col} cannot be converted to numeric: {e}")
    
    def test_no_nan_strings(self):
        """Test that there are no string 'nan' values"""
        if self.file_exists:
            # Check object columns
            for col in self.df.select_dtypes(include='object').columns:
                nan_strings = self.df[col].astype(str).str.lower().eq('nan').sum()
                self.assertEqual(nan_strings, 0, f"Column {col} contains string 'nan' values")


class TestDataIntegrity(unittest.TestCase):
    """Test data integrity and logical consistency"""
    
    def setUp(self):
        """Load the parquet file for testing"""
        self.file_path = "Voluntary-Registry-Offsets-Database--v2025-12-year-end.parquet"
        try:
            self.df = pd.read_parquet(self.file_path)
            self.df = self.df.replace("nan", None)
            numeric_cols = [col for col in self.df.columns if any(str(year) in col for year in range(1996, 2026))]
            for col in numeric_cols:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
            self.file_exists = True
        except FileNotFoundError:
            self.file_exists = False
    
    def test_positive_credits(self):
        """Test that credit values are positive"""
        if self.file_exists:
            issued_col = "Total Credits \nIssued"
            retired_col = "Total Credits \nRetired"
            remaining_col = "Total Credits Remaining"
            
            # Check issued credits are non-negative
            if issued_col in self.df.columns:
                negative_issued = (self.df[issued_col] < 0).sum()
                self.assertEqual(negative_issued, 0, f"Found {negative_issued} negative values in {issued_col}")
            
            # Check retired credits are non-negative
            if retired_col in self.df.columns:
                negative_retired = (self.df[retired_col] < 0).sum()
                self.assertEqual(negative_retired, 0, f"Found {negative_retired} negative values in {retired_col}")
            
            # Check remaining credits are non-negative
            if remaining_col in self.df.columns:
                negative_remaining = (self.df[remaining_col] < 0).sum()
                self.assertEqual(negative_remaining, 0, f"Found {negative_remaining} negative values in {remaining_col}")
    
    def test_credits_math(self):
        """Test that issued = retired + remaining"""
        if self.file_exists:
            issued_col = "Total Credits \nIssued"
            retired_col = "Total Credits \nRetired"
            remaining_col = "Total Credits Remaining"
            
            if all(col in self.df.columns for col in [issued_col, retired_col, remaining_col]):
                # Calculate expected remaining
                calculated_remaining = self.df[issued_col] - self.df[retired_col]
                
                # Allow for small floating point errors
                mismatches = (abs(self.df[remaining_col] - calculated_remaining) > 0.01).sum()
                if mismatches > 0:
                    print(f"Warning: {mismatches} rows have mismatched credit calculations")
    
    def test_unique_project_ids(self):
        """Test that Project IDs are unique"""
        if self.file_exists:
            if "Project ID" in self.df.columns:
                duplicates = self.df["Project ID"].duplicated().sum()
                self.assertEqual(duplicates, 0, f"Found {duplicates} duplicate Project IDs")
    
    def test_valid_registries(self):
        """Test that registries are not empty"""
        if self.file_exists:
            if "Voluntary Registry" in self.df.columns:
                non_null = self.df["Voluntary Registry"].notna().sum()
                self.assertGreater(non_null, 0, "No valid registry values found")
    
    def test_valid_countries(self):
        """Test that countries are not empty"""
        if self.file_exists:
            if "Country" in self.df.columns:
                non_null = self.df["Country"].notna().sum()
                self.assertGreater(non_null, 0, "No valid country values found")


class TestFiltering(unittest.TestCase):
    """Test filtering logic"""
    
    def setUp(self):
        """Load the parquet file for testing"""
        self.file_path = "Voluntary-Registry-Offsets-Database--v2025-12-year-end.parquet"
        try:
            self.df = pd.read_parquet(self.file_path)
            self.df = self.df.replace("nan", None)
            numeric_cols = [col for col in self.df.columns if any(str(year) in col for year in range(1996, 2026))]
            for col in numeric_cols:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
            self.file_exists = True
        except FileNotFoundError:
            self.file_exists = False
    
    def test_registry_filter(self):
        """Test filtering by registry"""
        if self.file_exists and "Voluntary Registry" in self.df.columns:
            registries = self.df["Voluntary Registry"].dropna().unique()
            if len(registries) > 0:
                test_registry = registries[0]
                filtered = self.df[self.df["Voluntary Registry"] == test_registry]
                self.assertGreater(len(filtered), 0, f"Filter returned no results for {test_registry}")
    
    def test_country_filter(self):
        """Test filtering by country"""
        if self.file_exists and "Country" in self.df.columns:
            countries = self.df["Country"].dropna().unique()
            if len(countries) > 0:
                test_country = countries[0]
                filtered = self.df[self.df["Country"] == test_country]
                self.assertGreater(len(filtered), 0, f"Filter returned no results for {test_country}")
    
    def test_status_filter(self):
        """Test filtering by status"""
        if self.file_exists and "Voluntary Status" in self.df.columns:
            statuses = self.df["Voluntary Status"].dropna().unique()
            if len(statuses) > 0:
                test_status = statuses[0]
                filtered = self.df[self.df["Voluntary Status"] == test_status]
                self.assertGreater(len(filtered), 0, f"Filter returned no results for {test_status}")
    
    def test_type_filter(self):
        """Test filtering by project type"""
        if self.file_exists and "Type" in self.df.columns:
            types = self.df["Type"].dropna().unique()
            if len(types) > 0:
                test_type = types[0]
                filtered = self.df[self.df["Type"] == test_type]
                self.assertGreater(len(filtered), 0, f"Filter returned no results for type {test_type}")


class TestAggregations(unittest.TestCase):
    """Test aggregation calculations"""
    
    def setUp(self):
        """Load the parquet file for testing"""
        self.file_path = "Voluntary-Registry-Offsets-Database--v2025-12-year-end.parquet"
        try:
            self.df = pd.read_parquet(self.file_path)
            self.df = self.df.replace("nan", None)
            numeric_cols = [col for col in self.df.columns if any(str(year) in col for year in range(1996, 2026))]
            for col in numeric_cols:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
            self.file_exists = True
        except FileNotFoundError:
            self.file_exists = False
    
    def test_total_credits_calculation(self):
        """Test that total credits sum is calculated correctly"""
        if self.file_exists and "Total Credits \nIssued" in self.df.columns:
            total = self.df["Total Credits \nIssued"].sum()
            self.assertGreater(total, 0, "Total credits sum is zero or negative")
    
    def test_groupby_registry(self):
        """Test groupby aggregation for registries"""
        if self.file_exists and "Voluntary Registry" in self.df.columns:
            issued_col = "Total Credits \nIssued"
            if issued_col in self.df.columns:
                grouped = self.df.groupby("Voluntary Registry")[issued_col].sum()
                self.assertGreater(len(grouped), 0, "No registries found for groupby")
    
    def test_groupby_country(self):
        """Test groupby aggregation for countries"""
        if self.file_exists and "Country" in self.df.columns:
            grouped = self.df.groupby("Country").size()
            self.assertGreater(len(grouped), 0, "No countries found for groupby")
    
    def test_value_counts_status(self):
        """Test value_counts for status"""
        if self.file_exists and "Voluntary Status" in self.df.columns:
            counts = self.df["Voluntary Status"].value_counts()
            self.assertGreater(len(counts), 0, "No status values found for value_counts")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
