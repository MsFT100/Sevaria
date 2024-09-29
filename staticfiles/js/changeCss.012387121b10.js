document.addEventListener('DOMContentLoaded', function() {
    // Get the main element
    var mainElement = document.querySelector('main.container-full');

    // Check if we're on the home page
    var isHomePage = window.location.pathname === '/';

    // Swap CSS classes based on the current page
    if (isHomePage) {
        mainElement.classList.add('home-page');
        mainElement.classList.remove('other-page');
    } else {
        mainElement.classList.add('other-page');
        mainElement.classList.remove('home-page');
    }
});