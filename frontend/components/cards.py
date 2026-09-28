"""
cards.py – Visual card components for PricePulse.

Features:
- Pure vector SVG iconography (zero AI emojis)
- High-contrast typography across light and dark modes
- metric_card, deal_card, product_grid_card, product_highlight_card, product_detail_card
"""

from __future__ import annotations

from typing import Optional
import pandas as pd
import streamlit as st
from theme import get_palette, render_html
from components.icons import get_icon


def metric_card(
    label: str,
    value: str,
    subtitle: Optional[str] = None,
    icon_name: str = "charts",
    delta: Optional[str] = None,
    delta_positive: bool = True,
) -> None:
    """Render a modern stat metric card with SVG vector icon and accent border."""
    p = get_palette()
    delta_html = ""
    if delta:
        delta_color = p["success"] if delta_positive else p["error"]
        arrow = "↑" if delta_positive else "↓"
        delta_html = f'<span style="font-size:0.8rem; font-weight:700; color:{delta_color}; margin-left:8px;">{arrow} {delta}</span>'

    sub_html = f'<p class="pp-subtitle">{subtitle}</p>' if subtitle else ""
    icon_svg = get_icon(icon_name, size=20, color=p["accent"])

    html = f"""
<div class="pp-card">
    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
        <div>
            <h4>{label}</h4>
            <div style="display:flex; align-items:baseline;">
                <span class="pp-value">{value}</span>
                {delta_html}
            </div>
            {sub_html}
        </div>
        <div style="width:38px; height:38px; border-radius:10px; background:{p['accent_light']}; display:flex; align-items:center; justify-content:center; flex-shrink:0;">
            {icon_svg}
        </div>
    </div>
</div>
"""
    render_html(html)


def deal_card(row: pd.Series, rank: int) -> None:
    """
    Render a visual Deal Card with SVG icons, rank badge, price/MRP, discount pill,
    ratings, and deal score meter.
    """
    p = get_palette()
    name = str(row.get("name", "Product"))
    category = str(row.get("category", "General"))
    price = row.get("price")
    orig_price = row.get("original_price")
    discount = row.get("discount_percentage", 0.0)
    rating = row.get("rating", 0.0)
    deal_score = row.get("deal_score", 0.0)

    price_str = f"₹{price:,.2f}" if pd.notna(price) else "N/A"
    orig_str = f"₹{orig_price:,.2f}" if pd.notna(orig_price) else ""
    discount_str = f"-{discount:.0f}%" if pd.notna(discount) and discount > 0 else ""
    rating_val = f"{rating:.1f}" if pd.notna(rating) else "N/A"
    score_val = f"{deal_score:.0f}" if pd.notna(deal_score) else "N/A"

    rank_color = p["accent_gradient"] if rank <= 3 else p["card_border"]
    rank_text_color = "#FFFFFF" if rank <= 3 else p["text_secondary"]
    star_svg = get_icon("star", size=14, color=p["warning"])
    check_svg = get_icon("check", size=13, color=p["text_secondary"])

    html = f"""
<div class="pp-deal-card">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
        <span style="background:{rank_color}; color:{rank_text_color}; font-size:0.75rem; font-weight:800; padding:3px 10px; border-radius:20px; letter-spacing:0.04em;">
            #{rank} DEAL
        </span>
        <span style="background:{p['accent_light']}; color:{p['accent']}; font-size:0.75rem; font-weight:800; padding:3px 10px; border-radius:8px;">
            SCORE: {score_val}/100
        </span>
    </div>
    
    <div style="font-size:0.78rem; font-weight:700; text-transform:uppercase; color:{p['text_muted']}; margin-bottom:4px; letter-spacing:0.05em;">
        {category}
    </div>
    <h3 style="font-size:1.02rem; font-weight:700; line-height:1.4; margin:0 0 12px 0; color:{p['text']}; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; min-height:2.8rem;">
        {name}
    </h3>

    <div style="display:flex; align-items:baseline; gap:8px; margin-bottom:12px;">
        <span style="font-size:1.35rem; font-weight:800; color:{p['text']};">{price_str}</span>
        {f'<span style="font-size:0.9rem; text-decoration:line-through; color:{p["text_muted"]};">{orig_str}</span>' if orig_str else ''}
        {f'<span style="background:rgba(16, 185, 129, 0.15); color:{p["success"]}; font-size:0.78rem; font-weight:800; padding:2px 8px; border-radius:6px; margin-left:auto;">{discount_str}</span>' if discount_str else ''}
    </div>

    <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.82rem; padding-top:8px; border-top:1px solid {p['border']};">
        <span style="color:{p['warning']}; font-weight:700; display:inline-flex; align-items:center; gap:4px;">
            {star_svg} {rating_val}
        </span>
        <span style="color:{p['text_secondary']}; font-size:0.78rem; display:inline-flex; align-items:center; gap:4px;">
            {check_svg} Verified Listing
        </span>
    </div>
</div>
"""
    render_html(html)


def product_grid_card(row: pd.Series) -> None:
    """
    Render a clean ecommerce card for catalog browsing with SVG icons.
    """
    p = get_palette()
    pid = int(row.get("id", 0))
    name = str(row.get("name", "Product"))
    category = str(row.get("category", "General"))
    price = row.get("price")
    orig_price = row.get("original_price")
    discount = row.get("discount_percentage", 0.0)
    rating = row.get("rating", 0.0)
    avail = str(row.get("availability", "In Stock"))

    price_str = f"₹{price:,.2f}" if pd.notna(price) else "N/A"
    orig_str = f"₹{orig_price:,.2f}" if pd.notna(orig_price) else ""
    discount_str = f"-{discount:.0f}%" if pd.notna(discount) and discount > 0 else ""
    rating_val = f"{rating:.1f}" if pd.notna(rating) else "N/A"
    star_svg = get_icon("star", size=13, color=p["warning"])

    html = f"""
<div class="pp-deal-card">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
        <span style="background:{p['accent_light']}; color:{p['accent']}; font-size:0.75rem; font-weight:700; padding:3px 8px; border-radius:6px; letter-spacing:0.04em;">
            {category}
        </span>
        <span style="font-size:0.75rem; color:{p['text_muted']};">ID #{pid}</span>
    </div>

    <h4 style="font-size:0.98rem; font-weight:700; line-height:1.4; margin:0 0 10px 0; color:{p['text']}; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden; min-height:2.6rem;">
        {name}
    </h4>

    <div style="display:flex; align-items:baseline; gap:8px; margin-bottom:10px;">
        <span style="font-size:1.3rem; font-weight:800; color:{p['text']};">{price_str}</span>
        {f'<span style="font-size:0.85rem; text-decoration:line-through; color:{p["text_muted"]};">{orig_str}</span>' if orig_str else ''}
        {f'<span style="background:rgba(16, 185, 129, 0.15); color:{p["success"]}; font-size:0.78rem; font-weight:800; padding:2px 8px; border-radius:6px; margin-left:auto;">{discount_str}</span>' if discount_str else ''}
    </div>

    <div style="display:flex; justify-content:space-between; align-items:center; font-size:0.8rem; padding-top:8px; border-top:1px solid {p['border']};">
        <span style="color:{p['warning']}; font-weight:700; display:inline-flex; align-items:center; gap:4px;">
            {star_svg} {rating_val}
        </span>
        <span style="color:{p['text_secondary']};">{avail}</span>
    </div>
</div>
"""
    render_html(html)


def product_highlight_card(
    product: pd.Series,
    title: str = "Featured Product",
    icon_name: str = "fire",
    badge: Optional[str] = None,
) -> None:
    """Render a spotlight product card with vector SVG icon."""
    p = get_palette()
    name = str(product.get("name", "N/A"))
    price = product.get("price")
    orig_price = product.get("original_price")
    discount = product.get("discount_percentage")
    rating = product.get("rating")
    category = product.get("category", "")

    price_str = f"₹{price:,.2f}" if pd.notna(price) else "N/A"
    orig_str = f"₹{orig_price:,.2f}" if pd.notna(orig_price) else ""
    discount_val = f"{discount:.0f}% OFF" if pd.notna(discount) and discount > 0 else ""
    rating_val = f"{rating:.1f}/5" if pd.notna(rating) else "N/A"

    badge_html = f'<span style="background:{p["accent_gradient"]}; color:#FFF; font-size:0.75rem; font-weight:800; padding:2px 8px; border-radius:6px; margin-left:auto;">{badge or discount_val}</span>' if (badge or discount_val) else ""
    icon_svg = get_icon(icon_name, size=18, color=p["accent"])
    star_svg = get_icon("star", size=13, color=p["warning"])

    html = f"""
<div class="pp-deal-card" style="border-top: 3px solid {p['accent']};">
    <div style="display:flex; align-items:center; margin-bottom:8px;">
        <span style="margin-right:6px; display:inline-flex; align-items:center;">{icon_svg}</span>
        <span style="font-size:0.85rem; font-weight:800; text-transform:uppercase; letter-spacing:0.04em; color:{p['accent']};">{title}</span>
        {badge_html}
    </div>
    <p style="font-weight:700; font-size:1.05rem; line-height:1.4; margin:0 0 10px 0; color:{p['text']}; display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden;">
        {name}
    </p>
    <div style="display:flex; align-items:baseline; gap:10px; margin-bottom:10px;">
        <span style="font-size:1.4rem; font-weight:800; color:{p['text']};">{price_str}</span>
        {f'<span style="font-size:0.95rem; text-decoration:line-through; color:{p["text_secondary"]};">{orig_str}</span>' if orig_str else ''}
    </div>
    <div style="display:flex; align-items:center; justify-content:space-between; font-size:0.82rem; color:{p['text_secondary']}; border-top:1px solid {p['border']}; padding-top:8px;">
        <span>{category}</span>
        <span style="color:{p['warning']}; font-weight:700; display:inline-flex; align-items:center; gap:4px;">{star_svg} {rating_val}</span>
    </div>
</div>
"""
    render_html(html)


def product_detail_card(product: pd.Series) -> None:
    """
    Render a comprehensive, structured product showcase card for single-item views.
    Includes visual savings comparison and key specifications.
    """
    p = get_palette()
    name = str(product.get("name", "Product"))
    category = str(product.get("category", "General"))
    asin = str(product.get("asin", "N/A"))
    price = product.get("price")
    orig_price = product.get("original_price")
    discount = product.get("discount_percentage")
    rating = product.get("rating")
    availability = str(product.get("availability", "In Stock"))
    deal_score = product.get("deal_score")

    price_str = f"₹{price:,.2f}" if pd.notna(price) else "N/A"
    orig_str = f"₹{orig_price:,.2f}" if pd.notna(orig_price) else "N/A"
    discount_pct = float(discount) if pd.notna(discount) else 0.0
    savings = (orig_price - price) if (pd.notna(orig_price) and pd.notna(price) and orig_price > price) else 0.0

    rating_str = f"{rating:.1f} / 5.0" if pd.notna(rating) else "N/A"
    score_str = f"{deal_score:.1f}" if pd.notna(deal_score) else None
    bar_pct = min(100.0, max(0.0, discount_pct))

    score_box = f"""
<div style="background:{p['card_bg']}; border:1px solid {p['border']}; border-radius:12px; padding:12px 16px;">
    <div style="font-size:0.75rem; text-transform:uppercase; color:{p['text_secondary']}; font-weight:700; letter-spacing:0.04em;">Deal Score</div>
    <div style="font-size:1.25rem; font-weight:800; color:{p['accent_secondary']};">{score_str} / 100</div>
</div>
""" if score_str else ""

    html = f"""
<div style="background:{p['card_bg']}; border:1px solid {p['card_border']}; border-radius:16px; padding:24px; box-shadow:{p['card_shadow']}; margin-bottom:20px;">
    <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:12px; flex-wrap:wrap; gap:8px;">
        <div>
            <span style="background:{p['accent_light']}; color:{p['accent']}; font-size:0.75rem; font-weight:700; padding:4px 10px; border-radius:6px; text-transform:uppercase; letter-spacing:0.04em;">{category}</span>
            <span style="font-size:0.75rem; color:{p['text_muted']}; margin-left:8px;">ASIN: {asin}</span>
        </div>
        <span style="font-size:0.8rem; font-weight:700; padding:4px 10px; border-radius:6px; background:{p['card_bg']}; border:1px solid {p['border']}; color:{p['text_secondary']};">
            {availability}
        </span>
    </div>
    
    <h2 style="font-size:1.35rem; font-weight:800; margin:0 0 18px 0; color:{p['text']}; line-height:1.4;">
        {name}
    </h2>
    
    <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap:12px; margin-bottom:18px;">
        <div style="background:{p['header_gradient']}; border:1px solid {p['header_border']}; border-radius:12px; padding:12px 16px;">
            <div style="font-size:0.75rem; text-transform:uppercase; color:{p['text_secondary']}; font-weight:700; letter-spacing:0.04em;">Current Price</div>
            <div style="font-size:1.4rem; font-weight:800; color:{p['accent']};">{price_str}</div>
        </div>
        <div style="background:{p['card_bg']}; border:1px solid {p['border']}; border-radius:12px; padding:12px 16px;">
            <div style="font-size:0.75rem; text-transform:uppercase; color:{p['text_secondary']}; font-weight:700; letter-spacing:0.04em;">List MRP</div>
            <div style="font-size:1.25rem; font-weight:600; color:{p['text_muted']}; text-decoration:line-through;">{orig_str}</div>
        </div>
        <div style="background:{p['card_bg']}; border:1px solid {p['border']}; border-radius:12px; padding:12px 16px;">
            <div style="font-size:0.75rem; text-transform:uppercase; color:{p['text_secondary']}; font-weight:700; letter-spacing:0.04em;">Instant Savings</div>
            <div style="font-size:1.25rem; font-weight:800; color:{p['success']};">₹{savings:,.2f}</div>
        </div>
        <div style="background:{p['card_bg']}; border:1px solid {p['border']}; border-radius:12px; padding:12px 16px;">
            <div style="font-size:0.75rem; text-transform:uppercase; color:{p['text_secondary']}; font-weight:700; letter-spacing:0.04em;">Rating</div>
            <div style="font-size:1.25rem; font-weight:800; color:{p['warning']};">{rating_str}</div>
        </div>
        {score_box}
    </div>

    <div>
        <div style="display:flex; justify-content:space-between; font-size:0.82rem; font-weight:700; margin-bottom:6px;">
            <span style="color:{p['text_secondary']};">Discount Percentage</span>
            <span style="color:{p['accent']}; font-weight:800;">{discount_pct:.1f}% OFF</span>
        </div>
        <div style="width:100%; height:8px; background:{p['border']}; border-radius:4px; overflow:hidden;">
            <div style="width:{bar_pct}%; height:100%; background:{p['accent_gradient']}; border-radius:4px;"></div>
        </div>
    </div>
</div>
"""
    render_html(html)
