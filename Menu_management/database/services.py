from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from datetime import datetime
from sqlalchemy.sql import func
from database.create_database import *

'''
PRIMARY KEY ID MAPPING:
-----------------------
    U001 for user
    IC001 for category
    MI001 for menu_item
    O001 for orders
    OI001 for order_item
    C001 for cart. 
    D001 for delivery_agent
'''


def generate_next_id(latest_id: str, prefix: str):
    """Generates the next auto-incremented ID while preserving the prefix."""
    if latest_id:
        num_part = int(latest_id[len(prefix):])  # Extract numeric part
        return f"{prefix}{num_part + 1:03d}"  # Keep prefix, increment number
    return f"{prefix}001"  # Default starting ID

class MenuService:
    def __init__(self, session: Session):
        self.session = session
    
    def get_latest_id(self, id_column):
        """Fetches the latest ID for a given table."""
        latest_entry = self.session.execute(select(func.max(id_column))).scalar_one_or_none()
        return latest_entry if latest_entry else None
# menu_item_id, name, description, price, image_url, category_id,  nutrient_value,  calorie_count,  is_best_seller,
# is_out_of_stock,  discount_percentage,  scheduled_update_time,

    def add_menu_item(self, name: str, description: str, price: float, image_url: str,
                      category_name: str, nutrient_value: str, calorie_count: int,
                      is_best_seller: bool = False, is_out_of_stock: bool = False,discount_percentage:int = 0,scheduled_update_time: datetime = None):
        """Adds a new menu item and associates it with a category."""
        try:
            latest_menu_id = self.get_latest_id(MenuItem.menu_item_id)
            menu_item_id = generate_next_id(latest_menu_id, "MI")
            
            category = self.session.execute(select(Category).where(Category.name == category_name)).scalar_one_or_none()
            if not category:
                latest_category_id = self.get_latest_id(Category.category_id)
                category_id = generate_next_id(latest_category_id, "IC")
                category = Category(category_id=category_id, name=category_name)
                self.session.add(category)
            
            new_item = MenuItem(
                menu_item_id=menu_item_id, name=name, description=description, price=price,
                image_url=image_url, category_id=category.category_id, nutrient_value=nutrient_value,
                calorie_count=calorie_count, is_best_seller=is_best_seller, is_out_of_stock=is_out_of_stock,
                discount_percentage = discount_percentage,scheduled_update_time = scheduled_update_time
            )
            self.session.add(new_item)
            self.session.commit()
            return new_item
        except Exception as e:
            self.session.rollback()
            raise e

    def update_menu_item(self, menu_item_id: str, **kwargs):
        """Updates a menu item with new values."""
        try:
            stmt = update(MenuItem).where(MenuItem.menu_item_id == menu_item_id).values(**kwargs)
            self.session.execute(stmt)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

    def remove_menu_item(self, menu_item_id: str):
        """Removes a menu item."""
        try:
            self.session.execute(delete(MenuItem).where(MenuItem.menu_item_id == menu_item_id))
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

    def get_all_menu_items(self):
        """Fetches all menu items."""
        stmt = select(MenuItem)
        return self.session.scalars(stmt).all()
    
    def get_menu_item_by_id(self, menu_item_id: str):
        """Fetches a menu item by its ID."""
        stmt = select(MenuItem).where(MenuItem.menu_item_id == menu_item_id)
        return self.session.scalar(stmt)
    
    def mark_as_best_seller(self, menu_item_id: str):
        """Marks a menu item as a best seller."""
        try:
            self.session.execute(update(MenuItem).where(MenuItem.menu_item_id == menu_item_id).values(is_best_seller=True))
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

    def mark_as_out_of_stock(self, menu_item_id: str, status: bool):
        """Updates the stock status of a menu item."""
        try:
            self.session.execute(update(MenuItem).where(MenuItem.menu_item_id == menu_item_id).values(is_out_of_stock=status))
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e

    def get_best_sellers(self):
        """Retrieves best-selling items."""
        stmt = select(MenuItem).where(MenuItem.is_best_seller == True)
        return self.session.scalars(stmt).all()
