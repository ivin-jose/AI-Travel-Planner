// NAVBAR TOGGLE

document.addEventListener('DOMContentLoaded', function() {
	const hamburger = document.querySelector(".hamburger");
	const navLinks = document.querySelector(".nav-links");
	const links = document.querySelectorAll(".nav-links li");

	hamburger.addEventListener('click', () => {
        // Animate Links
		navLinks.classList.toggle("open");
		links.forEach(link => {
			link.classList.toggle("");
		});

        // Hamburger Animation
		hamburger.classList.toggle("toggle");
	});
});


function closeAlert() {
    // Find the alert box element by its ID
    var alertBox = document.getElementById('msg-alert-box');

    // Check if the alert box element exists
    if (alertBox) {
        // Hide the alert box by adding the "d-none" class
        alertBox.classList.add('d-none');
    }
}




