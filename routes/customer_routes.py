from flask import jsonify, render_template, request, redirect, url_for
from flask_login import current_user, login_required
from models import Address, MenuItem, Category, Subcategory, Cart, Order, OrderItem
from sqlalchemy import text
import json
from datetime import datetime

def customer_routes(app, db):
    @app.route('/user/profile')
    @login_required
    def customer():
        return render_template('user/profile.html', user=current_user)
    
    @app.route('/show_menu')
    @login_required
    def show_menu():
        return render_template('user/show_menu.html', user=current_user)

    # ORDER MANAGEMENT ENDPOINTS: Order page route
    @app.route('/order', methods=['GET', 'POST'])
    @login_required
    def order():
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
                        MenuItem.price,
                        MenuItem.discount_percentage
                    )
                    .all()
                )

                cart_data = [
                    {
                        'cart_id': item.cart_id,
                        'menu_item_id': item.menu_item_id,
                        'name': item.menu_item_name,
                        'price': float(item.price),
                        'quantity': item.quantity,
                        'discount_percentage': float(item.discount_percentage) if item.discount_percentage else 0
                    }
                    for item in cart_items
                ]

                # Calculate totals
                subtotal = 0
                total_discount = 0
                for item in cart_data:
                    item_total = item['price'] * item['quantity']
                    item_discount = (item_total * item['discount_percentage']) / 100
                    subtotal += item_total
                    total_discount += item_discount
                tax = (subtotal - total_discount) * 0.18  # 18% tax
                delivery_charge = 50.0
                total = subtotal - total_discount + tax + delivery_charge

                return render_template(
                    'user/order.html',
                    cart_json=json.dumps(cart_data),
                    total=total,
                    subtotal=subtotal - total_discount,
                    tax=tax,
                    delivery_charge=delivery_charge,
                    user=current_user
                )
            except Exception as e:
                db.session.rollback()
                return jsonify({"error": str(e)}), 500

        elif request.method == 'POST':
            # Redirect to delivery_details when "Place Order" is clicked
            return redirect(url_for('delivery_details'))
    
    @app.route('/delivery_details')
    @login_required
    def delivery_details():
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
                    MenuItem.price,
                    MenuItem.discount_percentage
                )
                .all()
            )

            cart_data = [
                {
                    'cart_id': item.cart_id,
                    'menu_item_id': item.menu_item_id,
                    'name': item.menu_item_name,
                    'price': float(item.price),
                    'quantity': item.quantity,
                    'discount_percentage': float(item.discount_percentage) if item.discount_percentage else 0
                }
                for item in cart_items
            ]

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
                
            tax = (subtotal - total_discount) * 0.18  # 18% tax
            delivery_charge = 50.0
            total = subtotal - total_discount + tax + delivery_charge

            return render_template(
                'user/delivery_details.html',
                cart_json=json.dumps(cart_data),
                total=total,
                subtotal=subtotal - total_discount,
                tax=tax,
                delivery_charge=delivery_charge,
                user=current_user
            )
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500
        
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
                Cart.query
                .join(MenuItem, Cart.menu_item_id == MenuItem.menu_item_id)
                .filter(Cart.customer_id == current_user.customer_id)
                .all()
            )
            if not cart_items:
                return jsonify({"error": "Cart is empty"}), 400

            # Check stock
            for cart_item in cart_items:
                menu_item = cart_item.menu_item  # Use relationship
                if menu_item.stock_available < cart_item.quantity:
                    return jsonify({"error": f"Insufficient stock for {menu_item.name}"}), 400

            # Create order (ID auto-generated by BaseModel event)
            new_order = Order(
                customer_id=current_user.customer_id,
                delivery_agent_id=None,
                status="Pending",
                total_price=total,
                delivery_location=f"{delivery_details.get('street', '')}, {delivery_details.get('city', '')}, {delivery_details.get('state', '')} {delivery_details.get('pincode', '')}",
                created_at=datetime.utcnow()
            )
            db.session.add(new_order)
            db.session.flush()  # Flush to assign order_id

            # Create order items and update stock
            for cart_item in cart_items:
                menu_item = cart_item.menu_item
                order_item = OrderItem(
                    order_id=new_order.order_id,  # Now set from flushed order
                    menu_item_id=cart_item.menu_item_id,
                    quantity=cart_item.quantity,
                    price=float(menu_item.price)
                )
                db.session.add(order_item)
                db.session.flush()  # Flush each OrderItem to assign unique order_item_id
                menu_item.stock_available -= cart_item.quantity

            # Clear cart
            Cart.query.filter_by(customer_id=current_user.customer_id).delete()
            db.session.commit()

            return jsonify({"message": "Order placed successfully", "order_id": new_order.order_id}), 201
        except Exception as e:
            db.session.rollback()
            print("\n\n\n", str(e), "\n\n\n")
            return jsonify({"error": str(e)}), 500
    
    # http://127.0.0.1:5000/order_confirmation?order_id=O001
    @app.route('/order_confirmation')
    @login_required
    def order_confirmation():
        order_id = request.args.get('order_id')
        if not order_id:
            return "Order ID not provided", 400

        # Fetch order details from the database
        order = Order.query.filter_by(order_id=order_id, customer_id=current_user.customer_id).first()
        if not order:
            return "Order not found", 404

        # Fetch order items using relationship
        order_items = order.order_items  # Use the relationship defined in models.py

        # Prepare cart_items data for the template
        cart_data = [
            {
                'menu_item_id': item.menu_item_id,
                'name': item.menu_item.name,
                'quantity': item.quantity,
                'price': float(item.price),
                'discount_percentage': float(item.menu_item.discount_percentage) if item.menu_item.discount_percentage else 0
            }
            for item in order_items
        ]

        # Prepare order data for the template
        total_price = float(order.total_price)
        # Correctly parse delivery_location
        location_parts = order.delivery_location.split(', ') if order.delivery_location else []
        delivery_details = {
            'street': location_parts[0] if len(location_parts) > 0 else '',
            'city': location_parts[1] if len(location_parts) > 1 else '',
            'state': location_parts[2].rsplit(' ', 1)[0] if len(location_parts) > 2 else '',
            'pincode': location_parts[2].rsplit(' ', 1)[1] if len(location_parts) > 2 and len(location_parts[2].split()) > 1 else ''
        }

        order_data = {
            'order_id': order.order_id,
            'ordered_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S') if order.created_at else datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
            'total': total_price,
            'subtotal': total_price - (total_price * 0.18) - 50.0,  # Reverse calculate subtotal
            'tax': total_price * 0.18,  # 18% tax
            'delivery_charge': 50.0,  # Fixed delivery charge
            'delivery_details': delivery_details,
            'tracking_id': order.order_id  # Using order_id as tracking_id
        }

        # Mock agent data (replace with actual logic if DeliveryAgent table is used)
        agent_data = {
            'name': "Ravi Kumar",
            'contact': "+91 98765 43210"
        }

        return render_template(
            'user/order_confirmation.html',
            order_json=order_data,
            cart_items_json=cart_data,
            agent_json=agent_data,
            user=current_user
        )
    
    
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
    