from flask import Flask, request, render_template, redirect, url_for, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from database.create_database import MenuItem, Category, Subcategory
from database.services import MenuService
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create connection to database
engine = create_engine("sqlite:///hifi_database.db", echo=False)
Session = sessionmaker(bind=engine)
session = Session()
menu_service = MenuService(session)

app = Flask(__name__)

UPLOAD_FOLDER = "static/images"  # Folder to store images
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    """Render the Home page."""
    return render_template('index.html')

@app.route('/menu')
def menu():
    """Render the Menu page."""
    return render_template('menu.html')

@app.route('/show_menu')
def show_menu():
    """Render the Menu page."""
    return render_template('show_menu.html')


@app.route('/order')
def order():
    """Render the Menu page."""
    return render_template('order.html')

# http://127.0.0.1:5000/order_track use this for accessing this webpage.
@app.route('/order_track')
def order_track():
    """Render the Menu page."""
    return render_template('order_track.html')



@app.route('/add_item', methods=["POST"])
def add_item():
    try:
        data = request.form
        item_name = data["item_name"]
        description = data["description"]
        price = float(data["price"])
        category_name = data["category"]
        subcategory_name = data["subcategory"]
        discount = float(data.get("discount", 0))
        best_seller = data.get("best_seller", "false").lower() in ["yes", "true", "1"]
        is_out_of_stock = data.get("stock_available", "1") == "0"
        
        # Handle image upload
        image_url = ""
        BASE_URL = "https://HiFiDeliveryEats.com/"
        if "image" in request.files:
            image = request.files["image"]
            if image.filename:
                image_path = os.path.join(app.config["UPLOAD_FOLDER"], image.filename)
                image.save(image_path) # Save image
                # Generate a dummy image URL
                image_url = f"{BASE_URL}{image.filename}"
        
        new_item = menu_service.add_menu_item(
            name=item_name,
            description=description,
            price=price,
            image_url=image_url,
            category_name=category_name,
            subcategory_name=subcategory_name,
            nutrient_value="N/A",
            calorie_count=0,
            is_best_seller=best_seller,
            is_out_of_stock=is_out_of_stock,
            discount_percentage=discount
        )
        
        return jsonify({"success": True, "message": "Item added successfully", "menu_item_id": new_item.menu_item_id,"image_url":new_item.image_url})
    except Exception as e:
        session.rollback()
        session.close()
        logger.error(f"Error adding menu item: {e}", exc_info=True)
        return jsonify({"success": False, "message": str(e)})
    
@app.route('/get_items', methods=['GET'])
def get_items():
    items = (session.query(MenuItem, Category, Subcategory).join(Category, MenuItem.category_id == Category.category_id)
        .join(Subcategory, MenuItem.subcategory_id == Subcategory.subcategory_id).all())
    items_list = [
        {
            "menu_item_id": item.MenuItem.menu_item_id,
            "name": item.MenuItem.name,
            "description": item.MenuItem.description,
            "price": item.MenuItem.price,  # Convert DECIMAL to float
            "category_name": item.Category.name,
            "subcategory_name": item.Subcategory.name,
            "nutrient_value": item.MenuItem.nutrient_value,
            "calorie_count": item.MenuItem.calorie_count,
            "discount_percentage": item.MenuItem.discount_percentage if item.MenuItem.discount_percentage else 0.0,
            "image_url": item.MenuItem.image_url,
            "is_best_seller": item.MenuItem.is_best_seller,
            "is_out_of_stock": item.MenuItem.is_out_of_stock
        }
        for item in items
    ]
    session.close()
    return jsonify(items_list)

@app.route('/get_item_by_name/<string:item_name>', methods=['GET'])
def get_item_by_name(item_name):
    try:
        item = (
            session.query(
                MenuItem.menu_item_id, MenuItem.name, MenuItem.description, MenuItem.price,
                MenuItem.nutrient_value, MenuItem.calorie_count, MenuItem.discount_percentage,
                MenuItem.image_url, MenuItem.is_best_seller, MenuItem.is_out_of_stock,
                MenuItem.scheduled_update_time,  
                Category.name.label("category_name"),
                Subcategory.name.label("subcategory_name")
            )    #category_id subcategory_id
            .join(Category, MenuItem.category_id == Category.category_id, isouter=True)  # Left join in case category is missing
            .join(Subcategory, MenuItem.subcategory_id == Subcategory.subcategory_id, isouter=True)  # Left join in case subcategory is missing
            .filter(MenuItem.name == item_name)
            .first()
        )

        if not item:
            return jsonify({"error": "Item not found"}), 404  # Return 404 if not found

        print("\n\n\n")
        print("Fetched Item:", item)  # Debugging
        print("\n\n\n")
        
        response_data = {
            "menu_item_id": item.menu_item_id,
            "name": item.name,
            "description": item.description,
            "price": float(item.price),  # Convert DECIMAL to float
            "category_name": item.category_name if item.category_name else "Uncategorized",
            "subcategory_name": item.subcategory_name if item.subcategory_name else "Uncategorized",
            "nutrient_value": item.nutrient_value,
            "calorie_count": item.calorie_count,
            "discount_percentage": float(item.discount_percentage or 0.0),
            "image_url": item.image_url,
            "is_best_seller": item.is_best_seller,
            "is_out_of_stock": item.is_out_of_stock,
            "scheduled_update_time": item.scheduled_update_time.isoformat() if item.scheduled_update_time else None
        }
        session.close()
        return jsonify(response_data)

    except Exception as e:
        print("Error in get_item_by_name:", str(e))  # Debugging error
        return jsonify({"error": str(e)}), 500  # Return 500 for internal server errors

@app.route('/update_item', methods=["POST"])
def update_item():
    try:
        data = request.json  # Get JSON data from request
        logger.info("\n\n\nReceived Data for Update: %s", data,"\n\n\n")  # Log full request data
        
        menu_item_id = data.get("menu_item_id")
        
        if not menu_item_id:
            return jsonify({"error": "Menu item ID not provided"}), 400
        
        # Fetch the menu item from the database
        menu_item = session.query(MenuItem).filter_by(menu_item_id=menu_item_id).first()
        if not menu_item:
            return jsonify({"error": "Menu item not found"}), 404

        
        # Update only provided fields, keep others unchanged
        menu_item.name = data.get("name", menu_item.name)
        menu_item.description = data.get("description", menu_item.description)
        menu_item.price = data.get("price", menu_item.price)
        menu_item.discount_percentage = data.get("discount_percentage", menu_item.discount_percentage)
        menu_item.is_best_seller = data.get("is_best_seller", menu_item.is_best_seller)
        menu_item.is_out_of_stock = data.get("is_out_of_stock", menu_item.is_out_of_stock)

        # 🔹 Fetch category_id case-insensitively if category_name is provided
        if "category_name" in data:
            category_name = data["category_name"].strip()
            category = session.query(Category).filter(func.lower(Category.name) == category_name.lower()).first()
            
            if category:
                menu_item.category_id = category.category_id
                logger.info(f"\n\n\nUpdated category_id to: {menu_item.category_id}")
            else:
                logger.error(f"Invalid category name: {category_name}")
                return jsonify({"error": "Invalid category name"}), 400
        
        # 🔹 Fetch subcategory_id case-insensitively if subcategory_name is provided
        if "subcategory_name" in data:
            subcategory_name = data["subcategory_name"].strip()
            subcategory = session.query(Subcategory).filter(func.lower(Subcategory.name) == subcategory_name.lower()).first()
            
            if subcategory:
                menu_item.subcategory_id = subcategory.subcategory_id
                logger.info(f"\n\n\nUpdated subcategory_id to: {menu_item.subcategory_id}")
            else:
                logger.error(f"Invalid subcategory name: {subcategory_name}")
                return jsonify({"error": "Invalid subcategory name"}), 400
        
        # Commit changes
        session.commit()
        session.close()
        logger.info(f"\n\nUpdated Successfully\n\n\n")
        return jsonify({"message": "Menu item updated successfully"}), 200

    except Exception as e:
        session.rollback()
        logger.error(f"Error updating menu item: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route("/delete_item", methods=["DELETE"])
def delete_item():
    try:
        data = request.get_json()
        item_name = data.get("name")

        # Find item by name
        item = session.query(MenuItem).filter_by(name=item_name).first()

        if item :
            session.delete(item)
            session.commit()
            session.close()
            return jsonify({"message": f"Item '{item_name}' deleted successfully!"}), 200
        else:
            return jsonify({"error": f"Item '{item_name}' not found"}), 404

    except Exception as e:
        session.rollback()
        session.close()
        logger.error(f"Error deleting menu item: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)