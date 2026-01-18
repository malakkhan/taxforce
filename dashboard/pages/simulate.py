"""
Simulate Page - Configure simulation settings.
Three-tier settings hierarchy with nested expanders.
Professional design for Tax Authority dashboard.
"""
import streamlit as st
import streamlit_nested_layout  # Enables nested expanders


def render():
    """Render the simulation configuration page with tiered settings."""
    
    # Create centered content area
    left_spacer, content, right_spacer = st.columns([1, 4, 1])
    
    with content:
        # Page header
        st.markdown("""
            <div style="margin-bottom: 24px;">
                <h1 style="font-size: 28px; font-weight: 700; color: #1A1A1A; margin: 0 0 8px 0;">
                    Configure Simulation
                </h1>
                <p style="font-size: 14px; color: #718096; margin: 0;">
                    Adjust parameters and run your tax policy simulation
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # =====================================================
        # TIER 1: ESSENTIAL SETTINGS (Expanded by Default)
        # =====================================================
        
        # --- Scenario Settings ---
        with st.expander("Scenario Settings", expanded=True):
            st.caption("Core parameters that control simulation scale and precision")
            
            # Initialize session state for synced values
            if "pop_value" not in st.session_state:
                st.session_state.pop_value = 1000
            if "dur_value" not in st.session_state:
                st.session_state.dur_value = 50
            if "run_value" not in st.session_state:
                st.session_state.run_value = 3
            
            # Callback functions to sync values
            def sync_pop_from_slider():
                st.session_state.pop_value = st.session_state.pop_slider
            
            def sync_pop_from_input():
                st.session_state.pop_value = st.session_state.pop_input
            
            def sync_dur_from_slider():
                st.session_state.dur_value = st.session_state.dur_slider
            
            def sync_dur_from_input():
                st.session_state.dur_value = st.session_state.dur_input
            
            def sync_run_from_slider():
                st.session_state.run_value = st.session_state.run_slider
            
            def sync_run_from_input():
                st.session_state.run_value = st.session_state.run_input
            
            # --- Population Size ---
            st.markdown("**Population Size** — Number of synthetic taxpayers")
            col_pop_sl, col_pop_in = st.columns([4, 1])
            with col_pop_sl:
                st.slider(
                    "Population Slider",
                    min_value=500,
                    max_value=2500,
                    value=st.session_state.pop_value,
                    step=50,
                    key="pop_slider",
                    label_visibility="collapsed",
                    on_change=sync_pop_from_slider
                )
            with col_pop_in:
                st.number_input(
                    "Pop",
                    min_value=500,
                    max_value=2500,
                    value=st.session_state.pop_value,
                    step=50,
                    key="pop_input",
                    label_visibility="collapsed",
                    on_change=sync_pop_from_input
                )
            n_agents = st.session_state.pop_value
            
            st.write("")
            
            # --- Simulation Duration ---
            st.markdown("**Simulation Duration** — Number of time periods (years)")
            col_dur_sl, col_dur_in = st.columns([4, 1])
            with col_dur_sl:
                st.slider(
                    "Duration Slider",
                    min_value=10,
                    max_value=100,
                    value=st.session_state.dur_value,
                    step=5,
                    key="dur_slider",
                    label_visibility="collapsed",
                    on_change=sync_dur_from_slider
                )
            with col_dur_in:
                st.number_input(
                    "Dur",
                    min_value=10,
                    max_value=100,
                    value=st.session_state.dur_value,
                    step=5,
                    key="dur_input",
                    label_visibility="collapsed",
                    on_change=sync_dur_from_input
                )
            n_steps = st.session_state.dur_value
            
            st.write("")
            
            # --- Result Precision ---
            st.markdown("**Result Precision** — Monte Carlo repetitions")
            col_run_sl, col_run_in = st.columns([4, 1])
            with col_run_sl:
                st.slider(
                    "Runs Slider",
                    min_value=1,
                    max_value=10,
                    value=st.session_state.run_value,
                    step=1,
                    key="run_slider",
                    label_visibility="collapsed",
                    on_change=sync_run_from_slider
                )
            with col_run_in:
                st.number_input(
                    "Runs",
                    min_value=1,
                    max_value=10,
                    value=st.session_state.run_value,
                    step=1,
                    key="run_input",
                    label_visibility="collapsed",
                    on_change=sync_run_from_input
                )
            n_runs = st.session_state.run_value
        
        # --- Tax Policy ---
        with st.expander("Tax Policy", expanded=True):
            st.caption("Configure tax rates and penalties applied to taxpayers")
            
            col_t1, col_t2, col_t3 = st.columns(3)
            
            with col_t1:
                # Tax Rate - select_slider for common values
                st.markdown("**Tax Rate**")
                tax_rate = st.select_slider(
                    "Tax Rate",
                    options=[0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55],
                    value=0.30,
                    format_func=lambda x: f"{int(x*100)}%",
                    key="sl_tax",
                    label_visibility="collapsed"
                )
                st.caption("Marginal income rate")
            
            with col_t2:
                # Penalty - select_slider
                st.markdown("**Penalty**")
                penalty_rate = st.select_slider(
                    "Penalty",
                    options=[1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0],
                    value=3.0,
                    format_func=lambda x: f"{x:.1f}×",
                    key="sl_penalty",
                    label_visibility="collapsed"
                )
                st.caption("Fine multiplier")
            
            with col_t3:
                # Compliance - select_slider
                st.markdown("**Compliance**")
                honest_ratio = st.select_slider(
                    "Compliance",
                    options=[0.80, 0.85, 0.90, 0.92, 0.95, 0.97, 0.99],
                    value=0.92,
                    format_func=lambda x: f"{int(x*100)}%",
                    key="sl_honest",
                    label_visibility="collapsed"
                )
                st.caption("Honest taxpayer ratio")
        
        # --- Enforcement Strategy ---
        with st.expander("Enforcement Strategy", expanded=True):
            st.caption("How the tax authority selects taxpayers for audits")
            
            # Audit Strategy
            st.markdown("**Audit Selection Method**")
            audit_strategy = st.selectbox(
                "Strategy",
                options=["random", "risk_based", "network"],
                format_func=lambda x: {
                    "random": "Random — Uniform probability for all taxpayers",
                    "risk_based": "Risk-Based — Focus on high-risk profiles",
                    "network": "Network — Target based on social connections"
                }.get(x, x),
                key="sel_audit",
                label_visibility="collapsed"
            )
            
            st.write("")
            
            # Audit Rates
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("**Private Audit Rate**")
                audit_private = st.slider(
                    "Private Rate",
                    min_value=0.005,
                    max_value=0.10,
                    value=0.024,
                    step=0.005,
                    format="%.1f%%",
                    key="sl_audit_priv",
                    label_visibility="collapsed",
                    help="Default: 2.4% per Dutch Jaarrapportage"
                )
            with col_b:
                st.markdown("**Business Audit Rate**")
                audit_business = st.slider(
                    "Business Rate",
                    min_value=0.001,
                    max_value=0.05,
                    value=0.0046,
                    step=0.001,
                    format="%.2f%%",
                    key="sl_audit_biz",
                    label_visibility="collapsed",
                    help="Default: 0.46% per Dutch Jaarrapportage"
                )
        
        # =====================================================
        # TIER 2: ADVANCED SETTINGS (Collapsed by Default)
        # =====================================================
        
        # --- Network Parameters ---
        with st.expander("Network Parameters", expanded=False):
            st.caption("Configure social network structure between taxpayers")
            
            st.markdown("**Homophily** — Connection preference for similar agents")
            homophily = st.slider(
                "Homophily",
                min_value=0.0,
                max_value=1.0,
                value=0.80,
                step=0.05,
                key="sl_homo",
                label_visibility="collapsed",
                help="80% = agents prefer connecting with same type (private/business)"
            )
            
            st.write("")
            
            col_n1, col_n2 = st.columns(2)
            with col_n1:
                st.markdown("**Avg. Connections**")
                degree_mean = st.slider(
                    "Degree Mean",
                    min_value=10.0,
                    max_value=200.0,
                    value=86.27,
                    step=5.0,
                    key="sl_deg_mean",
                    label_visibility="collapsed",
                    help="Based on Dutch social contact research"
                )
            with col_n2:
                st.markdown("**Connection Variability**")
                degree_std = st.slider(
                    "Degree Std",
                    min_value=10.0,
                    max_value=100.0,
                    value=64.99,
                    step=5.0,
                    key="sl_deg_std",
                    label_visibility="collapsed"
                )
        
        # --- Social Dynamics ---
        with st.expander("Social Dynamics", expanded=False):
            st.caption("How taxpayers influence each other's behavior")
            
            st.markdown("**Peer Influence (ω)** — Strength of social influence")
            social_influence = st.slider(
                "Social Influence",
                min_value=0.0,
                max_value=1.0,
                value=0.5,
                step=0.1,
                key="sl_social",
                label_visibility="collapsed",
                help="0 = independent, 1 = fully influenced by peers"
            )
            
            st.write("")
            st.markdown("**Policy Interventions**")
            
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                st.markdown("Service Orientation Boost")
                pso_boost = st.slider(
                    "PSO Boost",
                    min_value=-1.0,
                    max_value=1.0,
                    value=0.0,
                    step=0.1,
                    key="sl_pso",
                    label_visibility="collapsed",
                    help="Simulate service-oriented interventions"
                )
            with col_s2:
                st.markdown("Trust Perception Boost")
                trust_boost = st.slider(
                    "Trust Boost",
                    min_value=-1.0,
                    max_value=1.0,
                    value=0.0,
                    step=0.1,
                    key="sl_trust",
                    label_visibility="collapsed",
                    help="Simulate trust-building interventions"
                )
        
        # --- Population Composition ---
        with st.expander("Population Composition", expanded=False):
            st.caption("Configure the mix of taxpayer types")
            
            st.markdown("**Business/SME Ratio**")
            business_ratio = st.slider(
                "Business Ratio",
                min_value=0.05,
                max_value=0.40,
                value=0.134,
                step=0.01,
                format="%.1f%%",
                key="sl_biz",
                label_visibility="collapsed",
                help="Default: 13.4% based on Dutch CBS data"
            )
            st.caption(f"{business_ratio*100:.1f}% businesses, {(1-business_ratio)*100:.1f}% private individuals")
        
        # =====================================================
        # TIER 3: EXPERT SETTINGS (Nested Expanders)
        # =====================================================
        
        with st.expander("Agent Traits (Expert)", expanded=False):
            st.caption("Fine-tune agent psychological and economic parameters")
            
            # --- Private Individual Traits ---
            with st.expander("Private Individual Traits", expanded=False):
                col_p1, col_p2 = st.columns(2)
                
                with col_p1:
                    st.markdown("**Personal Norms**")
                    priv_pn = st.slider("PN", 1.0, 5.0, 3.40, 0.1, key="sl_priv_pn", 
                                        label_visibility="collapsed", help="Internal ethics (1-5 scale)")
                    
                    st.markdown("**Social Norms**")
                    priv_sn = st.slider("SN", 1.0, 5.0, 3.42, 0.1, key="sl_priv_sn",
                                        label_visibility="collapsed", help="Perceived peer norms")
                    
                    st.markdown("**Societal Norms**")
                    priv_stn = st.slider("StN", 1.0, 5.0, 3.97, 0.1, key="sl_priv_stn",
                                         label_visibility="collapsed", help="Perceived societal norms")
                
                with col_p2:
                    st.markdown("**Service Orientation**")
                    priv_pso = st.slider("PSO", 1.0, 5.0, 3.22, 0.1, key="sl_priv_pso",
                                         label_visibility="collapsed", help="Perceived authority helpfulness")
                    
                    st.markdown("**Trustworthiness**")
                    priv_pt = st.slider("PT", 1.0, 5.0, 3.37, 0.1, key="sl_priv_pt",
                                        label_visibility="collapsed", help="Trust in tax authority")
                    
                    st.markdown("**Average Income (€)**")
                    priv_income = st.slider("Income", 20000, 80000, 41000, 1000, key="sl_priv_inc",
                                            label_visibility="collapsed")
            
            # --- Business Traits ---
            with st.expander("Business Owner Traits", expanded=False):
                col_b1, col_b2 = st.columns(2)
                
                with col_b1:
                    st.markdown("**Personal Norms**")
                    biz_pn = st.slider("PN", 1.0, 5.0, 3.82, 0.1, key="sl_biz_pn",
                                       label_visibility="collapsed")
                    
                    st.markdown("**Social Norms**")
                    biz_sn = st.slider("SN", 1.0, 5.0, 3.82, 0.1, key="sl_biz_sn",
                                       label_visibility="collapsed")
                    
                    st.markdown("**Societal Norms**")
                    biz_stn = st.slider("StN", 1.0, 5.0, 4.12, 0.1, key="sl_biz_stn",
                                        label_visibility="collapsed")
                
                with col_b2:
                    st.markdown("**Service Orientation**")
                    biz_pso = st.slider("PSO", 1.0, 5.0, 3.18, 0.1, key="sl_biz_pso",
                                        label_visibility="collapsed")
                    
                    st.markdown("**Trustworthiness**")
                    biz_pt = st.slider("PT", 1.0, 5.0, 3.37, 0.1, key="sl_biz_pt",
                                       label_visibility="collapsed")
            
            # --- SME Risk Model ---
            with st.expander("SME Risk Model", expanded=False):
                st.caption("Adjust risk score deltas for business characteristics")
                
                col_r1, col_r2 = st.columns(2)
                
                with col_r1:
                    st.markdown("**Base Risk**")
                    risk_base = st.slider("Base", 0.05, 0.35, 0.20, 0.01, key="sl_risk_base",
                                          label_visibility="collapsed")
                    
                    st.markdown("**High-Risk Sector Δ**")
                    delta_sector = st.slider("Sector", 0.0, 0.30, 0.20, 0.01, key="sl_d_sector",
                                             label_visibility="collapsed")
                    
                    st.markdown("**Cash Intensive Δ**")
                    delta_cash = st.slider("Cash", 0.0, 0.20, 0.10, 0.01, key="sl_d_cash",
                                           label_visibility="collapsed")
                
                with col_r2:
                    st.markdown("**High Digitalisation Δ**")
                    delta_digi_high = st.slider("Digi High", -0.20, 0.0, -0.10, 0.01, key="sl_d_digi",
                                                label_visibility="collapsed")
                    
                    st.markdown("**Has Advisor Δ**")
                    delta_advisor = st.slider("Advisor", -0.20, 0.0, -0.10, 0.01, key="sl_d_adv",
                                              label_visibility="collapsed")
                    
                    st.markdown("**Prior Audit Δ**")
                    delta_audit = st.slider("Audit", -0.20, 0.0, -0.10, 0.01, key="sl_d_audit",
                                            label_visibility="collapsed")
        
        # =====================================================
        # ACTION BAR
        # =====================================================
        
        st.markdown("<div style='height: 24px'></div>", unsafe_allow_html=True)
        st.divider()
        
        col1, col2, spacer, col3 = st.columns([1, 1, 2, 2])
        
        with col1:
            st.button("Import", use_container_width=True, key="btn_import")
        with col2:
            st.button("Export", use_container_width=True, key="btn_export")
        with col3:
            if st.button("Start Simulation", type="primary", use_container_width=True, key="btn_start"):
                # Build complete config dict
                st.session_state.simulation_params = {
                    # Simulation core
                    "n_agents": n_agents,
                    "n_steps": n_steps,
                    "n_runs": n_runs,
                    "business_ratio": business_ratio,
                    
                    # Behaviors
                    "honest_ratio": honest_ratio,
                    
                    # Enforcement
                    "tax_rate": tax_rate,
                    "penalty_rate": penalty_rate,
                    "audit_strategy": audit_strategy,
                    "audit_rate_private": audit_private,
                    "audit_rate_business": audit_business,
                    
                    # Network
                    "homophily": homophily,
                    "degree_mean": degree_mean,
                    "degree_std": degree_std,
                    
                    # Social
                    "social_influence": social_influence,
                    "pso_boost": pso_boost,
                    "trust_boost": trust_boost,
                    
                    # Traits - Private
                    "traits_private": {
                        "personal_norms_mean": priv_pn,
                        "social_norms_mean": priv_sn,
                        "societal_norms_mean": priv_stn,
                        "pso_mean": priv_pso,
                        "trust_mean": priv_pt,
                        "income_mean": priv_income,
                    },
                    
                    # Traits - Business
                    "traits_business": {
                        "personal_norms_mean": biz_pn,
                        "social_norms_mean": biz_sn,
                        "societal_norms_mean": biz_stn,
                        "pso_mean": biz_pso,
                        "trust_mean": biz_pt,
                    },
                    
                    # SME Risk
                    "sme_risk": {
                        "base": risk_base,
                        "delta_sector": delta_sector,
                        "delta_cash": delta_cash,
                        "delta_digi_high": delta_digi_high,
                        "delta_advisor": delta_advisor,
                        "delta_audit": delta_audit,
                    },
                }
                
                st.session_state.current_page = "running"
                st.rerun()
