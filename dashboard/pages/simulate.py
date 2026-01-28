"""
Simulate Page - Configure simulation settings.
Three-tier settings hierarchy with nested expanders.
Professional design for Tax Authority dashboard.
"""
import json
import streamlit as st
import streamlit_nested_layout  # Enables nested expanders
from scipy.stats import norm
import sys
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from core.config import SimulationConfig
from dataclasses import dataclass
from typing import Optional


@dataclass
class BudgetConfig:
    """Configuration for budget mode in synced_slider_input."""
    cost_key: str           # Session state key for unit cost
    unit_key: str           # Session state key for unit size
    param_format: str = "%.1f%%"  # Format string for derived value display
    param_baseline: float = 0.0   # Baseline to add to derived value
    param_cap: float = 100.0       # Maximum derived value


# Load defaults from actual config files
_cfg = SimulationConfig.default()

def vertical_separator(rows=1):
    """
    Renders a vertical line separator with height calculated based on number of rows.
    Approx 100px per row covers labels + inputs + padding.
    """
    height_px = rows * 70
    st.markdown(
        f'<div style="border-left: 1px solid #D1D9E0; height: {height_px}px; margin: 0 auto; width: 1px;"></div>', 
        unsafe_allow_html=True
    )

def _get_default_values():
    """Build default values dict from core config."""
    return {
        # Simulation
        "pop_value": _cfg.simulation["n_agents"],
        "dur_value": _cfg.simulation["n_steps"],
        "run_value": 1,
        
        # Behaviors - TCI thresholds
        "tci_threshold_priv": _cfg.behaviors["compliance_inclination"]["private"]["threshold"],
        "tci_threshold_biz": _cfg.behaviors["compliance_inclination"]["business"]["threshold"],
        
        # Enforcement Strategy
        "priv_audit_value": _cfg.enforcement["audit_rate"]["private"] * 100,
        "biz_audit_value": _cfg.enforcement["audit_rate"]["business"] * 100,
        "audit_depth_value": _cfg.enforcement["audit_type_probs"]["books"] * 100,
        "audit_strategy": _cfg.enforcement["audit_strategy"],
        
        # Interventions - Deterrence Letters
        "letter_enabled": _cfg.interventions["letter_deterrence"]["enabled"],
        "letter_rate_priv": _cfg.interventions["letter_deterrence"]["rate"]["private"] * 100,
        "letter_rate_biz": _cfg.interventions["letter_deterrence"]["rate"]["business"] * 100,
        "letter_strategy": _cfg.interventions["letter_deterrence"]["selection_strategy"],
        # Advanced Letter Effects
        "letter_eff_perm": _cfg.interventions["letter_deterrence"]["effects"]["subjective_audit_prob_permanent"],
        "letter_eff_temp": _cfg.interventions["letter_deterrence"]["effects"]["subjective_audit_prob_temporary"],
        "letter_eff_trust": _cfg.interventions["letter_deterrence"]["effects"]["trust_delta"],
        
        # Interventions - Phone Calls
        "phone_enabled": _cfg.interventions["call"]["enabled"],
        "phone_rate_priv": _cfg.interventions["call"]["rate"]["private"] * 100,
        "phone_rate_biz": _cfg.interventions["call"]["rate"]["business"] * 100,
        "phone_strategy": _cfg.interventions["call"]["selection_strategy"],
        # Advanced Phone Effects
        "phone_sat_delta": _cfg.interventions["call"]["effects"]["satisfied"]["pso_delta"],
        "phone_dissat_delta": _cfg.interventions["call"]["effects"]["dissatisfied"]["pso_delta"],
        "phone_eff_audit_temp": _cfg.interventions["call"]["effects"]["satisfied"]["subjective_audit_prob_temporary"],
        
        # Service & Trust
        "phone_sat_value": _cfg.pso_update["private"]["phone_satisfied_prob"] * 100,
        "web_qual_priv_value": _cfg.pso_update["private"]["webcare_mean"],
        "web_qual_biz_value": _cfg.pso_update["business"]["webcare_mean"],
        "transparency_value": False,
        "huba_delta": _cfg.pso_update["huba_delta"],
        
        # External Environment
        "tax_rate_value": int(_cfg.enforcement["tax_rate"] * 100),
        "penalty_value": _cfg.enforcement["penalty_rate"],
        "biz_ratio_value": _cfg.simulation["business_ratio"] * 100,
        
        # Advanced: Belief Dynamics
        "belief_mu": _cfg.belief_update["mu"],
        "belief_drift": _cfg.belief_update["audit_prob_drift_rate"],
        "belief_signal": _cfg.belief_update["audit_signal_strength"],
        "belief_perception": _cfg.belief_update["perception_weight"],
        "belief_delta": _cfg.belief_update["audit_prob_response_delta"],
        "belief_target": _cfg.belief_update["audit_target_prob"],
        
        # Advanced: PSO/Trust
        "pso_sigma": _cfg.pso_update["sigma_pso"],
        "pso_drift": _cfg.pso_update["pso_drift_rate"],
        "trust_sigma": _cfg.trust_update["sigma_trust"],
        "trust_punfair": _cfg.trust_update["p_unfair"],
        
        # Advanced: Network
        "homophily_value": _cfg.network["homophily"],
        "degree_mean_value": _cfg.network["degree_mean"],
        "degree_std_value": _cfg.network["degree_std"],
        "social_influence_value": _cfg.social["social_influence"],
        
        # Advanced: SME Opportunity
        "sme_opp_base_slider": _cfg.sme["opportunity"]["base"],
        "sme_opp_min": _cfg.sme["opportunity"]["min"],
        "sme_opp_max": _cfg.sme["opportunity"]["max"],
        "sme_opp_cash": _cfg.sme["opportunity"]["cash_bonus"],
        "sme_opp_digi_low": _cfg.sme["opportunity"]["low_digi_bonus"],
        "sme_opp_digi_high": abs(_cfg.sme["opportunity"]["high_digi_penalty"]),
        "sme_opp_high_risk": _cfg.sme["opportunity"]["high_risk_sector_bonus"],
        "sme_opp_micro": _cfg.sme["opportunity"]["micro_bonus"],

        # Advanced: Risk & Traits
        "risk_aversion_value": _cfg.traits["private"]["risk_aversion"]["mean"],
        "risk_aversion_std": _cfg.traits["private"]["risk_aversion"]["std"],
        "tci_weight_dishonest": 0.5, # Default manual value for now
        
        # Traits - Private (Mean & Std)
        "priv_audit_belief_value": float(_cfg.traits["private"]["subjective_audit_prob"]["mean"]),
        "priv_audit_belief_std": float(_cfg.traits["private"]["subjective_audit_prob"]["std"]),
        "priv_pn_value": _cfg.traits["private"]["personal_norms"]["mean"],
        "priv_pn_std": _cfg.traits["private"]["personal_norms"]["std"],
        "priv_sn_value": _cfg.traits["private"]["social_norms"]["mean"],
        "priv_sn_std": _cfg.traits["private"]["social_norms"]["std"],
        "priv_stn_value": _cfg.traits["private"]["societal_norms"]["mean"],
        "priv_stn_std": _cfg.traits["private"]["societal_norms"]["std"],
        "priv_pso_value": _cfg.traits["private"]["pso"]["mean"],
        "priv_pso_std": _cfg.traits["private"]["pso"]["std"],
        "priv_pt_value": _cfg.traits["private"]["p_trust"]["mean"],
        "priv_pt_std": _cfg.traits["private"]["p_trust"]["std"],
        "priv_risk_value": _cfg.traits["private"]["risk_aversion"]["mean"],
        "priv_risk_std": _cfg.traits["private"]["risk_aversion"]["std"],
        
        # Traits - Business (Mean & Std)
        "biz_audit_belief_value": float(_cfg.traits["business"]["subjective_audit_prob"]["mean"]),
        "biz_audit_belief_std": float(_cfg.traits["business"]["subjective_audit_prob"]["std"]),
        "biz_pn_value": _cfg.traits["business"]["personal_norms"]["mean"],
        "biz_pn_std": _cfg.traits["business"]["personal_norms"]["std"],
        "biz_sn_value": _cfg.traits["business"]["social_norms"]["mean"],
        "biz_sn_std": _cfg.traits["business"]["social_norms"]["std"],
        "biz_stn_value": _cfg.traits["business"]["societal_norms"]["mean"],
        "biz_stn_std": _cfg.traits["business"]["societal_norms"]["std"],
        "biz_pso_value": _cfg.traits["business"]["pso"]["mean"],
        "biz_pso_std": _cfg.traits["business"]["pso"]["std"],
        "biz_pt_value": _cfg.traits["business"]["p_trust"]["mean"],
        "biz_pt_std": _cfg.traits["business"]["p_trust"]["std"],
        "biz_risk_value": _cfg.traits["business"]["risk_aversion"]["mean"],
        "biz_risk_std": _cfg.traits["business"]["risk_aversion"]["std"],
        
        # Missing Widget Keys (Required for render)
        "sl_priv_audit_belief": float(_cfg.traits["private"]["subjective_audit_prob"]["mean"]),
        "sl_biz_audit_belief": float(_cfg.traits["business"]["subjective_audit_prob"]["mean"]),
        
        # Widget Key Aliases (For conditional widgets with mismatched keys)
        "tci_threshold_priv_slider": _cfg.behaviors["compliance_inclination"]["private"]["threshold"],
        "tci_threshold_biz_slider": _cfg.behaviors["compliance_inclination"]["business"]["threshold"],
        
        # Private Traits (Explicit Widget Keys)
        "priv_audit_mean": float(_cfg.traits["private"]["subjective_audit_prob"]["mean"]),
        "priv_audit_std": float(_cfg.traits["private"]["subjective_audit_prob"]["std"]),
        "priv_pn_mean": _cfg.traits["private"]["personal_norms"]["mean"],
        "priv_pn_std": _cfg.traits["private"]["personal_norms"]["std"],
        "priv_sn_mean": _cfg.traits["private"]["social_norms"]["mean"],
        "priv_sn_std": _cfg.traits["private"]["social_norms"]["std"],
        "priv_stn_mean": _cfg.traits["private"]["societal_norms"]["mean"],
        "priv_stn_std": _cfg.traits["private"]["societal_norms"]["std"],
        "priv_pso_mean": _cfg.traits["private"]["pso"]["mean"],
        "priv_pso_std": _cfg.traits["private"]["pso"]["std"],
        "priv_pt_mean": _cfg.traits["private"]["p_trust"]["mean"],
        "priv_pt_std": _cfg.traits["private"]["p_trust"]["std"],
        
        # Business Traits (Explicit Widget Keys)
        "biz_audit_mean": float(_cfg.traits["business"]["subjective_audit_prob"]["mean"]),
        "biz_audit_std": float(_cfg.traits["business"]["subjective_audit_prob"]["std"]),
        "biz_pn_mean": _cfg.traits["business"]["personal_norms"]["mean"],
        "biz_pn_std": _cfg.traits["business"]["personal_norms"]["std"],
        "biz_sn_mean": _cfg.traits["business"]["social_norms"]["mean"],
        "biz_sn_std": _cfg.traits["business"]["social_norms"]["std"],
        "biz_stn_mean": _cfg.traits["business"]["societal_norms"]["mean"],
        "biz_stn_std": _cfg.traits["business"]["societal_norms"]["std"],
        "biz_pso_mean": _cfg.traits["business"]["pso"]["mean"],
        "biz_pso_std": _cfg.traits["business"]["pso"]["std"],
        "biz_pt_mean": _cfg.traits["business"]["p_trust"]["mean"],
        "biz_pt_std": _cfg.traits["business"]["p_trust"]["std"],
        
        # Legacy Aliases (Legacy support)
        "risk_slider": _cfg.traits["private"]["risk_aversion"]["mean"],
        "sl_priv_pn": _cfg.traits["private"]["personal_norms"]["mean"],
        "sl_priv_pso": _cfg.traits["private"]["pso"]["mean"],
        "sl_priv_pt": _cfg.traits["private"]["p_trust"]["mean"],
        "sl_biz_pn": _cfg.traits["business"]["personal_norms"]["mean"],
        "sl_biz_pso": _cfg.traits["business"]["pso"]["mean"],
        "sl_biz_pt": _cfg.traits["business"]["p_trust"]["mean"],
        
        # More Aliases (Network, Interventions, Toggles)
        "transparency_toggle": False,
        "error_enabled": _cfg.interventions.get("error_model", {}).get("enabled", False), # Safety default
        
        "letter_rate_priv_slider": _cfg.interventions["letter_deterrence"]["rate"]["private"] * 100,
        "letter_rate_biz_slider": _cfg.interventions["letter_deterrence"]["rate"]["business"] * 100,
        "phone_rate_priv_slider": _cfg.interventions["call"]["rate"]["private"] * 100,
        "phone_rate_biz_slider": _cfg.interventions["call"]["rate"]["business"] * 100,
        
        "soc_inf_slider": _cfg.social["social_influence"],
        "net_homo": _cfg.network["homophily"],
        "net_deg": _cfg.network["degree_mean"],
        "net_std": _cfg.network["degree_std"],
        
        "risk_base": _cfg.sme["base_risk_baseline"],
        "delta_sector": _cfg.sme["delta_sector_high_risk"],
        "delta_cash": _cfg.sme["delta_cash_intensive"],
        "delta_digi_high": _cfg.sme["delta_digi_high"],
        "delta_advisor": _cfg.sme["delta_advisor_yes"],
        "delta_audit": _cfg.sme["delta_audit_books"],
        
        # SME Risk Modifiers
        "risk_base_value": _cfg.sme["base_risk_baseline"],
        "delta_sector_value": _cfg.sme["delta_sector_high_risk"],
        "delta_cash_value": _cfg.sme["delta_cash_intensive"],
        "delta_digi_high_value": _cfg.sme["delta_digi_high"],
        "delta_advisor_value": _cfg.sme["delta_advisor_yes"],
        "delta_audit_value": _cfg.sme["delta_audit_books"],
        
        # Error Model
        # Error Model - Correctly accessing from root config_data, not simulation
        "error_enabled": _cfg.config_data.get("error_model", {}).get("enabled", False),
        "error_rate_priv": _cfg.config_data.get("error_model", {}).get("private", {}).get("base", 0.005) * 100,
        "error_rate_biz": _cfg.config_data.get("error_model", {}).get("business", {}).get("base", 0.35) * 100,
        "error_mag_min": _cfg.config_data.get("error_model", {}).get("magnitude", {}).get("min", 0.12) * 100,
        "error_mag_max": _cfg.config_data.get("error_model", {}).get("magnitude", {}).get("max", 0.23) * 100,
        "error_under_prob": _cfg.config_data.get("error_model", {}).get("under_report_prob", 0.90) * 100,
        
        # Budget Game Mode
        "budget_mode": False,
        "budget_total": 75000,
        # Unit Costs ($ per unit) - Enforcement
        "cost_audit_priv": 12000,
        "unit_audit_priv": 1.0,
        "cost_audit_biz": 15000,
        "unit_audit_biz": 1.0,
        "cost_audit_deep": 3000,
        "unit_audit_deep": 10.0,
        # Unit Costs - Interventions
        "cost_letter": 500,
        "unit_letter": 1.0,
        "cost_phone": 3000,
        "unit_phone": 1.0,
        # Unit Costs - Services
        "cost_call_sat": 200,
        "unit_call_sat": 1.0,
        "cost_web": 250,
        "unit_web": 0.1,
        "cost_huba": 10000,
        # Budget Spending Allocations (initialized to approximate defaults)
        "spend_audit_priv": 12000,
        "spend_audit_biz": 15000,
        "spend_audit_deep": 8400,
        "spend_letter_priv": 1000,
        "spend_letter_biz": 1500,
        "spend_phone_priv": 3000,
        "spend_phone_biz": 9000,
        "spend_call_sat": 6000,
        "spend_web_priv": 3000,
        "spend_web_biz": 3750,
        "spend_huba": 0,
    }

DEFAULT_VALUES = _get_default_values()

def reset_to_defaults():
    """Reset all session state values to their defaults and trigger local slider resets."""
    # 1. Reset standard session state keys from DEFAULT_VALUES
    for key, value in DEFAULT_VALUES.items():
        st.session_state[key] = value
    
    # 2. Trigger local reset for all UI sliders that have been initialized
    # This ensures they pick up their 'default' argument and refresh handle via version increment.
    sync_keys = [k for k in st.session_state.keys() if k.endswith("_sync_v")]
    for k in sync_keys:
        master_key = k.rsplit("_sync_v", 1)[0]
        st.session_state[f"{master_key}_do_reset"] = True


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
    budget_config: Optional[BudgetConfig] = None,
):
    """
    Creates a slider + number input pair that stay in sync.
    Reset button is positioned absolutely to hug the right side of the input.
    
    If budget_config is provided, shows derived metric text below the slider.
    """
    # 1. State Maintenance & Synchronization Architecture
    if key not in st.session_state:
        st.session_state[key] = default
    if f"{key}_input" not in st.session_state:
        st.session_state[f"{key}_input"] = default
    if f"{key}_sync_v" not in st.session_state:
        st.session_state[f"{key}_sync_v"] = 1  # Version counter for the dynamic key

    # Local Slider Reset logic
    reset_flag_key = f"{key}_do_reset"
    if st.session_state.get(reset_flag_key, False):
        st.session_state[reset_flag_key] = False
        st.session_state[key] = default
        st.session_state[f"{key}_input"] = default
        st.session_state[f"{key}_sync_v"] += 1 # Change key to force visual reset

    # Callbacks for bidirectional sync
    def on_slider_change(master_k, sl_k):
        # User moved slider -> update master state and input box
        val = st.session_state[sl_k]
        st.session_state[master_k] = val
        st.session_state[f"{master_k}_input"] = val

    def on_input_change(master_k, min_v, max_v):
        # User typed value -> update master state and increment version to force slider refresh
        val = st.session_state[f"{master_k}_input"]
        clamped = max(min_v, min(max_v, val))
        st.session_state[master_k] = clamped
        st.session_state[f"{master_k}_input"] = clamped
        st.session_state[f"{master_k}_sync_v"] += 1 # Change key to force visual sync

    # Helper for default string display
    if isinstance(default, float):
        default_str = format_str % default if format_str else (f"{default:.2f}" if default != int(default) else str(int(default)))
    else:
        default_str = str(default)
    
    # Three columns: slider | input | reset button
    # Tight ratios that keep input and reset close together
    col_sl, col_in, col_reset = st.columns([4, 0.8, 0.4], gap="small")
    
    
    
    with col_sl:
        st.markdown('<div class="slider-compact-marker"></div>', unsafe_allow_html=True)
        
        # LATCHING DYNAMIC KEY Logic:
        # 1. Get version and construct key
        sync_v = st.session_state[f"{key}_sync_v"]
        slider_key = f"{key}_dyn_sl_{sync_v}"
        
        # 2. LATCH: Manually prime session state if key is new.
        # This tricks Streamlit into showing the correct handle WITHOUT needing 'value='.
        if slider_key not in st.session_state:
            st.session_state[slider_key] = st.session_state[key]
            
        slider_kwargs = {
            "label": f"{label} Slider",
            "min_value": min_value, 
            "max_value": max_value,
            "step": step,
            "key": slider_key,
            # CRITICAL: Omit 'value' here. Focus stays during drag.
            "label_visibility": "collapsed",
            "help": help_text,
            "on_change": on_slider_change,
            "args": (key, slider_key)
        }
            
        st.slider(**slider_kwargs)

        # BUDGET MODE: Show derived metric text below slider
        if budget_config is not None:
            cost = st.session_state.get(budget_config.cost_key, 1)
            unit = st.session_state.get(budget_config.unit_key, 1.0)
            current_value = st.session_state[key]
            
            if cost > 0:
                derived = (current_value / cost) * unit + budget_config.param_baseline
            else:
                derived = budget_config.param_baseline
            derived = min(derived, budget_config.param_cap)
            
            # Store derived value for simulation
            st.session_state[f"{key}_derived"] = derived
            
            st.markdown(
                f'<div style="font-size: 11px; color: #718096; margin-top: -8px;">→ {budget_config.param_format % derived}</div>',
                unsafe_allow_html=True
            )
    
    with col_in:
        input_kwargs = {
            "label": label,
            "min_value": input_min if input_min is not None else min_value,
            "max_value": input_max if input_max is not None else max_value,
            "step": step,
            "key": f"{key}_input",
            "label_visibility": "collapsed",
            "on_change": on_input_change,
            "args": (key, min_value, max_value)
        }
        
        if format_str:
            input_kwargs["format"] = format_str
            
        st.number_input(**input_kwargs)
        
        # Show default value
        st.markdown(
            f'''<div style="width: 80px; text-align: center; margin-top: 4px; font-size: 10px; color: #718096; white-space: nowrap;">Default: {default_str}</div>''',
            unsafe_allow_html=True
        )
    
    with col_reset:
        if st.button("↻", key=f"{key}_reset", help=f"Reset to default: {default_str}"):
            # We set a flag to perform a full reset on next rerun
            st.session_state[f"{key}_do_reset"] = True
            st.rerun()

    
    return st.session_state[key]


def compact_text_input(
    label: str,
    key: str,
    default,
    min_value=None,
    max_value=None,
    step=None,
    format_str: str = None,
    help_text: str = None,
):
    """
    Creates a compact horizontal text input: Label | Input | Reset
    Designed to tile horizontally (2-3 per row) and stack vertically.
    
    Layout (single row):
    ┌─────────────────────────────────────────────────────┐
    │ Label (?)         [  value  ]  ↻                    │
    │                   default: X.XX                     │
    └─────────────────────────────────────────────────────┘
    """
    # Reset flag key - use 'txt_' prefix to differentiate from slider resets
    reset_flag_key = f"txt_{key}_do_reset"
    if st.session_state.get(reset_flag_key, False):
        st.session_state[reset_flag_key] = False
        st.session_state[key] = default
    
    # Initialize state
    if key not in st.session_state:
        st.session_state[key] = default
    
    # Format default for display
    if isinstance(default, float):
        if format_str:
            default_str = format_str % default
        elif default != int(default):
            default_str = f"{default:.2f}"
        else:
            default_str = str(int(default))
    else:
        default_str = str(default)
    
    # Determine step if not provided
    if step is None:
        step = 0.1 if isinstance(default, float) else 1
    
    # Three columns layout: label | input | reset
    # Equal ratios - CSS will override with fixed widths for precise proximity
    col_label, col_input, col_reset = st.columns([1, 1, 1], gap="small")
    
    with col_label:
        # Class-based marker for robust CSS targeting
        st.markdown('<div class="compact-marker"></div>', unsafe_allow_html=True)
        # Label with optional help tooltip - ADJUSTED SIZE TO MATCH SLIDERS
        label_html = f'<span style="font-size: 1.05rem; font-weight: 600;">{label}</span>'
        if help_text:
            st.markdown(f"{label_html}", help=help_text, unsafe_allow_html=True)
        else:
            st.markdown(f"{label_html}", unsafe_allow_html=True)
    
    with col_input:
        input_kwargs = {
            "label": label,
            "value": st.session_state[key],
            "step": step,
            "key": f"txt_{key}_input",
            "label_visibility": "collapsed",
        }
        if min_value is not None:
            input_kwargs["min_value"] = min_value
        if max_value is not None:
            input_kwargs["max_value"] = max_value
        if format_str:
            input_kwargs["format"] = format_str
            
        input_val = st.number_input(**input_kwargs)
        
        # Default value below input - tight styling
        st.markdown(
            f'''<div style="
                position: relative;
                width: 80px;
                height: 12px;
                margin-top: 2px;
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
        
        # Sync back to state if changed
        if input_val != st.session_state[key]:
            new_val = input_val
            if min_value is not None:
                new_val = max(min_value, new_val)
            if max_value is not None:
                new_val = min(max_value, new_val)
            st.session_state[key] = new_val
            st.rerun()
    
    with col_reset:
        # Reset button - same pattern as slider reset
        reset_key = f"txt_{key}_reset"
        if st.button("↻", key=reset_key, help=f"Reset to default: {default_str}"):
            st.session_state[reset_flag_key] = True
            st.rerun()
    
    return st.session_state[key]


def render():


    """Render the simulation configuration page with tiered settings."""
    
    # =====================================================
    # INTEGRITY CHECK: GLOBAL STATE INITIALIZATION
    # =====================================================
    # Ensure all parameters (including hidden expert ones) are initialized
    # This prevents state loss when toggling visibility (e.g. error model, SME sliders)
    for k, v in DEFAULT_VALUES.items():
        if k not in st.session_state:
            st.session_state[k] = v
            
    # =====================================================
    # APPLY PENDING CONFIG (must happen BEFORE widgets render)
    # =====================================================
    if "_pending_config" in st.session_state:
        config_data = st.session_state.pop("_pending_config")
        config_name = st.session_state.pop("_pending_config_name", "config")
        _apply_config_to_state(config_data)
        st.toast(f"Loaded: {config_name}")
    
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
                        Adjust parameters and run
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
        st.markdown('<div style="border-bottom:1px solid #D1D9E0; margin-bottom:12px; margin-top:-12px;"></div>', unsafe_allow_html=True)
        
        # EXPERT MODE TOGGLE
        show_expert = st.toggle("Show Expert Settings", key="show_expert_settings", help="Reveal advanced calibration parameters for beliefs, networks, and compliance models.")
        
        # Detection logic for mode changes to reset slider visualizations
        def force_slider_visual_sync():
            """Increment version for all sliders so they perform a one-time visual sync."""
            sync_keys = [k for k in st.session_state.keys() if k.endswith("_sync_v")]
            for k in sync_keys:
                st.session_state[k] += 1

        if "last_show_expert" not in st.session_state:
            st.session_state.last_show_expert = show_expert
        if show_expert != st.session_state.last_show_expert:
            st.session_state.last_show_expert = show_expert
            force_slider_visual_sync()
        
        st.markdown("<div style='height: 12px'></div>", unsafe_allow_html=True)

        # =====================================================
        # 1. SETUP - Always Visible
        # =====================================================
        
        # Initialize session state for synced values
        if "pop_value" not in st.session_state:
            reset_to_defaults()

        with st.expander("Simulation Setup", expanded=True):
            st.markdown("**Population**", help="Total number of agents in the simulation.")
            n_agents = synced_slider_input(
                label="Population Size", key="pop_slider",
                min_value=500, max_value=10000,
                default=DEFAULT_VALUES["pop_value"],
                step=50, input_max=100000
            )
            
            st.markdown("**Simulation Duration (Years)**", help="Number of time steps (years) to simulate.")
            n_steps = synced_slider_input(
                label="Duration", key="dur_slider",
                min_value=10, max_value=100,
                default=DEFAULT_VALUES["dur_value"],
                step=5, input_max=1000
            )
            
            st.markdown("**Monte Carlo Runs**", help="Number of independent simulation runs to average results over.")
            n_runs = synced_slider_input(
                label="Runs", key="run_slider",
                min_value=1, max_value=10,
                default=DEFAULT_VALUES["run_value"],
                step=1
            )

        # =====================================================
        # 2. STRATEGY - ENFORCEMENT
        # =====================================================
        st.markdown("""
            <div style="margin-top: 32px; margin-bottom: 12px;">
                <span style="font-size: 18px; font-weight: 600; color: #1A1A1A;">Tax Authority Strategy</span>
                <div style="border-bottom: 1px solid #D1D9E0; margin-top: 8px;"></div>
            </div>
        """, unsafe_allow_html=True)
        
        # BUDGET MODE TOGGLE
        budget_mode = st.toggle("Budget Mode", key="budget_mode", help="Enable budget-constrained allocation. Control spending instead of direct parameters.")
        
        if "last_budget_mode" not in st.session_state:
            st.session_state.last_budget_mode = budget_mode
        if budget_mode != st.session_state.last_budget_mode:
            st.session_state.last_budget_mode = budget_mode
            # In the current scope, force_slider_visual_sync is defined above the Setup section
            force_slider_visual_sync()
        
        # BUDGET SIMULATION OPTIONS (Only if Budget Mode is ON)
        if budget_mode:
            with st.expander("Budget Simulation Options", expanded=True):
                st.markdown("**Total Budget ($)**", help="Total budget available for tax authority strategies.")
                total_budget = synced_slider_input(
                    label="Total Budget", key="budget_total_slider",
                    min_value=25000, max_value=200000,
                    default=DEFAULT_VALUES["budget_total"],
                    step=5000, input_max=500000
                )
                
                # Cost Configuration (Nested Expander)
                with st.expander("Cost Configuration", expanded=False):
                    st.markdown('<div style="font-size: 1.05rem; font-weight: 600; margin-bottom: 0.5rem;">Enforcement Costs</div>', unsafe_allow_html=True)
                    with st.container():
                        st.markdown('<div class="compact-rows-wrapper"></div>', unsafe_allow_html=True)
                        c1, c2 = st.columns(2)
                        with c1: compact_text_input("Private Audit ($/unit)", "cost_audit_priv", DEFAULT_VALUES["cost_audit_priv"], 1000, 50000, help_text="Cost per 1% private audit rate.")
                        with c2: compact_text_input("Unit Size (%)", "unit_audit_priv", DEFAULT_VALUES["unit_audit_priv"], 0.1, 10.0, help_text="Unit size for private audit rate.")
                        
                        c3, c4 = st.columns(2)
                        with c3: compact_text_input("Business Audit ($/unit)", "cost_audit_biz", DEFAULT_VALUES["cost_audit_biz"], 1000, 50000, help_text="Cost per 1% business audit rate.")
                        with c4: compact_text_input("Unit Size (%)", "unit_audit_biz", DEFAULT_VALUES["unit_audit_biz"], 0.1, 10.0, help_text="Unit size for business audit rate.")
                        
                        c5, c6 = st.columns(2)
                        with c5: compact_text_input("Deep Audit ($/unit)", "cost_audit_deep", DEFAULT_VALUES["cost_audit_deep"], 500, 20000, help_text="Cost per 10% deep audit probability.")
                        with c6: compact_text_input("Unit Size (%)", "unit_audit_deep", DEFAULT_VALUES["unit_audit_deep"], 1.0, 50.0, help_text="Unit size for deep audit probability.")
                    
                    st.markdown('<div style="font-size: 1.05rem; font-weight: 600; margin-bottom: 0.5rem; margin-top: 1rem;">Intervention Costs</div>', unsafe_allow_html=True)
                    with st.container():
                        st.markdown('<div class="compact-rows-wrapper"></div>', unsafe_allow_html=True)
                        c7, c8 = st.columns(2)
                        with c7: compact_text_input("Letters ($/unit)", "cost_letter", DEFAULT_VALUES["cost_letter"], 100, 5000, help_text="Cost per 1% letter rate.")
                        with c8: compact_text_input("Unit Size (%)", "unit_letter", DEFAULT_VALUES["unit_letter"], 0.1, 10.0, help_text="Unit size for letter rate.")
                        
                        c9, c10 = st.columns(2)
                        with c9: compact_text_input("Phone Calls ($/unit)", "cost_phone", DEFAULT_VALUES["cost_phone"], 500, 10000, help_text="Cost per 1% phone call rate.")
                        with c10: compact_text_input("Unit Size (%)", "unit_phone", DEFAULT_VALUES["unit_phone"], 0.1, 10.0, help_text="Unit size for phone call rate.")
                    
                    st.markdown('<div style="font-size: 1.05rem; font-weight: 600; margin-bottom: 0.5rem; margin-top: 1rem;">Service Costs</div>', unsafe_allow_html=True)
                    with st.container():
                        st.markdown('<div class="compact-rows-wrapper"></div>', unsafe_allow_html=True)
                        c11, c12 = st.columns(2)
                        with c11: compact_text_input("Call Satisfaction ($/unit)", "cost_call_sat", DEFAULT_VALUES["cost_call_sat"], 50, 2000, help_text="Cost per 1% call satisfaction (above 50%).")
                        with c12: compact_text_input("Unit Size (%)", "unit_call_sat", DEFAULT_VALUES["unit_call_sat"], 0.1, 10.0, help_text="Unit size for call satisfaction.")
                        
                        c13, c14 = st.columns(2)
                        with c13: compact_text_input("Web Quality ($/unit)", "cost_web", DEFAULT_VALUES["cost_web"], 50, 2000, help_text="Cost per 0.1 web quality (above 2.0).")
                        with c14: compact_text_input("Unit Size (score)", "unit_web", DEFAULT_VALUES["unit_web"], 0.05, 1.0, help_text="Unit size for web quality improvement.")
                        
                        c15, _ = st.columns(2)
                        with c15: compact_text_input("HUBA (Flat Cost)", "cost_huba", DEFAULT_VALUES["cost_huba"], 1000, 50000, help_text="One-time cost to enable HUBA program.")
                
                # Budget Meter - only count enabled interventions
                letter_enabled = st.session_state.get("letter_enabled", False)
                phone_enabled = st.session_state.get("phone_enabled", False)
                huba_enabled = st.session_state.get("transparency_toggle", False)
                
                total_spent = (
                    st.session_state.get("spend_audit_priv", 0) +
                    st.session_state.get("spend_audit_biz", 0) +
                    st.session_state.get("spend_audit_deep", 0) +
                    # Only include if enabled
                    (st.session_state.get("spend_letter_priv", 0) if letter_enabled else 0) +
                    (st.session_state.get("spend_letter_biz", 0) if letter_enabled else 0) +
                    (st.session_state.get("spend_phone_priv", 0) if phone_enabled else 0) +
                    (st.session_state.get("spend_phone_biz", 0) if phone_enabled else 0) +
                    st.session_state.get("spend_call_sat", 0) +
                    st.session_state.get("spend_web_priv", 0) +
                    st.session_state.get("spend_web_biz", 0) +
                    (st.session_state.get("spend_huba", 0) if huba_enabled else 0)
                )
                remaining = total_budget - total_spent
                budget_exceeded = remaining < 0
                st.session_state["_budget_exceeded"] = budget_exceeded  # Store for run button
                
                meter_color = "#48BB78" if not budget_exceeded else "#F56565"  # Green or Red
                
                st.markdown(f"""
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 8px 12px; background: #F7FAFC; border-radius: 8px; margin-top: 12px;">
                        <div>
                            <span style="font-weight: 600;">Budget:</span> ${total_budget:,}
                        </div>
                        <div>
                            <span style="font-weight: 600;">Allocated:</span> ${total_spent:,.0f}
                        </div>
                        <div style="color: {meter_color}; font-weight: 600;">
                            <span>Remaining:</span> ${remaining:,.0f}
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                if budget_exceeded:
                    st.error("Budget exceeded! Reduce spending to run simulation.")
        else:
            # Clear budget exceeded flag when not in budget mode
            st.session_state["_budget_exceeded"] = False
        


        with st.expander("Audits", expanded=False):
            # Get total budget for spending sliders
            total_budget = st.session_state.get("budget_total_slider", DEFAULT_VALUES["budget_total"])
            
            if budget_mode:
                # BUDGET MODE: Spending sliders with derived metrics
                st.markdown("**Private Audit Spending**", help="Allocate budget for private taxpayer audits.")
                synced_slider_input(
                    label="Private Audit ($)", key="spend_audit_priv",
                    min_value=0, max_value=int(total_budget),
                    default=DEFAULT_VALUES["spend_audit_priv"], step=500,
                    help_text="Spending for private audit rate.",
                    budget_config=BudgetConfig(
                        cost_key="cost_audit_priv", unit_key="unit_audit_priv",
                        param_format="%.1f%% rate", param_cap=10.0
                    )
                )
                
                st.markdown("**Business Audit Spending**", help="Allocate budget for business taxpayer audits.")
                synced_slider_input(
                    label="Business Audit ($)", key="spend_audit_biz",
                    min_value=0, max_value=int(total_budget),
                    default=DEFAULT_VALUES["spend_audit_biz"], step=500,
                    help_text="Spending for business audit rate.",
                    budget_config=BudgetConfig(
                        cost_key="cost_audit_biz", unit_key="unit_audit_biz",
                        param_format="%.1f%% rate", param_cap=10.0
                    )
                )
                
                st.markdown("**Deep Audit Spending**", help="Allocate budget for deep book audits.")
                synced_slider_input(
                    label="Deep Audit ($)", key="spend_audit_deep",
                    min_value=0, max_value=int(total_budget),
                    default=DEFAULT_VALUES["spend_audit_deep"], step=500,
                    help_text="Spending for deep audit probability.",
                    budget_config=BudgetConfig(
                        cost_key="cost_audit_deep", unit_key="unit_audit_deep",
                        param_format="%.0f%% prob", param_cap=100.0
                    )
                )

            else:
                # NORMAL MODE: Direct parameter sliders
                st.markdown("**Private Audit Rate (%)**", help="Percentage of private taxpayers audited per year.")
                synced_slider_input(
                    label="Private Rate", key="priv_audit_slider",
                    min_value=0.0, max_value=10.0,
                    default=DEFAULT_VALUES["priv_audit_value"],
                    step=0.1, format_str="%.1f"
                )
                
                st.markdown("**Business Audit Rate (%)**", help="Percentage of business taxpayers audited per year.")
                synced_slider_input(
                    label="Business Rate", key="biz_audit_slider",
                    min_value=0.0, max_value=10.0,
                    default=DEFAULT_VALUES["biz_audit_value"],
                    step=0.05, format_str="%.2f"
                )

                st.markdown("**Deep Audit Probability (%)**")
                depth = synced_slider_input(
                    label="Deep Audit Prob", key="audit_depth_slider",
                    min_value=0.0, max_value=100.0,
                    default=DEFAULT_VALUES["audit_depth_value"],
                    step=5.0, format_str="%.0f",
                    help_text="Probability that an audit includes a deep book review (vs. simple check)."
                )
            

            
            st.markdown("**Audit Selection Strategy**")
            default_audit = DEFAULT_VALUES["audit_strategy"]
            if default_audit == "risk_based": default_audit = "risk"
            
            audit_display_map = {
                "random": "Random Selection",
                "risk": "Risk-Based",
                "network": "Network Connectivity"
            }
            
            st.selectbox(
                "Audit Selection Strategy",
                options=["random", "risk", "network"],
                index=["random", "risk", "network"].index(default_audit) if default_audit in ["random", "risk", "network"] else 0,
                format_func=lambda x: audit_display_map.get(x, x),
                key="sel_audit",
                label_visibility="collapsed"
            )

        # =====================================================
        # 3. STRATEGY - INTERVENTIONS
        # =====================================================
        with st.expander("Interventions", expanded=False):
            # Letter Deterrence
            st.markdown("**Deterrence Letters**")
            letter_enabled = st.toggle("Enable Letters", key="letter_enabled")
            
            if letter_enabled:
                if budget_mode:
                    st.markdown("**Letter Spending (Private)**", help="Allocate budget for private deterrence letters.")
                    synced_slider_input(
                        label="Letter (Priv) $", key="spend_letter_priv",
                        min_value=0, max_value=int(total_budget),
                        default=DEFAULT_VALUES["spend_letter_priv"], step=100,
                        help_text="Spending for private letter rate.",
                        budget_config=BudgetConfig(
                            cost_key="cost_letter", unit_key="unit_letter",
                            param_format="%.1f%% rate", param_cap=10.0
                        )
                    )
                    st.markdown("**Letter Spending (Business)**", help="Allocate budget for business deterrence letters.")
                    synced_slider_input(
                        label="Letter (Biz) $", key="spend_letter_biz",
                        min_value=0, max_value=int(total_budget),
                        default=DEFAULT_VALUES["spend_letter_biz"], step=100,
                        help_text="Spending for business letter rate.",
                        budget_config=BudgetConfig(
                            cost_key="cost_letter", unit_key="unit_letter",
                            param_format="%.1f%% rate", param_cap=10.0
                        )
                    )

                else:
                    st.markdown("Private Rate (%)", help="Percentage of private agents receiving letters.")
                    synced_slider_input(
                        "Priv Rate (%)", "letter_rate_priv_slider", 
                        0.0, 10.0, DEFAULT_VALUES["letter_rate_priv"], 0.5, format_str="%.1f"
                    )
                    st.markdown("Business Rate (%)", help="Percentage of business agents receiving letters.")
                    synced_slider_input(
                        "Biz Rate (%)", "letter_rate_biz_slider", 
                        0.0, 10.0, DEFAULT_VALUES["letter_rate_biz"], 0.5, format_str="%.1f"
                    )

                
                if show_expert:
                    with st.expander("Optimization (Expert)", expanded=False):
                        st.selectbox(
                            "Selection", 
                            ["random", "risk", "network"], 
                            index=0, 
                            key="sel_letter_strategy",
                            format_func=lambda x: {"random": "Random", "risk": "Risk-Based", "network": "Network"}.get(x, x)
                        )
                        
                        st.markdown('<div style="font-size: 1.15rem; font-weight: 600; margin-bottom: 0.5rem; margin-top: 1rem;">Effects (Change in Belief/Trust)</div>', unsafe_allow_html=True)
                        # Max 2 text inputs side by side
                        with st.container():
                            st.markdown('<div class="compact-rows-wrapper"></div>', unsafe_allow_html=True)
                            l_eff_1, l_eff_2 = st.columns(2)
                            with l_eff_1: compact_text_input("Permanent Impact (Δ)", "letter_eff_perm", DEFAULT_VALUES["letter_eff_perm"], 0.0, 20.0, help_text="Permanent change in audit probability perception after receiving a letter.")
                            with l_eff_2: compact_text_input("Temporary Impact (Δ)", "letter_eff_temp", DEFAULT_VALUES["letter_eff_temp"], 0.0, 50.0, help_text="Temporary spike in audit probability perception (decays over time).")
                            
                            l_eff_3, _ = st.columns([1, 1])
                            with l_eff_3: compact_text_input("Trust Impact (Δ)", "letter_eff_trust", DEFAULT_VALUES["letter_eff_trust"], -1.0, 1.0, help_text="Change in trust levels after receiving a letter.")
            
            st.markdown("---")
            
            # Phone Outreach
            st.markdown("**Phone Outreach**")
            phone_enabled = st.toggle("Enable Calls", key="phone_enabled")
            
            if phone_enabled:
                if budget_mode:
                    st.markdown("**Phone Spending (Private)**", help="Allocate budget for private phone outreach.")
                    synced_slider_input(
                        label="Phone (Priv) $", key="spend_phone_priv",
                        min_value=0, max_value=int(total_budget),
                        default=DEFAULT_VALUES["spend_phone_priv"], step=100,
                        help_text="Spending for private phone call rate.",
                        budget_config=BudgetConfig(
                            cost_key="cost_phone", unit_key="unit_phone",
                            param_format="%.1f%% rate", param_cap=10.0
                        )
                    )
                    st.markdown("**Phone Spending (Business)**", help="Allocate budget for business phone outreach.")
                    synced_slider_input(
                        label="Phone (Biz) $", key="spend_phone_biz",
                        min_value=0, max_value=int(total_budget),
                        default=DEFAULT_VALUES["spend_phone_biz"], step=100,
                        help_text="Spending for business phone call rate.",
                        budget_config=BudgetConfig(
                            cost_key="cost_phone", unit_key="unit_phone",
                            param_format="%.1f%% rate", param_cap=10.0
                        )
                    )

                else:
                    st.markdown("Private Rate (%)", help="Percentage of private agents receiving calls.")
                    synced_slider_input(
                        "Priv Rate (%)", "phone_rate_priv_slider", 
                        0.0, 10.0, DEFAULT_VALUES["phone_rate_priv"], 0.5, format_str="%.1f"
                    )
                    st.markdown("Business Rate (%)", help="Percentage of business agents receiving calls.")
                    synced_slider_input(
                        "Biz Rate (%)", "phone_rate_biz_slider", 
                        0.0, 10.0, DEFAULT_VALUES["phone_rate_biz"], 0.5, format_str="%.1f"
                    )

                if show_expert:
                    with st.expander("Optimization (Expert)", expanded=False):
                        st.selectbox(
                            "Selection", 
                            ["random", "risk", "network"], 
                            index=0, 
                            key="sel_phone_strategy",
                            format_func=lambda x: {"random": "Random", "risk": "Risk-Based", "network": "Network"}.get(x, x)
                        )
                        
                        st.markdown('<div style="font-size: 1.15rem; font-weight: 600; margin-bottom: 0.5rem; margin-top: 1rem;">Effects (PSO/Trust Impact)</div>', unsafe_allow_html=True)
                        with st.container():
                            st.markdown('<div class="compact-rows-wrapper"></div>', unsafe_allow_html=True)
                            p_eff_1, p_eff_2 = st.columns(2)
                            with p_eff_1: compact_text_input("Satisfied Impact (Δ)", "phone_sat_delta", DEFAULT_VALUES["phone_sat_delta"], -1.0, 1.0, help_text="Change in compliance (PSO) if call experience is satisfied.")
                            with p_eff_2: compact_text_input("Dissatisfied Impact (Δ)", "phone_dissat_delta", DEFAULT_VALUES["phone_dissat_delta"], -1.0, 1.0, help_text="Change in compliance (PSO) if call experience is dissatisfied.")
                            
                            p_eff_3, _ = st.columns([1, 1])
                            with p_eff_3: compact_text_input("Audit Perception Impact (Δ)", "phone_eff_audit_temp", DEFAULT_VALUES["phone_eff_audit_temp"], 0.0, 50.0, help_text="Temporary increase in perceived audit probability after a call.")

        # =====================================================
        # 4. SERVICE & FISCAL ENVIRONMENT
        # =====================================================
        # =====================================================
        # 4. SERVICE & FISCAL ENVIRONMENT
        # =====================================================
        with st.expander("Services", expanded=False):
            st.markdown("**Service Quality**")
            
            if budget_mode:
                # BUDGET MODE: Spending sliders with baselines
                st.markdown("**Call Satisfaction Spending**", help="Allocate budget for call satisfaction improvements (above 50%).")
                synced_slider_input(
                    label="Call Sat $", key="spend_call_sat",
                    min_value=0, max_value=int(total_budget),
                    default=DEFAULT_VALUES["spend_call_sat"], step=100,
                    help_text="Spending for call satisfaction (above 50% baseline).",
                    budget_config=BudgetConfig(
                        cost_key="cost_call_sat", unit_key="unit_call_sat",
                        param_format="%.0f%% sat", param_cap=99.0, param_baseline=50.0
                    )
                )
                
                st.markdown("**Private Web Quality Spending**", help="Allocate budget for private web quality (above 2.0).")
                synced_slider_input(
                    label="Web (Priv) $", key="spend_web_priv",
                    min_value=0, max_value=int(total_budget),
                    default=DEFAULT_VALUES["spend_web_priv"], step=100,
                    help_text="Spending for private web quality (above 2.0 baseline).",
                    budget_config=BudgetConfig(
                        cost_key="cost_web", unit_key="unit_web",
                        param_format="%.1f quality", param_cap=5.0, param_baseline=2.0
                    )
                )
                
                st.markdown("**Business Web Quality Spending**", help="Allocate budget for business web quality (above 2.0).")
                synced_slider_input(
                    label="Web (Biz) $", key="spend_web_biz",
                    min_value=0, max_value=int(total_budget),
                    default=DEFAULT_VALUES["spend_web_biz"], step=100,
                    help_text="Spending for business web quality (above 2.0 baseline).",
                    budget_config=BudgetConfig(
                        cost_key="cost_web", unit_key="unit_web",
                        param_format="%.1f quality", param_cap=5.0, param_baseline=2.0
                    )
                )
                

                # HUBA in budget mode
                st.markdown("**HUBA Program**", help="One-time cost to launch HUBA transparency program.")
                huba_enabled = st.toggle("Launch HUBA", key="transparency_toggle", help="Enable High Utility Business Audit (HUBA) program transparency effects.")
                if huba_enabled:
                    st.session_state["spend_huba"] = st.session_state.get("cost_huba", DEFAULT_VALUES["cost_huba"])
                    st.markdown(f"<div style='color: #718096; font-size: 12px;'>Cost: ${st.session_state['spend_huba']:,}</div>", unsafe_allow_html=True)
                else:
                    st.session_state["spend_huba"] = 0
            else:
                # NORMAL MODE: Direct parameter sliders
                st.markdown("Call Satisfaction (%)", help="Target probability that a taxpayer is satisfied after a phone call (>=3/5 rating).")
                synced_slider_input(
                    "Call Sat (%)", "phone_sat_slider",
                    50.0, 99.0, DEFAULT_VALUES["phone_sat_value"], 1.0, format_str="%.0f"
                )
                st.markdown("Private Web Quality (1-5)", help="Perceived quality of web services for private taxpayers.")
                synced_slider_input(
                    "Web Priv (1-5)", "web_qual_priv_slider",
                    1.0, 5.0, DEFAULT_VALUES["web_qual_priv_value"], 0.1, format_str="%.1f"
                )
                st.markdown("Business Web Quality (1-5)", help="Perceived quality of web services for business taxpayers.")
                synced_slider_input(
                    "Web Biz (1-5)", "web_qual_biz_slider",
                    1.0, 5.0, DEFAULT_VALUES["web_qual_biz_value"], 0.1, format_str="%.1f",
                )
                
                if show_expert:
                    st.markdown("Transparency (HUBA)")
                    st.toggle("Launch HUBA", key="transparency_toggle", help="Enable High Utility Business Audit (HUBA) program transparency effects.")
                    if st.session_state["transparency_toggle"]:
                        h_col, _ = st.columns([1, 1])
                        with h_col: compact_text_input("HUBA Impact (Δ)", "huba_delta", DEFAULT_VALUES["huba_delta"], 0.0, 5.0, help_text="Increase in trust/compliance due to HUBA transparency.")



        # =====================================================
        # 5. ALGORITHM CONFIGURATION
        # =====================================================
        st.markdown("""
            <div style="margin-top: 32px; margin-bottom: 12px;">
                <span style="font-size: 18px; font-weight: 600; color: #1A1A1A;">Algorithm Configuration</span>
                <div style="border-bottom: 1px solid #D1D9E0; margin-top: 8px;"></div>
            </div>
        """, unsafe_allow_html=True)

        # --- Fiscal Environment (Moved here) ---
        with st.expander("Fiscal Environment", expanded=False):
            st.markdown("**Fiscal Policy**")
            st.markdown("General Tax Rate (%)", help="Standard tax rate applied to all agent income.")
            synced_slider_input(
                "Tax Rate (%)", "tax_slider",
                10, 60, DEFAULT_VALUES["tax_rate_value"], 5
            )
            st.markdown("Penalty Multiplier (x)", help="Fine amount multiplier relative to the evaded tax amount.")
            synced_slider_input(
                "Penalty (x)", "penalty_slider",
                1.0, 5.0, DEFAULT_VALUES["penalty_value"], 0.5, format_str="%.1f"
            )
            st.markdown("SME Population Ratio (%)", help="Percentage of total population that are small/medium enterprises. 17.9% derived from Tax Authority Jaar Reportage 2024.")
            synced_slider_input(
                "SME Ratio (%)", "biz_ratio_slider",
                0.0, 100.0, DEFAULT_VALUES["biz_ratio_value"], 1.0, format_str="%.1f"
            )

        # --- Agent Behaviour (Was Compliance Thresholds) ---
        with st.expander("Agent Behaviour", expanded=False):
             st.markdown('<div style="font-size: 1.15rem; font-weight: 600; margin-bottom: 0.5rem;">Compliance Thresholds (TCI)</div>', unsafe_allow_html=True, help="Tax Compliance Intention (TCI)")
             st.markdown("Private Compliance Threshold", help="Tax Compliance Inclination (TCI) required for private agents to comply.")
             synced_slider_input("Priv Threshold", "tci_threshold_priv_slider", 1.0, 5.0, DEFAULT_VALUES["tci_threshold_priv"], 0.1)
             
             # Calculate and display Private Compliance %
             try:
                 p_mean = _cfg.behaviors["compliance_inclination"]["private"]["mean"]
                 p_std = _cfg.behaviors["compliance_inclination"]["private"]["std"]
                 p_thresh = st.session_state.get("tci_threshold_priv_slider", DEFAULT_VALUES["tci_threshold_priv"])
                 p_honest_pct = norm.sf(p_thresh, loc=p_mean, scale=p_std) * 100
                 st.caption(f"Projected Honesty: {p_honest_pct:.1f}% with N(μ={p_mean}, σ={p_std})")
             except KeyError:
                 pass

             st.markdown("Business Compliance Threshold", help="Tax Compliance Inclination (TCI) required for business agents to comply.")
             synced_slider_input("Biz Threshold", "tci_threshold_biz_slider", 1.0, 5.0, DEFAULT_VALUES["tci_threshold_biz"], 0.1)
             
             # Calculate and display Business Compliance %
             try:
                 b_mean = _cfg.behaviors["compliance_inclination"]["business"]["mean"]
                 b_std = _cfg.behaviors["compliance_inclination"]["business"]["std"]
                 b_thresh = st.session_state.get("tci_threshold_biz_slider", DEFAULT_VALUES["tci_threshold_biz"])
                 b_honest_pct = norm.sf(b_thresh, loc=b_mean, scale=b_std) * 100
                 st.caption(f"Projected Honesty: {b_honest_pct:.1f}% with N(μ={b_mean}, σ={b_std})")
             except KeyError:
                 pass

             if show_expert:
                st.markdown('<div style="font-size: 1.15rem; font-weight: 600; margin-bottom: 0.5rem; margin-top: 1.5rem;">Trait Configuration</div>', unsafe_allow_html=True)
                
                # --- Private Agents ---
                with st.expander("Private Agent Traits", expanded=False):
                        
                    # Subjective Audit Probability
                    with st.container():
                        st.markdown('<div class="compact-rows-wrapper"></div>', unsafe_allow_html=True)
                        c1, c2 = st.columns(2)
                        with c1: compact_text_input("Subj. Audit Prob. Mean (μ)", "priv_audit_mean", DEFAULT_VALUES["priv_audit_belief_value"], 0.0, 100.0, help_text="Perceived probability of being audited (0-100%).")
                        with c2: compact_text_input("Subj. Audit Prob. Std. (σ)", "priv_audit_std", DEFAULT_VALUES["priv_audit_belief_std"], 0.0, 50.0)

                        # Personal Norms
                        c3, c4 = st.columns(2)
                        with c3: compact_text_input("Personal Norms Mean (μ)", "priv_pn_mean", DEFAULT_VALUES["priv_pn_value"], 1.0, 5.0)
                        with c4: compact_text_input("Personal Norms Std. (σ)", "priv_pn_std", DEFAULT_VALUES["priv_pn_std"], 0.0, 2.0)

                        # Social Norms
                        c5, c6 = st.columns(2)
                        with c5: compact_text_input("Social Norms Mean (μ)", "priv_sn_mean", DEFAULT_VALUES["priv_sn_value"], 1.0, 5.0)
                        with c6: compact_text_input("Social Norms Std. (σ)", "priv_sn_std", DEFAULT_VALUES["priv_sn_std"], 0.0, 2.0)
                        
                        # Societal Norms 
                        c7, c8 = st.columns(2)
                        with c7: compact_text_input("Societal Norms Mean (μ)", "priv_stn_mean", DEFAULT_VALUES["priv_stn_value"], 1.0, 5.0)
                        with c8: compact_text_input("Societal Norms Std. (σ)", "priv_stn_std", DEFAULT_VALUES["priv_stn_std"], 0.0, 2.0)

                        # PSO
                        c9, c10 = st.columns(2)
                        with c9: compact_text_input("Perceived Service (PSO) Mean (μ)", "priv_pso_mean", DEFAULT_VALUES["priv_pso_value"], 1.0, 5.0)
                        with c10: compact_text_input("Perceived Service (PSO) Std. (σ)", "priv_pso_std", DEFAULT_VALUES["priv_pso_std"], 0.0, 2.0)

                        # Trust
                        c11, c12 = st.columns(2)
                        with c11: compact_text_input("Trust Baseline Mean (μ)", "priv_pt_mean", DEFAULT_VALUES["priv_pt_value"], 1.0, 5.0)
                        with c12: compact_text_input("Trust Baseline Std. (σ)", "priv_pt_std", DEFAULT_VALUES["priv_pt_std"], 0.0, 2.0)


                # --- Business Agents ---
                with st.expander("Business Agent Traits", expanded=False):

                    # Subjective Audit Probability
                    with st.container():
                        st.markdown('<div class="compact-rows-wrapper"></div>', unsafe_allow_html=True)
                        bc1, bc2 = st.columns(2)
                        with bc1: compact_text_input("Subj. Audit Prob. Mean (μ)", "biz_audit_mean", DEFAULT_VALUES["biz_audit_belief_value"], 0.0, 100.0, help_text="Perceived probability of being audited (0-100%).")
                        with bc2: compact_text_input("Subj. Audit Prob. Std. (σ)", "biz_audit_std", DEFAULT_VALUES["biz_audit_belief_std"], 0.0, 50.0)

                        # Personal Norms
                        bc3, bc4 = st.columns(2)
                        with bc3: compact_text_input("Business Norms Mean (μ)", "biz_pn_mean", DEFAULT_VALUES["biz_pn_value"], 1.0, 5.0)
                        with bc4: compact_text_input("Business Norms Std. (σ)", "biz_pn_std", DEFAULT_VALUES["biz_pn_std"], 0.0, 2.0)

                        # Social Norms
                        bc5, bc6 = st.columns(2)
                        with bc5: compact_text_input("Social Norms Mean (μ)", "biz_sn_mean", DEFAULT_VALUES["biz_sn_value"], 1.0, 5.0)
                        with bc6: compact_text_input("Social Norms Std. (σ)", "biz_sn_std", DEFAULT_VALUES["biz_sn_std"], 0.0, 2.0)
                        
                        # Societal Norms 
                        bc7, bc8 = st.columns(2)
                        with bc7: compact_text_input("Societal Norms Mean (μ)", "biz_stn_mean", DEFAULT_VALUES["biz_stn_value"], 1.0, 5.0)
                        with bc8: compact_text_input("Societal Norms Std. (σ)", "biz_stn_std", DEFAULT_VALUES["biz_stn_std"], 0.0, 2.0)

                        # PSO
                        bc9, bc10 = st.columns(2)
                        with bc9: compact_text_input("Perceived Service (PSO) Mean (μ)", "biz_pso_mean", DEFAULT_VALUES["biz_pso_value"], 1.0, 5.0)
                        with bc10: compact_text_input("Perceived Service (PSO) Std. (σ)", "biz_pso_std", DEFAULT_VALUES["biz_pso_std"], 0.0, 2.0)

                        # Trust
                        bc11, bc12 = st.columns(2)
                        with bc11: compact_text_input("Trust Baseline Mean (μ)", "biz_pt_mean", DEFAULT_VALUES["biz_pt_value"], 1.0, 5.0)
                        with bc12: compact_text_input("Trust Baseline Std. (σ)", "biz_pt_std", DEFAULT_VALUES["biz_pt_std"], 0.0, 2.0)

        # --- Conditional Expert Settings ---
        if show_expert:
            
            # --- Network & Social Dynamics ---
            # --- Network & Social Dynamics ---
            with st.expander("Network & Beliefs", expanded=False):
                st.markdown('<div style="font-size: 1.15rem; font-weight: 600; margin-bottom: 0.5rem;">Network Structure</div>', unsafe_allow_html=True)
                # Wrapped container for CSS targeting of these specific rows
                with st.container():
                     st.markdown('<div class="compact-rows-wrapper"></div>', unsafe_allow_html=True)
                     c1, c2 = st.columns(2)
                     with c1: compact_text_input("Social Influence Weight", "soc_inf_slider", DEFAULT_VALUES["social_influence_value"], 0.0, 1.0, help_text="How strongly agents are influenced by their neighbors' behavior.")
                     with c2: compact_text_input("Network Homophily", "net_homo", DEFAULT_VALUES["homophily_value"], 0.0, 1.0, help_text="0 = Random mixing, 1 = Complete segregation by type.")
                     
                     c3, c4 = st.columns(2)
                     with c3: compact_text_input("Avg. Network Degree", "net_deg", DEFAULT_VALUES["degree_mean_value"], 5.0, 300.0, help_text="Average number of connections per agent.")
                     with c4: compact_text_input("Degree Std.", "net_std", DEFAULT_VALUES["degree_std_value"], 0.0, 300.0, help_text="Standard deviation of the network degree distribution.")
                    
                st.markdown('<div style="font-size: 1.15rem; font-weight: 600; margin-bottom: 0.5rem; margin-top: 1rem;">Belief Dynamics</div>', unsafe_allow_html=True)
                with st.container():
                    st.markdown('<div class="compact-rows-wrapper"></div>', unsafe_allow_html=True)
                    b1, b2 = st.columns(2)
                    with b1: compact_text_input("Prior Belief Weight (μ)", "belief_mu", DEFAULT_VALUES["belief_mu"], 0.0, 1.0, help_text="Weight assigned to prior beliefs vs. new information.")
                    with b2: compact_text_input("Audit Signal Strength", "belief_signal", DEFAULT_VALUES["belief_signal"], 0.0, 100.0, help_text="Impact of a neighbor's audit outcome on the agent's belief.")
                    
                    b3, b4 = st.columns(2)
                    with b3: compact_text_input("Perception Weight", "belief_perception", DEFAULT_VALUES["belief_perception"], 0.0, 1.0, help_text="Weight of subjective perception regarding neighbors' audit status.")
                    with b4: compact_text_input("Belief Drift Rate", "belief_drift", DEFAULT_VALUES["belief_drift"], 0.0, 1.0, help_text="Rate at which beliefs drift back to the agent's initial baseline.")


                
            # --- SME Specifics ---
            with st.expander("SME Opportunities", expanded=False):
                # Opportunity Model
                st.markdown('<div style="font-size: 1.15rem; font-weight: 600; margin-bottom: 0.5rem;">SME Opportunities</div>', unsafe_allow_html=True)
                st.markdown("Base Opportunity Prob.", help="Baseline probability that an SME has the opportunity to evade.")
                synced_slider_input(
                    "Base Prob", "sme_opp_base_slider", 
                    0.0, 1.0, DEFAULT_VALUES["sme_opp_base_slider"], 0.05, format_str="%.2f",
                )
                
                with st.container():
                    st.markdown('<div class="compact-rows-wrapper"></div>', unsafe_allow_html=True)
                    op2, op3 = st.columns(2)
                    with op2: compact_text_input("Minimum Opportunity", "sme_opp_min", DEFAULT_VALUES["sme_opp_min"], 0.0, 1.0)
                    with op3: compact_text_input("Maximum Opportunity", "sme_opp_max", DEFAULT_VALUES["sme_opp_max"], 0.0, 1.0)
                    
                    op4, op5 = st.columns(2)
                    with op4: compact_text_input("Cash Bonus", "sme_opp_cash", DEFAULT_VALUES["sme_opp_cash"], 0.0, 1.0)
                    with op5: compact_text_input("Low Digital Bonus", "sme_opp_digi_low", DEFAULT_VALUES["sme_opp_digi_low"], 0.0, 1.0)
                    
                with st.expander("Opportunity Adjustments", expanded=False):
                    with st.container():
                        st.markdown('<div class="compact-rows-wrapper"></div>', unsafe_allow_html=True)
                        d1, d2 = st.columns(2)
                        with d1: compact_text_input("Sector Delta (Δ)", "delta_sector", DEFAULT_VALUES["delta_sector_value"], 0.0, 0.5)
                        with d2: compact_text_input("High Digital Delta (Δ)", "delta_digi_high", DEFAULT_VALUES["delta_digi_high_value"], -0.5, 0.0)
                        
                        d3, d4 = st.columns(2)
                        with d3: compact_text_input("Cash Intensive Delta (Δ)", "delta_cash", DEFAULT_VALUES["delta_cash_value"], 0.0, 0.5)
                        with d4: compact_text_input("Advisor Delta (Δ)", "delta_advisor", DEFAULT_VALUES["delta_advisor_value"], -0.5, 0.0)
                        
                        d5, d6 = st.columns(2)
                        with d5: compact_text_input("Past Audit Delta (Δ)", "delta_audit", DEFAULT_VALUES["delta_audit_value"], -0.5, 0.0)
                        with d6: compact_text_input("Base Risk Factor", "risk_base", DEFAULT_VALUES["risk_base_value"], 0.0, 1.0)

            # --- Error Model ---
            # --- Error Model ---
            with st.expander("Compliance Errors", expanded=False):
                # DEBUG: Verify default is loading correctly
                # st.caption(f"Debug: Default is {DEFAULT_VALUES['error_enabled']}")
                
                st.markdown('<div style="font-size: 1.15rem; font-weight: 600; margin-bottom: 0.5rem;">Reporting Errors (Unintentional)</div>', unsafe_allow_html=True)
                
                # FORCE VALUE from state to ensure toggle reflects state
                st.toggle("Enable Error Model", key="error_enabled", value=st.session_state["error_enabled"])
                if st.session_state["error_enabled"]:
                    with st.container():
                        st.markdown('<div class="compact-rows-wrapper"></div>', unsafe_allow_html=True)
                        st.markdown('<div style="font-size: 1.15rem; font-weight: 600; margin-bottom: 0.5rem;">Error Calibration</div>', unsafe_allow_html=True)
                        c_err_1, c_err_2 = st.columns(2)
                        with c_err_1: compact_text_input("Private Error Rate (%)", "error_rate_priv", DEFAULT_VALUES["error_rate_priv"], 0.0, 10.0, help_text="Prob. that a private agent makes an unintentional error.")
                        with c_err_2: compact_text_input("Business Error Rate (%)", "error_rate_biz", DEFAULT_VALUES["error_rate_biz"], 0.0, 50.0, help_text="Prob. that a business agent makes an unintentional error.")
                        
                        c_mag = st.columns(2)
                        with c_mag[0]: compact_text_input("Min. Magnitude (%)", "error_mag_min", DEFAULT_VALUES["error_mag_min"], 0.1, 100.0, help_text="Minimum error size as % of income.")
                        with c_mag[1]: compact_text_input("Max. Magnitude (%)", "error_mag_max", DEFAULT_VALUES["error_mag_max"], 0.1, 100.0, help_text="Maximum error size as % of income.")

                        c_err_3, _ = st.columns(2)
                        with c_err_3: compact_text_input("Under-reporting Prob. (%)", "error_under_prob", DEFAULT_VALUES["error_under_prob"], 0.0, 100.0, help_text="Conditional prob. that an error results in under-reporting.")


        # =====================================================
        # ACTION BAR
        # =====================================================
        st.markdown('<hr style="margin-top: 12px; margin-bottom: 8px; border: none; border-top: 1px solid #D1D9E0;">', unsafe_allow_html=True)
        
        col_load, _, col_start = st.columns([2, 3, 2])
        
        with col_load:
            uploaded_config = st.file_uploader(
                "Load Config",
                type=["json"],
                key="config_uploader",
                label_visibility="collapsed",
                help="Load a configuration JSON file to populate all settings"
            )
            if uploaded_config is not None:
                # Create a unique identifier for this file upload
                file_id = f"{uploaded_config.name}_{uploaded_config.size}"
                # Only process if this is a NEW file (not already processed)
                if st.session_state.get("_last_loaded_config_id") != file_id:
                    try:
                        # Parse the uploaded JSON
                        config_data = json.load(uploaded_config)
                        # Mark this file as processed
                        st.session_state["_last_loaded_config_id"] = file_id
                        # Store in session state - will be applied on next render BEFORE widgets
                        st.session_state["_pending_config"] = config_data
                        st.session_state["_pending_config_name"] = uploaded_config.name
                        # Rerun to apply the config before widgets are instantiated
                        st.rerun()
                    except json.JSONDecodeError as e:
                        st.error(f"Invalid JSON file: {e}")
                    except Exception as e:
                        st.error(f"Error loading config: {e}")
            
            if uploaded_config:
                 st.markdown(f"<div style='text-align: center; color: #333333; font-size: 14px; margin-top: -10px; font-weight: 500;'>Loaded: {uploaded_config.name}</div>", unsafe_allow_html=True)

        with col_start:
            budget_exceeded = st.session_state.get("_budget_exceeded", False)
            
            if st.button("Start Simulation", type="primary", use_container_width=True, key="btn_start", disabled=budget_exceeded):
                # Capturing all parameter values from session state for simulation run
                st.session_state.simulation_params = {
                    # Simulation core
                    "n_agents": st.session_state["pop_slider"],

                    "n_steps": st.session_state["dur_slider"],
                    "n_runs": st.session_state["run_slider"],
                    "business_ratio": st.session_state["biz_ratio_slider"] / 100.0,
                    
                    # Behaviors
                    "tci_threshold_private": st.session_state["tci_threshold_priv_slider"],
                    "tci_threshold_business": st.session_state["tci_threshold_biz_slider"],

                    
                    # Enforcement
                    "tax_rate": st.session_state["tax_slider"] / 100.0,
                    "penalty_rate": st.session_state["penalty_slider"],
                    "audit_strategy": st.session_state["sel_audit"],
                    "audit_rate_private": st.session_state["priv_audit_slider"] / 100.0,
                    "audit_rate_business": st.session_state["biz_audit_slider"] / 100.0,
                    "audit_depth_books": st.session_state["audit_depth_slider"] / 100.0,
                    
                    # Interventions
                    "letter_enabled": st.session_state["letter_enabled"],
                    "letter_rate_private": st.session_state["letter_rate_priv_slider"] / 100.0,
                    "letter_rate_business": st.session_state["letter_rate_biz_slider"] / 100.0,
                    "letter_strategy": st.session_state.get("sel_letter_strategy", "random"),
                    # Letter Effects
                    "letter_eff_perm": st.session_state["letter_eff_perm"],
                    "letter_eff_temp": st.session_state["letter_eff_temp"],
                    "letter_eff_trust": st.session_state["letter_eff_trust"],
                    
                    "phone_enabled": st.session_state["phone_enabled"],
                    "phone_rate_private": st.session_state["phone_rate_priv_slider"] / 100.0,
                    "phone_rate_business": st.session_state["phone_rate_biz_slider"] / 100.0,
                    "phone_strategy": st.session_state.get("sel_phone_strategy", "random"),
                    # Phone Effects
                    "phone_sat_delta": st.session_state["phone_sat_delta"],
                    "phone_dissat_delta": st.session_state["phone_dissat_delta"],
                    "phone_eff_audit_temp": st.session_state["phone_eff_audit_temp"],
                    
                    # Service
                    "phone_sat": st.session_state["phone_sat_slider"] / 100.0,
                    "web_qual_private": st.session_state["web_qual_priv_slider"],
                    "web_qual_business": st.session_state["web_qual_biz_slider"],
                    "transparency": st.session_state["transparency_toggle"],
                    "huba_delta": st.session_state["huba_delta"],
                    
                    # Network & Social
                    "homophily": st.session_state["net_homo"],
                    "degree_mean": st.session_state["net_deg"],
                    "social_influence": st.session_state["soc_inf_slider"],
                    
                    # Belief Dynamics
                    "belief_mu": st.session_state["belief_mu"],
                    "belief_drift": st.session_state["belief_drift"], 
                    "belief_signal": st.session_state["belief_signal"],
                    "belief_perception": st.session_state["belief_perception"],
                    "belief_delta": st.session_state["belief_delta"],
                    "belief_target": st.session_state["belief_target"],
                    
                    # Optimization / Trust
                    "pso_sigma": _cfg.pso_update["sigma_pso"], # Using config default for hidden params
                    "pso_drift": _cfg.pso_update["pso_drift_rate"],
                    
                    # Traits - Private
                    "traits_private": {
                        "risk_aversion_mean": DEFAULT_VALUES["priv_risk_value"],
                        "risk_aversion_std": DEFAULT_VALUES["priv_risk_std"],
                        "subjective_audit_prob_mean": st.session_state["priv_audit_mean"],
                        "subjective_audit_prob_std": st.session_state["priv_audit_std"],
                        "personal_norms_mean": st.session_state["priv_pn_mean"],
                        "personal_norms_std": st.session_state["priv_pn_std"],
                        "social_norms_mean": st.session_state["priv_sn_mean"],
                        "social_norms_std": st.session_state["priv_sn_std"],
                        "societal_norms_mean": st.session_state["priv_stn_mean"],
                        "societal_norms_std": st.session_state["priv_stn_std"],
                        "pso_mean": st.session_state["priv_pso_mean"],
                        "pso_std": st.session_state["priv_pso_std"],
                        "p_trust_mean": st.session_state["priv_pt_mean"],
                        "p_trust_std": st.session_state["priv_pt_std"],
                    },
                    
                    # Traits - Business
                    "traits_business": {
                        "risk_aversion_mean": DEFAULT_VALUES["biz_risk_value"],
                        "risk_aversion_std": DEFAULT_VALUES["biz_risk_std"],
                        "subjective_audit_prob_mean": st.session_state["biz_audit_mean"],
                        "subjective_audit_prob_std": st.session_state["biz_audit_std"],
                        "personal_norms_mean": st.session_state["biz_pn_mean"],
                        "personal_norms_std": st.session_state["biz_pn_std"],
                        "social_norms_mean": st.session_state["biz_sn_mean"],
                        "social_norms_std": st.session_state["biz_sn_std"],
                        "societal_norms_mean": st.session_state["biz_stn_mean"],
                        "societal_norms_std": st.session_state["biz_stn_std"],
                        "pso_mean": st.session_state["biz_pso_mean"],
                        "pso_std": st.session_state["biz_pso_std"],
                        "p_trust_mean": st.session_state["biz_pt_mean"],
                        "p_trust_std": st.session_state["biz_pt_std"],
                    },
                    
                    # SME Specifics
                    "sme_risk": {
                        "base": st.session_state["risk_base"],
                        "delta_sector": st.session_state["delta_sector"],
                        "delta_cash": st.session_state["delta_cash"],
                        "delta_digi_high": st.session_state["delta_digi_high"],
                        "delta_advisor": st.session_state["delta_advisor"],
                        "delta_audit": st.session_state["delta_audit"],
                    },
                    "sme_opportunity": {
                        "base": st.session_state["sme_opp_base_slider"],
                        "min": st.session_state["sme_opp_min"], 
                        "max": st.session_state["sme_opp_max"],
                        "cash_bonus": st.session_state["sme_opp_cash"],
                        "low_digi_bonus": st.session_state["sme_opp_digi_low"],
                    },
                    
                    # Error Model
                    "error_model": {
                        "enabled": st.session_state["error_enabled"],
                        "rate_private": st.session_state["error_rate_priv"] / 100.0,
                        "rate_business": st.session_state["error_rate_biz"] / 100.0,
                        "under_report_prob": st.session_state["error_under_prob"] / 100.0,
                        "magnitude_min": st.session_state["error_mag_min"] / 100.0,
                        "magnitude_max": st.session_state["error_mag_max"] / 100.0,
                    }
                }
                
                st.session_state.current_page = "running"
                st.rerun()
            
            # Show error message if budget exceeded (outside button block)
            if budget_exceeded:
                st.markdown('<div style="color: #E53E3E; font-size: 12px; text-align: center; margin-top: 4px;">Budget exceeded. Reduce spending.</div>', unsafe_allow_html=True)

def _apply_config_to_state(config_data: dict):
    """
    Load a nested JSON config (as used by core/configs/*.json) into session state.
    Merges with defaults first, then maps to widget keys with proper clamping.
    """
    if not config_data:
        return
    
    # Merge with defaults to fill in any missing values
    from core.config import SimulationConfig, deep_merge
    defaults = SimulationConfig.load_defaults()
    merged = deep_merge(defaults.copy(), config_data)
    
    # Helper to clamp values within slider ranges
    def clamp(val, min_val, max_val):
        return max(min_val, min(max_val, val))
    
    # Helper to safely set state with type handling and slider sync
    def set_state(key, value):
        st.session_state[key] = value
        
        # Sync the corresponding input box if it exists
        input_key = f"{key}_input"
        if input_key in st.session_state:
            st.session_state[input_key] = value
            
        # Increment sync version to force slider refresh
        sync_key = f"{key}_sync_v"
        if sync_key in st.session_state:
            st.session_state[sync_key] += 1
    
    # =====================================================
    # SIMULATION SETUP
    # =====================================================
    sim = merged.get("simulation", {})
    set_state("pop_slider", clamp(sim.get("n_agents", 1000), 500, 10000))
    set_state("dur_slider", clamp(sim.get("n_steps", 50), 10, 100))
    # n_runs not in config files, keep default
    
    # =====================================================
    # TAX AUTHORITY STRATEGY - ENFORCEMENT & INTERVENTIONS (AUDIT)
    # =====================================================
    enf = merged.get("enforcement", {})  # Ensure enf is defined for later use (tax/penalty)
    
    # FIX: Check 'interventions.audit' first, as per config_final.json
    interv = merged.get("interventions", {})
    audit_interv = interv.get("audit", {})
    
    if audit_interv and audit_interv.get("rate"):
        # Use interventions schema
        set_state("priv_audit_slider", clamp(audit_interv.get("rate", {}).get("private", 0.01) * 100, 0.0, 10.0))
        set_state("biz_audit_slider", clamp(audit_interv.get("rate", {}).get("business", 0.01) * 100, 0.0, 5.0))
        
        strategy = audit_interv.get("selection_strategy", "random")
        if strategy in ["random", "risk_based", "network"]:
            set_state("sel_audit", strategy)
            
        books_prob = audit_interv.get("audit_type_probs", {}).get("books", 0.28) * 100
        set_state("audit_depth_slider", clamp(books_prob, 0.0, 100.0))
    else:
        # Fallback to legacy enforcement block
        audit_rate = enf.get("audit_rate", {})
        
        # Private audit rate 
        priv_audit = audit_rate.get("private", 0.01) * 100
        set_state("priv_audit_slider", clamp(priv_audit, 0.0, 10.0))
        
        # Business audit rate
        biz_audit = audit_rate.get("business", 0.01) * 100
        set_state("biz_audit_slider", clamp(biz_audit, 0.0, 5.0))
        
        # Audit depth
        audit_type_probs = enf.get("audit_type_probs", {})
        books_prob = audit_type_probs.get("books", 0.28) * 100
        set_state("audit_depth_slider", clamp(books_prob, 0.0, 100.0))
        
        # Audit strategy
        strategy = enf.get("audit_strategy", "random")
        if strategy in ["random", "risk_based", "network"]:
            set_state("sel_audit", strategy)
    
    # =====================================================
    # TAX AUTHORITY STRATEGY - INTERVENTIONS
    # =====================================================
    interv = merged.get("interventions", {})
    
    # Letters
    letters = interv.get("letter_deterrence", {})
    set_state("letter_enabled", letters.get("enabled", False))
    set_state("letter_rate_priv_slider", clamp(letters.get("rate", {}).get("private", 0.02) * 100, 0.0, 10.0))
    set_state("letter_rate_biz_slider", clamp(letters.get("rate", {}).get("business", 0.03) * 100, 0.0, 10.0))
    if letters.get("selection_strategy") in ["random", "risk_based", "network"]:
        set_state("sel_letter_strategy", letters.get("selection_strategy"))
        
    letter_eff = letters.get("effects", {})
    set_state("letter_eff_perm", letter_eff.get("subjective_audit_prob_permanent", 1.0))
    set_state("letter_eff_temp", letter_eff.get("subjective_audit_prob_temporary", 12.0))
    set_state("letter_eff_trust", letter_eff.get("trust_delta", -0.1))

    # Phone
    phone = interv.get("call", {})
    set_state("phone_enabled", phone.get("enabled", False))
    set_state("phone_rate_priv_slider", clamp(phone.get("rate", {}).get("private", 0.01) * 100, 0.0, 10.0))
    set_state("phone_rate_biz_slider", clamp(phone.get("rate", {}).get("business", 0.03) * 100, 0.0, 10.0))
    if phone.get("selection_strategy") in ["random", "risk_based", "network"]:
        set_state("sel_phone_strategy", phone.get("selection_strategy"))
        
    phone_eff = phone.get("effects", {})
    set_state("phone_sat_delta", phone_eff.get("satisfied", {}).get("pso_delta", 0.3))
    set_state("phone_dissat_delta", phone_eff.get("dissatisfied", {}).get("pso_delta", -0.2))
    set_state("phone_eff_audit_temp", phone_eff.get("satisfied", {}).get("subjective_audit_prob_temporary", 8.0))

    # =====================================================
    # TAX AUTHORITY STRATEGY - SERVICE
    # =====================================================
    pso_update = merged.get("pso_update", {})
    priv_pso = pso_update.get("private", {})
    
    # Phone satisfaction
    phone_sat = priv_pso.get("phone_satisfied_prob", 0.80) * 100
    set_state("phone_sat_slider", clamp(phone_sat, 50.0, 99.0))
    
    # Web quality
    web_qual_priv = priv_pso.get("webcare_mean", 3.2)
    set_state("web_qual_priv_slider", clamp(web_qual_priv, 1.0, 5.0))
    
    biz_pso = pso_update.get("business", {})
    web_qual_biz = biz_pso.get("webcare_mean", 3.5)
    set_state("web_qual_biz_slider", clamp(web_qual_biz, 1.0, 5.0))
    
    # Transparency (HUBA)
    set_state("huba_delta", pso_update.get("huba_delta", 1.0))
    
    # Transparency toggle logic
    trust_upd = merged.get("trust_update", {})
    p_unfair = trust_upd.get("p_unfair", 0.30)
    set_state("transparency_toggle", p_unfair < 0.2)
    
    # =====================================================
    # FISCAL ENVIRONMENT
    # =====================================================
    tax_rate = int(enf.get("tax_rate", 0.30) * 100)
    set_state("tax_slider", clamp(tax_rate, 10, 60))
    
    penalty = enf.get("penalty_rate", 3.0)
    set_state("penalty_slider", clamp(penalty, 1.0, 5.0))
    
    biz_ratio = sim.get("business_ratio", 0.179) * 100
    set_state("biz_ratio_slider", clamp(biz_ratio, 0, 100))
    
    # =====================================================
    # EXPERT: BELIEF & SOCIAL
    # =====================================================
    belief_upd = merged.get("belief_update", {})
    set_state("belief_mu", clamp(belief_upd.get("mu", 0.85), 0.0, 1.0))
    set_state("belief_drift", clamp(belief_upd.get("audit_prob_drift_rate", 0.1), 0.0, 1.0))
    set_state("belief_signal", clamp(belief_upd.get("audit_signal_strength", 0.3), 0.0, 100.0))
    # NEW: Missing belief params
    # Note: These keys might need new widgets in render() if they don't exist yet
    # For now, we ensure they are loaded if widgets exist
    set_state("belief_perception", clamp(belief_upd.get("perception_weight", 0.05), 0.0, 1.0))
    set_state("belief_delta", clamp(belief_upd.get("audit_prob_response_delta", 25.0), 0.0, 100.0))
    set_state("belief_target", clamp(belief_upd.get("audit_target_prob", 0.75), 0.0, 1.0))
    
    set_state("pso_sigma", pso_update.get("sigma_pso", 0.68))
    set_state("pso_drift", pso_update.get("pso_drift_rate", 0.25))
    set_state("trust_sigma", trust_upd.get("sigma_trust", 0.69))
    set_state("trust_punfair", clamp(trust_upd.get("p_unfair", 0.3), 0.0, 1.0))

    # =====================================================
    # EXPERT: NETWORK & BEHAVIOR
    # =====================================================
    social = merged.get("social", {})
    set_state("soc_inf_slider", clamp(social.get("social_influence", 0.5), 0.0, 1.0))
    
    network = merged.get("network", {})
    set_state("net_homo", clamp(network.get("homophily", 0.80), 0.0, 1.0))
    set_state("net_deg", clamp(network.get("degree_mean", 86.27), 5.0, 300.0))
    set_state("degree_std_value", network.get("degree_std", 64.99))
    
    # =====================================================
    # EXPERT: SME OPPORTUNITY
    # =====================================================
    sme = merged.get("sme", {}) # Access via 'sme' key not 'agents_config'
    opp = sme.get("opportunity", {})
    set_state("sme_opp_base_slider", clamp(opp.get("base", 0.35), 0.0, 1.0))
    set_state("sme_opp_min", clamp(opp.get("min", 0.10), 0.0, 1.0))
    set_state("sme_opp_max", clamp(opp.get("max", 0.80), 0.0, 1.0))
    set_state("sme_opp_cash", opp.get("cash_bonus", 0.25))
    set_state("sme_opp_digi_low", opp.get("low_digi_bonus", 0.10))
    set_state("sme_opp_digi_high", abs(opp.get("high_digi_penalty", 0.15)))
    set_state("sme_opp_high_risk", opp.get("high_risk_sector_bonus", 0.0))
    set_state("sme_opp_micro", opp.get("micro_bonus", 0.0))
    
    # Risk Modifiers
    set_state("risk_base_value", sme.get("base_risk_baseline", 0.2))
    set_state("delta_sector_value", sme.get("delta_sector_high_risk", 0.2))
    set_state("delta_cash_value", sme.get("delta_cash_intensive", 0.1))
    set_state("delta_digi_high_value", abs(sme.get("delta_digi_high", -0.1)))
    set_state("delta_advisor_value", abs(sme.get("delta_advisor_yes", -0.1)))
    set_state("delta_audit_value", abs(sme.get("delta_audit_books", -0.1)))
    
    # =====================================================
    # EXPERT: ERROR MODEL
    # =====================================================
    # FIX: Check ROOT first, then simulation block
    err = merged.get("error_model", sim.get("error_model", {}))
    
    set_state("error_enabled", err.get("enabled", False))
    set_state("error_rate_priv", err.get("private", {}).get("base", 0.005) * 100)
    set_state("error_rate_biz", err.get("business", {}).get("base", 0.35) * 100)
    set_state("error_mag_min", err.get("magnitude", {}).get("min", 0.12) * 100)
    set_state("error_mag_max", err.get("magnitude", {}).get("max", 0.23) * 100)
    set_state("error_under_prob", err.get("under_report_prob", 0.90) * 100)

    # =====================================================
    # DEEP TRAIT CALIBRATION
    # =====================================================
    traits = merged.get("traits", {})
    priv_traits = traits.get("private", {})
    biz_traits = traits.get("business", {})
    
    # Risk Aversion
    risk_av = priv_traits.get("risk_aversion", {})
    set_state("priv_risk_mean", clamp(risk_av.get("mean", 2.0), 0.5, 5.0))
    set_state("priv_risk_std", risk_av.get("std", 1.0))
    
    risk_av_biz = biz_traits.get("risk_aversion", {})
    set_state("biz_risk_mean", clamp(risk_av_biz.get("mean", 2.0), 0.5, 5.0))
    set_state("biz_risk_std", risk_av_biz.get("std", 1.0))
    
    # Behaviors (Honest Ratio -> Compliance Slider legacy)
    behaviors = merged.get("behaviors", {})
    dist = behaviors.get("distribution", {})
    honest = int(dist.get("honest", 0.80) * 100)
    set_state("compliance_slider", clamp(honest, 0, 100))
    
    # Private Traits
    priv_pn = priv_traits.get("personal_norms", {})
    set_state("priv_pn_mean", clamp(priv_pn.get("mean", 3.40), 1.0, 5.0))
    set_state("priv_pn_std", priv_pn.get("std", 1.15))
    
    priv_sn = priv_traits.get("social_norms", {})
    set_state("priv_sn_mean", clamp(priv_sn.get("mean", 3.42), 1.0, 5.0))
    set_state("priv_sn_std", priv_sn.get("std", 1.06))
    
    priv_stn = priv_traits.get("societal_norms", {})
    set_state("priv_stn_mean", clamp(priv_stn.get("mean", 3.97), 1.0, 5.0))
    set_state("priv_stn_std", priv_stn.get("std", 1.01))
    
    priv_pso = priv_traits.get("pso", {})
    set_state("priv_pso_mean", clamp(priv_pso.get("mean", 3.22), 1.0, 5.0))
    set_state("priv_pso_std", priv_pso.get("std", 0.68))
    
    priv_pt = priv_traits.get("p_trust", {})
    set_state("priv_pt_mean", clamp(priv_pt.get("mean", 3.37), 1.0, 5.0))
    set_state("priv_pt_std", priv_pt.get("std", 0.69))
    
    priv_audit = priv_traits.get("subjective_audit_prob", {})
    set_state("priv_audit_mean", clamp(priv_audit.get("mean", 10.0), 0.0, 100.0))
    set_state("priv_audit_std", priv_audit.get("std", 5.0)) # TODO: confirm default
    
    # Business Traits
    biz_pn = biz_traits.get("personal_norms", {})
    set_state("biz_pn_mean", clamp(biz_pn.get("mean", 3.82), 1.0, 5.0))
    set_state("biz_pn_std", biz_pn.get("std", 1.04))
    
    biz_sn = biz_traits.get("social_norms", {})
    set_state("biz_sn_mean", clamp(biz_sn.get("mean", 3.82), 1.0, 5.0))
    set_state("biz_sn_std", biz_sn.get("std", 1.02))
    
    biz_stn = biz_traits.get("societal_norms", {})
    set_state("biz_stn_mean", clamp(biz_stn.get("mean", 4.12), 1.0, 5.0))
    set_state("biz_stn_std", biz_stn.get("std", 0.98))
    
    biz_pso = biz_traits.get("pso", {})
    set_state("biz_pso_mean", clamp(biz_pso.get("mean", 3.18), 1.0, 5.0))
    set_state("biz_pso_std", biz_pso.get("std", 0.67))
    
    biz_pt = biz_traits.get("p_trust", {})
    set_state("biz_pt_mean", clamp(biz_pt.get("mean", 3.37), 1.0, 5.0))
    set_state("biz_pt_std", biz_pt.get("std", 0.69))
    
    biz_audit = biz_traits.get("subjective_audit_prob", {})
    set_state("biz_audit_mean", clamp(biz_audit.get("mean", 22.0), 0.0, 100.0))
    set_state("biz_audit_std", biz_audit.get("std", 5.0))

def load_params_into_state(params: dict):
    """
    Legacy function for loading flat simulation_params dict into state.
    Kept for backward compatibility.
    """
    if not params:
        return

    def clamp(val, min_val, max_val):
        return max(min_val, min(max_val, val))

    # Helper to safely set state with type handling and slider sync
    def set_state(key, value):
        st.session_state[key] = value
        
        # Sync the corresponding input box if it exists
        input_key = f"{key}_input"
        if input_key in st.session_state:
            st.session_state[input_key] = value
            
        # Increment sync version to force slider refresh
        sync_key = f"{key}_sync_v"
        if sync_key in st.session_state:
            st.session_state[sync_key] += 1

    # Simulation
    set_state("pop_slider", clamp(params.get("n_agents", 1000), 500, 2500))
    set_state("dur_slider", clamp(params.get("n_steps", 50), 10, 100))
    set_state("run_slider", clamp(params.get("n_runs", 1), 1, 10))
    
    # Enforcement
    set_state("tax_slider", clamp(int(params.get("tax_rate", 0.3) * 100), 10, 60))
    set_state("penalty_slider", clamp(params.get("penalty_rate", 3.0), 1.0, 5.0))
    set_state("compliance_slider", clamp(int(params.get("honest_ratio", 0.80) * 100), 0, 100))
    
    strategy = params.get("audit_strategy", "random")
    if strategy in ["random", "risk_based", "network"]:
        set_state("sel_audit", strategy)
    
    set_state("priv_audit_slider", clamp(params.get("audit_rate_private", 0.01) * 100, 0.0, 10.0))
    set_state("biz_audit_slider", clamp(params.get("audit_rate_business", 0.01) * 100, 0.0, 5.0))
    
    # biz_ratio uses standard sync mechanism
    set_state("biz_ratio_slider", biz_ratio_val)
    
    # Network/Social
    set_state("net_homo", clamp(params.get("homophily", 0.80), 0.0, 1.0))
    set_state("net_deg", clamp(params.get("degree_mean", 86.27), 5.0, 300.0))
    set_state("soc_inf_slider", clamp(params.get("social_influence", 0.5), 0.0, 1.0))