// Initialize cart from localStorage
let cart = [];
try {
  const storedCart = localStorage.getItem('cart');
  cart = storedCart ? JSON.parse(storedCart) : [];
  if (!Array.isArray(cart)) {
    console.error("Stored cart data is not an array:", cart);
    cart = [];
  }
} catch (error) {
  console.error("Error parsing cart from localStorage:", error);
  cart = [];
}
window.globalCart = cart;

// Function to save cart to localStorage
function saveCart() {
  console.log("Before saving cart:", cart);
  try {
    localStorage.setItem('cart', JSON.stringify(cart));
    window.globalCart = cart;
  } catch (error) {
    console.error("Error saving cart to localStorage:", error);
    cart.length = 0;
  }
  console.log("After saving cart:", cart);
}

// Function to calculate total items in the cart
function getCartTotalItems() {
  return cart.reduce((sum, item) => sum + (item.quantity || 1), 0);
}

// Function to update cart count in the navigation bar
function updateCartCount() {
  const totalItems = getCartTotalItems();
  const cartLink = document.querySelector('.nav__link[href="../static/templates/order.html"]');
  if (cartLink) {
    const span = cartLink.querySelector('.nav__cart-count');
    if (span) {
      span.textContent = totalItems;
    } else {
      const newSpan = document.createElement('span');
      newSpan.className = 'nav__cart-count';
      newSpan.textContent = totalItems;
      cartLink.textContent = 'Cart(';
      cartLink.appendChild(newSpan);
      cartLink.appendChild(document.createTextNode(')'));
    }
    console.log("Updated cart count to:", totalItems);
  } else {
    console.error("Cart link element not found.");
  }
}

// Function to fetch menu items from the backend
async function fetchMenuItems() {
  try {
    const response = await fetch('/api/menu_items');
    if (!response.ok) {
      throw new Error('Failed to fetch menu items');
    }
    const menuItems = await response.json();
    appendDynamicItems(menuItems);
    applyFilters();
  } catch (error) {
    console.error("Error fetching menu items:", error);
  }
}

// Function to append dynamic items to the menu
function appendDynamicItems(menuItems) {
  if (!menuItems || menuItems.length === 0) {
    console.log("No dynamic menu items to display.");
    return;
  }

  document.querySelectorAll(".menu__container .menu__content.dynamic").forEach(item => item.remove());

  menuItems.forEach((item) => {
    const subcategory = item.subcategory_name?.toLowerCase();
    if (!subcategory) {
      console.warn(`Item ${item.name} has no subcategory, skipping.`);
      return;
    }

    const categorySection = Array.from(document.querySelectorAll(".menu-category")).find(
      (category) => category.dataset.category.toLowerCase() === subcategory
    );

    if (categorySection) {
      const menuContainer = categorySection.querySelector(".menu__container");
      const baseUrl = "https://HiFiDeliveryEats.com/";
      const staticImagePath = "/static/images/";
      if (menuContainer) {
        const menuItem = document.createElement("div");
        menuItem.classList.add("menu__content", "dynamic");
        menuItem.setAttribute("data-name", item.name);
        menuItem.setAttribute("data-price", item.price);
        menuItem.setAttribute("data-type", item.category?.toLowerCase() || "");
        menuItem.setAttribute("data-item-id", item.itemId || "");
        menuItem.innerHTML = `
          <img src="${staticImagePath}${item.image_url.replace(baseUrl, '')}" alt="${item.name}" class="menu__img" />
          <h3 class="menu__name">${item.name}</h3>
          <span class="menu__detail">${item.description || ''}</span><br>
          <span class="menu__preci">₹ ${parseFloat(item.price).toFixed(2)}</span>
          <a href="#" class="button menu__button"><i class="bx bx-cart-alt"></i></a>
        `;
        menuContainer.appendChild(menuItem);
        console.log(`Added item "${item.name}" to subcategory "${subcategory}"`);
      } else {
        console.error(`Menu container not found for subcategory: ${subcategory}`);
      }
    } else {
      console.error(`Category section not found for subcategory: ${subcategory}`);
    }
  });
}

document.addEventListener("DOMContentLoaded", function () {
  fetchMenuItems();
  updateCartCount();
});

document.addEventListener("DOMContentLoaded", function () {
    // DOM Elements
    fetchMenuItems();
    const searchInput = document.querySelector(".search-input");
    const vegNonVegFilter = document.getElementById("veg-nonveg-filter");
    const subCategoryFilter = document.getElementById("sub-category");
    const menuCategories = document.querySelectorAll(".menu-category");
    const menuHeading = document.getElementById("menu-heading");
    const menuSection = document.querySelector("section.menu");
  
    // Debug DOM availability
    console.log("DOM elements:", {
      searchInput: !!searchInput,
      vegNonVegFilter: !!vegNonVegFilter,
      subCategoryFilter: !!subCategoryFilter,
      menuCategories: menuCategories.length,
      menuHeading: !!menuHeading,
      menuSection: !!menuSection
    });

    // Function to apply filters
    function applyFilters() {
      const searchQuery = searchInput?.value.trim().toLowerCase() || "";
      const vegNonVegValue = vegNonVegFilter?.value.toLowerCase() || "";
      const subCategoryValue = subCategoryFilter?.value.toLowerCase() || "";
  
      console.log("Applying filters:", { searchQuery, vegNonVegValue, subCategoryValue });
  
      let headingText = "All Menu Items";
      if (searchQuery) headingText = `Search Results for "${searchQuery}"`;
      else if (vegNonVegValue && subCategoryValue) {
        headingText = `${vegNonVegValue.charAt(0).toUpperCase() + vegNonVegValue.slice(1)} ${subCategoryValue.charAt(0).toUpperCase() + subCategoryValue.slice(1)}`;
      } else if (vegNonVegValue) {
        headingText = `${vegNonVegValue.charAt(0).toUpperCase() + vegNonVegValue.slice(1)} Items`;
      } else if (subCategoryValue) {
        headingText = subCategoryValue.charAt(0).toUpperCase() + subCategoryValue.slice(1);
      }
  
      if (menuHeading) menuHeading.textContent = headingText;
      else {
        console.error("menu-heading element not found");
        return;
      }
  
      let hasResults = false;
      menuCategories.forEach((category) => {
        const categorySubcategory = category.dataset.category.toLowerCase();
        const matchesSubCategory = !subCategoryValue || categorySubcategory === subCategoryValue;
        const items = category.querySelectorAll(".menu__content");
        let hasVisibleItems = false;
  
        items.forEach((item) => {
          const itemName = item.getAttribute("data-name")?.toLowerCase() || "";
          const itemType = item.getAttribute("data-type")?.toLowerCase() || "";
          const matchesSearch = !searchQuery || itemName.includes(searchQuery);
          const matchesVegNonVeg = !vegNonVegValue || itemType === vegNonVegValue;
  
          if (matchesSearch && matchesVegNonVeg && matchesSubCategory) {
            item.style.display = "flex";
            hasVisibleItems = true;
            hasResults = true;
          } else {
            item.style.display = "none";
          }
        });
  
        category.style.display = matchesSubCategory ? "block" : "none";
        const categoryTitle = category.querySelector(".category-title");
        if (categoryTitle) categoryTitle.style.display = matchesSubCategory ? "block" : "none";
  
        const noItemsMessage = category.querySelector(".no-items-message");
        if (noItemsMessage) noItemsMessage.remove();
  
        if (matchesSubCategory && !hasVisibleItems) {
          const message = document.createElement("p");
          message.className = "no-items-message";
          message.textContent = "No items match your filters in this category.";
          message.style.textAlign = "center";
          message.style.color = "#707070";
          const menuContainer = category.querySelector(".menu__container");
          if (menuContainer) menuContainer.appendChild(message);
        }
      });
  
      if (!hasResults && (searchQuery || vegNonVegValue || subCategoryValue)) {
        menuHeading.textContent = "No Results Found";
        menuHeading.classList.add("no-results");
      } else {
        menuHeading.classList.remove("no-results");
      }
    }
  
    // Event listeners for filters
    searchInput?.addEventListener("input", applyFilters);
    vegNonVegFilter?.addEventListener("change", applyFilters);
    subCategoryFilter?.addEventListener("change", applyFilters);
  
    // Add to Cart event delegation
    if (menuSection) {
      menuSection.addEventListener("click", function (event) {
        const button = event.target.closest(".menu__button");
        if (!button) return;
  
        event.stopImmediatePropagation();
        event.preventDefault();
  
        const menuItem = button.closest(".menu__content");
        if (!menuItem) return console.error("Menu item not found for button.");
  
        const item = {
          itemId: menuItem.getAttribute("data-item-id") || "",
          name: menuItem.getAttribute("data-name"),
          price: menuItem.getAttribute("data-price"),
          image: menuItem.querySelector(".menu__img")?.src || "",
          quantity: 1,
        };
  
        if (!item.name || !item.price) return alert("Error: Cannot add item to cart. Data incomplete.");
  
        const existingItem = cart.find(cartItem => cartItem.name === item.name && cartItem.price === item.price);
        if (existingItem) existingItem.quantity += 1;
        else cart.push(item);
  
        saveCart();
        updateCartCount();
        console.log("Added to cart:", item);
        alert(`${item.name} added to cart!`);
      }, { capture: true });
    }
  
    // // Initialize page
    // fetchMenuItems();
    updateCartCount();
    // applyFilters();
  });