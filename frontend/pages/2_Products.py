"""
PricePulse – Products page.

Browse, search, filter, and inspect products in the database.
Features a visual product cards grid (default) and table view,
plus a rich product deep-dive card with no code display bugs and zero emojis.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st
import pandas as pd

# -- path setup --------------------------------------------------------------
_FRONTEND = Path(__file__).resolve().parent.parent
if str(_FRONTEND) not in sys.path:
    sys.path.insert(0, str(_FRONTEND))

from data_access import ensure_db, get_all_products, get_categories
from theme import inject_css, render_theme_toggle, get_palette, page_header, render_html
from components.filters import (
    search_box,
    category_filter,
    price_range_filter,
    discount_range_filter,
    rating_filter,
    sort_selector,
)
from components.tables import display_product_table
from components.cards import product_grid_card, product_detail_card

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="PricePulse – Products",
    page_icon="📦",
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
    title="Product Catalog & Explorer",
    subtitle="Search, filter, compare, and inspect granular metrics for all tracked Amazon items",
    icon_name="products",
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
    st.info("No products found in the database. Please verify that your product catalog is populated.")
    st.stop()

# ---------------------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Filter Catalog")
    categories = get_categories()
    filtered = category_filter(df, categories, key="prod_cat")
    filtered = price_range_filter(filtered, key="prod_price")
    filtered = discount_range_filter(filtered, key="prod_disc")
    filtered = rating_filter(filtered, key="prod_rating")

# ---------------------------------------------------------------------------
# Main area: search + sort + view switcher
# ---------------------------------------------------------------------------
col_search, col_sort = st.columns([3, 1])

with col_search:
    filtered = search_box(filtered, key="prod_search")

with col_sort:
    filtered = sort_selector(filtered, key="prod_sort")

# Header controls with View Mode selector & count
c_count, c_mode = st.columns([2, 1])
with c_count:
    render_html(f"""
        <div style="margin: 6px 0 12px 0; font-size: 0.92rem; color: {palette['text_secondary']};">
            Showing <strong>{len(filtered)}</strong> matching product(s) of <strong>{len(df)}</strong> total
        </div>
    """)

with c_mode:
    view_mode = st.radio(
        "View Mode",
        options=["Visual Cards", "Table View"],
        horizontal=True,
        label_visibility="collapsed",
        key="prod_view_mode",
    )

# ---------------------------------------------------------------------------
# Catalog Display (Visual Cards vs Table)
# ---------------------------------------------------------------------------
if filtered.empty:
    st.info("No products match your current search and filter criteria.")
else:
    if view_mode == "Visual Cards":
        cols = st.columns(3)
        for i, (_, row) in enumerate(filtered.iterrows()):
            with cols[i % 3]:
                product_grid_card(row)
    else:
        display_product_table(filtered, height=520, key="prod_table")

# ---------------------------------------------------------------------------
# Structured Product Deep Dive Card
# ---------------------------------------------------------------------------
st.divider()
st.markdown("### Product Deep Dive & Specification Inspector")
st.caption("Select any product below to inspect its pricing breakdown, list price comparison, and instant savings.")

product_ids = filtered["id"].dropna().astype(int).tolist()
if product_ids:
    id_name_map = dict(zip(filtered["id"].astype(int), filtered["name"].astype(str)))
    selected_id = st.selectbox(
        "Select Product to Inspect:",
        options=product_ids,
        format_func=lambda pid: f"#{pid} — {id_name_map.get(pid, '')[:70]}",
        key="prod_detail_id",
    )
    row = filtered[filtered["id"] == selected_id]
    if not row.empty:
        r = row.iloc[0]
        product_detail_card(r)
