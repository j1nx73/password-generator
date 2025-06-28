// Password Manager JavaScript Utilities

// Global utility functions
const PasswordManager = {
    // Copy text to clipboard with feedback
    copyToClipboard: function(text, button) {
        if (navigator.clipboard && window.isSecureContext) {
            // Use modern clipboard API
            navigator.clipboard.writeText(text).then(() => {
                this.showCopyFeedback(button);
            }).catch(err => {
                console.error('Failed to copy: ', err);
                this.fallbackCopy(text, button);
            });
        } else {
            // Fallback for older browsers
            this.fallbackCopy(text, button);
        }
    },

    // Fallback copy method
    fallbackCopy: function(text, button) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        
        try {
            document.execCommand('copy');
            this.showCopyFeedback(button);
        } catch (err) {
            console.error('Fallback copy failed: ', err);
        }
        
        document.body.removeChild(textArea);
    },

    // Show copy feedback animation
    showCopyFeedback: function(button) {
        const icon = button.querySelector('i');
        if (icon) {
            icon.classList.remove('fa-copy');
            icon.classList.add('fa-check');
        }
        
        button.classList.remove('btn-outline-secondary');
        button.classList.add('btn-success');
        button.classList.add('copy-success');
        
        setTimeout(() => {
            if (icon) {
                icon.classList.remove('fa-check');
                icon.classList.add('fa-copy');
            }
            button.classList.remove('btn-success');
            button.classList.add('btn-outline-secondary');
            button.classList.remove('copy-success');
        }, 2000);
    },

    // Toggle password visibility
    togglePasswordVisibility: function(inputId, button) {
        const input = document.getElementById(inputId);
        const icon = button.querySelector('i');
        
        if (input.type === 'password') {
            input.type = 'text';
            icon.classList.remove('fa-eye');
            icon.classList.add('fa-eye-slash');
        } else {
            input.type = 'password';
            icon.classList.remove('fa-eye-slash');
            icon.classList.add('fa-eye');
        }
    },

    // Generate password strength color
    getStrengthColor: function(strength) {
        switch (strength.toLowerCase()) {
            case 'weak': return 'danger';
            case 'medium': return 'warning';
            case 'strong': return 'info';
            case 'very strong': return 'success';
            default: return 'secondary';
        }
    },

    // Format date for display
    formatDate: function(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    },

    // Show loading spinner
    showLoading: function(button) {
        const originalText = button.innerHTML;
        button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Loading...';
        button.disabled = true;
        return originalText;
    },

    // Hide loading spinner
    hideLoading: function(button, originalText) {
        button.innerHTML = originalText;
        button.disabled = false;
    },

    // Show toast notification
    showToast: function(message, type = 'info') {
        const toastContainer = document.getElementById('toast-container');
        if (!toastContainer) {
            this.createToastContainer();
        }
        
        const toast = this.createToast(message, type);
        document.getElementById('toast-container').appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();
        
        // Remove toast after it's hidden
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    },

    // Create toast container
    createToastContainer: function() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    },

    // Create toast element
    createToast: function(message, type) {
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        return toast;
    },

    // Validate form fields
    validateForm: function(formId) {
        const form = document.getElementById(formId);
        if (!form) return true;
        
        const requiredFields = form.querySelectorAll('[required]');
        let isValid = true;
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                field.classList.add('is-invalid');
                isValid = false;
            } else {
                field.classList.remove('is-invalid');
            }
        });
        
        return isValid;
    },

    // Debounce function for search inputs
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Generate random password (client-side fallback)
    generateRandomPassword: function(length = 16) {
        const charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*';
        let password = '';
        for (let i = 0; i < length; i++) {
            password += charset.charAt(Math.floor(Math.random() * charset.length));
        }
        return password;
    }
};

// Initialize common event listeners when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Add loading states to forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                const originalText = PasswordManager.showLoading(submitBtn);
                submitBtn.dataset.originalText = originalText;
            }
        });
    });

    // Add copy functionality to password fields
    const copyButtons = document.querySelectorAll('[onclick*="copyPassword"]');
    copyButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const input = this.parentElement.querySelector('input');
            if (input) {
                PasswordManager.copyToClipboard(input.value, this);
            }
        });
    });

    // Add password visibility toggle
    const toggleButtons = document.querySelectorAll('[onclick*="togglePasswordVisibility"]');
    toggleButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const inputId = this.getAttribute('onclick').match(/['"]([^'"]+)['"]/)[1];
            PasswordManager.togglePasswordVisibility(inputId, this);
        });
    });
});

// Export for use in other scripts
window.PasswordManager = PasswordManager; 