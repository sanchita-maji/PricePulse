import pandas as pd
import matplotlib.pyplot as plt

from analysis.analyzer import load_latest_products


def prepare_data():
    """
    Load the latest product data and remove rows
    where price information is unavailable.
    """

    df = load_latest_products()

    df = df.dropna(
        subset=["price"]
    ).copy()

    return df


def plot_price_comparison(df):
    """
    Create a current-price comparison chart.
    """

    chart_df = (
        df.sort_values(
            "price",
            ascending=True
        )
        .head(10)
        .copy()
    )

    plt.figure(figsize=(12, 6))

    plt.barh(
        chart_df["name"].str[:35],
        chart_df["price"]
    )

    plt.xlabel("Price (₹)")
    plt.ylabel("Product")
    plt.title("Current Amazon Product Prices")

    plt.tight_layout()

    plt.show()


def plot_discount_comparison(df):
    """
    Create a discount comparison chart.
    """

    chart_df = (
        df.dropna(
            subset=["discount_percentage"]
        )
        .sort_values(
            "discount_percentage",
            ascending=True
        )
        .head(10)
        .copy()
    )

    plt.figure(figsize=(12, 6))

    plt.barh(
        chart_df["name"].str[:35],
        chart_df["discount_percentage"]
    )

    plt.xlabel("Discount (%)")
    plt.ylabel("Product")
    plt.title("Amazon Product Discounts")

    plt.tight_layout()

    plt.show()


def plot_rating_vs_price(df):
    """
    Show the relationship between product rating
    and current price.
    """

    chart_df = df.dropna(
        subset=["price", "rating"]
    ).copy()

    plt.figure(figsize=(9, 6))

    plt.scatter(
        chart_df["price"],
        chart_df["rating"]
    )

    plt.xlabel("Price (₹)")
    plt.ylabel("Rating")
    plt.title("Product Rating vs Price")

    plt.tight_layout()

    plt.show()


if __name__ == "__main__":

    dataframe = prepare_data()

    print(
        "Products available for visualization:",
        len(dataframe)
    )

    plot_price_comparison(
        dataframe
    )

    plot_discount_comparison(
        dataframe
    )

    plot_rating_vs_price(
        dataframe
    )