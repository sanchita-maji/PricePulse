"""
PricePulse – Price Trends page.

Interactive Plotly charts showing multi-point price trajectories over time
for individual products and catalog-wide benchmarks.
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
    get_price_history,
    get_all_price_history,
)
from theme import (
    inject_css,
    render_theme_toggle,
    get_palette,
    page_header,
    style_plotly_fig,
    PRICEPULSE_COLORS,
)
from components.tables import display_history_table
from components.cards import metric_card

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="PricePulse – Price Trends",
    page_icon="📈",
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
    title="Price Trends & Trajectory History",
    subtitle="Inspect multi-point historical pricing movements, list price variations, and category volatility over time",
    icon_name="trends",
)

# ---------------------------------------------------------------------------
# Load products for selector
# ---------------------------------------------------------------------------
try:
    products_df = get_all_products()
except Exception as exc:
    st.error(f"Failed to load products: {exc}")
    st.stop()

if products_df.empty:
    st.info("No product price history records available in the database.")
    st.stop()

# ---------------------------------------------------------------------------
# Tabs: single product vs all products overview
# ---------------------------------------------------------------------------
tab_single, tab_all = st.tabs(["Single Product Deep Dive", "Catalog-Wide Overview"])

# ---- Tab 1: Single Product ------------------------------------------------
with tab_single:
    name_id_map: dict[str, int] = {}
    for _, row in products_df.iterrows():
        pid = int(row["id"])
        name = str(row.get("name", f"Product {pid}"))
        label = f"#{pid} — {name[:75]}"
        name_id_map[label] = pid

    selected_label = st.selectbox(
        "Select Product to Analyze:",
        options=list(name_id_map.keys()),
        key="pt_product_sel",
    )

    if selected_label:
        product_id = name_id_map[selected_label]
        history = get_price_history(product_id)

        if history.empty:
            st.info("No price history recorded for this product yet.")
        else:
            history["recorded_at"] = pd.to_datetime(history["recorded_at"], errors="coerce")
            history = history.sort_values("recorded_at", ascending=True).reset_index(drop=True)

            curr_price = history["price"].iloc[-1]
            min_price = history["price"].min()
            max_price = history["price"].max()

            # Stat cards row (SVG icons)
            m1, m2, m3, m4 = st.columns(4)
            with m1:
                metric_card("Current Checkout", f"₹{curr_price:,.2f}", subtitle="Latest recorded price", icon_name="price")
            with m2:
                metric_card("7-Day Low", f"₹{min_price:,.2f}", subtitle="Best historic price", icon_name="trends")
            with m3:
                metric_card("7-Day High", f"₹{max_price:,.2f}", subtitle="Peak recorded price", icon_name="charts")
            with m4:
                metric_card("Recorded Points", f"{len(history)}", subtitle="Timeline observations", icon_name="dashboard")

            st.write("")

            # Main Price Trend Chart
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=history["recorded_at"],
                y=history["price"],
                mode="lines+markers",
                name="Sale Price",
                line=dict(color=palette["accent"], width=3, shape="spline"),
                marker=dict(size=9, color=palette["accent"], symbol="circle"),
                hovertemplate="<b>Date:</b> %{x|%Y-%m-%d %H:%M}<br><b>Sale Price:</b> ₹%{y:,.2f}<extra></extra>",
            ))

            if history["original_price"].notna().any():
                fig.add_trace(go.Scatter(
                    x=history["recorded_at"],
                    y=history["original_price"],
                    mode="lines+markers",
                    name="List Price (MRP)",
                    line=dict(color=palette["text_muted"], width=2, dash="dash"),
                    marker=dict(size=7, color=palette["text_muted"]),
                    hovertemplate="<b>MRP:</b> ₹%{y:,.2f}<extra></extra>",
                ))

            min_val = history["price"].min()
            max_val = max(history["price"].max(), history["original_price"].max() if history["original_price"].notna().any() else history["price"].max())
            pad = max(10.0, (max_val - min_val) * 0.15)

            fig.update_layout(
                title=f"Price Trajectory Over Time (₹)",
                xaxis_title="Recorded Date",
                yaxis_title="Price (₹)",
                yaxis=dict(range=[max(0, min_val - pad), max_val + pad]),
                hovermode="x unified",
                legend=dict(orientation="h", y=-0.18),
                height=450,
            )
            style_plotly_fig(fig)
            st.plotly_chart(fig, use_container_width=True)

            # Discount Percentage Trend Chart
            if history["discount_percentage"].notna().any():
                fig2 = go.Figure()
                fig2.add_trace(go.Scatter(
                    x=history["recorded_at"],
                    y=history["discount_percentage"],
                    mode="lines+markers",
                    name="Discount %",
                    line=dict(color=palette["accent_secondary"], width=3, shape="spline"),
                    marker=dict(size=8, color=palette["accent_secondary"]),
                    fill="tozeroy",
                    fillcolor="rgba(6, 182, 212, 0.1)",
                    hovertemplate="<b>Date:</b> %{x|%Y-%m-%d %H:%M}<br><b>Discount:</b> %{y:.1f}%<extra></extra>",
                ))
                fig2.update_layout(
                    title="Historical Discount Percentage (%)",
                    xaxis_title="Recorded Date",
                    yaxis_title="Discount %",
                    yaxis=dict(range=[0, min(100, history["discount_percentage"].max() + 10)]),
                    height=360,
                )
                style_plotly_fig(fig2)
                st.plotly_chart(fig2, use_container_width=True)

            with st.expander("View Historical Audit Records"):
                display_history_table(history, key="pt_single_table")

# ---- Tab 2: All Products overview -----------------------------------------
with tab_all:
    all_history = get_all_price_history()

    if all_history.empty:
        st.info("No aggregated price history data found.")
    else:
        all_history["recorded_at"] = pd.to_datetime(all_history["recorded_at"], errors="coerce")
        all_history = all_history.sort_values("recorded_at", ascending=True)

        st.caption(
            f"Analyzing **{len(all_history)}** historical price points across **{all_history['product_id'].nunique()}** tracked products."
        )

        avg_by_date = (
            all_history.groupby(all_history["recorded_at"].dt.date)["price"]
            .mean()
            .reset_index()
        )
        avg_by_date.columns = ["Date", "Avg Price"]

        if len(avg_by_date) > 1:
            fig3 = px.line(
                avg_by_date,
                x="Date",
                y="Avg Price",
                title="Market Average Price Movement (₹)",
                color_discrete_sequence=[palette["accent"]],
            )
            style_plotly_fig(fig3)
            fig3.update_traces(line=dict(width=3, shape="spline"), mode="lines+markers", marker=dict(size=7))
            st.plotly_chart(fig3, use_container_width=True)

        if "category" in all_history.columns and all_history["category"].notna().any():
            cat_avg = (
                all_history.dropna(subset=["category"])
                .groupby("category")["price"]
                .mean()
                .sort_values(ascending=False)
                .reset_index()
            )
            cat_avg.columns = ["Category", "Avg Price"]

            fig4 = px.bar(
                cat_avg,
                x="Category",
                y="Avg Price",
                title="Average Price Benchmark by Category (₹)",
                color="Category",
                color_discrete_sequence=PRICEPULSE_COLORS,
            )
            style_plotly_fig(fig4)
            fig4.update_layout(showlegend=False)
            fig4.update_traces(
                marker=dict(line=dict(color=palette["border"], width=1)),
                opacity=0.9,
            )
            st.plotly_chart(fig4, use_container_width=True)

        with st.expander("View Full Catalog Price Audit Records"):
            display_history_table(all_history, height=400, key="pt_all_table")
