"""
PricePulse – Charts page.

Plotly re-implementations of the backend's visualization charts:
price comparison, discount comparison, rating vs price scatter,
and sale price vs MRP overlay.
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

from data_access import ensure_db, get_all_products
from theme import (
    inject_css,
    render_theme_toggle,
    get_palette,
    page_header,
    style_plotly_fig,
    PRICEPULSE_COLORS,
)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="PricePulse – Visual Analytics",
    page_icon="📊",
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
    title="Visual Analytics & Graphical Suite",
    subtitle="Interactive benchmarks, price comparisons, rating correlations, and MRP spread analysis",
    icon_name="charts",
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
    st.info("No product listings available in the database.")
    st.stop()

# Remove rows without price
chart_df = df.dropna(subset=["price"]).copy()

if chart_df.empty:
    st.info("No products with recorded pricing data found.")
    st.stop()

# ---------------------------------------------------------------------------
# Chart 1: Price Comparison (top 10 cheapest)
# ---------------------------------------------------------------------------
st.markdown("### Price Comparison (Lowest Price Leaders)")
st.caption("Top 10 most budget-friendly products currently tracked.")

price_top = chart_df.sort_values("price", ascending=True).head(10).copy()
price_top["short_name"] = price_top["name"].str[:35] + "..."

fig1 = px.bar(
    price_top,
    y="short_name",
    x="price",
    orientation="h",
    title="Top 10 Most Affordable Items (₹)",
    labels={"short_name": "Product Listing", "price": "Price (₹)"},
    color="price",
    color_continuous_scale=["#10B981", palette["accent"], "#6366F1"],
)
style_plotly_fig(fig1)
fig1.update_layout(
    yaxis=dict(autorange="reversed"),
    height=440,
)
fig1.update_traces(
    marker=dict(line=dict(color=palette["border"], width=1)),
    opacity=0.9,
)
st.plotly_chart(fig1, use_container_width=True)

st.divider()

# ---------------------------------------------------------------------------
# Chart 2: Discount Comparison (top 10 highest discount)
# ---------------------------------------------------------------------------
st.markdown("### Top Discount Depth Comparison")
st.caption("Top 10 listings offering the highest percentage markdown.")

disc_df = chart_df.dropna(subset=["discount_percentage"]).copy()

if not disc_df.empty:
    disc_top = disc_df.sort_values("discount_percentage", ascending=False).head(10).copy()
    disc_top["short_name"] = disc_top["name"].str[:35] + "..."

    fig2 = px.bar(
        disc_top,
        y="short_name",
        x="discount_percentage",
        orientation="h",
        title="Top 10 Highest Discount Percentages (%)",
        labels={"short_name": "Product Listing", "discount_percentage": "Discount (%)"},
        color="discount_percentage",
        color_continuous_scale=["#A5B4FC", palette["accent"], "#06B6D4"],
    )
    style_plotly_fig(fig2)
    fig2.update_layout(
        yaxis=dict(autorange="reversed"),
        height=440,
    )
    fig2.update_traces(
        marker=dict(line=dict(color=palette["border"], width=1)),
        opacity=0.9,
    )
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("No discount data available for this chart.")

st.divider()

# ---------------------------------------------------------------------------
# Chart 3: Rating vs Price scatter
# ---------------------------------------------------------------------------
st.markdown("### Customer Rating vs Price Correlation")
st.caption("Examine whether higher prices correlate with customer satisfaction across categories.")

scatter_df = chart_df.dropna(subset=["price", "rating"]).copy()

if not scatter_df.empty:
    has_category = scatter_df["category"].notna().any()
    color_col = "category" if has_category else None

    fig3 = px.scatter(
        scatter_df,
        x="price",
        y="rating",
        color=color_col,
        hover_name=scatter_df["name"].str[:60],
        title="Product Rating vs Sale Price (₹)",
        labels={"price": "Sale Price (₹)", "rating": "Rating (out of 5)"},
        color_discrete_sequence=PRICEPULSE_COLORS,
        size_max=12,
    )
    style_plotly_fig(fig3)
    fig3.update_traces(
        marker=dict(size=12, opacity=0.88, line=dict(width=1, color=palette["border"]))
    )
    fig3.update_layout(height=480)
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("Not enough rating and price data to plot correlation.")

st.divider()

# ---------------------------------------------------------------------------
# Chart 4: Price vs Original Price comparison
# ---------------------------------------------------------------------------
st.markdown("### Sale Price vs. List Price (MRP) Comparison")
st.caption("Direct visual spread comparing current checkout price against manufacturer list price.")

mrp_df = chart_df.dropna(subset=["price", "original_price"]).copy()

if not mrp_df.empty:
    mrp_top = mrp_df.sort_values("original_price", ascending=False).head(15).copy()
    mrp_top["short_name"] = mrp_top["name"].str[:32] + "..."

    fig4 = go.Figure()
    fig4.add_trace(go.Bar(
        y=mrp_top["short_name"],
        x=mrp_top["original_price"],
        name="List Price (MRP)",
        orientation="h",
        marker_color=palette["text_muted"],
        opacity=0.4,
    ))
    fig4.add_trace(go.Bar(
        y=mrp_top["short_name"],
        x=mrp_top["price"],
        name="Sale Price",
        orientation="h",
        marker_color=palette["accent"],
    ))
    fig4.update_layout(
        title="Sale Price vs List MRP Spread",
        barmode="overlay",
        yaxis=dict(autorange="reversed"),
        height=520,
        legend=dict(orientation="h", y=-0.15),
    )
    style_plotly_fig(fig4)
    st.plotly_chart(fig4, use_container_width=True)
else:
    st.info("No listings have both sale price and list MRP recorded.")
