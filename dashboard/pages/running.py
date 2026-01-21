"""
Running Page - Execute actual simulation with real model.
Displays progress and collects results from TaxComplianceModel.
"""
import streamlit as st
import time
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core.model import TaxComplianceModel
from core.config import SimulationConfig, deep_merge


def build_config_overrides(params: dict) -> dict:
    """
    Convert dashboard params to config override structure.
    Only includes values that the dashboard sets - no redundant defaults.
    """
    overrides = {}
    
    # Simulation settings
    overrides["simulation"] = {
        "n_agents": params.get("n_agents"),
        "business_ratio": params.get("business_ratio"),
    }
    
    # Enforcement settings
    overrides["enforcement"] = {
        "tax_rate": params.get("tax_rate"),
        "penalty_rate": params.get("penalty_rate"),
        "audit_rate": {
            "private": params.get("audit_rate_private"),
            "business": params.get("audit_rate_business"),
        },
        "audit_strategy": params.get("audit_strategy"),
    }
    
    # Behavior distribution
    honest_ratio = params.get("honest_ratio")
    if honest_ratio is not None:
        overrides["behaviors"] = {
            "distribution": {
                "honest": honest_ratio,
                "dishonest": 1.0 - honest_ratio,
            }
        }
    
    # Network settings
    overrides["network"] = {
        "homophily": params.get("homophily"),
        "degree_mean": params.get("degree_mean"),
        "degree_std": params.get("degree_std"),
    }
    
    # Social dynamics
    overrides["social"] = {
        "social_influence": params.get("social_influence"),
        "pso_boost": params.get("pso_boost"),
        "trust_boost": params.get("trust_boost"),
    }
    
    # Norm Update Scales
    norm_update = params.get("norm_update", {})
    if norm_update:
        overrides["norm_update"] = norm_update
    
    # Traits - Private
    traits_private = params.get("traits_private", {})
    if traits_private:
        priv_traits = {}
        if "personal_norms_mean" in traits_private:
            priv_traits["personal_norms"] = {"mean": traits_private["personal_norms_mean"]}
        if "social_norms_mean" in traits_private:
            priv_traits["social_norms"] = {"mean": traits_private["social_norms_mean"]}
        if "societal_norms_mean" in traits_private:
            priv_traits["societal_norms"] = {"mean": traits_private["societal_norms_mean"]}
        if "pso_mean" in traits_private:
            priv_traits["perceived_service_orientation"] = {"mean": traits_private["pso_mean"]}
        if "trust_mean" in traits_private:
            priv_traits["perceived_trustworthiness"] = {"mean": traits_private["trust_mean"]}
        if "subjective_audit_prob_mean" in traits_private:
            priv_traits["subjective_audit_prob"] = {"mean": traits_private["subjective_audit_prob_mean"]}
        
        if priv_traits:
            overrides.setdefault("traits", {})["private"] = priv_traits
    
    # Traits - Business
    traits_business = params.get("traits_business", {})
    if traits_business:
        biz_traits = {}
        if "personal_norms_mean" in traits_business:
            biz_traits["personal_norms"] = {"mean": traits_business["personal_norms_mean"]}
        if "social_norms_mean" in traits_business:
            biz_traits["social_norms"] = {"mean": traits_business["social_norms_mean"]}
        if "societal_norms_mean" in traits_business:
            biz_traits["societal_norms"] = {"mean": traits_business["societal_norms_mean"]}
        if "pso_mean" in traits_business:
            biz_traits["perceived_service_orientation"] = {"mean": traits_business["pso_mean"]}
        if "trust_mean" in traits_business:
            biz_traits["perceived_trustworthiness"] = {"mean": traits_business["trust_mean"]}
        if "subjective_audit_prob_mean" in traits_business:
            biz_traits["subjective_audit_prob"] = {"mean": traits_business["subjective_audit_prob_mean"]}
        
        if biz_traits:
            overrides.setdefault("traits", {})["business"] = biz_traits
    
    # Private income
    if "income_mean" in traits_private:
        overrides["private"] = {"income": {"mean": traits_private["income_mean"]}}
    
    # Belief strategy drift - sync with subjective audit prob
    priv_audit = traits_private.get("subjective_audit_prob_mean")
    biz_audit = traits_business.get("subjective_audit_prob_mean")
    if priv_audit is not None or biz_audit is not None:
        drift = {}
        if priv_audit is not None:
            drift["private"] = {"mean": priv_audit}
        if biz_audit is not None:
            drift["business"] = {"mean": biz_audit}
        overrides["belief_strategies"] = {"hashimzade": {"drift": drift}}
    
    # SME Risk parameters
    sme_risk = params.get("sme_risk", {})
    if sme_risk:
        sme_overrides = {}
        if "base" in sme_risk:
            sme_overrides["base_risk_baseline"] = sme_risk["base"]
        if "delta_sector" in sme_risk:
            sme_overrides["delta_sector_high_risk"] = sme_risk["delta_sector"]
        if "delta_cash" in sme_risk:
            sme_overrides["delta_cash_intensive"] = sme_risk["delta_cash"]
        if "delta_digi_high" in sme_risk:
            sme_overrides["delta_digi_high"] = sme_risk["delta_digi_high"]
        if "delta_advisor" in sme_risk:
            # Dashboard sets a single value, apply to both yes/no
            sme_overrides["delta_advisor_yes"] = -abs(sme_risk["delta_advisor"])
            sme_overrides["delta_advisor_no"] = abs(sme_risk["delta_advisor"])
        if "delta_audit" in sme_risk:
            # Dashboard sets a single value, apply to books (stronger)
            sme_overrides["delta_audit_books"] = -abs(sme_risk["delta_audit"])
            sme_overrides["delta_audit_admin"] = -abs(sme_risk["delta_audit"]) * 0.3
        
        if sme_overrides:
            overrides["sme"] = sme_overrides
    
    # Clean up None values from overrides
    def remove_none(d):
        if isinstance(d, dict):
            return {k: remove_none(v) for k, v in d.items() if v is not None}
        return d
    
    return remove_none(overrides)


def run_simulation(params: dict, progress_callback=None):
    """
    Run the actual simulation and return results.
    """
    n_steps = params.get("n_steps", 50)
    n_runs = params.get("n_runs", 1)
    
    # Build config with overrides
    defaults = SimulationConfig.load_defaults()
    overrides = build_config_overrides(params)
    config_data = deep_merge(defaults, overrides)
    cfg = SimulationConfig(config_data)
    
    # Aggregate results across runs
    all_compliance = []
    all_tax_gap = []
    all_taxes = []
    all_audits = []
    all_declaration_ratio = []
    all_tax_morale = []
    all_four = []
    all_pso = []
    all_mgtr = []
    all_penalties = []
    
    total_iterations = n_runs * n_steps
    current_iteration = 0
    
    for run_idx in range(n_runs):
        # Create fresh model for each run
        model = TaxComplianceModel(config=cfg, seed=42 + run_idx)
        
        run_compliance = []
        run_tax_gap = []
        run_taxes = []
        run_audits = []
        run_declaration_ratio = []
        run_tax_morale = []
        run_four = []
        run_pso = []
        run_mgtr = []
        run_penalties = []
        
        for step in range(n_steps):
            model.step()
            
            # Collect metrics after each step
            df = model.datacollector.get_model_vars_dataframe()
            if len(df) > 0:
                run_compliance.append(df['Compliance_Rate'].iloc[-1])
                run_tax_gap.append(df['Tax_Gap'].iloc[-1])
                run_taxes.append(df['Total_Taxes'].iloc[-1])
                run_audits.append(df['Audits'].iloc[-1])
                run_declaration_ratio.append(df['Avg_Declaration_Ratio'].iloc[-1])
                run_tax_morale.append(df['Tax_Morale'].iloc[-1])
                run_four.append(df['Avg_FOUR'].iloc[-1])
                run_pso.append(df['Avg_PSO'].iloc[-1])
                run_mgtr.append(df['MGTR'].iloc[-1])
                run_penalties.append(df['Penalties'].iloc[-1])
            
            # Update progress
            current_iteration += 1
            if progress_callback:
                progress_callback(current_iteration / total_iterations, 
                                  f"Run {run_idx+1}/{n_runs}, Step {step+1}/{n_steps}")
        
        all_compliance.append(run_compliance)
        all_tax_gap.append(run_tax_gap)
        all_taxes.append(run_taxes)
        all_audits.append(run_audits)
        all_declaration_ratio.append(run_declaration_ratio)
        all_tax_morale.append(run_tax_morale)
        all_four.append(run_four)
        all_pso.append(run_pso)
        all_mgtr.append(run_mgtr)
        all_penalties.append(run_penalties)
    
    # Average across runs
    import numpy as np
    avg_compliance = np.mean(all_compliance, axis=0).tolist()
    avg_tax_gap = np.mean(all_tax_gap, axis=0).tolist()
    avg_taxes = np.mean(all_taxes, axis=0).tolist()
    avg_declaration_ratio = np.mean(all_declaration_ratio, axis=0).tolist()
    avg_tax_morale = np.mean(all_tax_morale, axis=0).tolist()
    avg_four = np.mean(all_four, axis=0).tolist()
    avg_pso = np.mean(all_pso, axis=0).tolist()
    avg_mgtr = np.mean(all_mgtr, axis=0).tolist()
    total_audits = int(np.mean([sum(run) for run in all_audits]))
    total_penalties = float(np.mean([sum(run) for run in all_penalties]))
    
    # Build results dict
    results = {
        "compliance_over_time": avg_compliance,
        "tax_gap_over_time": avg_tax_gap,
        "taxes_over_time": avg_taxes,
        "declaration_ratio_over_time": avg_declaration_ratio,
        "tax_morale_over_time": avg_tax_morale,
        "four_over_time": avg_four,
        "pso_over_time": avg_pso,
        "mgtr_over_time": avg_mgtr,
        "total_taxes": int(np.mean([sum(t) for t in all_taxes])),
        "total_tax_gap": int(np.mean([sum(tg) for tg in all_tax_gap])),  # Cumulative gap
        "final_tax_gap": float(np.mean([tg[-1] for tg in all_tax_gap])),  # Final year only
        "final_compliance": float(avg_compliance[-1]) if avg_compliance else 0.0,
        "initial_compliance": float(avg_compliance[0]) if avg_compliance else 0.0,
        "max_compliance": float(max(avg_compliance)) if avg_compliance else 0.0,
        "final_declaration_ratio": float(avg_declaration_ratio[-1]) if avg_declaration_ratio else 1.0,
        "final_tax_morale": float(avg_tax_morale[-1]) if avg_tax_morale else 0.0,
        "initial_tax_morale": float(avg_tax_morale[0]) if avg_tax_morale else 0.0,
        "final_four": float(avg_four[-1]) if avg_four else 0.0,
        "final_pso": float(avg_pso[-1]) if avg_pso else 0.0,
        "final_mgtr": float(avg_mgtr[-1]) if avg_mgtr else 0.0,
        "total_penalties": total_penalties,
        "total_audits": total_audits,
    }
    
    return results


def render():
    """Render the simulation running page."""
    
    # Aggressive CSS to hide any leftover elements from previous page
    # Uses a pseudo-element to create a solid background that covers remnants
    st.markdown("""
        <style>
        /* Hide any expanders that might be leftover from simulate page */
        [data-testid="stExpander"] {
            display: none !important;
        }
        
        /* Ensure running page has clean background */
        .main .block-container {
            padding-top: 2rem !important;
            background: #E8F4FD !important;
            min-height: 100vh !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Get simulation parameters
    params = st.session_state.get("simulation_params", {})
    if not params:
        st.session_state.current_page = "simulate"
        st.rerun()
        return
    
    # Use a single container that takes up the viewport
    main_container = st.container()
    
    with main_container:
        # Create centered layout
        spacer1, center, spacer2 = st.columns([1, 2, 1])
        
        with center:
            st.write("")
            st.write("")
            st.write("")
            
            # Progress card
            with st.container(border=True):
                st.markdown("### Running simulation...")
                st.caption("Executing tax compliance model")
                
                st.write("")
                progress_bar = st.progress(0)
                status_text = st.empty()
                st.write("")
                
                # Cancel button placeholder
                cancel_col1, cancel_col2, cancel_col3 = st.columns([1, 1, 1])
                with cancel_col2:
                    cancel_placeholder = st.empty()
            
            st.write("")
    
    # Progress callback
    def update_progress(progress, status):
        progress_bar.progress(progress)
        status_text.markdown(f"**{status}**")
    
    # Run actual simulation
    try:
        results_data = run_simulation(params, update_progress)
        
        # Store results in session
        st.session_state.simulation_results = results_data
        st.session_state.simulation_params_used = params
        
        # Add to history (disk persistence)
        try:
            from utils.history import add_history_entry
            
            history_entry = {
                "date": datetime.now().strftime("%b %d, %Y, %I:%M %p"),
                "n_agents": params.get("n_agents", 1000),
                "n_steps": params.get("n_steps", 50),
                "total_taxes": results_data["total_taxes"],
                "tax_gap": results_data["final_tax_gap"],
                "compliance": results_data["final_compliance"],
                "audits": results_data["total_audits"],
                "results": results_data,
                "params": params,
            }
            add_history_entry(history_entry)
        except Exception as e:
            # Log the error for debugging but don't crash
            import logging
            logging.warning(f"Failed to save history: {e}")
        
        time.sleep(0.3)
        st.session_state.current_page = "results"
        st.rerun()
        
    except Exception as e:
        st.error(f"Simulation failed: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        if st.button("Back to Configuration"):
            st.session_state.current_page = "simulate"
            st.rerun()
