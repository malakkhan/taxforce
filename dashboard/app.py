"""
TaxForce Dashboard - Main Entry Point
A Streamlit-based tax compliance simulation dashboard.
"""
import streamlit as st
from pathlib import Path

# Page configuration - must be first
st.set_page_config(
    page_title="Tax Force",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load custom CSS
def load_css():
    css_path = Path(__file__).parent / "styles" / "main.css"
    if css_path.exists():
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Initialize session state
if "simulation_results" not in st.session_state:
    st.session_state.simulation_results = None
if "simulation_history" not in st.session_state:
    st.session_state.simulation_history = []
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"

# Import pages
from pages import home, simulate, running, results, history

# Page routing
PAGES = {
    "home": home,
    "simulate": simulate,
    "running": running,
    "results": results,
    "history": history,
}

def render_back_button():
    """Render a back button on non-home pages."""
    if st.session_state.current_page != "home":
        if st.button("← Back to Home", key="back_home"):
            st.session_state.current_page = "home"
            st.rerun()
        st.write("")  # Small spacer

def main():
    # Show back button on non-home pages
    render_back_button()
    
    # Page content  
    current_page = st.session_state.current_page
    if current_page in PAGES:
        PAGES[current_page].render()
    else:
        home.render()

if __name__ == "__main__":
    main()
