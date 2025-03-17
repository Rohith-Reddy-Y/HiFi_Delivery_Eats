document.addEventListener("DOMContentLoaded", function () {
    const cartItemsContainer = document.getElementById("cart-items");
    const orderSummary = document.getElementById("order-summary");
    const clearControlsContainer = document.getElementById("cart-clear-controls");
    const orderHistoryContainer = document.getElementById("order-history-details");
    const orderHistorySection = document.getElementById("order-history");
    const clearOrdersButton = document.getElementById("clear-orders-button");
  
    // Load cart items, orders, and menu items from localStorage
    let cart = JSON.parse(localStorage.getItem("cart")) || [];
    let orders = JSON.parse(localStorage.getItem("orders")) || [];
    let menuItems = JSON.parse(localStorage.getItem("menuItems")) || [];
    let orderJustPlaced = false;
    let isSelectionMode = false;
  
    // Debug: Log initial cart state
    console.log("Initial cart state in order.js:", cart);
    console.log("Initial localStorage cart:", JSON.parse(localStorage.getItem("cart")));
    console.log("Initial menuItems:", menuItems);
  
    // Function to resolve image references
    function resolveImage(image, itemId) {
      console.log(`Resolving image for itemId: ${itemId}, image: ${image}`); // Debug log
  
      if (!image && !itemId) {
        console.warn(`No image or itemId provided for itemId: ${itemId}`);
        return "https://via.placeholder.com/150?text=Image+Not+Found";
      }
  
      // Handle reference images (e.g., "ref:ITEM-XXXXX")
      if (image && image.startsWith("ref:")) {
        const id = image.split("ref:")[1];
        const menuItem = menuItems.find((item) => item.itemId === id);
        if (menuItem) {
          console.log(`Resolved ref:${id} to menuItem image: ${menuItem.image}`);
          return resolveImage(menuItem.image, id);
        } else {
          console.warn(`Menu item not found for ref:${id}`);
          return "https://via.placeholder.com/150?text=Image+Not+Found";
        }
      }
  
      // Handle base64-encoded images (used for newly added items)
      if (image && image.startsWith("data:image/")) {
        console.log(`Using base64 image for itemId: ${itemId}`);
        return image;
      }
  
      // Handle relative paths (e.g., "Menu_Images/..." or "../Menu_Images/...")
      if (image && image.includes("Menu_Images/")) {
        // Normalize the path by removing any "../" and ensuring consistent format
        let cleanPath = image.replace(/\.\.\//g, ""); // Remove any "../" prefixes
        cleanPath = cleanPath.replace(/^Menu_Images\//, ""); // Remove "Menu_Images/" prefix for consistency
        // URL-encode the filename to handle spaces and special characters
        cleanPath = encodeURI(cleanPath);
        // Adjust path to go up one level from order/ to menu/ and then to Menu_Images
        const adjustedPath = `../menu/Menu_Images/${cleanPath}`;
        console.log(`Adjusted relative path for itemId: ${itemId} to ${adjustedPath}`);
        return adjustedPath;
      }
  
      // Fallback: Look up the image in menuItems based on itemId
      const menuItem = menuItems.find((item) => item.itemId === itemId);
      if (menuItem && menuItem.image) {
        console.log(`Fallback: Using menuItem.image for itemId: ${itemId}, image: ${menuItem.image}`);
        if (menuItem.image.startsWith("data:image/")) {
          return menuItem.image;
        } else if (menuItem.image.includes("Menu_Images/")) {
          let cleanPath = menuItem.image.replace(/\.\.\//g, ""); // Remove any "../" prefixes
          cleanPath = cleanPath.replace(/^Menu_Images\//, ""); // Remove "Menu_Images/" prefix
          cleanPath = encodeURI(cleanPath); // URL-encode the filename
          const adjustedPath = `../menu/Menu_Images/${cleanPath}`;
          console.log(`Adjusted fallback path for itemId: ${itemId} to ${adjustedPath}`);
          return adjustedPath;
        }
      }
  
      // If all else fails, use a placeholder image
      console.warn(`Image resolution failed for itemId: ${itemId}, image: ${image}`);
      return "https://via.placeholder.com/150?text=Image+Not+Found";
    }
  
    // Function to show stock alert popup
    function showStockAlert(itemName, stockAvailable) {
      const popup = document.createElement("div");
      popup.className = "popup-container";
      const message = stockAvailable === 0
        ? `Item "${itemName}" not available - Out of stock!`
        : `Item "${itemName}" not available - Out of stock! Only ${stockAvailable} items left.`;
      popup.innerHTML = `
        <p>${message}</p>
        <div class="button-group">
          <button id="close-stock-alert">OK</button>
        </div>
      `;
      document.body.appendChild(popup);
  
      document.getElementById("close-stock-alert").addEventListener("click", () => {
        document.body.removeChild(popup);
      });
    }
  
    // Function to calculate total items in the cart
    function getCartTotalItems() {
      return cart.reduce((sum, item) => sum + (item.quantity || 1), 0);
    }
  
    // Function to update cart count in the navigation bar (aligned with show_menu.js)
    function updateCartCount() {
      cart = JSON.parse(localStorage.getItem("cart")) || [];
      const totalItems = getCartTotalItems();
      const cartLink = document.querySelector('.nav__link[href="order.html"]');
      if (cartLink) {
        const span = cartLink.querySelector(".nav__cart-count") || document.createElement("span");
        span.className = "nav__cart-count";
        span.textContent = totalItems;
        if (!cartLink.querySelector(".nav__cart-count")) {
          const textNode = cartLink.firstChild;
          if (textNode && textNode.nodeType === Node.TEXT_NODE) {
            const text = textNode.nodeValue;
            const parts = text.split("(");
            if (parts.length > 1) {
              textNode.nodeValue = parts[0] + "(";
              cartLink.insertBefore(span, textNode.nextSibling);
              cartLink.appendChild(document.createTextNode(" )"));
            } else {
              console.error("Unable to parse the text for inserting span.");
            }
          } else {
            console.error("Unable to find text node to insert span.");
          }
        } else {
          span.textContent = totalItems;
        }
        console.log("Updated cart count to:", totalItems, "Cart state:", cart);
        console.log("localStorage cart after update:", JSON.parse(localStorage.getItem("cart")));
      } else {
        console.error("Cart link element (.nav__link[href='order.html']) not found in the DOM.");
      }
    }
  
    function mergeCartItems(cart) {
      const mergedCart = [];
      cart.forEach((item) => {
        // Ensure itemName and image are included by fetching from menuItems if not present
        if (!item.itemName && item.itemId) {
          const menuItem = menuItems.find((menuItem) => menuItem.itemId === item.itemId);
          item.itemName = menuItem ? menuItem.name : `Unknown Item (ID: ${item.itemId})`;
          item.image = menuItem ? menuItem.image : item.image || "https://via.placeholder.com/150?text=Image+Not+Found";
        }
        const existingItem = mergedCart.find(
          (cartItem) => cartItem.itemId === item.itemId && cartItem.price === item.price
        );
        if (existingItem) {
          existingItem.quantity = (existingItem.quantity || 1) + (item.quantity || 1);
        } else {
          mergedCart.push({ ...item, quantity: item.quantity || 1 });
        }
      });
      return mergedCart;
    }
  
    cart = mergeCartItems(cart);
    localStorage.setItem("cart", JSON.stringify(cart));
    console.log("Cart after mergeCartItems:", cart);
    updateCartCount();
  
    function toggleSelectionMode() {
      isSelectionMode = !isSelectionMode;
      displayCartItems();
    }
  
    function simulateDelivery(order, callback) {
      setTimeout(() => {
        order.status = "delivered";
        orders = orders.map((o) => (o.orderId === order.orderId ? order : o));
        localStorage.setItem("orders", JSON.stringify(orders));
        callback();
      }, 10000);
    }
  
    function displayCartItems() {
      cartItemsContainer.innerHTML = "";
      clearControlsContainer.innerHTML = "";
  
      console.log("Cart state before displayCartItems:", cart);
  
      if (cart.length === 0) {
        if (!orderJustPlaced) {
          cartItemsContainer.innerHTML = `
            <div class="empty-cart-container">
              <img src="./static/images/cart.png" alt="Empty Cart" class="empty-cart-image" onerror="this.onerror=null; this.src='https://via.placeholder.com/150?text=Cart+Image+Not+Found'; console.log('Failed to load cart.png at ../images/cart.png');" />
              <p>Your cart is empty.</p>
            </div>
          `;
        } else {
          cartItemsContainer.style.display = "none";
        }
        orderSummary.style.display = "none";
        return;
      }
  
      cartItemsContainer.style.display = "block";
      orderSummary.style.display = "block";
  
      if (cart.length > 0) {
        if (!isSelectionMode) {
          clearControlsContainer.innerHTML = `
            <div style="flex: 1;"></div>
            <button class="cart__clear-button" id="clear-cart-button">Clear Cart</button>
          `;
        } else {
          clearControlsContainer.innerHTML = `
            <div class="cart__select-all">
              <input type="checkbox" id="select-all" />
              <label for="select-all">Select All</label>
            </div>
            <div class="cart__selection-buttons">
              <button class="clear-selected" id="clear-selected">Clear</button>
              <button class="cancel" id="cancel-clear">Cancel</button>
            </div>
          `;
        }
  
        const clearCartButton = document.getElementById("clear-cart-button");
        const clearSelectedButton = document.getElementById("clear-selected");
        const cancelClearButton = document.getElementById("cancel-clear");
        const selectAllCheckbox = document.getElementById("select-all");
  
        if (clearCartButton) {
          clearCartButton.addEventListener("click", toggleSelectionMode);
        }
  
        if (cancelClearButton) {
          cancelClearButton.addEventListener("click", toggleSelectionMode);
        }
  
        if (clearSelectedButton) {
          clearSelectedButton.addEventListener("click", function () {
            const selectedItems = Array.from(document.querySelectorAll(".cart__item-checkbox input:checked")).map((input) => parseInt(input.value));
            cart = cart.filter((_, index) => !selectedItems.includes(index));
            localStorage.setItem("cart", JSON.stringify(cart));
            isSelectionMode = false;
            displayCartItems();
            updateCartCount();
          });
        }
  
        if (selectAllCheckbox) {
          selectAllCheckbox.addEventListener("change", function () {
            const checkboxes = document.querySelectorAll(".cart__item-checkbox input");
            checkboxes.forEach((checkbox) => {
              checkbox.checked = this.checked;
            });
          });
        }
  
        const updateSelectAllState = () => {
          const checkboxes = document.querySelectorAll(".cart__item-checkbox input");
          const allChecked = Array.from(checkboxes).every((checkbox) => checkbox.checked);
          selectAllCheckbox.checked = allChecked;
        };
  
        cart.forEach((item, index) => {
          const cartItem = document.createElement("div");
          cartItem.classList.add("cart__item");
          const adjustedImagePath = resolveImage(item.image, item.itemId);
          cartItem.innerHTML = `
            ${isSelectionMode
              ? `
              <div class="cart__item-checkbox">
                <input type="checkbox" id="cart-item-${index}" value="${index}" />
                <label for="cart-item-${index}"></label>
              </div>
            `
              : ""
            }
            <img src="${adjustedImagePath}" alt="${item.itemName || item.name}" class="cart__item-img" onerror="this.onerror=null; this.src='https://via.placeholder.com/150?text=Image+Not+Found'; console.log('Image failed to load for ${item.itemName || item.name}: ${adjustedImagePath}');" />
            <div class="cart__item-details">
              <h3 class="cart__item-name">${item.itemName || item.name}</h3>
              <p class="cart__item-price">₹ ${parseFloat(item.price).toFixed(2)}</p>
            </div>
            <div class="quantity-controls">
              <button class="decrease" data-index="${index}">-</button>
              <span class="quantity quantity-${index}">${item.quantity || 1}</span>
              <button class="increase" data-index="${index}">+</button>
            </div>
          `;
          cartItemsContainer.appendChild(cartItem);
        });
  
        if (isSelectionMode) {
          const checkboxes = document.querySelectorAll(".cart__item-checkbox input");
          checkboxes.forEach((checkbox) => {
            checkbox.addEventListener("change", updateSelectAllState);
          });
        }
  
        updateOrderSummary();
      }
    }
  
    cartItemsContainer.addEventListener("click", (event) => {
      const index = parseInt(event.target.getAttribute("data-index"));
      if (event.target.classList.contains("decrease")) {
        decreaseQuantity(index);
      }
      if (event.target.classList.contains("increase")) {
        increaseQuantity(index);
      }
    });
  
    function increaseQuantity(index) {
      const item = cart[index];
      const stockAvailable = parseInt(menuItems.find((i) => i.itemId === item.itemId)?.stockAvailable) || 0;
      const currentQuantity = item.quantity || 1;
  
      if (currentQuantity + 1 > stockAvailable) {
        showStockAlert(item.itemName || item.name, stockAvailable);
        return;
      }
  
      item.quantity = currentQuantity + 1;
      cart = mergeCartItems(cart);
      localStorage.setItem("cart", JSON.stringify(cart));
      console.log("Cart after increaseQuantity:", cart);
      displayCartItems();
      updateCartCount();
    }
  
    function decreaseQuantity(index) {
      if (cart[index].quantity > 1) {
        cart[index].quantity -= 1;
      } else {
        cart.splice(index, 1);
      }
      cart = mergeCartItems(cart);
      localStorage.setItem("cart", JSON.stringify(cart));
      console.log("Cart after decreaseQuantity:", cart);
      displayCartItems();
      updateCartCount();
    }
  
    function updateOrderSummary() {
      // Refresh menuItems to ensure we have the latest discounts
      menuItems = JSON.parse(localStorage.getItem("menuItems")) || [];
  
      let subtotal = 0;
      let totalDiscount = 0;
  
      orderSummary.innerHTML = `
        <h2 class="summary-title">Order Summary</h2>
        <table class="order-table">
          <thead>
            <tr>
              <th>Item Description</th>
              <th>Quantity</th>
              <th>Discount</th>
              <th>Amount</th>
            </tr>
          </thead>
          <tbody id="order-items"></tbody>
        </table>
        <div class="summary-details" id="summary-details"></div>
        <div class="place-order-section" id="place-order-section"></div>
      `;
  
      const tbody = document.getElementById("order-items");
      const summaryDetails = document.getElementById("summary-details");
      const placeOrderSection = document.getElementById("place-order-section");
  
      if (!tbody || !summaryDetails || !placeOrderSection) {
        console.error("One or more DOM elements for order summary not found.");
        return;
      }
  
      cart.forEach((item) => {
        const quantity = item.quantity || 1;
        const itemPrice = parseFloat(item.price) || 0;
        const itemTotal = itemPrice * quantity;
  
        // Fetch the latest discount from menuItems
        const menuItem = menuItems.find((i) => i.itemId === item.itemId);
        const discountPercentage = menuItem && menuItem.discount ? parseFloat(menuItem.discount) : (item.discount ? parseFloat(item.discount) : 0);
        const itemDiscount = (itemTotal * discountPercentage) / 100;
        const actualPrice = itemTotal - itemDiscount;
  
        // Ensure itemName is present
        const displayName = item.itemName || item.name || (menuItem ? menuItem.name : `Unknown Item (ID: ${item.itemId})`);
  
        const row = document.createElement("tr");
        row.innerHTML = `
          <td>${displayName} (₹${itemTotal.toFixed(2)})</td>
          <td>${quantity}</td>
          <td>${discountPercentage > 0 ? `₹${itemDiscount.toFixed(2)} (${discountPercentage}%)` : "₹0.00"}</td>
          <td>₹${actualPrice.toFixed(2)}</td>
        `;
        tbody.appendChild(row);
  
        subtotal += itemTotal;
        totalDiscount += itemDiscount;
  
        console.log(`Item: ${displayName}, Price: ${itemPrice}, Quantity: ${quantity}, Item Total: ${itemTotal}, Discount (${discountPercentage}%): ${itemDiscount}, Actual Price: ${actualPrice}`);
      });
  
      const taxRate = 0.18;
      const tax = (subtotal - totalDiscount) * taxRate;
      const deliveryCharge = 50.0;
      const total = (subtotal - totalDiscount) + tax + deliveryCharge;
  
      console.log(`Subtotal: ${subtotal}, Tax: ${tax}, Delivery: ${deliveryCharge}, Discount: ${totalDiscount}, Total: ${total}`);
  
      summaryDetails.innerHTML = `
        <div class="summary-item">
          <span>Subtotal:</span> <span class="summary-value">₹${(subtotal - totalDiscount).toFixed(2)}</span>
        </div>
        <div class="summary-item">
          <span>Tax (18%):</span> <span class="summary-value">₹${tax.toFixed(2)}</span>
        </div>
        <div class="summary-item">
          <span>Delivery Charge:</span> <span class="summary-value">₹${deliveryCharge.toFixed(2)}</span>
        </div>
        <div class="summary-item total">
          <span>Total:</span> <span class="summary-value">₹${total.toFixed(2)}</span>
        </div>
      `;
  
      placeOrderSection.innerHTML = `
        <button id="place-order-button" class="place-order-btn">Place Order</button>
      `;
  
      const newPlaceOrderButton = document.getElementById("place-order-button");
      if (newPlaceOrderButton) {
        newPlaceOrderButton.addEventListener("click", function () {
          if (cart.length === 0) {
            alert("Your cart is empty. Please add items to place an order.");
            return;
          }
  
          // Refresh menuItems again before placing the order
          menuItems = JSON.parse(localStorage.getItem("menuItems")) || [];
  
          let subtotal = 0;
          let totalDiscount = 0;
  
          cart.forEach((item) => {
            const quantity = item.quantity || 1;
            const itemPrice = parseFloat(item.price) || 0;
            const itemTotal = itemPrice * quantity;
  
            const menuItem = menuItems.find((i) => i.itemId === item.itemId);
            const discountPercentage = menuItem && menuItem.discount ? parseFloat(menuItem.discount) : (item.discount ? parseFloat(item.discount) : 0);
            const itemDiscount = (itemTotal * discountPercentage) / 100;
  
            subtotal += itemTotal;
            totalDiscount += itemDiscount;
  
            if (menuItem) {
              const currentStock = parseInt(menuItem.stockAvailable) || 0;
              menuItem.stockAvailable = Math.max(0, currentStock - quantity).toString();
            }
          });
  
          localStorage.setItem("menuItems", JSON.stringify(menuItems));
  
          const tax = (subtotal - totalDiscount) * 0.18;
          const deliveryCharge = 50.0;
          const total = (subtotal - totalDiscount) + tax + deliveryCharge;
  
          const orderId = "ORD" + Date.now();
          const date = new Date().toLocaleString();
  
          const order = {
            orderId: orderId,
            items: cart.map((item) => {
              const menuItem = menuItems.find((i) => i.itemId === item.itemId);
              return {
                itemId: item.itemId,
                itemName: item.itemName || item.name || (menuItem ? menuItem.name : `Unknown Item (ID: ${item.itemId})`),
                quantity: item.quantity || 1,
                price: item.price,
                discount: menuItem && menuItem.discount ? parseFloat(menuItem.discount) : (item.discount ? parseFloat(item.discount) : 0),
              };
            }),
            total: total,
            date: date,
            status: "pending",
          };
  
          // Save the order to localStorage but do not clear the cart yet
          localStorage.setItem("pendingOrder", JSON.stringify(order));
          orders.push(order);
          localStorage.setItem("orders", JSON.stringify(orders));
  
          // Redirect to delivery_details.html without clearing the cart
          window.location.href = "delivery_details";
        });
      }
    }
  
    function displayOrderHistory() {
      const orders = JSON.parse(localStorage.getItem("orders")) || [];
      orderHistoryContainer.innerHTML = "";
  
      const deliveredOrders = orders.filter((order) => order.status === "delivered");
  
      if (deliveredOrders.length === 0) {
        orderHistorySection.style.display = "none";
        return;
      }
  
      orderHistorySection.style.display = "block";
  
      const tableHeader = document.querySelector("#order-history table thead tr");
      tableHeader.innerHTML = `
        <th>Order ID</th>
        <th>Item</th>
        <th>Price</th>
        <th>Date</th>
      `;
  
      deliveredOrders.forEach((order) => {
        const orderRow = document.createElement("tr");
        const itemsDetails = order.items
          .map((item) => {
            const menuItem = menuItems.find((i) => i.itemId === item.itemId);
            return menuItem ? `${menuItem.name} x ${item.quantity || 1}` : "Unknown Item";
          })
          .join(", ");
        orderRow.innerHTML = `
          <td>${order.orderId}</td>
          <td>${itemsDetails}</td>
          <td>₹ ${order.total.toFixed(2)}</td>
          <td>${order.date}</td>
        `;
        orderHistoryContainer.appendChild(orderRow);
      });
    }
  
    clearOrdersButton.addEventListener("click", function () {
      orders = orders.filter((order) => order.status !== "delivered");
      localStorage.setItem("orders", JSON.stringify(orders));
      displayOrderHistory();
    });
  
    displayCartItems();
    displayOrderHistory();
    updateCartCount();
  
    // Add CSS for the stock alert popup, table styling, and handle dark/light mode styles
    const popupStyles = `
      .popup-container {
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: #069c54;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        z-index: 1000;
        text-align: center;
      }
      .popup-container p {
        margin: 0 0 15px;
        font-size: 16px;
        color: #fff;
      }
      .button-group {
        display: flex;
        justify-content: center;
        gap: 10px;
      }
      .button-group button {
        padding: 8px 16px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-size: 14px;
      }
      .button-group #close-stock-alert {
        background: #fff;
        color: #333;
      }
      .button-group button:hover {
        opacity: 0.9;
      }
      .order-table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 20px;
        background: #fff;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        border-radius: 8px;
        overflow: hidden;
      }
      .order-table th {
        background-color: #4CAF50;
        color: white;
        padding: 12px;
        text-align: left;
        font-weight: bold;
      }
      .order-table td {
        padding: 12px;
        border-bottom: 1px solid #ddd;
      }
      .order-table tr:last-child td {
        border-bottom: none;
      }
      .order-table tr:hover {
        background-color: #f5f5f5;
      }
      .summary-details {
        background: #f9f9f9;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
      }
      .summary-item {
        display: flex;
        justify-content: space-between;
        margin-bottom: 10px;
        font-size: 16px;
        color: #333;
      }
      .summary-item.total {
        font-size: 18px;
        font-weight: bold;
        border-top: 1px solid #ddd;
        padding-top: 10px;
      }
      .summary-value {
        color: #4CAF50;
      }
      .place-order-section {
        margin-top: 20px;
        text-align: center;
      }
      .place-order-btn {
        background: #4CAF50;
        color: white;
        padding: 12px 24px;
        border: none;
        border-radius: 8px;
        font-size: 18px;
        font-weight: bold;
        cursor: pointer;
        transition: background 0.3s, transform 0.1s;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
      }
      .place-order-btn:hover {
        background: #45a049;
        transform: scale(1.05);
      }
      .place-order-btn:active {
        transform: scale(0.95);
      }
      @media (prefers-color-scheme: light) {
        .cart__item-name {
          color: green !important;
        }
      }
      @media (prefers-color-scheme: dark) {
        .cart__item-details h3,
        .cart__item-details p,
        .empty-cart-container p,
        .quantity-controls span,
        .cart__select-all label,
        .cart__selection-buttons button,
        .cart__clear-button,
        .summary-title,
        .order-table th,
        .order-table td,
        .summary-details .summary-item {
          color: #000 !important;
        }
      }
      .cart__item-img {
        width: 50px;
        height: 50px;
        object-fit: cover;
        border-radius: 5px;
      }
    `;
    const styleSheet = document.createElement("style");
    styleSheet.textContent = popupStyles;
    document.head.appendChild(styleSheet);
  });