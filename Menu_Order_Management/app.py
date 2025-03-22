from flask import Flask, request, render_template, redirect, url_for, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user
from sqlalchemy import create_engine, func, asc, desc
from sqlalchemy.orm import sessionmaker
from database.create_database import Base, MenuItem, Category, Subcategory, Cart, User, Order, OrderItem, DeliveryAgent
from database.services import MenuService, generate_next_id
from apscheduler.schedulers.background import BackgroundScheduler
import os
import logging
import json
from datetime import datetime, timezone
import pytz
import datetime as dt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create connection to database
engine = create_engine("sqlite:///hifi_database.db", echo=False)
Session = sessionmaker(bind=engine)
session = Session()
menu_service = MenuService(session)

app = Flask(__name__)
# app.secret_key = 'ksfiwqy239478i32hkbqwmehrkasdf'  # Replace with a secure key
app.secret_key = 'sdfasdrwersdasdfas345ads'  
# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.start()


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

# http://127.0.0.1:5000/admin.html
@app.route('/admin')
def admin():
    return render_template('admin.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

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

# Function to apply scheduled updates
def apply_scheduled_updates():
    with app.app_context():
        try:
            now = datetime.now(dt.UTC)
            logger.info(f"Checking updates at {now} UTC")
            pending_items = session.query(MenuItem).filter(
                MenuItem.scheduled_update_time <= now,
                MenuItem.pending_update.isnot(None)
            ).all()
            logger.info(f"Found {len(pending_items)} items to update")
            if pending_items:
                for item in pending_items:
                    logger.info(f"Item {item.menu_item_id}: scheduled_update_time={item.scheduled_update_time}, pending_update={item.pending_update}")
            else:
                # Log all items with pending updates to diagnose
                all_pending = session.query(MenuItem).filter(MenuItem.pending_update.isnot(None)).all()
                logger.info(f"All items with pending updates: {len(all_pending)}")
                for item in all_pending:
                    logger.info(f"Excluded item {item.menu_item_id}: scheduled_update_time={item.scheduled_update_time}")
            for item in pending_items:
                updates = json.loads(item.pending_update)
                logger.info(f"Updating item {item.menu_item_id} with {updates}")
                for key, value in updates.items():
                    if key == "price":
                        item.price = float(value)
                    elif key == "stock_available":
                        item.stock_available = int(value)
                        item.is_out_of_stock = int(value) == 0
                    elif key == "discount_percentage":
                        item.discount_percentage = float(value)
                    elif key == "is_best_seller":
                        item.is_best_seller = bool(value)
                    elif key == "name":
                        item.name = value
                    elif key == "description":
                        item.description = value
                    elif key == "category_name":
                        category = session.query(Category).filter(func.lower(Category.name) == value.lower()).first()
                        if category:
                            item.category_id = category.category_id
                    elif key == "subcategory_name":
                        subcategory = session.query(Subcategory).filter(func.lower(Subcategory.name) == value.lower()).first()
                        if subcategory:
                            item.subcategory_id = subcategory.subcategory_id
                item.pending_update = None
                item.scheduled_update_time = None
            session.commit()
            logger.info(f"Applied scheduled updates to {len(pending_items)} items")
        except Exception as e:
            session.rollback()
            logger.error(f"Error applying scheduled updates: {e}", exc_info=True)
        finally:
            session.close()
# Schedule the task to run every minute
scheduler.add_job(apply_scheduled_updates, 'interval', minutes=1)

@app.route('/add_item', methods=["POST"])
def add_item():
    try:
        data = request.form
        scheduled_time = data.get("scheduled_update_time")
        if scheduled_time and scheduled_time.strip():
            # Assume input is IST, convert to UTC
            ist_tz = pytz.timezone('Asia/Kolkata')
            scheduled_dt = datetime.fromisoformat(scheduled_time)
            scheduled_ist = ist_tz.localize(scheduled_dt)
            scheduled_update_time = scheduled_ist.astimezone(timezone.utc)
            logger.info(f"Converted {scheduled_time} IST to {scheduled_update_time} UTC")
        else:
            scheduled_update_time = None
            
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
        
        # If scheduled, store as pending update
        if scheduled_update_time:
            pending_update = {
                "name": item_name,
                "description": description,
                "price": price,
                "category_name": category_name,
                "subcategory_name": subcategory_name,
                "discount_percentage": discount,
                "is_best_seller": best_seller,
                "stock_available": stock_available
            }
            new_item = MenuItem(
                menu_item_id=generate_next_id(menu_service.get_latest_id(MenuItem.menu_item_id), "MI"),
                name="Pending Item",  # Placeholder until scheduled
                description="Pending",
                price=0.0,
                image_url=image_url,
                category_id=session.query(Category).filter_by(name=category_name).first().category_id,
                subcategory_id=session.query(Subcategory).filter_by(name=subcategory_name).first().subcategory_id,
                nutrient_value="N/A",
                calorie_count=0,
                is_best_seller=False,
                is_out_of_stock=True,
                discount_percentage=0.0,
                stock_available=0,
                scheduled_update_time=scheduled_update_time,
                pending_update=json.dumps(pending_update)
            )
        else:
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

        session.add(new_item)
        session.commit()
        
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
            "stock_available": item.MenuItem.stock_available,
            "scheduled_update_time": (
                    item.MenuItem.scheduled_update_time.isoformat()
                    if item.MenuItem.scheduled_update_time else None),  # Handle None explicitly
            "pending_update": item.MenuItem.pending_update  # Include pending_update if added
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
        
        scheduled_time = data.get("scheduled_update_time")
        scheduled_update_time = datetime.fromisoformat(scheduled_time) if scheduled_time else None
        
        # Fetch the menu item from the database
        menu_item = session.query(MenuItem).filter_by(menu_item_id=menu_item_id).first()
        if not menu_item:
            return jsonify({"error": "Menu item not found"}), 404

        
        # If scheduled, store changes in pending_update
        if scheduled_update_time:
            pending_update = {
                "name": data.get("name", menu_item.name),
                "description": data.get("description", menu_item.description),
                "price": float(data.get("price", menu_item.price)),
                "category_name": data.get("category_name", menu_item.category.name),
                "subcategory_name": data.get("subcategory_name", menu_item.subcategory.name),
                "discount_percentage": float(data.get("discount_percentage", menu_item.discount_percentage or 0)),
                "is_best_seller": data.get("is_best_seller", menu_item.is_best_seller),
                "stock_available": int(data.get("stock_available", menu_item.stock_available))
            }
            menu_item.scheduled_update_time = scheduled_update_time
            menu_item.pending_update = json.dumps(pending_update)
        else:
            # Apply changes immediately
            menu_item.name = data.get("name", menu_item.name)
            menu_item.description = data.get("description", menu_item.description)
            menu_item.price = data.get("price", menu_item.price)
            menu_item.discount_percentage = data.get("discount_percentage", menu_item.discount_percentage)
            menu_item.is_best_seller = data.get("is_best_seller", menu_item.is_best_seller)
            menu_item.stock_available = data.get("stock_available", menu_item.stock_available)
            menu_item.is_out_of_stock = int(data.get("stock_available", menu_item.stock_available)) == 0

            if "category_name" in data:
                category = session.query(Category).filter(func.lower(Category.name) == data["category_name"].lower()).first()
                if category:
                    menu_item.category_id = category.category_id
            if "subcategory_name" in data:
                subcategory = session.query(Subcategory).filter(func.lower(Subcategory.name) == data["subcategory_name"].lower()).first()
                if subcategory:
                    menu_item.subcategory_id = subcategory.subcategory_id

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

# New Endpoint: Fetch User 1's Order History
# Updated /api/user_order_history endpoint
@app.route('/api/user_order_history', methods=['GET'])
@login_required
def get_user_order_history():
    try:
        user_id = current_user.id 
        orders = session.query(Order).filter(Order.user_id == user_id).all()
            
        if not orders:  # If no orders exist, mark as new user
            return jsonify({'data': [], 'is_new_user': True, 'ok': True})
        order_items = session.query(OrderItem).join(Order).filter(Order.user_id == user_id).all()
        
        order_history = []
        for item in order_items:
            menu_item = session.query(MenuItem).filter(MenuItem.menu_item_id == item.menu_item_id).first()
            order_history.append({
                'order_id': item.order_id,
                'menu_item_id': item.menu_item_id,
                'name': menu_item.name,
                'subcategory_name': menu_item.subcategory.name if menu_item.subcategory else None,
                'category_name': menu_item.category.name if menu_item.category else None,
                'quantity': item.quantity,
                'price': float(item.price),
                'ordered_at': item.order.created_at.isoformat()
            })
        
        return jsonify({'data': order_history, 'is_new_user': False, 'ok': True})
    except Exception as e:
        logger.error(f"Error fetching user order history: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
        
        
# New /api/recommendations endpoint
@app.route('/api/recommendations', methods=['GET'])
@login_required
def get_recommendations():
    try:
        user_id = current_user.id
        orders = session.query(Order).filter(Order.user_id == user_id).all()
        
        if not orders:  # New user, no recommendations
            return jsonify({'data': [], 'is_new_user': True, 'ok': True})
        # Get ordered items and their subcategories
        order_items = session.query(OrderItem).join(Order).filter(Order.user_id == user_id).all()
        ordered_item_ids = {item.menu_item_id for item in order_items}
        ordered_subcategories = {
            session.query(MenuItem).filter(MenuItem.menu_item_id == item.menu_item_id).first().subcategory.name
            for item in order_items
        }
        # Fetch all menu items and filter recommendations
        all_menu_items = session.query(MenuItem).all()
        recommendations = [
            {
                'menu_item_id': item.menu_item_id,
                'name': item.name,
                'price': float(item.price),
                'subcategory_name': item.subcategory.name if item.subcategory else None,
                'category_name': item.category.name if item.category else None,
                'description': item.description,
                'image_url': item.image_url,
                'is_out_of_stock': item.is_out_of_stock,
                'stock_available': item.stock_available
            }
            for item in all_menu_items
            if (item.subcategory.name in ordered_subcategories and 
                item.menu_item_id not in ordered_item_ids and 
                not item.is_out_of_stock)
        ]
        # Limit to 5 recommendations (adjust as needed)
        recommendations = recommendations[:5]
        
        return jsonify({'data': recommendations, 'is_new_user': False, 'ok': True})
    except Exception as e:
        logger.error(f"Error fetching recommendations: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
        

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

# http://127.0.0.1:5000/order_confirmation?order_id=O001
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



@app.route('/api/admin/pending_orders', methods=['GET'])
@login_required
def get_pending_orders():
    # if current_user.role != 'admin':
    #     return jsonify({"error": "Unauthorized access"}), 403

    try:
        # Fetch pending orders with user and order items
        orders = (
            session.query(Order, User)
            .join(User, Order.user_id == User.user_id)
            .filter(Order.status == "Pending")
            .all()
        )

        orders_list = []
        for order, user in orders:
            # Fetch order items
            order_items = (
                session.query(OrderItem, MenuItem)
                .join(MenuItem, OrderItem.menu_item_id == MenuItem.menu_item_id)
                .filter(OrderItem.order_id == order.order_id)
                .all()
            )
            items = [{
                'itemId': item.OrderItem.menu_item_id,
                'itemName': item.MenuItem.name,
                'quantity': item.OrderItem.quantity,
                'price': float(item.OrderItem.price),
                'image': item.MenuItem.image_url
            } for item in order_items]

            delivery_parts = order.delivery_location.split(', ') if order.delivery_location else ['', '', '']
            state_pin = delivery_parts[2].split(' ') if len(delivery_parts) > 2 else ['', '']

            orders_list.append({
                'orderId': order.order_id,
                'date': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'items': items,
                'total': float(order.total_price),
                'name': user.full_name,
                'phone': user.phone,
                'street': delivery_parts[0],
                'city': delivery_parts[1] if len(delivery_parts) > 1 else '',
                'state': state_pin[0] if state_pin else '',
                'pincode': state_pin[1] if len(state_pin) > 1 else '',
                'status': order.status
            })

        return jsonify({'data': orders_list, 'ok': True})
    except Exception as e:
        logger.error(f"Error fetching pending orders: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/admin/delivery_agents', methods=['GET'])
@login_required
def get_delivery_agents():
    # if current_user.role != 'admin':
    #     return jsonify({"error": "Unauthorized access"}), 403

    try:
        agents = session.query(DeliveryAgent).all()
        agents_list = [{
            'name': agent.name,
            'status': agent.availability_status.lower(),
            'delivery_agent_id': agent.delivery_agent_id  # Include for assignment later
        } for agent in agents]
        return jsonify({'data': agents_list, 'ok': True})
    except Exception as e:
        logger.error(f"Error fetching delivery agents: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route('/api/admin/assign_order', methods=['POST'])
@login_required
def assign_order():
    # if current_user.role != 'admin':
    #     return jsonify({"error": "Unauthorized access"}), 403

    data = request.get_json()
    order_id = data.get('order_id')
    delivery_agent_id = data.get('delivery_agent_id')

    try:
        order = session.query(Order).filter_by(order_id=order_id).first()
        if not order or order.status != "Pending":
            return jsonify({"error": "Order not found or not pending"}), 404

        agent = session.query(DeliveryAgent).filter_by(delivery_agent_id=delivery_agent_id).first()
        if not agent:
            return jsonify({"error": "Delivery agent not found"}), 404
        if agent.availability_status != "Available":
            return jsonify({"error": "Agent not available"}), 400

        order.delivery_agent_id = delivery_agent_id
        order.status = "Preparing"
        agent.availability_status = "Busy"

        session.commit()
        return jsonify({"message": f"Order {order_id} assigned to {agent.name}", "ok": True}), 200
    except Exception as e:
        session.rollback()
        logger.error(f"Error assigning order: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/reject_order', methods=['POST'])
@login_required
def reject_order():
    # if current_user.role != 'admin':
    #     return jsonify({"error": "Unauthorized access"}), 403

    data = request.get_json()
    order_id = data.get('order_id')

    try:
        order = session.query(Order).filter_by(order_id=order_id).first()
        if not order or order.status != "Pending":
            return jsonify({"error": "Order not found or not pending"}), 404

        order.status = "Cancelled"
        session.commit()
        return jsonify({"message": f"Order {order_id} rejected", "ok": True}), 200
    except Exception as e:
        session.rollback()
        logger.error(f"Error rejecting order: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    


# New Endpoint: Summary Statistics
@app.route('/api/admin/summary', methods=['GET'])
@login_required
def get_summary():
    # if current_user.role != 'admin':
    #     return jsonify({"error": "Unauthorized access"}), 403
    try:
        total_orders = session.query(func.count(Order.order_id)).scalar()
        total_revenue = session.query(func.sum(Order.total_price)).scalar() or 0.0
        cancelled_orders = session.query(func.count(Order.order_id)).filter(Order.status == "Cancelled").scalar()
        delivered_orders = session.query(func.count(Order.order_id)).filter(Order.status == "Delivered").scalar()
        summary = {
            "total_orders": total_orders,
            "total_revenue": float(total_revenue),  # Convert Decimal to float for JSON
            "cancelled_orders": cancelled_orders,
            "delivered_orders": delivered_orders
        }
        return jsonify({"data": summary, "ok": True})
    except Exception as e:
        logger.error(f"Error fetching summary: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# New Endpoint: Order Status Chart Data
@app.route('/api/admin/order_status_chart', methods=['GET'])
@login_required
def get_order_status_chart():
    # if current_user.role != 'admin':
    #     return jsonify({"error": "Unauthorized access"}), 403
    try:
        status_counts = session.query(Order.status, func.count(Order.order_id)).group_by(Order.status).all()
        chart_data = {status: count for status, count in status_counts}
        # Ensure all statuses are included, even if count is 0
        all_statuses = ["Pending", "Preparing", "Out for Delivery", "Delivered", "Cancelled"]
        for status in all_statuses:
            if status not in chart_data:
                chart_data[status] = 0
        return jsonify({"data": chart_data, "ok": True})
    except Exception as e:
        logger.error(f"Error fetching chart data: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500



# New Endpoint: Fetch All Orders with Pagination and Sorting
@app.route('/api/admin/all_orders', methods=['GET'])
@login_required
def get_all_orders():
    # if current_user.role != 'admin':
    #     return jsonify({"error": "Unauthorized access"}), 403
    try:
        # Pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        offset = (page - 1) * per_page
        # Sorting parameters
        sort_by = request.args.get('sort_by', 'order_id')  # Default sort by order_id
        sort_dir = request.args.get('sort_dir', 'asc')  # Default ascending
        sort_func = asc if sort_dir.lower() == 'asc' else desc
        # Valid sortable columns
        valid_columns = {'order_id': Order.order_id, 'status': Order.status, 'created_at': Order.created_at, 'total_price': Order.total_price}
        sort_column = valid_columns.get(sort_by, Order.order_id)  # Fallback to order_id
        # Query orders with sorting and pagination
        total_orders = session.query(func.count(Order.order_id)).scalar()
        orders_query = session.query(Order).join(User, Order.user_id == User.user_id).order_by(sort_func(sort_column)).limit(per_page).offset(offset)
        orders = orders_query.all()
        orders_list = [{
            'order_id': order.order_id,
            'customer_name': order.user.full_name,
            'status': order.status,
            'total_price': float(order.total_price),
            'created_at': order.created_at.isoformat(),
            'delivery_agent_id': order.delivery_agent_id or 'Not Assigned'
        } for order in orders]
        return jsonify({
            'data': orders_list,
            'total': total_orders,
            'page': page,
            'per_page': per_page,
            'total_pages': (total_orders + per_page - 1) // per_page,
            'ok': True
        })
    except Exception as e:
        logger.error(f"Error fetching all orders: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500




if __name__ == '__main__':
    # print("Creating tables...")
    # Base.metadata.create_all(bind=engine)
    app.run(debug=True)
    