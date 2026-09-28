"""
data_access.py – Thin wrapper around backend modules.

Adds the backend directory to sys.path so every page can simply call
``from data_access import …`` without worrying about path manipulation.

ALL database/analysis/scraper calls go through this module so the UI
layer stays clean.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Optional

import pandas as pd

# ---------------------------------------------------------------------------
# Path setup: make the *backend* package importable.
# The backend lives at  <project_root>/backend/  and its modules use
# ``from database.db import …`` style imports, so we add the *backend*
# directory itself to sys.path.
# ---------------------------------------------------------------------------

_BACKEND_DIR = Path(__file__).resolve().parent.parent / "backend"

if str(_BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(_BACKEND_DIR))

# ---------------------------------------------------------------------------
# Import backend modules (after path setup)
# ---------------------------------------------------------------------------

import os
import database.db as backend_db

# Support DATABASE_PATH environment variable override for cloud platforms (e.g. /tmp/app.db)
_custom_db_path = os.getenv("DATABASE_PATH")
if _custom_db_path:
    backend_db.DATABASE_PATH = Path(_custom_db_path)

from database.db import get_connection                          # noqa: E402
from database.init_db import initialize_database                # noqa: E402
from database.product_repository import save_product            # noqa: E402
from analysis.analyzer import (                                 # noqa: E402
    load_latest_products,
    calculate_summary,
    calculate_deal_score,
    get_best_deals,
    get_lowest_price_product,
    get_highest_discount_product,
)


# ---------------------------------------------------------------------------
# Convenience wrappers & Auto-initialization
# ---------------------------------------------------------------------------

def _seed_sample_catalog() -> None:
    """Populate default catalog if starting on an empty production instance."""
    from datetime import datetime, timedelta

    sample_items = [
        {"asin": "B09XYZ001", "name": "boAt Rockerz 450 Bluetooth Headphone", "url": "https://www.amazon.in/dp/B09XYZ001", "category": "Electronics", "rating": 4.1, "availability": "In Stock", "price": 1299.0, "original_price": 2990.0},
        {"asin": "B09XYZ002", "name": "JBL Tune 760NC Wireless Over-Ear Headphones", "url": "https://www.amazon.in/dp/B09XYZ002", "category": "Electronics", "rating": 4.4, "availability": "In Stock", "price": 4499.0, "original_price": 7999.0},
        {"asin": "B09XYZ003", "name": "Sony WH-1000XM5 Noise Cancelling Headphones", "url": "https://www.amazon.in/dp/B09XYZ003", "category": "Electronics", "rating": 4.6, "availability": "In Stock", "price": 22990.0, "original_price": 34990.0},
        {"asin": "B09XYZ004", "name": "OnePlus Nord Buds 2r True Wireless Earbuds", "url": "https://www.amazon.in/dp/B09XYZ004", "category": "Electronics", "rating": 4.2, "availability": "In Stock", "price": 1799.0, "original_price": 2299.0},
        {"asin": "B09XYZ005", "name": "Noise Buds VS104 Truly Wireless Earbuds", "url": "https://www.amazon.in/dp/B09XYZ005", "category": "Electronics", "rating": 3.9, "availability": "In Stock", "price": 899.0, "original_price": 1999.0},
        {"asin": "B09XYZ006", "name": "Libas Women Printed Anarkali Kurta", "url": "https://www.amazon.in/dp/B09XYZ006", "category": "Fashion", "rating": 4.0, "availability": "In Stock", "price": 549.0, "original_price": 1299.0},
        {"asin": "B09XYZ007", "name": "BIBA Women Cotton Straight Kurta", "url": "https://www.amazon.in/dp/B09XYZ007", "category": "Fashion", "rating": 4.3, "availability": "In Stock", "price": 899.0, "original_price": 1599.0},
        {"asin": "B09XYZ008", "name": "Amazon Brand - Solimo Wall Clock", "url": "https://www.amazon.in/dp/B09XYZ008", "category": "Home", "rating": 4.1, "availability": "In Stock", "price": 399.0, "original_price": 799.0},
        {"asin": "B09XYZ009", "name": "Asian Paints Royale Matt Finish Interior Paint", "url": "https://www.amazon.in/dp/B09XYZ009", "category": "Home", "rating": 4.5, "availability": "In Stock", "price": 2650.0, "original_price": 3200.0},
        {"asin": "B09XYZ010", "name": "Plum Green Tea Face Wash Gel", "url": "https://www.amazon.in/dp/B09XYZ010", "category": "Beauty", "rating": 4.3, "availability": "In Stock", "price": 285.0, "original_price": 345.0},
        {"asin": "B09XYZ011", "name": "Mamaearth Vitamin C Face Serum", "url": "https://www.amazon.in/dp/B09XYZ011", "category": "Beauty", "rating": 4.0, "availability": "In Stock", "price": 449.0, "original_price": 699.0},
        {"asin": "B09XYZ012", "name": "Atomic Habits by James Clear", "url": "https://www.amazon.in/dp/B09XYZ012", "category": "Books", "rating": 4.7, "availability": "In Stock", "price": 350.0, "original_price": 799.0},
        {"asin": "B09XYZ013", "name": "Rich Dad Poor Dad by Robert Kiyosaki", "url": "https://www.amazon.in/dp/B09XYZ013", "category": "Books", "rating": 4.5, "availability": "In Stock", "price": 249.0, "original_price": 499.0},
        {"asin": "B09XYZ014", "name": "Ikigai: The Japanese Secret by Hector Garcia", "url": "https://www.amazon.in/dp/B09XYZ014", "category": "Books", "rating": 4.4, "availability": "In Stock", "price": 199.0, "original_price": 450.0},
        {"asin": "B09XYZ015", "name": "Fire-Boltt Ninja Call Pro Plus Smartwatch", "url": "https://www.amazon.in/dp/B09XYZ015", "category": "Electronics", "rating": 3.8, "availability": "In Stock", "price": 1499.0, "original_price": 5999.0},
    ]

    saved_pids = []
    for item in sample_items:
        try:
            res = save_product(item)
            saved_pids.append((res["product_id"], item["price"], item["original_price"]))
        except Exception:
            pass

    # Insert historical trend points for rich charts
    try:
        conn = get_connection()
        cur = conn.cursor()
        now = datetime.now()
        for pid, base_price, orig_price in saved_pids:
            for day_offset in [15, 12, 9, 6, 3]:
                hist_date = (now - timedelta(days=day_offset)).isoformat(timespec="seconds")
                fluctuation = 1.0 + ((day_offset % 3) - 1) * 0.04
                hist_price = round(base_price * fluctuation, 2)
                hist_disc = round(((orig_price - hist_price) / orig_price) * 100, 2)
                cur.execute(
                    "INSERT INTO price_history (product_id, price, original_price, discount_percentage, recorded_at) VALUES (?, ?, ?, ?, ?)",
                    (pid, hist_price, orig_price, hist_disc, hist_date)
                )
        conn.commit()
        conn.close()
    except Exception:
        pass


def ensure_db() -> None:
    """Create tables if they don't exist yet and populate seed data if empty."""
    initialize_database()
    try:
        df = load_latest_products()
        if df.empty:
            _seed_sample_catalog()
    except Exception:
        pass


def get_all_products() -> pd.DataFrame:
    """Return the latest-price snapshot for every product."""
    return load_latest_products()


def get_summary(df: pd.DataFrame) -> dict[str, Any]:
    """Dashboard summary stats (total products, avg price, etc.)."""
    return calculate_summary(df)


def get_deal_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Add deal_score column to the DataFrame."""
    return calculate_deal_score(df)


def get_top_deals(df: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    """Best deals by deal-score."""
    return get_best_deals(df, limit=limit)


def get_cheapest(df: pd.DataFrame) -> Optional[pd.Series]:
    """Product with the lowest price."""
    return get_lowest_price_product(df)


def get_most_discounted(df: pd.DataFrame) -> Optional[pd.Series]:
    """Product with the highest discount percentage."""
    return get_highest_discount_product(df)


def get_price_history(product_id: int) -> pd.DataFrame:
    """
    Return full price history for a single product.

    Queries the ``price_history`` table directly – this is reading
    existing backend data, not inventing new logic.
    """
    conn = get_connection()
    query = """
        SELECT
            ph.price,
            ph.original_price,
            ph.discount_percentage,
            ph.recorded_at
        FROM price_history ph
        WHERE ph.product_id = ?
        ORDER BY ph.recorded_at ASC
    """
    df = pd.read_sql_query(query, conn, params=(product_id,))
    conn.close()
    return df


def get_discount_history(product_id: int) -> pd.DataFrame:
    """
    Return full discount history for a single product.

    Queries the ``discount_history`` table directly.
    """
    conn = get_connection()
    query = """
        SELECT
            dh.original_price,
            dh.sale_price,
            dh.discount_percentage,
            dh.recorded_at
        FROM discount_history dh
        WHERE dh.product_id = ?
        ORDER BY dh.recorded_at ASC
    """
    df = pd.read_sql_query(query, conn, params=(product_id,))
    conn.close()
    return df


def get_all_price_history() -> pd.DataFrame:
    """Return price history for ALL products (with product name)."""
    conn = get_connection()
    query = """
        SELECT
            p.id   AS product_id,
            p.name AS product_name,
            p.category,
            ph.price,
            ph.original_price,
            ph.discount_percentage,
            ph.recorded_at
        FROM price_history ph
        JOIN products p ON p.id = ph.product_id
        ORDER BY ph.recorded_at ASC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def get_all_discount_history() -> pd.DataFrame:
    """Return discount history for ALL products (with product name)."""
    conn = get_connection()
    query = """
        SELECT
            p.id   AS product_id,
            p.name AS product_name,
            p.category,
            dh.original_price,
            dh.sale_price,
            dh.discount_percentage,
            dh.recorded_at
        FROM discount_history dh
        JOIN products p ON p.id = dh.product_id
        ORDER BY dh.recorded_at ASC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def get_categories() -> list[str]:
    """Return distinct non-null categories from the products table."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT DISTINCT category FROM products WHERE category IS NOT NULL ORDER BY category"
    )
    rows = cursor.fetchall()
    conn.close()
    return [row["category"] for row in rows]


def save_scraped_product(product_dict: dict[str, Any]) -> dict[str, Any]:
    """Save a single scraped product via the backend repository."""
    return save_product(product_dict)


def scrape_amazon_category(keyword: str, category: str) -> int:
    """
    Run the Selenium scraper for one category.

    Returns the number of products saved.
    Raises on error (Selenium not installed, Chrome missing, etc.).
    """
    # Import lazily – Selenium may not be installed on the frontend host.
    from scraper.amazon_selenium import scrape_category  # noqa: E402
    return scrape_category(keyword, category)
