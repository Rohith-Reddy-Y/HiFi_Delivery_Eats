from flask import Flask, request, render_template, redirect, url_for, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from database.create_database import Base, MenuItem, Category, Subcategory, Cart, User, Order, OrderItem
from database.services import MenuService, generate_next_id
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
    return render_template('show_menu.html')


@app.route('/order')
def order():
    return render_template('order.html')

# http://127.0.0.1:5000/order_track use this for accessing this webpage.
@app.route('/order_track')
def order_track():
    return render_template('order_track.html')


# http://127.0.0.1:5000/delivery_details.html
@app.route('/delivery_details')
def delivery_details():
    return render_template('delivery_details.html')
    





# MENU MANAGEMENT FUNCTIONS : Add_menu webpage

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
        stock_available = float(data.get("stock_available", 0))
        
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
            discount_percentage=discount,
            stock_available=stock_available
        )
        
        return jsonify({"success": True, "message": "Item added successfully", "menu_item_id": new_item.menu_item_id,"image_url":new_item.image_url})
    except Exception as e:
        session.rollback()
        session.close()
        logger.error(f"Error adding menu item: {e}", exc_info=True)
        return jsonify({"success": False, "message": str(e)})
    
# For renderMenuItems function in menu.js
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
            "is_out_of_stock": item.MenuItem.is_out_of_stock,
            "stock_available": item.MenuItem.stock_available
        }
        for item in items
    ]
    # print("\n\n\n\n\n",*items_list,"\n\n\n\n\n")
    session.close()
    return jsonify(items_list)

# for showEditPopup, showDeleteConfirmation funtion in menu.js
@app.route('/get_item_by_id/<string:menu_item_id>', methods=['GET'])
def get_item_by_id(menu_item_id):
    try:
        item = (
            session.query(
                MenuItem.menu_item_id, MenuItem.name, MenuItem.description, MenuItem.price,
                MenuItem.nutrient_value, MenuItem.calorie_count, MenuItem.discount_percentage,
                MenuItem.image_url, MenuItem.is_best_seller, MenuItem.stock_available,
                MenuItem.scheduled_update_time,  
                Category.name.label("category_name"),
                Subcategory.name.label("subcategory_name")
            )    #category_id subcategory_id
            .join(Category, MenuItem.category_id == Category.category_id, isouter=True)  # Left join in case category is missing
            .join(Subcategory, MenuItem.subcategory_id == Subcategory.subcategory_id, isouter=True)  # Left join in case subcategory is missing
            .filter(MenuItem.menu_item_id == menu_item_id)
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
            "stock_available": item.stock_available,
            "scheduled_update_time": item.scheduled_update_time.isoformat() if item.scheduled_update_time else None
        }
        session.close()
        return jsonify(response_data)

    except Exception as e:
        print("Error in get_item_by_name:", str(e))  # Debugging error
        return jsonify({"error": str(e)}), 500  # Return 500 for internal server errors

# for showEditPopup function, when click on ok to update in menu.js
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
        menu_item.stock_available = data.get("stock_available", menu_item.stock_available)

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

# for showDeleteConfirmation funtion, when click on ok to delete in menu.js
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


# MENU MANAGEMENT FUNCTIONS : show_menu webpage
@app.route('/api/menu_items', methods=['GET'])
def get_menu_items_api():
    try:
        # Fetch all menu items with their category and subcategory details
        items = (
            session.query(
                MenuItem.menu_item_id,
                MenuItem.name,
                MenuItem.description,
                MenuItem.price,
                MenuItem.image_url,
                MenuItem.is_best_seller,
                MenuItem.is_out_of_stock,
                MenuItem.stock_available,
                Category.name.label("category_name"),
                Subcategory.name.label("subcategory_name")
            )
            .join(Category, MenuItem.category_id == Category.category_id, isouter=True)  # Left join for category
            .join(Subcategory, MenuItem.subcategory_id == Subcategory.subcategory_id, isouter=True)  # Left join for subcategory
            .filter(MenuItem.is_out_of_stock == False)  # Filter out-of-stock items
            .all()
        )


        # Format the response data
        items_list = [
            {
                "menu_item_id": item.menu_item_id,
                "name": item.name,
                "description": item.description,
                "price": float(item.price),  # Convert DECIMAL to float
                "category_name": item.category_name if item.category_name else "Uncategorized",
                "subcategory_name": item.subcategory_name if item.subcategory_name else "Uncategorized",
                "image_url": item.image_url,
                "is_best_seller": item.is_best_seller,
                "is_out_of_stock": item.is_out_of_stock,
                "stock_available": item.stock_available,
            }
            for item in items
        ]

        session.close()
        return jsonify({'data':items_list,'ok':True})

    except Exception as e:
        session.close()
        logger.error(f"Error fetching menu items: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    


# ORDER MANAGEMENT ENDPOINTS

'''
New Endpoints:
- /api/get_cart_items/<user_id>: Retrieves cart items for a user.
- /api/update_cart: Updates quantity or removes an item from the cart.
- /api/clear_cart_items: Clears selected or all cart items for a user.
- /api/place_order: Places an order, creates Order and OrderItem entries, and clears the cart.

- /api/get_cart_items: to include discount and stock information.
- /api/place_order: to use cart items from the database, include payment method and coordinates, and update stock.
- /api/get_order_history: to fetch past orders for a user.
'''
@app.route('/api/get_cart_items/<string:user_id>', methods=['GET'])
def get_cart_items(user_id):
    try:
        cart_items = (
            session.query(Cart, MenuItem)
            .join(MenuItem, Cart.menu_item_id == MenuItem.menu_item_id)
            .filter(Cart.user_id == user_id)
            .all()
        )
        cart_items_list = [
            {
                "cart_id": item.Cart.cart_id,
                "menu_item_id": item.MenuItem.menu_item_id,
                "name": item.MenuItem.name,
                "price": float(item.MenuItem.price),
                "quantity": item.Cart.quantity,
                "image_url": item.MenuItem.image_url,
                "discount_percentage": float(item.MenuItem.discount_percentage or 0.0),
                "stock_available": item.MenuItem.stock_available
            }
            for item in cart_items
        ]
        return jsonify(cart_items_list), 200
    except Exception as e:
        logger.error(f"Error fetching cart items: {e}", exc_info=True)
        return jsonify({"success": False, "message": str(e)}), 500
@app.route('/api/update_cart', methods=['POST'])
def update_cart():
    try:
        data = request.json
        user_id = data.get("user_id")
        cart_id = data.get("cart_id")
        quantity = data.get("quantity")

        cart_item = session.query(Cart).filter_by(cart_id=cart_id, user_id=user_id).first()
        if not cart_item:
            return jsonify({"success": False, "message": "Cart item not found"}), 404

        menu_item = session.query(MenuItem).filter_by(menu_item_id=cart_item.menu_item_id).first()
        if quantity > menu_item.stock_available:
            return jsonify({"success": False, "message": f"Only {menu_item.stock_available} items available"}), 400

        if quantity <= 0:
            session.delete(cart_item)
        else:
            cart_item.quantity = quantity
        session.commit()
        return jsonify({"success": True, "message": "Cart updated"}), 200
    except Exception as e:
        session.rollback()
        logger.error(f"Error updating cart: {e}", exc_info=True)
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/clear_cart_items', methods=['POST'])
def clear_cart_items():
    try:
        data = request.json
        user_id = data.get("user_id")
        cart_ids = data.get("cart_ids", [])

        if not cart_ids:
            session.query(Cart).filter_by(user_id=user_id).delete()
        else:
            session.query(Cart).filter(Cart.user_id == user_id, Cart.cart_id.in_(cart_ids)).delete(synchronize_session=False)
        session.commit()
        return jsonify({"success": True, "message": "Selected cart items cleared"}), 200
    except Exception as e:
        session.rollback()
        logger.error(f"Error clearing cart items: {e}", exc_info=True)
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/place_order', methods=['POST'])
def place_order():
    try:
        data = request.json
        user_id = data.get("user_id")
        delivery_details = data.get("delivery_details")
        payment_method = data.get("payment_method")
        coordinates = data.get("coordinates")

        cart_items = session.query(Cart, MenuItem)\
            .join(MenuItem, Cart.menu_item_id == MenuItem.menu_item_id)\
            .filter(Cart.user_id == user_id).all()

        if not cart_items:
            return jsonify({"success": False, "message": "Cart is empty"}), 400

        # Calculate total price
        total_price = 0
        order_items_data = []
        for cart, menu_item in cart_items:
            if cart.quantity > menu_item.stock_available:
                return jsonify({"success": False, "message": f"Insufficient stock for {menu_item.name}"}), 400
            item_total = float(menu_item.price) * cart.quantity
            discount = item_total * (float(menu_item.discount_percentage or 0) / 100)
            total_price += (item_total - discount)
            order_items_data.append({
                "menu_item_id": menu_item.menu_item_id,
                "quantity": cart.quantity,
                "price": float(menu_item.price),
                "name": menu_item.name
            })

        tax = total_price * 0.18
        delivery_charge = 50.0
        total_price += tax + delivery_charge

        # Create order
        latest_order_id = menu_service.get_latest_id(Order.order_id)
        order_id = generate_next_id(latest_order_id, "O")
        new_order = Order(
            order_id=order_id,
            user_id=user_id,
            total_price=total_price,
            delivery_location=delivery_details,
            payment_method=payment_method,
            coordinates=coordinates,
            status="Pending"
        )
        session.add(new_order)

        # Create order items and update stock
        for item in order_items_data:
            latest_order_item_id = menu_service.get_latest_id(OrderItem.order_item_id)
            order_item_id = generate_next_id(latest_order_item_id, "OI")
            new_order_item = OrderItem(
                order_item_id=order_item_id,
                order_id=order_id,
                menu_item_id=item["menu_item_id"],
                quantity=item["quantity"],
                price=item["price"]
            )
            session.add(new_order_item)
            menu_item = session.query(MenuItem).filter_by(menu_item_id=item["menu_item_id"]).first()
            menu_item.stock_available -= item["quantity"]

        # Clear cart
        session.query(Cart).filter_by(user_id=user_id).delete()
        session.commit()

        return jsonify({"success": True, "message": "Order placed successfully", "order_id": order_id}), 200
    except Exception as e:
        session.rollback()
        logger.error(f"Error placing order: {e}", exc_info=True)
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/get_order_history/<string:user_id>', methods=['GET'])
def get_order_history(user_id):
    try:
        orders = session.query(Order).filter_by(user_id=user_id).all()
        order_history = []
        for order in orders:
            order_items = session.query(OrderItem, MenuItem)\
                .join(MenuItem, OrderItem.menu_item_id == MenuItem.menu_item_id)\
                .filter(OrderItem.order_id == order.order_id).all()
            items = [{"name": item.MenuItem.name, "quantity": item.OrderItem.quantity, "price": float(item.OrderItem.price)} for item in order_items]
            order_history.append({
                "order_id": order.order_id,
                "items": items,
                "total_price": float(order.total_price),
                "date": order.created_at.isoformat(),
                "status": order.status
            })
        return jsonify(order_history), 200
    except Exception as e:
        logger.error(f"Error fetching order history: {e}", exc_info=True)
        return jsonify({"success": False, "message": str(e)}), 500











if __name__ == '__main__':
    # print("Creating tables...")
    # Base.metadata.create_all(bind=engine)
    app.run(debug=True)
    