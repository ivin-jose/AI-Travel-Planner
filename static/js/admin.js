
// admin preloader
window.onload = function() {
    // Hide the preloader when the page is fully loaded
    document.getElementById('adminpreloader').style.display = 'none';
};


// Function to validate the password
function validatePassword() {
    var password = document.getElementById('admin_password').value;

    // Check if the password has at least 6 characters
    if (password.length < 6) {
        alert('Password must be at least 6 characters long.');
        return false;
    }

    // Check if the password contains at least one letter and one number
    if (!/[a-zA-Z]/.test(password) || !/\d/.test(password)) {
        alert('Password must contain at least one letter and one number.');
        return false;
    }

    return true;
}

// Attach the validation function to the form's onsubmit event
document.getElementById('admin_Add_Form').onsubmit = function() {
    return validatePassword();
};



    function validateAdminAddForm() {
  // Get form input values
  var adminName = document.forms["admin_Add_Form"]["admin_name"].value;
  var adminPassword = document.forms["admin_Add_Form"]["admin_password"].value;
  
  // Reset previous error messages
  document.getElementById("nameError").innerHTML = "";
  document.getElementById("passwordError").innerHTML = "";
  
  // Define a flag for validation
  var isValid = true;
  
  // Validate admin name (min 6 characters)
  if (adminName.length < 6) {
    document.getElementById("nameError").innerHTML = "Name must be at least 6 characters";
    isValid = false;
  }
  else if (adminPassword.length < 6) {
    document.getElementById("passwordError").innerHTML = "Password must be at least 6 characters";
    isValid = false;
  }
  
  // You can add more validation checks for admin_password here
  
  // Return the validation result
  return isValid;
}

// Function to clear error messages when the form is submitted
function clear() {
  document.getElementById("nameError").innerHTML = "";
  document.getElementById("passwordError").innerHTML = "";
}


// JavaScript function to toggle the visibility of the close button
function toggleCloseButton(adminId) {
  // Get the elements by their IDs
  var removeLink = document.getElementById("deleteConfirmation_" + adminId);
  var closeButton = document.getElementById("deleteConfirmationclose_" + adminId);
  var ticButton = document.getElementById("deleteConfirmationtic_" + adminId);
  
  // Toggle the visibility of the close button
  closeButton.style.display = (closeButton.style.display === "none") ? "inline-block" : "none";
  ticButton.style.display = (ticButton.style.display === "none") ? "inline-block" : "none";

  // Toggle the visibility of the link and close button
  if (removeLink.style.display === "none") {
    removeLink.style.display = "inline-block";
    closeButton.style.display = "none";
  } else {
    removeLink.style.display = "none";
    closeButton.style.display = "inline-block";
  }
}







