import streamlit as st
import sys

st.write(f"Python version: {sys.version}")

try:
    import gspread
    st.success("Successfully imported gspread")
except ImportError as e:
    st.error(f"Failed to import gspread: {e}")

try:
    import pkg_resources
    installed_packages = [f"{pkg.key}=={pkg.version}" for pkg in pkg_resources.working_set]
    st.write("Installed packages:")
    st.write(installed_packages)
except Exception as e:
    st.write(f"Error listing packages: {e}")
