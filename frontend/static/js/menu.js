
// script.js

document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector("form");
  const tableBody = document.querySelector("table tbody");

  // Add event listener for form submission
  form.addEventListener("submit", function (event) {
    event.preventDefault(); // Prevent the form from submitting

    // Get form values
    const itemName = document.querySelector('input[type="text"]').value.trim();
    const description = document.querySelector("textarea").value.trim();
    const price = document
      .querySelector('input[type="number"][step="0.01"]')
      .value.trim();
    const category = document.querySelector("select").value;
    const subcategory = document.querySelectorAll("select")[1].value;
    const discount =
      document
        .querySelector('input[type="number"][min="0"][max="100"]')
        .value.trim() || 0; // Default to 0 if empty
    const imageFile = document.querySelector('input[type="file"]').files[0];
    const bestSeller = document.querySelector(
      'input[name="best_seller"]:checked'
    )?.value;
    const stockAvailable = document
      .querySelector('input[type="number"][min="0"]')
      .value.trim();

    // Validate required fields
    if (
      !itemName ||
      !description ||
      !price ||
      !category ||
      !subcategory ||
      !bestSeller ||
      !stockAvailable ||
      !imageFile // Ensure an image is uploaded
    ) {
      alert("Please fill out all required fields and upload an image.");
      return;
    }

    // Create a new row in the table
    const newRow = document.createElement("tr");

    // Add cells to the row
    newRow.innerHTML = `
      <td>${itemName}</td>
      <td>${description}</td>
      <td>${price}</td>
      <td>${category}</td>
      <td>${subcategory}</td>
      <td>${discount}%</td>
      <td><img src="${URL.createObjectURL(
        imageFile
      )}" alt="${itemName}" width="50"></td>
      <td>${bestSeller}</td>
      <td>${stockAvailable}</td>
      <td>
        <div class="action-buttons">
          <button class="edit-btn">Edit</button>
          <button class="delete-btn">Delete</button>
        </div>
      </td>
    `;

    // Append the new row to the table
    tableBody.appendChild(newRow);

    // Clear the form
    form.reset();

    // Add event listeners to the edit and delete buttons
    const editButton = newRow.querySelector(".edit-btn");
    const deleteButton = newRow.querySelector(".delete-btn");

    editButton.addEventListener("click", function () {
      // Disable the delete button while editing
      deleteButton.disabled = true;
      // Disable the edit button while editing
      editButton.disabled = true;
      showEditPopup(newRow, deleteButton, editButton);
    });

    deleteButton.addEventListener("click", function () {
      // Disable the edit button while deleting
      editButton.disabled = true;
      showDeleteConfirmation(newRow, editButton);
    });
  });

  // Function to show edit popup
  function showEditPopup(row, deleteButton, editButton) {
    const cells = row.querySelectorAll("td");
    const itemName = cells[0].textContent;
    const description = cells[1].textContent;
    const price = cells[2].textContent;
    const category = cells[3].textContent;
    const subcategory = cells[4].textContent;
    const discount = cells[5].textContent.replace("%", "");
    const bestSeller = cells[7].textContent;
    const stockAvailable = cells[8].textContent;

    // Create a popup for editing
    const popup = document.createElement("div");
    popup.style.position = "fixed";
    popup.style.top = "50%";
    popup.style.left = "50%";
    popup.style.transform = "translate(-50%, -50%)";
    popup.style.backgroundColor = "#FFFFFF";
    popup.style.color = "#000000";
    popup.style.padding = "20px";
    popup.style.borderRadius = "8px";
    popup.style.boxShadow = "0 0 10px rgba(0, 0, 0, 0.1)";
    popup.style.zIndex = "1000";
    popup.style.textAlign = "center";
    popup.style.maxHeight = "80vh"; // Set max height for the popup
    popup.style.overflowY = "auto"; // Add scrollbar if content overflows

    popup.innerHTML = `
      <h3>Edit Item</h3>
      <label>Item Name:</label>
      <input type="text" id="edit-item-name" value="${itemName}" required><br><br>
      <label>Description:</label>
      <textarea id="edit-description" required>${description}</textarea><br><br>
      <label>Price:</label>
      <input type="number" id="edit-price" step="0.01" value="${price}" required><br><br>
      <label>Category:</label>
      <select id="edit-category" required>
        <option value="veg" ${category === "veg" ? "selected" : ""}>VEG</option>
        <option value="non-veg" ${
          category === "non-veg" ? "selected" : ""
        }>NON-VEG</option>
      </select><br><br>
      <label>Subcategory:</label>
      <select id="edit-subcategory" required>
        <option value="Starter" ${
          subcategory === "Starter" ? "selected" : ""
        }>Starter</option>
        <option value="Soups" ${
          subcategory === "Soups" ? "selected" : ""
        }>Soups</option>
        <option value="Salads" ${
          subcategory === "Salads" ? "selected" : ""
        }>Salads</option>
        <option value="Breads" ${
          subcategory === "Breads" ? "selected" : ""
        }>Breads</option>
        <option value="Main Course" ${
          subcategory === "Main Course" ? "selected" : ""
        }>Main Course</option>
        <option value="Beverages" ${
          subcategory === "Beverages" ? "selected" : ""
        }>Beverages</option>
        <option value="Breakfast" ${
          subcategory === "Breakfast" ? "selected" : ""
        }>Breakfast</option>
        <option value="Bryani" ${
          subcategory === "Bryani" ? "selected" : ""
        }>Bryani</option>
        <option value="Icecreams" ${
          subcategory === "Icecreams" ? "selected" : ""
        }>Icecreams</option>
      </select><br><br>
      <label>Discount (%):</label>
      <input type="number" id="edit-discount" min="0" max="100" value="${discount}"><br><br>
      <label>Best Seller:</label>
      <input type="radio" id="edit-best-seller-yes" name="edit-best-seller" value="yes" ${
        bestSeller === "yes" ? "checked" : ""
      }> Yes
      <input type="radio" id="edit-best-seller-no" name="edit-best-seller" value="no" ${
        bestSeller === "no" ? "checked" : ""
      }> No<br><br>
      <label>Stock Available:</label>
      <input type="number" id="edit-stock-available" min="0" value="${stockAvailable}" required><br><br>
      <button id="save-edit">Save</button>
      <button id="cancel-edit">Cancel</button>
    `;

    // Append the popup to the body
    document.body.appendChild(popup);

    // Handle save edit
    document.getElementById("save-edit").addEventListener("click", function () {
      // Update the row with new values
      cells[0].textContent = document.getElementById("edit-item-name").value;
      cells[1].textContent = document.getElementById("edit-description").value;
      cells[2].textContent = document.getElementById("edit-price").value;
      cells[3].textContent = document.getElementById("edit-category").value;
      cells[4].textContent = document.getElementById("edit-subcategory").value;
      cells[5].textContent = `${
        document.getElementById("edit-discount").value
      }%`;
      cells[7].textContent = document.querySelector(
        'input[name="edit-best-seller"]:checked'
      ).value;
      cells[8].textContent = document.getElementById(
        "edit-stock-available"
      ).value;

      // Remove the popup
      document.body.removeChild(popup);

      // Re-enable the delete button
      deleteButton.disabled = false;
      // Re-enable the edit button after saving
      editButton.disabled = false;
    });

    // Handle cancel edit
    document
      .getElementById("cancel-edit")
      .addEventListener("click", function () {
        // Remove the popup
        document.body.removeChild(popup);

        // Re-enable the delete button
        deleteButton.disabled = false;
        // Re-enable the edit button after canceling
        editButton.disabled = false;
      });
  }

  // Function to show delete confirmation popup
  function showDeleteConfirmation(row, editButton) {
    const popup = document.createElement("div");
    popup.style.position = "fixed";
    popup.style.top = "50%";
    popup.style.left = "50%";
    popup.style.transform = "translate(-50%, -50%)";
    popup.style.backgroundColor = "#FC8019"; // Swiggy orange
    popup.style.color = "#FFFFFF"; // White text
    popup.style.padding = "20px";
    popup.style.borderRadius = "8px";
    popup.style.boxShadow = "0 0 10px rgba(0, 0, 0, 0.1)";
    popup.style.zIndex = "1000";
    popup.style.textAlign = "center";

    popup.innerHTML = `
      <p>Are you sure you want to delete this item?</p>
      <button id="confirm-delete">Yes</button>
      <button id="cancel-delete">No</button>
    `;

    // Append the popup to the body
    document.body.appendChild(popup);

    // Handle confirm delete
    document
      .getElementById("confirm-delete")
      .addEventListener("click", function () {
        row.remove(); // Remove the row
        document.body.removeChild(popup); // Remove the popup

        // Re-enable the edit button
        editButton.disabled = false;
      });

    // Handle cancel delete
    document
      .getElementById("cancel-delete")
      .addEventListener("click", function () {
        document.body.removeChild(popup); // Remove the popup

        // Re-enable the edit button
        editButton.disabled = false;
      });
  }
});
