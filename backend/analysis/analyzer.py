import pandas as pd
import numpy as np

from database.db import get_connection


def load_latest_products():
    """
    Load the latest price observation for each product.
    """

    connection = get_connection()

    query = """
        SELECT
            p.id,
            p.asin,
            p.name,
            p.category,
            p.rating,
            p.availability,
            ph.price,
            ph.original_price,
            ph.discount_percentage,
            ph.recorded_at
        FROM products p
        LEFT JOIN price_history ph
            ON ph.id = (
                SELECT ph2.id
                FROM price_history ph2
                WHERE ph2.product_id = p.id
                ORDER BY ph2.recorded_at DESC, ph2.id DESC
                LIMIT 1
            )
        ORDER BY p.id
    """

    df = pd.read_sql_query(query, connection)

    connection.close()

    return df


def calculate_summary(df):
    """
    Calculate dashboard summary statistics.
    """

    total_products = len(df)

    average_price = (
        df["price"].dropna().mean()
        if df["price"].notna().any()
        else 0
    )

    average_discount = (
        df["discount_percentage"].dropna().mean()
        if df["discount_percentage"].notna().any()
        else 0
    )

    average_rating = (
        df["rating"].dropna().mean()
        if df["rating"].notna().any()
        else 0
    )

    return {
        "total_products": total_products,
        "average_price": round(average_price, 2),
        "average_discount": round(average_discount, 2),
        "average_rating": round(average_rating, 2),
    }


def calculate_deal_score(df):
    """
    Calculate a deal score using:
    60% discount
    40% rating
    """

    result = df.copy()

    result["discount_score"] = (
        result["discount_percentage"]
        .fillna(0)
        .clip(0, 100)
    )

    result["rating_score"] = (
        result["rating"]
        .fillna(0)
        .clip(0, 5)
        / 5
    ) * 100

    result["deal_score"] = (
        result["discount_score"] * 0.60
        + result["rating_score"] * 0.40
    )

    result["deal_score"] = np.round(
        result["deal_score"],
        2
    )

    return result


def get_best_deals(df, limit=5):
    """
    Return products with the highest deal scores.
    """

    scored = calculate_deal_score(df)

    return (
        scored
        .sort_values(
            by="deal_score",
            ascending=False
        )
        .head(limit)
    )


def get_lowest_price_product(df):
    """
    Find the product with the lowest current price.
    """

    valid = df.dropna(
        subset=["price"]
    )

    if valid.empty:
        return None

    return valid.loc[
        valid["price"].idxmin()
    ]


def get_highest_discount_product(df):
    """
    Find the product with the highest available discount.
    """

    valid = df.dropna(
        subset=["discount_percentage"]
    )

    if valid.empty:
        return None

    return valid.loc[
        valid["discount_percentage"].idxmax()
    ]


def print_report(df):
    """
    Print a clean analysis report.
    """

    summary = calculate_summary(df)

    best_deals = get_best_deals(
        df,
        limit=5
    )

    cheapest = get_lowest_price_product(df)

    highest_discount = get_highest_discount_product(df)

    print("\n" + "=" * 60)
    print("              AMAZON ANALYZER REPORT")
    print("=" * 60)

    print("\nSUMMARY")
    print("-" * 60)

    print(
        f"Total products       : "
        f"{summary['total_products']}"
    )

    print(
        f"Average price        : "
        f"₹{summary['average_price']:.2f}"
    )

    print(
        f"Average discount     : "
        f"{summary['average_discount']:.2f}%"
    )

    print(
        f"Average rating       : "
        f"{summary['average_rating']:.2f}/5"
    )

    print("\nLOWEST PRICE")
    print("-" * 60)

    if cheapest is not None:

        print(
            f"{cheapest['name']}"
        )

        print(
            f"Price: ₹{cheapest['price']:.2f}"
        )

    print("\nHIGHEST DISCOUNT")
    print("-" * 60)

    if highest_discount is not None:

        print(
            f"{highest_discount['name']}"
        )

        print(
            "Discount: "
            f"{highest_discount['discount_percentage']:.2f}%"
        )

    print("\nBEST DEALS")
    print("-" * 60)

    for index, (_, product) in enumerate(
        best_deals.iterrows(),
        start=1
    ):

        print(
            f"{index}. "
            f"{product['name'][:70]}"
        )

        print(
            f"   Price: ₹{product['price']:.2f}"
        )

        if pd.notna(
            product["discount_percentage"]
        ):

            print(
                "   Discount: "
                f"{product['discount_percentage']:.2f}%"
            )

        else:

            print(
                "   Discount: Not available"
            )

        print(
            f"   Rating: {product['rating']}/5"
        )

        print(
            f"   Deal Score: "
            f"{product['deal_score']:.2f}/100"
        )

    print("\n" + "=" * 60)


if __name__ == "__main__":

    dataframe = load_latest_products()

    print_report(
        dataframe
    )