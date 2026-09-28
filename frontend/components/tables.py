"""
tables.py – High-end DataFrame display helpers with column configurations.

Features:
- Currency formatting for price & MRP (₹)
- Progress visual indicators for discount percentage and deal score
- Star rating formatting
- Consistent table container width and styling
"""

from __future__ import annotations

from typing import Optional
import pandas as pd
import streamlit as st

# Columns we typically want to show in the product table.
DEFAULT_PRODUCT_COLUMNS = [
    "id",
    "name",
    "category",
    "price",
    "original_price",
    "discount_percentage",
    "rating",
    "availability",
]

# Friendly display names.
COLUMN_LABELS = {
    "id": "ID",
    "asin": "ASIN",
    "name": "Product Name",
    "category": "Category",
    "price": "Price",
    "original_price": "MRP",
    "discount_percentage": "Discount",
    "rating": "Rating",
    "availability": "Availability",
    "deal_score": "Deal Score",
    "recorded_at": "Recorded At",
    "product_name": "Product Name",
    "sale_price": "Sale Price",
}


def display_product_table(
    df: pd.DataFrame,
    columns: Optional[list[str]] = None,
    height: int = 460,
    key: Optional[str] = None,
) -> None:
    """
    Display a products DataFrame as an interactive Streamlit table
    with rich column configurations (currency, progress bars, star ratings).
    """
    if df.empty:
        st.info("No products to display.")
        return

    cols = columns or [c for c in DEFAULT_PRODUCT_COLUMNS if c in df.columns]
    view = df[cols].copy()

    # Column configuration definitions
    column_config = {}

    if "name" in view.columns:
        column_config["name"] = st.column_config.TextColumn(
            label="Product Name",
            width="large",
            help="Full Amazon listing title",
        )

    if "category" in view.columns:
        column_config["category"] = st.column_config.TextColumn(
            label="Category",
            width="small",
        )

    if "price" in view.columns:
        column_config["price"] = st.column_config.NumberColumn(
            label="Price (₹)",
            format="₹%.2f",
            width="small",
        )

    if "original_price" in view.columns:
        column_config["original_price"] = st.column_config.NumberColumn(
            label="MRP (₹)",
            format="₹%.2f",
            width="small",
        )

    if "discount_percentage" in view.columns:
        column_config["discount_percentage"] = st.column_config.ProgressColumn(
            label="Discount",
            format="%.0f%%",
            min_value=0,
            max_value=100,
            width="medium",
        )

    if "rating" in view.columns:
        column_config["rating"] = st.column_config.NumberColumn(
            label="Rating",
            format="★ %.1f",
            min_value=0,
            max_value=5,
            width="small",
        )

    if "deal_score" in view.columns:
        column_config["deal_score"] = st.column_config.ProgressColumn(
            label="Deal Score",
            format="%.1f",
            min_value=0,
            max_value=100,
            width="medium",
        )

    if "availability" in view.columns:
        column_config["availability"] = st.column_config.TextColumn(
            label="Status",
            width="small",
        )

    st.dataframe(
        view,
        height=height,
        use_container_width=True,
        hide_index=True,
        key=key,
        column_config=column_config,
    )


def display_history_table(
    df: pd.DataFrame,
    height: int = 350,
    key: Optional[str] = None,
) -> None:
    """Display a price/discount history DataFrame with formatted columns."""
    if df.empty:
        st.info("No history records to display.")
        return

    view = df.copy()
    column_config = {}

    if "price" in view.columns:
        column_config["price"] = st.column_config.NumberColumn(
            label="Price (₹)",
            format="₹%.2f",
        )
    if "original_price" in view.columns:
        column_config["original_price"] = st.column_config.NumberColumn(
            label="MRP (₹)",
            format="₹%.2f",
        )
    if "discount_percentage" in view.columns:
        column_config["discount_percentage"] = st.column_config.ProgressColumn(
            label="Discount",
            format="%.0f%%",
            min_value=0,
            max_value=100,
        )
    if "sale_price" in view.columns:
        column_config["sale_price"] = st.column_config.NumberColumn(
            label="Sale Price (₹)",
            format="₹%.2f",
        )
    if "recorded_at" in view.columns:
        column_config["recorded_at"] = st.column_config.DatetimeColumn(
            label="Timestamp",
            format="YYYY-MM-DD HH:mm",
        )

    st.dataframe(
        view,
        height=height,
        use_container_width=True,
        hide_index=True,
        key=key,
        column_config=column_config,
    )
