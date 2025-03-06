// Utility function to format timestamp as YYYY-MM-DD HH:mm:ss
// ! TIMESTAMP FORMAT NEED TO CONSIDER.
function formatTimestamp(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
  }
document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("menu-form");
    const tableBody = document.getElementById("menu-table-body");

   function fetchItemsFromDB() {
    fetch("/get_items")
      .then(response => response.json())
      .then(data => {
        const baseUrl = "https://HiFiDeliveryEats.com/";
        const staticImagePath = "/static/images/";
        tableBody.innerHTML = ""; // Clear previous data

        //! HERE FETCHING DATA FROM DB NEED TO CORRECT THIS FORMATTING.
        /*
            <td>${item.menu_item_id}</td>
            <td>${item.nutrient_value}</td>
            <td>${item.calorie_count}</td>
        */
        data.forEach(item => {
          const newRow = document.createElement("tr");
          newRow.innerHTML = `
            <td>${item.menu_item_id}</td>
            <td>${item.name}</td>
            <td>${item.description}</td>
            <td>${item.price}</td>
            <td>${item.category_name}</td>
            <td>${item.subcategory_name}</td>
            <td>${item.discount_percentage}%</td>
            <td><img src="${staticImagePath}${item.image_url.replace(baseUrl, '')}" alt="${item.name}" width="50"></td>
            <td>${item.is_best_seller ? "Yes" : "No"}</td>
            <td>${item.is_out_of_stock ? "Out of Stock" : "Available"}</td>
            <td></td>
            <td>
              <div class="action-buttons">
                <button class="edit-btn">Edit</button>
                <button class="delete-btn">Delete</button>
              </div>
            </td>
          `;
          tableBody.appendChild(newRow);
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
        });
      })
      .catch(error => console.error("Error fetching items:", error));
  }
  

  fetchItemsFromDB(); 
  
//   for showing the notification to the admin that something has changed
function showNotification(message, type) {
    const notification = document.createElement("div");
    notification.className = `notification ${type} show`;
    notification.innerText = message;
  
    document.body.appendChild(notification);
  
    setTimeout(() => {
      notification.remove();
    }, 5000);
  }

  // Add event listener for form submission
  form.addEventListener("submit", function (event) {
    event.preventDefault(); // Prevent the form from submitting

    // Get form values
    const itemName = document.getElementById("item-name").value.trim();
    const description = document.getElementById("description").value.trim();
    const price = document.getElementById("price").value.trim();
    const category = document.getElementById("category").value;
    const subcategory = document.getElementById("subcategory").value;
    const discount = document.getElementById("discount").value.trim() || "0";
    const imageFile = document.getElementById("image").files[0];
    const bestSeller = document.querySelector('input[name="best_seller"]:checked')?.value || "no";
    const stockAvailable = document.getElementById("stock-available").value.trim();

    // Validate required fields
    if (!itemName || !description || !price || !category || !subcategory || !bestSeller || !stockAvailable || !imageFile){ 
        showNotification("⚠️ Please fill out all required fields and upload an image.", "error");
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
        // alert(data);
        if (data.success) {
        //   alert("Item added successfully!");
        showNotification("✅ Item added successfully!", "success");

          // Create a new row in the table
          const newRow = document.createElement("tr");
          const staticImagePath = "/static/images/";

          // Add cells to the row
          newRow.innerHTML = `
            <td>${data.menu_item_id}</td>
            <td>${itemName}</td>
            <td>${description}</td>
            <td>${price}</td>
            <td>${category}</td>
            <td>${subcategory}</td>
            <td>${discount}%</td>
            <td><img src="${staticImagePath}${data.image_url ? data.image_url.split('/').pop() : ''}" alt="${itemName}" width="50"></td>
            <td>${bestSeller}</td>
            <td>${stockAvailable}</td>
            <td></td>
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
        //   alert("Error adding item: " + data.message);
            showNotification(`❌ Error: ${data.message}`, "error");
        }
      })
      .catch((error) => {
        console.log(data);
        console.error("Error:", error);
        // showNotification("Error: " + error, "error");
        // alert("An error occurred while adding the item.");
        showNotification("⚠️ An unexpected error occurred.", "error");
      });
  });

  // Function to show edit popup
function showEditPopup(row, deleteButton, editButton) {
    const cells = row.querySelectorAll("td");
    const ORINGINAL_NAME = cells[1].textContent.trim();

    fetch(`/get_item_by_name/${ORINGINAL_NAME}`)
    .then(response => response.json())
    .then(data => {
        console.log("Fetched Data:", data);  // Debugging

        if (data.error) {
            alert("Error: " + data.error);
            return;
        }

        const MI = data.menu_item_id;
        const itemName = data.name;
        const description = data.description;
        const price = data.price;
        const category = data.category_name;
        const subcategory = data.subcategory_name;  // 🔹 Updated
        const discount = data.discount_percentage || 0;
        const bestSeller = data.is_best_seller ? "yes" : "no";
        const stockAvailable = data.is_out_of_stock ? "0" : "1";

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
            <option value="Veg" ${category === "Veg" ? "selected" : ""}>VEG</option>
            <option value="Non-Veg" ${category === "Non-Veg" ? "selected" : ""}>NON-VEG</option>
          </select><br><br>
          <label>Subcategory:</label>
          <select id="edit-subcategory" required>
            <option value="Starter" ${subcategory === "Starter" ? "selected" : ""}>Starter</option>
            <option value="Soups" ${subcategory === "Soups" ? "selected" : ""}>Soups</option>
            <option value="Salads" ${subcategory === "Salads" ? "selected" : ""}>Salads</option>
            <option value="Breads" ${subcategory === "Breads" ? "selected" : ""}>Breads</option>
            <option value="Main Course" ${subcategory === "Main Course" ? "selected" : ""}>Main Course</option>
            <option value="Beverages" ${subcategory === "Beverages" ? "selected" : ""}>Beverages</option>
            <option value="Breakfast" ${subcategory === "Breakfast" ? "selected" : ""}>Breakfast</option>
            <option value="Biryani" ${subcategory === "Biryani" ? "selected" : ""}>Biryani</option>
            <option value="Icecreams" ${subcategory === "Icecreams" ? "selected" : ""}>Icecreams</option>
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
                menu_item_id: MI,
                name: document.getElementById("edit-item-name").value,
                description: document.getElementById("edit-description").value,
                price: document.getElementById("edit-price").value ? parseFloat(document.getElementById("edit-price").value) : 0.0,
                category_name: document.getElementById("edit-category").value,
                subcategory_name: document.getElementById("edit-subcategory").value,  // 🔹 Added
                discount_percentage: document.getElementById("edit-discount").value ? parseFloat(document.getElementById("edit-discount").value) : 0.0,
                is_best_seller: document.querySelector('input[name="edit-best-seller"]:checked').value === "yes",
                is_out_of_stock: parseInt(document.getElementById("edit-stock-available").value) === 0  // 🔹 Ensure boolean logic
            };

            fetch('/update_item', {
                method: "POST",
                headers: {"Content-Type":"application/json"},
                body: JSON.stringify(updatedItem),
            }).then(response => response.json())
            .then((data) => {
                // alert('Updated item successfully')
                showNotification(`Item ${MI}  Updated successfully!`, "success");
                // Delay reload to let the notification be visible
                setTimeout(() => {
                    location.reload();
                }, 5000); // Reload after 2 seconds (adjust timing as needed)
                document.body.removeChild(popup);
                deleteButton.disabled = false;
                editButton.disabled = false;
            });
        });

        document.getElementById("cancel-edit").addEventListener("click", function () {
            document.body.removeChild(popup);
            deleteButton.disabled = false;
            editButton.disabled = false;
        });

    })
    .catch(error => {
        console.error("Error fetching item:", error);
        alert("Failed to fetch item details. Please try again.");
    });
}


  // Function to show delete confirmation popup
  function showDeleteConfirmation(row, editButton) {
    const itemName = row.cells[1].innerText;

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
                // alert(data.message); // Alert after successful deletion
                showNotification("Item Deleted successfully!", "success");
                row.remove(); // Remove row from UI
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
