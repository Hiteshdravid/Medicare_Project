
    document.addEventListener('DOMContentLoaded', (event) => {
        const flashPopup = document.querySelector('.flash-popup');
        if (flashPopup) {
            // Show the popup
            flashPopup.classList.add('show');
            // Hide and remove the popup after 5 seconds
            setTimeout(() => {
                flashPopup.classList.remove('show');
                // Add a slight delay before removing the element to allow for the transition
                setTimeout(() => {
                    flashPopup.remove();
                }, 500); 
            }, 5000);
        }
    });