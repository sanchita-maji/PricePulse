"""
PricePulse – Dashboard page.

Shows summary metrics, visual best deal cards, lowest-price product,
and highest-discount product at a glance.
Professional SVG vector icons with zero emojis.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st
import plotly.express as px
import pandas as pd

# -- path setup so sibling imports work when Streamlit runs this page --------
_FRONTEND = Path(__file__).resolve().parent.parent
if str(_FRONTEND) not in sys.path:
    sys.path.insert(0, str(_FRONTEND))

from data_access import (
    ensure_db,
    get_all_products,
    get_summary,
    get_top_deals,
    get_cheapest,
    get_most_discounted,
)
from theme import (
    inject_css,
    render_theme_toggle,
    get_palette,
    page_header,
    style_plotly_fig,
    PRICEPULSE_COLORS,
    render_html,
)
from components.cards import metric_card, product_highlight_card, deal_card
from components.tables import display_product_table

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="PricePulse – Dashboard",
    page_icon="📊",
    layout="wide",
)

# Theme
render_theme_toggle()
inject_css()
palette = get_palette()
ensure_db()

# ---------------------------------------------------------------------------
# Header (Vector SVG icon)
# ---------------------------------------------------------------------------
page_header(
    title="Executive Dashboard",
    subtitle="Consolidated metrics, category volume distribution, and top deal opportunities across Amazon",
    icon_name="dashboard",
)

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
try:
    df = get_all_products()
except Exception as exc:
    st.error(f"Failed to load products: {exc}")
    st.stop()

if df.empty:
    st.info("No products found in the database. Ensure the catalog database is populated.")
    st.stop()

# ---------------------------------------------------------------------------
# Summary metrics row (Vector SVG icons)
# ---------------------------------------------------------------------------
summary = get_summary(df)

col1, col2, col3, col4 = st.columns(4)

with col1:
    metric_card(
        label="Total Products",
        value=str(summary["total_products"]),
        subtitle="Active catalog items",
        icon_name="products",
    )

with col2:
    metric_card(
        label="Average Price",
        value=f"₹{summary['average_price']:,.2f}",
        subtitle="Catalog mean checkout",
        icon_name="price",
    )

with col3:
    metric_card(
        label="Average Discount",
        value=f"{summary['average_discount']:.1f}%",
        subtitle="Across all items",
        icon_name="discount",
    )

with col4:
    metric_card(
        label="Average Rating",
        value=f"{summary['average_rating']:.1f} / 5",
        subtitle="Customer satisfaction",
        icon_name="star",
    )

st.divider()

# ---------------------------------------------------------------------------
# Highlights row – cheapest & most discounted
# ---------------------------------------------------------------------------
st.markdown("### Spotlight Deals")

h1, h2 = st.columns(2)

cheapest = get_cheapest(df)
most_disc = get_most_discounted(df)

with h1:
    if cheapest is not None:
        product_highlight_card(cheapest, title="Lowest Price In Catalog", icon_name="price", badge="BUDGET PICK")
    else:
        st.info("No price data available.")

with h2:
    if most_disc is not None:
        product_highlight_card(most_disc, title="Deepest Discount Found", icon_name="fire", badge="TOP SAVER")
    else:
        st.info("No discount data available.")

st.divider()

# ---------------------------------------------------------------------------
# Top 10 Best Deals – Visual Cards
# ---------------------------------------------------------------------------
st.markdown("### Top 10 Best Deals Showcase")
st.caption("Ranked by our weighted Deal Score algorithm (60% discount depth + 40% customer rating).")

top_deals = get_top_deals(df, limit=10)

if not top_deals.empty:
    deal_tab_cards, deal_tab_table = st.tabs(["Visual Deal Cards", "Detailed Data Table"])
    
    with deal_tab_cards:
        col_left, col_right = st.columns(2)
        for idx, (_, row) in enumerate(top_deals.iterrows()):
            target_col = col_left if idx % 2 == 0 else col_right
            with target_col:
                deal_card(row, rank=idx + 1)
                
    with deal_tab_table:
        display_product_table(
            top_deals,
            columns=["name", "category", "price", "original_price", "discount_percentage", "rating", "deal_score"],
            key="dashboard_deals",
        )
else:
    st.info("Not enough data to compute deal scores.")

st.divider()

# ---------------------------------------------------------------------------
# Quick charts
# ---------------------------------------------------------------------------
st.markdown("### Visual Market Breakdown")

c1, c2 = st.columns(2)

with c1:
    cat_counts = df["category"].dropna().value_counts().reset_index()
    cat_counts.columns = ["Category", "Count"]
    if not cat_counts.empty:
        fig = px.pie(
            cat_counts,
            names="Category",
            values="Count",
            title="Catalog Volume by Category",
            hole=0.55,
            color_discrete_sequence=PRICEPULSE_COLORS,
        )
        style_plotly_fig(fig)
        fig.update_traces(
            textposition="inside",
            textinfo="percent+label",
            marker=dict(line=dict(color=palette["card_bg"], width=2)),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No category data yet.")

with c2:
    discounts = df["discount_percentage"].dropna()
    if not discounts.empty:
        fig2 = px.histogram(
            discounts,
            nbins=15,
            title="Discount Frequency Distribution (%)",
            labels={"value": "Discount %", "count": "Products"},
            color_discrete_sequence=[palette["accent"]],
        )
        style_plotly_fig(fig2)
        fig2.update_layout(showlegend=False)
        fig2.update_traces(
            marker=dict(line=dict(color=palette["border"], width=1)),
            opacity=0.88,
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No discount data yet.")
