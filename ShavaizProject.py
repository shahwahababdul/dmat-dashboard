import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from io import BytesIO
from matplotlib.backends.backend_pdf import PdfPages
import datetime
from google.oauth2.service_account import Credentials
import PIL.Image
from plotly.io import write_image
import numpy as np
try:
    import gspread
    st.write("Successfully imported gspread")
except ImportError:
    st.error("Failed to import gspread")


# Add debugging information here
import sys
st.write(f"Python version: {sys.version}")
st.write(f"Installed packages:")
try:
    import pkg_resources
    installed_packages = [f"{pkg.key}=={pkg.version}" for pkg in pkg_resources.working_set]
    st.write(installed_packages)
except Exception as e:
    st.write(f"Error listing packages: {e}")

# Page configuration
st.set_page_config(layout="wide")  # Enable full page width layout

# Custom Background Color for Live Dashboard
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #7F7FD5, #91EAE4);
        background-attachment: fixed;
        height: 100vh;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Apply Custom Styling
st.markdown(
    """
    <style>
    .main-title {
        color: #003366 !important;
        font-size: 28px;
        font-weight: bold;
        text-align: center;
        margin-top: 30px;
        font-family: 'Poppins', sans-serif;
    }
    .sub-title {
        color: black !important;
        font-size: 22px;
        font-weight: bold;
        text-align: center;
        font-family: 'Poppins', sans-serif;
    }
    .stSidebar {
        background: linear-gradient(135deg, #83a4d4, #b6fbff);
        background-attachment: fixed;
        height: 100%;
        padding: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# Function to save Plotly figures as images and add them to a PDF
def generate_pdf(figures, df_filtered):
    pdf_buffer = BytesIO()

    with PdfPages(pdf_buffer) as pdf:
        for fig in figures:
            # Set the figure background to white to avoid black background
            fig.update_layout(plot_bgcolor='white', paper_bgcolor='white')

            # Save the Plotly figure as a PNG image to a BytesIO buffer
            img_buf = BytesIO()
            write_image(fig, img_buf, format="png", scale=3)  # Increase scale for better resolution
            img_buf.seek(0)  # Reset buffer position to the beginning

            # Open the image using PIL (Pillow)
            img = PIL.Image.open(img_buf)
            img = img.convert("RGB")  # Convert image to RGB (to avoid transparency issues)

            # Convert image to an array that can be used by matplotlib
            img_array = np.array(img)

            # Use matplotlib to read the image and add it to the PDF
            fig_matplotlib, ax = plt.subplots()
            ax.imshow(img_array)
            ax.axis('off')  # Hide axes
            pdf.savefig(fig_matplotlib, bbox_inches='tight', dpi=300)
            plt.close(fig_matplotlib)  # Close the matplotlib figure to avoid display issues

    pdf_buffer.seek(0)  # Reset buffer position to the beginning
    return pdf_buffer


try:
    # First try to get credentials from streamlit secrets (for cloud deployment)
    import json
    service_account_info = st.secrets["gcp_service_account"]
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
    client = gspread.authorize(creds)
except Exception as e:
    # Display error about credentials
    st.error(f"Failed to access Google credentials: {e}")
    st.info("Please make sure you have set up your Google credentials in Streamlit secrets.")
    st.stop()  # Stop execution if credentials fail

    # Google Sheet details
    spreadsheet_id = "11FoqJicHt3BGpzAmBnLi1FQFN-oeTxR_WGKszARDcR4"
    worksheet_name = "Sheet1"

    sheet = client.open_by_key(spreadsheet_id).worksheet(worksheet_name)
    data = sheet.get_all_records(
        expected_headers=["Mode", "Type", "Escalation Date", "Domain", "Account name", "Case Category", "Escalated To"])

    # Convert to DataFrame
    df = pd.DataFrame(data)

    # Debug information - enable temporarily if you still have issues
    # st.write("Raw Data Sample:", df.head())
    # st.write("Column Names:", df.columns.tolist())

    # Normalize column names (case-insensitive)
    df.columns = [col.strip().lower() for col in df.columns]

    # Rename columns back to proper case for display (while keeping lowercase keys for access)
    column_mapping = {
        "mode": "Mode",
        "type": "Type",
        "escalation date": "Escalation Date",
        "domain": "Domain",
        "account name": "Account name",
        "case category": "Case Category",
        "escalated to": "Escalated To"
    }

    # Check for any unexpected column that might be causing the issue
    for col in df.columns:
        if col not in column_mapping:
            # If we find an unexpected column, either remove it or handle it
            df = df.drop(columns=[col])  # Remove unexpected columns

    # Rename first row as column headers if needed
    if df.iloc[0].tolist() == list(column_mapping.values()):
        df = df[1:].reset_index(drop=True)  # Drop the first row if it's a header

    # Rename columns for consistent access
    df = df.rename(columns=column_mapping)

    # Remove duplicate columns (keep first occurrence)
    df = df.loc[:, ~df.columns.duplicated()]

    # Clean up data to avoid PyArrow conversion issues
    # Replace empty strings with NaN for numeric columns
    df = df.apply(lambda x: x.replace('', pd.NA) if x.dtype == 'object' else x)

    # Convert 'Escalation Date' to datetime
    df["Escalation Date"] = pd.to_datetime(df["Escalation Date"], errors="coerce")

    # Cast columns to appropriate types explicitly
    for col in df.columns:
        if col != "Escalation Date":  # Skip already converted date column
            # Ensure all non-date columns are strings to avoid conversion issues
            df[col] = df[col].astype(str)

    # Sidebar Filters
    st.sidebar.header("Filters")

    # Case Category Dropdown
    case_categories = df["Case Category"].unique().tolist()
    # Convert any numeric values to strings before sorting
    case_categories = [str(category) for category in case_categories if str(category) != 'nan']
    case_categories = sorted(case_categories)
    selected_category = st.sidebar.selectbox("Search Case Category", ["All"] + case_categories)

    # Account Name Dropdown
    account_names = df["Account name"].unique().tolist()
    # Convert any numeric values to strings before sorting
    account_names = [str(name) for name in account_names if str(name) != 'nan']
    account_names = sorted(account_names)
    selected_account = st.sidebar.selectbox("Search Account Name", ["All"] + account_names)

    # Date Range Filter
    min_date = df["Escalation Date"].min().date() if not df["Escalation Date"].isna().all() else datetime.date.today()
    max_date = df["Escalation Date"].max().date() if not df["Escalation Date"].isna().all() else datetime.date.today()
    start_date = st.sidebar.date_input("Start Date", min_date)
    end_date = st.sidebar.date_input("End Date", max_date)

    # Apply Filters
    df_filtered = df.copy()

    # Apply date filter
    df_filtered = df_filtered[
        (df_filtered["Escalation Date"] >= pd.to_datetime(start_date)) &
        (df_filtered["Escalation Date"] <= pd.to_datetime(end_date))
        ]

    # Apply category filter
    if selected_category != "All":
        df_filtered = df_filtered[df_filtered["Case Category"].astype(str) == selected_category]

    # Apply account filter
    if selected_account != "All":
        df_filtered = df_filtered[df_filtered["Account name"].astype(str) == selected_account]

    # Dashboard Title
    st.markdown("<h1 class='main-title'>📊 DMAT - TA Escalations Dashboard</h1>", unsafe_allow_html=True)

    # KPIs
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="📌 Total Escalations", value=len(df_filtered))
    with col2:
        st.metric(label="🌐 Total Domains", value=df_filtered["Domain"].nunique())
    with col3:
        st.metric(label="📑 Total Escalation Categories", value=df_filtered["Case Category"].nunique())


    # Convert dataframe to use streamlit's display functions safely
    # This helps avoid Arrow serialization issues
    @st.cache_data
    def convert_df(df):
        # Force all columns to be string type for display purposes
        display_df = df.copy()
        for col in display_df.columns:
            if col == 'Escalation Date':
                # Format date for display
                display_df[col] = display_df[col].dt.strftime('%Y-%m-%d')
            else:
                # Ensure all other columns are strings
                display_df[col] = display_df[col].astype(str)
        return display_df


    # Display Table on Top
    st.markdown("<h2 class='sub-title'>Escalation Data</h2>", unsafe_allow_html=True)
    # Use the converted dataframe for display
    display_df = convert_df(df_filtered)
    st.dataframe(display_df)

    # Graphs in Horizontal Layout
    col1, col2 = st.columns(2)

    # Prepare data for visualizations
    category_counts = df_filtered["Case Category"].value_counts().reset_index()
    category_counts.columns = ["Case Category", "Count"]

    with col1:
        st.markdown("<h2 class='sub-title' style='white-space: nowrap;'>📌 Escalations by Case Category</h2>",
                    unsafe_allow_html=True)
        fig1 = px.bar(category_counts, x="Case Category", y="Count", text="Count", color="Case Category")
        fig1.update_layout(
            autosize=True,
            margin=dict(t=20, b=20, l=20, r=20),
            height=450
        )
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        st.markdown("<h2 class='sub-title'>📈 Escalation Trend Over Time</h2>", unsafe_allow_html=True)
        time_series = df_filtered.groupby(df_filtered["Escalation Date"].dt.date).size().reset_index(name="Count")
        time_series["Escalation Date"] = pd.to_datetime(time_series["Escalation Date"])
        fig2 = px.line(time_series, x="Escalation Date", y="Count", markers=True)
        fig2.update_layout(height=450, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig2, use_container_width=True, key="fig2")

    col4, col5 = st.columns(2)
    with col4:
        st.markdown("<h2 class='sub-title'>📌 Top 5 Most Escalated Categories</h2>", unsafe_allow_html=True)
        top5_categories = category_counts.nlargest(5, "Count")
        fig4 = px.bar(top5_categories, x="Case Category", y="Count", text="Count", color="Case Category")
        fig4.update_layout(height=400, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig4, use_container_width=True, key="fig4")

    with col5:
        st.markdown("<h2 class='sub-title'>Escalation Trends Across the Week</h2>", unsafe_allow_html=True)
        df_filtered['Day of Week'] = df_filtered['Escalation Date'].dt.day_name()
        day_counts = df_filtered['Day of Week'].value_counts().reset_index()
        day_counts.columns = ['Day of Week', 'Count']

        # Sort days of week in proper order
        days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        day_counts['Day of Week'] = pd.Categorical(day_counts['Day of Week'], categories=days_order, ordered=True)
        day_counts = day_counts.sort_values('Day of Week')

        fig5 = px.line(day_counts, x='Day of Week', y='Count', markers=True)
        fig5.update_layout(height=400, margin=dict(t=0, b=0, l=0, r=0))
        st.plotly_chart(fig5, use_container_width=True, key="fig5")

    col6, col7 = st.columns(2)
    with col6:
        st.markdown("<h2 class='sub-title'>Escalations by Mode</h2>", unsafe_allow_html=True)
        mode_counts = df_filtered['Mode'].value_counts().reset_index()
        mode_counts.columns = ['Mode', 'Count']
        mode_counts['Percentage'] = (mode_counts['Count'] / mode_counts['Count'].sum()) * 100
        mode_counts['Label'] = mode_counts['Mode'] + " (" + mode_counts['Count'].astype(str) + ")"
        fig6 = px.pie(mode_counts, names='Mode', values='Count', title='Escalations by Mode')
        fig6.update_traces(textinfo='label+value', hoverinfo='label+value', textposition='inside')
        fig6.update_layout(height=400)
        st.plotly_chart(fig6, use_container_width=True, key="fig6")

    with col7:
        st.markdown("<h2 class='sub-title'>Escalations by Domain</h2>", unsafe_allow_html=True)
        domain_counts = df_filtered['Domain'].value_counts().reset_index()
        domain_counts.columns = ['Domain', 'Count']
        fig7 = px.bar(domain_counts, x='Domain', y='Count', text='Count', color='Domain')
        fig7.update_layout(height=400)
        st.plotly_chart(fig7, use_container_width=True, key="fig7")

    # Escalation Distribution by Assignees
    st.markdown("<h2 class='sub-title'>🔹 Escalation Distribution by Assignees</h2>", unsafe_allow_html=True)
    assigned_counts = df_filtered["Escalated To"].value_counts().reset_index()
    assigned_counts.columns = ["Escalated To", "Count"]
    assigned_counts["Percentage"] = (assigned_counts["Count"] / assigned_counts["Count"].sum()) * 100
    fig3 = px.pie(assigned_counts, names="Escalated To", values="Count", title="Escalation Distribution", hole=0.3)
    fig3.update_traces(textinfo="label+percent+value", hoverinfo="label+value+percent", textposition="inside")
    fig3.update_layout(height=400)
    st.plotly_chart(fig3, use_container_width=True, key="fig3")

    # Generate and provide PDF Download
    figures = [fig1, fig2, fig3, fig4, fig5, fig6, fig7]
    pdf_file = generate_pdf(figures, df_filtered)
    st.download_button("Download Escalations Dashboard PDF", pdf_file, file_name="Escalations_Dashboard.pdf",
                       mime="application/pdf")

except gspread.exceptions.SpreadsheetNotFound:
    st.error("Error: The Google Sheet was not found. Check the spreadsheet ID and permissions.")
except Exception as e:
    st.error(f"An error occurred: {e}")
    st.exception(e)  # This will show the full traceback for debugging
