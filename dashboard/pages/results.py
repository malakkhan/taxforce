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


def create_chart(data, color="#01689B", y_format="auto"):
    """Create a clean, modern line chart."""
    fig = go.Figure()
    
    x_vals = list(range(1, len(data) + 1))
    
    # Convert color to rgb for transparency
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    
    # Area fill under line
    fig.add_trace(go.Scatter(
        x=x_vals,
        y=data,
        mode='lines',
        line=dict(color=color, width=3),
        fill='tozeroy',
        fillcolor=f"rgba({r}, {g}, {b}, 0.1)",
        hovertemplate="%{y:.2f}<extra></extra>" if y_format == "ratio" else "%{y:,.0f}<extra></extra>"
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
            tickformat=".0%" if y_format == "percent" else None,
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
    
    if not results:
        st.warning("No simulation results available.")
        if st.button("Run a Simulation", type="primary"):
            st.session_state.current_page = "simulate"
            st.rerun()
        return
    
    # Page header
    st.markdown(f"""
        <div style="margin-bottom: 32px;">
            <h1 style="font-size: 28px; font-weight: 700; color: #1A1A1A; margin: 0 0 8px 0;">
                Simulation Results
            </h1>
            <p style="font-size: 14px; color: #718096; margin: 0;">
                Completed {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # ===== KPI CARDS ROW =====
    kpi1, kpi2, kpi3, kpi4 = st.columns(4, gap="medium")
    
    with kpi1:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Total Tax Revenue</div>
                <div class="kpi-value">{format_number(results.get('total_taxes', 0))}</div>
                <div class="kpi-change positive">Collected</div>
            </div>
        """, unsafe_allow_html=True)
    
    with kpi2:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Tax Gap</div>
                <div class="kpi-value">{format_number(results.get('tax_gap', 0))}</div>
                <div class="kpi-change negative">Uncollected</div>
            </div>
        """, unsafe_allow_html=True)
    
    with kpi3:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Final Compliance</div>
                <div class="kpi-value">{format_percentage(results.get('final_compliance', 0))}</div>
                <div class="kpi-change positive">Fully compliant agents</div>
            </div>
        """, unsafe_allow_html=True)
    
    with kpi4:
        st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">Audits Performed</div>
                <div class="kpi-value">{results.get('total_audits', 0):,}</div>
                <div class="kpi-change">Total across simulation</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Spacing
    st.markdown("<div style='height: 32px'></div>", unsafe_allow_html=True)
    
    # ===== SUMMARY STATISTICS =====
    with st.expander("Summary Statistics", expanded=True):
        stat_cols = st.columns(4)
        
        with stat_cols[0]:
            st.metric("Initial Compliance", format_percentage(results.get('initial_compliance', 0)))
        with stat_cols[1]:
            st.metric("Max Compliance", format_percentage(results.get('max_compliance', 0)))
        with stat_cols[2]:
            st.metric("Final Declaration Ratio", format_percentage(results.get('final_declaration_ratio', 1)))
        with stat_cols[3]:
            # Calculate efficiency ratio
            total_taxes = results.get('total_taxes', 0)
            tax_gap = results.get('tax_gap', 0)
            theoretical = total_taxes + tax_gap
            efficiency = total_taxes / theoretical if theoretical > 0 else 1.0
            st.metric("Collection Efficiency", format_percentage(efficiency))
    
    # ===== CHARTS SECTION =====
    st.markdown("""
        <h2 style="font-size: 20px; font-weight: 600; color: #1A1A1A; margin: 20px 0;">
            Trends Over Time
        </h2>
    """, unsafe_allow_html=True)
    
    # Main chart - Tax Revenue
    with st.container(border=True):
        st.markdown("**Tax Revenue Over Time**")
        taxes_data = results.get("taxes_over_time", list(range(10, 60)))
        fig = create_chart(taxes_data, "#01689B")
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    # Four charts in 2x2 grid
    chart_row1_col1, chart_row1_col2 = st.columns(2, gap="medium")
    
    with chart_row1_col1:
        with st.container(border=True):
            st.markdown("**Compliance Rate**")
            compliance_data = results.get("compliance_over_time", [0.0] * 50)
            fig = create_chart(compliance_data, "#059669", y_format="percent")
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with chart_row1_col2:
        with st.container(border=True):
            st.markdown("**Tax Gap Trend**")
            gap_data = results.get("tax_gap_over_time", [100] * 50)
            fig = create_chart(gap_data, "#DC2626")
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    chart_row2_col1, chart_row2_col2 = st.columns(2, gap="medium")
    
    with chart_row2_col1:
        with st.container(border=True):
            st.markdown("**Average Declaration Ratio**")
            st.caption("Proportion of income declared (even partial compliance)")
            declaration_data = results.get("declaration_ratio_over_time", [1.0] * 50)
            fig = create_chart(declaration_data, "#7C3AED", y_format="percent")
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
    with chart_row2_col2:
        # Placeholder for future chart or can show a dual-axis comparison
        with st.container(border=True):
            st.markdown("**Compliance vs Declaration**")
            st.caption("Full compliance (green) vs partial declaration (purple)")
            
            fig = go.Figure()
            x_vals = list(range(1, len(compliance_data) + 1))
            
            fig.add_trace(go.Scatter(
                x=x_vals, y=compliance_data,
                mode='lines', name='Compliance Rate',
                line=dict(color='#059669', width=2),
            ))
            fig.add_trace(go.Scatter(
                x=x_vals, y=declaration_data,
                mode='lines', name='Declaration Ratio',
                line=dict(color='#7C3AED', width=2),
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
    
    # ===== SIMULATION PARAMETERS =====
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
    
    # ===== ACTION BAR =====
    st.markdown("<div style='height: 24px'></div>", unsafe_allow_html=True)
    st.divider()
    
    col1, spacer, col2 = st.columns([1, 3, 1])
    
    with col1:
        st.button("Export Results", use_container_width=True, key="btn_export")
    with col2:
        if st.button("New Simulation", type="primary", use_container_width=True, key="btn_new"):
            st.session_state.current_page = "simulate"
            st.rerun()
