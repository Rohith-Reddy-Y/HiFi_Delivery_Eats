from sqlalchemy.orm import sessionmaker
from create_database import engine, MenuItem, Category  # Import your models
from datetime import datetime

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Ensure default category exists
default_category = session.query(Category).filter_by(category_id="C001").first()
if not default_category:
    # default_category = Category(category_id="C001", name="Veg")
    session.add(Category(category_id="C001", name="Veg"))
    session.add(Category(category_id="C002", name="Non-Veg"))
    session.commit()

# Check if menu items already exist
existing_items = session.query(MenuItem).count()
if existing_items > 0:
    print("Dummy data already exists. Skipping insertion.")
else:
    # Define dummy menu items
    dummy_items = [
        MenuItem(
            menu_item_id="MI001",
            name="Margherita Pizza",
            description="Classic pizza with tomato sauce, mozzarella, and basil.",
            price=299.99,
            image_url="https://photos_pixel.com/margherita.jpg",
            category_id="C001",
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
            image_url="https://photos_pixel.com/biryani.jpg",
            category_id="C002",
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
            image_url="https://photos_pixel.com/caesar_salad.jpg",
            category_id="C002",
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
            image_url="https://photos_pixel.com/brownie.jpg",
            category_id="C001",
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
