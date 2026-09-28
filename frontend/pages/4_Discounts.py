"""
PricePulse – Discounts page.

Discount analysis: distributions, top discounted products,
multi-point discount history timeline, and category-level breakdown.
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
    get_all_discount_history,
    get_discount_history,
)
from theme import (
    inject_css,
    render_theme_toggle,
    get_palette,
    page_header,
    style_plotly_fig,
    PRICEPULSE_COLORS,
)
from components.cards import metric_card, product_grid_card
from components.tables import display_product_table, display_history_table

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="PricePulse – Discounts",
    page_icon="💰",
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
    title="Discount Analytics & Savings",
    subtitle="Evaluate markdown distributions, category savings benchmarks, and temporal price cuts",
    icon_name="discount",
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
    st.info("No product records found in the database.")
    st.stop()

# ---------------------------------------------------------------------------
# Summary metrics (SVG Icons)
# ---------------------------------------------------------------------------
discounted = df[df["discount_percentage"].notna() & (df["discount_percentage"] > 0)]
total_with_discount = len(discounted)
avg_discount = discounted["discount_percentage"].mean() if not discounted.empty else 0
max_discount = discounted["discount_percentage"].max() if not discounted.empty else 0

c1, c2, c3 = st.columns(3)
with c1:
    metric_card(
        label="Discounted Listings",
        value=f"{total_with_discount}",
        subtitle=f"{total_with_discount / len(df) * 100:.0f}% of catalog currently on sale",
        icon_name="discount",
    )
with c2:
    metric_card(
        label="Average Markdown",
        value=f"{avg_discount:.1f}%",
        subtitle="Across discounted listings",
        icon_name="charts",
    )
with c3:
    metric_card(
        label="Peak Discount",
        value=f"{max_discount:.1f}%",
        subtitle="Maximum catalog reduction",
        icon_name="fire",
    )

st.divider()

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab_overview, tab_product, tab_history = st.tabs([
    "Market Overview", "Single Product History", "Catalog Discount Log"
])

# ---- Tab 1: Overview -------------------------------------------------------
with tab_overview:
    col_a, col_b = st.columns(2)

    with col_a:
        disc_vals = df["discount_percentage"].dropna()
        if not disc_vals.empty:
            fig1 = px.histogram(
                disc_vals,
                nbins=15,
                title="Discount Frequency Distribution (%)",
                labels={"value": "Discount %", "count": "Products"},
                color_discrete_sequence=[palette["accent"]],
            )
            style_plotly_fig(fig1)
            fig1.update_layout(showlegend=False)
            fig1.update_traces(
                marker=dict(line=dict(color=palette["border"], width=1)),
                opacity=0.88,
            )
            st.plotly_chart(fig1, use_container_width=True)
        else:
            st.info("No discount values recorded.")

    with col_b:
        if "category" in df.columns and df["category"].notna().any():
            cat_disc = (
                df.dropna(subset=["category", "discount_percentage"])
                .groupby("category")["discount_percentage"]
                .mean()
                .sort_values(ascending=False)
                .reset_index()
            )
            cat_disc.columns = ["Category", "Avg Discount %"]
            if not cat_disc.empty:
                fig2 = px.bar(
                    cat_disc,
                    x="Category",
                    y="Avg Discount %",
                    title="Average Discount Benchmark by Category",
                    color="Category",
                    color_discrete_sequence=PRICEPULSE_COLORS,
                )
                style_plotly_fig(fig2)
                fig2.update_layout(showlegend=False)
                fig2.update_traces(
                    marker=dict(line=dict(color=palette["border"], width=1)),
                    opacity=0.9,
                )
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("No category discount data.")
        else:
            st.info("No category data available.")

    st.markdown("### Top Deepest Discount Opportunities")
    top_disc = (
        df.dropna(subset=["discount_percentage"])
        .sort_values("discount_percentage", ascending=False)
        .head(12)
    )
    if not top_disc.empty:
        card_cols = st.columns(3)
        for i, (_, r) in enumerate(top_disc.head(6).iterrows()):
            with card_cols[i % 3]:
                product_grid_card(r)

        with st.expander("View All Top 12 Deals in Formatted Table"):
            display_product_table(
                top_disc,
                columns=["name", "category", "price", "original_price", "discount_percentage", "rating"],
                key="disc_top_table",
            )
    else:
        st.info("No discounted products found.")

# ---- Tab 2: By Product -----------------------------------------------------
with tab_product:
    name_id_map: dict[str, int] = {}
    for _, row in df.iterrows():
        pid = int(row["id"])
        name = str(row.get("name", f"Product {pid}"))
        label = f"#{pid} — {name[:75]}"
        name_id_map[label] = pid

    selected = st.selectbox(
        "Select Product to Track Discount Timeline:",
        options=list(name_id_map.keys()),
        key="disc_prod_sel",
    )

    if selected:
        prod_id = name_id_map[selected]
        dh = get_discount_history(prod_id)
        if dh.empty:
            st.info("No discount history records found for this product.")
        else:
            dh["recorded_at"] = pd.to_datetime(dh["recorded_at"], errors="coerce")
            dh = dh.sort_values("recorded_at", ascending=True).reset_index(drop=True)

            fig4 = go.Figure()
            fig4.add_trace(go.Scatter(
                x=dh["recorded_at"],
                y=dh["discount_percentage"],
                mode="lines+markers",
                name="Discount %",
                line=dict(color=palette["accent_secondary"], width=3, shape="spline"),
                marker=dict(size=8, color=palette["accent_secondary"]),
                fill="tozeroy",
                fillcolor="rgba(6, 182, 212, 0.12)",
                hovertemplate="<b>Date:</b> %{x|%Y-%m-%d %H:%M}<br><b>Discount:</b> %{y:.1f}%<extra></extra>",
            ))
            fig4.update_layout(
                title="Historical Discount Percentage (%)",
                xaxis_title="Recorded Date",
                yaxis_title="Discount %",
                height=380,
            )
            style_plotly_fig(fig4)
            st.plotly_chart(fig4, use_container_width=True)

            if dh["original_price"].notna().any() and dh["sale_price"].notna().any():
                dh["savings"] = dh["original_price"] - dh["sale_price"]
                fig5 = go.Figure()
                fig5.add_trace(go.Scatter(
                    x=dh["recorded_at"],
                    y=dh["savings"],
                    mode="lines+markers",
                    name="Savings (₹)",
                    line=dict(color=palette["success"], width=3, shape="spline"),
                    marker=dict(size=8, color=palette["success"]),
                    fill="tozeroy",
                    fillcolor="rgba(16, 185, 129, 0.12)",
                    hovertemplate="<b>Date:</b> %{x|%Y-%m-%d %H:%M}<br><b>Savings:</b> ₹%{y:,.2f}<extra></extra>",
                ))
                fig5.update_layout(
                    title="Realized Cash Savings (₹) Over Time",
                    xaxis_title="Recorded Date",
                    yaxis_title="Savings (₹)",
                    height=380,
                )
                style_plotly_fig(fig5)
                st.plotly_chart(fig5, use_container_width=True)

            with st.expander("View Detailed Discount Audit Log"):
                display_history_table(dh, key="disc_prod_table")

# ---- Tab 3: All Discount History -------------------------------------------
with tab_history:
    all_dh = get_all_discount_history()
    if all_dh.empty:
        st.info("No discount history records recorded yet.")
    else:
        st.markdown(
            f"**{len(all_dh)}** historical discount snapshots recorded across **{all_dh['product_id'].nunique()}** unique products"
        )
        display_history_table(all_dh, height=520, key="disc_all_table")
