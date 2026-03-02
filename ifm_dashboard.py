import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")

# Set page configuration with custom styling
st.set_page_config(
    page_title="Improved Forest Management | Carbon Credits",
    page_icon="🌲",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for hero section and styling - Symbiosis Coalition inspired
st.markdown("""
    <style>
    /* Color Palette */
    :root {
        --primary-dark: #1a4d7e;
        --primary-medium: #2166a0;
        --primary-light: #4a90cb;
        --accent-teal: #2ba084;
        --accent-gold: #c9a031;
        --accent-coral: #d97f6d;
        --background-light: #f8f9fa;
        --background-white: #ffffff;
        --text-dark: #2c3e50;
        --text-light: #7f8c8d;
    }
    
    /* Hero Section Styling */
    .hero-section {
        position: relative;
        margin-bottom: 40px;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 8px 16px rgba(26, 77, 126, 0.2);
    }
    
    .hero-text-container {
        background: linear-gradient(135deg, #1a4d7e 0%, #2166a0 50%, #2ba084 100%);
        color: white;
        padding: 80px 40px;
        text-align: center;
        position: relative;
        z-index: 2;
    }
    
    .hero-text-container::before {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 500px;
        height: 500px;
        background: radial-gradient(circle, rgba(201, 160, 49, 0.1) 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
    }
    
    .hero-image-container {
        width: 100%;
        height: 400px;
        background: url('https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=1920&h=600&fit=crop') center/cover no-repeat;
        position: relative;
    }
    
    .hero-section h1 {
        font-size: 3.5em;
        font-weight: 900;
        margin: 20px 0;
        text-shadow: 2px 2px 8px rgba(0, 0, 0, 0.3);
        letter-spacing: -1px;
    }
    
    .hero-section p {
        font-size: 1.3em;
        margin: 15px 0;
        opacity: 0.98;
        line-height: 1.6;
    }
    
    .hero-section .subtitle {
        font-size: 1.5em;
        opacity: 0.95;
        margin: 20px 0;
        font-weight: 600;
        color: #c9a031;
    }
    
    .stats-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin-top: 30px;
        padding-top: 30px;
        border-top: 2px solid rgba(201, 160, 49, 0.3);
    }
    
    .stat-box {
        background: rgba(255, 255, 255, 0.12);
        padding: 25px;
        border-radius: 12px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.25);
        transition: all 0.3s ease;
    }
    
    .stat-box:hover {
        background: rgba(255, 255, 255, 0.18);
        transform: translateY(-2px);
        border-color: rgba(201, 160, 49, 0.6);
    }
    
    .stat-number {
        font-size: 2.2em;
        font-weight: bold;
        color: #c9a031;
        font-family: 'Courier New', monospace;
    }
    
    .stat-label {
        font-size: 0.95em;
        opacity: 0.88;
        margin-top: 8px;
        font-weight: 500;
    }
    
    /* Section Styling */
    .section-title {
        font-size: 2.2em;
        color: #1a4d7e;
        margin: 40px 0 20px 0;
        font-weight: 800;
        border-left: 6px solid #2ba084;
        padding-left: 15px;
        position: relative;
    }
    
    .section-subtitle {
        font-size: 1.1em;
        color: #7f8c8d;
        margin-bottom: 20px;
        line-height: 1.5;
    }
    
    /* Card Styling */
    .info-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        padding: 25px;
        border-radius: 12px;
        border-left: 5px solid #2ba084;
        margin: 15px 0;
        box-shadow: 0 4px 12px rgba(26, 77, 126, 0.08);
        transition: all 0.3s ease;
    }
    
    .info-card:hover {
        box-shadow: 0 6px 20px rgba(26, 77, 126, 0.12);
        transform: translateY(-2px);
    }
    
    /* Filter Section */
    .filter-section {
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        padding: 25px;
        border-radius: 12px;
        margin-bottom: 30px;
        border: 1px solid #e1e8ed;
        box-shadow: 0 2px 8px rgba(26, 77, 126, 0.05);
    }
    
    /* Metric styling */
    .metric-card {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 12px;
        border-left: 4px solid #2ba084;
        transition: all 0.3s ease;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #2ba084;
        border-radius: 5px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #1a4d7e;
    }
    </style>
    """, unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_parquet("Voluntary-Registry-Offsets-Database--v2025-12-year-end.parquet")
        df = df.replace("nan", None)
        numeric_cols = [col for col in df.columns if any(str(year) in col for year in range(1996, 2026))]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        return df
    except FileNotFoundError:
        st.error("❌ Data file not found. Make sure the parquet file is in the same directory.")
        return None

def get_country_coordinates():
    """Get approximate coordinates for countries"""
    coordinates = {
        'United States': (37.0902, -95.7129),
        'Canada': (56.1304, -106.3468),
        'Brazil': (-14.2350, -51.9253),
        'Australia': (-25.2744, 133.7751),
        'Mexico': (23.6345, -102.5528),
        'Indonesia': (-0.7893, 113.9213),
        'Malaysia': (4.2105, 101.6964),
        'Peru': (-9.1900, -75.0152),
        'Colombia': (4.5709, -74.2973),
        'Russia': (61.5240, 105.3188),
        'China': (35.8617, 104.1954),
        'Vietnam': (14.0583, 108.2772),
        'Thailand': (15.8700, 100.9925),
        'Philippines': (12.8797, 121.7740),
        'Papua New Guinea': (-6.3150, 143.9555),
        'Chile': (-35.6751, -71.5430),
        'Argentina': (-38.4161, -63.6167),
        'Bolivia': (-16.2902, -63.5887),
        'Ecuador': (-1.8312, -78.1834),
        'Ghana': (7.3697, -5.3624),
        'Kenya': (-0.0236, 37.9062),
        'Democratic Republic of Congo': (-4.0383, 21.7587),
        'Cameroon': (3.8480, 11.5021),
        'Uganda': (1.3733, 32.2903),
        'Laos': (19.8523, 102.4955),
        'Myanmar': (21.9162, 95.9560),
        'Zambia': (-13.1339, 27.8493),
        'Zimbabwe': (-19.0154, 29.1549),
        'Mozambique': (-18.6657, 35.5296),
        'Cameroon': (3.8480, 11.5021),
        'Turkey': (38.9637, 35.2433),
        'Congo': (-0.6455, 15.5524),
        'Central African Republic': (6.6111, 20.9394),
        'Tanzania': (-6.3690, 34.8888),
        'South Africa': (-30.5595, 22.9375),
        'Nicaragua': (12.8654, -85.2072),
        'Costa Rica': (9.7489, -83.7534),
        'Panama': (8.7832, -80.7744),
        'Honduras': (15.2000, -86.2419),
        'Guatemala': (15.7835, -90.2308),
        'El Salvador': (13.7942, -88.8965),
        'Dominican Republic': (18.7357, -70.1627),
        'Haiti': (18.9712, -72.2852),
    }
    return coordinates

# Load data
df = load_data()

if df is not None:
    # Filter for Improved Forest Management (IFM) projects
    ifm_projects = df[df["Type"].str.contains("Improved Forest Management|IFM|Forest Management", case=False, na=False)]
    
    # ============ HERO SECTION ============
    hero_html = f"""
    <div class="hero-section">
        <div class="hero-text-container">
            <h1>🌲 Improved Forest Management</h1>
            <p class="subtitle">Carbon Credits & Climate Impact</p>
            <p>Explore {len(ifm_projects):,} verified forest management projects worldwide protecting millions of trees and storing carbon</p>
        </div>
        <div class="hero-image-container"></div>
    </div>
    """
    
    st.markdown(hero_html, unsafe_allow_html=True)
    
    # ============ INTERACTIVE FILTERS ============
    st.markdown('<div class="section-title">🔍 Explore the Data</div>', unsafe_allow_html=True)
    
    with st.expander("🎛️ Filters & Options", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_registries = st.multiselect(
                "Registry",
                options=sorted(ifm_projects["Voluntary Registry"].dropna().unique()),
                default=None,
                key="registry_filter"
            )
        
        with col2:
            selected_countries = st.multiselect(
                "Countries",
                options=sorted(ifm_projects["Country"].dropna().unique()),
                default=None,
                key="country_filter"
            )
        
        with col3:
            selected_status = st.multiselect(
                "Project Status",
                options=sorted(ifm_projects["Voluntary Status"].dropna().unique()),
                default=None,
                key="status_filter"
            )
    
    # Apply filters
    filtered_ifm = ifm_projects.copy()
    
    if selected_registries:
        filtered_ifm = filtered_ifm[filtered_ifm["Voluntary Registry"].isin(selected_registries)]
    
    if selected_countries:
        filtered_ifm = filtered_ifm[filtered_ifm["Country"].isin(selected_countries)]
    
    if selected_status:
        filtered_ifm = filtered_ifm[filtered_ifm["Voluntary Status"].isin(selected_status)]
    
    # ============ KEY METRICS ============
    st.markdown('<div class="section-title">📊 Key Metrics</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    issued_col = "Total Credits \nIssued"
    retired_col = "Total Credits \nRetired"
    remaining_col = "Total Credits Remaining"
    
    with col1:
        st.metric("🌍 Projects", f"{len(filtered_ifm):,}")
    
    with col2:
        total_issued = filtered_ifm[issued_col].sum() if issued_col in filtered_ifm.columns else 0
        st.metric("📤 Credits Issued", f"{int(total_issued):,}")
    
    with col3:
        total_retired = filtered_ifm[retired_col].sum() if retired_col in filtered_ifm.columns else 0
        st.metric("♻️ Credits Retired", f"{int(total_retired):,}")
    
    with col4:
        total_remaining = filtered_ifm[remaining_col].sum() if remaining_col in filtered_ifm.columns else 0
        st.metric("💰 Credits Remaining", f"{int(total_remaining):,}")
    
    st.divider()
    
    # ============ MAIN CONTENT TABS ============
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["🗺️ World Map", "📈 Analytics", "🌍 Geographic", "📋 Projects", "ℹ️ About IFM"]
    )
    
    # ============ WORLD MAP TAB ============
    with tab1:
        st.markdown('<div class="section-title">📍 Project Locations Worldwide</div>', unsafe_allow_html=True)
        st.markdown('<p class="section-subtitle">Interactive map showing Improved Forest Management projects globally. Hover over markers for details.</p>', unsafe_allow_html=True)
        
        # Prepare data for map
        country_coords = get_country_coordinates()
        map_data = []
        
        for country in filtered_ifm["Country"].dropna().unique():
            country_df = filtered_ifm[filtered_ifm["Country"] == country]
            if country in country_coords:
                lat, lon = country_coords[country]
                map_data.append({
                    'Country': country,
                    'Latitude': lat,
                    'Longitude': lon,
                    'Projects': len(country_df),
                    'Credits_Issued': country_df[issued_col].sum(),
                    'Credits_Remaining': country_df[remaining_col].sum(),
                })
        
        if map_data:
            map_df = pd.DataFrame(map_data)
            
            # Create map with plotly
            fig_map = px.scatter_geo(
                map_df,
                lat='Latitude',
                lon='Longitude',
                hover_name='Country',
                size='Projects',
                color='Credits_Issued',
                hover_data={
                    'Latitude': False,
                    'Longitude': False,
                    'Projects': True,
                    'Credits_Issued': ':.0f',
                    'Credits_Remaining': ':.0f'
                },
                color_continuous_scale='RdYlBu_r',
                title='IFM Projects by Location (Size = Number of Projects)',
                projection='natural earth',
                size_max=120,
            )
            
            fig_map.update_layout(
                height=700,
                geo=dict(
                    showland=True,
                    landcolor='rgb(243, 247, 250)',
                    showocean=True,
                    oceancolor='rgb(230, 245, 255)',
                ),
                coloraxis_colorbar=dict(
                    title='Credits<br>Issued',
                    thickness=15,
                    len=0.7,
                ),
                font=dict(size=12)
            )
            
            st.plotly_chart(fig_map, use_container_width=True)
            
            # Top countries
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Top Countries by Project Count")
                top_countries = map_df.nlargest(10, 'Projects')[['Country', 'Projects']]
                fig_top = px.bar(
                    top_countries,
                    x='Projects',
                    y='Country',
                    orientation='h',
                    title='Projects by Country',
                    color='Projects',
                    color_continuous_scale='Viridis'
                )
                fig_top.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig_top, use_container_width=True)
            
            with col2:
                st.subheader("Top Countries by Credits")
                top_credits = map_df.nlargest(10, 'Credits_Issued')[['Country', 'Credits_Issued']]
                fig_cred = px.bar(
                    top_credits,
                    x='Credits_Issued',
                    y='Country',
                    orientation='h',
                    title='Credits Issued by Country',
                    color='Credits_Issued',
                    color_continuous_scale='RdYlBu_r'
                )
                fig_cred.update_layout(height=400, showlegend=False)
                st.plotly_chart(fig_cred, use_container_width=True)
        else:
            st.warning("No geographic data available for selected filters")
    
    # ============ ANALYTICS TAB ============
    with tab2:
        st.markdown('<div class="section-title">📊 Carbon Credits Analytics</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Credits by Registry
            if issued_col in filtered_ifm.columns:
                reg_credits = filtered_ifm.groupby("Voluntary Registry")[issued_col].sum().sort_values(ascending=False)
                if not reg_credits.empty:
                    fig1 = px.pie(
                        values=reg_credits.values,
                        names=reg_credits.index,
                        title="Credits Issued by Registry",
                        color_discrete_sequence=['#1a4d7e', '#2166a0', '#4a90cb', '#2ba084', '#c9a031']
                    )
                    st.plotly_chart(fig1, use_container_width=True)
        
        with col2:
            # Project Status distribution
            status_counts = filtered_ifm["Voluntary Status"].value_counts()
            if not status_counts.empty:
                fig2 = px.pie(
                    values=status_counts.values,
                    names=status_counts.index,
                    title="Projects by Status",
                    hole=0.3,
                    color_discrete_sequence=['#1a4d7e', '#2166a0', '#4a90cb', '#2ba084', '#c9a031', '#d97f6d']
                )
                st.plotly_chart(fig2, use_container_width=True)
        
        # Credits by Vintage Year
        st.subheader("Credits Issued Over Time (by Vintage Year)")
        vintage_issued = []
        years = []
        for year in range(1996, 2026):
            col_name = str(year)
            if col_name in filtered_ifm.columns:
                vintage_issued.append(filtered_ifm[col_name].sum())
                years.append(year)
        
        if vintage_issued:
            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(
                x=years,
                y=vintage_issued,
                mode='lines+markers',
                fill='tozeroy',
                name='Credits Issued',
                line=dict(color='#1a4d7e', width=3),
                fillcolor='rgba(26, 77, 126, 0.15)'
            ))
            fig3.update_layout(
                title="Credits Issued by Vintage Year",
                xaxis_title="Year",
                yaxis_title="Credits",
                height=400,
                hovermode='x unified',
                template='plotly_white',
                plot_bgcolor='rgba(248, 249, 250, 0.5)',
            )
            st.plotly_chart(fig3, use_container_width=True)
        
        # Credits issued vs retired vs remaining
        col1, col2 = st.columns(2)
        
        with col1:
            total_issued_val = filtered_ifm[issued_col].sum()
            total_retired_val = filtered_ifm[retired_col].sum()
            total_remaining_val = filtered_ifm[remaining_col].sum()
            
            fig4 = go.Figure(data=[
                go.Bar(name='Issued', x=['Total'], y=[total_issued_val], marker_color='#1a4d7e'),
                go.Bar(name='Retired', x=['Total'], y=[total_retired_val], marker_color='#2ba084'),
                go.Bar(name='Remaining', x=['Total'], y=[total_remaining_val], marker_color='#c9a031'),
            ])
            fig4.update_layout(
                title="Credit Lifecycle Overview",
                barmode='group',
                height=400,
                template='plotly_white',
                plot_bgcolor='rgba(248, 249, 250, 0.5)',
            )
            st.plotly_chart(fig4, use_container_width=True)
        
        with col2:
            # Stacked bar showing retired percentage
            retired_pct = (total_retired_val / total_issued_val * 100) if total_issued_val > 0 else 0
            remaining_pct = (total_remaining_val / total_issued_val * 100) if total_issued_val > 0 else 0
            
            fig5 = go.Figure(data=[
                go.Bar(name='Retired (%)', x=['Credits'], y=[retired_pct], marker_color='#2ba084'),
                go.Bar(name='Remaining (%)', x=['Credits'], y=[remaining_pct], marker_color='#1a4d7e'),
            ])
            fig5.update_layout(
                title="Credit Utilization Rate",
                barmode='stack',
                height=400,
                template='plotly_white',
                plot_bgcolor='rgba(248, 249, 250, 0.5)',
                yaxis_title="Percentage (%)"
            )
            st.plotly_chart(fig5, use_container_width=True)
    
    # ============ GEOGRAPHIC TAB ============
    with tab3:
        st.markdown('<div class="section-title">🌍 Geographic Distribution</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top Countries by Project Count
            country_projects = filtered_ifm["Country"].value_counts().head(15)
            if not country_projects.empty:
                fig6 = px.bar(
                    country_projects,
                    title="Top 15 Countries by Project Count",
                    labels={"value": "Projects", "index": "Country"},
                    color=country_projects.values,
                    color_continuous_scale='Viridis'
                )
                fig6.update_xaxes(tickangle=-45)
                fig6.update_layout(height=500, xaxis_title="Country", yaxis_title="Number of Projects")
                st.plotly_chart(fig6, use_container_width=True)
        
        with col2:
            # Top Countries by Credits Issued
            country_credits = filtered_ifm.groupby("Country")[issued_col].sum().sort_values(ascending=False).head(15)
            if not country_credits.empty:
                fig7 = px.bar(
                    country_credits,
                    title="Top 15 Countries by Credits Issued",
                    labels={"value": "Credits", "index": "Country"},
                    color=country_credits.values,
                    color_continuous_scale='RdYlBu_r'
                )
                fig7.update_xaxes(tickangle=-45)
                fig7.update_layout(height=500, xaxis_title="Country", yaxis_title="Credits Issued")
                st.plotly_chart(fig7, use_container_width=True)
        
        # Registry breakdown
        st.subheader("Credits by Registry")
        registry_stats = filtered_ifm.groupby("Voluntary Registry").agg({
            issued_col: 'sum',
            'Project ID': 'count'
        }).rename(columns={'Project ID': 'Projects'})
        registry_stats = registry_stats.sort_values(by=issued_col, ascending=False)
        
        fig8 = go.Figure()
        fig8.add_trace(go.Bar(
            name='Credits Issued',
            x=registry_stats.index,
            y=registry_stats[issued_col],
            yaxis='y',
            marker_color='#1a4d7e'
        ))
        fig8.add_trace(go.Scatter(
            name='Project Count',
            x=registry_stats.index,
            y=registry_stats['Projects'],
            yaxis='y2',
            mode='lines+markers',
            line=dict(color='#c9a031', width=3),
            marker=dict(size=10)
        ))
        
        fig8.update_layout(
            title="Registry Performance: Credits vs Project Count",
            yaxis=dict(title='Credits Issued', side='left'),
            yaxis2=dict(title='Number of Projects', overlaying='y', side='right'),
            hovermode='x unified',
            height=500,
            template='plotly_white',
            plot_bgcolor='rgba(248, 249, 250, 0.5)',
        )
        st.plotly_chart(fig8, use_container_width=True)
    
    # ============ PROJECTS TAB ============
    with tab4:
        st.markdown('<div class="section-title">📋 Project Database</div>', unsafe_allow_html=True)
        
        # Search and filter
        search_query = st.text_input("🔍 Search by project name or developer", value="")
        
        display_df = filtered_ifm.copy()
        
        if search_query:
            display_df = display_df[
                (display_df["Project Name"].str.contains(search_query, case=False, na=False)) |
                (display_df["Project Developer"].str.contains(search_query, case=False, na=False))
            ]
        
        # Column selector
        default_cols = [
            "Project ID",
            "Project Name",
            "Country",
            "Voluntary Registry",
            "Voluntary Status",
            issued_col,
            remaining_col,
            "Registry Documents",
        ]
        
        available_cols = [col for col in default_cols if col in display_df.columns]
        
        if not display_df.empty:
            st.write(f"**Showing {len(display_df):,} projects**")
            
            # Format dataframe with clickable links for Registry Documents
            display_df_formatted = display_df[available_cols].sort_values(
                by=issued_col,
                ascending=False
            ).copy()
            
            # Convert URLs to clickable links showing just the website URL
            if "Registry Documents" in display_df_formatted.columns:
                display_df_formatted["Registry Documents"] = display_df_formatted["Registry Documents"].apply(
                    lambda x: x if pd.notna(x) and x != "" else "N/A"
                )
            
            st.dataframe(
                display_df_formatted,
                use_container_width=True,
                height=600,
                column_config={
                    "Registry Documents": st.column_config.LinkColumn(
                        "Registry Documents"
                    ) if "Registry Documents" in available_cols else None
                }
            )
            
            # Download button
            csv = display_df[available_cols].to_csv(index=False)
            st.download_button(
                label="📥 Download Data (CSV)",
                data=csv,
                file_name="ifm_projects.csv",
                mime="text/csv"
            )
        else:
            st.info("No projects found matching your search criteria")
    
    # ============ ABOUT IFM TAB ============
    with tab5:
        st.markdown('<div class="section-title">ℹ️ About Improved Forest Management</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### What is Improved Forest Management (IFM)?
            
            Improved Forest Management refers to changes in forest management practices that 
            reduce harvesting intensity or delay harvesting. This conservation approach stores 
            carbon in forests that would otherwise be harvested.
            
            ### Key Benefits:
            - 🌳 **Carbon Sequestration**: Forests store more carbon when harvested less intensively
            - 🌎 **Climate Mitigation**: Helps reduce atmospheric CO₂ levels
            - 🦋 **Biodiversity**: Reduced harvesting supports wildlife habitats
            - 💼 **Economic**: Provides revenue through carbon credits
            - 🏘️ **Community**: Supports local livelihoods and forest-dependent communities
            """)
        
        with col2:
            st.markdown("""
            ### How IFM Projects Work:
            
            1. **Baseline**: Establish historical harvesting patterns
            2. **Implementation**: Reduce or delay timber harvest
            3. **Monitoring**: Track carbon stored in standing forests
            4. **Verification**: Third-party verification of carbon benefits
            5. **Credits**: Generate tradeable carbon credits
            
            ### Carbon Credit Metrics:
            - **1 Carbon Credit** = 1 metric ton of CO₂ equivalent
            - **Projects Track**:
              - Credits Issued: Total credits generated
              - Credits Retired: Credits removed from circulation (used)
              - Credits Remaining: Credits available for trading
            """)
        
        st.divider()
        
        # IFM Statistics
        st.markdown("### Global IFM Project Statistics")
        
        stat_col1, stat_col2, stat_col3, stat_col4, stat_col5 = st.columns(5)
        
        with stat_col1:
            st.metric("🌍 Countries", len(filtered_ifm["Country"].dropna().unique()))
        
        with stat_col2:
            st.metric("📊 Registries", len(filtered_ifm["Voluntary Registry"].dropna().unique()))
        
        with stat_col3:
            avg_issued = filtered_ifm[issued_col].mean() if len(filtered_ifm) > 0 else 0
            st.metric("📈 Avg Credits/Project", f"{int(avg_issued):,}")
        
        with stat_col4:
            retired_rate = (total_retired_val / total_issued_val * 100) if total_issued_val > 0 else 0
            st.metric("♻️ Retired Rate", f"{retired_rate:.1f}%")
        
        with stat_col5:
            remaining_rate = (total_remaining_val / total_issued_val * 100) if total_issued_val > 0 else 0
            st.metric("💰 Remaining Rate", f"{remaining_rate:.1f}%")
        
        st.divider()
        
        # Project Status Distribution
        st.subheader("Project Status Overview")
        
        status_dist = filtered_ifm["Voluntary Status"].value_counts()
        if not status_dist.empty:
            fig_status = px.bar(
                status_dist,
                title="IFM Projects by Status",
                labels={"value": "Number of Projects", "index": "Status"},
                color=status_dist.values,
                color_continuous_scale='RdYlBu_r'
            )
            fig_status.update_xaxes(tickangle=-45)
            st.plotly_chart(fig_status, use_container_width=True)

else:
    st.error("❌ Unable to load data. Please check the data file path.")
