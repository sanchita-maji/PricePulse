from database.product_repository import add_product, get_all_products


product_id = add_product(
    asin="TEST123",
    name="Test Amazon Product",
    url="https://www.amazon.in/",
    category="Electronics",
    rating=4.5,
    availability="In Stock"
)

print("Inserted product ID:", product_id)

products = get_all_products()

print("\nProducts in database:")

for product in products:
    print(
        product["id"],
        product["name"],
        product["category"],
        product["rating"]
    )