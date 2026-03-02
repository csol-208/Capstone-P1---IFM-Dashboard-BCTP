# 📊 Excel Data Visualization Tool

An easy-to-use web interface for exploring and visualizing your Excel data with interactive graphs.

## Features

- **📈 Data Preview**: View your data with customizable row selection and column filtering
- **📊 Create Graphs**: Generate interactive charts including:
  - Bar Charts
  - Line Charts
  - Scatter Plots
  - Histograms
  - Box Plots
  - Pie Charts
  - Area Charts
- **🔍 Data Analysis**: View statistics, correlations, value counts, and missing data
- **🔎 Filters**: Filter your data by columns and download filtered results
- **Interactive Controls**: Customize colors, select axes, and adjust parameters

## Installation

1. Make sure you have Python 3.7+ installed
2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

Run the application with:
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### How to Use

1. **Data Preview Tab**: 
   - Adjust the slider to see different numbers of rows
   - Select specific columns to view

2. **Create Graph Tab**:
   - Select your chart type
   - Choose X and Y axes
   - Optionally color by another column
   - Interactive graph appears instantly

3. **Data Analysis Tab**:
   - View summary statistics
   - Check correlations between variables
   - See value distributions
   - Identify missing data

4. **Filters Tab**:
   - Filter by multiple columns
   - Apply custom ranges for numeric data
   - Download filtered results as CSV

## File Requirements

Make sure your Excel file `Voluntary-Registry-Offsets-Database--v2025-12-year-end.xlsx` is in the same directory as `app.py`.

## Tips

- Use the "Color by" option to add a third dimension to your visualizations
- Click and drag on graphs to zoom in
- Hover over data points to see exact values
- Use the Pie Chart to see top categories by percentage

Enjoy exploring your data! 🎉
