"""
History Page - View past simulation results.
Loads history from disk for persistence across sessions.
"""
import streamlit as st


def format_number(n):
    """Format numbers for display."""
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    elif n >= 1_000:
        return f"{n/1_000:.1f}K"
    else:
        return f"{n:.0f}"


def render():
    """Render the history page."""
    
    # Back button and title row
    back_col, title_col, sort_col = st.columns([1, 6, 2])
    
    with back_col:
        if st.button("< Back", key="back_btn"):
            st.session_state.current_page = "home"
            st.rerun()
    
    with title_col:
        st.markdown("""
            <h2 style="font-size: 18px; font-weight: 600; color: #154273; margin: 0;
                       text-decoration: underline; text-underline-offset: 4px;">History</h2>
        """, unsafe_allow_html=True)
    
    with sort_col:
        sort_order = st.selectbox("Sort by", ["Most Recent", "Oldest First"], 
                                   label_visibility="collapsed", key="sort")
    
    st.write("")
    
    # Load history from disk
    try:
        from utils.history import load_history
        history = load_history()
    except Exception:
        history = []
    
    if not history:
        # Show empty state
        with st.container(border=True):
            st.markdown("""
                <div style="text-align: center; padding: 40px 20px;">
                    <svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="#718096" stroke-width="1.5" style="margin-bottom: 16px;">
                        <circle cx="12" cy="12" r="9"/>
                        <polyline points="12,7 12,12 15,14"/>
                    </svg>
                    <p style="font-size: 14px; color: #718096; margin: 0;">No simulation history yet</p>
                    <p style="font-size: 12px; color: #A0AEC0; margin: 4px 0 0 0;">Run a simulation to see results here</p>
                </div>
            """, unsafe_allow_html=True)
        
        st.write("")
        if st.button("Run New Simulation", type="primary"):
            st.session_state.current_page = "simulate"
            st.rerun()
    else:
        # Sort history
        sorted_history = list(enumerate(history))
        if sort_order == "Most Recent":
            sorted_history = list(reversed(sorted_history))
        
        # Display history entries
        for idx, entry in sorted_history:
            with st.container(border=True):
                # Title row with date and params
                st.markdown(f"""
                    <div style="margin-bottom: 12px;">
                        <span style="font-weight: 600; font-size: 14px; color: #1A1A1A;">
                            {entry.get('date', 'Unknown date')}
                        </span>
                        <br>
                        <span style="font-size: 12px; color: #718096;">
                            {entry.get('n_agents', 0):,} agents • {entry.get('n_steps', 0)} steps • 
                            Tax rate: {entry.get('params', {}).get('tax_rate', 0.3)*100:.0f}%
                        </span>
                    </div>
                """, unsafe_allow_html=True)
                
                # Metrics row
                m1, m2, m3, m4, btn_col = st.columns([1.5, 1.5, 1.5, 1.5, 1])
                
                with m1:
                    st.markdown(f"""
                        <div style="font-size: 11px; color: #718096;">Total Taxes</div>
                        <div style="font-size: 14px; font-weight: 600; color: #1A1A1A;">
                            {format_number(entry.get('total_taxes', 0))}
                        </div>
                    """, unsafe_allow_html=True)
                
                with m2:
                    tax_gap = entry.get('tax_gap', 0)
                    st.markdown(f"""
                        <div style="font-size: 11px; color: #718096;">Tax Gap</div>
                        <div style="font-size: 14px; font-weight: 600; color: #38A169;">
                            +{format_number(tax_gap)}
                        </div>
                    """, unsafe_allow_html=True)
                
                with m3:
                    st.markdown(f"""
                        <div style="font-size: 11px; color: #718096;">Interventions</div>
                        <div style="font-size: 14px; font-weight: 600; color: #1A1A1A;">
                            {entry.get('interventions', 0):,}
                        </div>
                    """, unsafe_allow_html=True)
                
                with m4:
                    morale = entry.get('tax_morale', 0) * 100
                    st.markdown(f"""
                        <div style="font-size: 11px; color: #718096;">Tax Morale</div>
                        <div style="font-size: 14px; font-weight: 600; color: #1A1A1A;">
                            {morale:.0f}%
                        </div>
                    """, unsafe_allow_html=True)
                
                with btn_col:
                    if st.button("View Results", key=f"view_{idx}", type="primary", use_container_width=True):
                        st.session_state.simulation_results = entry.get("results", {})
                        st.session_state.simulation_params_used = entry.get("params", {})
                        st.session_state.current_page = "results"
                        st.rerun()
