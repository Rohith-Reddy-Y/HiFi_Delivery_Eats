/*==================== SHOW MENU ====================*/
const showMenu = (toggleId, navId) => {
  const toggle = document.getElementById(toggleId),
    nav = document.getElementById(navId);

  if (toggle && nav) {
    toggle.addEventListener("click", () => {
      nav.classList.toggle("show-menu");
    });
  }
};
showMenu("nav-toggle", "nav-menu");

/*==================== REMOVE MENU MOBILE ====================*/
const navLink = document.querySelectorAll(".nav__link");

function linkAction() {
  const navMenu = document.getElementById("nav-menu");
  navMenu.classList.remove("show-menu");
}
navLink.forEach((n) => n.addEventListener("click", linkAction));

/*==================== SCROLL SECTIONS ACTIVE LINK ====================*/
const sections = document.querySelectorAll("section[id]");

function scrollActive() {
  const scrollY = window.pageYOffset;

  sections.forEach((current) => {
    const sectionHeight = current.offsetHeight;
    const sectionTop = current.offsetTop - 50;
    const sectionId = current.getAttribute("id");

    if (scrollY > sectionTop && scrollY <= sectionTop + sectionHeight) {
      document
        .querySelector(".nav__menu a[href*=" + sectionId + "]")
        .classList.add("active-link");
    } else {
      document
        .querySelector(".nav__menu a[href*=" + sectionId + "]")
        .classList.remove("active-link");
    }
  });
}
window.addEventListener("scroll", scrollActive);

/*==================== CHANGE BACKGROUND HEADER ====================*/
function scrollHeader() {
  const nav = document.getElementById("header");
  if (window.scrollY >= 200) nav.classList.add("scroll-header");
  else nav.classList.remove("scroll-header");
}
window.addEventListener("scroll", scrollHeader);

/*==================== SHOW SCROLL TOP ====================*/
function scrollTop() {
  const scrollTop = document.getElementById("scroll-top");
  if (window.scrollY >= 560) scrollTop.classList.add("show-scroll");
  else scrollTop.classList.remove("show-scroll");
}
window.addEventListener("scroll", scrollTop);

/*==================== DARK LIGHT THEME ====================*/
const themeButton = document.getElementById("theme-button");
const darkTheme = "dark-theme";
const iconTheme = "bx-sun";

const selectedTheme = localStorage.getItem("selected-theme");
const selectedIcon = localStorage.getItem("selected-icon");

const getCurrentTheme = () =>
  document.body.classList.contains(darkTheme) ? "dark" : "light";
const getCurrentIcon = () =>
  themeButton.classList.contains(iconTheme) ? "bx-moon" : "bx-sun";

if (selectedTheme) {
  document.body.classList[selectedTheme === "dark" ? "add" : "remove"](darkTheme);
  themeButton.classList[selectedIcon === "bx-moon" ? "add" : "remove"](iconTheme);
}

themeButton.addEventListener("click", () => {
  document.body.classList.toggle(darkTheme);
  themeButton.classList.toggle(iconTheme);
  localStorage.setItem("selected-theme", getCurrentTheme());
  localStorage.setItem("selected-icon", getCurrentIcon());
});

/*==================== SCROLL REVEAL ANIMATION ====================*/
const sr = ScrollReveal({
  origin: "top",
  distance: "30px",
  duration: 2000,
  reset: true,
});

sr.reveal(
  `.home_data, .home_img,
    .about_data, .about_img,
    .services_content, .menu_content,
    .app_data, .app_img,
    .contact_data, .contact_button,
    .footer__content`,
  {
    interval: 200,
  }
);

/*==================== CART FUNCTIONALITY ====================*/

// Function to update the cart counter with total quantity
function updateCartCounter() {
  let cart = JSON.parse(localStorage.getItem("cart")) || [];
  const totalQuantity = cart.reduce((sum, item) => sum + (item.quantity || 1), 0);
  const cartLink = document.querySelector('.nav__link[href="../order/order.html"]');
  if (cartLink) {
    cartLink.textContent = `Cart (${totalQuantity})`;
  }
}

// Add to Cart Functionality using event delegation
if (!window.hasAttachedCartListener) {
  const menuContainer = document.querySelector(".menu__container");
  if (menuContainer) {
    menuContainer.addEventListener("click", (e) => {
      const button = e.target.closest(".menu__button");
      if (button) {
        e.preventDefault(); // Prevent default link behavior
        console.log("Add to Cart button clicked");

        const menuItem = button.closest(".menu__content");
        const imageSrc = menuItem.querySelector(".menu__img").src;
        const relativeImagePath = imageSrc.replace(window.location.origin, "");
        const item = {
          name: menuItem.getAttribute("data-name"),
          price: menuItem.getAttribute("data-price"),
          image: relativeImagePath,
        };

        // Retrieve existing cart or initialize an empty array
        let cart = JSON.parse(localStorage.getItem("cart")) || [];

        // Check if the item already exists in the cart
        const existingItemIndex = cart.findIndex(
          (cartItem) => cartItem.name === item.name && cartItem.price === item.price
        );

        if (existingItemIndex !== -1) {
          // Item exists, increment quantity
          cart[existingItemIndex].quantity = (cart[existingItemIndex].quantity || 1) + 1;
        } else {
          // Item does not exist, add with quantity 1
          item.quantity = 1;
          cart.push(item);
        }

        // Save the updated cart to localStorage
        localStorage.setItem("cart", JSON.stringify(cart));

        alert(`${item.name} added to cart!`);
        updateCartCounter(); // Update the cart counter after adding the item
      }
    });

    // Set the flag to indicate listener has been attached
    window.hasAttachedCartListener = true;
  }
}

// Initialize cart counter on page load
updateCartCounter();