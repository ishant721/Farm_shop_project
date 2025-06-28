// apps/users/static/users/js/password_toggle.js

function togglePasswordVisibility(fieldId) {
    const passwordField = document.getElementById(fieldId);
    // Find the toggle icon specifically related to this input
    // It's safer to find it by its class within the same parent or a specific structure
    const toggleIcon = passwordField.parentElement.querySelector('.password-toggle-icon');

    if (passwordField && toggleIcon) {
        if (passwordField.type === "password") {
            passwordField.type = "text";
            toggleIcon.querySelector('i').classList.remove("fa-eye");
            toggleIcon.querySelector('i').classList.add("fa-eye-slash");
        } else {
            passwordField.type = "password";
            toggleIcon.querySelector('i').classList.remove("fa-eye-slash");
            toggleIcon.querySelector('i').classList.add("fa-eye");
        }
    }
}

// Initial setup to ensure only fields not marked with data-password-toggle="false" get the icon
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('input[type="password"]').forEach(input => {
        // Only apply if the input doesn't explicitly opt out of the toggle
        if (input.dataset.passwordToggle !== 'false') {
            // Ensure the input has an ID for the toggle function
            if (!input.id) {
                input.id = 'password_field_' + Math.random().toString(36).substr(2, 9);
            }

            let wrapper = input.parentElement;
            // If the parent is not already 'position-relative', create a new wrapper
            if (!wrapper || !wrapper.classList.contains('position-relative')) {
                const newWrapper = document.createElement('div');
                newWrapper.classList.add('position-relative');
                // Check if the input itself has mb-3, if not, add it to the wrapper
                if (!input.classList.contains('mb-3')) {
                    newWrapper.classList.add('mb-3');
                }
                input.parentNode.insertBefore(newWrapper, input);
                newWrapper.appendChild(input);
                wrapper = newWrapper;
            }

            // Check if an icon already exists to prevent duplicates
            if (!wrapper.querySelector('.password-toggle-icon')) {
                const toggleSpan = document.createElement('span');
                toggleSpan.classList.add('password-toggle-icon');
                toggleSpan.setAttribute('onclick', `togglePasswordVisibility('${input.id}')`);
                const icon = document.createElement('i');
                icon.classList.add('fas', 'fa-eye'); // Default eye icon
                toggleSpan.appendChild(icon);
                wrapper.appendChild(toggleSpan);
            }
        }
    });
});