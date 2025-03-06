from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fooddelivery.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    __table_name__ = 'user'
    user_id = db.Column(db.String, primary_key=True)
    full_name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.String)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.Date, default=db.func.current_date())
    updated_at = db.Column(db.Date, onupdate=db.func.current_date())

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class Category(db.Model):
    __table_name__ = 'category'
    category_id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class MenuItem(db.Model):
    __table_name__ = 'menu_item'
    menu_item_id = db.Column(db.String, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String)
    category_id = db.Column(db.String, db.ForeignKey('category.category_id'))
    nutrient_value = db.Column(db.String)
    calorie_count = db.Column(db.Integer)
    is_best_seller = db.Column(db.Boolean, default=False)
    is_out_of_stock = db.Column(db.Boolean, default=False)
    discount_percentage = db.Column(db.Float)
    scheduled_update_time = db.Column(db.Date)
    rating = db.Column(db.Float)  # Added for sorting by rating

    def to_dict(self):
        return {
            'menu_item_id': self.menu_item_id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'image_url': self.image_url,
            'category_id': self.category_id,
            'nutrient_value': self.nutrient_value,
            'calorie_count': self.calorie_count,
            'is_best_seller': self.is_best_seller,
            'is_out_of_stock': self.is_out_of_stock,
            'discount_percentage': self.discount_percentage,
            'scheduled_update_time': self.scheduled_update_time,
            'rating': self.rating
        }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class Cart(db.Model):
    __table_name__ = 'cart'
    cart_id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('user.user_id'), nullable=False)
    menu_item_id = db.Column(db.String, db.ForeignKey('menu_item.menu_item_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    added_at = db.Column(db.Date, default=db.func.current_date())
    custom_instructions = db.Column(db.String)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class Order(db.Model):
    __table_name__ = 'order'
    order_id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('user.user_id'), nullable=False)
    delivery_agent_id = db.Column(db.String, db.ForeignKey('delivery_agent.delivery_agent_id'))
    status = db.Column(db.String, default='pending')
    total_price = db.Column(db.Float, nullable=False)
    delivery_location = db.Column(db.String, nullable=False)
    created_at = db.Column(db.Date, default=db.func.current_date())
    payment_method = db.Column(db.String, default='COD')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class OrderItem(db.Model):
    __table_name__ = 'order_item'
    order_item_id = db.Column(db.String, primary_key=True)
    order_id = db.Column(db.String, db.ForeignKey('order.order_id'), nullable=False)
    menu_item_id = db.Column(db.String, db.ForeignKey('menu_item.menu_item_id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class DeliveryAgent(db.Model):
    __table_name__ = 'delivery_agent'
    delivery_agent_id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('user.user_id'), nullable=False)
    availability_status = db.Column(db.String)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class Favorite(db.Model):
    __table_name__ = 'favorite'
    favorite_id = db.Column(db.String, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('user.user_id'), nullable=False)
    menu_item_id = db.Column(db.String, db.ForeignKey('menu_item.menu_item_id'), nullable=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

# API Endpoints
@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': 'Welcome to Food Delivery API',
        'endpoints': {
            '/cart/add': 'Add items to cart (POST)',
            '/order/summary': 'Get order summary (POST)',
            '/menu/items': 'Get menu items (GET)',
            '/favorites/list/<user_id>': 'List favorite items (GET)'
        }
    })

@app.route('/cart/add', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    user_id = data['user_id']
    menu_item_id = data['menu_item_id']
    quantity = data['quantity']
    custom_instructions = data.get('custom_instructions', '')

    cart_item = Cart(
        cart_id=f"C{len(Cart.query.all()) + 1:03d}",
        user_id=user_id,
        menu_item_id=menu_item_id,
        quantity=quantity,
        custom_instructions=custom_instructions
    )
    db.session.add(cart_item)
    db.session.commit()
    return jsonify({"message": "Item added to cart"}), 201

@app.route('/order/summary', methods=['POST'])
def order_summary():
    data = request.get_json()
    user_id = data['user_id']
    cart_items = Cart.query.filter_by(user_id=user_id).all()

    subtotal = 0
    for item in cart_items:
        menu_item = MenuItem.query.get(item.menu_item_id)
        if menu_item:
            subtotal += menu_item.price * item.quantity
        else:
            pass

    tax = subtotal * 0.1
    delivery_charge = 5.0
    total_price = subtotal + tax + delivery_charge

    return jsonify({
        "subtotal": subtotal,
        "tax": tax,
        "delivery_charge": delivery_charge,
        "total_price": total_price
    })

@app.route('/order/check_location', methods=['POST'])
def check_location():
    data = request.get_json()
    delivery_location = data['delivery_location']
    service_areas = ['Area1', 'Area2', 'Area3']  # Replace with actual data
    if delivery_location in service_areas:
        return jsonify({"message": "Location is within service area"}), 200
    else:
        return jsonify({"message": "Location is outside service area"}), 400

@app.route('/order/confirm', methods=['POST'])
def confirm_order():
    data = request.get_json()
    user_id = data['user_id']
    delivery_location = data['delivery_location']
    estimated_delivery_time = (datetime.now() + timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S")
    return jsonify({"message": "Order confirmed", "estimated_delivery_time": estimated_delivery_time}), 200

@app.route('/order/payment_method', methods=['POST'])
def set_payment_method():
    data = request.get_json()
    order_id = data['order_id']
    payment_method = data['payment_method']
    order = Order.query.get(order_id)
    if order:
        order.payment_method = payment_method
        db.session.commit()
        return jsonify({"message": "Payment method updated"}), 200
    else:
        return jsonify({"message": "Order not found"}), 404

@app.route('/order/delivery_agent_info/<order_id>', methods=['GET'])
def get_delivery_agent_info(order_id):
    order = Order.query.get(order_id)
    if order:
        delivery_agent = DeliveryAgent.query.get(order.delivery_agent_id)
        if delivery_agent:
            user = User.query.get(delivery_agent.user_id)
            if user:
                return jsonify({"name": user.full_name, "phone": user.phone})
            else:
                return jsonify({"message": "User not found for delivery agent"}), 404
        else:
            return jsonify({"message": "No delivery agent assigned yet"}), 404
    else:
        return jsonify({"message": "Order not found"}), 404

@app.route('/order/apply_discount', methods=['POST'])
def apply_discount():
    data = request.get_json()
    discount_code = data['discount_code']
    user_id = data['user_id']
    if discount_code == "VALIDCODE":
        return jsonify({"message": "Discount applied successfully"}), 200
    else:
        return jsonify({"message": "Invalid discount code"}), 400

@app.route('/cart/update/<cart_id>', methods=['PUT'])
def update_cart_item(cart_id):
    data = request.get_json()
    quantity = data['quantity']
    custom_instructions = data.get('custom_instructions', '')
    cart_item = Cart.query.get(cart_id)
    if cart_item:
        cart_item.quantity = quantity
        cart_item.custom_instructions = custom_instructions
        db.session.commit()
        return jsonify({"message": "Cart item updated"}), 200
    else:
        return jsonify({"message": "Cart item not found"}), 404

@app.route('/cart/remove/<cart_id>', methods=['DELETE'])
def remove_cart_item(cart_id):
    cart_item = Cart.query.get(cart_id)
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify({"message": "Cart item removed"}), 200
    else:
        return jsonify({"message": "Cart item not found"}), 404

@app.route('/favorites/add', methods=['POST'])
def add_favorite():
    data = request.get_json()
    user_id = data['user_id']
    menu_item_id = data['menu_item_id']
    favorite = Favorite(
        favorite_id=f"F{len(Favorite.query.all()) + 1:03d}",
        user_id=user_id,
        menu_item_id=menu_item_id
    )
    db.session.add(favorite)
    db.session.commit()
    return jsonify({"message": "Favorite added"}), 201

@app.route('/favorites/list/<user_id>', methods=['GET'])
def list_favorites(user_id):
    favorites = Favorite.query.filter_by(user_id=user_id).all()
    favorite_items = [fav.menu_item_id for fav in favorites]
    menu_items = [MenuItem.query.get(item_id) for item_id in favorite_items]
    menu_items_list = [item.to_dict() for item in menu_items if item]
    return jsonify(menu_items_list), 200

@app.route('/menu/sort', methods=['GET'])
def sort_menu():
    sort_by = request.args.get('sort_by', 'popularity')
    if sort_by == 'rating':
        menu_items = MenuItem.query.order_by(MenuItem.rating.desc()).all()
    elif sort_by == 'popularity':
        menu_items = MenuItem.query.order_by(MenuItem.is_best_seller.desc()).all()
    else:
        menu_items = MenuItem.query.all()
    return jsonify([item.to_dict() for item in menu_items]), 200

@app.route('/menu/items', methods=['GET'])
def get_menu_items():
    menu_items = MenuItem.query.all()
    return jsonify([item.to_dict() for item in menu_items]), 200

@app.route('/order/create', methods=['POST'])
def create_order():
    data = request.get_json()
    user_id = data['user_id']
    delivery_location = data['delivery_location']
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    total_price = 0
    for item in cart_items:
        menu_item = MenuItem.query.get(item.menu_item_id)
        if menu_item:
            total_price += menu_item.price * item.quantity
        else:
            pass

    order = Order(
        order_id=f"O{len(Order.query.all()) + 1:03d}",
        user_id=user_id,
        total_price=total_price + 5.0,
        delivery_location=delivery_location
    )
    db.session.add(order)

    for item in cart_items:
        menu_item = MenuItem.query.get(item.menu_item_id)
        if menu_item:
            order_item = OrderItem(
                order_item_id=f"OI{len(OrderItem.query.all()) + 1:03d}",
                order_id=order.order_id,
                menu_item_id=item.menu_item_id,
                quantity=item.quantity,
                price=menu_item.price
            )
            db.session.add(order_item)

    Cart.query.filter_by(user_id=user_id).delete()
    db.session.commit()

    return jsonify({"message": "Order created, cart emptied", "order_id": order.order_id}), 201

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=8080)