"""
PricePulse – Best Deals page.

Ranks products by deal score (60 % discount weight + 40 % rating weight)
and presents them with visual deal cards (default) and interactive charts.
Clean typography, SVG vector icons, zero emojis.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# -- path setup --------------------------------------------------------------
_FRONTEND = Path(__file__).resolve().parent.parent
if str(_FRONTEND) not in sys.path:
    sys.path.insert(0, str(_FRONTEND))

from data_access import (
    ensure_db,
    get_all_products,
    get_deal_scores,
    get_top_deals,
)
from theme import (
    inject_css,
    render_theme_toggle,
    get_palette,
    page_header,
    style_plotly_fig,
    PRICEPULSE_COLORS,
)
from components.tables import display_product_table
from components.cards import metric_card, deal_card

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="PricePulse – Best Deals",
    page_icon="🏆",
    layout="wide",
)

render_theme_toggle()
inject_css()
palette = get_palette()
ensure_db()

# ---------------------------------------------------------------------------
# Header (SVG Icon)
# ---------------------------------------------------------------------------
page_header(
    title="Curated Best Value Deals",
    subtitle="Algorithmic scoring combining 60% discount depth with 40% customer review quality",
    icon_name="deal",
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
    st.info("No product listings available to calculate deal scores.")
    st.stop()

# ---------------------------------------------------------------------------
# Controls
# ---------------------------------------------------------------------------
col_limit, col_cat = st.columns([1, 2])

with col_limit:
    limit = st.slider("Deal limit to display", min_value=4, max_value=30, value=8, step=2, key="bd_limit")

with col_cat:
    categories = sorted(df["category"].dropna().unique().tolist())
    selected_cats = st.multiselect("Filter by Category", options=categories, key="bd_cats")

# Apply category filter
working_df = df.copy()
if selected_cats:
    working_df = working_df[working_df["category"].isin(selected_cats)]

if working_df.empty:
    st.info("No products match the selected category filters.")
    st.stop()

# ---------------------------------------------------------------------------
# Compute deal scores
# ---------------------------------------------------------------------------
scored_df = get_deal_scores(working_df)
top = get_top_deals(working_df, limit=limit)

# ---------------------------------------------------------------------------
# Summary metrics (SVG Icons)
# ---------------------------------------------------------------------------
avg_score = scored_df["deal_score"].mean() if "deal_score" in scored_df.columns else 0
max_score = scored_df["deal_score"].max() if "deal_score" in scored_df.columns else 0

c1, c2, c3 = st.columns(3)
with c1:
    metric_card(
        label="Analyzed Pool",
        value=str(len(scored_df)),
        subtitle="Eligible items scored",
        icon_name="dashboard",
    )
with c2:
    metric_card(
        label="Average Deal Score",
        value=f"{avg_score:.1f} / 100",
        subtitle="Catalog composite mean",
        icon_name="trends",
    )
with c3:
    metric_card(
        label="Top Score Achieved",
        value=f"{max_score:.1f} / 100",
        subtitle="Highest value ranking",
        icon_name="deal",
    )

st.divider()

# ---------------------------------------------------------------------------
# Best Deals Showcase (Visual Cards Grid vs Table)
# ---------------------------------------------------------------------------
st.markdown(f"### Top {len(top)} Ranked Best Deals")

view_tab_cards, view_tab_table = st.tabs(["Visual Deal Cards Grid", "Tabular View"])

with view_tab_cards:
    col_l, col_r = st.columns(2)
    for idx, (_, row) in enumerate(top.iterrows()):
        target = col_l if idx % 2 == 0 else col_r
        with target:
            deal_card(row, rank=idx + 1)

with view_tab_table:
    display_product_table(
        top,
        columns=["name", "category", "price", "original_price", "discount_percentage", "rating", "deal_score"],
        key="bd_table",
    )

st.divider()

# ---------------------------------------------------------------------------
# Charts Section
# ---------------------------------------------------------------------------
st.markdown("### Deal Score Analytics & Visual Breakdown")

if not top.empty:
    fig = px.bar(
        top,
        x=top["name"].str[:35] + "...",
        y="deal_score",
        color="deal_score",
        color_continuous_scale=["#A5B4FC", palette["accent"], "#06B6D4"],
        title=f"Top {len(top)} Ranked Deals (Deal Score Index)",
        labels={"x": "Product Listing", "deal_score": "Deal Score Index"},
    )
    style_plotly_fig(fig)
    fig.update_layout(xaxis_tickangle=-30)
    fig.update_traces(
        marker=dict(line=dict(color=palette["border"], width=1)),
        opacity=0.9,
    )
    st.plotly_chart(fig, use_container_width=True)

    # Score breakdown chart
    st.markdown("### Deal Score Composition Breakdown")
    st.caption("Deconstructed view showing the 60% discount weight vs. 40% rating weight contributions.")

    breakdown = top[["name", "discount_score", "rating_score"]].copy()
    breakdown["name"] = breakdown["name"].str[:35] + "..."
    breakdown = breakdown.melt(id_vars="name", var_name="Component", value_name="Score")
    breakdown["Component"] = breakdown["Component"].replace({
        "discount_score": "Discount Component (60%)",
        "rating_score": "Rating Component (40%)",
    })

    fig2 = px.bar(
        breakdown,
        x="name",
        y="Score",
        color="Component",
        barmode="stack",
        title="Weighted Deal Score Contributions",
        labels={"name": "Product"},
        color_discrete_map={
            "Discount Component (60%)": palette["accent"],
            "Rating Component (40%)": palette["success"],
        },
    )
    style_plotly_fig(fig2)
    fig2.update_layout(
        xaxis_tickangle=-30,
        legend_title_text="Weight Factor",
    )
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Not enough data to compute deal scores.")
