from flask import jsonify, render_template, request
from flask_login import current_user, login_required
from models import Address, MenuItem, Category, Subcategory, Cart, Order, OrderItem
from sqlalchemy import text

def customer_routes(app, db):
    @app.route('/user/profile')
    @login_required
    def customer():
        return render_template('user/profile.html', user=current_user)
    
    @app.route('/show_menu')
    def show_menu():
        return render_template('user/show_menu.html', user=current_user)

    @app.route("/address/new", methods=["POST"])
    @login_required
    def add_address():
        data = request.get_json()
        if not data:
            return jsonify({"error": "No input data provided"}), 400

        new_address = Address(
            address_line=data.get("address_line"),
            city=data.get("city"),
            state=data.get("state"),
            zip_code=data.get("zip_code"),
            customer_id=current_user.customer_id
        )
        try:
            db.session.add(new_address)
            db.session.commit()
            return jsonify({"message": "Address added successfully!"}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500
    
    @app.route("/address/<string:address_id>/set-preferred", methods=["POST"])
    @login_required
    def set_preferred_address(address_id):
        # Fetch the selected address using the correct primary key name
        address = Address.query.filter_by(address_id=address_id, customer_id=current_user.customer_id).first()
        
        if not address:
            return jsonify({"error": "Address not found"}), 404

        try:
            # Set all addresses as not preferred for the current user
            Address.query.filter_by(customer_id=current_user.customer_id).update({"is_preferred": False})
            # Set the selected address as preferred
            address.is_preferred = True
            db.session.commit()
            return jsonify({"message": "Default address updated!"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500
    
    @app.route("/address/<string:address_id>", methods=["DELETE"])
    @login_required
    def delete_address(address_id):
        # Fetch the address using the correct primary key name
        address = Address.query.filter_by(address_id=address_id, customer_id=current_user.customer_id).first()

        if not address:
            return jsonify({"error": "Address not found"}), 404

        try:
            db.session.delete(address)
            db.session.commit()
            return jsonify({"message": "Address deleted successfully!"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    @app.route("/address/<string:address_id>", methods=["PUT"])
    @login_required
    def edit_address(address_id):
        data = request.get_json()
        address = Address.query.filter_by(address_id=address_id, customer_id=current_user.customer_id).first()
        
        if not address:
            return jsonify({"error": "Address not found"}), 404

        # Update only if values are provided
        if data.get("address_line"):
            address.address_line = data["address_line"]
        if data.get("city"):
            address.city = data["city"]
        if data.get("state"):
            address.state = data["state"]
        if data.get("zip_code"):
            address.zip_code = data["zip_code"]

        try:
            db.session.commit()
            return jsonify({
                "message": "Address updated successfully!",
                "address": {
                    "address_line": address.address_line,
                    "city": address.city,
                    "state": address.state,
                    "zip_code": address.zip_code
                }
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    # MENU MANAGEMENT FUNCTIONS : show_menu webpage
    @app.route("/api/menu_items",methods=['GET'])
    @login_required
    def get_menu_items():
        try:
            # Fetch menu items with category and subcategory details
            items = (
                MenuItem.query
                .outerjoin(Category, MenuItem.category_id == Category.category_id)
                .outerjoin(Subcategory, MenuItem.subcategory_id == Subcategory.subcategory_id)
                .filter(MenuItem.is_out_of_stock == False)
                .with_entities(
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
                .all()
            )

            # Format the response data
            items_list = [
                {
                    "menu_item_id": item.menu_item_id,
                    "name": item.name,
                    "description": item.description,
                    "price": float(item.price),  # Convert DECIMAL to float for JSON
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

            return jsonify({'data': items_list, 'ok': True}), 200

        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500
        
        
    # API to fetch and update cart
    @app.route('/api/cart', methods=['GET', 'POST'])
    @login_required
    def manage_cart():
        if request.method == 'GET':
            try:
                cart_items = (
                    Cart.query
                    .join(MenuItem, Cart.menu_item_id == MenuItem.menu_item_id)
                    .filter(Cart.customer_id == current_user.customer_id)
                    .with_entities(
                        Cart.cart_id,
                        Cart.menu_item_id,
                        Cart.quantity,
                        MenuItem.name.label("menu_item_name"),
                        MenuItem.price
                    )
                    .all()
                )

                data = [
                    {
                        'cart_id': item.cart_id,
                        'menu_item_id': item.menu_item_id,
                        'name': item.menu_item_name,
                        'price': float(item.price),
                        'quantity': item.quantity
                    }
                    for item in cart_items
                ]
                return jsonify({'ok': True, 'data': data}), 200
            except Exception as e:
                db.session.rollback()
                return jsonify({"error": str(e)}), 500

        elif request.method == 'POST':
            try:
                items = request.get_json().get('items', [])
                # Clear existing cart for this customer
                Cart.query.filter_by(customer_id=current_user.customer_id).delete()

                # Get the latest cart_id before adding new items
                last_id_query = text("SELECT cart_id FROM cart ORDER BY cart_id DESC LIMIT 1")
                result = db.session.execute(last_id_query).scalar()
                last_numeric = int(result[1:]) if result else 0

                # Add new items with unique cart_ids
                for i, item in enumerate(items, start=last_numeric + 1):
                    if item.get('quantity', 0) > 0:  # Only add items with quantity > 0
                        cart_id = f"C{i:03d}"  # Generate unique cart_id (e.g., C002, C003)
                        cart_item = Cart(
                            cart_id=cart_id,  # Set cart_id manually
                            customer_id=current_user.customer_id,
                            menu_item_id=item['menu_item_id'],
                            quantity=item['quantity']
                        )
                        db.session.add(cart_item)

                db.session.commit()
                return jsonify({'data': items, 'message': 'Cart updated successfully'}), 200
            except Exception as e:
                db.session.rollback()
                return jsonify({"error": str(e)}), 500
    
    @app.route('/api/recommendations', methods=['GET'])
    @login_required
    def get_recommendations():
        try:
            customer_id = current_user.customer_id
            orders = Order.query.filter_by(customer_id=customer_id).all()

            if not orders:  # New user, no recommendations
                return jsonify({'data': [], 'is_new_user': True, 'ok': True}), 200

            # Get ordered items and their subcategories
            order_items = (
                OrderItem.query
                .join(Order, OrderItem.order_id == Order.order_id)
                .filter(Order.customer_id == customer_id)
                .all()
            )
            ordered_item_ids = {item.menu_item_id for item in order_items}
            ordered_subcategories = {
                MenuItem.query
                .filter(MenuItem.menu_item_id == item.menu_item_id)
                .join(Subcategory, MenuItem.subcategory_id == Subcategory.subcategory_id)
                .with_entities(Subcategory.name)
                .scalar()
                for item in order_items
            }

            # Fetch all menu items and filter recommendations
            all_menu_items = (
                MenuItem.query
                .join(Category, MenuItem.category_id == Category.category_id)
                .join(Subcategory, MenuItem.subcategory_id == Subcategory.subcategory_id)
                .all()
            )
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

            # Limit to 5 recommendations
            recommendations = recommendations[:5]

            return jsonify({'data': recommendations, 'is_new_user': False, 'ok': True}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500
    