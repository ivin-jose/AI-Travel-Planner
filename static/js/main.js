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



