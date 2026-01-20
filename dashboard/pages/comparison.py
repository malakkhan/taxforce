"""Simulation Run Comparison page - Direct port from iotprof with taxforce adaptations."""

import streamlit as st
import plotly.graph_objects as go

# Distinct colors for each run (up to 5)
RUN_COLORS = ["#01689B", "#059669", "#7C3AED", "#D97706", "#DC2626"]

# ESSENTIAL params - always shown in config comparison
ESSENTIAL_PARAMS = [
    ("n_agents", "Agents", lambda v: f"{v:,}" if v else "—"),
    ("n_steps", "Steps", lambda v: f"{v}" if v else "—"),
    ("audit_strategy", "Audit Strategy", lambda v: str(v).capitalize() if v else "—"),
    ("audit_rate_private", "Private Audit", lambda v: f"{v*100:.1f}%" if v else "—"),
    ("audit_rate_business", "Business Audit", lambda v: f"{v*100:.1f}%" if v else "—"),
    ("business_ratio", "Business Ratio", lambda v: f"{v*100:.0f}%" if v else "—"),
]

# OPTIONAL params - only shown if they differ between runs
OPTIONAL_PARAMS = [
    ("tax_rate", "Tax Rate", lambda v: f"{v*100:.0f}%" if v else "—"),
    ("penalty_rate", "Penalty Rate", lambda v: f"{v:.1f}×" if v else "—"),
    ("social_influence", "Social Influence", lambda v: f"{v:.2f}" if v is not None else "—"),
    ("homophily", "Homophily", lambda v: f"{v:.2f}" if v is not None else "—"),
    ("pso_boost", "PSO Boost", lambda v: f"{v:+.1f}" if v else "0"),
    ("trust_boost", "Trust Boost", lambda v: f"{v:+.1f}" if v else "0"),
]

# Combined for compatibility
CONFIG_PARAMS = ESSENTIAL_PARAMS + OPTIONAL_PARAMS


def inject_page_css():
    """Inject CSS overrides specific to comparison page to fix main.css aggressive rules."""
    st.markdown('''
        <style>
        /* ===== COMPARISON PAGE CSS OVERRIDES ===== */
        
        /* Add side padding to the main container */
        .main .block-container {
            padding-left: 40px !important;
            padding-right: 40px !important;
            max-width: 1400px !important;
            margin: 0 auto !important;
        }
        
        /* Fix button padding - main.css uses way too much, but exclude back button (first button in page) */
        /* Target buttons inside containers with borders (comparison page content) */
        [data-testid="stVerticalBlockBorderWrapper"] .stButton > button {
            padding: 6px 14px !important;
            min-width: auto !important;
            white-space: nowrap !important;
            font-size: 13px !important;
        }
        
        /* Fix container inner padding - main.css uses 24px which clips content */
        [data-testid="stVerticalBlockBorderWrapper"] > div {
            padding: 12px !important;
        }
        
        /* Scrollbar styling */
        [data-testid="stVerticalBlock"] > div[style*="height"] {
            scrollbar-width: thin;
            scrollbar-color: #D1D9E0 transparent;
        }
        
        /* Pill-shaped search input */
        [data-testid="stTextInput"] input {
            border-radius: 20px !important;
            border: 1px solid #D1D9E0 !important;
            padding: 8px 16px !important;
            font-size: 13px !important;
        }
        
        [data-testid="stTextInput"] input:focus {
            border-color: #01689B !important;
            box-shadow: 0 0 0 1px #01689B !important;
        }
        
        /* Add/Remove button specific styles */
        [data-testid="stButton"] button:has(p:contains("＋")),
        [data-testid="stButton"] button:has(p:contains("✕")) {
            padding: 4px 10px !important;
            min-width: 28px !important;
            border-radius: 6px !important;
        }
        
        /* Green outline for add buttons */
        [data-testid="stButton"] button:has(p:contains("＋")) {
            border-color: rgba(5, 150, 105, 0.4) !important;
        }
        
        /* Red outline for remove buttons */
        [data-testid="stButton"] button:has(p:contains("✕")) {
            border-color: rgba(220, 38, 38, 0.4) !important;
        }
        
        /* Restore back button styling - target by button key */
        button[data-testid^="baseButton-secondary"] {
            padding: 12px 24px !important;
            font-size: 14px !important;
            border: 1px solid #D1D9E0 !important;
        }
        
        /* But keep small buttons inside bordered containers */
        [data-testid="stVerticalBlockBorderWrapper"] button[data-testid^="baseButton-secondary"] {
            padding: 6px 14px !important;
            font-size: 13px !important;
        }
        </style>
    ''', unsafe_allow_html=True)


def find_differentiating_params(entries: list[dict]) -> list[str]:
    if len(entries) < 2:
        return []
    differing = []
    for param_key, _, _ in CONFIG_PARAMS:
        values = [e.get("params", {}).get(param_key) for e in entries]
        unique_vals = set(str(v) for v in values if v is not None)
        if len(unique_vals) > 1:
            differing.append(param_key)
    return differing


def get_run_label(entry: dict, run_index: int = None, differing_params: list[str] = None) -> str:
    """Get a consistent label for a run. Uses 'Run X' format when index is provided."""
    if run_index is not None:
        return f"Run {run_index + 1}"
    # Fallback to descriptive label
    parts = []
    n = entry.get("n_agents", 0)
    if n:
        parts.append(f"{n:,} agents")
    strategy = entry.get("params", {}).get("audit_strategy", "")
    if strategy:
        parts.append(strategy)
    return " · ".join(parts) if parts else "run"


def init_session_state():
    if "selected_for_comparison" not in st.session_state:
        st.session_state.selected_for_comparison = []


def render_selection_panel(history: list):
    """Render the run selection panel."""
    # Inline header: "Select Runs" + "Choose 2-5 runs"
    st.markdown('<div style="display:flex; align-items:baseline; gap:10px; margin-bottom:8px;">'
                '<span style="font-size:15px; font-weight:600; color:#1A1A1A;">Select Runs</span>'
                '<span style="font-size:12px; color:#718096;">Choose 2-5 runs</span></div>', 
                unsafe_allow_html=True)
    
    search = st.text_input("Search", placeholder="Search...", 
                           key="comp_search", label_visibility="collapsed")

    filtered_indices = list(range(len(history)))
    if search:
        search_lower = search.lower()
        filtered_indices = [
            i for i in filtered_indices
            if search_lower in history[i].get("date", "").lower()
            or search_lower in str(history[i].get("params", {}).get("audit_strategy", "")).lower()
        ]

    num_selected = len(st.session_state.selected_for_comparison)
    
    # Selected count and clear button
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**{num_selected}/5 Selected**")
    with col2:
        if num_selected > 0:
            if st.button("Clear", key="clear_sel"):
                st.session_state.selected_for_comparison = []
                st.rerun()

    # Scrollable run list - taller to show more runs
    with st.container(height=420):
        for idx in filtered_indices[:50]:
            entry = history[idx]
            is_selected = idx in st.session_state.selected_for_comparison

            col1, col2 = st.columns([5, 1])

            with col1:
                status = "✓ " if is_selected else ""
                date = entry.get("date", "Unknown")[:16]
                n_agents = entry.get("n_agents", 0)
                strategy = entry.get("params", {}).get("audit_strategy", "unknown")
                
                color = "#01689B" if is_selected else "#718096"
                weight = "600" if is_selected else "400"
                
                st.markdown(
                    f'<div style="font-size:11px; color:{color}; font-weight:{weight}; '
                    f'line-height:1.8; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">'
                    f'{status}{date} '
                    f'<span style="padding:1px 4px; border-radius:3px; font-size:8px; '
                    f'background:rgba(1,104,155,0.12); color:#01689B;">{n_agents:,}</span> '
                    f'<span style="padding:1px 4px; border-radius:3px; font-size:8px; '
                    f'background:rgba(5,150,105,0.12); color:#059669;">{strategy}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            with col2:
                if is_selected:
                    if st.button("✕", key=f"r_{idx}", help="Remove"):
                        st.session_state.selected_for_comparison.remove(idx)
                        st.rerun()
                else:
                    if st.button("＋", key=f"a_{idx}", disabled=num_selected >= 5, help="Add"):
                        st.session_state.selected_for_comparison.append(idx)
                        st.rerun()


def render_config_comparison(entries: list[dict], differing_params: list[str]):
    """Render configuration comparison table."""
    st.markdown("**Configuration Comparison**")
    
    if not entries:
        st.caption("Select runs to compare their configurations")
        return
    
    n_runs = len(entries)
    
    # Header row with run dates
    header_cols = st.columns([1.5] + [1] * n_runs)
    with header_cols[0]:
        st.markdown('<div style="font-size:11px; color:#718096; padding:4px 0;">PARAMETER</div>', unsafe_allow_html=True)
    
    for i, entry in enumerate(entries):
        with header_cols[i + 1]:
            run_color = RUN_COLORS[i % len(RUN_COLORS)]
            run_label = f"Run {i + 1}"
            date = entry.get("date", "Unknown")[:10]
            st.markdown(
                f'<div style="text-align:center; padding:4px 0;">'
                f'<div style="font-size:12px; font-weight:600; color:{run_color};">{run_label}</div>'
                f'<div style="font-size:9px; color:#718096;">{date}</div></div>',
                unsafe_allow_html=True
            )
    
    st.markdown('<div style="border-bottom:1px solid #D1D9E0; margin:4px 0;"></div>', unsafe_allow_html=True)
    
    # Build list of params to display:
    # 1. All essential params (always shown)
    # 2. Optional params only if they differ
    params_to_show = list(ESSENTIAL_PARAMS)  # Always show essential
    
    # Add optional params that differ
    differing_optional = [(k, l, f) for k, l, f in OPTIONAL_PARAMS if k in differing_params]
    if differing_optional:
        params_to_show.extend(differing_optional)
    
    # Helper to render a param row
    def render_param_row(param_key, param_label, formatter, is_differing):
        row_cols = st.columns([1.5] + [1] * n_runs)
        
        with row_cols[0]:
            if is_differing:
                st.markdown(f'<div style="font-size:11px; font-weight:700; color:#1A1A1A; padding:4px 0;">{param_label}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div style="font-size:11px; color:#718096; padding:4px 0;">{param_label}</div>', unsafe_allow_html=True)
        
        for i, entry in enumerate(entries):
            with row_cols[i + 1]:
                params = entry.get("params", {})
                if param_key == "n_agents":
                    val = entry.get("n_agents", params.get("n_agents"))
                elif param_key == "n_steps":
                    val = entry.get("n_steps", params.get("n_steps"))
                else:
                    val = params.get(param_key)
                formatted = formatter(val)
                
                if is_differing:
                    st.markdown(
                        f'<div style="text-align:center; font-size:11px; font-weight:700; color:#1A1A1A; '
                        f'background:rgba(1, 104, 155, 0.1); padding:4px 6px; border-radius:4px;">{formatted}</div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f'<div style="text-align:center; font-size:11px; color:#4A5568; padding:4px 0;">{formatted}</div>',
                        unsafe_allow_html=True
                    )
    
    # Scrollable config rows - matches run list height
    with st.container(height=420):
        # Render essential params
        for param_key, param_label, formatter in ESSENTIAL_PARAMS:
            is_differing = param_key in differing_params
            render_param_row(param_key, param_label, formatter, is_differing)
        
        # Separator if there are differing optional params
        if differing_optional:
            st.markdown('<div style="border-top:1px dashed #D1D9E0; margin:8px 0; padding-top:4px;">'
                       '<span style="font-size:9px; color:#A0AEC0; text-transform:uppercase;">Differing Parameters</span></div>', 
                       unsafe_allow_html=True)
            
            for param_key, param_label, formatter in differing_optional:
                render_param_row(param_key, param_label, formatter, is_differing=True)


def render_metrics_comparison(entries: list[dict], differing_params: list[str]):
    """Render performance metrics cards."""
    st.markdown("#### Performance Results")

    if len(entries) < 2:
        st.info("Select at least 2 runs")
        return

    metric_defs = [
        ("total_taxes", "Total Taxes", lambda v: f"€{v/1e6:.1f}M" if v and v >= 1e6 else (f"€{v/1e3:.1f}K" if v and v >= 1e3 else f"€{v:.0f}" if v else "—"), "higher"),
        ("total_tax_gap", "Tax Gap", lambda v: f"€{v/1e6:.1f}M" if v and v >= 1e6 else (f"€{v/1e3:.1f}K" if v and v >= 1e3 else f"€{v:.0f}" if v else "—"), "lower"),
        ("final_compliance", "Final Compliance", lambda v: f"{v*100:.1f}%" if v else "—", "higher"),
        ("final_declaration_ratio", "Declaration Ratio", lambda v: f"{v*100:.1f}%" if v else "—", "higher"),
        ("final_four", "Final FOUR", lambda v: f"{v*100:.1f}%" if v else "—", "lower"),
        ("final_tax_morale", "Tax Morale", lambda v: f"{v:.1f}%" if v else "—", "higher"),
        ("final_mgtr", "Final MGTR", lambda v: f"{v*100:.1f}%" if v else "—", "higher"),
        ("total_penalties", "Correction Yield", lambda v: f"€{v/1e6:.1f}M" if v and v >= 1e6 else (f"€{v/1e3:.1f}K" if v and v >= 1e3 else f"€{v:.0f}" if v else "—"), "higher"),
    ]

    best_values = {}
    for key, _, _, direction in metric_defs:
        vals = [e.get("results", {}).get(key, 0) for e in entries if e.get("results", {}).get(key, 0) > 0]
        if vals:
            best_values[key] = max(vals) if direction == "higher" else min(vals)

    cols = st.columns(len(entries))

    for i, entry in enumerate(entries):
        with cols[i]:
            run_color = RUN_COLORS[i % len(RUN_COLORS)]
            label = get_run_label(entry, run_index=i)
            date = entry.get("date", "Unknown")[:10]

            st.markdown(f"""
                <div style="text-align:center; padding:8px; background:white; 
                            border:2px solid {run_color}; border-radius:8px; margin-bottom:10px;">
                    <div style="font-size:12px; font-weight:600; color:{run_color};">{date}</div>
                    <div style="font-size:10px; color:#718096;">{label}</div>
                </div>
            """, unsafe_allow_html=True)

            results = entry.get("results", {})
            for key, metric_label, formatter, _ in metric_defs:
                val = results.get(key, 0)
                is_best = val > 0 and val == best_values.get(key)
                formatted = formatter(val) if val else "—"
                
                if is_best:
                    st.markdown(f"""
                        <div style="padding:6px 8px; margin-bottom:4px; background:rgba(5, 150, 105, 0.08); 
                                    border-radius:6px; border-left:3px solid #059669;">
                            <div style="font-size:9px; color:#718096; text-transform:uppercase;">{metric_label}</div>
                            <div style="font-size:14px; font-weight:600; color:#059669;">{formatted}</div>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div style="padding:6px 8px; margin-bottom:4px; background:white; 
                                    border-radius:6px; border:1px solid #E8EEF2;">
                            <div style="font-size:9px; color:#718096; text-transform:uppercase;">{metric_label}</div>
                            <div style="font-size:14px; font-weight:500; color:#1A1A1A;">{formatted}</div>
                        </div>
                    """, unsafe_allow_html=True)


def render_chart(entries: list[dict], data_key: str, title: str, y_format: str = "auto", differing_params: list[str] = None):
    """Render a comparison line chart."""
    has_data = any(e.get("results", {}).get(data_key) for e in entries)
    
    with st.container(border=True):
        st.markdown(f"**{title}**")
        
        if not has_data:
            st.caption("No data available")
            return

        fig = go.Figure()
        for i, entry in enumerate(entries):
            data = entry.get("results", {}).get(data_key, [])
            if not data:
                continue
            color = RUN_COLORS[i % len(RUN_COLORS)]
            label = get_run_label(entry, run_index=i)
            date = entry.get("date", "Unknown")[:10]
            name = f"{date} ({label})"
            x_vals = [j / max(len(data) - 1, 1) * 100 for j in range(len(data))]
            fig.add_trace(go.Scatter(
                x=x_vals, y=data, mode="lines", name=name,
                line=dict(color=color, width=2),
            ))

        fig.update_layout(
            paper_bgcolor="white",
            plot_bgcolor="white",
            font=dict(color="#4A5568", family="Inter, sans-serif", size=11),
            height=260,
            margin=dict(t=20, b=40, l=50, r=15),
            xaxis=dict(title="Progress (%)", gridcolor="#E8EEF2", linecolor="#D1D9E0", tickfont=dict(size=10), zeroline=False),
            yaxis=dict(gridcolor="#E8EEF2", linecolor="#D1D9E0", tickfont=dict(size=10), zeroline=False,
                       tickformat=".0%" if y_format == "percent" else None),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, font=dict(size=9), bgcolor="rgba(255,255,255,0)"),
            showlegend=True,
            hovermode="x unified",  # Show all values at same x position when hovering
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})


def render():
    """Main render function for comparison page."""
    # Inject CSS overrides first
    inject_page_css()
    init_session_state()

    # Create centered content area with side padding (like simulate.py)
    left_spacer, content, right_spacer = st.columns([0.15, 8, 0.15])
    
    with content:
        # Page header - inline with subtitle like iotprof
        st.markdown('<div style="display:flex; align-items:baseline; gap:16px; margin-bottom:4px;">'
                    '<span style="font-size:28px; font-weight:700; color:#1A1A1A;">Compare Runs</span>'
                    '<span style="font-size:14px; color:#718096;">Side-by-side performance comparison</span></div>', 
                    unsafe_allow_html=True)
        st.markdown('<div style="border-bottom:1px solid #D1D9E0; margin-bottom:28px;"></div>', unsafe_allow_html=True)

        # Load history and sort by date (most recent first)
        try:
            from utils.history import load_history
            from datetime import datetime
            
            history = load_history()
            
            # Sort by date descending (most recent first)
            def parse_date(entry):
                try:
                    # Format: "Jan 18, 2026, 07:06 PM"
                    return datetime.strptime(entry.get("date", ""), "%b %d, %Y, %I:%M %p")
                except:
                    return datetime.min
            
            history = sorted(history, key=parse_date, reverse=True)
        except Exception:
            history = []

        if not history:
            st.info("No simulation runs found. Run some simulations first.")
            return

        selected_indices = st.session_state.selected_for_comparison
        selected_entries = [history[i] for i in selected_indices if i < len(history)]
        differing_params = find_differentiating_params(selected_entries)

        # Main layout: Selection panel | Config comparison
        # Note: No height on outer containers - they size naturally
        col_select, col_config = st.columns([1, 2.5])

        with col_select:
            with st.container(border=True):
                render_selection_panel(history)

        with col_config:
            with st.container(border=True):
                render_config_comparison(selected_entries, differing_params)

        # Performance results section
        if len(selected_entries) >= 2:
            st.markdown("---")
            render_metrics_comparison(selected_entries, differing_params)

            st.markdown("---")
            st.markdown("#### Charts")

            col1, col2 = st.columns(2)
            with col1:
                render_chart(selected_entries, "taxes_over_time", "Tax Revenue Over Time", differing_params=differing_params)
            with col2:
                render_chart(selected_entries, "compliance_over_time", "Compliance Rate", y_format="percent", differing_params=differing_params)

            col3, col4 = st.columns(2)
            with col3:
                render_chart(selected_entries, "tax_gap_over_time", "Tax Gap Over Time", differing_params=differing_params)
            with col4:
                render_chart(selected_entries, "declaration_ratio_over_time", "Declaration Ratio", y_format="percent", differing_params=differing_params)


            col5, col6 = st.columns(2)
            with col5:
                render_chart(selected_entries, "four_over_time", "Fraud Opportunity Use Rate (FOUR)", y_format="percent", differing_params=differing_params)
            with col6:
                render_chart(selected_entries, "tax_morale_over_time", "Tax Morale Index", differing_params=differing_params)


            col7, col8 = st.columns(2)
            with col7:
                render_chart(selected_entries, "mgtr_over_time", "Mean Gross Tax Rate (MGTR)", y_format="percent", differing_params=differing_params)
            with col8:
                render_chart(selected_entries, "pso_over_time", "Service Experience (Avg PSO)", differing_params=differing_params)

        elif len(selected_entries) == 1:
            st.markdown("---")
            st.info("Select one more run to compare")
        else:
            st.markdown("---")
            st.info("Select 2+ runs to compare")
