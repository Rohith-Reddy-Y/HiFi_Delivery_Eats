// Add functionality to the close buttons in the Customer Order section
document.querySelectorAll('.close-button').forEach(button => {
    button.addEventListener('click', () => {
        button.parentElement.parentElement.remove();
    });
});

// Add functionality to the status buttons (optional, for demo purposes)
document.querySelectorAll('.status-button').forEach(button => {
    button.addEventListener('click', () => {
        alert('Status button clicked!');
    });
});