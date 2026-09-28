"""
filters.py – Polished filter & search widgets for product DataFrames.
Professional labels with zero emojis.
"""

from __future__ import annotations

from typing import Optional
import pandas as pd
import streamlit as st


def search_box(
    df: pd.DataFrame,
    label: str = "Search catalog",
    key: str = "search",
) -> pd.DataFrame:
    """
    Polished search box searching across name, category, and asin.
    """
    query = st.text_input(
        label,
        key=key,
        placeholder="Type to search by product name, category, or ASIN...",
        label_visibility="collapsed",
    )
    if query:
        q = query.strip()
        mask = df["name"].str.contains(q, case=False, na=False)
        if "category" in df.columns:
            mask = mask | df["category"].str.contains(q, case=False, na=False)
        if "asin" in df.columns:
            mask = mask | df["asin"].str.contains(q, case=False, na=False)
        return df[mask].copy()
    return df


def category_filter(
    df: pd.DataFrame,
    categories: list[str],
    key: str = "cat_filter",
) -> pd.DataFrame:
    """Multi-select category filter."""
    if not categories:
        return df
    selected = st.multiselect(
        "Filter by Category",
        options=categories,
        key=key,
        placeholder="All Categories",
    )
    if selected:
        return df[df["category"].isin(selected)].copy()
    return df


def price_range_filter(
    df: pd.DataFrame,
    key: str = "price_range",
) -> pd.DataFrame:
    """Slider filter for the price column."""
    prices = df["price"].dropna()
    if prices.empty:
        return df
    min_p = float(prices.min())
    max_p = float(prices.max())
    if min_p >= max_p:
        return df
    low, high = st.slider(
        "Price Range (₹)",
        min_value=min_p,
        max_value=max_p,
        value=(min_p, max_p),
        format="₹%.0f",
        key=key,
    )
    return df[(df["price"] >= low) & (df["price"] <= high)].copy()


def discount_range_filter(
    df: pd.DataFrame,
    key: str = "disc_range",
) -> pd.DataFrame:
    """Slider filter for the discount_percentage column."""
    discounts = df["discount_percentage"].dropna()
    if discounts.empty:
        return df
    min_d = float(discounts.min())
    max_d = float(discounts.max())
    if min_d >= max_d:
        return df
    low, high = st.slider(
        "Discount Range (%)",
        min_value=min_d,
        max_value=max_d,
        value=(min_d, max_d),
        format="%.0f%%",
        key=key,
    )
    mask = df["discount_percentage"].fillna(0).between(low, high)
    return df[mask].copy()


def rating_filter(
    df: pd.DataFrame,
    key: str = "rating_filter",
) -> pd.DataFrame:
    """Slider filter for minimum rating."""
    ratings = df["rating"].dropna()
    if ratings.empty:
        return df
    min_r = float(ratings.min())
    max_r = float(ratings.max())
    if min_r >= max_r:
        return df
    threshold = st.slider(
        "Minimum Customer Rating",
        min_value=1.0,
        max_value=5.0,
        value=1.0,
        step=0.5,
        format="★ %.1f",
        key=key,
    )
    return df[df["rating"].fillna(0) >= threshold].copy()


def sort_selector(
    df: pd.DataFrame,
    key: str = "sort_sel",
) -> pd.DataFrame:
    """Sort selector dropdown."""
    options = {
        "Default (Catalog ID)": ("id", True),
        "Price: Low to High": ("price", True),
        "Price: High to Low": ("price", False),
        "Discount: Highest First": ("discount_percentage", False),
        "Rating: Highest First": ("rating", False),
    }
    choice = st.selectbox(
        "Sort Catalog",
        options=list(options.keys()),
        key=key,
        label_visibility="collapsed",
    )
    col, asc = options[choice]
    if col in df.columns:
        return df.sort_values(col, ascending=asc, na_position="last").copy()
    return df
