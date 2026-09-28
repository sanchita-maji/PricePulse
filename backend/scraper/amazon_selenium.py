from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from scraper.parser import parse_product_cards
from database.product_repository import save_product


BASE_URL = "https://www.amazon.in"


def fetch_search_page(keyword, page=1):
    """
    Open an Amazon search page using Selenium
    and return the rendered HTML.
    """

    driver = webdriver.Chrome()

    try:

        url = f"{BASE_URL}/s?k={keyword}&page={page}"

        print("\nOpening Amazon...")
        print("Search:", keyword)

        driver.get(url)

        print("Waiting for Amazon product results...")

        try:

            WebDriverWait(
                driver,
                20
            ).until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        'div[data-component-type="s-search-result"]'
                    )
                )
            )

            print(
                "Amazon product results detected."
            )

        except Exception:

            print(
                "\nAmazon may be showing a verification page."
            )

            print(
                "Please complete the verification "
                "in the Chrome window."
            )

            input(
                "\nAfter the product results appear, "
                "press ENTER here..."
            )

        html = driver.page_source

        print(
            "Page length:",
            len(html)
        )

        with open(
            "amazon_selenium_debug.html",
            "w",
            encoding="utf-8"
        ) as file:

            file.write(html)

        return html

    finally:

        driver.quit()


def search_products(
    keyword,
    category,
    page=1
):
    """
    Search Amazon and parse products.
    """

    html = fetch_search_page(
        keyword,
        page
    )

    products = parse_product_cards(
        html
    )

    print(
        "Products parsed:",
        len(products)
    )

    # Store the category that belongs
    # to this search.
    for product in products:

        product["category"] = category

    return products


def save_scraped_products(
    products
):
    """
    Save scraped products into the database.
    """

    saved_count = 0

    for product in products[:10]:

        print(
            "\n-----------------------------"
        )

        print(
            "ASIN:",
            product.get("asin")
        )

        print(
            "Name:",
            product.get("name")
        )

        print(
            "Price:",
            product.get("price")
        )

        print(
            "Original Price:",
            product.get("original_price")
        )

        print(
            "Rating:",
            product.get("rating")
        )

        print(
            "Category:",
            product.get("category")
        )

        print(
            "URL:",
            product.get("url")
        )

        # Skip incomplete products.

        if not product.get("name"):

            print(
                "Skipped: product name is missing."
            )

            continue

        if not product.get("url"):

            print(
                "Skipped: product URL is missing."
            )

            continue

        try:

            result = save_product(
                product
            )

            print(
                "Discount:",
                result["discount_percentage"],
                "%"
            )

            print(
                "Database Product ID:",
                result["product_id"]
            )

            print(
                "Saved to database!"
            )

            saved_count += 1

        except Exception as error:

            print(
                "Could not save this product:"
            )

            print(
                error
            )

    return saved_count


def scrape_category(
    keyword,
    category
):
    """
    Scrape and save one category.
    """

    print(
        "\n"
        + "=" * 60
    )

    print(
        f"SCRAPING CATEGORY: {category}"
    )

    print(
        f"SEARCH KEYWORD: {keyword}"
    )

    print(
        "=" * 60
    )

    products = search_products(
        keyword,
        category
    )

    print(
        f"\nFound {len(products)} products "
        f"for {category}"
    )

    saved_count = save_scraped_products(
        products
    )

    print(
        f"\n{category}: "
        f"saved {saved_count} products."
    )

    return saved_count


if __name__ == "__main__":

    # Category -> Amazon search keyword
    categories = {
        "Electronics": "wireless headphones",
        "Fashion": "women dresses",
        "Home": "home decor",
        "Beauty": "skincare products",
        "Books": "books"
    }

    total_saved = 0

    for category, keyword in categories.items():

        saved = scrape_category(
            keyword,
            category
        )

        total_saved += saved

    print(
        "\n"
        + "=" * 60
    )

    print(
        "MULTI-CATEGORY SCRAPING COMPLETE"
    )

    print(
        f"Total products saved in this run: "
        f"{total_saved}"
    )

    print(
        "=" * 60
    )