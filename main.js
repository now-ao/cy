/**
 * Main JavaScript file for the Phone Locator application
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Phone number input formatting
    const phoneInput = document.getElementById('phone_number');
    if (phoneInput) {
        phoneInput.addEventListener('input', function(e) {
            // Basic formatting - you could enhance this with a library like libphonenumber-js
            let value = e.target.value.replace(/\D/g, '');
            
            // Add + for international format if it starts with a digit
            if (value.length > 0 && !e.target.value.startsWith('+')) {
                value = '+' + value;
            }
            
            // Don't update if we're deleting from the start
            if (e.inputType !== 'deleteContentBackward' || e.target.value.length > value.length) {
                e.target.value = value;
            }
        });
    }
    
    // Form validation
    const searchForm = document.getElementById('phone-search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(event) {
            const phoneNumber = phoneInput.value.trim();
            
            if (phoneNumber.length < 7) {
                event.preventDefault();
                alert('Please enter a valid phone number with at least 7 digits');
                phoneInput.focus();
            }
        });
    }
    
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert:not(.alert-warning):not(.alert-info)');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
});
