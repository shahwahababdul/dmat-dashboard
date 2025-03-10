import streamlit as st
import sys

st.title("Streamlit Function & Data Loading Test")

# Test pandas
st.subheader("Testing pandas")
try:
    import pandas as pd
    st.success("✅ Successfully imported pandas")
    st.info(f"pandas version: {pd.__version__}")
except ImportError as e:
    st.error(f"❌ Failed to import pandas: {e}")

# Test numpy
st.subheader("Testing numpy")
try:
    import numpy as np
    st.success("✅ Successfully imported numpy")
    st.info(f"numpy version: {np.__version__}")
except ImportError as e:
    st.error(f"❌ Failed to import numpy: {e}")

# Test loading data from Google Sheets directly with pandas
st.subheader("Testing Google Sheets Data Loading")
try:
    # Set the spreadsheet details
    sheet_id = "11FoqJicHt3BGpzAmBnLi1FQFN-oeTxR_WGKszARDcR4"
    sheet_name = "Sheet1"
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    
    # Try to load the data
    st.info("Attempting to load data from Google Sheets...")
    df = pd.read_csv(url)
    
    # Display success and show the data
    st.success(f"✅ Successfully loaded data from Google Sheets! Found {len(df)} rows.")
    st.dataframe(df.head())
    
    # If we successfully loaded data, try to visualize it with plotly
    st.subheader("Testing st.plotly_chart() with Google Sheets data")
    try:
        import plotly.express as px
        
        # Get numeric columns if any
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        if numeric_cols and len(df) > 0:
            # Create a simple bar chart of first numeric column
            if len(df) > 20:
                display_df = df.head(20)  # Limit to first 20 rows if many
            else:
                display_df = df
                
            fig = px.bar(display_df, x=df.columns[0], y=numeric_cols[0], 
                         title=f"{numeric_cols[0]} by {df.columns[0]}")
            st.plotly_chart(fig)
            st.success("✅ st.plotly_chart() works with the data!")
        else:
            st.warning("No numeric columns found for plotly visualization")
            
    except Exception as e:
        st.error(f"❌ st.plotly_chart() failed: {e}")
    
    # Try to visualize with matplotlib
    st.subheader("Testing st.pyplot() with Google Sheets data")
    try:
        import matplotlib.pyplot as plt
        
        if numeric_cols and len(df) > 0:
            # Create a simple matplotlib figure
            fig, ax = plt.subplots(figsize=(10, 6))
            if len(df) > 20:
                display_df = df.head(20)
            else:
                display_df = df
                
            ax.bar(display_df[df.columns[0]].astype(str), display_df[numeric_cols[0]])
            ax.set_title(f"{numeric_cols[0]} by {df.columns[0]}")
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            st.pyplot(fig)
            st.success("✅ st.pyplot() works with the data!")
        else:
            st.warning("No numeric columns found for matplotlib visualization")
            
    except Exception as e:
        st.error(f"❌ st.pyplot() failed: {e}")
        
except Exception as e:
    st.error(f"❌ Failed to load data from Google Sheets: {e}")
    
    # Provide troubleshooting information
    st.warning("""
    If you're seeing an error, check the following:
    
    1. Make sure the Google Sheet is shared with "Anyone with the link can view" permissions
    2. Verify the spreadsheet ID is correct
    3. Ensure the sheet name is correct (case sensitive)
    """)

# Show system information
st.subheader("System Information")
st.info(f"Python version: {sys.version}")
