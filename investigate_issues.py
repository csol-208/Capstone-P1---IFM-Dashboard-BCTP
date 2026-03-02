import pandas as pd
import numpy as np

# Load and prepare data
df = pd.read_parquet("Voluntary-Registry-Offsets-Database--v2025-12-year-end.parquet")
df = df.replace("nan", None)

# Convert numeric columns
numeric_cols = [col for col in df.columns if any(str(year) in col for year in range(1996, 2026))]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

issued_col = "Total Credits \nIssued"
retired_col = "Total Credits \nRetired"
remaining_col = "Total Credits Remaining"

# Find rows with negative remaining credits
negative_remaining = df[df[remaining_col] < 0]

print(f"\n=== NEGATIVE REMAINING CREDITS ISSUE ===")
print(f"Found {len(negative_remaining)} rows with negative remaining credits\n")

if len(negative_remaining) > 0:
    print("Projects with negative remaining credits:")
    print("-" * 100)
    display_cols = ["Project ID", "Project Name", issued_col, retired_col, remaining_col]
    for col in display_cols:
        if col not in df.columns:
            print(f"Warning: Column '{col}' not found")
            continue
    
    for idx, row in negative_remaining.iterrows():
        print(f"\nProject ID: {row.get('Project ID', 'N/A')}")
        print(f"Project Name: {row.get('Project Name', 'N/A')}")
        print(f"  Issued: {row.get(issued_col, 'N/A')}")
        print(f"  Retired: {row.get(retired_col, 'N/A')}")
        print(f"  Remaining: {row.get(remaining_col, 'N/A')}")
        print(f"  Calculated (Issued - Retired): {row.get(issued_col, 0) - row.get(retired_col, 0)}")
        print("-" * 100)

# Check the math consistency
print(f"\n=== CREDIT CALCULATION CONSISTENCY ===")
calculated_remaining = df[issued_col] - df[retired_col]
mismatches = abs(df[remaining_col] - calculated_remaining) > 0.01
mismatch_count = mismatches.sum()

if mismatch_count > 0:
    print(f"Found {mismatch_count} rows where remaining ≠ issued - retired")
    print("\nExamples of mismatches:")
    mismatch_rows = df[mismatches].head(5)
    for idx, row in mismatch_rows.iterrows():
        print(f"\n  Project: {row.get('Project ID', 'N/A')}")
        print(f"    Issued: {row.get(issued_col, 'N/A')}")
        print(f"    Retired: {row.get(retired_col, 'N/A')}")
        print(f"    Remaining (in data): {row.get(remaining_col, 'N/A')}")
        print(f"    Remaining (calculated): {row.get(issued_col, 0) - row.get(retired_col, 0)}")
else:
    print("✓ All remaining credit values match the calculation (Issued - Retired)")

print(f"\n=== SUMMARY ===")
print(f"Total projects: {len(df)}")
print(f"Projects with negative remaining: {len(negative_remaining)}")
print(f"Calculation mismatches: {mismatch_count}")
