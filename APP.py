"""
Egyptian ID Card OCR – Streamlit Entry Point
=============================================
Run with:  streamlit run APP.py
"""

import streamlit as st

from config.settings import PAGE_TITLE, PAGE_ICON, PAGE_LAYOUT
from pages import home, guide

# ── Page config 
st.set_page_config(page_title=PAGE_TITLE, page_icon=PAGE_ICON, layout=PAGE_LAYOUT)

# ── Session state 
if "current_tab" not in st.session_state:
    st.session_state.current_tab = "Home"

# ── Sidebar navigation 
tabs = ["Home", "Guide"]
st.session_state.current_tab = st.sidebar.radio("Navigation", tabs)

# ── Route to the selected page 
if st.session_state.current_tab == "Home":
    home.render()
elif st.session_state.current_tab == "Guide":
    guide.render()
