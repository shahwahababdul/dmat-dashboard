import streamlit as st
import pandas as pd

# Page configuration
st.set_page_config(layout="wide", page_title="Google Sheet Test")

st.title("Google Sheets Direct Access Test")

# Set the spreadsheet URL
sheet_id = "11FoqJicHt3BGpzAmBnLi1FQFN-oeTxR_WGKszARDcR4"
sheet_name = "Sheet1"
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

# Display status
st.info("Attempting to connect to Google Sheets...")

try:
    # Read the data
    df = pd.read_csv(url)
    
    # Show success message
    st.success(f"Successfully loaded data from Google Sheets! Found {len(df)} rows.")
    
    # Display the first few rows of the dataframe
    st.subheader("Data Preview")
    st.dataframe(df.head())
    
    # Show column information
    st.subheader("Column Information")
    st.write(f"Columns found: {', '.join(df.columns)}")
    
    # Use Streamlit's built-in visualization capabilities
    st.subheader("Data Visualization")
    
    # Check if there are numeric columns
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    
    if numeric_cols:
        # Display a bar chart using Streamlit's built-in chart function
        st.subheader(f"Bar Chart of {numeric_cols[0]}")
        st.bar_chart(df[numeric_cols[0]])
        
        # If we have multiple numeric columns, show a line chart too
        if len(numeric_cols) > 1:
            st.subheader(f"Line Chart Comparing Numeric Values")
            chart_data = df[numeric_cols].head(20)  # Limit to first 20 rows for visibility
            st.line_chart(chart_data)
    
    # Display statistics
    st.subheader("Data Statistics")
    if numeric_cols:
        st.write(df[numeric_cols].describe())
    
    # Show unique values for categorical columns
    cat_cols = [col for col in df.columns if col not in numeric_cols]
    if cat_cols:
        st.subheader("Categorical Columns Summary")
        for col in cat_cols[:3]:  # Limit to first 3 categorical columns
            st.write(f"Unique values in {col}:")
            value_counts = df[col].value_counts().head(10)  # Show top 10 values
            st.write(value_counts)

except Exception as e:
    st.error(f"Error accessing the Google Sheet: {e}")
    
    # Provide troubleshooting information
    st.subheader("Troubleshooting")
    st.markdown("""
    If you're seeing an error, check the following:
    
    1. Make sure the Google Sheet is shared with "Anyone with the link can view" permissions
    2. Verify the spreadsheet ID is correct
    3. Ensure the sheet name is correct (case sensitive)
    """)
