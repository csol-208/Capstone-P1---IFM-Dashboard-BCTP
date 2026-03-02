import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import warnings
warnings.filterwarnings("ignore")

# Set page configuration
st.set_page_config(
    page_title="Carbon Offsets Database",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.title("🌍 Voluntary Carbon Offsets Database")
st.markdown("Explore 10,975+ carbon offset projects from global voluntary registries")

# Load parquet file
@st.cache_data
def load_data():
    try:
        df = pd.read_parquet("Voluntary-Registry-Offsets-Database--v2025-12-year-end.parquet")
        # Convert string 'nan' to actual NaN
        df = df.replace("nan", None)
        # Convert numeric columns that might be strings
        numeric_cols = [col for col in df.columns if any(str(year) in col for year in range(1996, 2026))]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        return df
    except FileNotFoundError:
        st.error("❌ Could not find parquet file. Make sure it's in the same directory.")
        return None

# Load data
df = load_data()

if df is not None:
    # Sidebar - Filters
    with st.sidebar:
        st.header("🔍 Filters")
        st.markdown("---")
        
        # Registry filter
        registries = ["All"] + sorted(df["Voluntary Registry"].dropna().unique().tolist())
        selected_registries = st.multiselect("Registry", registries, default="All")
        
        # Country filter
        countries = ["All"] + sorted(df["Country"].dropna().unique().tolist())
        selected_countries = st.multiselect("Country", countries, default="All")
        
        # Status filter
        statuses = sorted(df["Voluntary Status"].dropna().unique().tolist())
        selected_statuses = st.multiselect("Project Status", statuses, default=statuses[:3])
        
        # Project Type filter
        types = sorted(df["Type"].dropna().unique().tolist())
        selected_types = st.multiselect("Project Type", types, default=types[:5] if len(types) > 5 else types)
        
        st.markdown("---")
        st.write(f"**Total Projects in DB:** {len(df):,}")
    
    # Apply filters
    filtered_df = df.copy()
    
    if "All" not in selected_registries:
        filtered_df = filtered_df[filtered_df["Voluntary Registry"].isin(selected_registries)]
    
    if "All" not in selected_countries:
        filtered_df = filtered_df[filtered_df["Country"].isin(selected_countries)]
    
    if selected_statuses:
        filtered_df = filtered_df[filtered_df["Voluntary Status"].isin(selected_statuses)]
    
    if selected_types:
        filtered_df = filtered_df[filtered_df["Type"].isin(selected_types)]
    
    # Display key metrics
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    issued_col = "Total Credits \nIssued"
    retired_col = "Total Credits \nRetired"
    remaining_col = "Total Credits Remaining"
    
    with col1:
        st.metric("📊 Total Projects", f"{len(filtered_df):,}")
    
    with col2:
        total_issued = filtered_df[issued_col].sum() if issued_col in filtered_df.columns else 0
        st.metric("✓ Credits Issued", f"{total_issued:,.0f}")
    
    with col3:
        total_retired = filtered_df[retired_col].sum() if retired_col in filtered_df.columns else 0
        st.metric("♻️ Credits Retired", f"{total_retired:,.0f}")
    
    with col4:
        total_remaining = filtered_df[remaining_col].sum() if remaining_col in filtered_df.columns else 0
        st.metric("💰 Credits Remaining", f"{total_remaining:,.0f}")
    
    st.markdown("---")
    
    # Create tabs for different analytics
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Charts & Analytics", "📊 Geographic View", "📋 Project Data", "🔍 Detailed Search"])
    
    with tab1:
        st.subheader("Charts & Analytics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Credits by Registry
            reg_credits = filtered_df.groupby("Voluntary Registry")[issued_col].sum().sort_values(ascending=False).head(10)
            if not reg_credits.empty:
                fig1 = px.bar(reg_credits, title="Top 10 Registries by Credits Issued", labels={"value": "Credits", "index": "Registry"})
                st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Project Status distribution
            status_counts = filtered_df["Voluntary Status"].value_counts()
            if not status_counts.empty:
                fig2 = px.pie(status_counts, names=status_counts.index, title="Projects by Status", hole=0.3)
                st.plotly_chart(fig2, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top Project Types
            type_credits = filtered_df.groupby("Type")[issued_col].sum().sort_values(ascending=False).head(10)
            if not type_credits.empty:
                fig3 = px.bar(type_credits, title="Top 10 Project Types by Credits Issued", labels={"value": "Credits", "index": "Type"})
                fig3.update_xaxes(tickangle=-45)
                st.plotly_chart(fig3, use_container_width=True)
        
        with col2:
            # Reduction vs Removal
            reduction_data = filtered_df["Reduction / Removal"].value_counts()
            if not reduction_data.empty:
                fig4 = px.pie(reduction_data, names=reduction_data.index, title="Projects by Type (Reduction vs Removal)")
                st.plotly_chart(fig4, use_container_width=True)
        
        # Credits by Vintage Year
        st.subheader("Credits Issued by Vintage Year")
        vintage_cols = [str(year) for year in range(1996, 2026)]
        vintage_issued = []
        years = []
        for year in range(1996, 2026):
            col_name = str(year)
            if col_name in filtered_df.columns:
                vintage_issued.append(filtered_df[col_name].sum())
                years.append(year)
        
        if vintage_issued:
            fig5 = go.Figure()
            fig5.add_trace(go.Scatter(x=years, y=vintage_issued, mode='lines+markers', fill='tozeroy', name='Credits Issued'))
            fig5.update_layout(title="Credits Issued by Vintage Year", xaxis_title="Year", yaxis_title="Credits", height=400)
            st.plotly_chart(fig5, use_container_width=True)
    
    with tab2:
        st.subheader("Geographic Distribution")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top Countries
            country_credits = filtered_df.groupby("Country")[issued_col].sum().sort_values(ascending=False).head(15)
            if not country_credits.empty:
                fig6 = px.bar(country_credits, title="Top 15 Countries by Credits Issued", labels={"value": "Credits", "index": "Country"})
                fig6.update_xaxes(tickangle=-45)
                st.plotly_chart(fig6, use_container_width=True)
        
        with col2:
            # Projects by Country
            country_projects = filtered_df["Country"].value_counts().head(15)
            if not country_projects.empty:
                fig7 = px.bar(country_projects, title="Top 15 Countries by Project Count", labels={"value": "Projects", "index": "Country"})
                fig7.update_xaxes(tickangle=-45)
                st.plotly_chart(fig7, use_container_width=True)
        
        # Region view
        if "Region" in filtered_df.columns:
            st.subheader("Projects by Region")
            region_credits = filtered_df.groupby("Region")[issued_col].sum().sort_values(ascending=False)
            if not region_credits.empty:
                fig8 = px.bar(region_credits, title="Credits Issued by Region", labels={"value": "Credits", "index": "Region"})
                st.plotly_chart(fig8, use_container_width=True)
    
    with tab3:
        st.subheader(f"Project Database ({len(filtered_df):,} projects)")
        
        # Select columns to display
        display_cols = st.multiselect(
            "Select columns to display:",
            filtered_df.columns.tolist(),
            default=["Project ID", "Project Name", "Voluntary Registry", "Country", "Type", "Voluntary Status", issued_col, retired_col, remaining_col]
        )
        
        if display_cols:
            # Display table
            st.dataframe(filtered_df[display_cols], use_container_width=True, height=400)
            
            # Download button
            csv = filtered_df[display_cols].to_csv(index=False)
            st.download_button(
                label="📥 Download Filtered Data (CSV)",
                data=csv,
                file_name="carbon_offsets_filtered.csv",
                mime="text/csv"
            )
    
    with tab4:
        st.subheader("🔍 Search & Filter")
        
        search_type = st.radio("Search by:", ["Project ID", "Project Name", "Developer", "Custom Filter"])
        
        if search_type == "Project ID":
            project_id = st.text_input("Enter Project ID:")
            if project_id:
                results = filtered_df[filtered_df["Project ID"].str.contains(project_id, case=False, na=False)]
                if not results.empty:
                    st.write(f"Found {len(results)} project(s):")
                    st.dataframe(results, use_container_width=True)
                else:
                    st.warning("No projects found with that ID.")
        
        elif search_type == "Project Name":
            project_name = st.text_input("Enter Project Name (partial match):")
            if project_name:
                results = filtered_df[filtered_df["Project Name"].str.contains(project_name, case=False, na=False)]
                if not results.empty:
                    st.write(f"Found {len(results)} project(s):")
                    st.dataframe(results, use_container_width=True)
                else:
                    st.warning("No projects found with that name.")
        
        elif search_type == "Developer":
            developer = st.text_input("Enter Developer Name (partial match):")
            if developer:
                results = filtered_df[filtered_df["Project Developer"].str.contains(developer, case=False, na=False)]
                if not results.empty:
                    st.write(f"Found {len(results)} project(s) by this developer:")
                    st.dataframe(results, use_container_width=True)
                else:
                    st.warning("No projects found with that developer.")
        
        elif search_type == "Custom Filter":
            st.write("Build a custom filter:")
            
            filter_column = st.selectbox("Column to filter:", filtered_df.columns)
            
            if filtered_df[filter_column].dtype == 'object':
                unique_values = sorted(filtered_df[filter_column].dropna().unique().tolist())
                filter_values = st.multiselect(f"Select values from {filter_column}:", unique_values)
                if filter_values:
                    results = filtered_df[filtered_df[filter_column].isin(filter_values)]
            else:
                min_val = float(filtered_df[filter_column].min())
                max_val = float(filtered_df[filter_column].max())
                filter_range = st.slider(f"Select range for {filter_column}:", min_val, max_val, (min_val, max_val))
                results = filtered_df[(filtered_df[filter_column] >= filter_range[0]) & (filtered_df[filter_column] <= filter_range[1])]
            
            if not results.empty:
                st.write(f"Found {len(results)} project(s):")
                st.dataframe(results, use_container_width=True)
            else:
                st.info("No results found for the selected filter.")

else:
    st.error("❌ Failed to load the parquet file. Make sure 'Voluntary-Registry-Offsets-Database--v2025-12-year-end.parquet' is in the same directory as this script.")
