"""Simulation Run Comparison page - Direct port from iotprof with taxforce adaptations."""

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime


def format_date_iso(date_str: str) -> str:
    """Convert date from 'Jan 18, 2026, 07:06:30 PM' format to '2026-01-18 19:06:30' ISO format."""
    if not date_str or date_str == "Unknown":
        return "Unknown"
    try:
        # Try new format with seconds first
        dt = datetime.strptime(date_str, "%b %d, %Y, %I:%M:%S %p")
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        try:
            # Fall back to old format without seconds (for existing history entries)
            dt = datetime.strptime(date_str, "%b %d, %Y, %I:%M %p")
            return dt.strftime("%Y-%m-%d %H:%M:00")
        except (ValueError, TypeError):
            # If all parsing fails, return as-is
            return date_str


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

# Keys that are essential (not shown in optional section)
ESSENTIAL_KEYS = {p[0] for p in ESSENTIAL_PARAMS}


def flatten_params(params: dict, prefix: str = "") -> dict:
    """Flatten nested dict into dot-notation keys."""
    flat = {}
    for key, value in params.items():
        full_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict):
            flat.update(flatten_params(value, full_key))
        else:
            flat[full_key] = value
    return flat


def format_param_value(key: str, value) -> str:
    """Generic formatter for any param value."""
    if value is None:
        return "—"
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, float):
        # Check if it looks like a percentage (0-1 range)
        if 0 <= value <= 1 and "rate" in key.lower() or "ratio" in key.lower():
            return f"{value*100:.1f}%"
        return f"{value:.3g}"
    if isinstance(value, int):
        return f"{value:,}"
    return str(value)


def format_param_label(key: str) -> str:
    """Convert param key to human-readable label."""
    # Handle dot notation (nested keys)
    parts = key.split(".")
    # Take the last part and convert to readable
    name = parts[-1]
    # Convert snake_case to Title Case
    return name.replace("_", " ").title()

# Priority order for chips (most identifiable first)
# This determines which params show as chips when there are too many differences
PARAM_PRIORITY = [
    "audit_strategy",      # Most identifiable - the approach used
    "audit_rate_private",  # Key enforcement param
    "audit_rate_business", # Key enforcement param  
    "business_ratio",      # Population composition
    "tax_rate",            # Economic param
    "penalty_rate",        # Economic param
    "honest_ratio",        # Initial compliance
    "income_mean",         # Economic param
    "social_influence",    # Behavioral param
    "homophily",           # Network param
    "degree_mean",         # Network param
    "degree_std",          # Network param
    "pso_boost",           # Service experience
    "trust_boost",         # Trust in government
    "n_agents",            # Scale param (usually same)
    "n_steps",             # Duration param (usually same)
]

# Chip color scheme by category with shades
# Format: (text_color, bg_color) - using darker tones for better contrast
CHIP_COLORS = {
    # ENFORCEMENT (Teal family) - audit strategy and rates
    "enforcement_primary": ("#0F766E", "#0F766E18"),    # Teal-700
    "enforcement_secondary": ("#0D9488", "#0D948818"),  # Teal-600
    "enforcement_tertiary": ("#14B8A6", "#14B8A618"),   # Teal-500
    
    # TAX POLICY (Amber family) - tax rate, penalty
    "tax_primary": ("#B45309", "#B4530918"),            # Amber-700
    "tax_secondary": ("#D97706", "#D9770618"),          # Amber-600
    
    # POPULATION (Purple family) - business ratio, honest ratio
    "population_primary": ("#6D28D9", "#6D28D918"),     # Violet-700
    "population_secondary": ("#7C3AED", "#7C3AED18"),   # Violet-600
    
    # NETWORK (Indigo family) - homophily, degree
    "network_primary": ("#4338CA", "#4338CA18"),        # Indigo-700
    "network_secondary": ("#4F46E5", "#4F46E518"),      # Indigo-600
    "network_tertiary": ("#6366F1", "#6366F118"),       # Indigo-500
    
    # SOCIAL (Rose family) - social influence, PSO, trust
    "social_primary": ("#BE123C", "#BE123C18"),         # Rose-700
    "social_secondary": ("#E11D48", "#E11D4818"),       # Rose-600
    "social_tertiary": ("#F43F5E", "#F43F5E18"),        # Rose-500
    
    # SCALE (Emerald family) - agents, steps
    "scale_primary": ("#047857", "#04785718"),          # Emerald-700
    "scale_secondary": ("#059669", "#05966918"),        # Emerald-600
    
    # TRAITS PRIVATE (Sky family) - private agent traits
    "traits_priv_primary": ("#0369A1", "#0369A118"),    # Sky-700
    "traits_priv_secondary": ("#0284C7", "#0284C718"),  # Sky-600
    
    # TRAITS BUSINESS (Orange family) - business agent traits
    "traits_biz_primary": ("#C2410C", "#C2410C18"),     # Orange-700
    "traits_biz_secondary": ("#EA580C", "#EA580C18"),   # Orange-600
    
    # SME RISK (Fuchsia family) - SME risk deltas
    "sme_primary": ("#A21CAF", "#A21CAF18"),            # Fuchsia-700
    "sme_secondary": ("#C026D3", "#C026D318"),          # Fuchsia-600
    
    # NORM UPDATE (Lime family) - norm scales
    "norm_primary": ("#4D7C0F", "#4D7C0F18"),           # Lime-700
    "norm_secondary": ("#65A30D", "#65A30D18"),         # Lime-600
}


def get_chip_style(param_key: str) -> tuple[str, str]:
    """Get chip color based on param key. Supports nested params via pattern matching."""
    # Exact matches first
    style_map = {
        # Enforcement
        "audit_strategy": CHIP_COLORS["enforcement_primary"],
        "audit_rate_private": CHIP_COLORS["enforcement_secondary"],
        "audit_rate_business": CHIP_COLORS["enforcement_tertiary"],
        # Tax Policy
        "tax_rate": CHIP_COLORS["tax_primary"],
        "penalty_rate": CHIP_COLORS["tax_secondary"],
        # Population
        "business_ratio": CHIP_COLORS["population_primary"],
        "honest_ratio": CHIP_COLORS["population_secondary"],
        "income_mean": CHIP_COLORS["tax_primary"],  # Group with other economic params
        # Network
        "homophily": CHIP_COLORS["network_primary"],
        "degree_mean": CHIP_COLORS["network_secondary"],
        "degree_std": CHIP_COLORS["network_tertiary"],
        # Social
        "social_influence": CHIP_COLORS["social_primary"],
        "pso_boost": CHIP_COLORS["social_secondary"],
        "trust_boost": CHIP_COLORS["social_tertiary"],
        # Scale
        "n_agents": CHIP_COLORS["scale_primary"],
        "n_steps": CHIP_COLORS["scale_secondary"],
        "n_runs": CHIP_COLORS["scale_secondary"],
    }
    
    if param_key in style_map:
        return style_map[param_key]
    
    # Pattern-based matching for nested params
    if param_key.startswith("traits_private."):
        return CHIP_COLORS["traits_priv_primary"]
    if param_key.startswith("traits_business."):
        return CHIP_COLORS["traits_biz_primary"]
    if param_key.startswith("sme_risk."):
        return CHIP_COLORS["sme_primary"]
    if param_key.startswith("norm_update."):
        return CHIP_COLORS["norm_primary"]
    
    # Default fallback (gray)
    return ("#64748B", "#64748B15")

# Chip formatters (short display format)
CHIP_FORMATTERS = {
    "audit_strategy": lambda v: str(v).capitalize() if v else None,
    "audit_rate_private": lambda v: f"{v*100:.1f}% priv" if v is not None else None,
    "audit_rate_business": lambda v: f"{v*100:.1f}% biz" if v is not None else None,
    "business_ratio": lambda v: f"{v*100:.0f}% SME" if v is not None else None,
    "honest_ratio": lambda v: f"{v*100:.0f}% honest" if v is not None else None,
    "income_mean": lambda v: f"€{v/1000:.0f}k avg" if v else None,
    "tax_rate": lambda v: f"{v*100:.0f}% tax" if v is not None else None,
    "penalty_rate": lambda v: f"{v:.1f}× pen" if v is not None else None,
    "social_influence": lambda v: f"ω={v:.2f}" if v is not None else None,
    "homophily": lambda v: f"h={v:.2f}" if v is not None else None,
    "degree_mean": lambda v: f"{v:.0f} conn" if v else None,
    "degree_std": lambda v: f"±{v:.0f}" if v else None,
    "pso_boost": lambda v: f"PSO{v:+.1f}" if v else None,
    "trust_boost": lambda v: f"trust{v:+.1f}" if v else None,
    "n_agents": lambda v: f"{v:,}" if v else None,
    "n_steps": lambda v: f"{v} steps" if v else None,
}


def get_run_chips(entry: dict, differing_params: list[str], max_chips: int = 3) -> list[tuple[str, str, str]]:
    """
    Get chips for a run, prioritizing differing params.
    Returns list of (text, text_color, bg_color) tuples.
    """
    chips = []
    params = entry.get("params", {})
    
    # First pass: differing params in priority order
    for param in PARAM_PRIORITY:
        if param in differing_params and len(chips) < max_chips:
            # Get value from entry or params dict
            if param == "n_agents":
                val = entry.get("n_agents", params.get("n_agents"))
            elif param == "n_steps":
                val = entry.get("n_steps", params.get("n_steps"))
            else:
                val = params.get(param)
            
            if val is not None:
                formatter = CHIP_FORMATTERS.get(param)
                if formatter:
                    text = formatter(val)
                    if text:
                        colors = get_chip_style(param)
                        chips.append((text, colors[0], colors[1]))
    
    # Second pass: if we have no chips, add non-differing priority params
    if not chips:
        for param in PARAM_PRIORITY[:3]:  # Top 3 priority
            val = params.get(param)
            if param == "n_agents":
                val = entry.get("n_agents", val)
            if val is not None and len(chips) < max_chips:
                formatter = CHIP_FORMATTERS.get(param)
                if formatter:
                    text = formatter(val)
                    if text:
                        colors = get_chip_style(param)
                        chips.append((text, colors[0], colors[1]))
    
    return chips


def get_short_label(entry: dict, differing_params: list[str]) -> str:
    """Get a short label for chart legends using up to 3 differing params."""
    params = entry.get("params", {})
    parts = []
    
    # Check differing params first, in priority order
    for param in PARAM_PRIORITY:
        if param in differing_params:
            if param == "n_agents":
                val = entry.get("n_agents", params.get("n_agents"))
            elif param == "n_steps":
                val = entry.get("n_steps", params.get("n_steps"))
            else:
                val = params.get(param)
            
            if val is not None:
                formatter = CHIP_FORMATTERS.get(param)
                if formatter:
                    text = formatter(val)
                    if text:
                        parts.append(text)
                        
        if len(parts) >= 3:
            break
    
    if parts:
        full_label = " ⋅ ".join(parts)
        # Dynamic shortening if too long
        if len(full_label) > 30:
            replacements = {
                "Random": "Rnd",
                "Standard": "Std",
                "Network": "Net",
                "honest": "hon",
                "private": "priv",
                "business": "biz", 
                "audit": "aud",
                "income": "inc",
                "tax_rate": "tax",
                "penalty": "pen",
                "ratio": "rt",
                " 1.0%": " 1%", # Shorten percentages
                " 2.0%": " 2%",
                " 0.5%": " .5%",
            }
            for old, new in replacements.items():
                full_label = full_label.replace(old, new)
                if len(full_label) <= 30: # Stop if short enough
                    break
        return full_label
            
    # Fallback: strategy or agent count
    strategy = params.get("audit_strategy")
    if strategy:
        return str(strategy).capitalize()
    
    n_agents = entry.get("n_agents", params.get("n_agents"))
    if n_agents:
        return f"{n_agents:,}"
    
    return "run"


def render_chips_html(chips: list[tuple[str, str, str]]) -> str:
    """Generate HTML for inline chips."""
    if not chips:
        return ""
    
    html_parts = []
    for text, text_color, bg_color in chips:
        html_parts.append(
            f'<span style="display:inline-block; padding:1px 5px; margin:1px; border-radius:3px; '
            f'font-size:10px; font-weight:500; background:{bg_color}; color:{text_color};">{text}</span>'
        )
    return "".join(html_parts)


def get_default_values() -> dict:
    """Get default simulation values from SimulationConfig. Returns nested structure matching history format."""
    from core.config import SimulationConfig
    _cfg = SimulationConfig.default()
    return {
        # Top-level params
        "n_agents": _cfg.simulation["n_agents"],
        "n_steps": _cfg.simulation["n_steps"],
        "n_runs": 1,
        "business_ratio": _cfg.simulation["business_ratio"],
        "tax_rate": _cfg.enforcement["tax_rate"],
        "penalty_rate": _cfg.enforcement["penalty_rate"],
        "audit_strategy": "random",
        "audit_rate_private": _cfg.enforcement["audit_rate"]["private"],
        "audit_rate_business": _cfg.enforcement["audit_rate"]["business"],
        "honest_ratio": _cfg.behaviors.get("distribution", {"honest": 0.92})["honest"],
        "social_influence": _cfg.social["social_influence"],
        "homophily": _cfg.network["homophily"],
        "degree_mean": _cfg.network["degree_mean"],
        "degree_std": _cfg.network["degree_std"],
        "pso_boost": _cfg.social["pso_boost"],
        "trust_boost": _cfg.social["trust_boost"],
        
        # Nested: Norm Update Scales
        "norm_update": {
            "social_norm_scale": {
                "private": _cfg.norm_update["social_norm_scale"]["private"],
                "business": _cfg.norm_update["social_norm_scale"]["business"],
            },
            "societal_norm_scale": {
                "private": _cfg.norm_update["societal_norm_scale"]["private"],
                "business": _cfg.norm_update["societal_norm_scale"]["business"],
            },
        },
        
        # Nested: Traits - Private
        "traits_private": {
            "personal_norms_mean": _cfg.traits["private"]["personal_norms"]["mean"],
            "social_norms_mean": _cfg.traits["private"]["social_norms"]["mean"],
            "societal_norms_mean": _cfg.traits["private"]["societal_norms"]["mean"],
            "pso_mean": _cfg.traits["private"]["pso"]["mean"],
            "trust_mean": _cfg.traits["private"]["p_trust"]["mean"],
            "income_mean": _cfg.private["income"]["mean"],
            "subjective_audit_prob_mean": float(_cfg.traits["private"]["subjective_audit_prob"]["mean"]),
        },
        
        # Nested: Traits - Business
        "traits_business": {
            "personal_norms_mean": _cfg.traits["business"]["personal_norms"]["mean"],
            "social_norms_mean": _cfg.traits["business"]["social_norms"]["mean"],
            "societal_norms_mean": _cfg.traits["business"]["societal_norms"]["mean"],
            "pso_mean": _cfg.traits["business"]["pso"]["mean"],
            "trust_mean": _cfg.traits["business"]["p_trust"]["mean"],
            "subjective_audit_prob_mean": float(_cfg.traits["business"]["subjective_audit_prob"]["mean"]),
        },
        
        # Nested: SME Risk
        "sme_risk": {
            "base": _cfg.sme["base_risk_baseline"],
            "delta_sector": _cfg.sme["delta_sector_high_risk"],
            "delta_cash": _cfg.sme["delta_cash_intensive"],
            "delta_digi_high": _cfg.sme["delta_digi_high"],
            "delta_advisor": _cfg.sme["delta_advisor_yes"],
            "delta_audit": _cfg.sme["delta_audit_books"],
        },
    }


def get_non_default_chips(entry: dict, max_chips: int = 3) -> list[tuple[str, str, str]]:
    """
    Get chips for params that differ from defaults.
    Returns list of (text, text_color, bg_color) tuples.
    If all settings are default, returns agent count and strategy as fallback.
    """
    chips = []
    params = entry.get("params", {})
    defaults = get_default_values()
    
    # Check each param in priority order
    for param in PARAM_PRIORITY:
        if len(chips) >= max_chips:
            break
            
        # Get value from entry
        if param == "n_agents":
            val = entry.get("n_agents", params.get("n_agents"))
        elif param == "n_steps":
            val = entry.get("n_steps", params.get("n_steps"))
        else:
            val = params.get(param)
        
        if val is None:
            continue
            
        # Get default value
        default = defaults.get(param)
        
        # Compare - use tolerance for floats
        is_different = False
        if default is not None:
            if isinstance(val, float) and isinstance(default, float):
                is_different = abs(val - default) > 0.001
            else:
                is_different = val != default
        
        if is_different:
            formatter = CHIP_FORMATTERS.get(param)
            if formatter:
                text = formatter(val)
                if text:
                    colors = get_chip_style(param)
                    chips.append((text, colors[0], colors[1]))
    
    # Fallback: if no differences found, show agent count and strategy
    if not chips:
        n_agents = entry.get("n_agents", params.get("n_agents"))
        strategy = params.get("audit_strategy", "random")
        
        if n_agents:
            chips.append((f"{n_agents:,}", "#059669", "#05966920"))
        if strategy:
            chips.append((str(strategy).capitalize(), "#01689B", "#01689B20"))
    
    return chips


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
        
        /* Fix button padding - main.css uses way too much */
        /* Target buttons inside containers with borders (comparison page content) */
        [data-testid="stVerticalBlockBorderWrapper"] .stButton > button {
            padding: 6px 14px !important;
            min-width: auto !important;
            white-space: nowrap !important;
            font-size: 13px !important;
        }

        /* RESTORE BACK BUTTON STYLING */
        /* Placed AFTER the generic rule to ensure it wins on cascade */
        /* Use higher specificity: div.stElementContainer.st-key-back_home */
        div[data-testid="stElementContainer"].st-key-back_home .stButton > button {
            background: white !important;
            border: 1px solid #D1D9E0 !important;
            color: #4A5568 !important;
            padding: 8px 16px !important;
            border-radius: 8px !important;
            font-size: 14px !important;
            box-shadow: none !important;
            min-width: unset !important;
            height: auto !important;
        }

        div[data-testid="stElementContainer"].st-key-back_home .stButton > button:hover {
            border-color: #01689B !important;
            color: #01689B !important;
            background: #F8FAFC !important;
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
    """
    Find params that differ BETWEEN entries (not from defaults).
    Used for highlighting differences when comparing multiple runs.
    """
    if len(entries) < 2:
        return []
    
    # Collect all flattened params from all entries
    all_flat_params = [flatten_params(e.get("params", {})) for e in entries]
    
    # Get union of all keys
    all_keys = set()
    for flat in all_flat_params:
        all_keys.update(flat.keys())
    
    # Find keys that differ between entries
    differing = []
    for key in sorted(all_keys):
        values = [flat.get(key) for flat in all_flat_params]
        unique_vals = set(str(v) for v in values if v is not None)
        if len(unique_vals) > 1:
            differing.append(key)
    
    return differing


def find_non_default_params(entries: list[dict]) -> list[str]:
    """
    Find ALL params across entries that differ from the DEFAULT config.
    Returns list of param keys that are non-default in ANY of the entries.
    If a param doesn't exist in defaults, it's considered non-default.
    """
    if not entries:
        return []
    
    # Get default values
    defaults = get_default_values()
    defaults_flat = flatten_params(defaults) if defaults else {}
    
    # Collect all flattened params from all entries
    all_flat_params = [flatten_params(e.get("params", {})) for e in entries]
    
    # Get union of all keys
    all_keys = set()
    for flat in all_flat_params:
        all_keys.update(flat.keys())
    
    # Find keys that differ from defaults in ANY entry
    non_default = []
    for key in sorted(all_keys):
        default_val = defaults_flat.get(key)
        
        for flat in all_flat_params:
            val = flat.get(key)
            if val is None:
                continue
            
            # If no default exists for this key, it's non-default (new/custom param)
            if default_val is None:
                non_default.append(key)
                break
            
            # Compare with tolerance for floats
            is_different = False
            if isinstance(val, float) and isinstance(default_val, float):
                is_different = abs(val - default_val) > 0.001
            else:
                is_different = val != default_val
            
            if is_different:
                non_default.append(key)
                break  # Found at least one entry with non-default value
    
    return non_default


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
                date = format_date_iso(entry.get("date", "Unknown"))
                
                # Get chips for params that differ from defaults
                chips = get_non_default_chips(entry, max_chips=2)
                chips_html = render_chips_html(chips) if chips else ""
                
                color = "#01689B" if is_selected else "#718096"
                weight = "600" if is_selected else "400"
                
                st.markdown(
                    f'<div style="font-size:11px; color:{color}; font-weight:{weight}; '
                    f'line-height:1.8; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">'
                    f'{status}{date} {chips_html}'
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


def render_config_comparison(entries: list[dict], differing_params: list[str], non_default_params: list[str] = None):
    """Render configuration comparison table."""
    st.markdown("**Configuration Comparison**")
    
    if not entries:
        st.caption("Select runs to compare their configurations")
        return
    
    n_runs = len(entries)
    non_default_params = non_default_params or []
    
    # Pre-flatten all params for dynamic access
    all_flat_params = [flatten_params(e.get("params", {})) for e in entries]
    
    # Header row - add left padding to match the 12px padding inside the container below
    st.markdown('<div style="padding-left: 12px;">', unsafe_allow_html=True)
    header_cols = st.columns([1.5] + [1] * n_runs)
    with header_cols[0]:
        st.markdown('<div style="font-size:11px; color:#718096; padding:4px 0;">PARAMETER</div>', unsafe_allow_html=True)
    
    for i, entry in enumerate(entries):
        with header_cols[i + 1]:
            run_color = RUN_COLORS[i % len(RUN_COLORS)]
            run_label = f"Run {i + 1}"
            date = format_date_iso(entry.get("date", "Unknown"))
            st.markdown(
                f'<div style="text-align:center; padding:4px 0;">'
                f'<div style="font-size:12px; font-weight:600; color:{run_color};">{run_label}</div>'
                f'<div style="font-size:9px; color:#718096;">{date}</div></div>',
                unsafe_allow_html=True
            )
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div style="border-bottom:1px solid #D1D9E0; margin:4px 0;"></div>', unsafe_allow_html=True)
    
    # Helper to render a param row (works with both essential and dynamic params)
    def render_param_row(param_key, param_label, formatter, is_differing, use_flat=False):
        row_cols = st.columns([1.5] + [1] * n_runs)
        
        with row_cols[0]:
            if is_differing:
                st.markdown(f'<div style="font-size:11px; font-weight:700; color:#1A1A1A; padding:4px 0;">{param_label}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div style="font-size:11px; color:#718096; padding:4px 0;">{param_label}</div>', unsafe_allow_html=True)
        
        for i, entry in enumerate(entries):
            with row_cols[i + 1]:
                if use_flat:
                    # Use flattened params for dynamic keys
                    val = all_flat_params[i].get(param_key)
                else:
                    # Use original logic for essential params
                    params = entry.get("params", {})
                    if param_key == "n_agents":
                        val = entry.get("n_agents", params.get("n_agents"))
                    elif param_key == "n_steps":
                        val = entry.get("n_steps", params.get("n_steps"))
                    else:
                        val = params.get(param_key)
                
                formatted = formatter(val) if callable(formatter) else format_param_value(param_key, val)
                
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
    
    # Get non-default params that are NOT essential
    non_default_non_essential = [k for k in non_default_params if k not in ESSENTIAL_KEYS]
    
    # Split into: differing (between runs) and just non-default
    differing_non_essential = [k for k in non_default_non_essential if k in differing_params]
    non_differing_non_default = [k for k in non_default_non_essential if k not in differing_params]
    
    # Scrollable config rows - matches run list height
    with st.container(height=420):
        # Render essential params
        for param_key, param_label, formatter in ESSENTIAL_PARAMS:
            is_differing = param_key in differing_params
            render_param_row(param_key, param_label, formatter, is_differing, use_flat=False)
        
        # Separator if there are non-default params to show
        if non_default_non_essential:
            st.markdown('<div style="border-top:1px dashed #D1D9E0; margin:8px 0; padding-top:4px;">'
                       '<span style="font-size:9px; color:#A0AEC0; text-transform:uppercase;">Non-Default Parameters</span></div>', 
                       unsafe_allow_html=True)
            
            # First: render differing non-essential params (highlighted)
            for param_key in differing_non_essential:
                param_label = format_param_label(param_key)
                render_param_row(param_key, param_label, None, is_differing=True, use_flat=True)
            
            # Then: render non-differing non-default params (not highlighted)
            for param_key in non_differing_non_default:
                param_label = format_param_label(param_key)
                render_param_row(param_key, param_label, None, is_differing=False, use_flat=True)


def render_metrics_comparison(entries: list[dict], differing_params: list[str]):
    """Render performance metrics cards."""
    st.markdown("#### Performance Results")

    if len(entries) < 2:
        st.info("Select at least 2 runs")
        return

    metric_defs = [
        ("total_taxes", "Total Taxes", lambda v: f"€{v/1e6:.1f}M" if v and v >= 1e6 else (f"€{v/1e3:.1f}K" if v and v >= 1e3 else f"€{v:.0f}" if v else "—"), "higher", "Average sum of Total Taxes collected over the full duration, averaged across runs."),
        ("total_tax_gap", "Tax Gap", lambda v: f"€{v/1e6:.1f}M" if v and v >= 1e6 else (f"€{v/1e3:.1f}K" if v and v >= 1e3 else f"€{v:.0f}" if v else "—"), "lower", "Average sum of Tax Gap accumulated over the full duration, averaged across runs."),
        ("final_compliance", "Final Compliance", lambda v: f"{v*100:.1f}%" if v else "—", "higher", "The Compliance Rate at the very last step (averaged across runs)."),
        ("final_declaration_ratio", "Declaration Ratio", lambda v: f"{v*100:.1f}%" if v else "—", "higher", "The Avg Declaration Ratio at the very last step (averaged across runs)."),
        ("final_four", "Final FOUR", lambda v: f"{v*100:.1f}%" if v else "—", "lower", "The Avg FOUR at the very last step (averaged across runs)."),
        ("final_tax_morale", "Tax Morale", lambda v: f"{v:.1f}%" if v else "—", "higher", "The Tax Morale at the very last step (averaged across runs)."),
        ("final_mgtr", "Final MGTR", lambda v: f"{v*100:.1f}%" if v else "—", "higher", "The MGTR at the very last step (averaged across runs)."),
        ("total_penalties", "Correction Yield", lambda v: f"€{v/1e6:.1f}M" if v and v >= 1e6 else (f"€{v/1e3:.1f}K" if v and v >= 1e3 else f"€{v:.0f}" if v else "—"), "higher", "Sum of all penalties collected across all steps (averaged across runs)."),
    ]

    best_values = {}
    for key, _, _, direction, _ in metric_defs:
        vals = [e.get("results", {}).get(key, 0) for e in entries if e.get("results", {}).get(key, 0) > 0]
        if vals:
            best_values[key] = max(vals) if direction == "higher" else min(vals)

    cols = st.columns(len(entries))

    for i, entry in enumerate(entries):
        with cols[i]:
            run_color = RUN_COLORS[i % len(RUN_COLORS)]
            label = get_run_label(entry, run_index=i)
            chips = get_run_chips(entry, differing_params, max_chips=4)
            chips_html = render_chips_html(chips)

            st.markdown(f"""
                <div style="text-align:center; padding:8px; background:white; 
                            border:2px solid {run_color}; border-radius:8px; margin-bottom:10px;">
                    <div style="font-size:12px; font-weight:600; color:{run_color};">{label}</div>
                    <div style="margin-top:4px;">{chips_html}</div>
                </div>
            """, unsafe_allow_html=True)

            results = entry.get("results", {})
            for key, metric_label, formatter, _, help_text in metric_defs:
                val = results.get(key, 0)
                is_best = val > 0 and val == best_values.get(key)
                formatted = formatter(val) if val else "—"
                
                if is_best:
                    st.markdown(f"""
                        <div style="padding:6px 8px; margin-bottom:4px; background:rgba(5, 150, 105, 0.08); 
                                    border-radius:6px; border:1px solid rgba(5, 150, 105, 0.2); border-left:3px solid #059669;"
                                    title="{help_text}">
                            <div style="font-size:9px; color:#718096; text-transform:uppercase;">{metric_label}</div>
                            <div style="font-size:14px; font-weight:600; color:#059669;">{formatted}</div>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div style="padding:6px 8px; margin-bottom:4px; background:white; 
                                    border-radius:6px; border:1px solid #E8EEF2;"
                                    title="{help_text}">
                            <div style="font-size:9px; color:#718096; text-transform:uppercase;">{metric_label}</div>
                            <div style="font-size:14px; font-weight:500; color:#1A1A1A;">{formatted}</div>
                        </div>
                    """, unsafe_allow_html=True)


def render_chart(entries: list[dict], data_key: str, title: str, y_format: str = "auto", differing_params: list[str] = None, help_text: str = None):
    """Render a comparison line chart."""
    has_data = any(e.get("results", {}).get(data_key) for e in entries)
    
    with st.container(border=True):
        # st.markdown(f"**{title}**") # REMOVED: Moved into chart for better spacing control
        
        if not has_data:
            st.markdown(f"**{title}**", help=help_text)
            st.caption("No data available")
            return

        fig = go.Figure()
        for i, entry in enumerate(entries):
            data = entry.get("results", {}).get(data_key, [])
            if not data:
                continue
            color = RUN_COLORS[i % len(RUN_COLORS)]
            run_label = f"Run {i + 1}"
            short_label = get_short_label(entry, differing_params or [])
            legend_name = f"{run_label} ({short_label})"
            x_vals = [j / max(len(data) - 1, 1) * 100 for j in range(len(data))]
            fig.add_trace(go.Scatter(
                x=x_vals, y=data, mode="lines", name=legend_name,
                line=dict(color=color, width=2),
                hovertemplate=f"{run_label}: %{{y}}<extra></extra>",
            ))

        active_series_count = sum(1 for e in entries if e.get("results", {}).get(data_key))
        # Adaptive settings based on series count
        is_multiline_legend = active_series_count > 3
        
        # Adaptive margin calculations
        # Base margin for title (approx 30px) + legend (approx 20px) + spacing
        # If subtitle (help_text) is present, need extra space (approx 20px)
        base_top_margin = 90 if help_text else 65
        
        # If multiline legend, add extra space
        if is_multiline_legend:
            base_top_margin += 25
            
        margin_top = base_top_margin
        
        fig.update_layout(
            title=dict(
                text=title + (f"<br><span style='font-size:11px;color:#718096;font-weight:400'>{help_text}</span>" if help_text else ""),
                font=dict(size=14, color="#1A1A1A", family="Inter, sans-serif"),
                x=0.01, # Slight padding from left edge
                y=0.99, # Slightly below absolute top to prevent cut-off
                xanchor="left",
                yanchor="top",
                pad=dict(b=10, t=10, l=0)
            ),
            paper_bgcolor="white",
            plot_bgcolor="white",
            font=dict(color="#4A5568", family="Inter, sans-serif", size=11),
            height=320, # Increased height slightly to accommodate larger margins
            margin=dict(t=margin_top, b=30, l=10, r=10), # Adaptive top margin
            xaxis=dict(title="Progress (%)", gridcolor="#E8EEF2", linecolor="#D1D9E0", tickfont=dict(size=10), zeroline=False),
            yaxis=dict(gridcolor="#E8EEF2", linecolor="#D1D9E0", tickfont=dict(size=10), zeroline=False,
                       tickformat=".0%" if y_format == "percent" else None),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="center",
                x=0.5,
                # Use grid layout (entrywidth) only if >3 items to prevent gaps for few items
                **({"entrywidth": 0.32, "entrywidthmode": "fraction"} if is_multiline_legend else {}),
                font=dict(size=10),
                bgcolor="rgba(255,255,255,0)"
            ),
            showlegend=True,
            hovermode="x unified",
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
        header_col1, header_col2 = st.columns([3, 1])
        with header_col1:
            st.markdown('<div style="display:flex; align-items:baseline; gap:16px; margin-bottom:4px;">'
                        '<span style="font-size:28px; font-weight:700; color:#1A1A1A;">Compare Runs</span>'
                        '<span style="font-size:14px; color:#718096;">Side-by-side performance comparison</span></div>', 
                        unsafe_allow_html=True)
        with header_col2:
            from dashboard.utils.ui import render_download_button
            render_download_button()
            
        st.markdown('<div style="border-bottom:1px solid #D1D9E0; margin-bottom:28px;"></div>', unsafe_allow_html=True)

        # Load history and sort by date (most recent first)
        try:
            from utils.history import load_history
            from datetime import datetime
            
            history = load_history()
            
            # Sort by date descending (most recent first)
            def parse_date(entry):
                date_str = entry.get("date", "")
                # Try new format with seconds first
                try:
                    return datetime.strptime(date_str, "%b %d, %Y, %I:%M:%S %p")
                except:
                    pass
                # Try old format without seconds
                try:
                    return datetime.strptime(date_str, "%b %d, %Y, %I:%M %p")
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
        
        # Find params that differ between selected runs
        differing_params = find_differentiating_params(selected_entries)
        # Find params that differ from defaults (in any selected entry)
        non_default_params = find_non_default_params(selected_entries)

        # Main layout: Selection panel | Config comparison
        # Note: No height on outer containers - they size naturally
        col_select, col_config = st.columns([1, 2.5])

        with col_select:
            with st.container(border=True):
                render_selection_panel(history)

        with col_config:
            with st.container(border=True):
                render_config_comparison(selected_entries, differing_params, non_default_params)

        # Performance results section
        if len(selected_entries) >= 2:
            st.markdown("---")
            render_metrics_comparison(selected_entries, differing_params)

            st.markdown("---")
            st.markdown("#### Charts")

            col1, col2 = st.columns(2)
            with col1:
                render_chart(selected_entries, "taxes_over_time", "Tax Revenue Over Time", differing_params=differing_params, help_text="Total tax revenue collected at each simulation step.")
            with col2:
                render_chart(selected_entries, "compliance_over_time", "Compliance Rate", y_format="percent", differing_params=differing_params, help_text="Percentage of agents who are fully compliant (100% declaration) at each step.")

            col3, col4 = st.columns(2)
            with col3:
                render_chart(selected_entries, "tax_gap_over_time", "Tax Gap Over Time", differing_params=differing_params, help_text="Total uncollected tax revenue (evaded income × tax rate) at each step.")
            with col4:
                render_chart(selected_entries, "declaration_ratio_over_time", "Declaration Ratio", y_format="percent", differing_params=differing_params, help_text="Average ratio of (Declared Income / True Income) across all agents at each step.")


            col5, col6 = st.columns(2)
            with col5:
                render_chart(selected_entries, "four_over_time", "Fraud Opportunity Use Rate (FOUR)", y_format="percent", differing_params=differing_params, help_text="Average evasion rate among non-honest agents who had an opportunity to evade.")
            with col6:
                render_chart(selected_entries, "tax_morale_over_time", "Tax Morale Index", differing_params=differing_params, help_text="Average Tax Morale score (0-100%) across population, reflecting intrinsic willingness to comply.")


            col7, col8 = st.columns(2)
            with col7:
                render_chart(selected_entries, "mgtr_over_time", "Mean Gross Tax Rate (MGTR)", y_format="percent", differing_params=differing_params, help_text="Effective tax rate: (Total Revenue + Penalties) / Total True Income.")
            with col8:
                render_chart(selected_entries, "pso_over_time", "Service Experience (Avg PSO)", differing_params=differing_params, help_text="Average Perceived Service Orientation (PSO) towards the tax authority.")

        elif len(selected_entries) == 1:
            st.markdown("---")
            st.info("Select one more run to compare")
        else:
            st.markdown("---")
            st.info("Select 2+ runs to compare")
