"""
theme.py – PricePulse theme engine & design system.

Features:
- Pure vector SVG iconography (zero AI emojis)
- Guaranteed 100% contrast in both Light & Dark modes
- Plotly chart titles, axes, and ticks high-contrast in dark mode
- Refined, pleasant button colors for Light Mode (clean Royal Blue) while preserving Dark Mode gradient
- Completely hidden Deploy button
- Modern executive sidebar UI with active indicators
"""

from __future__ import annotations

import streamlit as st
import plotly.graph_objects as go
from components.icons import get_icon

# ---------------------------------------------------------------------------
# Brand Color Sequences & Palettes
# ---------------------------------------------------------------------------

PRICEPULSE_COLORS = [
    "#6366F1",  # Electric Indigo
    "#06B6D4",  # Cyan Blue
    "#10B981",  # Emerald Green
    "#8B5CF6",  # Violet
    "#F59E0B",  # Amber
    "#EC4899",  # Pink
    "#3B82F6",  # Sky Blue
    "#14B8A6",  # Teal
]

LIGHT = {
    "theme_name": "light",
    "bg": "#F8FAFC",
    "surface": "#FFFFFF",
    "sidebar_bg": "#F1F5F9",
    "card_bg": "#FFFFFF",
    "card_border": "#E2E8F0",
    "card_shadow": "0 4px 20px -2px rgba(0, 0, 0, 0.05), 0 2px 6px -1px rgba(0, 0, 0, 0.03)",
    "card_hover_shadow": "0 16px 28px -6px rgba(37, 99, 235, 0.16)",
    "text": "#0F172A",             # Slate-900 (ultra high contrast)
    "text_secondary": "#334155",   # Slate-700 (crisp and readable)
    "text_muted": "#64748B",       # Slate-500
    "accent": "#2563EB",           # Royal Blue (pleasant and clean on light)
    "accent_secondary": "#0284C7",
    "accent_gradient": "linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%)",
    "accent_light": "rgba(37, 99, 235, 0.08)",
    "border": "#E2E8F0",
    "success": "#10B981",
    "warning": "#D97706",
    "error": "#DC2626",
    "header_bg": "#FFFFFF",
    "header_gradient": "linear-gradient(135deg, rgba(37, 99, 235, 0.07) 0%, rgba(2, 132, 199, 0.03) 100%)",
    "header_border": "#CBD5E1",
    "plotly_template": "plotly_white",
    "plotly_bg": "rgba(0,0,0,0)",
    "plotly_paper": "rgba(0,0,0,0)",
    "plotly_grid": "#E2E8F0",
    "plotly_font_color": "#0F172A",
    # Pleasant button styling for Light Mode (clean royal blue)
    "button_bg": "linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%)",
    "button_hover_bg": "linear-gradient(135deg, #1D4ED8 0%, #1E40AF 100%)",
    "button_color": "#FFFFFF",
    "button_shadow": "0 4px 14px rgba(37, 99, 235, 0.28)",
    "button_hover_shadow": "0 6px 20px rgba(37, 99, 235, 0.38)",
}

DARK = {
    "theme_name": "dark",
    "bg": "#080B11",
    "surface": "#0F172A",
    "sidebar_bg": "#06080E",
    "card_bg": "#0F172A",
    "card_border": "rgba(255, 255, 255, 0.09)",
    "card_shadow": "0 10px 30px -5px rgba(0, 0, 0, 0.55)",
    "card_hover_shadow": "0 20px 35px -5px rgba(99, 102, 241, 0.28)",
    "text": "#F8FAFC",             # Crisp white
    "text_secondary": "#CBD5E1",   # Light silver-slate (crisp and visible)
    "text_muted": "#94A3B8",       # Medium light slate
    "accent": "#6366F1",
    "accent_secondary": "#06B6D4",
    "accent_gradient": "linear-gradient(135deg, #6366F1 0%, #06B6D4 100%)",
    "accent_light": "rgba(99, 102, 241, 0.16)",
    "border": "#1E293B",
    "success": "#34D399",
    "warning": "#FBBF24",
    "error": "#F87171",
    "header_bg": "#0F172A",
    "header_gradient": "linear-gradient(135deg, rgba(99, 102, 241, 0.16) 0%, rgba(6, 182, 212, 0.08) 100%)",
    "header_border": "rgba(99, 102, 241, 0.35)",
    "plotly_template": "plotly_dark",
    "plotly_bg": "rgba(0,0,0,0)",
    "plotly_paper": "rgba(0,0,0,0)",
    "plotly_grid": "#1E293B",
    "plotly_font_color": "#F8FAFC",
    # Preserved electric gradient for Dark Mode
    "button_bg": "linear-gradient(135deg, #6366F1 0%, #06B6D4 100%)",
    "button_hover_bg": "linear-gradient(135deg, #4F46E5 0%, #0891B2 100%)",
    "button_color": "#FFFFFF",
    "button_shadow": "0 4px 14px rgba(99, 102, 241, 0.25)",
    "button_hover_shadow": "0 6px 20px rgba(6, 182, 212, 0.45)",
}


def _init_theme() -> None:
    """Initialise session-state theme on first visit."""
    if "theme" not in st.session_state:
        st.session_state["theme"] = "dark"


def get_palette() -> dict[str, str]:
    """Return the active colour palette dict."""
    _init_theme()
    return DARK if st.session_state["theme"] == "dark" else LIGHT


def render_html(html_str: str) -> None:
    """
    Renders HTML cleanly in Streamlit with zero risk of markdown code block parsing.
    Strips all line breaks and indentation so CommonMark never triggers code-block formatting.
    """
    clean_html = " ".join(line.strip() for line in html_str.splitlines() if line.strip())
    st.markdown(clean_html, unsafe_allow_html=True)


def render_theme_toggle() -> None:
    """
    Render a clean, professional theme toggle in the sidebar with SVG icons.
    """
    _init_theme()
    is_dark: bool = st.session_state["theme"] == "dark"
    label = "Switch to Light Mode" if is_dark else "Switch to Dark Mode"
    if st.sidebar.button(label, key="theme_toggle", use_container_width=True):
        st.session_state["theme"] = "light" if is_dark else "dark"
        st.rerun()


def page_header(title: str, subtitle: str, icon_name: str = "dashboard") -> None:
    """
    Render a reliable, high-contrast page header banner with SVG vector icons and sharp typography.
    """
    p = get_palette()
    icon_svg = get_icon(icon_name, size=24, color="#FFFFFF", stroke_width=2.2)
    icon_html = f'<div style="width:48px; height:48px; border-radius:12px; background:{p["accent_gradient"]}; display:flex; align-items:center; justify-content:center; color:#FFFFFF; flex-shrink:0; box-shadow:0 4px 14px {p["accent_light"]};">{icon_svg}</div>'
    
    html = f"""
<div class="pp-page-header">
    <div style="display:flex; align-items:center; gap:16px;">
        {icon_html}
        <div>
            <h1 class="pp-page-title">{title}</h1>
            <p class="pp-page-subtitle">{subtitle}</p>
        </div>
    </div>
</div>
"""
    render_html(html)


def style_plotly_fig(fig: go.Figure) -> go.Figure:
    """
    Apply PricePulse theme styling, fonts, and clean padding to any Plotly figure.
    Guarantees that chart titles, axes, and legends are crisp and clearly visible in dark mode.
    """
    p = get_palette()
    fig.update_layout(
        template=p["plotly_template"],
        paper_bgcolor=p["plotly_paper"],
        plot_bgcolor=p["plotly_bg"],
        font=dict(family="Inter, system-ui, sans-serif", color=p["plotly_font_color"], size=12),
        font_color=p["plotly_font_color"],
        title_font=dict(family="Inter, system-ui, sans-serif", color=p["plotly_font_color"], size=16),
        title_font_color=p["plotly_font_color"],
        legend=dict(
            font=dict(color=p["plotly_font_color"], size=11),
            title=dict(font=dict(color=p["plotly_font_color"])),
        ),
        margin=dict(l=40, r=40, t=55, b=40),
        hoverlabel=dict(
            bgcolor=p["card_bg"],
            font_size=12,
            font_family="Inter, sans-serif",
            bordercolor=p["border"],
            font_color=p["text"],
        ),
        colorway=PRICEPULSE_COLORS,
    )
    fig.update_xaxes(
        gridcolor=p["plotly_grid"],
        zerolinecolor=p["plotly_grid"],
        showline=True,
        linecolor=p["border"],
        title_font=dict(color=p["plotly_font_color"], size=12),
        tickfont=dict(color=p["plotly_font_color"], size=11),
    )
    fig.update_yaxes(
        gridcolor=p["plotly_grid"],
        zerolinecolor=p["plotly_grid"],
        showline=True,
        linecolor=p["border"],
        title_font=dict(color=p["plotly_font_color"], size=12),
        tickfont=dict(color=p["plotly_font_color"], size=11),
    )
    return fig


def inject_css() -> None:
    """Inject full-page CSS that ensures high contrast in both Light & Dark modes."""
    p = get_palette()
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    }}

    /* Global backgrounds */
    .stApp, [data-testid="stAppViewContainer"] {{
        background-color: {p['bg']} !important;
        color: {p['text']} !important;
    }}
    header[data-testid="stHeader"] {{
        background-color: transparent !important;
    }}

    .main .block-container {{
        padding-top: 1.6rem !important;
        padding-bottom: 3rem !important;
        max-width: 1220px !important;
    }}

    /* ---------------------------------------------------- */
    /* HIDE DEPLOY BUTTON COMPLETELY                        */
    /* ---------------------------------------------------- */
    .stDeployButton,
    [data-testid="stDeployButton"],
    [data-testid="stAppDeployButton"],
    button[data-testid="stAppDeployButton"],
    div[data-testid="stHeader"] .stDeployButton,
    div[data-testid="stHeader"] [data-testid="stAppDeployButton"],
    div[data-testid="stToolbar"] .stDeployButton,
    div[data-testid="stToolbar"] [data-testid="stAppDeployButton"],
    header [data-testid="stAppDeployButton"] {{
        display: none !important;
        visibility: hidden !important;
        opacity: 0 !important;
        width: 0 !important;
        height: 0 !important;
        pointer-events: none !important;
    }}

    /* ---------------------------------------------------- */
    /* GUARANTEED HIGH CONTRAST TYPOGRAPHY IN LIGHT & DARK  */
    /* ---------------------------------------------------- */
    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3,
    [data-testid="stMarkdownContainer"] h4,
    [data-testid="stMarkdownContainer"] strong,
    [data-testid="stVerticalBlockBorderWrapper"] h1,
    [data-testid="stVerticalBlockBorderWrapper"] h2,
    [data-testid="stVerticalBlockBorderWrapper"] h3,
    [data-testid="stVerticalBlockBorderWrapper"] h4 {{
        color: {p['text']} !important;
        font-weight: 700;
        letter-spacing: -0.015em;
    }}

    .stApp p, [data-testid="stMarkdownContainer"] p,
    [data-testid="stVerticalBlockBorderWrapper"] p,
    [data-testid="stVerticalBlockBorderWrapper"] div,
    [data-testid="stVerticalBlockBorderWrapper"] span {{
        color: {p['text']};
    }}

    /* Subtitles, Captions & Secondary copy */
    .pp-page-subtitle, .pp-subtitle, .stCaption, [data-testid="stCaptionContainer"],
    [data-testid="stCaptionContainer"] p, [data-testid="stCaptionContainer"] span {{
        color: {p['text_secondary']} !important;
        font-size: 0.88rem !important;
    }}

    /* ---------------------------------------------------- */
    /* SIDEBAR UI                                           */
    /* ---------------------------------------------------- */
    section[data-testid="stSidebar"] {{
        background-color: {p['sidebar_bg']} !important;
        border-right: 1px solid {p['border']} !important;
        box-shadow: 2px 0 16px rgba(0, 0, 0, 0.04) !important;
    }}

    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] {{
        padding-top: 8px !important;
    }}

    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] ul {{
        gap: 4px;
        padding: 0 4px;
    }}
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] li a {{
        border-radius: 10px !important;
        padding: 8px 14px !important;
        color: {p['text_secondary']} !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        transition: all 0.2s ease !important;
    }}
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] li a:hover {{
        background-color: {p['accent_light']} !important;
        color: {p['accent']} !important;
    }}
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] li a[aria-current="page"] {{
        background: {p['accent_light']} !important;
        color: {p['accent']} !important;
        border-left: 3px solid {p['accent']} !important;
        font-weight: 700 !important;
    }}

    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {{
        color: {p['text']} !important;
    }}

    /* ---------------------------------------------------- */
    /* PAGE HEADER BANNER                                   */
    /* ---------------------------------------------------- */
    .pp-page-header {{
        background: {p['header_gradient']};
        border: 1px solid {p['header_border']};
        border-radius: 16px;
        padding: 22px 26px;
        margin-bottom: 22px;
        box-shadow: {p['card_shadow']};
    }}
    .pp-page-title {{
        margin: 0 !important;
        font-size: 1.85rem !important;
        font-weight: 800 !important;
        color: {p['text']} !important;
        letter-spacing: -0.02em;
    }}
    .pp-page-subtitle {{
        margin: 4px 0 0 0 !important;
        font-size: 0.92rem !important;
        color: {p['text_secondary']} !important;
        font-weight: 400;
    }}

    /* ---------------------------------------------------- */
    /* ALL ACTION BUTTONS (ADAPTIVE LIGHT & DARK)           */
    /* ---------------------------------------------------- */
    .stButton > button,
    .stButton > button[kind="primary"],
    .stButton > button[kind="secondary"] {{
        background: {p['button_bg']} !important;
        color: {p['button_color']} !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        padding: 9px 20px !important;
        transition: all 0.22s cubic-bezier(0.16, 1, 0.3, 1) !important;
        box-shadow: {p['button_shadow']} !important;
    }}
    .stButton > button *,
    .stButton > button p,
    .stButton > button span {{
        color: {p['button_color']} !important;
    }}
    .stButton > button:hover,
    .stButton > button[kind="primary"]:hover {{
        background: {p['button_hover_bg']} !important;
        transform: translateY(-2px) !important;
        box-shadow: {p['button_hover_shadow']} !important;
        color: {p['button_color']} !important;
    }}

    /* Sidebar theme toggle button */
    section[data-testid="stSidebar"] .stButton > button {{
        background: {p['card_bg']} !important;
        color: {p['text']} !important;
        border: 1px solid {p['border']} !important;
        box-shadow: {p['card_shadow']} !important;
        font-size: 0.85rem !important;
    }}
    section[data-testid="stSidebar"] .stButton > button *,
    section[data-testid="stSidebar"] .stButton > button p,
    section[data-testid="stSidebar"] .stButton > button span {{
        color: {p['text']} !important;
    }}
    section[data-testid="stSidebar"] .stButton > button:hover {{
        border-color: {p['accent']} !important;
        color: {p['accent']} !important;
    }}

    /* ---------------------------------------------------- */
    /* CONTAINERS & CARDS                                   */
    /* ---------------------------------------------------- */
    [data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: {p['card_bg']} !important;
        border: 1px solid {p['card_border']} !important;
        border-radius: 14px !important;
        box-shadow: {p['card_shadow']} !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    [data-testid="stVerticalBlockBorderWrapper"]:hover {{
        transform: translateY(-3px);
        box-shadow: {p['card_hover_shadow']} !important;
    }}

    /* Modern Pill Search Bar */
    .stTextInput > div > div > input {{
        background-color: {p['card_bg']} !important;
        color: {p['text']} !important;
        border: 1.5px solid {p['border']} !important;
        border-radius: 30px !important;
        padding: 10px 22px !important;
        font-size: 0.95rem !important;
        transition: all 0.2s ease !important;
        box-shadow: {p['card_shadow']} !important;
    }}
    .stTextInput > div > div > input:focus {{
        border-color: {p['accent']} !important;
        box-shadow: 0 0 0 4px {p['accent_light']} !important;
    }}

    /* Selectboxes & other inputs */
    .stSelectbox > div > div,
    .stMultiSelect > div > div {{
        background-color: {p['card_bg']} !important;
        color: {p['text']} !important;
        border: 1px solid {p['border']} !important;
        border-radius: 10px !important;
    }}

    /* Metric cards */
    [data-testid="stMetric"] {{
        background-color: {p['card_bg']} !important;
        border: 1px solid {p['border']} !important;
        border-radius: 14px !important;
        padding: 16px 20px !important;
        box-shadow: {p['card_shadow']} !important;
    }}
    [data-testid="stMetricValue"] {{
        color: {p['accent']} !important;
        font-weight: 800 !important;
    }}
    [data-testid="stMetricLabel"] {{
        color: {p['text_secondary']} !important;
        font-weight: 600 !important;
    }}

    /* Custom Cards */
    .pp-card {{
        background: {p['card_bg']};
        border: 1px solid {p['card_border']};
        border-left: 4px solid {p['accent']};
        border-radius: 14px;
        padding: 18px 20px;
        margin-bottom: 14px;
        box-shadow: {p['card_shadow']};
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    .pp-card:hover {{
        transform: translateY(-3px);
        box-shadow: {p['card_hover_shadow']};
    }}
    .pp-card h4 {{
        margin: 0 0 6px 0;
        font-size: 0.82rem;
        color: {p['text_secondary']} !important;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    .pp-card .pp-value {{
        font-size: 1.8rem;
        font-weight: 800;
        color: {p['text']} !important;
        margin: 0;
    }}
    .pp-card .pp-subtitle {{
        font-size: 0.8rem;
        color: {p['text_secondary']} !important;
        margin: 4px 0 0 0;
    }}

    /* Visual Product & Deal Cards */
    .pp-deal-card {{
        background: {p['card_bg']};
        border: 1px solid {p['card_border']};
        border-radius: 14px;
        padding: 18px;
        margin-bottom: 14px;
        box-shadow: {p['card_shadow']};
        transition: all 0.25s ease;
    }}
    .pp-deal-card:hover {{
        transform: translateY(-4px);
        box-shadow: {p['card_hover_shadow']};
        border-color: {p['accent']};
    }}

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] button {{
        color: {p['text_secondary']} !important;
        font-weight: 600 !important;
    }}
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {{
        color: {p['accent']} !important;
        border-bottom: 3px solid {p['accent']} !important;
        font-weight: 800 !important;
    }}

    /* Dataframe styling */
    .stDataFrame, [data-testid="stDataFrame"] {{
        border: 1px solid {p['border']} !important;
        border-radius: 12px !important;
        box-shadow: {p['card_shadow']} !important;
    }}

    hr {{
        border-color: {p['border']} !important;
        margin: 20px 0 !important;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
