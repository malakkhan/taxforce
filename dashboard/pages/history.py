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
    
    # Create centered content area with side padding (like comparison.py)
    left_spacer, content, right_spacer = st.columns([0.15, 8, 0.15])
    
    with content:
        # Page header row with title and sort dropdown
        header_cols = st.columns([5, 2, 1])
        with header_cols[0]:
            st.markdown('<div style="display:flex; align-items:baseline; gap:16px; margin-bottom:0px;">'
                        '<span style="font-size:28px; font-weight:700; color:#1A1A1A;">History</span>'
                        '<span style="font-size:14px; color:#718096;">View past simulation results</span></div>', 
                        unsafe_allow_html=True)
        with header_cols[1]:
            sort_order = st.selectbox("Sort by", ["Most Recent", "Oldest First"], 
                                       label_visibility="collapsed", key="sort")
        with header_cols[2]:
            from dashboard.utils.ui import render_download_button
            render_download_button()
                                       
        st.markdown('<div style="border-bottom:1px solid #D1D9E0; margin-bottom:16px; margin-top:-12px;"></div>', unsafe_allow_html=True)
        
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
            
            # Inject CSS to reduce card padding
            st.markdown("""
                <style>
                    [data-testid="stVerticalBlock"] > div:has(> [data-testid="stHorizontalBlock"]) {
                        padding: 8px 16px !important;
                    }
                </style>
            """, unsafe_allow_html=True)
            
            # Display history entries - compact layout
            for idx, entry in sorted_history:
                with st.container(border=True):
                    # Compact single row: date/params + metrics + button
                    row_cols = st.columns([2.5, 1, 1, 1, 1, 1])
                    
                    with row_cols[0]:
                        st.markdown(f"""
                            <div style="line-height:1.4;">
                                <span style="font-weight:600; font-size:15px; color:#1A1A1A;">{entry.get('date', 'Unknown')}</span><br>
                                <span style="font-size:12px; color:#718096;">{entry.get('n_agents', 0):,} agents • {entry.get('n_steps', 0)} steps • Tax: {entry.get('params', {}).get('tax_rate', 0.3)*100:.0f}%</span>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with row_cols[1]:
                        st.markdown(f"""
                            <div style="font-size:11px; color:#718096;">Total Taxes</div>
                            <div style="font-size:15px; font-weight:600; color:#1A1A1A;">{format_number(entry.get('total_taxes', 0))}</div>
                        """, unsafe_allow_html=True, help="Average sum of Total Taxes collected over the full duration, averaged across runs.")
                    
                    with row_cols[2]:
                        tax_gap = entry.get('tax_gap', 0)
                        st.markdown(f"""
                            <div style="font-size:11px; color:#718096;">Tax Gap</div>
                            <div style="font-size:15px; font-weight:600; color:#38A169;">+{format_number(tax_gap)}</div>
                        """, unsafe_allow_html=True, help="Average sum of Tax Gap accumulated over the full duration, averaged across runs.")
                    
                    with row_cols[3]:
                        audits = entry.get('audits', entry.get('interventions', 0))
                        st.markdown(f"""
                            <div style="font-size:11px; color:#718096;">Audits</div>
                            <div style="font-size:15px; font-weight:600; color:#1A1A1A;">{audits:,}</div>
                        """, unsafe_allow_html=True, help="Sum of all audits across all steps (averaged across runs).")
                    
                    with row_cols[4]:
                        compliance = entry.get('compliance', entry.get('tax_morale', 0)) * 100
                        st.markdown(f"""
                            <div style="font-size:11px; color:#718096;">Compliance</div>
                            <div style="font-size:15px; font-weight:600; color:#1A1A1A;">{compliance:.0f}%</div>
                        """, unsafe_allow_html=True, help="The Compliance Rate at the very last step (averaged across runs).")
                    
                    with row_cols[5]:
                        if st.button("View", key=f"view_{idx}", type="primary", use_container_width=True):
                            st.session_state.simulation_results = entry.get("results", {})
                            st.session_state.simulation_params_used = entry.get("params", {})
                            st.session_state.current_page = "results"
                            st.rerun()
