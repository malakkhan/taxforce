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
        "run_value": 1, 
        
        # Behaviors
        "compliance_value": int(_cfg.behaviors.get("distribution", {"honest": 0.92})["honest"] * 100),
        
        # Enforcement Strategy
        "priv_audit_value": _cfg.enforcement["audit_rate"]["private"] * 100,
        "biz_audit_value": _cfg.enforcement["audit_rate"]["business"] * 100,
        "audit_depth_value": 0.28 * 100, # Default books prob
        
        # Service & Trust (New)
        "phone_sat_value": 80.0, # 80% default
        "web_qual_value": 3.2, # 3.2/5 default
        "transparency_value": False, # Default off (p_unfair = 0.3)
        
        # External Environment (Govt)
        "tax_rate_value": int(_cfg.enforcement["tax_rate"] * 100),
        "penalty_value": _cfg.enforcement["penalty_rate"],
        "biz_ratio_value": _cfg.simulation["business_ratio"] * 100,
        
        # Expert - Network
        "homophily_value": _cfg.network["homophily"],
        "degree_mean_value": _cfg.network["degree_mean"],
        "degree_std_value": _cfg.network["degree_std"],
        "social_influence_value": _cfg.social["social_influence"],
        
        # Expert - Risk & Traits
        "risk_aversion_value": _cfg.traits["private"]["risk_aversion"]["mean"],
        
        # Expert - Norms
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


def synced_slider_input(
    label: str,
    key: str,
    min_value,
    max_value,
    default,
    step,
    input_min=None,
    input_max=None,
    format_str: str = None,
    help_text: str = None,
):
    """
    Creates a slider + number input pair that stay in sync.
    Reset button is positioned absolutely to hug the right side of the input.
    """
    reset_flag_key = f"{key}_do_reset"
    if st.session_state.get(reset_flag_key, False):
        st.session_state[reset_flag_key] = False
        st.session_state[key] = default
    
    if key not in st.session_state:
        st.session_state[key] = default
    
    if isinstance(default, float):
        default_str = format_str % default if format_str else (f"{default:.2f}" if default != int(default) else str(int(default)))
    else:
        default_str = str(default)
    
    # Three columns: slider | input | reset button
    # Tight ratios that keep input and reset close together
    col_sl, col_in, col_reset = st.columns([4, 0.6, 0.4], gap="small")
    
    with col_sl:
        st.slider(
            f"{label} Slider",
            min_value=min_value,
            max_value=max_value,
            step=step,
            key=key,
            label_visibility="collapsed",
            help=help_text,
        )
    
    with col_in:
        input_kwargs = {
            "label": label,
            "min_value": input_min if input_min is not None else min_value,
            "max_value": input_max if input_max is not None else max_value,
            "value": st.session_state[key],
            "step": step,
            "key": f"{key}_input",
            "label_visibility": "collapsed",
        }
        if format_str:
            input_kwargs["format"] = format_str
            
        input_val = st.number_input(**input_kwargs)
        
        # Show default value centered below the input
        # Use negative margin to pull it up closer to input, then position text below
        st.markdown(
            f'''<div style="
                position: relative;
                width: 90px;
                height: 15px;
                margin-top: 4px;
            ">
                <span style="
                    position: absolute;
                    top: 0;
                    left: 50%;
                    transform: translateX(-50%);
                    font-size: 10px;
                    color: #718096;
                    white-space: nowrap;
                ">Default: {default_str}</span>
            </div>''',
            unsafe_allow_html=True
        )
        
        if input_val != st.session_state[key]:
            st.session_state[key] = max(min_value, min(max_value, input_val))
            st.rerun()
    
    with col_reset:
        reset_key = f"{key}_reset"
        # Include default value in tooltip since we removed the text below input
        if st.button("↻", key=reset_key, help=f"Reset to default: {default_str}"):
            st.session_state[reset_flag_key] = True
            st.rerun()
    
    return st.session_state[key]

def render():
    """Render the simulation configuration page with tiered settings."""
    
    # Create centered content area
    left_spacer, content, right_spacer = st.columns([1, 4, 1])
    
    with content:
        # Page header
        header_col, download_col, reset_col = st.columns([4, 1.2, 1])
        
        with header_col:
            st.markdown("""
                <div style="display:flex; align-items:baseline; gap:16px; padding-top: 10px; margin-bottom: 0px;">
                    <span style="font-size: 28px; font-weight: 700; color: #1A1A1A;">
                        Configure Simulation
                    </span>
                    <span style="font-size: 14px; color: #718096;">
                        Adjust parameters and run simulation
                    </span>
                </div>
            """, unsafe_allow_html=True)

        with download_col:
            from dashboard.utils.ui import render_download_button
            render_download_button()
            
        with reset_col:
            if st.button("Reset Defaults", use_container_width=True, key="btn_reset_header"):
                reset_to_defaults()
                st.rerun()
        
        # Horizontal separator
        st.markdown('<div style="border-bottom:1px solid #D1D9E0; margin-bottom:24px; margin-top:-12px;"></div>', unsafe_allow_html=True)
        
        # =====================================================
        # 1. SETUP - Always Visible
        # =====================================================
        
        # Initialize session state for synced values
        if "pop_value" not in st.session_state:
            reset_to_defaults()

        with st.container(border=True):
            st.markdown("### Simulation Setup")
            # st.caption("Define the scale and duration of the simulation")
            st.write("")

            # --- Population Size ---
            # --- Population Size ---
            st.markdown("**Population Size** · Number of agents", help="Literature uses population sizes from 1000 to 5000. Larger populations obey statistical properties better but run slower.")
            n_agents = synced_slider_input(
                label="Pop", key="pop_slider",
                min_value=500, max_value=2500,
                default=DEFAULT_VALUES["pop_value"],
                step=50,
                input_max=100000,
                help_text="Literature uses population sizes from 1000 to 5000. Larger populations obey statistical properties better but run slower."
            )
             
            # --- Simulation Duration ---
            # --- Simulation Duration ---
            st.markdown("**Simulation Duration** · Number of steps (years)", help="Literature uses timesteps in the range of 50 to 100. Each timestep represents one fiscal year.")
            n_steps = synced_slider_input(
                label="Dur", key="dur_slider",
                min_value=10, max_value=100,
                default=DEFAULT_VALUES["dur_value"],
                step=5,
                input_max=1000,
                help_text="Literature uses timesteps in the range of 50 to 100. Each timestep represents one fiscal year."
            )
            
            # --- Repetitions ---
            # --- Repetitions ---
            st.markdown("**Repetitions** · Number of simulations to run", help="The simulation can be repeated numerous times to provide aggregate scores across various random scenarios.")
            n_runs = synced_slider_input(
                label="Runs", key="run_slider",
                min_value=1, max_value=10,
                default=DEFAULT_VALUES["run_value"],
                step=1, input_max=100,
                help_text="The simulation can be repeated numerous times to provide aggregate scores (see final metric definitions in Phase 4) across various scenarios."
            )

        st.markdown("<div style='height: 12px'></div>", unsafe_allow_html=True)

        # =====================================================
        # 2. TAX AUTHORITY STRATEGY (The Controls)
        # =====================================================
        with st.expander("Tax Authority Strategy", expanded=True):
            # st.caption("Operational controls available to the Tax Authority")
            
            # --- Enforcement Intensity ---
            st.markdown("#### Enforcement Intensity")
            
            st.markdown("**Private Audit Rate** (%)", help="Jaarreportage 2024: audit rate for private individuals is 2.4% (manual+automated) or 0.91% (manual). Defaults to 1%.")
            priv_audit_raw = synced_slider_input(
                label="Priv", key="priv_audit_slider",
                min_value=0.0, max_value=10.0,
                default=DEFAULT_VALUES["priv_audit_value"],
                step=0.1, input_max=100.0, format_str="%.1f",
                help_text="Jaarreportage 2024: audit rate for private individuals is 2.4% (manual+automated) or 0.91% (manual). Defaults to 1%."
            )
            audit_private = priv_audit_raw / 100.0

            st.write("")

            st.markdown("**Business Audit Rate** (%)", help="Jaarreportage 2024: audit rate for MKBs is 0.46%. Defaults to 1%.")
            biz_audit_raw = synced_slider_input(
                label="Biz", key="biz_audit_slider",
                min_value=0.0, max_value=5.0,
                default=DEFAULT_VALUES["biz_audit_value"],
                step=0.01, input_max=100.0, format_str="%.2f",
                help_text="Jaarreportage 2024: audit rate for MKBs is 0.46%. Defaults to 1%."
            )
            audit_business = biz_audit_raw / 100.0

            st.markdown("**Audit Focus** (Quantity vs Quality)", help="Percentage of budget allocated to deep 'Book Investigations' vs simple 'Admin Checks'")
            audit_depth_raw = synced_slider_input(
                label="Depth", key="audit_depth_slider",
                min_value=0.0, max_value=100.0,
                default=DEFAULT_VALUES["audit_depth_value"],
                step=5.0, format_str="%.0f"
            )
            audit_depth_books = audit_depth_raw / 100.0
            st.caption(f"Strategy: {100-audit_depth_raw:.0f}% Admin Checks / {audit_depth_raw:.0f}% Book Investigations")

            st.write("")
            st.markdown("#### Audit Selection Strategy", help="Method of selecting agents to audit")
            audit_strategy = st.selectbox(
                "Method",
                options=["random", "risk_based", "network"],
                format_func=lambda x: {
                    "random": "Random · Uniform probability within occupation",
                    "risk_based": "Risk-Based · Focus on high-risk profiles",
                    "network": "Network · Target nodes with highest closeness centrality"
                }.get(x, x),
                key="sel_audit",
                label_visibility="collapsed",
                help="Choose how agents are selected for audit: Random (uniform), Risk-Based (top risk scores), or Network (closeness centrality)."
            )

            st.write("")
            st.markdown("#### Service & Prevention", help="Operational controls available to the Tax Authority")
            
            st.markdown("**Call Center Quality** (% Satisfied)", help="Probability of satisfaction (>=3 on Likert scale) for telephone interactions as in Jaarreportage 2024. Default 80%.")
            phone_sat = synced_slider_input(
                label="Phone", key="phone_sat_slider",
                min_value=50.0, max_value=99.0,
                default=DEFAULT_VALUES["phone_sat_value"],
                step=1.0, format_str="%.0f",
                help_text="Probability of satisfaction (>=3 on Likert scale) for telephone interactions as in Jaarreportage 2024. Default 80%."
            )

            st.markdown("**Web Portal Experience** (1-5 Stars)", help="Mean satisfaction score (1-5) for web services as in Jaarreportage 2024. Default 3.2.")
            web_qual = synced_slider_input(
                label="Web", key="web_qual_slider",
                min_value=1.0, max_value=5.0,
                default=DEFAULT_VALUES["web_qual_value"],
                step=0.1, format_str="%.1f",
                help_text="Mean satisfaction score (1-5) for web services as in Jaarreportage 2024. Default 3.2."
            )

            st.write("")
            is_transparent = st.toggle("Launch Fairness/Transparency Campaign", 
                                     value=st.session_state.get("transparency_toggle", False),
                                     key="transparency_toggle",
                                     help="Reduces the perception of unfairness when audited (Trust repair)")

        # =====================================================
        # 3. EXTERNAL ENVIRONMENT (Government)
        # =====================================================
        with st.expander("Fiscal Environment", expanded=False):
            # st.caption("Fiscal policy and economic conditions set by the Government")
            
            st.markdown("**Fiscal Policy**")
            
            st.markdown("Income Tax Rate (%)", help="All agents will be subject to the same tax rate. Defaults to 0.3 (30%).")
            tax_rate_raw = synced_slider_input(
                label="Tax", key="tax_slider",
                min_value=10, max_value=60,
                default=DEFAULT_VALUES["tax_rate_value"],
                step=5, input_max=100,
                help_text="All agents will be subject to the same tax rate. Defaults to 0.3 (30%)."
            )
            tax_rate = tax_rate_raw / 100.0
            
            st.write("")
            
            st.markdown("Penalty Multiplier (x)", help="Multiplier upon tax rate for fines. Fine = fine rate * tax rate * undeclared amount. Default 3.")
            penalty_rate = synced_slider_input(
                label="Penalty", key="penalty_slider",
                min_value=1.0, max_value=5.0,
                default=DEFAULT_VALUES["penalty_value"],
                step=0.5, input_max=20.0,
                help_text="Multiplier upon tax rate for fines. Fine = fine rate * tax rate * undeclared amount. Default 3."
            )

            st.markdown("---")
            st.markdown("**Economic Context**")
            
            # Business Ratio Logic
            if "biz_ratio_value" not in st.session_state:
                st.session_state.biz_ratio_value = DEFAULT_VALUES["biz_ratio_value"]
            
            def sync_biz_ratio_from_slider():
                st.session_state.biz_ratio_value = st.session_state.biz_ratio_slider
            def sync_biz_ratio_from_input():
                st.session_state.biz_ratio_value = st.session_state.biz_ratio_input
            
            st.markdown("**Private/SME Ratio** · Percentage of SMEs (%)", help="Approximately 0.134% of Dutch labor force is self-employed as per CBS 2024 data. Default of 10%.")
            col_biz_sl, col_biz_in = st.columns([4, 1])
            with col_biz_sl:
                st.slider(
                    "Business Ratio Slider",
                    min_value=0, max_value=100,
                    value=max(0, min(100, int(st.session_state.biz_ratio_value))),
                    step=1,
                    key="biz_ratio_slider",
                    label_visibility="collapsed",
                    on_change=sync_biz_ratio_from_slider,
                    help="Approximately 0.134% of Dutch labor force is self-employed as per CBS 2024 data. Default of 10%."
                )
            with col_biz_in:
                st.number_input(
                    "BizRatio", min_value=0.0, max_value=100.0,
                    value=float(st.session_state.biz_ratio_value),
                    step=1.0, format="%.1f", key="biz_ratio_input",
                    label_visibility="collapsed", on_change=sync_biz_ratio_from_input
                )
            business_ratio = st.session_state.biz_ratio_value / 100.0

        # =====================================================
        # 4. EXPERT CALIBRATION (Model)
        # =====================================================
        with st.expander("Expert Calibration", expanded=False):
            # st.caption("Fine-tune model parameters, social dynamics, and psychometrics")
            
            # Psychometrics
            st.markdown("#### Traits")
            st.markdown("**Risk Aversion**", help="Mean for initial sampling from normal distribution clamped between 0.5 to 5: Default Mean 2.0, Std 1.0.")
            risk_aversion = synced_slider_input(
                label="Risk", key="risk_slider",
                min_value=0.5, max_value=5.0,
                default=DEFAULT_VALUES["risk_aversion_value"],
                step=0.1, help_text="Mean for initial sampling from normal distribution clamped between 0.5 to 5: DefaultMean 2.0, Std 1.0.",
            )
            
            st.markdown("**Baseline Honesty**", help="Percentage of agents initialized as 'honest'.")
            compliance_raw = synced_slider_input(
                label="Compliance", key="compliance_slider",
                min_value=0, max_value=100,
                default=DEFAULT_VALUES["compliance_value"],
                step=5,
                help_text="Percentage of agents initialized as 'honest'."
            )
            honest_ratio = compliance_raw / 100.0

            st.markdown("#### Social Dynamics")
            st.markdown("Social Influence", help="Strength of social influence (0-1). 1 = fully adopts median of neighbors. 0 = independent.")
            social_influence = synced_slider_input(
                label="Influence", key="soc_inf_slider",
                min_value=0.0, max_value=1.0,
                default=DEFAULT_VALUES["social_influence_value"],
                step=0.05,
                help_text="Strength of social influence (0-1). 1 = fully adopts median of neighbors. 0 = independent."
            )
            
            st.markdown("Homophily", help="Percentage of an agent's connections to be selected from within the same group (Occupation/Business Sector).")
            homophily = synced_slider_input(
                label="Homophily", key="net_homo",
                min_value=0.0, max_value=1.0,
                default=DEFAULT_VALUES["homophily_value"],
                step=0.05,
                help_text="Percentage of an agent's connections to be selected from within the same group (Occupation/Business Sector)."
            )
            
            st.write("")
            
            st.markdown("Avg Connections", help="Target avg connections per agent. Lognormal distribution (Default Mean 86.27, Std 64.99).")
            degree_mean = synced_slider_input(
                label="Degree", key="net_deg",
                min_value=5.0, max_value=300.0,
                default=DEFAULT_VALUES["degree_mean_value"],
                step=5.0,
                help_text="Target avg connections per agent. Lognormal distribution (DefaultMean 86.27, Std 64.99)."
            )

            # Deep Traits (Nested)
            with st.expander("Deep Trait Calibration"):
                 # --- Private Individual Traits ---
                st.markdown("**Private Individual Traits**")
                col_p1, col_p2, _ = st.columns([10, 10, 0.5], gap="large")
                with col_p1:
                    st.markdown("Personal Norms", help="Private Personal Norms. Normal dist, Default Mean 3.40, SD 1.15. (Gangl et al. 2013)")
                    priv_pn = st.slider("PN", 1.0, 5.0, DEFAULT_VALUES["priv_pn_value"], 0.1, key="sl_priv_pn", label_visibility="collapsed", help="Private Personal Norms. Normal dist, Default Mean 3.40, SD 1.15. (Gangl et al. 2013)")
                    st.markdown("Social Norms", help="Private Social Norms. Normal dist, Default Mean 3.42, SD 1.06. (Gangl et al. 2013)")
                    priv_sn = st.slider("SN", 1.0, 5.0, DEFAULT_VALUES["priv_sn_value"], 0.1, key="sl_priv_sn", label_visibility="collapsed", help="Private Social Norms. Normal dist, Default Mean 3.42, SD 1.06. (Gangl et al. 2013)")
                    st.markdown("Societal Norms", help="Private Societal Norms. Normal dist, Default Mean 3.97, SD 1.01. (Gangl et al. 2013)")
                    priv_stn = st.slider("StN", 1.0, 5.0, DEFAULT_VALUES["priv_stn_value"], 0.1, key="sl_priv_stn", label_visibility="collapsed", help="Private Societal Norms. Normal dist, Default Mean 3.97, SD 1.01. (Gangl et al. 2013)")
                with col_p2:
                    st.markdown("Perceived Service Orientation", help="Private PSO. Normal dist, Default Mean 3.22, SD 0.68. (Gangl et al. 2013)")
                    priv_pso = st.slider("PSO", 1.0, 5.0, DEFAULT_VALUES["priv_pso_value"], 0.1, key="sl_priv_pso", label_visibility="collapsed", help="Private PSO. Normal dist, Default Mean 3.22, SD 0.68. (Gangl et al. 2013)")
                    st.markdown("Perceived Trustworthiness", help="Private Trust. Normal dist, Default Mean 3.37, SD 0.69. (Gangl et al. 2013)")
                    priv_pt = st.slider("PT", 1.0, 5.0, DEFAULT_VALUES["priv_pt_value"], 0.1, key="sl_priv_pt", label_visibility="collapsed", help="Private Trust. Normal dist, Default Mean 3.37, SD 0.69. (Gangl et al. 2013)")
                    st.markdown("Subjective Audit Probability", help="Private Subjective Audit Prob. Default Mean ~60.75, SD 22.00.")
                    priv_audit_belief = st.slider("Belief", 0.0, 100.0, DEFAULT_VALUES["priv_audit_belief_value"], 1.0, key="sl_priv_audit_belief", label_visibility="collapsed", help="Private Subjective Audit Prob. Default Mean ~60.75, SD 22.00.")

                st.markdown("---")
                st.markdown("**Business Traits**")
                col_b1, col_b2, _ = st.columns([10, 10, 0.5], gap="large")
                with col_b1:
                    st.markdown("Personal Norms", help="Business Personal Norms. Normal dist, Default Mean 3.82, SD 1.04. (Gangl et al. 2013)")
                    biz_pn = st.slider("PN", 1.0, 5.0, DEFAULT_VALUES["biz_pn_value"], 0.1, key="sl_biz_pn", label_visibility="collapsed", help="Business Personal Norms. Normal dist, Default Mean 3.82, SD 1.04. (Gangl et al. 2013)")
                    st.markdown("Social Norms", help="Business Social Norms. Normal dist, Default Mean 3.82, SD 1.02. (Gangl et al. 2013)")
                    biz_sn = st.slider("SN", 1.0, 5.0, DEFAULT_VALUES["biz_sn_value"], 0.1, key="sl_biz_sn", label_visibility="collapsed", help="Business Social Norms. Normal dist, Default Mean 3.82, SD 1.02. (Gangl et al. 2013)")
                    st.markdown("Societal Norms", help="Business Societal Norms. Normal dist, Default Mean 4.12, SD 0.98. (Gangl et al. 2013)")
                    biz_stn = st.slider("StN", 1.0, 5.0, DEFAULT_VALUES["biz_stn_value"], 0.1, key="sl_biz_stn", label_visibility="collapsed", help="Business Societal Norms. Normal dist, Default Mean 4.12, SD 0.98. (Gangl et al. 2013)")
                with col_b2:
                    st.markdown("Perceived Service Orientation", help="Business PSO. Normal dist, Default Mean 3.18, SD 0.67. (Gangl et al. 2013)")
                    biz_pso = st.slider("PSO", 1.0, 5.0, DEFAULT_VALUES["biz_pso_value"], 0.1, key="sl_biz_pso", label_visibility="collapsed", help="Business PSO. Normal dist, Default Mean 3.18, SD 0.67. (Gangl et al. 2013)")
                    st.markdown("Perceived Trustworthiness", help="Business Trust. Normal dist, Default Mean 3.37, SD 0.69. (Gangl et al. 2013)")
                    biz_pt = st.slider("PT", 1.0, 5.0, DEFAULT_VALUES["biz_pt_value"], 0.1, key="sl_biz_pt", label_visibility="collapsed", help="Business Trust. Normal dist, Default Mean 3.37, SD 0.69. (Gangl et al. 2013)")
                    st.markdown("Subjective Audit Probability", help="Business Subjective Audit Prob. Default Mean ~63.50, SD 23.00.")
                    biz_audit_belief = st.slider("Belief", 0.0, 100.0, DEFAULT_VALUES["biz_audit_belief_value"], 1.0, key="sl_biz_audit_belief", label_visibility="collapsed", help="Business Subjective Audit Prob. Default Mean ~63.50, SD 23.00.")

                # Hidden defaults for unused params to keep code working
                degree_std = DEFAULT_VALUES["degree_std_value"]
                risk_base = DEFAULT_VALUES["risk_base_value"]
                delta_sector = DEFAULT_VALUES["delta_sector_value"]
                delta_cash = DEFAULT_VALUES["delta_cash_value"]
                delta_digi_high = DEFAULT_VALUES["delta_digi_high_value"]
                delta_advisor = DEFAULT_VALUES["delta_advisor_value"]
                delta_audit = DEFAULT_VALUES["delta_audit_value"]
                social_norm_scale_priv = DEFAULT_VALUES["social_norm_scale_priv"]
                social_norm_scale_biz = DEFAULT_VALUES["social_norm_scale_biz"]
                societal_norm_scale_priv = DEFAULT_VALUES["societal_norm_scale_priv"]
                societal_norm_scale_biz = DEFAULT_VALUES["societal_norm_scale_biz"]
                priv_income = DEFAULT_VALUES["priv_income_value"]

        # =====================================================
        # ACTION BAR
        # =====================================================
        # =====================================================
        # ACTION BAR
        # =====================================================
        # Custom tight separator matching results.py
        st.markdown('<hr style="margin-top: 12px; margin-bottom: 8px; border: none; border-top: 1px solid #D1D9E0;">', unsafe_allow_html=True)
        
        _, col_start = st.columns([5, 2])

        with col_start:
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
                    "audit_depth_books": audit_depth_books, # New: Pass ratio
                    
                    # Service (New)
                    "phone_sat": phone_sat,
                    "web_qual": web_qual,
                    "transparency": is_transparent,
                    
                    # Expert - Network
                    "homophily": homophily,
                    "degree_mean": degree_mean,
                    "degree_std": degree_std,
                    "social_influence": social_influence,
                    "pso_boost": 0.0, # Deprecated by detailed service
                    "trust_boost": 0.0, # Deprecated by transparency
                    
                    # Expert - Risk
                    "risk_aversion": risk_aversion,

                    # Norm Update Scales (Hidden defaults)
                    "norm_update": {
                        "social_norm_scale": {
                            "private": social_norm_scale_priv,
                            "business": social_norm_scale_biz,
                        },
                        "societal_norm_scale": {
                            "private": societal_norm_scale_priv,
                            "business": societal_norm_scale_biz,
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
                    
                    # SME Risk (Hidden defaults)
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
