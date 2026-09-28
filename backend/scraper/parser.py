from bs4 import BeautifulSoup
from urllib.parse import urljoin


BASE_URL = "https://www.amazon.in"


def clean_price(price_text):
    """Convert Amazon price text into a number."""

    if not price_text:
        return None

    price_text = (
        price_text
        .replace("₹", "")
        .replace(",", "")
        .replace("Rs.", "")
        .replace("Rs", "")
        .strip()
    )

    try:
        return float(price_text)
    except ValueError:
        return None


def extract_rating(rating_text):
    """Extract numeric rating from text such as '4.3 out of 5 stars'."""

    if not rating_text:
        return None

    try:
        return float(rating_text.split()[0])
    except (ValueError, IndexError):
        return None


def parse_product_cards(html):
    """Parse Amazon search-result HTML into product dictionaries."""

    soup = BeautifulSoup(html, "html.parser")

    products = []

    # ---------------------------------------------------------
    # Find Amazon product cards
    # ---------------------------------------------------------

    cards = soup.select(
        'div[data-component-type="s-search-result"]'
    )

    # Fallback selectors in case Amazon changes its HTML
    if not cards:
        cards = soup.select(
            'div[data-asin]:not([data-asin=""])'
        )

    if not cards:
        cards = soup.select(
            'div.s-result-item[data-asin]'
        )

    print("Product cards found:", len(cards))

    # ---------------------------------------------------------
    # Extract information from each product
    # ---------------------------------------------------------

    for card in cards:

        # ASIN
        asin = card.get("data-asin")

        # -----------------------------------------------------
        # Product name
        # -----------------------------------------------------

        name_element = card.select_one(
            "h2 span"
        )

        if not name_element:
            name_element = card.select_one(
                "h2 a span"
            )

        if not name_element:
            name_element = card.select_one(
                "h2"
            )

        if not name_element:
            continue

        name = name_element.get_text(
            " ",
            strip=True
        )

        if not name:
            continue

        # -----------------------------------------------------
        # Price
        # -----------------------------------------------------

        price_element = card.select_one(
            "span.a-price span.a-offscreen"
        )

        price = None

        if price_element:

            price_text = price_element.get_text(
                strip=True
            )

            price = clean_price(
                price_text
            )

        # -----------------------------------------------------
        # Original / list price
        # -----------------------------------------------------

        original_price_element = card.select_one(
            "span.a-price.a-text-price span.a-offscreen"
        )

        original_price = None

        if original_price_element:

            original_price_text = (
                original_price_element.get_text(
                    strip=True
                )
            )

            original_price = clean_price(
                original_price_text
            )

        # -----------------------------------------------------
        # Rating
        # -----------------------------------------------------

        rating_element = card.select_one(
            "span.a-icon-alt"
        )

        rating = None

        if rating_element:

            rating_text = rating_element.get_text(
                strip=True
            )

            rating = extract_rating(
                rating_text
            )

        # -----------------------------------------------------
        # Product URL
        # -----------------------------------------------------

        link_element = card.select_one(
            "h2 a"
        )

        if not link_element:

            link_element = card.select_one(
                "a[href*='/dp/']"
            )

        url = None

        if link_element:

            href = link_element.get(
                "href"
            )

            if href:

                url = urljoin(
                    BASE_URL,
                    href
                )

        # -----------------------------------------------------
        # Availability
        # -----------------------------------------------------

        availability = None

        availability_element = card.select_one(
            ".a-size-base-plus"
        )

        if availability_element:

            availability = availability_element.get_text(
                " ",
                strip=True
            )

        # -----------------------------------------------------
        # Save product
        # -----------------------------------------------------

        product = {
            "asin": asin,
            "name": name,
            "price": price,
            "original_price": original_price,
            "rating": rating,
            "availability": availability,
            "url": url
        }

        products.append(
            product
        )

    return products