'''
from sqlalchemy.orm import sessionmaker
from create_database import engine, MenuItem  # Import models
from datetime import datetime

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Check if menu items already exist
existing_items = session.query(MenuItem).filter(MenuItem.menu_item_id >= "MI053").count()
if existing_items > 0:
    print("Dummy data for ice creams already exists. Skipping insertion.")
else:
    # Define dummy menu items for Icecreams
    dummy_items = [
        MenuItem(
            menu_item_id="MI053",
            name="Vanilla Icecream",
            description="Classic vanilla flavor",
            price=60.00,
            image_url="https://HiFiDeliveryEats.com/Vanilla_Icecream.jpg",
            category_id="IC001",
            subcategory_id="ISC011",
            nutrient_value="Carbs: 30g, Protein: 5g, Fat: 8g",
            calorie_count=200,
            is_best_seller=True,
            is_out_of_stock=False,
            discount_percentage=None,
            scheduled_update_time=None
        ),
        MenuItem(
            menu_item_id="MI054",
            name="Chocolate Icecream",
            description="Rich chocolate flavor",
            price=70.00,
            image_url="https://HiFiDeliveryEats.com/Chocolate_Icecream.jpg",
            category_id="IC001",
            subcategory_id="ISC011",
            nutrient_value="Carbs: 35g, Protein: 6g, Fat: 10g",
            calorie_count=220,
            is_best_seller=True,
            is_out_of_stock=False,
            discount_percentage=5.00,
            scheduled_update_time=None
        ),
        MenuItem(
            menu_item_id="MI055",
            name="Strawberry Icecream",
            description="Fresh strawberry flavor",
            price=80.00,
            image_url="https://HiFiDeliveryEats.com/Strawberry_Icecream.jpg",
            category_id="IC001",
            subcategory_id="ISC011",
            nutrient_value="Carbs: 32g, Protein: 5g, Fat: 9g",
            calorie_count=210,
            is_best_seller=False,
            is_out_of_stock=False,
            discount_percentage=None,
            scheduled_update_time=None
        ),
        MenuItem(
            menu_item_id="MI056",
            name="Mango Sorbet",
            description="Refreshing mango ice dessert",
            price=75.00,
            image_url="https://HiFiDeliveryEats.com/Mango_Sorbet.jpg",
            category_id="IC001",
            subcategory_id="ISC011",
            nutrient_value="Carbs: 28g, Protein: 3g, Fat: 5g",
            calorie_count=180,
            is_best_seller=False,
            is_out_of_stock=False,
            discount_percentage=10.00,
            scheduled_update_time=None
        ),
        MenuItem(
            menu_item_id="MI057",
            name="Butterscotch Icecream",
            description="Creamy with crunchy bits",
            price=70.00,
            image_url="https://HiFiDeliveryEats.com/Butterscotch_Icecream.jpg",
            category_id="IC001",
            subcategory_id="ISC011",
            nutrient_value="Carbs: 34g, Protein: 5g, Fat: 9g",
            calorie_count=215,
            is_best_seller=False,
            is_out_of_stock=False,
            discount_percentage=5.00,
            scheduled_update_time=None
        ),
        MenuItem(
            menu_item_id="MI058",
            name="Rocky Road Icecream",
            description="Chocolate with marshmallows (contains gelatin)",
            price=85.00,
            image_url="https://HiFiDeliveryEats.com/Rocky_Road_Icecream.jpg",
            category_id="IC002",  # Non-Veg due to gelatin
            subcategory_id="ISC011",
            nutrient_value="Carbs: 40g, Protein: 7g, Fat: 12g",
            calorie_count=250,
            is_best_seller=True,
            is_out_of_stock=False,
            discount_percentage=7.00,
            scheduled_update_time=None
        )
    ]

    # Insert dummy data
    session.add_all(dummy_items)
    session.commit()
    print("Dummy data for ice creams inserted successfully!")

# Close session
session.close()
'''

'''
from sqlalchemy.orm import sessionmaker
from create_database import engine, MenuItem, Category, Subcategory  # Import models

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Ensure Biryani category and subcategory exist
biryani_category_id = "IC004"  # Biryani Category
subcategory_biryani_id = "ISC010"  # Biryani Subcategory

category_biryani = session.query(Category).filter_by(category_id=biryani_category_id).first()
if not category_biryani:
    session.add(Category(category_id=biryani_category_id, name="Biryani"))

subcategory_biryani = session.query(Subcategory).filter_by(subcategory_id=subcategory_biryani_id).first()
if not subcategory_biryani:
    session.add(Subcategory(subcategory_id=subcategory_biryani_id, category_id=biryani_category_id, name="Biryani"))

# Commit category & subcategory additions
session.commit()

# Check if biryani menu items already exist
existing_biryani = session.query(MenuItem).filter(MenuItem.subcategory_id == subcategory_biryani_id).count()
if existing_biryani < 0:
    print("Dummy data for Biryani already exists. Skipping insertion.")
else:
    # Define dummy biryani menu items
    dummy_items_biryani = [
        MenuItem(
            menu_item_id="MI046",
            name="Chicken Biryani",
            description="Spicy chicken biryani",
            price=200.00,
            image_url="https://HiFiDeliveryEats.com/Chicken_Biryani.jpg",
            category_id=biryani_category_id,
            subcategory_id=subcategory_biryani_id,
            nutrient_value="Protein: 20g, Carbs: 50g, Fat: 10g",
            calorie_count=500,
            is_best_seller=True,
            is_out_of_stock=False,
            discount_percentage=None,
            scheduled_update_time=None
        ),
        MenuItem(
            menu_item_id="MI047",
            name="Veg Biryani",
            description="Vegetable biryani",
            price=150.00,
            image_url="https://HiFiDeliveryEats.com/Veg_Biryani.jpg",
            category_id=biryani_category_id,
            subcategory_id=subcategory_biryani_id,
            nutrient_value="Protein: 8g, Carbs: 60g, Fat: 5g",
            calorie_count=450,
            is_best_seller=False,
            is_out_of_stock=False,
            discount_percentage=None,
            scheduled_update_time=None
        ),
        MenuItem(
            menu_item_id="MI048",
            name="Mutton Biryani",
            description="Spicy mutton biryani",
            price=250.00,
            image_url="https://HiFiDeliveryEats.com/Mutton_Biryani.jpg",
            category_id=biryani_category_id,
            subcategory_id=subcategory_biryani_id,
            nutrient_value="Protein: 25g, Carbs: 50g, Fat: 15g",
            calorie_count=550,
            is_best_seller=True,
            is_out_of_stock=False,
            discount_percentage=None,
            scheduled_update_time=None
        ),
        MenuItem(
            menu_item_id="MI049",
            name="Paneer Biryani",
            description="Biryani with paneer chunks",
            price=170.00,
            image_url="https://HiFiDeliveryEats.com/Paneer_Biryani.jpg",
            category_id=biryani_category_id,
            subcategory_id=subcategory_biryani_id,
            nutrient_value="Protein: 15g, Carbs: 55g, Fat: 8g",
            calorie_count=480,
            is_best_seller=False,
            is_out_of_stock=False,
            discount_percentage=None,
            scheduled_update_time=None
        ),
        MenuItem(
            menu_item_id="MI050",
            name="Mushroom Biryani",
            description="Biryani with fresh mushrooms",
            price=160.00,
            image_url="https://HiFiDeliveryEats.com/Mushroom_Biryani.jpg",
            category_id=biryani_category_id,
            subcategory_id=subcategory_biryani_id,
            nutrient_value="Protein: 10g, Carbs: 50g, Fat: 6g",
            calorie_count=460,
            is_best_seller=False,
            is_out_of_stock=False,
            discount_percentage=None,
            scheduled_update_time=None
        ),
        MenuItem(
            menu_item_id="MI051",
            name="Fish Biryani",
            description="Spicy biryani with fish",
            price=230.00,
            image_url="https://HiFiDeliveryEats.com/Fish_Biryani.jpg",
            category_id=biryani_category_id,
            subcategory_id=subcategory_biryani_id,
            nutrient_value="Protein: 22g, Carbs: 50g, Fat: 12g",
            calorie_count=530,
            is_best_seller=False,
            is_out_of_stock=False,
            discount_percentage=None,
            scheduled_update_time=None
        ),
        MenuItem(
            menu_item_id="MI052",
            name="Special Hyderabadi Biryani",
            description="Traditional Hyderabadi dum biryani with aromatic spices",
            price=260.00,
            image_url="https://HiFiDeliveryEats.com/Hyderabadi_Biryani.jpg",
            category_id=biryani_category_id,
            subcategory_id=subcategory_biryani_id,
            nutrient_value="Protein: 28g, Carbs: 55g, Fat: 14g",
            calorie_count=600,
            is_best_seller=True,
            is_out_of_stock=False,
            discount_percentage=10.00,
            scheduled_update_time=None
        )
    ]
    
    # Insert dummy biryani data
    session.add_all(dummy_items_biryani)
    session.commit()
    print("Dummy data for Biryani inserted successfully!")

# Close session
session.close()
'''

'''
from sqlalchemy.orm import sessionmaker
from create_database import engine, MenuItem, Category, Subcategory  # Import models
from datetime import datetime

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Ensure Breakfast category and subcategory exist
breakfast_category_id = "IC004"  # Breakfast Category
subcategory_breakfast_id = "ISC010"  # Breakfast Subcategory

category_breakfast = session.query(Category).filter_by(category_id=breakfast_category_id).first()
if not category_breakfast:
    session.add(Category(category_id=breakfast_category_id, name="Breakfast"))

subcategory_breakfast = session.query(Subcategory).filter_by(subcategory_id=subcategory_breakfast_id).first()
if not subcategory_breakfast:
    session.add(Subcategory(subcategory_id=subcategory_breakfast_id, category_id=breakfast_category_id, name="Breakfast"))

# Commit category & subcategory additions
session.commit()

# Check if breakfast menu items already exist
existing_breakfast = session.query(MenuItem).filter(MenuItem.subcategory_id == subcategory_breakfast_id).count()
if existing_breakfast > 0:
    print("Dummy data for Breakfast already exists. Skipping insertion.")
else:
    # Define dummy breakfast menu items
    dummy_items_breakfast = [
        MenuItem(
            menu_item_id="MI040",
            name="Masala Dosa",
            description="Crispy rice crepe with potato filling",
            price=50.00,
            image_url="https://HiFiDeliveryEats.com/Masala_Dosa.jpg",
            category_id=breakfast_category_id,
            subcategory_id=subcategory_breakfast_id,
            nutrient_value="Protein: 4g, Carbs: 40g, Fat: 5g",
            calorie_count=200,
            is_best_seller=True,
            is_out_of_stock=False,
            discount_percentage=None,
            scheduled_update_time=None
        ),
        MenuItem(
            menu_item_id="MI041",
            name="Poha",
            description="Flattened rice with spices and vegetables",
            price=40.00,
            image_url="https://HiFiDeliveryEats.com/Poha.jpg",
            category_id=breakfast_category_id,
            subcategory_id=subcategory_breakfast_id,
            nutrient_value="Protein: 3g, Carbs: 35g, Fat: 3g",
            calorie_count=180,
            is_best_seller=False,
            is_out_of_stock=False,
            discount_percentage=None,
            scheduled_update_time=None
        ),
        MenuItem(
            menu_item_id="MI042",
            name="Idli Sambar",
            description="Steamed rice cakes with lentil soup",
            price=45.00,
            image_url="https://HiFiDeliveryEats.com/Idli_Sambar.jpg",
            category_id=breakfast_category_id,
            subcategory_id=subcategory_breakfast_id,
            nutrient_value="Protein: 5g, Carbs: 38g, Fat: 2g",
            calorie_count=190,
            is_best_seller=True,
            is_out_of_stock=False,
            discount_percentage=5.00,
            scheduled_update_time=None
        ),
        MenuItem(
            menu_item_id="MI043",
            name="Cheese Omelette",
            description="Fluffy eggs with melted cheese",
            price=60.00,
            image_url="https://HiFiDeliveryEats.com/Cheese_Omelette.jpg",
            category_id=breakfast_category_id,
            subcategory_id=subcategory_breakfast_id,
            nutrient_value="Protein: 10g, Carbs: 2g, Fat: 10g",
            calorie_count=150,
            is_best_seller=False,
            is_out_of_stock=False,
            discount_percentage=None,
            scheduled_update_time=None
        ),
        MenuItem(
            menu_item_id="MI044",
            name="Chicken Sausage",
            description="Grilled sausages with toast",
            price=70.00,
            image_url="https://HiFiDeliveryEats.com/Chicken_Sausage.jpg",
            category_id=breakfast_category_id,
            subcategory_id=subcategory_breakfast_id,
            nutrient_value="Protein: 12g, Carbs: 5g, Fat: 15g",
            calorie_count=220,
            is_best_seller=False,
            is_out_of_stock=False,
            discount_percentage=None,
            scheduled_update_time=None
        ),
        MenuItem(
            menu_item_id="MI045",
            name="Egg Bhurji",
            description="Spicy scrambled eggs with spices",
            price=55.00,
            image_url="https://HiFiDeliveryEats.com/Egg_Bhurji.jpg",
            category_id=breakfast_category_id,
            subcategory_id=subcategory_breakfast_id,
            nutrient_value="Protein: 8g, Carbs: 4g, Fat: 7g",
            calorie_count=170,
            is_best_seller=True,
            is_out_of_stock=False,
            discount_percentage=5.00,
            scheduled_update_time=None
        )
    ]
    
    # Insert dummy breakfast data
    session.add_all(dummy_items_breakfast)
    session.commit()
    print("Dummy data for Breakfast inserted successfully!")

# Close session
session.close()
'''

'''
from sqlalchemy.orm import sessionmaker
from create_database import engine, MenuItem, Category, Subcategory  # Import models
from datetime import datetime

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Ensure Beverages category and subcategory exist
beverages_category_id = "IC003"  # Beverages Category
subcategory_beverages_id = "ISC009"  # Beverages Subcategory

category_beverages = session.query(Category).filter_by(category_id=beverages_category_id).first()
if not category_beverages:
    session.add(Category(category_id=beverages_category_id, name="Beverages"))

subcategory_beverages = session.query(Subcategory).filter_by(subcategory_id=subcategory_beverages_id).first()
if not subcategory_beverages:
    session.add(Subcategory(subcategory_id=subcategory_beverages_id, category_id=beverages_category_id, name="Beverages"))

# Commit category & subcategory additions
session.commit()

# Check if beverages menu items already exist
existing_beverages = session.query(MenuItem).filter(MenuItem.subcategory_id == subcategory_beverages_id).count()
if existing_beverages > 0:
    print("Dummy data for Beverages already exists. Skipping insertion.")
else:
    # Define dummy beverages menu items
    dummy_items_beverages = [
        MenuItem(
            menu_item_id="MI034",
            name="Mango Lassi",
            description="Sweet yogurt-based mango drink",
            price=60.00,
            image_url="https://HiFiDeliveryEats.com/Mango_Lassi.jpg",
            category_id=beverages_category_id,
            subcategory_id=subcategory_beverages_id,
            nutrient_value="Protein: 5g, Carbs: 30g, Fat: 4g",
            calorie_count=180,
            is_best_seller=True,
            is_out_of_stock=False,
            discount_percentage=5.00,
            scheduled_update_time=None
        ),
        MenuItem(
            menu_item_id="MI035",
            name="Lemonade",
            description="Refreshing lemon drink",
            price=40.00,
            image_url="https://HiFiDeliveryEats.com/Lemonade.jpg",
            category_id=beverages_category_id,
            subcategory_id=subcategory_beverages_id,
            nutrient_value="Protein: 0g, Carbs: 25g, Fat: 0g",
            calorie_count=100,
            is_best_seller=False,
            is_out_of_stock=False,
            discount_percentage=None,
            scheduled_update_time=None
        ),
        MenuItem(
            menu_item_id="MI036",
            name="Mint Cooler",
            description="Chilled mint and lime drink",
            price=50.00,
            image_url="https://HiFiDeliveryEats.com/Mint_Cooler.jpg",
            category_id=beverages_category_id,
            subcategory_id=subcategory_beverages_id,
            nutrient_value="Protein: 0g, Carbs: 20g, Fat: 0g",
            calorie_count=90,
            is_best_seller=False,
            is_out_of_stock=False,
            discount_percentage=None,
            scheduled_update_time=None
        ),
        MenuItem(
            menu_item_id="MI037",
            name="Iced Tea",
            description="Cold tea with lemon flavor",
            price=45.00,
            image_url="https://HiFiDeliveryEats.com/Iced_Tea.jpg",
            category_id=beverages_category_id,
            subcategory_id=subcategory_beverages_id,
            nutrient_value="Protein: 0g, Carbs: 18g, Fat: 0g",
            calorie_count=80,
            is_best_seller=False,
            is_out_of_stock=False,
            discount_percentage=None,
            scheduled_update_time=None
        ),
        MenuItem(
            menu_item_id="MI038",
            name="Coconut Water",
            description="Fresh and hydrating coconut drink",
            price=55.00,
            image_url="https://HiFiDeliveryEats.com/Coconut_Water.jpg",
            category_id=beverages_category_id,
            subcategory_id=subcategory_beverages_id,
            nutrient_value="Protein: 1g, Carbs: 10g, Fat: 0g",
            calorie_count=50,
            is_best_seller=True,
            is_out_of_stock=False,
            discount_percentage=None,
            scheduled_update_time=None
        ),
        MenuItem(
            menu_item_id="MI039",
            name="Orange Juice",
            description="Freshly squeezed orange juice",
            price=50.00,
            image_url="https://HiFiDeliveryEats.com/Orange_Juice.jpg",
            category_id=beverages_category_id,
            subcategory_id=subcategory_beverages_id,
            nutrient_value="Protein: 1g, Carbs: 22g, Fat: 0g",
            calorie_count=90,
            is_best_seller=True,
            is_out_of_stock=False,
            discount_percentage=None,
            scheduled_update_time=None
        )
    ]
    
    # Insert dummy beverages data
    session.add_all(dummy_items_beverages)
    session.commit()
    print("Dummy data for Beverages inserted successfully!")

# Close session
session.close()
'''

'''
from sqlalchemy.orm import sessionmaker
from create_database import engine, MenuItem, Category, Subcategory  # Import models
from datetime import datetime

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Ensure Main Course category exists
veg_category_id = "IC001"  # Veg Category
non_veg_category_id = "IC002"  # Non-Veg Category
subcategory_id = "ISC008"  # Main Course Subcategory

category_veg = session.query(Category).filter_by(category_id=veg_category_id).first()
if not category_veg:
    session.add(Category(category_id=veg_category_id, name="Veg"))

category_non_veg = session.query(Category).filter_by(category_id=non_veg_category_id).first()
if not category_non_veg:
    session.add(Category(category_id=non_veg_category_id, name="Non-Veg"))

subcategory = session.query(Subcategory).filter_by(subcategory_id=subcategory_id).first()
if not subcategory:
    session.add(Subcategory(subcategory_id=subcategory_id, category_id=veg_category_id, name="Main Course"))

# Commit category & subcategory additions
session.commit()

# Check if menu items already exist
existing_items = session.query(MenuItem).filter(MenuItem.subcategory_id == subcategory_id).count()
if existing_items > 0:
    print("Dummy data for Main Course already exists. Skipping insertion.")
else:
    # Define dummy menu items
    dummy_items = [
        MenuItem(
            menu_item_id="MI028",
            name="Paneer Butter Masala",
            description="Paneer in rich tomato gravy",
            price=220.00,
            image_url="https://HiFiDeliveryEats.com/Paneer_Butter_Masala.jpg",
            category_id=veg_category_id,
            subcategory_id=subcategory_id,
            nutrient_value="Protein: 12g, Carbs: 20g, Fat: 18g",
            calorie_count=320,
            is_best_seller=True,
            is_out_of_stock=False,
            discount_percentage=5.00,
            scheduled_update_time=None
        ),
        MenuItem(
            menu_item_id="MI029",
            name="Dal Makhani",
            description="Creamy black lentils with butter",
            price=180.00,
            image_url="https://HiFiDeliveryEats.com/Dal_Makhani.jpg",
            category_id=veg_category_id,
            subcategory_id=subcategory_id,
            nutrient_value="Protein: 10g, Carbs: 25g, Fat: 15g",
            calorie_count=290,
            is_best_seller=False,
            is_out_of_stock=False,
            discount_percentage=None,
            scheduled_update_time=None
        ),
        MenuItem(
            menu_item_id="MI030",
            name="Vegetable Korma",
            description="Mixed veggies in creamy gravy",
            price=190.00,
            image_url="https://HiFiDeliveryEats.com/Vegetable_Korma.jpg",
            category_id=veg_category_id,
            subcategory_id=subcategory_id,
            nutrient_value="Protein: 8g, Carbs: 22g, Fat: 12g",
            calorie_count=280,
            is_best_seller=False,
            is_out_of_stock=False,
            discount_percentage=8.00,
            scheduled_update_time=None
        ),
        MenuItem(
            menu_item_id="MI031",
            name="Butter Chicken",
            description="Chicken in creamy tomato sauce",
            price=250.00,
            image_url="https://HiFiDeliveryEats.com/Butter_Chicken.jpg",
            category_id=non_veg_category_id,
            subcategory_id=subcategory_id,
            nutrient_value="Protein: 22g, Carbs: 15g, Fat: 20g",
            calorie_count=350,
            is_best_seller=True,
            is_out_of_stock=False,
            discount_percentage=10.00,
            scheduled_update_time=None
        ),
        MenuItem(
            menu_item_id="MI032",
            name="Mutton Rogan Josh",
            description="Spicy mutton curry",
            price=280.00,
            image_url="https://HiFiDeliveryEats.com/Mutton_Rogan_Josh.jpg",
            category_id=non_veg_category_id,
            subcategory_id=subcategory_id,
            nutrient_value="Protein: 25g, Carbs: 10g, Fat: 22g",
            calorie_count=400,
            is_best_seller=False,
            is_out_of_stock=False,
            discount_percentage=None,
            scheduled_update_time=None
        ),
        MenuItem(
            menu_item_id="MI033",
            name="Fish Curry",
            description="Fish in spicy coconut gravy",
            price=260.00,
            image_url="https://HiFiDeliveryEats.com/Fish_Curry.jpg",
            category_id=non_veg_category_id,
            subcategory_id=subcategory_id,
            nutrient_value="Protein: 20g, Carbs: 12g, Fat: 18g",
            calorie_count=330,
            is_best_seller=True,
            is_out_of_stock=False,
            discount_percentage=12.00,
            scheduled_update_time=None
        )
    ]
    
    # Insert dummy data
    session.add_all(dummy_items)
    session.commit()
    print("Dummy data for Main Course inserted successfully!")

# Close session
session.close()
'''

'''
from sqlalchemy.orm import sessionmaker
from create_database import engine, MenuItem, Category, Subcategory  # Import models
from datetime import datetime

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Ensure Breads category exists
category_id = "IC001"  # Veg Category
subcategory_id = "ISC007"  # Breads Subcategory

category = session.query(Category).filter_by(category_id=category_id).first()
if not category:
    session.add(Category(category_id=category_id, name="Veg"))

subcategory = session.query(Subcategory).filter_by(subcategory_id=subcategory_id).first()
if not subcategory:
    session.add(Subcategory(subcategory_id=subcategory_id, category_id=category_id, name="Breads"))

# Commit category & subcategory additions
session.commit()

# Check if menu items already exist
existing_items = session.query(MenuItem).filter(MenuItem.subcategory_id == subcategory_id).count()
if existing_items < 0:
    print("Dummy data for Breads already exists. Skipping insertion.")
else:
    # Define dummy menu items
    dummy_items = [
        MenuItem(
            menu_item_id="MI022",
            name="Garlic Naan",
            description="Buttery garlic bread",
            price=40.00,
            image_url="https://HiFiDeliveryEats.com/Garlic_Naan.jpg",
            category_id=category_id,
            subcategory_id=subcategory_id,
            nutrient_value="Carbs: 45g, Protein: 8g, Fat: 6g",
            calorie_count=220,
            is_best_seller=True,
            is_out_of_stock=False,
            discount_percentage=5.00,
            scheduled_update_time=None
        ),
        MenuItem(
            menu_item_id="MI023",
            name="Butter Roti",
            description="Soft and buttery",
            price=30.00,
            image_url="https://HiFiDeliveryEats.com/Butter_Roti.jpg",
            category_id=category_id,
            subcategory_id=subcategory_id,
            nutrient_value="Carbs: 40g, Protein: 7g, Fat: 4g",
            calorie_count=180,
            is_best_seller=False,
            is_out_of_stock=False,
            discount_percentage=None,
            scheduled_update_time=None
        ),
        MenuItem(
            menu_item_id="MI024",
            name="Aloo Paratha",
            description="Stuffed bread with spiced potatoes",
            price=50.00,
            image_url="https://HiFiDeliveryEats.com/Aloo_Paratha.jpg",
            category_id=category_id,
            subcategory_id=subcategory_id,
            nutrient_value="Carbs: 50g, Protein: 10g, Fat: 12g",
            calorie_count=280,
            is_best_seller=True,
            is_out_of_stock=False,
            discount_percentage=10.00,
            scheduled_update_time=None
        ),
        MenuItem(
            menu_item_id="MI025",
            name="Plain Naan",
            description="Soft and fluffy Indian bread",
            price=35.00,
            image_url="https://HiFiDeliveryEats.com/Plain_Naan.jpg",
            category_id=category_id,
            subcategory_id=subcategory_id,
            nutrient_value="Carbs: 42g, Protein: 6g, Fat: 3g",
            calorie_count=200,
            is_best_seller=False,
            is_out_of_stock=False,
            discount_percentage=None,
            scheduled_update_time=None
        ),
        MenuItem(
            menu_item_id="MI026",
            name="Keema Naan",
            description="Naan stuffed with spiced minced meat",
            price=60.00,
            image_url="https://HiFiDeliveryEats.com/Keema_Naan.jpg",
            category_id="IC002",  # Non-Veg Category
            subcategory_id=subcategory_id,
            nutrient_value="Carbs: 48g, Protein: 15g, Fat: 14g",
            calorie_count=320,
            is_best_seller=True,
            is_out_of_stock=False,
            discount_percentage=8.00,
            scheduled_update_time=None
        ),
        MenuItem(
            menu_item_id="MI027",
            name="Chicken Stuffed Kulcha",
            description="Kulcha with shredded chicken filling",
            price=65.00,
            image_url="https://HiFiDeliveryEats.com/Chicken_Stuffed_Kulcha.jpg",
            category_id="IC002",  # Non-Veg Category
            subcategory_id=subcategory_id,
            nutrient_value="Carbs: 50g, Protein: 18g, Fat: 16g",
            calorie_count=350,
            is_best_seller=True,
            is_out_of_stock=False,
            discount_percentage=12.00,
            scheduled_update_time=None
        )
    ]
    
    # Insert dummy data
    session.add_all(dummy_items)
    session.commit()
    print("Dummy data for Breads inserted successfully!")

# Close session
session.close()
'''

'''
from sqlalchemy.orm import sessionmaker
from create_database import engine, MenuItem, Category, Subcategory  # Import models
from datetime import datetime

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Ensure required category and subcategory exist
category_id_veg = "IC001"   # Veg
category_id_non_veg = "IC002"  # Non-Veg
subcategory_id_salad = "ISC003"  # Salads

# Check if menu items already exist for Salads
existing_items = session.query(MenuItem).filter_by(subcategory_id=subcategory_id_salad).count()
if existing_items < 0:
    print("Salad items already exist. Skipping insertion.")
else:
    # Define dummy menu items for Salads with updated menu_item_id
    dummy_salad_items = [
        MenuItem(
            menu_item_id="MI017",
            name="Greek Salad",
            description="Fresh and healthy",
            price=120.00,
            image_url="https://HiFiDeliveryEats.com/Greek_Salad.jpg",
            category_id=category_id_veg,
            subcategory_id=subcategory_id_salad,
            nutrient_value="Carbs: 20g, Protein: 5g, Fat: 10g",
            calorie_count=200,
            is_best_seller=False,
            is_out_of_stock=False,
            discount_percentage=None,
            scheduled_update_time=None
        ),
        MenuItem(
            menu_item_id="MI018",
            name="Cucumber Avocado Salad",
            description="Refreshing cucumber and avocado mix",
            price=110.00,
            image_url="https://HiFiDeliveryEats.com/Cucumber_Avocado_Salad.jpg",
            category_id=category_id_veg,
            subcategory_id=subcategory_id_salad,
            nutrient_value="Carbs: 12g, Protein: 4g, Fat: 8g",
            calorie_count=180,
            is_best_seller=False,
            is_out_of_stock=False,
            discount_percentage=10.00,
            scheduled_update_time=datetime.utcnow()
        ),
        MenuItem(
            menu_item_id="MI019",
            name="Pasta Salad",
            description="Pasta with veggies and dressing",
            price=115.00,
            image_url="https://HiFiDeliveryEats.com/Pasta_Salad.jpg",
            category_id=category_id_veg,
            subcategory_id=subcategory_id_salad,
            nutrient_value="Carbs: 40g, Protein: 8g, Fat: 12g",
            calorie_count=250,
            is_best_seller=False,
            is_out_of_stock=False,
            discount_percentage=None,
            scheduled_update_time=None
        ),
        MenuItem(
            menu_item_id="MI020",
            name="Chicken Caesar Salad",
            description="Caesar salad with grilled chicken",
            price=140.00,
            image_url="https://HiFiDeliveryEats.com/Chicken_Caesar_Salad.jpg",
            category_id=category_id_non_veg,
            subcategory_id=subcategory_id_salad,
            nutrient_value="Carbs: 20g, Protein: 25g, Fat: 15g",
            calorie_count=300,
            is_best_seller=True,
            is_out_of_stock=False,
            discount_percentage=8.00,
            scheduled_update_time=datetime.utcnow()
        ),
        MenuItem(
            menu_item_id="MI021",
            name="Shrimp Salad",
            description="Fresh shrimp with mixed greens",
            price=150.00,
            image_url="https://HiFiDeliveryEats.com/Shrimp_Salad.jpg",
            category_id=category_id_non_veg,
            subcategory_id=subcategory_id_salad,
            nutrient_value="Carbs: 15g, Protein: 30g, Fat: 10g",
            calorie_count=280,
            is_best_seller=False,
            is_out_of_stock=False,
            discount_percentage=None,
            scheduled_update_time=None
        )
    ]

    # Insert dummy data
    session.add_all(dummy_salad_items)
    session.commit()
    print("Salad dummy data inserted successfully!")

# Close session
session.close()
'''

'''
from sqlalchemy.orm import sessionmaker
from create_database import engine, MenuItem, Category, Subcategory  # Import models
from datetime import datetime

def format_image_url(name):
    formatted_name = name.replace(" ", "_").replace("-", "_").title()
    return f"https://HiFiDeliveryEats.com/{formatted_name}.jpg"

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

# Ensure default subcategories exist
subcategory_mapping = "ISC005"  # Starter subcategory

default_subcategories = {
    "ISC005": ("IC001", "Starter"),
    "ISC012": ("IC002", "Starter")  # Separate for Non-Veg
}

for subcategory_id, (category_id, name) in default_subcategories.items():
    subcategory = session.query(Subcategory).filter_by(subcategory_id=subcategory_id).first()
    if not subcategory:
        session.add(Subcategory(subcategory_id=subcategory_id, category_id=category_id, name=name))

# Commit category & subcategory additions
session.commit()

# Check if menu items already exist
existing_items = session.query(MenuItem).count()
if existing_items < 0:
    print("Dummy data already exists. Skipping insertion.")
else:
    dummy_items = [
        MenuItem(
            menu_item_id="MI005",
            name="Paneer Tikka",
            description="Grilled cottage cheese",
            price=150.00,
            image_url=format_image_url("Paneer Tikka"),
            category_id="IC001",
            subcategory_id="ISC005",
            nutrient_value="Carbs: 20g, Protein: 15g, Fat: 10g",
            calorie_count=220,
            is_best_seller=True,
            is_out_of_stock=False,
            discount_percentage=5.00,
            scheduled_update_time=datetime.utcnow()
        ),
        MenuItem(
            menu_item_id="MI006",
            name="Chicken Lollipop",
            description="Spicy chicken appetizer",
            price=180.00,
            image_url=format_image_url("Chicken Lollipop"),
            category_id="IC002",
            subcategory_id="ISC012",
            nutrient_value="Carbs: 10g, Protein: 25g, Fat: 15g",
            calorie_count=280,
            is_best_seller=True,
            is_out_of_stock=False,
            discount_percentage=10.00,
            scheduled_update_time=None
        ),
        MenuItem(
            menu_item_id="MI007",
            name="Vegetable Spring Rolls",
            description="Crispy rolls with veggie filling",
            price=120.00,
            image_url=format_image_url("Vegetable Spring Rolls"),
            category_id="IC001",
            subcategory_id="ISC005",
            nutrient_value="Carbs: 30g, Protein: 5g, Fat: 10g",
            calorie_count=180,
            is_best_seller=False,
            is_out_of_stock=False,
            discount_percentage=7.00,
            scheduled_update_time=None
        ),
        MenuItem(
            menu_item_id="MI008",
            name="Mushroom Manchurian",
            description="Spicy Indo-Chinese mushroom dish",
            price=140.00,
            image_url=format_image_url("Mushroom Manchurian"),
            category_id="IC001",
            subcategory_id="ISC005",
            nutrient_value="Carbs: 20g, Protein: 10g, Fat: 12g",
            calorie_count=200,
            is_best_seller=False,
            is_out_of_stock=False,
            discount_percentage=5.00,
            scheduled_update_time=None
        ),
        MenuItem(
            menu_item_id="MI009",
            name="Fish Fingers",
            description="Crispy fried fish sticks",
            price=200.00,
            image_url=format_image_url("Fish Fingers"),
            category_id="IC002",
            subcategory_id="ISC012",
            nutrient_value="Carbs: 25g, Protein: 20g, Fat: 15g",
            calorie_count=250,
            is_best_seller=True,
            is_out_of_stock=False,
            discount_percentage=12.00,
            scheduled_update_time=None
        ),
        MenuItem(
            menu_item_id="MI010",
            name="Prawn Tempura",
            description="Lightly battered fried prawns",
            price=220.00,
            image_url=format_image_url("Prawn Tempura"),
            category_id="IC002",
            subcategory_id="ISC012",
            nutrient_value="Carbs: 15g, Protein: 30g, Fat: 10g",
            calorie_count=260,
            is_best_seller=True,
            is_out_of_stock=False,
            discount_percentage=10.00,
            scheduled_update_time=datetime.utcnow()
        )
    ]

    # Insert dummy data
    session.add_all(dummy_items)
    session.commit()
    print("Dummy data inserted successfully!")

# Close session
session.close()
'''

'''
from sqlalchemy.orm import sessionmaker
from create_database import engine, MenuItem, Category, Subcategory  # Import models
from datetime import datetime

# Create a session
Session = sessionmaker(bind=engine)
session = Session()

# Ensure Soups category exists
category_id = "IC001"  # Veg Category
subcategory_id = "ISC006"  # Soups Subcategory
subcategory_name = "Soup"

subcategory = session.query(Subcategory).filter_by(subcategory_id=subcategory_id).first()
if not subcategory:
    session.add(Subcategory(subcategory_id=subcategory_id, category_id=category_id, name=subcategory_name))
    session.commit()

# Check if soup items already exist
existing_items = session.query(MenuItem).filter_by(subcategory_id=subcategory_id).count()
if existing_items < 0:
    print("Dummy soup data already exists. Skipping insertion.")
else:
    # Define dummy soup menu items
    soup_items = [
        MenuItem(
            menu_item_id="MI011",
            name="Tomato Soup",
            description="Classic tomato soup",
            price=80.00,
            image_url="https://HiFiDeliveryEats.com/tomato_Soup.jpg",
            category_id=category_id,
            subcategory_id=subcategory_id,
            nutrient_value="Carbs: 15g, Protein: 3g, Fat: 1g",
            calorie_count=90,
            is_best_seller=False,
            is_out_of_stock=False,
            discount_percentage=None,
            scheduled_update_time=None
        ),
        MenuItem(
            menu_item_id="MI012",
            name="Hot & Sour Soup",
            description="Spicy and tangy soup",
            price=90.00,
            image_url="https://HiFiDeliveryEats.com/hot_Sour_Soup.jpg",
            category_id=category_id,
            subcategory_id=subcategory_id,
            nutrient_value="Carbs: 18g, Protein: 5g, Fat: 2g",
            calorie_count=110,
            is_best_seller=False,
            is_out_of_stock=False,
            discount_percentage=None,
            scheduled_update_time=None
        ),
        MenuItem(
            menu_item_id="MI013",
            name="Cream of Spinach Soup",
            description="Creamy spinach and herb soup",
            price=85.00,
            image_url="https://HiFiDeliveryEats.com/cream_Spinach_Soup.jpg",
            category_id=category_id,
            subcategory_id=subcategory_id,
            nutrient_value="Carbs: 20g, Protein: 6g, Fat: 4g",
            calorie_count=120,
            is_best_seller=False,
            is_out_of_stock=False,
            discount_percentage=None,
            scheduled_update_time=None
        ),
        MenuItem(
            menu_item_id="MI014",
            name="Sweet Corn Soup",
            description="Corn soup with vegetables",
            price=80.00,
            image_url="https://HiFiDeliveryEats.com/sweet_Corn_Soup.jpg",
            category_id=category_id,
            subcategory_id=subcategory_id,
            nutrient_value="Carbs: 22g, Protein: 4g, Fat: 3g",
            calorie_count=130,
            is_best_seller=False,
            is_out_of_stock=False,
            discount_percentage=None,
            scheduled_update_time=None
        ),
        MenuItem(
            menu_item_id="MI015",
            name="Chicken Noodle Soup",
            description="Hearty soup with chicken and noodles",
            price=100.00,
            image_url="https://HiFiDeliveryEats.com/chicken_Noodle_Soup.jpg",
            category_id="IC002",  # Non-Veg
            subcategory_id=subcategory_id,
            nutrient_value="Carbs: 30g, Protein: 15g, Fat: 5g",
            calorie_count=180,
            is_best_seller=False,
            is_out_of_stock=False,
            discount_percentage=None,
            scheduled_update_time=None
        ),
        MenuItem(
            menu_item_id="MI016",
            name="Mutton Broth",
            description="Flavorful mutton soup",
            price=110.00,
            image_url="https://HiFiDeliveryEats.com/mutton_Broth.jpg",
            category_id="IC002",  # Non-Veg
            subcategory_id=subcategory_id,
            nutrient_value="Carbs: 10g, Protein: 20g, Fat: 8g",
            calorie_count=190,
            is_best_seller=False,
            is_out_of_stock=False,
            discount_percentage=None,
            scheduled_update_time=None
        )
    ]

    # Insert dummy data
    session.add_all(soup_items)
    session.commit()
    print("Dummy soup data inserted successfully!")

# Close session
session.close()
'''
