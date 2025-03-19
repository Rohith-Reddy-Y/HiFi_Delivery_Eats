from flask import Flask, request, render_template, redirect, url_for, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from database.create_database import Base, MenuItem, Category, Subcategory, Cart, User, Order, OrderItem
from database.services import MenuService, generate_next_id
import os
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create connection to database
engine = create_engine("sqlite:///hifi_database.db", echo=False)
Session = sessionmaker(bind=engine)
session = Session()
menu_service = MenuService(session)

app = Flask(__name__)
app.secret_key = 'ksfiwqy239478i32hkbqwmehrkasdf'  # Replace with a secure key

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

        
UPLOAD_FOLDER = "static/images"  # Folder to store images
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class FlaskUser(UserMixin):
    def __init__(self, user):
        self.id = user.user_id
        self.role = user.role

@login_manager.user_loader
def load_user(user_id):
    user = session.get(User, user_id)
    return FlaskUser(user) if user else None

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = session.query(User).filter_by(email=email).first()
        if user and user.password == password:  # Direct comparison for now
            login_user(FlaskUser(user))
            return jsonify({'message': f'Logged in as {user.full_name}'})
        return jsonify({'error': 'Invalid email or password'}), 401
    return render_template('login.html')

# Test protected route
@app.route('/api/test', methods=['GET'])
@login_required
def test():
    return jsonify({'message': f'Hello, {current_user.id}!'})


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


# @app.route('/order')
# def order():
#     return render_template('order.html')

# http://127.0.0.1:5000/order_track use this for accessing this webpage.
@app.route('/order_track')
def order_track():
    return render_template('order_track.html')


# http://127.0.0.1:5000/delivery_details.html
# @app.route('/delivery_details')
# def delivery_details():
#     return render_template('delivery_details.html')
    





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
                MenuItem.discount_percentage,
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
                "discount_percentage": float(item.discount_percentage) if item.discount_percentage else 0,
            }
            for item in items
        ]

        session.close()
        return jsonify({'data':items_list,'ok':True})

    except Exception as e:
        session.close()
        logger.error(f"Error fetching menu items: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    
# API to fetch and update cart
@app.route('/api/cart', methods=['GET', 'POST'])
@login_required
def manage_cart():
    if request.method == 'GET':
        cart_items = (
            session.query(
                Cart.cart_id,
                Cart.menu_item_id,
                Cart.quantity,
                MenuItem.name.label("menu_item_name"),
                MenuItem.price
            )
            .join(MenuItem, Cart.menu_item_id == MenuItem.menu_item_id)
            .filter(Cart.user_id == current_user.id)
            .all()
        )
        data = [{
            'cart_id': item.cart_id,
            'menu_item_id': item.menu_item_id,
            'name': item.menu_item_name,
            'price': float(item.price),
            'quantity': item.quantity
        } for item in cart_items]
        return jsonify({'ok':True,'data': data})
    elif request.method == 'POST':
        items = request.json.get('items', [])
        # Clear existing cart for this user
        session.query(Cart).filter_by(user_id=current_user.id).delete()
        # Add new items
        for i, item in enumerate(items, 1):
            if item.get('quantity', 0) > 0:  # Only add items with quantity > 0
                latest_cart_id = menu_service.get_latest_id(Cart.cart_id)
                cart_item = Cart(
                    cart_id=generate_next_id(latest_cart_id, "C"),
                    # cart_id=f"C{str(i).zfill(3)}",  # Generate new cart_id (e.g., C001, C002)
                    user_id=current_user.id,
                    menu_item_id=item['menu_item_id'],
                    quantity=item['quantity']
                )
                session.add(cart_item)
        session.commit()
        return jsonify({'data': items, 'message': 'Cart updated successfully'})


# ORDER MANAGEMENT ENDPOINTS

# Order page route

@app.route('/order', methods=['GET', 'POST'])
@login_required
def order():
    if request.method == 'GET':
        cart_items = (
            session.query(
                Cart.cart_id,
                Cart.menu_item_id,
                Cart.quantity,
                MenuItem.name.label("menu_item_name"),
                MenuItem.price,
                MenuItem.discount_percentage
            )
            .join(MenuItem, Cart.menu_item_id == MenuItem.menu_item_id)
            .filter(Cart.user_id == current_user.id)
            .all()
        )
        cart_data = [{
            'cart_id': item.cart_id,
            'menu_item_id': item.menu_item_id,
            'name': item.menu_item_name,
            'price': float(item.price),
            'quantity': item.quantity,
            'discount_percentage': float(item.discount_percentage) if item.discount_percentage else 0
        } for item in cart_items]
        # Calculate totals
        subtotal = 0
        total_discount = 0
        for item in cart_data:
            item_total = item['price'] * item['quantity']
            item_discount = (item_total * item['discount_percentage']) / 100
            subtotal += item_total
            total_discount += item_discount
        tax = (subtotal - total_discount) * 0.18
        delivery_charge = 50.0
        total = subtotal - total_discount + tax + delivery_charge
        return render_template('order.html', cart_json=json.dumps(cart_data), total=total, subtotal=subtotal - total_discount, tax=tax, delivery_charge=delivery_charge)
    elif request.method == 'POST':
        # Redirect to delivery_details when "Place Order" is clicked
        return redirect(url_for('delivery_details'))

@app.route('/delivery_details')
@login_required
def delivery_details():
    cart_items = (
        session.query(
            Cart.cart_id,
            Cart.menu_item_id,
            Cart.quantity,
            MenuItem.name.label("menu_item_name"),
            MenuItem.price,
            MenuItem.discount_percentage
        )
        .join(MenuItem, Cart.menu_item_id == MenuItem.menu_item_id)
        .filter(Cart.user_id == current_user.id)
        .all()
    )
    cart_data = [{
        'cart_id': item.cart_id,
        'menu_item_id': item.menu_item_id,
        'name': item.menu_item_name,
        'price': float(item.price),
        'quantity': item.quantity,
        'discount_percentage': float(item.discount_percentage) if item.discount_percentage else 0
    } for item in cart_items]
    if not cart_data:
        return redirect(url_for('order'))  # Redirect back if cart is empty
    # Calculate totals
    subtotal = 0
    total_discount = 0
    for item in cart_data:
        item_total = item['price'] * item['quantity']
        item_discount = (item_total * item['discount_percentage']) / 100
        subtotal += item_total
        total_discount += item_discount
    tax = (subtotal - total_discount) * 0.18
    delivery_charge = 50.0
    total = subtotal - total_discount + tax + delivery_charge
    return render_template('delivery_details.html', cart_json=json.dumps(cart_data), total=total, subtotal=subtotal - total_discount, tax=tax, delivery_charge=delivery_charge)

@app.route('/api/orders', methods=['POST'])
@login_required
def place_customer_order():
    data = request.get_json()
    try:
        total = float(data.get('total', 0))
        subtotal = float(data.get('subtotal', 0))
        tax = float(data.get('tax', 0))
        delivery_charge = float(data.get('delivery_charge', 0))
        delivery_details = data.get('delivery_details', {})
        if total <= 0 or subtotal <= 0:
            return jsonify({"error": "Invalid total or subtotal"}), 400
        # Fetch cart from database
        cart_items = (
            session.query(Cart, MenuItem)
            .join(MenuItem, Cart.menu_item_id == MenuItem.menu_item_id)
            .filter(Cart.user_id == current_user.id)
            .all()
        )
        if not cart_items:
            return jsonify({"error": "Cart is empty"}), 400
        # Check stock
        for cart_item, menu_item in cart_items:
            if menu_item.stock_available < cart_item.quantity:
                return jsonify({"error": f"Insufficient stock for {menu_item.name}"}), 400
        # Create order
        latest_order_id = menu_service.get_latest_id(Order.order_id)
        order_id = generate_next_id(latest_order_id, "O")
        new_order = Order(
            order_id=order_id,
            user_id=current_user.id,
            delivery_agent_id=None,
            status="Pending",
            total_price=total,
            delivery_location=f"{delivery_details.get('street', '')}, {delivery_details.get('city', '')}, {delivery_details.get('state', '')} {delivery_details.get('pincode', '')}",
            payment_method=delivery_details.get('payment_method', 'cod'),
            coordinates=delivery_details.get('coordinates', ''),
            created_at=datetime.utcnow()
        )
        session.add(new_order)
        # Create order items and update stock
        for cart_item, menu_item in cart_items:
            latest_order_item_id = menu_service.get_latest_id(OrderItem.order_item_id)
            order_item_id = generate_next_id(latest_order_item_id, "OI")
            order_item = OrderItem(
                order_item_id=order_item_id,
                order_id=order_id,
                menu_item_id=cart_item.menu_item_id,
                quantity=cart_item.quantity,
                price=float(menu_item.price)
            )
            menu_item.stock_available -= cart_item.quantity
            session.add(order_item)
        # Clear cart
        session.query(Cart).filter_by(user_id=current_user.id).delete()
        session.commit()
        return jsonify({"message": "Order placed successfully", "order_id": order_id}), 201
    except Exception as e:
        session.rollback()
        logger.error(f"Error placing order: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/order_confirmation')
@login_required
def order_confirmation():
    order_id = request.args.get('order_id')
    if not order_id:
        return "Order ID not provided", 400

    # Fetch order details from the database
    order = (
        session.query(Order)
        .filter(Order.order_id == order_id, Order.user_id == current_user.id)
        .first()
    )
    if not order:
        return "Order not found", 404

    # Fetch order items with menu item details
    order_items = (
        session.query(OrderItem, MenuItem)
        .join(MenuItem, OrderItem.menu_item_id == MenuItem.menu_item_id)
        .filter(OrderItem.order_id == order_id)
        .all()
    )

    # Prepare cart_items data for the template
    cart_data = [{
        'menu_item_id': item.OrderItem.menu_item_id,
        'name': item.MenuItem.name,
        'quantity': item.OrderItem.quantity,
        'price': float(item.OrderItem.price),  # Ensure price is float
        'discount_percentage': float(item.MenuItem.discount_percentage) if item.MenuItem.discount_percentage else 0
    } for item in order_items]

    # Convert Decimal to float for calculations
    total_price = float(order.total_price)  # Convert Decimal to float

    # Prepare order data for the template
    delivery_details = {
        'street': order.delivery_location.split(', ')[0] if order.delivery_location else '',
        'city': order.delivery_location.split(', ')[1] if order.delivery_location and len(order.delivery_location.split(', ')) > 1 else '',
        'state': order.delivery_location.split(', ')[2].split(' ')[0] if order.delivery_location and len(order.delivery_location.split(', ')) > 2 else '',
        'pincode': order.delivery_location.split(', ')[2].split(' ')[1] if order.delivery_location and len(order.delivery_location.split(', ')) > 2 else '',
        'coordinates': order.coordinates,
        'payment_method': order.payment_method
    }

    order_data = {
        'order_id': order.order_id,
        'ordered_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S') if order.created_at else datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        'payment_method': order.payment_method,
        'total': total_price,
        'subtotal': total_price - (total_price * 0.18) - 50.0,  # Reverse calculate subtotal (all floats now)
        'tax': total_price * 0.18,  # 18% tax as float
        'delivery_charge': 50.0,  # Fixed delivery charge
        'delivery_details': delivery_details,
        'tracking_id': order.order_id  # Using order_id as tracking_id for simplicity
    }

    # Mock agent data (replace with actual logic if you have a DeliveryAgent table)
    agent_data = {
        'name': "Ravi Kumar",
        'contact': "+91 98765 43210"
    }

    return render_template('order_confirmation.html',
                          order_json=order_data,
                          cart_items_json=cart_data,
                          agent_json=agent_data)


if __name__ == '__main__':
    # print("Creating tables...")
    # Base.metadata.create_all(bind=engine)
    app.run(debug=True)
    