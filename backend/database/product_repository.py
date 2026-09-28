from datetime import datetime

from database.db import get_connection


def calculate_discount(price, original_price):
    """
    Calculate discount percentage.
    """

    if price is None or original_price is None:
        return None

    if original_price <= 0:
        return None

    discount = (
        (original_price - price)
        / original_price
    ) * 100

    return round(discount, 2)


def save_product(product):
    """
    Save one scraped Amazon product and its price information.
    """

    connection = get_connection()
    cursor = connection.cursor()

    recorded_at = datetime.now().isoformat(
        timespec="seconds"
    )

    asin = product.get("asin")
    name = product.get("name")
    price = product.get("price")
    original_price = product.get("original_price")
    rating = product.get("rating")
    availability = product.get("availability")
    url = product.get("url")
    category = product.get("category")

    # Convert empty ASIN values to None.
    if asin:
        asin = asin.strip()
    else:
        asin = None

    # Convert empty category values to None.
    if category:
        category = category.strip()
    else:
        category = None

    # A product must have at least a name and URL.
    if not name or not url:
        connection.close()

        raise ValueError(
            "Product name or URL is missing."
        )

    discount_percentage = calculate_discount(
        price,
        original_price
    )

    # First check whether this product already exists.
    existing_product = None

    if asin:

        cursor.execute(
            """
            SELECT id
            FROM products
            WHERE asin = ?
            """,
            (asin,)
        )

        existing_product = cursor.fetchone()

    if existing_product is None:

        cursor.execute(
            """
            SELECT id
            FROM products
            WHERE url = ?
            """,
            (url,)
        )

        existing_product = cursor.fetchone()

    # If product already exists, update its information.
    if existing_product is not None:

        product_id = existing_product["id"]

        cursor.execute(
            """
            UPDATE products
            SET
                name = ?,
                category = ?,
                rating = ?,
                availability = ?
            WHERE id = ?
            """,
            (
                name,
                category,
                rating,
                availability,
                product_id
            )
        )

    # Otherwise insert a new product.
    else:

        cursor.execute(
            """
            INSERT INTO products (
                asin,
                name,
                url,
                category,
                rating,
                availability,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                asin,
                name,
                url,
                category,
                rating,
                availability,
                recorded_at
            )
        )

        product_id = cursor.lastrowid

    # Save price history.
    if price is not None:

        cursor.execute(
            """
            INSERT INTO price_history (
                product_id,
                price,
                original_price,
                discount_percentage,
                recorded_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                product_id,
                price,
                original_price,
                discount_percentage,
                recorded_at
            )
        )

        # Save discount history.
        cursor.execute(
            """
            INSERT INTO discount_history (
                product_id,
                original_price,
                sale_price,
                discount_percentage,
                recorded_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                product_id,
                original_price,
                price,
                discount_percentage,
                recorded_at
            )
        )

    connection.commit()
    connection.close()

    return {
        "product_id": product_id,
        "discount_percentage": discount_percentage
    }   