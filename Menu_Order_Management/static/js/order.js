document.addEventListener("DOMContentLoaded", function () {
  const cartItemsContainer = document.getElementById("cart-items");
  const orderSummary = document.getElementById("order-summary");
  const subtotalElement = document.getElementById("subtotal");
  const taxElement = document.getElementById("tax");
  const deliveryElement = document.getElementById("delivery");
  const discountElement = document.getElementById("discount");
  const totalElement = document.getElementById("total");
  const placeOrderButton = document.getElementById("place-order-button");
  const orderHistoryContainer = document.getElementById("order-history-details");
  const orderHistorySection = document.getElementById("order-history");
  const orderConfirmationSection = document.getElementById("order-confirmation");
  const orderDetailsContainer = document.getElementById("order-details");
  const clearOrdersButton = document.getElementById("clear-orders-button");
  const clearControlsContainer = document.getElementById("cart-clear-controls");
  const currentOrderSection = document.getElementById("current-order");
  const currentOrderDetailsContainer = document.getElementById("current-order-details");
  const cancelOrderButton = document.getElementById("cancel-order-button");

  // Load cart items, orders, and menu items from localStorage
  let cart = JSON.parse(localStorage.getItem("cart")) || [];
  let orders = JSON.parse(localStorage.getItem("orders")) || [];
  let menuItems = JSON.parse(localStorage.getItem("menuItems")) || [];
  let orderJustPlaced = false;
  let isSelectionMode = false;
  let currentOrder = null;

  // Debug: Log initial cart state
  console.log("Initial cart state in order.js:", cart);
  console.log("Initial localStorage cart:", JSON.parse(localStorage.getItem("cart")));

  // Function to resolve image references
  function resolveImage(image, itemId) {
    if (image && image.startsWith("ref:")) {
      const id = image.split("ref:")[1];
      const menuItem = menuItems.find(item => item.itemId === id);
      return menuItem ? menuItem.image : "";
    }
    return image;
  }

  // Function to calculate total items in the cart
  function getCartTotalItems() {
    return cart.reduce((sum, item) => sum + (item.quantity || 1), 0);
  }
  
  // Function to update cart count in the navigation bar (aligned with show_menu.js)
  function updateCartCount() {
    cart = JSON.parse(localStorage.getItem("cart")) || [];
    const totalItems = getCartTotalItems();
    const cartLink = document.querySelector('.nav__cart-count');
  //   alert(`${totalItems}`);
    if (cartLink) {
      const span = cartLink.querySelector('.nav__cart-count');
      if (span) {
        span.textContent = totalItems;
      } else {
        const newSpan = document.createElement('span');
        newSpan.className = 'nav__cart-count';
      //   alert(`cart count update : ${newSpan}`);
        newSpan.textContent = totalItems;
      //   cartLink.textContent = 'Cart(';
        cartLink.appendChild(newSpan);
      //   cartLink.appendChild(document.createTextNode(')'));
      }
      console.log("Updated cart count to:", totalItems);
    } else {
      console.error("Cart link element not found.");
    }
  }
  
  // Initialize Leaflet Map
  let map;
  let marker;
  function initMap() {
    map = L.map("map").setView([12.9716, 77.5946], 12);

    L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}", {
      attribution: 'Tiles © Esri — Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
    }).addTo(map);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      opacity: 0.5,
    }).addTo(map);

    map.on("click", function (event) {
      const lat = event.latlng.lat;
      const lng = event.latlng.lng;
      geocodeLatLng(lat, lng);
      updateMarker(lat, lng);
    });
  }

  function updateMarker(lat, lng) {
    const redIcon = L.icon({
      iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
      shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
      iconSize: [25, 41],
      iconAnchor: [12, 41],
      popupAnchor: [1, -34],
      shadowSize: [41, 41]
    });

    if (marker) {
      map.removeLayer(marker);
    }
    marker = L.marker([lat, lng], { icon: redIcon }).addTo(map);
  }

  function geocodeLatLng(lat, lng) {
    const nominatimUrl = `https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${lat}&lon=${lng}`;

    fetch(nominatimUrl, {
      headers: {
        "User-Agent": "HIFI-Delivery-Eats/1.0 (your-email@example.com)",
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data && data.address) {
          const address = data.address;
          const street = address.road || address.street || "";
          const city = address.city || address.city_district || address.county || address.town || address.village || address.suburb || "";
          const state = address.state || "";
          const pincode = address.postcode || "";

          document.getElementById("street").value = street;
          document.getElementById("city").value = city;
          document.getElementById("state").value = state;
          document.getElementById("pincode").value = pincode;
          document.getElementById("coordinates").value = `(${lat}, ${lng})`;
        } else {
          alert("No address found for this location");
        }
      })
      .catch((error) => {
        console.error("Reverse Geocoding error:", error);
        alert("Failed to fetch address. Please try again.");
      });
  }

  function geocodeAddress() {
    const street = document.getElementById("street").value.trim();
    const city = document.getElementById("city").value.trim();
    const state = document.getElementById("state").value.trim();
    const pincode = document.getElementById("pincode").value.trim();

    const address = [street, city, state, pincode].filter(Boolean).join(", ");

    if (!address) {
      return;
    }

    const nominatimUrl = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(address)}`;

    fetch(nominatimUrl, {
      headers: {
        "User-Agent": "HIFI-Delivery-Eats/1.0 (your-email@example.com)",
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data && data.length > 0) {
          const result = data[0];
          const lat = parseFloat(result.lat);
          const lng = parseFloat(result.lon);

          map.setView([lat, lng], 12);
          updateMarker(lat, lng);
          document.getElementById("coordinates").value = `(${lat}, ${lng})`;
        } else {
          console.log("No coordinates found for this address");
        }
      })
      .catch((error) => {
        console.error("Forward Geocoding error:", error);
        alert("Failed to locate the address on the map. Please try again.");
      });
  }

  initMap();

  const addressFields = ["street", "city", "state", "pincode"];
  addressFields.forEach((fieldId) => {
    const field = document.getElementById(fieldId);
    field.addEventListener("input", geocodeAddress);
  });

  function mergeCartItems(cart) {
    const mergedCart = [];
    cart.forEach((item) => {
      const existingItem = mergedCart.find(
        (cartItem) => cartItem.name === item.name && cartItem.price === item.price
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
    }, 5000);
  }

  function displayCartItems() {
    cartItemsContainer.innerHTML = "";
    clearControlsContainer.innerHTML = "";

    // Debug: Log cart state before display
    console.log("Cart state before displayCartItems:", cart);

    if (cart.length === 0) {
      if (!orderJustPlaced) {
        cartItemsContainer.innerHTML = `
          <div class="empty-cart-container">
            <img src="/static/images/cart.png" alt="Empty Cart" class="empty-cart-image" onerror="this.onerror=null; this.src='https://via.placeholder.com/150?text=Cart+Image+Not+Found'; console.log('Failed to load cart.png at ../images/cart.png');" />
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

    if (map) {
      setTimeout(() => {
        map.invalidateSize();
      }, 0);
    }

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
          const selectedItems = Array.from(
            document.querySelectorAll(".cart__item-checkbox input:checked")
          ).map((input) => parseInt(input.value));
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
        const adjustedImagePath = item.image.startsWith("ref:")
          ? resolveImage(item.image, item.itemId)
          : item.image.startsWith("/home")
          ? `../${item.image.split("/home/")[1]}`
          : item.image;
        cartItem.innerHTML = `
          ${isSelectionMode ? `
            <div class="cart__item-checkbox">
              <input type="checkbox" id="cart-item-${index}" value="${index}" />
              <label for="cart-item-${index}"></label>
            </div>
          ` : ""}
          <img src="${adjustedImagePath}" alt="${item.name}" class="cart__item-img" />
          <div class="cart__item-details">
              <h3 class="cart__item-name">${item.name}</h3>
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

  // Add event listeners for quantity controls
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
    cart[index].quantity = (cart[index].quantity || 1) + 1;
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
    let subtotal = 0;
    cart.forEach((item) => {
      const quantity = item.quantity || 1;
      const itemPrice = parseFloat(item.price) || 0;
      const itemTotal = itemPrice * quantity;
      subtotal += itemTotal;
      console.log(`Item: ${item.name}, Price: ${itemPrice}, Quantity: ${quantity}, Item Total: ${itemTotal}`);
    });

    const taxRate = 0.18;
    const tax = subtotal * taxRate;
    const deliveryCharge = 50.0;
    const discount = 0.0;
    const total = subtotal + tax + deliveryCharge - discount;

    console.log(`Subtotal: ${subtotal}, Tax: ${tax}, Delivery: ${deliveryCharge}, Discount: ${discount}, Total: ${total}`);

    subtotalElement.textContent = `₹ ${subtotal.toFixed(2)}`;
    taxElement.textContent = `₹ ${tax.toFixed(2)}`;
    deliveryElement.textContent = `₹ ${deliveryCharge.toFixed(2)}`;
    discountElement.textContent = `₹ ${discount.toFixed(2)}`;
    totalElement.textContent = `₹ ${total.toFixed(2)}`;
  }

  function displayCurrentOrder() {
    currentOrderDetailsContainer.innerHTML = "";

    if (!currentOrder) {
      currentOrderSection.style.display = "none";
      return;
    }

    currentOrderSection.style.display = "block";
    const orderRow = document.createElement("tr");
    const deliveryDetails = `${currentOrder.street}, ${currentOrder.city}, ${currentOrder.state} - ${currentOrder.pincode}<br>Phone: ${currentOrder.phone}`;
    const itemsDetails = currentOrder.items
      .map((item) => `${item.name} x ${item.quantity || 1}`)
      .join(", ");
    const adjustedImagePath = currentOrder.items[0].image.startsWith("ref:")
      ? resolveImage(currentOrder.items[0].image, currentOrder.items[0].itemId)
      : currentOrder.items[0].image.startsWith("/home")
      ? `../${currentOrder.items[0].image.split("/home/")[1]}`
      : currentOrder.items[0].image;
    orderRow.innerHTML = `
      <td>${currentOrder.orderId}</td>
      <td>${currentOrder.name}</td>
      <td><img src="${adjustedImagePath}" alt="${currentOrder.items[0].name}" width="50" /></td>
      <td>${itemsDetails}</td>
      <td>₹ ${currentOrder.total.toFixed(2)}</td>
      <td>${deliveryDetails}</td>
      <td>${currentOrder.coordinates || "N/A"}</td>
      <td>${currentOrder.paymentMethod}</td>
      <td>${currentOrder.deliveryAgentDetails || "Not Assigned"}</td>
      <td>${currentOrder.orderTracking || currentOrder.status || "Pending"}</td>
    `;
    currentOrderDetailsContainer.appendChild(orderRow);

    cancelOrderButton.style.display = currentOrder.status === "delivered" ? "none" : "block";
    cancelOrderButton.style.marginLeft = "auto";
    cancelOrderButton.style.display = currentOrder.status === "delivered" ? "none" : "block";
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
      <th>Name</th>
      <th>Image</th>
      <th>Item</th>
      <th>Price</th>
      <th>Delivery Details</th>
      <th>Coordinates</th>
      <th>Payment Method</th>
      <th>Date</th>
    `;

    deliveredOrders.forEach((order) => {
      const orderRow = document.createElement("tr");
      const deliveryDetails = `${order.street}, ${order.city}, ${order.state} - ${order.pincode}<br>Phone: ${order.phone}`;
      const itemsDetails = order.items
        .map((item) => `${item.name} x ${item.quantity || 1}`)
        .join(", ");
      const adjustedImagePath = order.items[0].image.startsWith("ref:")
        ? resolveImage(order.items[0].image, order.items[0].itemId)
        : order.items[0].image.startsWith("/home")
        ? `../${order.items[0].image.split("/home/")[1]}`
        : order.items[0].image;
      orderRow.innerHTML = `
        <td>${order.orderId}</td>
        <td>${order.name}</td>
        <td><img src="${adjustedImagePath}" alt="${order.items[0].name}" width="50" /></td>
        <td>${itemsDetails}</td>
        <td>₹ ${order.total.toFixed(2)}</td>
        <td>${deliveryDetails}</td>
        <td>${order.coordinates || "N/A"}</td>
        <td>${order.paymentMethod}</td>
        <td>${order.date}</td>
      `;
      orderHistoryContainer.appendChild(orderRow);
    });
  }

  placeOrderButton.addEventListener("click", function () {
    if (cart.length === 0) {
      alert("Your cart is empty. Please add items to place an order.");
      return;
    }

    const name = document.getElementById("name").value.trim();
    const phone = document.getElementById("phone").value.trim();
    const street = document.getElementById("street").value.trim();
    const city = document.getElementById("city").value.trim();
    const state = document.getElementById("state").value.trim();
    const pincode = document.getElementById("pincode").value.trim();
    const coordinates = document.getElementById("coordinates").value.trim();
    const paymentMethod = document.querySelector(
      'input[name="payment"]:checked'
    ).value;

    if (!name || !phone || !street || !city || !state || !pincode) {
      alert("Please fill out all delivery details.");
      return;
    }

    let subtotal = 0;
    cart.forEach((item) => {
      const quantity = item.quantity || 1;
      const itemPrice = parseFloat(item.price) || 0;
      const itemTotal = itemPrice * quantity;
      subtotal += itemTotal;
    });
    const tax = subtotal * 0.18;
    const deliveryCharge = 50.0;
    const total = subtotal + tax + deliveryCharge;

    const orderId = "ORD" + Math.floor(Math.random() * 10000);
    const date = new Date().toLocaleString();

    const order = {
      orderId: orderId,
      name: name,
      items: cart.map((item) => ({ ...item, quantity: item.quantity || 1 })),
      total: total,
      phone: phone,
      street: street,
      city: city,
      state: state,
      pincode: pincode,
      coordinates: coordinates,
      paymentMethod: paymentMethod,
      date: date,
      status: "pending",
      deliveryAgentDetails: "",
      orderTracking: "Order Placed",
    };

    orderConfirmationSection.style.display = "block";
    orderDetailsContainer.innerHTML = "";
    const orderRow = document.createElement("tr");
    const deliveryDetails = `${street}, ${city}, ${state} - ${pincode}<br>Phone: ${phone}`;
    const itemsDetails = cart
      .map((item) => `${item.name} x ${item.quantity || 1}`)
      .join(", ");
    const adjustedImagePath = cart[0].image.startsWith("ref:")
      ? resolveImage(cart[0].image, cart[0].itemId)
      : cart[0].image.startsWith("/home")
      ? `../${cart[0].image.split("/home/")[1]}`
      : cart[0].image;
    orderRow.innerHTML = `
      <td>${order.orderId}</td>
      <td>${order.name}</td>
      <td><img src="${adjustedImagePath}" alt="${cart[0].name}" width="50" /></td>
      <td>${itemsDetails}</td>
      <td>₹ ${total.toFixed(2)}</td>
      <td>${deliveryDetails}</td>
      <td>${order.coordinates || "N/A"}</td>
      <td>${order.paymentMethod}</td>
    `;
    orderDetailsContainer.appendChild(orderRow);

    const buttonContainer = document.createElement("div");
    buttonContainer.style.display = "flex";
    buttonContainer.style.justifyContent = "flex-end";
    buttonContainer.style.gap = "0.5rem";
    buttonContainer.style.marginTop = "1rem";

    const confirmButton = document.createElement("button");
    confirmButton.id = "confirm-order-button";
    confirmButton.classList.add("button");
    confirmButton.textContent = "Confirm Order";
    confirmButton.style.backgroundColor = "green";
    buttonContainer.appendChild(confirmButton);

    const cancelOrderButtonInConfirmation = document.createElement("button");
    cancelOrderButtonInConfirmation.id = "cancel-order-confirmation-button";
    cancelOrderButtonInConfirmation.classList.add("button");
    cancelOrderButtonInConfirmation.textContent = "Cancel Order";
    cancelOrderButtonInConfirmation.style.backgroundColor = "#ff4444";
    buttonContainer.appendChild(cancelOrderButtonInConfirmation);

    orderConfirmationSection.appendChild(buttonContainer);

    confirmButton.addEventListener("click", function () {
      orders.push(order);
      localStorage.setItem("orders", JSON.stringify(orders));

      currentOrder = order;

      cart = [];
      localStorage.setItem("cart", JSON.stringify(cart));
      console.log("Cart after placing order:", cart);
      orderJustPlaced = true;
      displayCartItems();
      updateCartCount();

      orderConfirmationSection.style.display = "none";
      displayCurrentOrder();

      simulateDelivery(currentOrder, () => {
        displayCurrentOrder();
        displayOrderHistory();
      });
    });

    cancelOrderButtonInConfirmation.addEventListener("click", function () {
      orderConfirmationSection.style.display = "none";
      cartItemsContainer.style.display = "block";
      orderSummary.style.display = "block";
      clearControlsContainer.style.display = "block";
      displayCartItems();
    });

    cartItemsContainer.style.display = "none";
    orderSummary.style.display = "none";
    clearControlsContainer.style.display = "none";
    orderHistorySection.style.display = "none";
  });

  cancelOrderButton.addEventListener("click", function () {
    if (!currentOrder || currentOrder.status === "delivered") {
      alert("Cannot cancel a delivered order.");
      return;
    }

    orders = orders.filter((order) => order.orderId !== currentOrder.orderId);
    localStorage.setItem("orders", JSON.stringify(orders));
    currentOrder = null;
    displayCurrentOrder();
    displayOrderHistory();
  });

  clearOrdersButton.addEventListener("click", function () {
    orders = orders.filter((order) => order.status !== "delivered");
    localStorage.setItem("orders", JSON.stringify(orders));
    displayOrderHistory();
  });

  displayCartItems();
  displayOrderHistory();
  displayCurrentOrder();

  // Force cart count update after all initial DOM updates
  updateCartCount();
  displayOrderHistory();
});