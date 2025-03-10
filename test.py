import streamlit as st
import pandas as pd
import plotly.express as px

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
    
    # Create a simple visualization if there's data
    if len(df) > 0:
        st.subheader("Sample Visualization")
        
        # Check if there are numeric columns
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
        
        if numeric_cols:
            # If there are numeric columns, create a bar chart of one of them
            fig = px.bar(df, x=df.columns[0], y=numeric_cols[0], title=f"{numeric_cols[0]} by {df.columns[0]}")
            st.plotly_chart(fig, use_container_width=True)
        else:
            # If no numeric columns, show counts of unique values in the first column
            col_name = df.columns[0]
            counts = df[col_name].value_counts().reset_index()
            counts.columns = [col_name, "Count"]
            fig = px.bar(counts, x=col_name, y="Count", title=f"Counts of {col_name}")
            st.plotly_chart(fig, use_container_width=True)

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
