from flask_login import UserMixin
from sqlalchemy import func
from app import db
from datetime import datetime

'''
PRIMARY KEY ID MAPPING:
-----------------------
    address: ADD001
    admin: A001
    customer: U001
    delivery_agent: DA001
    delivery_feedback: DF001
    earnings: E001
    cart: C001
    categories: IC001
    menu_items: MI001
    order_item: OI001
    orders: O001
    subcategory: ISC001
'''

# Admin Model
class Admin(UserMixin, db.Model):
    __tablename__ = 'admin'
    admin_id = db.Column(db.String(10), primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.Integer, unique=True, nullable=False)

    def __repr__(self):
        return f'<Admin {self.username}>'

    def get_id(self):
        return f"admin:{self.admin_id}"

# Customer Model (replaces User)
class Customer(UserMixin, db.Model):
    __tablename__ = 'customer'
    customer_id = db.Column(db.String(10), primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.Integer, unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    # address = db.Column(db.String(100), nullable=False)
    # created_at = db.Column(db.DateTime, default=func.now())
    
    # Relationship
    addresses = db.relationship("Address", back_populates="customer", lazy=True)
    orders = db.relationship("Order", back_populates="customer", foreign_keys="Order.customer_id")
    cart_items = db.relationship("Cart", back_populates="customer")

    def __repr__(self):
        return f'<Customer {self.username}>'
    def get_id(self):
        return f"customer:{self.customer_id}"

# Address Model
class Address(db.Model):
    __tablename__ = 'address'
    address_id = db.Column(db.String(10), primary_key=True)
    customer_id = db.Column(db.String(10), db.ForeignKey('customer.customer_id'), nullable=False)
    address_line = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    zip_code = db.Column(db.String(20), nullable=False)
    is_preferred = db.Column(db.Boolean, default=False)

    # Relationship
    customer = db.relationship("Customer", back_populates="addresses")

    def __repr__(self):
        return f'<Address {self.address_line}>'

# DeliveryAgent Model
class DeliveryAgent(UserMixin, db.Model):
    __tablename__ = 'delivery_agent'
    delivery_agent_id = db.Column(db.String(10), primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    phone = db.Column(db.Integer, unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    image = db.Column(db.String(255), nullable=True, server_default='')
    bio = db.Column(db.Text, nullable=True, server_default='')
    delivery_area = db.Column(db.String(100), nullable=False)
    available_slots = db.Column(db.Boolean, nullable=False, default=True)
    id_proof = db.Column(db.String(12), nullable=False, server_default='')
    is_approved = db.Column(db.Boolean, nullable=False, server_default='0')
    is_active = db.Column(db.Boolean, nullable=False, server_default='1')

    # Relationship
    earnings = db.relationship("Earnings", back_populates="delivery_agent")
    delivery_feedbacks = db.relationship("DeliveryFeedback", back_populates="delivery_agent")
    deliveries = db.relationship("Order", back_populates="delivery_agent", foreign_keys="Order.delivery_agent_id")

    def __repr__(self):
        return f'<DeliveryAgent {self.username}>'

    def get_id(self):
        return f"delivery:{self.delivery_agent_id}"

# Earnings Model
class Earnings(db.Model):
    __tablename__ = 'earnings'
    earnings_id = db.Column(db.String(10), primary_key=True)
    delivery_agent_id = db.Column(db.String(10), db.ForeignKey('delivery_agent.delivery_agent_id'), nullable=False)
    base_pay = db.Column(db.Float, nullable=False, default=0.0)
    bonus = db.Column(db.Float, nullable=False, default=0.0)
    trips_count = db.Column(db.Integer, nullable=False, default=0)
    earned_at = db.Column(db.DateTime, default=func.now)

    # Relationship
    delivery_agent = db.relationship("DeliveryAgent", back_populates="earnings")

    def __repr__(self):
        return f'<Earnings {self.delivery_agent_id} - {self.earned_at}>'

# DeliveryFeedback Model
class DeliveryFeedback(db.Model):
    __tablename__ = 'delivery_feedback'
    delivery_feedback_id = db.Column(db.String(10), primary_key=True)
    order_id = db.Column(db.String(10), db.ForeignKey('orders.order_id'), nullable=False)
    delivery_agent_id = db.Column(db.String(10), db.ForeignKey('delivery_agent.delivery_agent_id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    feedback = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=func.now)

    # Relationships
    order = db.relationship("Order", back_populates="delivery_feedbacks")
    delivery_agent = db.relationship("DeliveryAgent", back_populates="delivery_feedbacks")

    def __repr__(self):
        return f'<DeliveryFeedback Order:{self.order_id} Agent:{self.delivery_agent_id} Rating:{self.rating}>'

# Category Model
class Category(db.Model):
    __tablename__ = "categories"
    category_id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    # Relationship
    menu_items = db.relationship("MenuItem", back_populates="category")

# Subcategory Model
class Subcategory(db.Model):
    __tablename__ = "subcategories"
    subcategory_id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    category_id = db.Column(db.String(10), db.ForeignKey("categories.category_id", ondelete="CASCADE"), nullable=False)

    # Relationship
    menu_items = db.relationship("MenuItem", back_populates="subcategory")

# MenuItem Model
class MenuItem(db.Model):
    __tablename__ = "menu_items"
    menu_item_id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.DECIMAL(10, 2), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    category_id = db.Column(db.String(10), db.ForeignKey("categories.category_id", ondelete="CASCADE"), nullable=False)
    subcategory_id = db.Column(db.String(10), db.ForeignKey("subcategories.subcategory_id", ondelete="CASCADE"), nullable=False)
    nutrient_value = db.Column(db.String(255), nullable=False)
    calorie_count = db.Column(db.Integer, nullable=False)
    is_best_seller = db.Column(db.Boolean, default=False)
    is_out_of_stock = db.Column(db.Boolean, default=False)
    discount_percentage = db.Column(db.DECIMAL(5, 2), nullable=True)
    stock_available = db.Column(db.Integer, default=100)
    scheduled_update_time = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)

    # Relationships
    category = db.relationship("Category", back_populates="menu_items")
    subcategory = db.relationship("Subcategory", back_populates="menu_items")
    order_items = db.relationship("OrderItem", back_populates="menu_item")
    cart_items = db.relationship("Cart", back_populates="menu_item")

    def __repr__(self):
        return f'<MenuItem {self.name}, Price: {self.price}>'

# Order Model
class Order(db.Model):
    __tablename__ = "orders"
    order_id = db.Column(db.String(10), primary_key=True)
    customer_id = db.Column(db.String(10), db.ForeignKey("customer.customer_id", ondelete="CASCADE"), nullable=False)
    delivery_agent_id = db.Column(db.String(10), db.ForeignKey("delivery_agent.delivery_agent_id", ondelete="SET NULL"), nullable=True)
    status = db.Column(db.Enum("Pending", "Preparing", "Out for Delivery", "Delivered", "Cancelled", name="order_status"), nullable=False, default="Pending")
    total_price = db.Column(db.DECIMAL(10, 2), nullable=False)
    delivery_location = db.Column(db.Text, nullable=False)
    # payment_method = db.Column(db.Enum("cod", "online", name="payment_methods"), nullable=False)
    # coordinates = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    delivered_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    customer = db.relationship("Customer", back_populates="orders", foreign_keys=[customer_id])
    delivery_agent = db.relationship("DeliveryAgent", back_populates="deliveries")
    order_items = db.relationship("OrderItem", back_populates="order")
    delivery_feedbacks = db.relationship("DeliveryFeedback", back_populates="order")

    def __repr__(self):
        return f'<Order {self.order_id}, Status: {self.status}>'

# OrderItem Model
class OrderItem(db.Model):
    __tablename__ = "order_item"
    order_item_id = db.Column(db.String(10), primary_key=True)
    order_id = db.Column(db.String(10), db.ForeignKey("orders.order_id", ondelete="CASCADE"), nullable=False)
    menu_item_id = db.Column(db.String(10), db.ForeignKey("menu_items.menu_item_id", ondelete="CASCADE"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.DECIMAL(10, 2), nullable=False)

    # Relationships
    order = db.relationship("Order", back_populates="order_items")
    menu_item = db.relationship("MenuItem", back_populates="order_items")

    def __repr__(self):
        return f'<OrderItem {self.order_item_id}, Order: {self.order_id}, Item: {self.menu_item_id}>'

# Cart Model
class Cart(db.Model):
    __tablename__ = "cart"
    cart_id = db.Column(db.String(10), primary_key=True)
    customer_id = db.Column(db.String(10), db.ForeignKey("customer.customer_id", ondelete="CASCADE"), nullable=False)
    menu_item_id = db.Column(db.String(10), db.ForeignKey("menu_items.menu_item_id", ondelete="CASCADE"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    customer = db.relationship("Customer", back_populates="cart_items")
    menu_item = db.relationship("MenuItem", back_populates="cart_items")