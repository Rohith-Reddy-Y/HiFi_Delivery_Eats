from sqlalchemy import create_engine, Integer, String, Text, Boolean, DECIMAL, TIMESTAMP, ForeignKey, DATETIME, Enum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session
from datetime import datetime

# Database Connection
engine = create_engine("sqlite:///hifi_database.db", echo=True)

# Base Class
class Base(DeclarativeBase):
    pass

# # Function to Generate Custom IDs
# def generate_custom_id(prefix: str, number: int) -> str:
#     return f"{prefix}{str(number).zfill(3)}"

# User Table
class User(Base):
    __table_args__ = {'extend_existing': True}
    __tablename__ = "users"
    user_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(15), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(Enum("customer", "admin", "delivery_agent", name="user_roles"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Explicitly define foreign_keys
    orders = relationship("Order", back_populates="user", foreign_keys="Order.user_id")  # Orders placed by user
    deliveries = relationship("Order", back_populates="delivery_agent", foreign_keys="Order.delivery_agent_id")  # Orders assigned to delivery agent
    cart_items = relationship("Cart", back_populates="user")


# Category Table
class Category(Base):
    __table_args__ = {'extend_existing': True}
    __tablename__ = "categories"
    category_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    menu_items = relationship("MenuItem", back_populates="category")

# MenuItem Table
class MenuItem(Base):
    __table_args__ = {'extend_existing': True}
    __tablename__ = "menu_items"
    menu_item_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[float] = mapped_column(DECIMAL(10,2), nullable=False)
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    category_id: Mapped[str] = mapped_column(ForeignKey("categories.category_id", ondelete="CASCADE"), nullable=False)
    nutrient_value: Mapped[str] = mapped_column(String(255), nullable=False)
    calorie_count: Mapped[int] = mapped_column(Integer, nullable=False)
    is_best_seller: Mapped[bool] = mapped_column(Boolean, default=False)
    is_out_of_stock: Mapped[bool] = mapped_column(Boolean, default=False)
    discount_percentage: Mapped[float] = mapped_column(DECIMAL(5,2), nullable=True)
    scheduled_update_time: Mapped[datetime] = mapped_column(DATETIME, nullable=True)
    category = relationship("Category", back_populates="menu_items")
    orders = relationship("OrderItem", back_populates="menu_item")
    cart_items = relationship("Cart", back_populates="menu_item")

# Order Table
class Order(Base):
    __table_args__ = {'extend_existing': True}
    __tablename__ = "orders"
    order_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    delivery_agent_id: Mapped[str] = mapped_column(ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    status: Mapped[str] = mapped_column(Enum("Pending", "Preparing", "Out for Delivery", "Delivered", "Cancelled", name="order_status"), nullable=False, default="Pending")
    total_price: Mapped[float] = mapped_column(DECIMAL(10,2), nullable=False)
    delivery_location: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    # Explicitly specify foreign_keys for clarity
    user = relationship("User", back_populates="orders", foreign_keys=[user_id])  # Customer
    delivery_agent = relationship("User", back_populates="deliveries", foreign_keys=[delivery_agent_id])  # Delivery agent

    order_items = relationship("OrderItem", back_populates="order")

# Order Items Table
class OrderItem(Base):
    __table_args__ = {'extend_existing': True}
    __tablename__ = "order_items"
    order_item_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    order_id: Mapped[str] = mapped_column(ForeignKey("orders.order_id", ondelete="CASCADE"), nullable=False)
    menu_item_id: Mapped[str] = mapped_column(ForeignKey("menu_items.menu_item_id", ondelete="CASCADE"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float] = mapped_column(DECIMAL(10,2), nullable=False)
    order = relationship("Order", back_populates="order_items")
    menu_item = relationship("MenuItem", back_populates="orders")

# Delivery Agent Table
class DeliveryAgent(Base):
    __table_args__ = {'extend_existing': True}
    __tablename__ = "delivery_agents"
    delivery_agent_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False, unique=True)
    availability_status: Mapped[str] = mapped_column(Enum("Available", "Busy", "Inactive", name="agent_status"), nullable=False, default="Available")

# Cart Table
class Cart(Base):
    __table_args__ = {'extend_existing': True}
    __tablename__ = "cart"
    cart_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    menu_item_id: Mapped[str] = mapped_column(ForeignKey("menu_items.menu_item_id", ondelete="CASCADE"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    added_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    user = relationship("User", back_populates="cart_items")
    menu_item = relationship("MenuItem", back_populates="cart_items")
    
# Creating Tables
# print("Creating tables...")
# Base.metadata.create_all(bind=engine)
