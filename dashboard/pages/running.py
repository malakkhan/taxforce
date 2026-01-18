"""
Running Page - Display simulation progress.
Clean centered design with progress bar matching Figma prototype.
"""
import streamlit as st
import time
import random
from datetime import datetime


def render():
    """Render the simulation running page."""
    
    # Get simulation parameters
    params = st.session_state.get("simulation_params", {})
    if not params:
        st.session_state.current_page = "simulate"
        st.rerun()
        return
    
    # Create centered layout
    spacer1, center, spacer2 = st.columns([1, 2, 1])
    
    with center:
        st.write("")
        st.write("")
        st.write("")
        
        # Progress card
        with st.container(border=True):
            st.markdown("### Running simulation...")
            st.caption("Calculating tax gains and interventions")
            
            st.write("")
            progress_bar = st.progress(0)
            status_text = st.empty()
            st.write("")
            
            # Cancel button placeholder
            cancel_col1, cancel_col2, cancel_col3 = st.columns([1, 1, 1])
            with cancel_col2:
                cancel_btn = st.button("Cancel", use_container_width=True, key="btn_cancel")
        
        st.write("")
    
    if cancel_btn:
        st.session_state.current_page = "simulate"
        st.rerun()
        return
    
    # Run simulation
    n_agents = params.get("n_agents", 1000)
    n_steps = params.get("n_steps", 50)
    n_runs = params.get("n_runs", 10)
    
    total_iterations = n_runs
    
    # Simulate progress
    results_data = {
        "total_taxes": 0,
        "interventions": 0,
        "tax_morale": 0,
        "tax_gap": 0,
        "compliance_over_time": [],
        "taxes_over_time": [],
        "tax_gap_over_time": [],
    }
    
    for i in range(total_iterations):
        progress = (i + 1) / total_iterations
        progress_bar.progress(progress)
        status_text.markdown(f"**{int(progress * 100)}% complete**")
        
        # Simulate some work
        time.sleep(0.3)
        
        # Accumulate results
        results_data["total_taxes"] += random.uniform(1000000, 2000000)
        results_data["interventions"] += random.randint(50, 100)
    
    # Finalize results
    results_data["total_taxes"] = int(results_data["total_taxes"] / n_runs)
    results_data["interventions"] = int(results_data["interventions"] / n_runs)
    results_data["tax_morale"] = random.uniform(0.75, 0.95)
    results_data["tax_gap"] = results_data["total_taxes"] * random.uniform(0.05, 0.15)
    
    # Generate time series data
    for step in range(n_steps):
        results_data["compliance_over_time"].append(0.85 + random.uniform(-0.05, 0.10) * (step / n_steps))
        results_data["taxes_over_time"].append(results_data["total_taxes"] * (0.8 + 0.4 * step / n_steps))
        results_data["tax_gap_over_time"].append(results_data["tax_gap"] * (1.2 - 0.4 * step / n_steps))
    
    # Store results in session
    st.session_state.simulation_results = results_data
    st.session_state.simulation_params_used = params
    
    # Add to history (disk persistence)
    try:
        from utils.history import add_history_entry
        
        history_entry = {
            "date": datetime.now().strftime("%b %d, %Y, %I:%M %p"),
            "n_agents": n_agents,
            "n_steps": n_steps,
            "total_taxes": results_data["total_taxes"],
            "tax_gap": results_data["tax_gap"],
            "interventions": results_data["interventions"],
            "tax_morale": results_data["tax_morale"],
            "results": results_data,
            "params": params,
        }
        add_history_entry(history_entry)
    except Exception as e:
        # History persistence is optional
        pass
    
    time.sleep(0.5)
    st.session_state.current_page = "results"
    st.rerun()
