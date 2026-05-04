"""
Guide / Documentation page.
"""

import streamlit as st


def render():
    """Render the Guide tab."""
    st.title("How to use our application 📖")
    st.write("""
    ## Project Overview:
    This application processes Egyptian ID cards to extract key information, including names, addresses, and national IDs.  
    It also decodes the national ID to provide additional details like birth date, governorate, and gender.

    ## Features:
    - **ID Card Detection**: Automatically detects and crops the ID card from the image.
    - **Field Detection**: Identifies key fields such as first name, last name, address, and serial number.
    - **Text Extraction**: Extracts Arabic and English text using EasyOCR.
    - **National ID Decoding**: Decodes the ID to extract:
        - Birth Date
        - Governorate
        - Gender
        - Birthplace
        - Location
        - Nationality

    ## How It Works:
    1. **Upload an Image**: Upload an image of the ID card using the sidebar.
    2. **Detection and Extraction**:
        - YOLO models detect the ID card and its fields.
        - EasyOCR extracts text from the identified fields.
    3. **Result Presentation**:
        - Outputs extracted information such as full name, address, and national ID details.
    4. **ID Decoding**:
        - Decodes the national ID to reveal demographic details.

    ## Steps to Use:
    - Get your image ready.
    - Click on Home.
    - Upload an Egyptian ID card image.
    - View the extracted information and analysis.
        
    ## I HOPE YOU ENJOY THE EXPERIENCE 💖
    """)
