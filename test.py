import streamlit as st
import sys
import subprocess
import pkg_resources

# Check if gspread is installed
required_packages = ['gspread', 'google-auth']
installed_packages = [pkg.key for pkg in pkg_resources.working_set]

missing_packages = [pkg for pkg in required_packages if pkg not in installed_packages]

if missing_packages:
    st.warning(f"Attempting to install missing packages: {missing_packages}")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade"] + missing_packages)
        st.success("Packages installed successfully!")
        # Restart the script to use the newly installed packages
        import importlib
        importlib.invalidate_caches()
    except Exception as e:
        st.error(f"Failed to install packages: {e}")

# Now try to import gspread
try:
    import gspread
    st.success("Successfully imported gspread")
except ImportError as e:
    st.error(f"Failed to import gspread: {e}")

st.write(f"Python version: {sys.version}")

try:
    installed_packages = [f"{pkg.key}=={pkg.version}" for pkg in pkg_resources.working_set]
    st.write("Installed packages:")
    st.write(installed_packages)
except Exception as e:
    st.write(f"Error listing packages: {e}")
