from flask import Flask, request, render_template, redirect, url_for, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.create_database import MenuItem, Category
from database.services import MenuService
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create connection to database
engine = create_engine("sqlite:///hifi_database.db", echo=True)
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

@app.route('/add_item', methods=["POST"])
def add_item():
    try:
        data = request.form
        item_name = data["item_name"]
        description = data["description"]
        price = float(data["price"])
        category_name = data["category"]
        discount = float(data.get("discount", 0))
        best_seller = data.get("best_seller", "false").lower() in ["yes", "true", "1"]
        is_out_of_stock = data.get("stock_available", "1") == "0"
        
        # Handle image upload
        image_url = ""
        if "image" in request.files:
            image = request.files["image"]
            if image.filename:
                image_path = os.path.join(app.config["UPLOAD_FOLDER"], image.filename)
                image.save(image_path)
                image_url = image_path
        
        new_item = menu_service.add_menu_item(
            name=item_name,
            description=description,
            price=price,
            image_url=image_url,
            category_name=category_name,
            nutrient_value="N/A",
            calorie_count=0,
            is_best_seller=best_seller,
            is_out_of_stock=is_out_of_stock,
            discount_percentage=discount
        )
        return jsonify({"success": True, "message": "Item added successfully", "item_id": new_item.menu_item_id})
    except Exception as e:
        session.rollback()
        session.close()
        logger.error(f"Error adding menu item: {e}", exc_info=True)
        return jsonify({"success": False, "message": str(e)})
    

@app.route('/get_items', methods=['GET'])
def get_items():
    items = session.query(MenuItem).all()
    items_list = [
        {
            "menu_item_id": item.menu_item_id,
            "name": item.name,
            "description": item.description,
            "price": item.price,  # Convert DECIMAL to float
            "category_id": item.category_id,
            "nutrient_value": item.nutrient_value,
            "calorie_count": item.calorie_count,
            "discount_percentage": item.discount_percentage if item.discount_percentage else 0.0,
            "image_url": item.image_url,
            "is_best_seller": item.is_best_seller,
            "is_out_of_stock": item.is_out_of_stock
        }
        for item in items
    ]
    return jsonify(items_list)

@app.route('/get_item_by_name/<string:item_name>', methods=['GET'])
def get_item_by_name(item_name):
    item = session.query(MenuItem, Category.name.label("category_name")) \
        .join(Category, MenuItem.category_id == Category.category_id) \
        .filter(MenuItem.name == item_name).first()

    if not item:
        return jsonify({"error": "Item not found"}), 404  # Return 404 if not found
    
    session.close()
    return jsonify({
        "menu_item_id": item.MenuItem.menu_item_id,
        "name": item.MenuItem.name,
        "description": item.MenuItem.description,
        "price": float(item.MenuItem.price),
        "category_name": item.category_name,  # Fetch category name instead of ID
        "discount_percentage": item.MenuItem.discount_percentage,
        "is_best_seller": item.MenuItem.is_best_seller,
        "is_out_of_stock": item.MenuItem.is_out_of_stock
    })

@app.route('/update_item', methods=["POST"])
def update_item():
    try:
        data = request.json  # Get JSON data from request
        logger.info("Received Data for Update:", data) 
        
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
        
        # Fetch category_id based on category_name (if provided)
        category_id = None
        if "category_name" in data:
            category = session.query(Category).filter_by(name=data["category_name"]).first()
            if category:
                category_id = category.category_id
            else:
                return jsonify({"error": "Invalid category name"}), 400
            
        menu_item.category_id = category_id if category_id else menu_item.category_id
        
        menu_item.discount_percentage = data.get("discount_percentage", menu_item.discount_percentage)
        menu_item.is_best_seller = data.get("is_best_seller", menu_item.is_best_seller)
        menu_item.is_out_of_stock = data.get("is_out_of_stock", menu_item.is_out_of_stock)

        # Commit changes
        session.commit()
        session.close()
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