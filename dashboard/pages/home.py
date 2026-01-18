"""
Home Page - Landing page with clickable action cards.
"""
import streamlit as st


def render():
    """Render the home page with the original card design, but entire cards are clickable."""
    
    # Page title
    st.markdown("""
        <div style="text-align: center; padding: 40px 0 48px 0;">
            <h1 style="font-size: 32px; font-weight: 700; color: #1A1A1A; margin: 0 0 12px 0;">
                Tax Policy Simulation Dashboard
            </h1>
            <p style="font-size: 16px; color: #718096; margin: 0;">
                Configure, run, and analyze tax compliance simulations
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Centered cards area
    spacer1, card_area, spacer2 = st.columns([0.5, 3, 0.5])
    
    with card_area:
        col1, col2 = st.columns(2, gap="large")
        
        with col1:
            # Original card design inside a container
            with st.container(border=True):
                st.markdown("""
                    <div style="text-align: center; padding: 20px 16px;">
                        <div style="width: 72px; height: 72px; background: linear-gradient(135deg, #01689B 0%, #154273 100%); 
                                    border-radius: 50%; display: flex; align-items: center; justify-content: center; 
                                    margin: 0 auto 20px auto;">
                            <svg viewBox="0 0 24 24" width="36" height="36" fill="white">
                                <polygon points="5,3 19,12 5,21"/>
                            </svg>
                        </div>
                        <div style="font-size: 20px; font-weight: 600; color: #1A1A1A; margin-bottom: 8px;">
                            Run Simulation
                        </div>
                        <div style="font-size: 14px; color: #718096;">
                            Configure parameters and run tax policy simulations with Monte Carlo analysis
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button("Start New Simulation", key="btn_simulate", use_container_width=True, type="primary"):
                    st.session_state.current_page = "simulate"
                    st.rerun()
        
        with col2:
            # Original card design inside a container
            with st.container(border=True):
                st.markdown("""
                    <div style="text-align: center; padding: 20px 16px;">
                        <div style="width: 72px; height: 72px; background: linear-gradient(135deg, #01689B 0%, #154273 100%); 
                                    border-radius: 50%; display: flex; align-items: center; justify-content: center; 
                                    margin: 0 auto 20px auto;">
                            <svg viewBox="0 0 24 24" width="36" height="36" fill="none" stroke="white" stroke-width="2">
                                <circle cx="12" cy="12" r="9"/>
                                <polyline points="12,7 12,12 15,14"/>
                            </svg>
                        </div>
                        <div style="font-size: 20px; font-weight: 600; color: #1A1A1A; margin-bottom: 8px;">
                            View History
                        </div>
                        <div style="font-size: 14px; color: #718096;">
                            Browse past simulation results and compare different policy configurations
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                if st.button("View Past Results", key="btn_history", use_container_width=True, type="primary"):
                    st.session_state.current_page = "history"
                    st.rerun()
    
    # Quick stats section
    st.write("")
    st.write("")
    
    # Load history count
    try:
        from utils.history import load_history
        history = load_history()
        history_count = len(history)
    except:
        history_count = 0
    
    if history_count > 0:
        st.markdown(f"""
            <div style="text-align: center; padding: 24px; background: white; border-radius: 12px; 
                        box-shadow: 0 2px 8px rgba(0,0,0,0.06); max-width: 400px; margin: 0 auto;">
                <span style="font-size: 14px; color: #718096;">You have </span>
                <span style="font-size: 18px; font-weight: 600; color: #01689B;">{history_count}</span>
                <span style="font-size: 14px; color: #718096;"> saved simulation{'' if history_count == 1 else 's'}</span>
            </div>
        """, unsafe_allow_html=True)
