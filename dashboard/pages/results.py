"""
Results Page - Display simulation results.
Clean layout with KPI cards at top and charts below.
"""
import streamlit as st
import plotly.graph_objects as go
from datetime import datetime


def format_number(n):
    """Format numbers for display."""
    if n >= 1_000_000:
        return f"€{n/1_000_000:.1f}M"
    elif n >= 1_000:
        return f"€{n/1_000:.1f}K"
    else:
        return f"€{n:.0f}"


def format_percentage(n):
    """Format as percentage."""
    return f"{n*100:.1f}%"


def create_chart(data, color="#01689B", y_format="auto", auto_range=False):
    """Create a clean, modern line chart.
    
    Args:
        auto_range: If True, zoom Y-axis to data range with 10% padding
    """
    fig = go.Figure()
    
    x_vals = list(range(1, len(data) + 1))
    
    # Convert color to rgb for transparency
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    
    # Default hover template
    if y_format == "percent":
        hover_template = "%{y:.1%}<extra></extra>"
    elif y_format == "ratio":
        hover_template = "%{y:.2f}<extra></extra>"
    else:
        hover_template = "%{y:,.0f}<extra></extra>"
    
    # Calculate Y-axis range with padding if auto_range
    y_range = None
    tick_format = None
    if auto_range and data:
        data_min = min(data)
        data_max = max(data)
        data_range = data_max - data_min
        padding = data_range * 0.15  # 15% padding
        if padding == 0:
            padding = data_max * 0.1  # If flat line, use 10% of value
        y_range = [data_min - padding, data_max + padding]
        
        # Dynamically adjust precision for percentage format based on data range
        if y_format == "percent":
            if data_range < 0.01:  # Less than 1% variation
                tick_format = ".2%"
                hover_template = "%{y:.2%}<extra></extra>"
            elif data_range < 0.05:  # Less than 5% variation
                tick_format = ".1%"
                hover_template = "%{y:.1%}<extra></extra>"
            else:
                tick_format = ".0%"
    elif y_format == "percent":
        tick_format = ".0%"
    
    # Area fill under line (disable for auto_range to avoid fill extending to 0)
    fig.add_trace(go.Scatter(
        x=x_vals,
        y=data,
        mode='lines',
        line=dict(color=color, width=3),
        fill='tozeroy' if not auto_range else None,
        fillcolor=f"rgba({r}, {g}, {b}, 0.1)" if not auto_range else None,
        hovertemplate=hover_template,
        showlegend=False,
    ))
    
    fig.update_layout(
        xaxis=dict(
            title=dict(text="Time Period", font=dict(size=12, color="#718096")),
            tickfont=dict(size=11, color="#718096"),
            showgrid=True,
            gridcolor="#E8EEF2",
            zeroline=False,
        ),
        yaxis=dict(
            tickfont=dict(size=11, color="#718096"),
            showgrid=True,
            gridcolor="#E8EEF2",
            zeroline=False,
            tickformat=tick_format,
            range=y_range,
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=40, r=20, t=20, b=40),
        height=280,
        hovermode="x unified",
    )
    
    return fig


def render():
    """Render the results page."""
    
    # Get results
    results = st.session_state.get("simulation_results", {})
    params = st.session_state.get("simulation_params_used", {})
    
    # Create centered content area with side padding
    left_spacer, content, right_spacer = st.columns([0.15, 8, 0.15])
    
    with content:
        if not results:
            st.warning("No simulation results available.")
            if st.button("Run a Simulation", type="primary"):
                st.session_state.current_page = "simulate"
                st.rerun()
            return
        
        # Page header - title with date inline (like History page)
        st.markdown(f'<div style="display:flex; align-items:baseline; gap:16px; margin-bottom:4px;">'
                    f'<span style="font-size:28px; font-weight:700; color:#1A1A1A;">Simulation Results</span>'
                    f'<span style="font-size:14px; color:#718096;">{datetime.now().strftime("%B %d, %Y at %I:%M %p")}</span></div>', 
                    unsafe_allow_html=True)
        st.markdown('<div style="border-bottom:1px solid #D1D9E0; margin-bottom:24px;"></div>', unsafe_allow_html=True)
        
        # ===== KPI CARDS ROW =====
        kpi1, kpi2, kpi3, kpi4 = st.columns(4, gap="medium")
    
        with kpi1:
            st.markdown(f"""
                <div class="kpi-card" title="Total tax revenue collected from declared income across all agents throughout the simulation.">
                    <div class="kpi-label">Total Tax Revenue</div>
                    <div class="kpi-value">{format_number(results.get('total_taxes', 0))}</div>
                    <div class="kpi-change positive">Collected</div>
                </div>
            """, unsafe_allow_html=True)
        
        with kpi2:
            st.markdown(f"""
                <div class="kpi-card" title="Total calculated tax gap (evaded income × tax rate) accumulated across all agents and steps.">
                    <div class="kpi-label">Total Tax Gap</div>
                    <div class="kpi-value">{format_number(results.get('total_tax_gap', 0))}</div>
                    <div class="kpi-change negative">Cumulative uncollected</div>
                </div>
            """, unsafe_allow_html=True)
        
        with kpi3:
            st.markdown(f"""
                <div class="kpi-card" title="Percentage of agents who were fully compliant (100% declaration) in the final simulation step.">
                    <div class="kpi-label">Final Compliance</div>
                    <div class="kpi-value">{format_percentage(results.get('final_compliance', 0))}</div>
                    <div class="kpi-change positive">Fully compliant agents</div>
                </div>
            """, unsafe_allow_html=True)
        
        with kpi4:
            st.markdown(f"""
                <div class="kpi-card" title="Average number of audits conducted per simulation run.">
                    <div class="kpi-label">Audits Performed</div>
                    <div class="kpi-value">{results.get('total_audits', 0):,}</div>
                    <div class="kpi-change">Average per run</div>
                </div>
            """, unsafe_allow_html=True)
        
        # Small spacing between KPI rows
        st.markdown("<div style='height: 16px'></div>", unsafe_allow_html=True)
        
        # ===== KPI CARDS ROW 2 (New Metrics) =====
        kpi5, kpi6, kpi7, kpi8 = st.columns(4, gap="medium")
        
        with kpi5:
            final_four = results.get('final_four', 0)
            st.markdown(f"""
                <div class="kpi-card" title="Fraud Opportunity Use Rate: Average evasion rate among non-honest agents who had an opportunity to evade.">
                    <div class="kpi-label">Final FOUR</div>
                    <div class="kpi-value">{format_percentage(final_four)}</div>
                    <div class="kpi-change">Fraud opportunity use</div>
                </div>
            """, unsafe_allow_html=True)
        
        with kpi6:
            final_morale = results.get('final_tax_morale', 0)
            st.markdown(f"""
                <div class="kpi-card" title="Average intrinsic willingness to pay taxes (0-100%), weighted by social norms, societal norms, PSO, and trust.">
                    <div class="kpi-label">Tax Morale</div>
                    <div class="kpi-value">{final_morale:.1f}%</div>
                    <div class="kpi-change positive">Intrinsic willingness</div>
                </div>
            """, unsafe_allow_html=True)
        
        with kpi7:
            final_mgtr = results.get('final_mgtr', 0)
            st.markdown(f"""
                <div class="kpi-card" title="Mean Gross Tax Rate: The effective tax burden (Taxes + Penalties) divided by True Income in the final step.">
                    <div class="kpi-label">Final MGTR</div>
                    <div class="kpi-value">{format_percentage(final_mgtr)}</div>
                    <div class="kpi-change positive">Effective tax rate</div>
                </div>
            """, unsafe_allow_html=True)
        
        with kpi8:
            total_penalties = results.get('total_penalties', 0)
            st.markdown(f"""
                <div class="kpi-card" title="Average total revenue generated from penalties per simulation run.">
                    <div class="kpi-label">Correction Yield</div>
                    <div class="kpi-value">{format_number(total_penalties)}</div>
                    <div class="kpi-change">Avg penalties per run</div>
                </div>
            """, unsafe_allow_html=True)
        
        # Spacing
        st.markdown("<div style='height: 32px'></div>", unsafe_allow_html=True)
        
        # ===== SUMMARY STATISTICS =====
        with st.expander("Summary Statistics", expanded=True):
            stat_cols = st.columns(4, gap="medium")
            
            with stat_cols[0]:
                st.metric("Initial Compliance", format_percentage(results.get('initial_compliance', 0)), help="Percentage of fully compliant agents at the start of the simulation.")
            with stat_cols[1]:
                st.metric("Max Compliance", format_percentage(results.get('max_compliance', 0)), help="The highest compliance rate achieved during any single step of the simulation.")
            with stat_cols[2]:
                st.metric("Final Declaration Ratio", format_percentage(results.get('final_declaration_ratio', 1)), help="Average ratio of (Declared Income / True Income) across all agents in the final step.")
            with stat_cols[3]:
                # Calculate efficiency ratio
                total_taxes = results.get('total_taxes', 0)
                tax_gap = results.get('tax_gap', 0)
                theoretical = total_taxes + tax_gap
                efficiency = total_taxes / theoretical if theoretical > 0 else 1.0
                st.metric("Collection Efficiency", format_percentage(efficiency), help="Ratio of Total Taxes Collected / (Total Taxes + Tax Gap). Represents the percentage of theoretical potential revenue that was actually captured.")
        
        # ===== SIMULATION PARAMETERS (moved up for visibility) =====
        with st.expander("Simulation Parameters Used"):
            param_cols = st.columns(3)
            
            with param_cols[0]:
                st.markdown("**Population**")
                st.write(f"• Agents: {params.get('n_agents', 'N/A'):,}")
                st.write(f"• Business ratio: {params.get('business_ratio', 0)*100:.1f}%")
                st.write(f"• Steps: {params.get('n_steps', 'N/A')}")
            
            with param_cols[1]:
                st.markdown("**Policy**")
                st.write(f"• Tax rate: {params.get('tax_rate', 0)*100:.0f}%")
                st.write(f"• Penalty: {params.get('penalty_rate', 0):.1f}×")
                st.write(f"• Runs: {params.get('n_runs', 'N/A')}")
            
            with param_cols[2]:
                st.markdown("**Enforcement**")
                st.write(f"• Strategy: {params.get('audit_strategy', 'N/A')}")
                st.write(f"• Private audit: {params.get('audit_rate_private', 0)*100:.1f}%")
                st.write(f"• Business audit: {params.get('audit_rate_business', 0)*100:.1f}%")
        
        # ===== CHARTS SECTION =====
        st.markdown("""
            <h2 style="font-size: 20px; font-weight: 600; color: #1A1A1A; margin: 20px 0;">
                Trends Over Time
            </h2>
        """, unsafe_allow_html=True)
        
        # Main chart - Tax Revenue
        with st.container(border=True):
            st.markdown("**Tax Revenue Over Time**", help="Total tax revenue collected at each simulation step.")
            taxes_data = results.get("taxes_over_time", list(range(10, 60)))
            fig = create_chart(taxes_data, "#01689B", auto_range=True)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        # Four charts in 2x2 grid
        chart_row1_col1, chart_row1_col2 = st.columns(2, gap="medium")
        
        with chart_row1_col1:
            with st.container(border=True):
                st.markdown("**Compliance Rate**", help="Percentage of agents who are fully compliant (100% declaration) at each step.")
                compliance_data = results.get("compliance_over_time", [0.0] * 50)
                fig = create_chart(compliance_data, "#059669", y_format="percent", auto_range=True)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        with chart_row1_col2:
            with st.container(border=True):
                st.markdown("**Tax Gap Trend**", help="Total uncollected tax revenue (evaded income × tax rate) at each step.")
                gap_data = results.get("tax_gap_over_time", [100] * 50)
                fig = create_chart(gap_data, "#DC2626")
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        chart_row2_col1, chart_row2_col2 = st.columns(2, gap="medium")
        
        with chart_row2_col1:
            with st.container(border=True):
                st.markdown("**Average Declaration Ratio**", help="Average ratio of (Declared Income / True Income) across all agents at each step.")
                declaration_data = results.get("declaration_ratio_over_time", [1.0] * 50)
                fig = create_chart(declaration_data, "#7C3AED", y_format="percent", auto_range=True)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        with chart_row2_col2:
            with st.container(border=True):
                st.markdown("**Tax Morale**", help="Average Tax Morale score (0-100%) across population, reflecting intrinsic willingness to comply.")
                morale_data_raw = results.get("tax_morale_over_time", [50.0] * 50)
                # Convert from 0-100 to 0-1 scale for percentage formatting
                morale_data = [v / 100 for v in morale_data_raw]
                fig = create_chart(morale_data, "#F59E0B", y_format="percent", auto_range=True)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        # Third row: FOUR and MGTR
        chart_row3_col1, chart_row3_col2 = st.columns(2, gap="medium")
        
        with chart_row3_col1:
            with st.container(border=True):
                st.markdown("**Fraud Opportunity Use Rate (FOUR)**", help="Average evasion rate among non-honest agents who had an opportunity to evade.")
                four_data = results.get("four_over_time", [0.5] * 50)
                fig = create_chart(four_data, "#EF4444", y_format="percent", auto_range=True)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        with chart_row3_col2:
            with st.container(border=True):
                st.markdown("**Mean Gross Tax Rate (MGTR)**", help="Effective tax rate: (Total Revenue + Penalties) / Total True Income.")
                mgtr_data = results.get("mgtr_over_time", [0.3] * 50)
                fig = create_chart(mgtr_data, "#3B82F6", y_format="percent", auto_range=True)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        # Fourth row: PSO and Comparison
        chart_row4_col1, chart_row4_col2 = st.columns(2, gap="medium")
        
        with chart_row4_col1:
            with st.container(border=True):
                st.markdown("**Service Experience (1-5 scale)**", help="Average Perceived Service Orientation (PSO) towards the tax authority.")
                pso_data = results.get("pso_over_time", [3.0] * 50)
                fig = create_chart(pso_data, "#10B981", y_format="ratio", auto_range=True)
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        with chart_row4_col2:
            with st.container(border=True):
                st.markdown("**Compliance vs Declaration**", help="Direct comparison of the Compliance Rate (binary) vs the Declaration Ratio (continuous) to show if agents are partially evading or fully compliant.")
                
                fig = go.Figure()
                x_vals = list(range(1, len(compliance_data) + 1))
                
                fig.add_trace(go.Scatter(
                    x=x_vals, y=compliance_data,
                    mode='lines', name='Compliance Rate',
                    line=dict(color='#059669', width=2),
                    hovertemplate="%{y:.1%}<extra></extra>",
                ))
                fig.add_trace(go.Scatter(
                    x=x_vals, y=declaration_data,
                    mode='lines', name='Declaration Ratio',
                    line=dict(color='#7C3AED', width=2),
                    hovertemplate="%{y:.1%}<extra></extra>",
                ))
                
                fig.update_layout(
                    xaxis=dict(title="Time Period", tickfont=dict(size=11), showgrid=True, gridcolor="#E8EEF2"),
                    yaxis=dict(tickfont=dict(size=11), showgrid=True, gridcolor="#E8EEF2", tickformat=".0%"),
                    plot_bgcolor="white", paper_bgcolor="white",
                    margin=dict(l=40, r=20, t=20, b=40),
                    height=280, hovermode="x unified",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    showlegend=True,
                )
                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        
        # ===== ACTION BAR =====
        # Custom tight separator
        st.markdown('<hr style="margin-top: 12px; margin-bottom: 8px; border: none; border-top: 1px solid #D1D9E0;">', unsafe_allow_html=True)
        
        # Custom style for the big action button
        st.markdown("""
            <style>
                div[data-testid="stElementContainer"].st-key-btn_sim_config button {
                    font-size: 16px !important;
                    font-weight: 600 !important;
                    padding: 10px 24px !important;
                }
            </style>
        """, unsafe_allow_html=True)
        
        # Single primary button aligned to right - reduced width (5:1 ratio)
        spacer, col_btn = st.columns([5, 1])
        
        with col_btn:
            if st.button("Simulate With Config", type="primary", use_container_width=True, key="btn_sim_config", help="Load these settings and return to simulation setup"):
                from pages.simulate import load_params_into_state
                load_params_into_state(params)
                st.session_state.current_page = "simulate"
                st.rerun()
