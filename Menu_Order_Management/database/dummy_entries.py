from sqlalchemy.orm import sessionmaker
from create_database import engine, MenuItem, Category, Subcategory  # Import models
from datetime import datetime

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Ensure default categories exist
default_categories = {
    "IC001": "Veg",
    "IC002": "Non-Veg"
}

for category_id, name in default_categories.items():
    category = session.query(Category).filter_by(category_id=category_id).first()
    if not category:
        session.add(Category(category_id=category_id, name=name))

# Ensure default subcategories exist with proper category mapping
default_subcategories = {
    "ISC001": ("IC001", "Pizza"),  
    "ISC002": ("IC002", "Biryani"),
    "ISC003": ("IC002", "Salad"),
    "ISC004": ("IC001", "Dessert"),
    "ISC005": ("IC001", "Starter"),
    "ISC006": ("IC001", "Soups"),
    "ISC007": ("IC001", "Salads"),
    "ISC008": ("IC001", "Breads"),
    "ISC009": ("IC001", "Main Course"),
    "ISC010": ("IC001", "Beverages"),
    "ISC011": ("IC001", "Breakfast"),
    "ISC012": ("IC001", "Icecreams")
}

for subcategory_id, (category_id, name) in default_subcategories.items():
    subcategory = session.query(Subcategory).filter_by(subcategory_id=subcategory_id).first()
    if not subcategory:
        session.add(Subcategory(subcategory_id=subcategory_id, category_id=category_id, name=name))

# Commit category & subcategory additions
session.commit()

# Check if menu items already exist
existing_items = session.query(MenuItem).count()
if existing_items > 0:
    print("Dummy data already exists. Skipping insertion.")
else:
    # Define dummy menu items with subcategories
    dummy_items = [
        MenuItem(
            menu_item_id="MI001",
            name="Margherita Pizza",
            description="Classic pizza with tomato sauce, mozzarella, and basil.",
            price=299.99,
            image_url="https://HiFiDeliveryEats.com/margherita.jpg",
            category_id="IC001",
            subcategory_id="ISC001",  # Pizza
            nutrient_value="Carbs: 50g, Protein: 12g, Fat: 10g",
            calorie_count=250,
            is_best_seller=True,
            is_out_of_stock=False,
            discount_percentage=10.00,
            scheduled_update_time=datetime.utcnow()
        ),
        MenuItem(
            menu_item_id="MI002",
            name="Chicken Biryani",
            description="Aromatic basmati rice cooked with tender chicken and spices.",
            price=399.99,
            image_url="https://HiFiDeliveryEats.com/Biryani-1.jpg",
            category_id="IC002",
            subcategory_id="ISC002",  # Biryani
            nutrient_value="Carbs: 70g, Protein: 20g, Fat: 15g",
            calorie_count=450,
            is_best_seller=True,
            is_out_of_stock=False,
            discount_percentage=5.00,
            scheduled_update_time=None
        ),
        MenuItem(
            menu_item_id="MI003",
            name="Caesar Salad",
            description="Fresh romaine lettuce with Caesar dressing, croutons, and Parmesan.",
            price=199.99,
            image_url="https://HiFiDeliveryEats.com/caesar_salad.jpg",
            category_id="IC002",
            subcategory_id="ISC003",  # Salad
            nutrient_value="Carbs: 10g, Protein: 8g, Fat: 5g",
            calorie_count=150,
            is_best_seller=False,
            is_out_of_stock=False,
            discount_percentage=None,
            scheduled_update_time=None
        ),
        MenuItem(
            menu_item_id="MI004",
            name="Chocolate Brownie",
            description="Rich and gooey chocolate brownie topped with walnuts.",
            price=149.99,
            image_url="https://HiFiDeliveryEats.com/brownie.jpg",
            category_id="IC001",
            subcategory_id="ISC004",  # Dessert
            nutrient_value="Carbs: 60g, Protein: 5g, Fat: 20g",
            calorie_count=300,
            is_best_seller=True,
            is_out_of_stock=False,
            discount_percentage=15.00,
            scheduled_update_time=datetime.utcnow()
        )
    ]

    # Insert dummy data
    session.add_all(dummy_items)
    session.commit()
    print("Dummy data inserted successfully!")

# Close session
session.close()
