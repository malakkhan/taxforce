"""
Simulate Page - Configure simulation settings.
Three-tier settings hierarchy with nested expanders.
Professional design for Tax Authority dashboard.
"""
import streamlit as st
import streamlit_nested_layout  # Enables nested expanders
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.config import SimulationConfig

# Load defaults from actual config files
_cfg = SimulationConfig.default()

def _get_default_values():
    """Build default values dict from core config."""
    return {
        # Simulation
        "pop_value": _cfg.simulation["n_agents"],
        "dur_value": _cfg.simulation["n_steps"],
        "run_value": 1,  # n_runs not in config, keep hardcoded
        
        # Tax policy
        "tax_rate_value": int(_cfg.enforcement["tax_rate"] * 100),
        "penalty_value": _cfg.enforcement["penalty_rate"],
        
        # Behaviors
        "compliance_value": int(_cfg.behaviors["distribution"]["honest"] * 100),
        
        # Audit rates
        "priv_audit_value": _cfg.enforcement["audit_rate"]["private"] * 100,
        "biz_audit_value": _cfg.enforcement["audit_rate"]["business"] * 100,
        
        # Population
        "biz_ratio_value": _cfg.simulation["business_ratio"] * 100,
        
        # Network
        "homophily_value": _cfg.network["homophily"],
        "degree_mean_value": _cfg.network["degree_mean"],
        "degree_std_value": _cfg.network["degree_std"],
        
        # Social
        "social_influence_value": _cfg.social["social_influence"],
        "pso_boost_value": _cfg.social["pso_boost"],
        "trust_boost_value": _cfg.social["trust_boost"],
        
        # Norm Update Scales
        "social_norm_scale_priv": _cfg.norm_update["social_norm_scale"]["private"],
        "social_norm_scale_biz": _cfg.norm_update["social_norm_scale"]["business"],
        "societal_norm_scale_priv": _cfg.norm_update["societal_norm_scale"]["private"],
        "societal_norm_scale_biz": _cfg.norm_update["societal_norm_scale"]["business"],
        
        # Traits - Private
        "priv_pn_value": _cfg.traits["private"]["personal_norms"]["mean"],
        "priv_sn_value": _cfg.traits["private"]["social_norms"]["mean"],
        "priv_stn_value": _cfg.traits["private"]["societal_norms"]["mean"],
        "priv_pso_value": _cfg.traits["private"]["perceived_service_orientation"]["mean"],
        "priv_pt_value": _cfg.traits["private"]["perceived_trustworthiness"]["mean"],
        "priv_income_value": _cfg.private["income"]["mean"],
        "priv_audit_belief_value": float(_cfg.traits["private"]["subjective_audit_prob"]["mean"]),
        
        # Traits - Business
        "biz_pn_value": _cfg.traits["business"]["personal_norms"]["mean"],
        "biz_sn_value": _cfg.traits["business"]["social_norms"]["mean"],
        "biz_stn_value": _cfg.traits["business"]["societal_norms"]["mean"],
        "biz_pso_value": _cfg.traits["business"]["perceived_service_orientation"]["mean"],
        "biz_pt_value": _cfg.traits["business"]["perceived_trustworthiness"]["mean"],
        "biz_audit_belief_value": float(_cfg.traits["business"]["subjective_audit_prob"]["mean"]),
        
        # SME Risk
        "risk_base_value": _cfg.sme["base_risk_baseline"],
        "delta_sector_value": _cfg.sme["delta_sector_high_risk"],
        "delta_cash_value": _cfg.sme["delta_cash_intensive"],
        "delta_digi_high_value": _cfg.sme["delta_digi_high"],
        "delta_advisor_value": abs(_cfg.sme["delta_advisor_yes"]),
        "delta_audit_value": abs(_cfg.sme["delta_audit_books"]),
    }

DEFAULT_VALUES = _get_default_values()

def reset_to_defaults():
    """Reset all session state values to their defaults."""
    for key, value in DEFAULT_VALUES.items():
        st.session_state[key] = value

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
            
            # Initialize session state for synced values from DEFAULT_VALUES
            if "pop_value" not in st.session_state:
                st.session_state.pop_value = DEFAULT_VALUES["pop_value"]
            if "dur_value" not in st.session_state:
                st.session_state.dur_value = DEFAULT_VALUES["dur_value"]
            if "run_value" not in st.session_state:
                st.session_state.run_value = DEFAULT_VALUES["run_value"]
            
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
            st.markdown("**Population Size** · Number of agents")
            pop_min, pop_max = 500, 2500
            col_pop_sl, col_pop_in = st.columns([4, 1])
            with col_pop_sl:
                st.slider(
                    "Population Slider",
                    min_value=pop_min,
                    max_value=pop_max,
                    value=max(pop_min, min(pop_max, st.session_state.pop_value)),
                    step=50,
                    key="pop_slider",
                    label_visibility="collapsed",
                    on_change=sync_pop_from_slider
                )
            with col_pop_in:
                st.number_input(
                    "Pop",
                    min_value=1,
                    max_value=100000,
                    value=st.session_state.pop_value,
                    step=50,
                    key="pop_input",
                    label_visibility="collapsed",
                    on_change=sync_pop_from_input
                )
            n_agents = st.session_state.pop_value
            
            # --- Simulation Duration ---
            st.markdown("**Simulation Duration** · Number of steps (years)")
            dur_min, dur_max = 10, 100
            col_dur_sl, col_dur_in = st.columns([4, 1])
            with col_dur_sl:
                st.slider(
                    "Duration Slider",
                    min_value=dur_min,
                    max_value=dur_max,
                    value=max(dur_min, min(dur_max, st.session_state.dur_value)),
                    step=5,
                    key="dur_slider",
                    label_visibility="collapsed",
                    on_change=sync_dur_from_slider
                )
            with col_dur_in:
                st.number_input(
                    "Dur",
                    min_value=1,
                    max_value=1000,
                    value=st.session_state.dur_value,
                    step=5,
                    key="dur_input",
                    label_visibility="collapsed",
                    on_change=sync_dur_from_input
                )
            n_steps = st.session_state.dur_value
            
            # --- Result Precision ---
            st.markdown("**Repetitions - Number of simulations to run**")
            run_min, run_max = 1, 10
            col_run_sl, col_run_in = st.columns([4, 1])
            with col_run_sl:
                st.slider(
                    "Runs Slider",
                    min_value=run_min,
                    max_value=run_max,
                    value=max(run_min, min(run_max, st.session_state.run_value)),
                    step=1,
                    key="run_slider",
                    label_visibility="collapsed",
                    on_change=sync_run_from_slider
                )
            with col_run_in:
                st.number_input(
                    "Runs",
                    min_value=1,
                    max_value=100,
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
            
            # Initialize session state for tax policy values
            if "tax_rate_value" not in st.session_state:
                st.session_state.tax_rate_value = DEFAULT_VALUES["tax_rate_value"]
            if "penalty_value" not in st.session_state:
                st.session_state.penalty_value = DEFAULT_VALUES["penalty_value"]
            if "compliance_value" not in st.session_state:
                st.session_state.compliance_value = DEFAULT_VALUES["compliance_value"]
            
            # Sync callbacks
            def sync_tax_from_slider():
                st.session_state.tax_rate_value = st.session_state.tax_slider
            def sync_tax_from_input():
                st.session_state.tax_rate_value = st.session_state.tax_input
            def sync_penalty_from_slider():
                st.session_state.penalty_value = st.session_state.penalty_slider
            def sync_penalty_from_input():
                st.session_state.penalty_value = st.session_state.penalty_input
            def sync_compliance_from_slider():
                st.session_state.compliance_value = st.session_state.compliance_slider
            def sync_compliance_from_input():
                st.session_state.compliance_value = st.session_state.compliance_input
            
            # --- Tax Rate ---
            st.markdown("**Tax Rate** · Income rate (%)")
            tax_min, tax_max = 10, 60
            col_tax_sl, col_tax_in = st.columns([4, 1])
            with col_tax_sl:
                st.slider(
                    "Tax Rate Slider",
                    min_value=tax_min,
                    max_value=tax_max,
                    value=max(tax_min, min(tax_max, st.session_state.tax_rate_value)),
                    step=5,
                    key="tax_slider",
                    label_visibility="collapsed",
                    on_change=sync_tax_from_slider
                )
            with col_tax_in:
                st.number_input(
                    "Tax",
                    min_value=0,
                    max_value=100,
                    value=st.session_state.tax_rate_value,
                    step=1,
                    key="tax_input",
                    label_visibility="collapsed",
                    on_change=sync_tax_from_input
                )
            tax_rate = st.session_state.tax_rate_value / 100.0
            
            # --- Penalty Rate ---
            st.markdown("**Penalty** · Fine multiplier (x)")
            pen_min, pen_max = 1.0, 5.0
            col_pen_sl, col_pen_in = st.columns([4, 1])
            with col_pen_sl:
                st.slider(
                    "Penalty Slider",
                    min_value=pen_min,
                    max_value=pen_max,
                    value=max(pen_min, min(pen_max, st.session_state.penalty_value)),
                    step=0.5,
                    key="penalty_slider",
                    label_visibility="collapsed",
                    on_change=sync_penalty_from_slider
                )
            with col_pen_in:
                st.number_input(
                    "Penalty",
                    min_value=0.1,
                    max_value=20.0,
                    value=st.session_state.penalty_value,
                    step=0.1,
                    key="penalty_input",
                    label_visibility="collapsed",
                    on_change=sync_penalty_from_input
                )
            penalty_rate = st.session_state.penalty_value
            
            # --- Compliance ---
            st.markdown("**Compliance** · Honest taxpayers (%)")
            comp_min, comp_max = 0, 100
            col_hon_sl, col_hon_in = st.columns([4, 1])
            with col_hon_sl:
                st.slider(
                    "Compliance Slider",
                    min_value=comp_min,
                    max_value=comp_max,
                    value=max(comp_min, min(comp_max, st.session_state.compliance_value)),
                    step=5,
                    key="compliance_slider",
                    label_visibility="collapsed",
                    on_change=sync_compliance_from_slider
                )
            with col_hon_in:
                st.number_input(
                    "Compliance",
                    min_value=0,
                    max_value=100,
                    value=st.session_state.compliance_value,
                    step=1,
                    key="compliance_input",
                    label_visibility="collapsed",
                    on_change=sync_compliance_from_input
                )
            honest_ratio = st.session_state.compliance_value / 100.0
        
        # --- Enforcement Strategy ---
        with st.expander("Enforcement Strategy", expanded=True):
            st.caption("How the tax authority selects taxpayers for audits")
            
            # Audit Strategy
            st.markdown("**Audit Selection Method**")
            audit_strategy = st.selectbox(
                "Strategy",
                options=["random", "risk_based", "network"],
                format_func=lambda x: {
                    "random": "Random · Uniform probability for all taxpayers",
                    "risk_based": "Risk-Based · Focus on high-risk profiles",
                    "network": "Network · Target based on social connections"
                }.get(x, x),
                key="sel_audit",
                label_visibility="collapsed"
            )
            
            st.write("")
            
            # Initialize session state for audit rates (store as percentages 0-100)
            if "priv_audit_value" not in st.session_state:
                st.session_state.priv_audit_value = DEFAULT_VALUES["priv_audit_value"]
            if "biz_audit_value" not in st.session_state:
                st.session_state.biz_audit_value = DEFAULT_VALUES["biz_audit_value"]
            
            # Sync callbacks
            def sync_priv_audit_from_slider():
                st.session_state.priv_audit_value = st.session_state.priv_audit_slider
            def sync_priv_audit_from_input():
                st.session_state.priv_audit_value = st.session_state.priv_audit_input
            def sync_biz_audit_from_slider():
                st.session_state.biz_audit_value = st.session_state.biz_audit_slider
            def sync_biz_audit_from_input():
                st.session_state.biz_audit_value = st.session_state.biz_audit_input
            
            # --- Private Audit Rate ---
            st.markdown("**Private Audit Rate** · Individual taxpayer audit probability (%)")
            priv_min, priv_max = 0.0, 10.0
            col_priv_sl, col_priv_in = st.columns([4, 1])
            with col_priv_sl:
                st.slider(
                    "Private Rate Slider",
                    min_value=priv_min,
                    max_value=priv_max,
                    value=max(priv_min, min(priv_max, st.session_state.priv_audit_value)),
                    step=0.1,
                    key="priv_audit_slider",
                    label_visibility="collapsed",
                    on_change=sync_priv_audit_from_slider
                )
            with col_priv_in:
                st.number_input(
                    "Priv",
                    min_value=0.0,
                    max_value=100.0,
                    value=st.session_state.priv_audit_value,
                    step=0.1,
                    format="%.1f",
                    key="priv_audit_input",
                    label_visibility="collapsed",
                    on_change=sync_priv_audit_from_input
                )
            audit_private = st.session_state.priv_audit_value / 100.0
            
            # --- Business Audit Rate ---
            st.markdown("**Business Audit Rate** · SME audit probability (%)")
            biz_min, biz_max = 0.0, 5.0
            col_biz_sl, col_biz_in = st.columns([4, 1])
            with col_biz_sl:
                st.slider(
                    "Business Rate Slider",
                    min_value=biz_min,
                    max_value=biz_max,
                    value=max(biz_min, min(biz_max, st.session_state.biz_audit_value)),
                    step=0.01,
                    key="biz_audit_slider",
                    label_visibility="collapsed",
                    on_change=sync_biz_audit_from_slider
                )
            with col_biz_in:
                st.number_input(
                    "Biz",
                    min_value=0.0,
                    max_value=100.0,
                    value=st.session_state.biz_audit_value,
                    step=0.01,
                    format="%.2f",
                    key="biz_audit_input",
                    label_visibility="collapsed",
                    on_change=sync_biz_audit_from_input
                )
            audit_business = st.session_state.biz_audit_value / 100.0
        
        # =====================================================
        # TIER 2: ADVANCED SETTINGS (Collapsed by Default)
        # =====================================================
        
        # --- Network & Social Dynamics ---
        with st.expander("Network & Social Dynamics", expanded=False):
            # Use three columns: Social | Divider | Network
            col_social, col_divider, col_network = st.columns([10, 1, 10])
            
            # Left column: Social Dynamics
            with col_social:
                st.markdown("**Social Dynamics**")
                
                row1_l, row1_r = st.columns([3, 2])
                with row1_l:
                    st.markdown("<div style='padding-top: 8px;'>Peer Influence (ω)</div>", unsafe_allow_html=True)
                with row1_r:
                    social_influence = st.number_input("s", min_value=0.0, max_value=1.0, 
                        value=DEFAULT_VALUES["social_influence_value"], step=0.1, format="%.2f", 
                        label_visibility="collapsed", key="soc_inf")
                
                row2_l, row2_r = st.columns([3, 2])
                with row2_l:
                    st.markdown("<div style='padding-top: 8px;'>Service Boost</div>", unsafe_allow_html=True)
                with row2_r:
                    pso_boost = st.number_input("p", min_value=-1.0, max_value=1.0, 
                        value=DEFAULT_VALUES["pso_boost_value"], step=0.1, format="%.1f", 
                        label_visibility="collapsed", key="soc_pso")
                
                row3_l, row3_r = st.columns([3, 2])
                with row3_l:
                    st.markdown("<div style='padding-top: 8px;'>Trust Boost</div>", unsafe_allow_html=True)
                with row3_r:
                    trust_boost = st.number_input("t", min_value=-1.0, max_value=1.0, 
                        value=DEFAULT_VALUES["trust_boost_value"], step=0.1, format="%.1f", 
                        label_visibility="collapsed", key="soc_trust")
                
                st.markdown("---")
                st.markdown("**Norm Update Scales**")
                
                row4_l, row4_r = st.columns([3, 2])
                with row4_l:
                    st.markdown("<div style='padding-top: 8px;'>Social (Private)</div>", unsafe_allow_html=True)
                with row4_r:
                    sn_scale_priv = st.number_input("snp", min_value=0.0, max_value=1.0, 
                        value=DEFAULT_VALUES["social_norm_scale_priv"], step=0.05, format="%.2f", 
                        label_visibility="collapsed", key="sn_scale_priv")
                
                row5_l, row5_r = st.columns([3, 2])
                with row5_l:
                    st.markdown("<div style='padding-top: 8px;'>Social (Business)</div>", unsafe_allow_html=True)
                with row5_r:
                    sn_scale_biz = st.number_input("snb", min_value=0.0, max_value=1.0, 
                        value=DEFAULT_VALUES["social_norm_scale_biz"], step=0.05, format="%.2f", 
                        label_visibility="collapsed", key="sn_scale_biz")
                
                row6_l, row6_r = st.columns([3, 2])
                with row6_l:
                    st.markdown("<div style='padding-top: 8px;'>Societal (Private)</div>", unsafe_allow_html=True)
                with row6_r:
                    stn_scale_priv = st.number_input("stnp", min_value=0.0, max_value=0.5, 
                        value=DEFAULT_VALUES["societal_norm_scale_priv"], step=0.01, format="%.3f", 
                        label_visibility="collapsed", key="stn_scale_priv")
                
                row7_l, row7_r = st.columns([3, 2])
                with row7_l:
                    st.markdown("<div style='padding-top: 8px;'>Societal (Business)</div>", unsafe_allow_html=True)
                with row7_r:
                    stn_scale_biz = st.number_input("stnb", min_value=0.0, max_value=0.5, 
                        value=DEFAULT_VALUES["societal_norm_scale_biz"], step=0.01, format="%.3f", 
                        label_visibility="collapsed", key="stn_scale_biz")
            
            # Center column: Vertical divider
            with col_divider:
                st.markdown("""
                    <div style='
                        width: 1px;
                        background-color: #CBD5E1;
                        min-height: 350px;
                        margin: 0 auto;
                    '></div>
                """, unsafe_allow_html=True)
            
            # Right column: Network Structure
            with col_network:
                st.markdown("**Network Structure**")
                
                row8_l, row8_r = st.columns([3, 2])
                with row8_l:
                    st.markdown("<div style='padding-top: 8px;'>Homophily</div>", unsafe_allow_html=True)
                with row8_r:
                    homophily = st.number_input("h", min_value=0.0, max_value=1.0, 
                        value=DEFAULT_VALUES["homophily_value"], step=0.05, format="%.2f", 
                        label_visibility="collapsed", key="net_homo")
                
                row9_l, row9_r = st.columns([3, 2])
                with row9_l:
                    st.markdown("<div style='padding-top: 8px;'>Avg. Connections</div>", unsafe_allow_html=True)
                with row9_r:
                    degree_mean = st.number_input("d", min_value=5.0, max_value=300.0, 
                        value=DEFAULT_VALUES["degree_mean_value"], step=5.0, format="%.1f", 
                        label_visibility="collapsed", key="net_deg")
                
                row10_l, row10_r = st.columns([3, 2])
                with row10_l:
                    st.markdown("<div style='padding-top: 8px;'>Variability</div>", unsafe_allow_html=True)
                with row10_r:
                    degree_std = st.number_input("v", min_value=5.0, max_value=150.0, 
                        value=DEFAULT_VALUES["degree_std_value"], step=5.0, format="%.1f", 
                        label_visibility="collapsed", key="net_std")
        
        # --- Population Composition ---
        with st.expander("Population Composition", expanded=False):
            # Initialize session state for business ratio (store as percentage 0-100)
            if "biz_ratio_value" not in st.session_state:
                st.session_state.biz_ratio_value = DEFAULT_VALUES["biz_ratio_value"]
            
            # Sync callbacks
            def sync_biz_ratio_from_slider():
                st.session_state.biz_ratio_value = st.session_state.biz_ratio_slider
            def sync_biz_ratio_from_input():
                st.session_state.biz_ratio_value = st.session_state.biz_ratio_input
            
            st.markdown("**Private/SME Ratio** · Percentage of SMEs (%)")
            col_biz_sl, col_biz_in = st.columns([4, 1])
            with col_biz_sl:
                st.slider(
                    "Business Ratio Slider",
                    min_value=0,
                    max_value=100,
                    value=max(0, min(100, int(st.session_state.biz_ratio_value))),
                    step=1,
                    key="biz_ratio_slider",
                    label_visibility="collapsed",
                    on_change=sync_biz_ratio_from_slider
                )
            with col_biz_in:
                st.number_input(
                    "BizRatio",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(st.session_state.biz_ratio_value),
                    step=1.0,
                    format="%.1f",
                    key="biz_ratio_input",
                    label_visibility="collapsed",
                    on_change=sync_biz_ratio_from_input
                )
            business_ratio = st.session_state.biz_ratio_value / 100.0
            st.caption(f"{st.session_state.biz_ratio_value:.1f}% businesses, {100 - st.session_state.biz_ratio_value:.1f}% private individuals")
        
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
                    priv_pn = st.slider("PN", 1.0, 5.0, DEFAULT_VALUES["priv_pn_value"], 0.1, key="sl_priv_pn", 
                                        label_visibility="collapsed", help="Internal ethics (1-5 scale)")
                    
                    st.markdown("**Social Norms**")
                    priv_sn = st.slider("SN", 1.0, 5.0, DEFAULT_VALUES["priv_sn_value"], 0.1, key="sl_priv_sn",
                                        label_visibility="collapsed", help="Perceived peer norms")
                    
                    st.markdown("**Societal Norms**")
                    priv_stn = st.slider("StN", 1.0, 5.0, DEFAULT_VALUES["priv_stn_value"], 0.1, key="sl_priv_stn",
                                         label_visibility="collapsed", help="Perceived societal norms")
                
                with col_p2:
                    st.markdown("**Service Orientation**")
                    priv_pso = st.slider("PSO", 1.0, 5.0, DEFAULT_VALUES["priv_pso_value"], 0.1, key="sl_priv_pso",
                                         label_visibility="collapsed", help="Perceived authority helpfulness")
                    
                    st.markdown("**Trustworthiness**")
                    priv_pt = st.slider("PT", 1.0, 5.0, DEFAULT_VALUES["priv_pt_value"], 0.1, key="sl_priv_pt",
                                        label_visibility="collapsed", help="Trust in tax authority")
                    
                    st.markdown("**Average Income (€)**")
                    priv_income = st.slider("Income", 20000, 80000, DEFAULT_VALUES["priv_income_value"], 1000, key="sl_priv_inc",
                                            label_visibility="collapsed")
                    
                    st.markdown("**Subjective Audit Prob (%)**")
                    priv_audit_belief = st.slider("Audit Belief", 0.0, 100.0, DEFAULT_VALUES["priv_audit_belief_value"], 1.0, key="sl_priv_audit_belief",
                                                   label_visibility="collapsed", help="Initial perceived audit probability")
            
            # --- Business Traits ---
            with st.expander("Business Owner Traits", expanded=False):
                col_b1, col_b2 = st.columns(2)
                
                with col_b1:
                    st.markdown("**Personal Norms**")
                    biz_pn = st.slider("PN", 1.0, 5.0, DEFAULT_VALUES["biz_pn_value"], 0.1, key="sl_biz_pn",
                                       label_visibility="collapsed")
                    
                    st.markdown("**Social Norms**")
                    biz_sn = st.slider("SN", 1.0, 5.0, DEFAULT_VALUES["biz_sn_value"], 0.1, key="sl_biz_sn",
                                       label_visibility="collapsed")
                    
                    st.markdown("**Societal Norms**")
                    biz_stn = st.slider("StN", 1.0, 5.0, DEFAULT_VALUES["biz_stn_value"], 0.1, key="sl_biz_stn",
                                        label_visibility="collapsed")
                
                with col_b2:
                    st.markdown("**Service Orientation**")
                    biz_pso = st.slider("PSO", 1.0, 5.0, DEFAULT_VALUES["biz_pso_value"], 0.1, key="sl_biz_pso",
                                        label_visibility="collapsed")
                    
                    st.markdown("**Trustworthiness**")
                    biz_pt = st.slider("PT", 1.0, 5.0, DEFAULT_VALUES["biz_pt_value"], 0.1, key="sl_biz_pt",
                                       label_visibility="collapsed")
                    
                    st.markdown("**Subjective Audit Prob (%)**")
                    biz_audit_belief = st.slider("Audit Belief", 0.0, 100.0, DEFAULT_VALUES["biz_audit_belief_value"], 1.0, key="sl_biz_audit_belief",
                                                  label_visibility="collapsed", help="Initial perceived audit probability")
            
            # --- SME Risk Model ---
            with st.expander("SME Risk Model", expanded=False):
                st.caption("Adjust risk score deltas for business characteristics")
                
                col_r1, col_r2 = st.columns(2)
                
                with col_r1:
                    st.markdown("**Base Risk**")
                    risk_base = st.slider("Base", 0.05, 0.35, DEFAULT_VALUES["risk_base_value"], 0.01, key="sl_risk_base",
                                          label_visibility="collapsed")
                    
                    st.markdown("**High-Risk Sector Δ**")
                    delta_sector = st.slider("Sector", 0.0, 0.30, DEFAULT_VALUES["delta_sector_value"], 0.01, key="sl_d_sector",
                                             label_visibility="collapsed")
                    
                    st.markdown("**Cash Intensive Δ**")
                    delta_cash = st.slider("Cash", 0.0, 0.20, DEFAULT_VALUES["delta_cash_value"], 0.01, key="sl_d_cash",
                                           label_visibility="collapsed")
                
                with col_r2:
                    st.markdown("**High Digitalisation Δ**")
                    delta_digi_high = st.slider("Digi High", -0.20, 0.0, DEFAULT_VALUES["delta_digi_high_value"], 0.01, key="sl_d_digi",
                                                label_visibility="collapsed")
                    
                    st.markdown("**Has Advisor Δ**")
                    delta_advisor = st.slider("Advisor", -0.20, 0.0, -DEFAULT_VALUES["delta_advisor_value"], 0.01, key="sl_d_adv",
                                              label_visibility="collapsed")
                    
                    st.markdown("**Prior Audit Δ**")
                    delta_audit = st.slider("Audit", -0.20, 0.0, -DEFAULT_VALUES["delta_audit_value"], 0.01, key="sl_d_audit",
                                            label_visibility="collapsed")
        
        # =====================================================
        # ACTION BAR
        # =====================================================
        
        st.markdown("<div style='height: 24px'></div>", unsafe_allow_html=True)
        st.divider()
        
        col1, col2, col3, spacer, col4 = st.columns([1, 1, 1, 2, 2])
        
        with col1:
            st.button("Import", use_container_width=True, key="btn_import")
        with col2:
            st.button("Export", use_container_width=True, key="btn_export")
        with col3:
            if st.button("Reset", use_container_width=True, key="btn_reset"):
                reset_to_defaults()
                st.rerun()
        with col4:
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
                    
                    # Norm Update Scales
                    "norm_update": {
                        "social_norm_scale": {
                            "private": sn_scale_priv,
                            "business": sn_scale_biz,
                        },
                        "societal_norm_scale": {
                            "private": stn_scale_priv,
                            "business": stn_scale_biz,
                        },
                    },
                    
                    # Traits - Private
                    "traits_private": {
                        "personal_norms_mean": priv_pn,
                        "social_norms_mean": priv_sn,
                        "societal_norms_mean": priv_stn,
                        "pso_mean": priv_pso,
                        "trust_mean": priv_pt,
                        "income_mean": priv_income,
                        "subjective_audit_prob_mean": priv_audit_belief,
                    },
                    
                    # Traits - Business
                    "traits_business": {
                        "personal_norms_mean": biz_pn,
                        "social_norms_mean": biz_sn,
                        "societal_norms_mean": biz_stn,
                        "pso_mean": biz_pso,
                        "trust_mean": biz_pt,
                        "subjective_audit_prob_mean": biz_audit_belief,
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
