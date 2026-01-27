import streamlit as st
from pathlib import Path
import warnings

# Suppress warnings about widgets having value set via session state
warnings.filterwarnings("ignore", message='The widget with key ".*" was created with a default value but also had its value set via the Session State API.')

# Page configuration - must be first
st.set_page_config(
    page_title="Tax Force",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load custom CSS - modular approach
def load_css(page_name: str = None):
    """Load base CSS and optional page-specific CSS."""
    styles_dir = Path(__file__).parent / "styles"
    
    # Always load main.css as base
    main_css = styles_dir / "main.css"
    if main_css.exists():
        with open(main_css) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    # Load page-specific CSS if it exists
    if page_name:
        page_css = styles_dir / f"{page_name}.css"
        if page_css.exists():
            with open(page_css) as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Load base CSS at startup
load_css()

# Initialize session state
# Initialize session state (and handle URL routing)
if "current_page" not in st.session_state:
    # Check if URL has a specific page
    params = st.query_params
    target_page = params.get("page", "home")
    
    # Validate page exists, default to home if not
    # We need to access PAGES keys, but PAGES isn't defined yet.
    # So we define it first or just trust it for now and validation happens later.
    st.session_state.current_page = target_page

if "simulation_results" not in st.session_state:
    st.session_state.simulation_results = None
if "simulation_history" not in st.session_state:
    st.session_state.simulation_history = []

# Sync URL to match current page (so internal navigation updates URL)
# This runs on every rerun
if "current_page" in st.session_state:
    st.query_params["page"] = st.session_state.current_page

# Import pages
from pages import home, simulate, running, results, history, comparison

# Page routing
PAGES = {
    "home": home,
    "simulate": simulate,
    "running": running,
    "results": results,
    "history": history,
    "comparison": comparison,
}

def render_back_button():
    current_page = st.session_state.current_page
    
    if current_page == "home":
        return  # No back button on home page
    
    # Page-specific column ratios to match content alignment
    if current_page == "simulate":
        # simulate.py uses [1, 4, 1]
        left_spacer, btn_col, right_spacer = st.columns([1, 4, 1])
    elif current_page == "running":
        # running page - centered, no back button needed during simulation
        return
    else:
        # history, results, comparison all use [0.15, 8, 0.15]
        left_spacer, btn_col, right_spacer = st.columns([0.15, 8, 0.15])
    
    with btn_col:
        if st.button("← Back to Home", key="back_home"):
            st.session_state.current_page = "home"
            st.rerun()
        st.write("")

def main():
    render_back_button()
    
    current_page = st.session_state.current_page
    
    # Load page-specific CSS if it exists
    load_css(current_page)
    
    if current_page in PAGES:
        PAGES[current_page].render()
    else:
        home.render()

if __name__ == "__main__":
    main()
