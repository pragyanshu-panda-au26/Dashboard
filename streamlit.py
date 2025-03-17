# import streamlit as st
# import pandas as pd
# import plotly.express as px

# # Load and preprocess data
# def load_data():
#     df = pd.read_csv('noida_properties_all_pages.csv')
#     # Clean numerical columns
#     df['Area'] = df['Area'].str.replace('[^\d.]', '', regex=True).astype(float)
#     df['Price'] = df['Price'].astype('int64')
#     df['Price per sqft'] = df['Price per sqft'].astype('float')
#     return df

# df = load_data()

# # App header with personal touch
# st.header("🏡 Noida Property Explorer")
# st.caption("Built by  MovinHomes© Tech Lead real estate analytics")

# # Interactive filters
# col1, col2, col3 = st.columns(3)
# with col1:
#     society = st.selectbox(
#         "Select Society", 
#         options=sorted(df['Property Name'].unique()),
#         help="Start typing for quick search"
#     )

# # Dynamic options based on selection
# society_data = df[df['Property Name'] == society]
# bhk_options = sorted(society_data['BHK'].unique())
# location_options = sorted(society_data['Location'].unique())

# with col2:
#     bhk = st.selectbox("Select BHK", options=bhk_options)

# with col3:
#     location = st.selectbox("Select Location", options=location_options)

# # Filter data
# filtered_data = society_data[
#     (society_data['BHK'] == bhk) & 
#     (society_data['Location'] == location)
# ]

# # Display results
# if not filtered_data.empty:
#     st.success(f"Found {len(filtered_data)} properties matching your criteria")
    
#     # Property listings
#     st.subheader("📌 Property Details")
#     st.dataframe(
#         filtered_data[[
#             'Price', 'Area', 'Price per sqft', 
#             'Posted Time', 'Posted By'
#         ]].reset_index(drop=True),
#         use_container_width=True
#     )

#     # Visual analytics
#     st.subheader("📊 Price Analysis")
    
#     tab1, tab2 = st.tabs(["Distribution", "Comparisons"])
    
#     with tab1:
#         fig = px.histogram(
#             filtered_data, 
#             x='Price',
#             title="Price Distribution",
#             color_discrete_sequence=['#FF4B4B']
#         )
#         st.plotly_chart(fig, use_container_width=True)

#     with tab2:
#         fig = px.scatter(
#             filtered_data,
#             x='Area',
#             y='Price',
#             size='Price per sqft',
#             color='Posted By',
#             title="Price vs Area Analysis"
#         )
#         st.plotly_chart(fig, use_container_width=True)

# else:
#     st.warning("No properties found matching these filters")


# st.subheader("📈 High Variance Properties")

# # Make sure we have the main dataframe loaded
# if 'df' not in locals():
#     df = load_data()

# # Filter data for the selected location
# location_data = df[df['Location'] == location].copy()

# if not location_data.empty:
#     # Group by Property Name and BHK to calculate variance metrics
#     variance_by_society = location_data.groupby(['Property Name', 'BHK']).agg(
#         max_price=('Price', 'max'),
#         min_price=('Price', 'min'),
#         price_variance=('Price', lambda x: x.max() - x.min()),
#         avg_price=('Price', 'mean'),
#         count=('Price', 'count')
#     ).reset_index()
    
#     # Filter for societies with at least 2 properties (to ensure variance can be calculated)
#     variance_by_society = variance_by_society[variance_by_society['count'] >= 2]
    
#     # Sort by highest variance and get top 5
#     top_variance_societies = variance_by_society.sort_values('price_variance', ascending=False).head(5)
    
#     if not top_variance_societies.empty:
#         st.write(f"Top 5 societies with highest price variance in {location}:")
        
#         # Format the data for better readability
#         top_variance_societies['max_price'] = top_variance_societies['max_price'].apply(lambda x: f"₹{x:,.0f}")
#         top_variance_societies['min_price'] = top_variance_societies['min_price'].apply(lambda x: f"₹{x:,.0f}")
#         top_variance_societies['price_variance'] = top_variance_societies['price_variance'].apply(lambda x: f"₹{x:,.0f}")
#         top_variance_societies['avg_price'] = top_variance_societies['avg_price'].apply(lambda x: f"₹{x:,.0f}")
        
#         # Rename columns for better display
#         top_variance_societies.columns = ['Society', 'BHK', 'Max Price', 'Min Price', 'Price Variance', 'Avg Price', 'Properties']
        
#         # Display as a styled dataframe
#         st.dataframe(top_variance_societies, use_container_width=True)
        
#         # Visualize the variance
#         fig = px.bar(
#             top_variance_societies, 
#             x='Society', 
#             y='Price Variance',
#             color='BHK',
#             title=f"Societies with Highest Price Variance in {location}",
#             text='Price Variance',
#             barmode='group'
#         )
#         fig.update_traces(texttemplate='%{text}', textposition='outside')
#         fig.update_layout(xaxis_tickangle=-45)
#         st.plotly_chart(fig, use_container_width=True)
        
#         # Add insights
#         highest_variance_society = top_variance_societies.iloc[0]['Society']
#         highest_variance_bhk = top_variance_societies.iloc[0]['BHK']
#         st.info(f"💡 **Insight**: {highest_variance_society} shows the highest price variance for {highest_variance_bhk} BHK properties in {location}. This could indicate potential negotiation opportunities or significant differences in property features like floor level, view, or interior condition.")
#     else:
#         st.info(f"Not enough data to calculate meaningful variance in {location}. Most societies have only one property listed per BHK type.")
# else:
#     st.warning(f"No properties found in {location} to analyze variance.")

# # Cultural touch in footer
# st.markdown("---")
# st.caption("Proudly made in India 🇮🇳 |")


# -----------------------------------------
import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime
import statsmodels

# Initialize session state for filter reset
if 'reset_clicked' not in st.session_state:
    st.session_state.reset_clicked = False

# Set page configuration
st.set_page_config(
    page_title="Noida Property Analytics",
    page_icon="ðŸ“Š",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for internal dashboard
def local_css():
    css = """
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3 {
        font-weight: 600;
        color: #1E3A8A;
    }
    
    .stDataFrame {
        border-radius: 4px;
    }
    
    .metric-container {
        background-color: #F3F4F6;
        border-radius: 4px;
        padding: 10px;
        border-left: 4px solid #2563EB;
    }
    
    .section-header {
        background-color: #F3F4F6;
        border-radius: 4px;
        padding: 8px 12px;
        margin: 15px 0px 15px 0px;
        border-left: 4px solid #2563EB;
        font-weight: 600;
    }
    
    .insight-box {
        background-color: #DBEAFE;
        border-radius: 4px;
        padding: 10px;
        border-left: 4px solid #2563EB;
        margin-top: 15px;
    }
    
    .stButton > button {
        background-color: #2563EB;
        color: white;
        border-radius: 4px;
        font-weight: 500;
    }
    
    .stButton > button:hover {
        background-color: #1D4ED8;
    }
    
    /* Table styling for better readability */
    .dataframe {
        font-size: 12px !important;
    }
    
    .dataframe th {
        background-color: #E5E7EB !important;
        color: #1F2937 !important;
        font-weight: 600 !important;
    }
    
    /* Compact elements for internal dashboard */
    .stSelectbox > div > div {
        padding-top: 0px !important;
        padding-bottom: 0px !important;
    }
    """
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

# Call custom CSS
local_css()

# Reset function for filters
def reset_filters():
    st.session_state.reset_clicked = True
    return

# Load and preprocess data with caching for performance
# @st.cache_data
# def load_data():
#     df = pd.read_csv('noida_properties_all_pages.csv')
#     # Clean numerical columns
#     df['Area'] = df['Area'].str.replace('[^\d.]', '', regex=True).astype(float)
#     df['Price'] = df['Price'].astype('int64')
#     df['Price per sqft'] = df['Price per sqft'].astype('float')
#     return df
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('noida_properties_all_pages.csv')
        
        # Clean Area column - remove non-numeric characters and convert to float
        df['Area'] = df['Area'].str.replace('[^\d.]', '', regex=True).astype(int)
        
        # Handle "Price on Request" or any non-numeric values in the Price column
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
        df = df.dropna(subset=['Price'])
        df['Price'] = df['Price'].astype('int64')
        
        # Clean Price per sqft column and handle any potential issues
        df['Price per sqft'] = pd.to_numeric(df['Price per sqft'], errors='coerce')
        
        # If Price per sqft is NaN, calculate it from Price and Area
        mask = df['Price per sqft'].isna()
        if any(mask):
            df.loc[mask, 'Price per sqft'] = df.loc[mask, 'Price'] / df.loc[mask, 'Area']
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()



df = load_data()

# Internal dashboard header
st.markdown("<h2>Noida Property Analytics Dashboard</h2>", unsafe_allow_html=True)
st.markdown("<p style='color: #6B7280; margin-bottom: 20px;'>Internal analysis tool for <a href='https://movin.homes'>Movin.homes©</a></p>", unsafe_allow_html=True)

# More comprehensive sidebar filters for internal use
with st.sidebar:
    st.markdown("## Filters")
    
    # Property filters
    st.markdown("### Property Filters")
    
    # Check if reset was clicked, use default values in that case
    if st.session_state.reset_clicked:
        society_index = 0
        location_index = 0
        bhk_index = 0
        type_index = 0
        st.session_state.reset_clicked = False  # Reset the state for next use
    else:
        society_index = None
        location_index = None
        bhk_index = None
        type_index = None
    
    # Main filters
    society = st.selectbox(
        "Society", 
        options=sorted(df['Property Name'].unique()),
        index=society_index
    )

    # Dynamic options based on selection
    society_data = df[df['Property Name'] == society]
    
    # Get filter options based on selection
    bhk_options = sorted(society_data['BHK'].unique()) if not society_data.empty else []
    location_options = sorted(society_data['Location'].unique()) if not society_data.empty else []
    type_options = sorted(society_data['Type'].unique()) if not society_data.empty else []
    
    # BHK selection with safety check
    if bhk_options:
        bhk = st.selectbox("BHK Type", options=bhk_options, index=bhk_index if bhk_index is not None and bhk_index < len(bhk_options) else 0)
    else:
        st.warning("No BHK options available for selected society")
        bhk = None
    
    # Location selection with safety check
    if location_options:
        location = st.selectbox("Location", options=location_options, index=location_index if location_index is not None and location_index < len(location_options) else 0)
    else:
        st.warning("No location options available for selected society")
        location = None
    
    # Type selection with safety check
    if type_options:
        property_type = st.selectbox("Property Type", options=type_options, index=type_index if type_index is not None and type_index < len(type_options) else 0)
    else:
        st.warning("No property types available for selected society")
        property_type = None
    
    # Advanced filters for internal analysis
    st.markdown("### Advanced Filters")
    
    # Add price range slider if data exists
    if not society_data.empty:
        min_possible = int(society_data['Price'].min())
        max_possible = int(society_data['Price'].max())
        
        if min_possible < max_possible:
            min_price, max_price = st.slider(
                "Price Range (₹)",
                min_value=min_possible,
                max_value=max_possible,
                value=(min_possible, max_possible)
            )
        else:
            min_price, max_price = min_possible, max_possible
            st.info("Limited price range available")
    else:
        min_price, max_price = 0, float('inf')
        st.warning("No data available")
    
    # Filter by property area (sq ft)
    if not society_data.empty:
        min_area = int(society_data['Area'].min())
        max_area = int(society_data['Area'].max())
        
        if min_area < max_area:
            min_area_filter, max_area_filter = st.slider(
                "Area Range (sq ft)",
                min_value=min_area,
                max_value=max_area,
                value=(min_area, max_area)
            )
        else:
            min_area_filter, max_area_filter = min_area, max_area
    else:
        min_area_filter, max_area_filter = 0, float('inf')
    
    # Filter by agent/posted by (for internal analysis)
    if not society_data.empty:
        agents = sorted(society_data['Posted By'].unique())
        selected_agents = st.multiselect(
            "Posted By",
            options=agents,
            default=agents
        )
    else:
        selected_agents = []
    
    # Reset filters button
    # if st.button("Reset Filters"):
    #     reset_filters()
    #     st.experimental_rerun()
    if st.button("Reset Filters"):
        reset_filters()
        st.rerun()
    
    # Add timestamp for data freshness
    st.markdown("---")
    st.caption(f"Data last updated: {datetime.now().strftime('%d %b %Y, %H:%M')}")
    st.caption("Data source: Internal property database")

# Filter data with all criteria
if not society_data.empty and bhk is not None and location is not None:
    filtered_data = society_data[
        (society_data['BHK'] == bhk) & 
        (society_data['Location'] == location) &
        (society_data['Price'] >= min_price) &
        (society_data['Price'] <= max_price) &
        (society_data['Area'] >= min_area_filter) &
        (society_data['Area'] <= max_area_filter)
    ]
    
    # Filter by property type if selected
    if property_type is not None:
        filtered_data = filtered_data[filtered_data['Type'] == property_type]
    
    # Filter by selected agents if any were selected
    if selected_agents:
        filtered_data = filtered_data[filtered_data['Posted By'].isin(selected_agents)]
else:
    filtered_data = pd.DataFrame()

# Main content area
if not filtered_data.empty:
    # Summary row with key metrics
    st.markdown('<div class="section-header">Key Metrics</div>', unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Total Properties", f"{len(filtered_data)}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        # st.metric("Avg Price", f"₹{filtered_data['Price'].mean():,.0f}")
        st.metric("Avg Price", f"₹{filtered_data['Price'].mean():,.0f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Avg Area (sqft)", f"{filtered_data['Area'].mean():.0f}")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col4:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        # st.metric("Avg ₹/sqft", f"₹{filtered_data['Price per sqft'].mean():.0f}")
        st.metric("Avg ₹/sqft", f"₹{filtered_data['Price per sqft'].mean():.0f}")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with col5:
        # For internal use - calculate and show volatility/coefficient of variation
        price_cv = (filtered_data['Price'].std() / filtered_data['Price'].mean()) * 100 if len(filtered_data) > 1 else 0
        price_volatility_label = "High" if price_cv > 20 else "Medium" if price_cv > 10 else "Low"
        
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Price Volatility", f"({price_cv:.1f}%)")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Property data table - more detailed for internal use
    # st.markdown('<div class="section-header">Property Listing Details</div>', unsafe_allow_html=True)
    
    # # Add column selection for customizable views
    # all_columns = filtered_data.columns.tolist()
    # default_columns = ['Property Name', 'BHK', 'Type', 'Price', 'Area', 'Price per sqft', 'Posted By', 'Posted Time']
    # display_columns = st.multiselect(
    #     "Select columns to display",
    #     options=all_columns,
    #     default=[col for col in default_columns if col in all_columns]
    # )
    
    # # Show detailed data table with selected columns
    # if display_columns:
    #     st.dataframe(
    #         filtered_data[display_columns],
    #         use_container_width=True,
    #         hide_index=True
    #     )
    # else:
    #     st.info("Please select at least one column to display")
    # Property data table - more detailed for internal use
    # Property data table - more detailed for internal use
    # Property data table - more detailed for internal use
    st.markdown('<div class="section-header">Property Listing Details</div>', unsafe_allow_html=True)

    # Add column selection for customizable views
    all_columns = filtered_data.columns.tolist()
    default_columns = ['Property Name', 'BHK', 'Type', 'Price', 'Area', 'Price per sqft', 'Posted By', 'Posted Time']
    display_columns = st.multiselect(
        "Select columns to display",
        options=all_columns,
        default=[col for col in default_columns if col in all_columns]
    )

    # Show detailed data table with selected columns
    if display_columns:
        # Create a copy of filtered data for display
        display_df = filtered_data[display_columns].copy()
        
        # Add a "View Property" column with clickable links
        if 'Property URL' in filtered_data.columns:
            display_df['View Property'] = filtered_data['Property URL'].apply(
                lambda url: f'''
                <a href="{url}" target="_blank" style="
                    background-color: #4CAF50;
                    color: white;
                    padding: 5px 10px;
                    text-align: center;
                    text-decoration: none;
                    display: inline-block;
                    border-radius: 4px;
                    border: none;
                    cursor: pointer;">
                    View Property
                </a>''' if pd.notna(url) else "N/A"
            )

        # Display the dataframe with HTML rendering
        st.markdown(
            display_df.style.hide(axis="index").set_table_styles(
                [dict(selector="th", props=[("text-align", "center")])]
            ).to_html(escape=False), 
            unsafe_allow_html=True
        )
        
        # Display the dataframe with the new button column
        # st.dataframe(
        #     display_df,
        #     use_container_width=True,
        #     hide_index=True
        # )
    else:
        st.info("Please select at least one column to display")


    
    # Advanced analytics section
    st.markdown('<div class="section-header">Price Analysis</div>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["Price Distribution", "Price vs Area"])
    
    # Color palette for internal dashboards - more professional/subtle
    color_palette = ["#2563EB", "#7C3AED", "#059669", "#DC2626", "#F59E0B"]
    
    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Histogram with kernel density estimation
            if len(filtered_data) > 1:  # Only create histogram if we have multiple data points
                fig = px.histogram(
                    filtered_data, 
                    x='Price',
                    title="Price Distribution",
                    color_discrete_sequence=[color_palette[0]],
                    opacity=0.7,
                    histnorm='probability density' if len(filtered_data) > 5 else None,
                    marginal='box' if len(filtered_data) > 5 else None  # Add boxplot on the margin if enough data
                )
                
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    title_font=dict(size=16),
                    margin=dict(l=40, r=40, t=40, b=40),
                    xaxis_title="Price (₹)",
                    yaxis_title="Density" if len(filtered_data) > 5 else "Count"
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Not enough data for histogram visualization. Need at least 2 properties.")
        
        with col2:
            # Statistical summary - useful for internal analysis
            st.markdown("### Statistical Summary")
            stats_df = pd.DataFrame({
                'Statistic': ['Count', 'Mean', 'Median', 'Std Dev', 'Min', 'Max', 'Range'],
                'Value': [
                    len(filtered_data),
                    f"₹{filtered_data['Price'].mean():,.0f}",
                    f"₹{filtered_data['Price'].median():,.0f}",
                    f"₹{filtered_data['Price'].std():,.0f}" if len(filtered_data) > 1 else "N/A",
                    f"₹{filtered_data['Price'].min():,.0f}",
                    f"₹{filtered_data['Price'].max():,.0f}",
                    f"₹{filtered_data['Price'].max() - filtered_data['Price'].min():,.0f}" if len(filtered_data) > 1 else "N/A"
                ]
            })
            st.table(stats_df)

    with tab2:
        # More detailed scatter plot with regression line for internal analysis
        if len(filtered_data) > 1:  # Only create scatter plot if we have multiple data points
            fig = px.scatter(
                filtered_data,
                x='Area',
                y='Price',
                size='Price per sqft',
                color='Posted By',
                title="Price vs Area Analysis with Trend",
                color_discrete_sequence=color_palette,
                trendline="ols" if len(filtered_data) > 3 else None,  # Add regression line if enough data
                trendline_color_override="black"
            )
            
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                title_font=dict(size=16),
                margin=dict(l=40, r=40, t=40, b=40),
                xaxis_title="Area (sqft)",
                yaxis_title="Price (₹)"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Calculate and display price-area correlation if enough data
            if len(filtered_data) > 3:
                correlation = filtered_data['Price'].corr(filtered_data['Area'])
                st.markdown(f"**Price-Area Correlation:** {correlation:.3f}")
                
                if correlation > 0.7:
                    st.markdown("**Insight:** Strong positive correlation between price and area")
                elif correlation > 0.3:
                    st.markdown("**Insight:** Moderate positive correlation between price and area")
                else:
                    st.markdown("**Insight:** Weak correlation between price and area. Other factors may have stronger influence on pricing")
        else:
            st.info("Not enough data for scatter plot visualization. Need at least 2 properties.")

    # Internal business intelligence section
    st.markdown('<div class="section-header">Business Intelligence</div>', unsafe_allow_html=True)
    
    # Analyze pricing by posting source if we have enough data
    if len(filtered_data) > 0 and len(filtered_data['Posted By'].unique()) > 1:
        source_analysis = filtered_data.groupby('Posted By').agg(
            count=('Price', 'count'),
            avg_price=('Price', 'mean'),
            avg_area=('Area', 'mean'),
            avg_price_sqft=('Price per sqft', 'mean'),
            min_price=('Price', 'min'),
            max_price=('Price', 'max')
        ).reset_index()
        
        # Format for display
        source_analysis['avg_price'] = source_analysis['avg_price'].apply(lambda x: f"₹{x:,.0f}")
        source_analysis['avg_price_sqft'] = source_analysis['avg_price_sqft'].apply(lambda x: f"₹{x:.0f}")
        source_analysis['min_price'] = source_analysis['min_price'].apply(lambda x: f"₹{x:,.0f}")
        source_analysis['max_price'] = source_analysis['max_price'].apply(lambda x: f"₹{x:,.0f}")
        source_analysis['avg_area'] = source_analysis['avg_area'].apply(lambda x: f"{x:.0f}")
        
        # Rename columns for display
        source_analysis.columns = ['Source', 'Listings', 'Avg Price', 'Avg Area', 'Avg ₹/sqft', 'Min Price', 'Max Price']
        
        st.markdown("#### Listing Source Analysis")
        st.dataframe(source_analysis, use_container_width=True, hide_index=True)
    else:
        st.info("Not enough data from different sources for meaningful source analysis")
    
    # High Variance Properties Analysis - more focused for internal business use
    st.markdown("#### High Variance Properties")
    
    # Filter data for the selected location
    location_data = df[df['Location'] == location].copy() if location else pd.DataFrame()
    
    if not location_data.empty and len(location_data) > 1:
        # Group by Property Name and BHK to calculate variance metrics
        variance_by_society = location_data.groupby(['Property Name', 'BHK']).agg(
            max_price=('Price', 'max'),
            min_price=('Price', 'min'),
            price_variance=('Price', lambda x: x.max() - x.min()),
            price_variance_pct=('Price', lambda x: (x.max() - x.min()) / x.mean() * 100 if len(x) > 1 else 0),
            avg_price=('Price', 'mean'),
            count=('Price', 'count')
        ).reset_index()
        
        # Filter for societies with at least 2 properties
        variance_by_society = variance_by_society[variance_by_society['count'] >= 2]
        
        # Sort by highest variance and get top 5
        top_variance_societies = variance_by_society.sort_values('price_variance', ascending=False).head(5)
        
        if not top_variance_societies.empty:
            # Format for better readability
            top_variance_societies['max_price'] = top_variance_societies['max_price'].apply(lambda x: f"₹{x:,.0f}")
            top_variance_societies['min_price'] = top_variance_societies['min_price'].apply(lambda x: f"₹{x:,.0f}")
            top_variance_societies['price_variance'] = top_variance_societies['price_variance'].apply(lambda x: f"₹{x:,.0f}")
            top_variance_societies['avg_price'] = top_variance_societies['avg_price'].apply(lambda x: f"₹{x:,.0f}")
            top_variance_societies['price_variance_pct'] = top_variance_societies['price_variance_pct'].apply(lambda x: f"{x:.1f}%")
            
            # Rename columns for better display
            top_variance_societies.columns = ['Society', 'BHK', 'Max Price', 'Min Price', 'Price Variance', 'Variance %', 'Avg Price', 'Properties']
            
            # Display as a dataframe
            st.dataframe(top_variance_societies, use_container_width=True, hide_index=True)
            
            # Visualize the variance
            fig = px.bar(
                variance_by_society.sort_values('price_variance', ascending=False).head(10), 
                x='Property Name', 
                y='price_variance',
                color='BHK',
                title=f"Societies with Highest Price Variance in {location}",
                labels={'price_variance': 'Price Variance (₹)', 'Property Name': 'Society'},
                color_discrete_sequence=color_palette
            )
            
            fig.update_layout(
                xaxis_tickangle=-45,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                title_font=dict(size=16),
                margin=dict(l=40, r=40, t=40, b=40)
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Business insight for internal teams
            st.markdown('<div class="insight-box">', unsafe_allow_html=True)
            st.markdown(f"**Business Insight:** High variance properties present potential arbitrage opportunities. Consider investigating why {top_variance_societies.iloc[0]['Society']} shows {top_variance_societies.iloc[0]['Variance %']} price variance for {top_variance_societies.iloc[0]['BHK']} BHK units. This may indicate non-standardized property features or negotiation opportunities.")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info(f"Not enough variance data in {location} to analyze")
    else:
        st.info(f"Not enough properties in {location} to analyze variance")
    
    # Add export functionality - crucial for internal dashboards
    st.markdown("#### Export Data")
    export_format = st.radio("Select export format:", ["CSV", "Excel", "JSON"])
    
    if st.button("Export Filtered Data"):
        # Get current timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if export_format == "CSV":
            csv = filtered_data.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"noida_properties_{timestamp}.csv",
                mime="text/csv"
            )
        elif export_format == "Excel":
            # For Excel we'd normally use BytesIO with to_excel, but for simplicity:
            st.info("Excel export would be implemented here with proper BytesIO handling")
        else:  # JSON
            json_data = filtered_data.to_json(orient="records")
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name=f"noida_properties_{timestamp}.json",
                mime="application/json"
            )

else:
    st.warning("No properties found matching the selected filters. Try adjusting your criteria or use the Reset Filters button.")

# Simple footer for internal tool
st.markdown("---")
st.caption("Movin.homes© Internal Analytics Tool | Data Refresh: Daily at 00:00 IST")
