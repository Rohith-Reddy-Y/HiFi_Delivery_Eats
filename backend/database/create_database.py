from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DECIMAL, TIMESTAMP, ForeignKey, DATETIME
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session
from datetime import datetime

# naming convention is all in lowercase with underscore between them

# Database Connection
engine = create_engine("sqlite:///menu.db", echo=True)

# Base Class
class Base(DeclarativeBase):
    pass

# Menu Table
class Menu(Base):
    __tablename__ = "menu"
    menu_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    menu_items: Mapped[list["MenuItem"]] = relationship("MenuItem", back_populates="menu")

# MenuItem Table
class MenuItem(Base):
    __tablename__ = "menu_item"
    menu_item_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    menu_id: Mapped[str] = mapped_column(ForeignKey("menu.menu_id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[float] = mapped_column(DECIMAL(10,2), nullable=False)
    image_url: Mapped[str] = mapped_column(String(500), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    nutrient_value: Mapped[str] = mapped_column(String(255), nullable=False)
    calorie_count: Mapped[int] = mapped_column(Integer, nullable=False)
    is_best_seller: Mapped[bool] = mapped_column(Boolean, default=False)
    is_out_of_stock: Mapped[bool] = mapped_column(Boolean, default=False)
    scheduled_update_time: Mapped[datetime] = mapped_column(DATETIME, nullable=True)
    menu: Mapped["Menu"] = relationship("Menu", back_populates="menu_items")
    discounts: Mapped[list["Discount"]] = relationship("Discount", back_populates="menu_item")
    ratings: Mapped[list["Rating"]] = relationship("Rating", back_populates="menu_item")

# Category Table
class Category(Base):
    __tablename__ = "category"
    category_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

# ItemCategoryMapping Table
class ItemCategoryMapping(Base):
    __tablename__ = "item_category_mapping"
    mapping_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    menu_item_id: Mapped[str] = mapped_column(ForeignKey("menu_item.menu_item_id"), nullable=False)
    category_id: Mapped[str] = mapped_column(ForeignKey("category.category_id"), nullable=False)

# Discount Table
class Discount(Base):
    __tablename__ = "discount"
    discount_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    menu_item_id: Mapped[str] = mapped_column(ForeignKey("menu_item.menu_item_id"), nullable=False)
    discount_percentage: Mapped[float] = mapped_column(DECIMAL(5,2), nullable=False)
    start_date: Mapped[datetime] = mapped_column(DATETIME, nullable=False)
    end_date: Mapped[datetime] = mapped_column(DATETIME, nullable=False)
    menu_item: Mapped["MenuItem"] = relationship("MenuItem", back_populates="discounts")

# Rating Table
class Rating(Base):
    __tablename__ = "rating"
    rating_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    menu_item_id: Mapped[str] = mapped_column(ForeignKey("menu_item.menu_item_id"), nullable=False)
    rating_value: Mapped[int] = mapped_column(Integer, nullable=False)
    review_text: Mapped[str] = mapped_column(Text, nullable=True)
    review_date: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow, nullable=False)
    menu_item: Mapped["MenuItem"] = relationship("MenuItem", back_populates="ratings")

# CustomerOrders Table
class CustomerOrders(Base):
    __tablename__ = "customer_orders"
    customer_order_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    customer_id: Mapped[str] = mapped_column(String(10), nullable=False)
    menu_item_id: Mapped[str] = mapped_column(ForeignKey("menu_item.menu_item_id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    order_date: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow, nullable=False)

# PersonalizedRecommendations Table
class PersonalizedRecommendations(Base):
    __tablename__ = "personalized_recommendations"
    personalized_recommendations_id: Mapped[str] = mapped_column(String(10), primary_key=True)
    customer_id: Mapped[str] = mapped_column(String(10), nullable=False)
    menu_item_id: Mapped[str] = mapped_column(ForeignKey("menu_item.menu_item_id"), nullable=False)
    recommendation_reason: Mapped[str] = mapped_column(Text, nullable=False)

# Creating Tables
print("Creating tables...")
Base.metadata.create_all(bind=engine)
