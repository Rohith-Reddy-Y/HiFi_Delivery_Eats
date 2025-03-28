document.addEventListener("DOMContentLoaded", function () {
    const orderPreview = document.getElementById("total-preview");
    const confirmOrderButton = document.getElementById("confirm-order-btn");
    const cartCountElement = document.getElementById("cart-count");
    const popupOverlay = document.getElementById("popup-overlay");
    const popupTitle = document.getElementById("popup-title");
    const popupMessage = document.getElementById("popup-message");
    const popupClose = document.getElementById("popup-close");
    const popupConfirm = document.getElementById("popup-confirm");

    const cart = window.initialCart || [];
    const total = window.total || 0;

    console.log(total);

    const subtotal = window.subtotal || 0;
    const tax = window.tax || 0;
    const deliveryCharge = window.deliveryCharge || 0;

    function getCartTotalItems() {
        return cart.reduce((sum, item) => sum + (item.quantity || 1), 0);
    }

    // function updateCartCount() {
    //     const totalItems = getCartTotalItems();
    //     const cartLink = document.querySelector('.nav__link[href="/order"]');
    //     if (cartLink) {
    //         const span = cartLink.querySelector(".nav__cart-count");
    //         if (span) span.textContent = totalItems;
    //     }
    // }

    function updateOrderPreview() {
        orderPreview.innerHTML = `
            <p>Total: <span id="total-preview">₹${total.toFixed(2)}</span></p>
        `;
    }

    // Initialize Leaflet Map
    let map, marker;
    function initMap() {
        // Ensure the map container is visible before initialization
        const mapContainer = document.getElementById("map");
        if (!mapContainer) {
            console.error("Map container not found!");
            return;
        }

        // map = L.map("map").setView([12.9716, 77.5946], 12); // Default: Bengaluru

        // Initialize map with explicit dimensions check
        map = L.map(mapContainer, {
            center: [28.5355, 77.3910], // Noida
            zoom: 12,
            scrollWheelZoom: false
        });

        L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
            attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        }).addTo(map);

        map.on("click", function (event) {
            const lat = event.latlng.lat;
            const lng = event.latlng.lng;
            geocodeLatLng(lat, lng);
            updateMarker(lat, lng);
            document.getElementById("coordinates").value = `(${lat.toFixed(6)}, ${lng.toFixed(6)})`;
        });

        // Robust map resizing function
        function resizeMap() {
            if (map) {
                map.invalidateSize();
                // Force a redraw of tiles
                map.setView([28.5355, 77.3910], 12);
            }
        }

        // Wait for animations and DOM to settle, then resize
        setTimeout(resizeMap, 1000); // Increased to 1000ms to account for fadeIn (0.8s)
        window.addEventListener("resize", resizeMap);

        // Additional check after map loads
        map.whenReady(() => {
            setTimeout(resizeMap, 100); // Extra call after tiles load
        });
    }

    function updateMarker(lat, lng) {
        if (marker) map.removeLayer(marker);
        marker = L.marker([lat, lng]).addTo(map);
        map.setView([lat, lng], 15);
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


    // Popup functions
    function showPopup(title, message, isConfirm = false) {
        popupTitle.textContent = title;
        popupMessage.textContent = message;
        popupOverlay.style.display = "flex";
        popupConfirm.style.display = isConfirm ? "inline-block" : "none";
        popupClose.style.display = "inline-block";
    }

    function hidePopup() {
        popupOverlay.style.display = "none";
    }

    popupOverlay.addEventListener("click", function (e) {
        if (e.target === popupOverlay) hidePopup();
    });
    popupClose.addEventListener("click", hidePopup);

    // Validate and show confirmation popup
    function validateAndProceed() {
        const name = document.getElementById("name").value.trim();
        const phone = document.getElementById("phone").value.trim();
        const street = document.getElementById("street").value.trim();
        const city = document.getElementById("city").value.trim();
        const state = document.getElementById("state").value.trim();
        const pincode = document.getElementById("pincode").value.trim();

        if (!name || !phone || !street || !city || !state || !pincode) {
            showPopup("Error", "Please fill out all delivery details.");
            return;
        }

        showPopup("Confirmation", "Are you sure you want to confirm this order?", true);
    }

    // Handle order confirmation
    function proceedWithOrder() {
        const deliveryDetails = {
            name: document.getElementById("name").value.trim(),
            phone: document.getElementById("phone").value.trim(),
            street: document.getElementById("street").value.trim(),
            city: document.getElementById("city").value.trim(),
            state: document.getElementById("state").value.trim(),
            pincode: document.getElementById("pincode").value.trim(),
            coordinates: document.getElementById("coordinates").value.trim(),
            payment_method: document.querySelector('input[name="payment"]:checked').value
        };

        const orderData = {
            total: total,
            subtotal: subtotal,
            tax: tax,
            delivery_charge: deliveryCharge,
            delivery_details: deliveryDetails
        };

        fetch('/api/orders', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify(orderData)
        })
        .then(response => {
            if (!response.ok) throw new Error('Failed to place order');
            return response.json();
        })
        .then(data => {
            window.location.href = `/order_confirmation?order_id=${data.order_id}`;
        })
        .catch(error => {
            console.error("Error placing order:", error);
            showPopup("Error", "Failed to place order: " + error.message);
        });
    }

    // Event listeners
    confirmOrderButton.addEventListener("click", validateAndProceed);
    popupConfirm.addEventListener("click", function () {
        hidePopup();
        proceedWithOrder();
    });

    updateOrderPreview();
    // updateCartCount();
    initMap();
});