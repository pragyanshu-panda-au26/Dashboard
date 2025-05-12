import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime

# Initialize session state for filter reset
if 'reset_clicked' not in st.session_state:
    st.session_state.reset_clicked = False

# Set page configuration
st.set_page_config(
    page_title="Movin Property Analytics",
    page_icon="🏠",
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
    
    .dataframe {
        font-size: 12px !important;
    }
    
    .dataframe th {
        background-color: #E5E7EB !important;
        color: #1F2937 !important;
        font-weight: 600 !important;
    }
    
    .stSelectbox > div > div {
        padding-top: 0px !important;
        padding-bottom: 0px !important;
    }
    """
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)

local_css()

def format_inr_lakh_cr(amount):
    try:
        amount = float(amount)
        if amount >= 1e7:
            return f"₹{amount/1e7:.2f} Cr"
        elif amount >= 1e5:
            return f"₹{amount/1e5:.2f} Lakhs"
        else:
            return f"₹{amount:,.0f}"
    except Exception:
        return "N/A"

def reset_filters():
    st.session_state.reset_clicked = True

@st.cache_data
def load_data():
    try:
        df = pd.read_csv("../merged_property_data_may2025.csv")
        df['Area'] = df['Area'].str.replace('[^\d.]', '', regex=True).astype(float)
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
        df = df.dropna(subset=['Price'])
        df['Price'] = df['Price'].astype('int64')
        df['Price per sqft'] = pd.to_numeric(df['Price_Per_Sqft'], errors='coerce')
        mask = df['Price per sqft'].isna()
        if any(mask):
            df.loc[mask, 'Price per sqft'] = df.loc[mask, 'Price'] / df.loc[mask, 'Area']
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

df = load_data()

# Dashboard Header
st.markdown("<h2>Noida Property Analytics Dashboard</h2>", unsafe_allow_html=True)

# Sidebar Filters
with st.sidebar:
    st.markdown("## Filters")
    st.markdown("### Property Filters")
    
    if st.session_state.reset_clicked:
        society_index = 0
        st.session_state.reset_clicked = False
    else:
        society_index = None

    society = st.selectbox("Society", options=sorted(df['Property Name'].unique()), index=society_index)
    society_data = df[df['Property Name'] == society]

    # Source Filter (Added)
    if not society_data.empty:
        source_options = sorted(society_data['Source'].dropna().unique())
        selected_sources = st.multiselect("Source", options=source_options, default=source_options)
    else:
        selected_sources = []

    # Existing filters
    bhk_options = sorted(society_data['BHK'].unique()) if not society_data.empty else []
    if bhk_options:
        bhk = st.selectbox("BHK Type", options=bhk_options, index=0)
    else:
        bhk = None

    location_options = sorted(society_data['Location'].unique()) if not society_data.empty else []
    if location_options:
        location = st.selectbox("Location", options=location_options, index=0)
    else:
        location = None

    # Price and Area Filters
    if not society_data.empty:
        min_price, max_price = st.slider("Price Range (₹)", 
            min_value=int(society_data['Price'].min()), 
            max_value=int(society_data['Price'].max()),
            value=(int(society_data['Price'].min()), int(society_data['Price'].max())))
        
        min_area_filter, max_area_filter = st.slider("Area Range (sq ft)", 
            min_value=int(society_data['Area'].min()),
            max_value=int(society_data['Area'].max()),
            value=(int(society_data['Area'].min()), int(society_data['Area'].max())))
    else:
        min_price, max_price = 0, 0
        min_area_filter, max_area_filter = 0, 0

    if st.button("Reset Filters"):
        reset_filters()
        st.rerun()

# Data Filtering
if not society_data.empty and bhk and location:
    filtered_data = society_data[
        (society_data['BHK'] == bhk) & 
        (society_data['Location'] == location) &
        (society_data['Price'] >= min_price) &
        (society_data['Price'] <= max_price) &
        (society_data['Area'] >= min_area_filter) &
        (society_data['Area'] <= max_area_filter)
    ]
    
    # Apply Source Filter (Added)
    if selected_sources:
        filtered_data = filtered_data[filtered_data['Source'].isin(selected_sources)]
else:
    filtered_data = pd.DataFrame()

# Main Content
if not filtered_data.empty:
    # Metrics and Visualizations (Same as before)
    st.markdown('<div class="section-header">Key Metrics</div>', unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)


    with col1:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        st.metric("Total Properties", f"{len(filtered_data)}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-container">', unsafe_allow_html=True)
        avg_price = filtered_data['Price'].mean()
        st.metric("Avg Price", format_inr_lakh_cr(avg_price))
        # st.metric("Avg Price", f"₹{filtered_data['Price'].mean():,.0f}")
        # st.metric("Avg Price", f"₹{filtered_data['Price'].mean():,.0f}")
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
        st.metric("Price Volatility", f"{price_volatility_label} ({price_cv:.1f}%)")
        st.markdown('</div>', unsafe_allow_html=True)



if 'Property URL' in filtered_data.columns and 'Source' in filtered_data.columns:
    source_idx = filtered_data.columns.get_loc('Source')
    filtered_data.insert(
        source_idx,
        'View Property',
        filtered_data['Property URL'].apply(
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
    )

    # Property Table with Source Column
    st.markdown('<div class="section-header">Property Listing Details</div>', unsafe_allow_html=True)
    default_columns = ['Property Name', 'BHK', 'Type', 'Price', 'Area', 'Price per sqft', 'Posted By', 'Posted Time','View Property', 'Source']
    # display_columns = st.multiselect("Select columns", options=filtered_data.columns.tolist(), default=default_columns)
    display_columns = st.multiselect(
    "Select columns",
    options=filtered_data.columns.tolist(),
    default=[col for col in default_columns if col in filtered_data.columns]
    )


    if display_columns:
        
        display_df = filtered_data[display_columns].copy()


        if 'Price' in display_df.columns:
            display_df['Price'] = display_df['Price'].apply(format_inr_lakh_cr)

        
        # display_columns = [col for col in default_columns if col in display_df.columns]
        # display_df = display_df[display_columns]
        
        st.markdown(display_df.style.hide(axis="index").to_html(escape=False), unsafe_allow_html=True)
    

            # --- Price Analysis ---
    st.subheader("📊 Price Analysis")
    tab1, tab2 = st.tabs(["Distribution", "Comparisons"])

    with tab1:
        fig = px.histogram(
            filtered_data,
            x='Price',
            title="Price Distribution",
            color_discrete_sequence=['#FF4B4B']
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        fig = px.scatter(
            filtered_data,
            x='Area',
            y='Price',
            size='Price per sqft',
            color='Posted By',
            title="Price vs Area Analysis"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # --- High Variance Properties ---
st.subheader("📈 High Variance Properties")
if location is not None and not df.empty:
    location_data = df[df['Location'] == location].copy()
    if not location_data.empty:
        variance_by_society = location_data.groupby(['Property Name', 'BHK']).agg(
            max_price=('Price', 'max'),
            min_price=('Price', 'min'),
            price_variance=('Price', lambda x: x.max() - x.min()),
            avg_price=('Price', 'mean'),
            count=('Price', 'count')
        ).reset_index()
        variance_by_society = variance_by_society[variance_by_society['count'] >= 2]
        top_variance_societies = variance_by_society.sort_values('price_variance', ascending=False).head(5)
        if not top_variance_societies.empty:
            top_variance_societies['max_price'] = top_variance_societies['max_price'].apply(format_inr_lakh_cr)
            top_variance_societies['min_price'] = top_variance_societies['min_price'].apply(format_inr_lakh_cr)
            top_variance_societies['price_variance'] = top_variance_societies['price_variance'].apply(format_inr_lakh_cr)
            top_variance_societies['avg_price'] = top_variance_societies['avg_price'].apply(format_inr_lakh_cr)
            top_variance_societies.columns = ['Society', 'BHK', 'Max Price', 'Min Price', 'Price Variance', 'Avg Price', 'Properties']
            st.dataframe(top_variance_societies, use_container_width=True)
            fig = px.bar(
                top_variance_societies,
                x='Society',
                y='Price Variance',
                color='BHK',
                title=f"Societies with Highest Price Variance in {location}",
                text='Price Variance',
                barmode='group'
            )
            fig.update_traces(texttemplate='%{text}', textposition='outside')
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
            highest = top_variance_societies.iloc[0]
            st.info(f"💡 **Insight**: {highest['Society']} shows the highest price variance for {highest['BHK']} BHK properties in {location}. This could indicate negotiation opportunities or major differences in features.")
        else:
            st.info(f"Not enough data to calculate meaningful variance in {location}.")
    else:
        st.warning(f"No properties found in {location} to analyze variance.")



    # ... (rest of your existing analysis sections)

else:
    st.warning("No properties found matching the selected filters")

st.markdown("---")
st.caption("Movin.homes© Internal Analytics Tool | Data Refresh: Daily at 00:00 IST")
