# DO NOT IMPORT THIS FILE INTO ANY OTHER FILE 
# BECAUSE IT WILL INSERT THE ENTRIES IN THE TABLE AGAIN AND AGAIN.

from sqlalchemy.orm import Session   # do not forget to close the session after each commit.
from create_database import * # import the class of tables (like import menu table)
from datetime import datetime

def create_session():
    """Create a new session"""
    return Session(bind=engine)

def insert_data(session):
    """Insert data into tables"""
    # Inserting data into Menu table
    menu = Menu(menu_id="M001")
    session.add(menu)

    # Inserting data into Category table
    categories = [
        Category(category_id="C001", name="Appetizers"),
        Category(category_id="C002", name="Main Course"),
        Category(category_id="C003", name="Desserts"),
        Category(category_id="C004", name="Beverages"),
        Category(category_id="C005", name="Salads")
    ]
    session.add_all(categories)

    # Inserting data into MenuItem table
    menu_items = [
        MenuItem(menu_item_id="MI001", menu_id="M001", name="Spring Rolls", description="Crispy vegetarian rolls", price=150,
                 image_url="https://github.com/AadityaRajGupta/HiFi_Delivery_Eats/blob/main/frontend/static/images/spring_rolls.jpg", category="Appetizers", nutrient_value="Low Fat", calorie_count=200,
                 is_best_seller=True, is_out_of_stock=False, scheduled_update_time=None),
        MenuItem(menu_item_id="MI002", menu_id="M001", name="Grilled Chicken", description="Juicy grilled chicken with herbs", price=350,
                 image_url="https://github.com/AadityaRajGupta/HiFi_Delivery_Eats/blob/main/frontend/static/images/grilled_chicken.jpg", category="Main Course", nutrient_value="High Protein", calorie_count=450,
                 is_best_seller=False, is_out_of_stock=False, scheduled_update_time=None),
        MenuItem(menu_item_id="MI003", menu_id="M001", name="Chocolate Cake", description="Rich and creamy chocolate cake", price=120,
                 image_url="https://github.com/AadityaRajGupta/HiFi_Delivery_Eats/blob/main/frontend/static/images/chocolate_cake.jpg", category="Desserts", nutrient_value="High Sugar", calorie_count=350,
                 is_best_seller=True, is_out_of_stock=False, scheduled_update_time=None),
        MenuItem(menu_item_id="MI004", menu_id="M001", name="Caesar Salad", description="Fresh lettuce with Caesar dressing", price=175,
                 image_url="https://github.com/AadityaRajGupta/HiFi_Delivery_Eats/blob/main/frontend/static/images/caesar_salad.jpg", category="Salads", nutrient_value="High Fiber", calorie_count=150,
                 is_best_seller=False, is_out_of_stock=False, scheduled_update_time=None),
        MenuItem(menu_item_id="MI005", menu_id="M001", name="Mango Smoothie", description="Refreshing mango smoothie", price=100,
                 image_url="https://github.com/AadityaRajGupta/HiFi_Delivery_Eats/blob/main/frontend/static/images/mango_smoothie.jpg", category="Beverages", nutrient_value="Vitamins Rich", calorie_count=180,
                 is_best_seller=True, is_out_of_stock=False, scheduled_update_time=None)
    ]
    session.add_all(menu_items)

    # Inserting data into ItemCategoryMapping table
    item_category_mappings = [
        ItemCategoryMapping(mapping_id="IC001", menu_item_id="MI001", category_id="C001"),
        ItemCategoryMapping(mapping_id="IC002", menu_item_id="MI002", category_id="C002"),
        ItemCategoryMapping(mapping_id="IC003", menu_item_id="MI003", category_id="C003"),
        ItemCategoryMapping(mapping_id="IC004", menu_item_id="MI004", category_id="C005"),
        ItemCategoryMapping(mapping_id="IC005", menu_item_id="MI005", category_id="C004")
    ]
    session.add_all(item_category_mappings)

    # Inserting data into Discount table
    discounts = [
        Discount(discount_id="D001", menu_item_id="MI001", discount_percentage=10.00, start_date=datetime(2025, 2, 1), end_date=datetime(2025, 2, 10)),
        Discount(discount_id="D002", menu_item_id="MI003", discount_percentage=15.00, start_date=datetime(2025, 2, 5), end_date=datetime(2025, 2, 15)),
        Discount(discount_id="D003", menu_item_id="MI004", discount_percentage=5.00, start_date=datetime(2025, 2, 8), end_date=datetime(2025, 2, 18)),
        Discount(discount_id="D004", menu_item_id="MI005", discount_percentage=12.00, start_date=datetime(2025, 2, 3), end_date=datetime(2025, 2, 13))
    ]
    session.add_all(discounts)

    # Inserting data into Rating table
    ratings = [
        Rating(rating_id="R001", menu_item_id="MI001", rating_value=5, review_text="Amazing!", review_date=datetime.utcnow()),
        Rating(rating_id="R002", menu_item_id="MI002", rating_value=4, review_text="Very tasty!", review_date=datetime.utcnow()),
        Rating(rating_id="R003", menu_item_id="MI003", rating_value=5, review_text="Delicious dessert!", review_date=datetime.utcnow()),
        Rating(rating_id="R004", menu_item_id="MI004", rating_value=3, review_text="Fresh but needs more flavor.", review_date=datetime.utcnow()),
        Rating(rating_id="R005", menu_item_id="MI005", rating_value=5, review_text="Perfect smoothie!", review_date=datetime.utcnow())
    ]
    session.add_all(ratings)

    # Inserting data into CustomerOrders table
    orders = [
        CustomerOrders(customer_order_id="CO001", customer_id="U001", menu_item_id="MI001", quantity=2, order_date=datetime.utcnow()),
        CustomerOrders(customer_order_id="CO002", customer_id="U002", menu_item_id="MI003", quantity=1, order_date=datetime.utcnow()),
        CustomerOrders(customer_order_id="CO003", customer_id="U003", menu_item_id="MI004", quantity=3, order_date=datetime.utcnow()),
        CustomerOrders(customer_order_id="CO004", customer_id="U004", menu_item_id="MI002", quantity=1, order_date=datetime.utcnow()),
        CustomerOrders(customer_order_id="CO005", customer_id="U005", menu_item_id="MI005", quantity=2, order_date=datetime.utcnow())
    ]
    session.add_all(orders)

    # Inserting data into PersonalizedRecommendations table
    recommendations = [
        PersonalizedRecommendations(personalized_recommendations_id="PR001", customer_id="U001", menu_item_id="MI002", recommendation_reason="Based on your previous orders"),
        PersonalizedRecommendations(personalized_recommendations_id="PR002", customer_id="U002", menu_item_id="MI001", recommendation_reason="Highly rated item"),
        PersonalizedRecommendations(personalized_recommendations_id="PR003", customer_id="U003", menu_item_id="MI004", recommendation_reason="Healthy choice recommendation"),
        PersonalizedRecommendations(personalized_recommendations_id="PR004", customer_id="U004", menu_item_id="MI003", recommendation_reason="Popular dessert recommendation"),
        PersonalizedRecommendations(personalized_recommendations_id="PR005", customer_id="U005", menu_item_id="MI005", recommendation_reason="Refreshing drink choice")
    ]
    session.add_all(recommendations)

def main():
    session = create_session()
    try:
        insert_data(session)
        session.commit()
        print("Data inserted successfully!")
    except Exception as e:
        session.rollback()
        print(f"An error occurred: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    main()# DO NOT IMPORT THIS FILE INTO ANY OTHER FILE 
# BECAUSE IT WILL INSERT THE ENTRIES IN THE TABLE AGAIN AND AGAIN.

from sqlalchemy.orm import Session   # do not forget to close the session after each commit.
from create_database import * # import the class of tables (like import menu table)
from datetime import datetime

# Creating a new session
session = Session(bind=engine)

# Inserting data into Menu table
menu = Menu(menu_id="M001")
session.add(menu)

# Inserting data into Category table
categories = [
    Category(category_id="C001", name="Appetizers"),
    Category(category_id="C002", name="Main Course"),
    Category(category_id="C003", name="Desserts"),
    Category(category_id="C004", name="Beverages"),
    Category(category_id="C005", name="Salads")
]
session.add_all(categories)

# image_path = "..\..\\frontend\static\images\spring_rolls.jpg"

# Inserting data into MenuItem table
menu_items = [
    MenuItem(menu_item_id="MI001", menu_id="M001", name="Spring Rolls", description="Crispy vegetarian rolls", price=150,
             image_url="https://github.com/AadityaRajGupta/HiFi_Delivery_Eats/blob/main/frontend/static/images/spring_rolls.jpg", category="Appetizers", nutrient_value="Low Fat", calorie_count=200,
             is_best_seller=True, is_out_of_stock=False, scheduled_update_time=None),
    MenuItem(menu_item_id="MI002", menu_id="M001", name="Grilled Chicken", description="Juicy grilled chicken with herbs", price=350,
             image_url="https://github.com/AadityaRajGupta/HiFi_Delivery_Eats/blob/main/frontend/static/images/grilled_chicken.jpg", category="Main Course", nutrient_value="High Protein", calorie_count=450,
             is_best_seller=False, is_out_of_stock=False, scheduled_update_time=None),
    MenuItem(menu_item_id="MI003", menu_id="M001", name="Chocolate Cake", description="Rich and creamy chocolate cake", price=120,
             image_url="https://github.com/AadityaRajGupta/HiFi_Delivery_Eats/blob/main/frontend/static/images/chocolate_cake.jpg", category="Desserts", nutrient_value="High Sugar", calorie_count=350,
             is_best_seller=True, is_out_of_stock=False, scheduled_update_time=None),
    MenuItem(menu_item_id="MI004", menu_id="M001", name="Caesar Salad", description="Fresh lettuce with Caesar dressing", price=175,
             image_url="https://github.com/AadityaRajGupta/HiFi_Delivery_Eats/blob/main/frontend/static/images/caesar_salad.jpg", category="Salads", nutrient_value="High Fiber", calorie_count=150,
             is_best_seller=False, is_out_of_stock=False, scheduled_update_time=None),
    MenuItem(menu_item_id="MI005", menu_id="M001", name="Mango Smoothie", description="Refreshing mango smoothie", price=100,
             image_url="https://github.com/AadityaRajGupta/HiFi_Delivery_Eats/blob/main/frontend/static/images/mango_smoothie.jpg", category="Beverages", nutrient_value="Vitamins Rich", calorie_count=180,
             is_best_seller=True, is_out_of_stock=False, scheduled_update_time=None)
]
session.add_all(menu_items)

# Inserting data into ItemCategoryMapping table
item_category_mappings = [
    ItemCategoryMapping(mapping_id="IC001", menu_item_id="MI001", category_id="C001"),
    ItemCategoryMapping(mapping_id="IC002", menu_item_id="MI002", category_id="C002"),
    ItemCategoryMapping(mapping_id="IC003", menu_item_id="MI003", category_id="C003"),
    ItemCategoryMapping(mapping_id="IC004", menu_item_id="MI004", category_id="C005"),
    ItemCategoryMapping(mapping_id="IC005", menu_item_id="MI005", category_id="C004")
]
session.add_all(item_category_mappings)

# Inserting data into Discount table
discounts = [
    Discount(discount_id="D001", menu_item_id="MI001", discount_percentage=10.00, start_date=datetime(2025, 2, 1), end_date=datetime(2025, 2, 10)),
    Discount(discount_id="D002", menu_item_id="MI003", discount_percentage=15.00, start_date=datetime(2025, 2, 5), end_date=datetime(2025, 2, 15)),
    Discount(discount_id="D003", menu_item_id="MI004", discount_percentage=5.00, start_date=datetime(2025, 2, 8), end_date=datetime(2025, 2, 18)),
    Discount(discount_id="D004", menu_item_id="MI005", discount_percentage=12.00, start_date=datetime(2025, 2, 3), end_date=datetime(2025, 2, 13))
]
session.add_all(discounts)

# Inserting data into Rating table
ratings = [
    Rating(rating_id="R001", menu_item_id="MI001", rating_value=5, review_text="Amazing!", review_date=datetime.utcnow()),
    Rating(rating_id="R002", menu_item_id="MI002", rating_value=4, review_text="Very tasty!", review_date=datetime.utcnow()),
    Rating(rating_id="R003", menu_item_id="MI003", rating_value=5, review_text="Delicious dessert!", review_date=datetime.utcnow()),
    Rating(rating_id="R004", menu_item_id="MI004", rating_value=3, review_text="Fresh but needs more flavor.", review_date=datetime.utcnow()),
    Rating(rating_id="R005", menu_item_id="MI005", rating_value=5, review_text="Perfect smoothie!", review_date=datetime.utcnow())
]
session.add_all(ratings)

# Inserting data into CustomerOrders table
orders = [
    CustomerOrders(customer_order_id="CO001", customer_id="U001", menu_item_id="MI001", quantity=2, order_date=datetime.utcnow()),
    CustomerOrders(customer_order_id="CO002", customer_id="U002", menu_item_id="MI003", quantity=1, order_date=datetime.utcnow()),
    CustomerOrders(customer_order_id="CO003", customer_id="U003", menu_item_id="MI004", quantity=3, order_date=datetime.utcnow()),
    CustomerOrders(customer_order_id="CO004", customer_id="U004", menu_item_id="MI002", quantity=1, order_date=datetime.utcnow()),
    CustomerOrders(customer_order_id="CO005", customer_id="U005", menu_item_id="MI005", quantity=2, order_date=datetime.utcnow())
]
session.add_all(orders)

# Inserting data into PersonalizedRecommendations table
recommendations = [
    PersonalizedRecommendations(personalized_recommendations_id="PR001", customer_id="U001", menu_item_id="MI002", recommendation_reason="Based on your previous orders"),
    PersonalizedRecommendations(personalized_recommendations_id="PR002", customer_id="U002", menu_item_id="MI001", recommendation_reason="Highly rated item"),
    PersonalizedRecommendations(personalized_recommendations_id="PR003", customer_id="U003", menu_item_id="MI004", recommendation_reason="Healthy choice recommendation"),
    PersonalizedRecommendations(personalized_recommendations_id="PR004", customer_id="U004", menu_item_id="MI003", recommendation_reason="Popular dessert recommendation"),
    PersonalizedRecommendations(personalized_recommendations_id="PR005", customer_id="U005", menu_item_id="MI005", recommendation_reason="Refreshing drink choice")
]
session.add_all(recommendations)

# Commit the transaction
session.commit()
print("Data inserted successfully!")

# Closing the session
session.close()

'''
BASICS:

now using the session class you can create a session object
this session object will help us to insert into our database
session = Session(bind=engine)
ARG = User(
    username='ARG',
    email_address='ARG@example.com'
)
session.add_all([ARG])
session.commit()
session.close() # close the session object so we can connect again 

'''