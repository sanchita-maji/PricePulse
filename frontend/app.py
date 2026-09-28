"""
PricePulse – Main entry point (app.py).

Run with:  streamlit run frontend/app.py
Electric Indigo & Cyan high-tech theme with SVG vector icons (no emojis).
All 6 module buttons use the primary blue gradient.
"""

from __future__ import annotations

import sys
from pathlib import Path
import streamlit as st

# -- path setup so sibling imports work --------------------------------------
_FRONTEND = Path(__file__).resolve().parent
if str(_FRONTEND) not in sys.path:
    sys.path.insert(0, str(_FRONTEND))

from data_access import ensure_db, get_all_products, get_summary
from theme import inject_css, render_theme_toggle, get_palette, render_html
from components.cards import metric_card
from components.icons import get_icon

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="PricePulse – Amazon Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Theme toggle + CSS injection
render_theme_toggle()
inject_css()
palette = get_palette()

# Ensure database tables exist
ensure_db()

# ---------------------------------------------------------------------------
# Sidebar branding
# ---------------------------------------------------------------------------
with st.sidebar:
    pulse_svg = get_icon("pulse", size=24, color="#FFFFFF", stroke_width=2.5)
    brand_html = f"""
<div style="padding: 12px 6px 18px 6px; text-align: center;">
    <div style="display: inline-flex; align-items: center; justify-content: center; width: 44px; height: 44px; border-radius: 12px; background: {palette['accent_gradient']}; color: white; margin-bottom: 10px; box-shadow: 0 4px 14px {palette['accent_light']};">
        {pulse_svg}
    </div>
    <h1 style="margin: 0; font-size: 1.55rem; font-weight: 800; color: {palette['text']}; letter-spacing: -0.02em;">
        PricePulse
    </h1>
    <p style="margin: 4px 0 0 0; font-size: 0.8rem; color: {palette['text_secondary']}; font-weight: 500;">
        Amazon Price & Discount Intelligence
    </p>
</div>
"""
    render_html(brand_html)
    st.divider()
    st.caption("EXPLORE MODULES")

# ---------------------------------------------------------------------------
# Hero Banner
# ---------------------------------------------------------------------------
hero_html = f"""
<div style="background: {palette['header_gradient']}; border: 1px solid {palette['header_border']}; border-radius: 20px; padding: 42px 32px; text-align: center; margin-bottom: 26px; box-shadow: {palette['card_shadow']};">
    <div style="display: inline-block; background: {palette['accent_light']}; color: {palette['accent']}; font-size: 0.78rem; font-weight: 800; padding: 4px 14px; border-radius: 20px; letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 12px; border: 1px solid {palette['header_border']};">
        Amazon Market Intelligence
    </div>
    <h1 style="font-size: 2.9rem; font-weight: 800; margin: 0; letter-spacing: -0.025em; color: {palette['text']}; line-height: 1.2;">
        PricePulse
    </h1>
    <p style="font-size: 1.15rem; color: {palette['text_secondary']}; max-width: 660px; margin: 10px auto 0 auto; line-height: 1.5;">
        Track historical price drops, benchmark discounts, and find optimal buying opportunities across Amazon.
    </p>
</div>
"""
render_html(hero_html)

# ---------------------------------------------------------------------------
# Live Quick Stats Strip
# ---------------------------------------------------------------------------
try:
    df_preview = get_all_products()
    if not df_preview.empty:
        summary_preview = get_summary(df_preview)
        total_p = summary_preview.get("total_products", len(df_preview))
        avg_price = summary_preview.get("average_price", 0.0)
        avg_disc = summary_preview.get("average_discount", 0.0)
        num_categories = df_preview["category"].nunique() if "category" in df_preview.columns else 0

        q1, q2, q3, q4 = st.columns(4)
        with q1:
            metric_card(
                label="Tracked Products",
                value=str(total_p),
                subtitle="Active catalog items",
                icon_name="products",
            )
        with q2:
            metric_card(
                label="Average Discount",
                value=f"{avg_disc:.1f}%",
                subtitle="Catalog mean markdown",
                icon_name="discount",
            )
        with q3:
            metric_card(
                label="Average Price",
                value=f"₹{avg_price:,.0f}",
                subtitle="Mean checkout cost",
                icon_name="price",
            )
        with q4:
            metric_card(
                label="Categories",
                value=str(num_categories),
                subtitle="Diverse segments tracked",
                icon_name="category",
            )
except Exception:
    pass

st.write("")

# ---------------------------------------------------------------------------
# Interactive Modules (All 6 buttons with primary blue gradient)
# ---------------------------------------------------------------------------
st.markdown("### Interactive Modules")
st.caption("Click any module card below to jump directly to that page:")

r1_c1, r1_c2, r1_c3 = st.columns(3)

with r1_c1:
    with st.container(border=True):
        st.markdown(f"#### {get_icon('dashboard', size=18, color=palette['accent'])} &nbsp; Executive Dashboard", unsafe_allow_html=True)
        st.write("Consolidated overview of summary statistics, spotlight deals, and category distributions.")
        if st.button("Open Dashboard ➜", key="btn_dash", use_container_width=True, type="primary"):
            st.switch_page("pages/1_Dashboard.py")

with r1_c2:
    with st.container(border=True):
        st.markdown(f"#### {get_icon('products', size=18, color=palette['accent'])} &nbsp; Product Catalog", unsafe_allow_html=True)
        st.write("Browse, filter, and inspect detailed metrics with card and table views across all items.")
        if st.button("Explore Products ➜", key="btn_prod", use_container_width=True, type="primary"):
            st.switch_page("pages/2_Products.py")

with r1_c3:
    with st.container(border=True):
        st.markdown(f"#### {get_icon('trends', size=18, color=palette['accent'])} &nbsp; Price Trends", unsafe_allow_html=True)
        st.write("Analyze multi-day price movements, all-time lows, highs, and volatility over time.")
        if st.button("Track Price Trends ➜", key="btn_trends", use_container_width=True, type="primary"):
            st.switch_page("pages/3_Price_Trends.py")

st.write("")
r2_c1, r2_c2, r2_c3 = st.columns(3)

with r2_c1:
    with st.container(border=True):
        st.markdown(f"#### {get_icon('discount', size=18, color=palette['accent'])} &nbsp; Discount Analytics", unsafe_allow_html=True)
        st.write("Examine markdown frequencies, category benchmarks, and cash savings timelines.")
        if st.button("View Discounts ➜", key="btn_disc", use_container_width=True, type="primary"):
            st.switch_page("pages/4_Discounts.py")

with r2_c2:
    with st.container(border=True):
        st.markdown(f"#### {get_icon('deal', size=18, color=palette['accent'])} &nbsp; Best Value Deals", unsafe_allow_html=True)
        st.write("Discover top-ranked bargains evaluated by our weighted Deal Score algorithm.")
        if st.button("Find Best Deals ➜", key="btn_deals", use_container_width=True, type="primary"):
            st.switch_page("pages/5_Best_Deals.py")

with r2_c3:
    with st.container(border=True):
        st.markdown(f"#### {get_icon('charts', size=18, color=palette['accent'])} &nbsp; Visual Analytics", unsafe_allow_html=True)
        st.write("Interact with price vs discount scatter plots, list MRP spreads, and graphical suites.")
        if st.button("Launch Charts ➜", key="btn_charts", use_container_width=True, type="primary"):
            st.switch_page("pages/6_Charts.py")

st.divider()

footer_html = f"""
<div style="text-align: center; padding: 8px 0 20px 0; color: {palette['text_secondary']}; font-size: 0.85rem;">
    <strong>PricePulse</strong> · Real-time Analytics Engine · Built with Python, Streamlit & Plotly
</div>
"""
render_html(footer_html)
