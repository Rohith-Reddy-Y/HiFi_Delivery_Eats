from sqlalchemy.orm import Session
from sqlalchemy import select, update, delete
from datetime import datetime
from create_database import MenuItem, Category, Discount, Rating, PersonalizedRecommendations, ItemCategoryMapping
from sqlalchemy.sql import func

'''
PRIMARY KEY ID MAPPING:
-----------------------

    "I": MenuItem
    "C": Category
    "IC": ItemCategoryMapping
    "D": Discount
    "R": Rating
    "CO": CustomerOrders
    "PR": PersonalizedRecommendations
    "U": UserID (CustomerID)
    
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


    #! work on taking stock data in count. Like how many want --> do not require that becoz food made after the order place. Keep it T/F
    def add_menu_item(self, menu_item_id: str, name: str, description: str, price: float, image_url: str,
                      category: str, nutrient_value: str, calorie_count: int, discount_percentage: float = None,
                      discount_start: datetime = None, discount_end: datetime = None, is_best_seller: bool = False,
                      is_out_of_stock: bool = False):
        """Adds a new menu item and updates all dependent tables (category, discount, recommendations)."""

        # Generate MenuItem ID
        latest_menu_id = self.get_latest_id(MenuItem.menu_item_id)
        menu_item_id = generate_next_id(latest_menu_id, "I")
        
        # Ensure category exists (auto-create if missing)
        category_obj = self.session.execute(select(Category).where(Category.name == category)).scalar_one_or_none()
        if not category_obj:
            latest_category_id = self.get_latest_id(Category.category_id)
            category_id = generate_next_id(latest_category_id, "C")
            category_obj = Category(category_id=category_id, name=category)
            self.session.add(category_obj)
            # self.session.commit()

        # Add menu item
        new_item = MenuItem(
            menu_item_id=menu_item_id, name=name, description=description, price=price,
            image_url=image_url, category=category_obj.name, nutrient_value=nutrient_value,
            calorie_count=calorie_count, is_best_seller=is_best_seller, is_out_of_stock=is_out_of_stock
        )
        self.session.add(new_item)
        # self.session.commit()

        # Link item to category (if not already linked)
        existing_mapping = self.session.execute(
            select(ItemCategoryMapping).where(
                ItemCategoryMapping.menu_item_id == menu_item_id,
                ItemCategoryMapping.category_id == category_obj.category_id
            )
        ).scalar_one_or_none()

        if not existing_mapping:
            latest_mapping_id = self.get_latest_id(ItemCategoryMapping.mapping_id)
            mapping_id = generate_next_id(latest_mapping_id, "IC")
            new_mapping = ItemCategoryMapping(mapping_id=mapping_id, menu_item_id=menu_item_id, category_id=category_obj.category_id)
            self.session.add(new_mapping)
            # self.session.commit()

        # Add discount if provided
        if discount_percentage and discount_start and discount_end:
            latest_discount_id = self.get_latest_id(Discount.discount_id)
            discount_id = generate_next_id(latest_discount_id, "D")
            self.apply_discount(menu_item_id, discount_id, discount_percentage, discount_start, discount_end)

        # Add trending/best seller to personalized recommendations for customer U001
        if is_best_seller:
            self.add_personalized_recommendation("U001", menu_item_id)

        self.session.commit()
        return new_item

    def remove_menu_item(self, menu_item_id: str):
        """Removes a menu item and its related entries from all linked tables."""
        self.session.execute(delete(ItemCategoryMapping).where(ItemCategoryMapping.menu_item_id == menu_item_id))
        self.session.execute(delete(Discount).where(Discount.menu_item_id == menu_item_id))
        self.session.execute(delete(Rating).where(Rating.menu_item_id == menu_item_id))
        self.session.execute(delete(PersonalizedRecommendations).where(PersonalizedRecommendations.menu_item_id == menu_item_id))
        self.session.execute(delete(MenuItem).where(MenuItem.menu_item_id == menu_item_id))
        self.session.commit()
    def update_menu_item(self, menu_item_id: str, **kwargs):
        stmt = update(MenuItem).where(MenuItem.menu_item_id == menu_item_id).values(**kwargs)
        self.session.execute(stmt)
        self.session.commit()

    def add_category_to_item(self, menu_item_id: str, category_name: str):
        """Adds a category to a menu item in ItemCategoryMapping"""
        category = self.session.execute(select(Category).where(Category.name == category_name)).scalar_one_or_none()
        if not category:
            return None  # Category must exist

        # Check if mapping already exists
        existing_mapping = self.session.execute(
            select(ItemCategoryMapping).where(
                ItemCategoryMapping.menu_item_id == menu_item_id,
                ItemCategoryMapping.category_id == category.category_id
            )
        ).scalar_one_or_none()

        if not existing_mapping:
            new_mapping = ItemCategoryMapping(
                        mapping_id=generate_next_id(self.get_latest_id(ItemCategoryMapping.mapping_id), "IC"),
                        menu_item_id=menu_item_id, category_id=category.category_id
                    )

            self.session.add(new_mapping)
            self.session.commit()
        return category
    
    def remove_category_from_item(self, menu_item_id: str, category_name: str):
        """Removes a category from a menu item"""
        category = self.session.execute(select(Category).where(Category.name == category_name)).scalar_one_or_none()
        if not category:
            return None

        stmt = delete(ItemCategoryMapping).where(
            ItemCategoryMapping.menu_item_id == menu_item_id,
            ItemCategoryMapping.category_id == category.category_id
        )
        self.session.execute(stmt)
        self.session.commit()
        return category
    
    def get_categories_for_item(self, menu_item_id: str):
        """Fetches all categories linked to a menu item"""
        stmt = select(Category).join(ItemCategoryMapping).where(ItemCategoryMapping.menu_item_id == menu_item_id)
        return self.session.scalars(stmt).all()

    def mark_as_best_seller(self, menu_item_id: str):
        self.session.execute(update(MenuItem).where(MenuItem.menu_item_id == menu_item_id).values(is_best_seller=True))
        self.session.commit()

    def mark_as_out_of_stock(self, menu_item_id: str, status: bool):
        self.session.execute(update(MenuItem).where(MenuItem.menu_item_id == menu_item_id).values(is_out_of_stock=status))
        self.session.commit()

    def schedule_menu_update(self, menu_item_id: str, scheduled_time: datetime):
        self.session.execute(update(MenuItem).where(MenuItem.menu_item_id == menu_item_id).values(scheduled_update_time=scheduled_time))
        self.session.commit()

    def add_personalized_recommendation(self, customer_id: str, menu_item_id: str):
        """Adds a menu item to a customer's personalizefd recommendations."""
        existing_recommendation = self.session.execute(
            select(PersonalizedRecommendations).where(
                PersonalizedRecommendations.customer_id == customer_id,
                PersonalizedRecommendations.menu_item_id == menu_item_id
            )
        ).scalar_one_or_none()

        if not existing_recommendation:
            latest_pr_id = self.get_latest_id(PersonalizedRecommendations.personalised_recommendations_id)
            pr_id = generate_next_id(latest_pr_id, "PR")
            recommendation = PersonalizedRecommendations(personalised_recommendations_id=pr_id, customer_id=customer_id, menu_item_id=menu_item_id)
            self.session.add(recommendation)
            self.session.commit()
            
    def get_personalized_recommendations(self, customer_id: str):
        """Fetches recommendations for a customer and adds new trending items to recommendations."""
        stmt = select(PersonalizedRecommendations).where(PersonalizedRecommendations.customer_id == customer_id)
        recommendations = self.session.scalars(stmt).all()

        # If no recommendations exist, add trending items
        if not recommendations:
            trending_items = self.get_best_sellers()[:3]  # Get top 3 best sellers
            for item in trending_items:
                new_recommendation = PersonalizedRecommendations(customer_id=customer_id, menu_item_id=item.menu_item_id)
                self.session.add(new_recommendation)
            self.session.commit()

        return recommendations
    
    def apply_discount(self, menu_item_id: str, discount_percentage: float, start_date: datetime, end_date: datetime):
        """Applies a discount to a menu item by updating an existing discount if present, otherwise adding a new one."""

        # Check if a discount already exists for the menu item
        existing_discount = self.session.execute(
            select(Discount).where(Discount.menu_item_id == menu_item_id)
        ).scalar_one_or_none()

        if existing_discount:
            # Update existing discount
            self.session.execute(
                update(Discount)
                .where(Discount.menu_item_id == menu_item_id)
                .values(discount_percentage=discount_percentage, start_date=start_date, end_date=end_date)
            )
        else:
            # Insert new discount
            latest_discount_id = self.get_latest_id(Discount.discount_id)
            discount_id = generate_next_id(latest_discount_id, "D")
            discount = Discount(
                discount_id=discount_id, menu_item_id=menu_item_id,
                discount_percentage=discount_percentage, start_date=start_date, end_date=end_date
            )
            self.session.add(discount)

        self.session.commit()


    def get_item_ratings(self, menu_item_id: str):
        stmt = select(Rating).where(Rating.menu_item_id == menu_item_id)
        return self.session.scalars(stmt).all()
    
    def get_best_sellers(self):
        """Retrieves top-rated/best-selling items based on ratings."""
        # outerjoin: Ensures even unrated best-sellers are retrieved.
        stmt = select(MenuItem).outerjoin(Rating).group_by(MenuItem.menu_item_id).order_by(func.coalesce(func.avg(Rating.rating), 0).desc()) # Handle NULL ratings
        return self.session.scalars(stmt).all()
    

'''
Use logger instead of print(): [FOR DEBUGGING]

python:

import logging
logger = logging.getLogger(__name__)
logger.error(f"Error adding menu item: {e}", exc_info=True)

===> Logs help debug issues better than print().
'''