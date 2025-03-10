import streamlit as st
import sys

st.write(f"Python version: {sys.version}")

# Try importing various packages
try:
    import gspread
    st.success("Successfully imported gspread")
except ImportError as e:
    st.error(f"Failed to import gspread: {e}")

try:
    import pandas
    st.success("Successfully imported pandas")
except ImportError as e:
    st.error(f"Failed to import pandas: {e}")

try:
    import plotly
    st.success("Successfully imported plotly")
except ImportError as e:
    st.error(f"Failed to import plotly: {e}")

try:
    import numpy
    st.success("Successfully imported numpy")
except ImportError as e:
    st.error(f"Failed to import numpy: {e}")

try:
    import google.auth
    st.success("Successfully imported google.auth")
except ImportError as e:
    st.error(f"Failed to import google.auth: {e}")
