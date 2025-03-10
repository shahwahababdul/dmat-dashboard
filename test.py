import streamlit as st

st.title("Library Import Test")

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

# Test matplotlib
st.subheader("Testing matplotlib")
try:
    import matplotlib.pyplot as plt
    st.success("✅ Successfully imported matplotlib")
    st.info(f"matplotlib version: {plt.__version__}")
except ImportError as e:
    st.error(f"❌ Failed to import matplotlib: {e}")

# Test plotly
st.subheader("Testing plotly")
try:
    import plotly.express as px
    st.success("✅ Successfully imported plotly")
    st.info(f"plotly version: {px.__version__}")
except ImportError as e:
    st.error(f"❌ Failed to import plotly: {e}")

# Test gspread
st.subheader("Testing gspread")
try:
    import gspread
    st.success("✅ Successfully imported gspread")
    st.info(f"gspread version: {gspread.__version__}")
except ImportError as e:
    st.error(f"❌ Failed to import gspread: {e}")

# Show system information
st.subheader("System Information")
import sys
st.info(f"Python version: {sys.version}")
