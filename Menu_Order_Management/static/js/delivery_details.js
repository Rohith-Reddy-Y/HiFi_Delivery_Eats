document.addEventListener("DOMContentLoaded", function () {
    const totalPreviewElement = document.getElementById("total-preview");
    const confirmOrderButton = document.getElementById("confirm-order-btn");
    const cartCountElement = document.getElementById("cart-count");
    const themeButton = document.getElementById("theme-button");
    const body = document.body;
    const popupOverlay = document.getElementById("popup-overlay");
    const popup = document.getElementById("popup");
    const popupTitle = document.getElementById("popup-title");
    const popupMessage = document.getElementById("popup-message");
    const popupClose = document.getElementById("popup-close");
    const popupConfirm = document.getElementById("popup-confirm");

    // Load cart and summary data from localStorage
    const cart = JSON.parse(localStorage.getItem("cart")) || [];
    const orders = JSON.parse(localStorage.getItem("orders")) || [];
    const menuItems = JSON.parse(localStorage.getItem("menuItems")) || [];
    const pendingOrder = JSON.parse(localStorage.getItem("pendingOrder")) || {};

    // Calculate and format total from cart and menuItems
    const calculateTotal = () => {
        let subtotal = 0;
        let totalDiscount = 0;
        cart.forEach(item => {
            const menuItem = menuItems.find(m => m.itemId === item.itemId);
            const unitPrice = menuItem ? parseFloat(menuItem.price) || 0 : (item.price ? parseFloat(item.price) : 0);
            const discountPercentage = menuItem ? parseFloat(menuItem.discount) || 0 : (item.discount ? parseFloat(item.discount) : 0);
            const discountAmount = (unitPrice * discountPercentage) / 100;
            subtotal += unitPrice * (item.quantity || 1);
            totalDiscount += discountAmount * (item.quantity || 1);
        });
        const tax = (subtotal - totalDiscount) * 0.18;
        const deliveryCharge = 50.0;
        return (subtotal - totalDiscount + tax + deliveryCharge).toFixed(2);
    };

    // Display formatted total in preview
    const total = pendingOrder.total ? parseFloat(pendingOrder.total).toFixed(2) : calculateTotal();
    totalPreviewElement.textContent = `₹${total}`;

    // Update cart count in title bar
    function updateCartCount() {
        const cart = JSON.parse(localStorage.getItem("cart")) || [];
        const totalItems = cart.reduce((sum, item) => sum + (item.quantity || 1), 0);
        cartCountElement.textContent = totalItems;
    }
    updateCartCount();

    // Initialize Leaflet Map
    let map;
    let marker;
    function initMap() {
        if (document.getElementById("map")) {
            map = L.map("map").setView([12.9716, 77.5946], 12);

            L.tileLayer(
                "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
                {
                    attribution:
                        "Tiles © Esri — Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community",
                }
            ).addTo(map);

            L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
                attribution:
                    '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                opacity: 0.5,
            }).addTo(map);

            map.on("click", function (event) {
                const lat = event.latlng.lat;
                const lng = event.latlng.lng;
                geocodeLatLng(lat, lng);
                updateMarker(lat, lng);
            });

            setTimeout(() => {
                map.invalidateSize();
            }, 100);
        }
    }

    function updateMarker(lat, lng) {
        const redIcon = L.icon({
            iconUrl:
                "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png",
            shadowUrl:
                "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
            iconSize: [25, 41],
            iconAnchor: [12, 41],
            popupAnchor: [1, -34],
            shadowSize: [41, 41],
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
                    const city =
                        address.city ||
                        address.city_district ||
                        address.county ||
                        address.town ||
                        address.village ||
                        address.suburb ||
                        "";
                    const state = address.state || "";
                    const pincode = address.postcode || "";

                    document.getElementById("street").value = street;
                    document.getElementById("city").value = city;
                    document.getElementById("state").value = state;
                    document.getElementById("pincode").value = pincode;
                    document.getElementById("coordinates").value = `(${lat}, ${lng})`;
                } else {
                    showPopup("Error", "No address found for this location.");
                }
            })
            .catch((error) => {
                console.error("Reverse Geocoding error:", error);
                showPopup("Error", "Failed to fetch address. Please try again.");
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

        const nominatimUrl = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(
            address
        )}`;

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
                    showPopup("Error", "No coordinates found for this address.");
                }
            })
            .catch((error) => {
                console.error("Forward Geocoding error:", error);
                showPopup("Error", "Failed to locate the address on the map. Please try again.");
            });
    }

    // Initialize map
    initMap();

    // Add event listeners for address fields
    const addressFields = ["street", "city", "state", "pincode"];
    addressFields.forEach((fieldId) => {
        const field = document.getElementById(fieldId);
        if (field) {
            field.addEventListener("input", geocodeAddress);
        }
    });

    // Function to resolve image references
    function resolveImage(image, itemId) {
        if (image && image.startsWith("ref:")) {
            const id = image.split("ref:")[1];
            const menuItem = menuItems.find((item) => item.itemId === id);
            return menuItem ? menuItem.image : "";
        }
        return image;
    }

    // Simulate delivery for order tracking
    function simulateDelivery(order, callback) {
        setTimeout(() => {
            order.status = "delivered";
            const updatedOrders = orders.map((o) =>
                o.orderId === order.orderId ? order : o
            );
            localStorage.setItem("orders", JSON.stringify(updatedOrders));
            callback();
        }, 10000);
    }

    // Popup Function
    function showPopup(title, message, isConfirm = false) {
        popupTitle.textContent = title;
        popupMessage.textContent = message;
        popupOverlay.style.display = "flex";

        if (isConfirm) {
            popupConfirm.style.display = "inline-block";
            popupClose.style.display = "inline-block";
        } else {
            popupConfirm.style.display = "none";
            popupClose.style.display = "inline-block";
        }

        popupOverlay.addEventListener("click", function (e) {
            if (e.target === popupOverlay) {
                hidePopup();
            }
        });

        popupClose.addEventListener("click", hidePopup);
        if (isConfirm) {
            popupConfirm.addEventListener("click", function confirmAction() {
                hidePopup();
                proceedWithOrder();
                popupConfirm.removeEventListener("click", confirmAction);
            });
        }
    }

    function hidePopup() {
        popupOverlay.style.display = "none";
    }

    // Handle Confirm Order button click with popup
    function validateAndProceed() {
        const name = document.getElementById("name").value.trim();
        const phone = document.getElementById("phone").value.trim();
        const street = document.getElementById("street").value.trim();
        const city = document.getElementById("city").value.trim();
        const state = document.getElementById("state").value.trim();
        const pincode = document.getElementById("pincode").value.trim();

        // Validate inputs
        if (!name || !phone || !street || !city || !state || !pincode) {
            showPopup("Error", "Please fill out all delivery details.");
            return;
        }

        // Debug: Log cart state before showing confirmation popup
        console.log("Cart before confirmation popup:", JSON.parse(localStorage.getItem("cart") || "[]"));

        // If all fields are filled, show confirmation popup
        showPopup("Confirmation", "Are you sure you want to confirm this order?", true);
    }

    function proceedWithOrder() {
        // Debug: Log cart state at the start of proceedWithOrder
        console.log("Cart at start of proceedWithOrder:", JSON.parse(localStorage.getItem("cart") || "[]"));

        const name = document.getElementById("name").value.trim();
        const phone = document.getElementById("phone").value.trim();
        const street = document.getElementById("street").value.trim();
        const city = document.getElementById("city").value.trim();
        const state = document.getElementById("state").value.trim();
        const pincode = document.getElementById("pincode").value.trim();
        const coordinates = document.getElementById("coordinates").value.trim();
        const paymentMethod = document.querySelector('input[name="payment"]:checked').value;

        // Validate inputs
        if (!name || !phone || !street || !city || !state || !pincode) {
            showPopup("Error", "Please fill out all delivery details.");
            return;
        }

        // Load cart and menu items
        const cart = JSON.parse(localStorage.getItem("cart")) || [];
        const menuItems = JSON.parse(localStorage.getItem("menuItems")) || [];
        const orders = JSON.parse(localStorage.getItem("orders")) || [];
        const pendingOrder = JSON.parse(localStorage.getItem("pendingOrder")) || {};

        // Debug: Log cart after loading
        console.log("Cart after loading in proceedWithOrder:", cart);

        if (cart.length === 0) {
            showPopup("Error", "Your cart is empty. Please add some items before confirming the order.");
            return;
        }

        // Update stock in menuItems
        cart.forEach((item) => {
            const menuItem = menuItems.find((i) => i.itemId === item.itemId);
            if (menuItem) {
                const currentStock = parseInt(menuItem.stockAvailable) || 0;
                const quantity = item.quantity || 1;
                menuItem.stockAvailable = Math.max(0, currentStock - quantity).toString();
            }
        });
        localStorage.setItem("menuItems", JSON.stringify(menuItems));

        // Recalculate and format total from cart
        const calculateTotal = () => {
            let subtotal = 0;
            let totalDiscount = 0;
            cart.forEach(item => {
                const menuItem = menuItems.find(m => m.itemId === item.itemId);
                const unitPrice = menuItem ? parseFloat(menuItem.price) || 0 : (item.price ? parseFloat(item.price) : 0);
                const discountPercentage = menuItem ? parseFloat(menuItem.discount) || 0 : (item.discount ? parseFloat(item.discount) : 0);
                const discountAmount = (unitPrice * discountPercentage) / 100;
                subtotal += unitPrice * (item.quantity || 1);
                totalDiscount += discountAmount * (item.quantity || 1);
            });
            const tax = (subtotal - totalDiscount) * 0.18;
            const deliveryCharge = 50.0;
            return {
                subtotal: (subtotal - totalDiscount).toFixed(2),
                tax: tax.toFixed(2),
                deliveryCharge: deliveryCharge.toFixed(2),
                total: (subtotal - totalDiscount + tax + deliveryCharge).toFixed(2)
            };
        };
        const totals = calculateTotal();
        totalPreviewElement.textContent = `₹${totals.total}`; // Update display before proceeding

        // Use orderId from pendingOrder if available, otherwise generate a new one
        const orderId = pendingOrder.orderId || ("ORD" + Date.now());
        const date = new Date().toLocaleString();
        const order = {
            orderId: orderId,
            name: name,
            items: cart.map(item => {
                const menuItem = menuItems.find(m => m.itemId === item.itemId);
                return {
                    itemId: item.itemId,
                    itemName: item.itemName || (menuItem ? menuItem.name : `Unknown Item (ID: ${item.itemId})`),
                    quantity: item.quantity || 1,
                    price: menuItem ? parseFloat(menuItem.price) || 0 : (item.price ? parseFloat(item.price) : 0),
                    discount: menuItem ? parseFloat(menuItem.discount) || 0 : (item.discount ? parseFloat(item.discount) : 0),
                };
            }),
            subtotal: totals.subtotal,
            tax: totals.tax,
            deliveryCharge: totals.deliveryCharge,
            total: parseFloat(totals.total),
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

        // Update orders array (replace the pending order if it exists)
        const existingOrderIndex = orders.findIndex(o => o.orderId === order.orderId);
        if (existingOrderIndex !== -1) {
            orders[existingOrderIndex] = order;
        } else {
            orders.push(order);
        }

        // Save order and clear pendingOrder
        localStorage.setItem("orders", JSON.stringify(orders));
        localStorage.setItem("currentOrder", JSON.stringify(order));
        localStorage.setItem("pendingOrder", JSON.stringify({}));

        // Clear the cart using the function from show_menu.js
        if (typeof window.clearCart === "function") {
            window.clearCart();
        } else {
            console.warn("window.clearCart not available, clearing cart manually");
            localStorage.setItem("cart", JSON.stringify([]));
        }

        // Debug: Log cart state before redirect
        console.log("Cart before redirect to order_track.html:", JSON.parse(localStorage.getItem("cart") || "[]"));

        // Redirect to order_track.html
        window.location.href = "order_track";
    }

    confirmOrderButton.addEventListener("click", validateAndProceed);

    // Theme Toggle Functionality
    let isDarkMode = localStorage.getItem("dark-mode") === "true";
    if (isDarkMode) {
        body.classList.add("dark-theme");
        themeButton.classList.remove("bx-moon");
        themeButton.classList.add("bx-sun");
    }

    themeButton.addEventListener("click", () => {
        isDarkMode = !isDarkMode;
        if (isDarkMode) {
            body.classList.add("dark-theme");
            themeButton.classList.remove("bx-moon");
            themeButton.classList.add("bx-sun");
        } else {
            body.classList.remove("dark-theme");
            themeButton.classList.remove("bx-sun");
            themeButton.classList.add("bx-moon");
        }
        localStorage.setItem("dark-mode", isDarkMode);
    });
});