"""
UI utilities for the dashboard.
"""
import os
import streamlit as st


def render_download_button(**kwargs):
    """
    Renders a download button for the ALGORITHM.pdf guide.
    This should be placed in the header area of pages.
    
    Args:
        **kwargs: Additional arguments passed to st.download_button
    """
    # Path to the PDF in the root directory
    # Assumes dashboard/utils/ui.py -> ../../ALGORITHM.pdf
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up 2 levels: utils -> dashboard -> root
    root_dir = os.path.dirname(os.path.dirname(current_dir))
    pdf_path = os.path.join(root_dir, "ALGORITHM.pdf")
    
    # Check if file exists to prevent errors
    if not os.path.exists(pdf_path):
        # Fallback for different CWD (e.g. running from root)
        pdf_path = "ALGORITHM.pdf"
        if not os.path.exists(pdf_path):
            st.error(f"Algorithm guide not found at {pdf_path}")
            return

    try:
        with open(pdf_path, "rb") as f:
            pdf_data = f.read()
            
        st.download_button(
            label="Algorithm Guide",
            data=pdf_data,
            file_name="ALGORITHM.pdf",
            mime="application/pdf",
            help="Download the detailed algorithm documentation PDF",
            key="btn_download_algo_guide",
            type="primary",
            **kwargs
        )
    except Exception as e:
        st.error(f"Error loading guide: {e}")
