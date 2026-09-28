import requests

from scraper.parser import parse_product_cards


BASE_URL = "https://www.amazon.in"


def fetch_search_page(keyword, page=1):

    url = f"{BASE_URL}/s"

    params = {
        "k": keyword,
        "page": page
    }

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/140.0 Safari/537.36"
        ),
        "Accept-Language": "en-IN,en;q=0.9"
    }

    response = requests.get(
        url,
        params=params,
        headers=headers,
        timeout=15
    )

    response.raise_for_status()

    html = response.text

    print("Status code:", response.status_code)
    print("Page length:", len(html))

    with open("amazon_debug.html", "w", encoding="utf-8") as file:
        file.write(html)

    return html


def search_products(keyword, page=1):

    html = fetch_search_page(
        keyword,
        page
    )

    return parse_product_cards(html)


if __name__ == "__main__":

    products = search_products(
        "wireless headphones"
    )

    print(
        f"Found {len(products)} products"
    )

    for product in products[:5]:

        print("\n----------------")

        print(
            "Name:",
            product["name"]
        )

        print(
            "Price:",
            product["price"]
        )

        print(
            "Rating:",
            product["rating"]
        )

        print(
            "URL:",
            product["url"]
        )