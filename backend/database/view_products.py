from database.db import get_connection


def show_products():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            p.id,
            p.asin,
            p.name,
            p.rating,
            ph.price,
            ph.original_price,
            ph.discount_percentage,
            ph.recorded_at
        FROM products p
        LEFT JOIN price_history ph
            ON p.id = ph.product_id
        ORDER BY p.id DESC
    """)

    products = cursor.fetchall()

    connection.close()

    print(f"\nTotal records found: {len(products)}")

    for product in products:

        print("\n-----------------------------")

        print("ID:", product["id"])
        print("ASIN:", product["asin"])
        print("Name:", product["name"])
        print("Rating:", product["rating"])
        print("Current Price:", product["price"])
        print("Original Price:", product["original_price"])
        print("Discount:", product["discount_percentage"], "%")
        print("Recorded At:", product["recorded_at"])


if __name__ == "__main__":
    show_products()