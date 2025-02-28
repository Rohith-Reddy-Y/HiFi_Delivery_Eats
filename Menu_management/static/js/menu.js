
// script.js

document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector("form");
  const tableBody = document.querySelector("table tbody");
/*
   function fetchItemsFromDB() {
    fetch("/get_items")
      .then(response => response.json())
      .then(data => {
        const tableBody = document.querySelector("table tbody");
        tableBody.innerHTML = ""; // Clear previous data

        //! HERE FETCHING DATA FROM DB NEED TO CORRECT THIS FORMATTING.

        data.forEach(item => {
          const newRow = document.createElement("tr");
          newRow.innerHTML = `
            <td>${item.menu_item_id}</td>
            <td>${item.name}</td>
            <td>${item.description}</td>
            <td>${item.price}</td>
            <td>${item.category_id}</td>
            <td>${item.nutrient_value}</td>
            <td>${item.calorie_count}</td>
            <td>${item.discount_percentage}%</td>
            <td><img src="${item.image_url}" alt="${item.name}" width="50"></td>
            <td>${item.is_best_seller ? "Yes" : "No"}</td>
            <td>${item.is_out_of_stock ? "Out of Stock" : "Available"}</td>
          `;
          tableBody.appendChild(newRow);
        });
      })
      .catch(error => console.error("Error fetching items:", error));
  }
  

  fetchItemsFromDB(); */

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
    const stockAvailable = document.querySelector('input[type="number"][min="0"]')
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

    // Prepare form data for the backend
    const formData = new FormData();
    formData.append("item_name", itemName);
    formData.append("description", description);
    formData.append("price", price);
    formData.append("category", category);
    formData.append("subcategory", subcategory);
    formData.append("discount", discount);
    formData.append("image", imageFile);
    formData.append("best_seller", bestSeller);
    formData.append("stock_available", stockAvailable);

    // Send data to the backend
    fetch("/add_item", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
        //   alert("Item added successfully!");
          alert(data.message);

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
            deleteButton.disabled = true;
            editButton.disabled = true;
            showEditPopup(newRow, deleteButton, editButton);
          });

          deleteButton.addEventListener("click", function () {
            editButton.disabled = true;
            showDeleteConfirmation(newRow, editButton);
          });
        } else {
          alert("Error adding item: " + data.message);
        }
      })
      .catch((error) => {
        console.error("Error:", error);
        alert("An error occurred while adding the item.");
      });
  });

  // Function to show edit popup
  function showEditPopup(row, deleteButton, editButton) {
    const cells = row.querySelectorAll("td");
    const itemName = cells[0].textContent.trim();
    const description = cells[1].textContent.trim();
    const price = cells[2].textContent;
    const category = cells[3].textContent;
    const subcategory = cells[4].textContent;
    const discount = cells[5].textContent.replace("%", "");
    const bestSeller = cells[7].textContent;
    const stockAvailable = cells[8].textContent;

    fetch('/get_item_by_name/${itemName}')
    .then(response => response.json())
    .then(data => {
        const {menu_item_id,itemName,description,price,category_name,discount,bestSeller,stockAvailable} = data;
        
        
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

    document.getElementById("save-edit").addEventListener("click", function () {
        const updatedItem = {
            menu_item_id: menu_item_id,
            name: document.getElementById("edit-item-name").value,
            description: document.getElementById("edit-description").value,
            price: document.getElementById("edit-price").value,
            category_name: document.getElementById("edit-category").value,
            discount_percentage: document.getElementById("edit-discount").value,
            is_best_seller: document.querySelector('input[name="edit-best-seller"]:checked').value === "yes",
            is_out_of_stock: document.getElementById("edit-stock-available").value === "0"
        };
        fetch('/update_item',{method: "POST", headers: {"Content-Type":"application/json"},
            body: JSON.stringify(updatedItem),
        }).then(response => response.json())
        .then((data)=>{
            if (data.success) { 
                alert(data.message);
            }
            // Remove the popup
            document.body.removeChild(popup);
            // Re-enable the delete button
            deleteButton.disabled = false;
            // Re-enable the edit button after saving
            editButton.disabled = false;
            location.reload();  // Refresh to reflect updates
        });
    });
    // Handle cancel edit
    document.getElementById("cancel-edit").addEventListener("click", function () {
        // Remove the popup
        document.body.removeChild(popup);
        // Re-enable the delete button
        deleteButton.disabled = false;
        // Re-enable the edit button after canceling
        editButton.disabled = false;
      });
    });
  }


  // Function to show delete confirmation popup
  function showDeleteConfirmation(row, editButton) {
    const itemName = row.cells[0].innerText;

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
      <p>Are you sure you want to delete "${itemName}"?</p>
      <button id="confirm-delete">Yes</button>
      <button id="cancel-delete">No</button>
    `;

    // Append the popup to the body
    document.body.appendChild(popup);

    document.getElementById("confirm-delete").addEventListener("click", function () {
        fetch("/delete_item", {
            method: "DELETE",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ name: itemName })
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert(data.message); // Alert after successful deletion
                row.remove(); // Remove row from UI
                alert("")
            } else {
                alert("Error: " + data.error);
            }
        })
        .catch(error => console.error("Error:", error));

        document.body.removeChild(popup);
        editButton.disabled = false;
    });

    document.getElementById("cancel-delete").addEventListener("click", function () {
        document.body.removeChild(popup);
        editButton.disabled = false;
    });
}

});
