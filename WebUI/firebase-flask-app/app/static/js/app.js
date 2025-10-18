// Firebase Flask App - Main JavaScript file

// Global app object
const App = {
    // Configuration
    config: {
        apiBaseUrl: '/api',
        refreshInterval: 30000 // 30 seconds
    },
    
    // Initialize the app
    init: function() {
        console.log('Firebase Flask App initialized');
        this.setupEventListeners();
    },
    
    // Setup event listeners
    setupEventListeners: function() {
        // Add any global event listeners here
        document.addEventListener('DOMContentLoaded', () => {
            console.log('DOM loaded');
        });
    },
    
    // Utility functions
    utils: {
        // Show loading spinner
        showLoading: function(elementId) {
            const element = document.getElementById(elementId);
            if (element) {
                element.style.display = 'block';
            }
        },
        
        // Hide loading spinner
        hideLoading: function(elementId) {
            const element = document.getElementById(elementId);
            if (element) {
                element.style.display = 'none';
            }
        },
        
        // Show error message
        showError: function(message, containerId = 'error-container') {
            const container = document.getElementById(containerId);
            if (container) {
                container.innerHTML = `
                    <div class="alert alert-danger alert-dismissible fade show" role="alert">
                        ${message}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                `;
            }
        },
        
        // Show success message
        showSuccess: function(message, containerId = 'success-container') {
            const container = document.getElementById(containerId);
            if (container) {
                container.innerHTML = `
                    <div class="alert alert-success alert-dismissible fade show" role="alert">
                        ${message}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                `;
            }
        },
        
        // Format currency
        formatCurrency: function(amount) {
            return new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'USD'
            }).format(amount);
        },
        
        // Format date
        formatDate: function(dateString) {
            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        }
    },
    
    // API functions
    api: {
        // Generic API call function
        call: async function(endpoint, options = {}) {
            const url = `${App.config.apiBaseUrl}${endpoint}`;
            const defaultOptions = {
                headers: {
                    'Content-Type': 'application/json',
                }
            };
            
            const finalOptions = { ...defaultOptions, ...options };
            
            try {
                const response = await fetch(url, finalOptions);
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || `HTTP error! status: ${response.status}`);
                }
                
                return data;
            } catch (error) {
                console.error('API call failed:', error);
                throw error;
            }
        },
        
        // Get products
        getProducts: function() {
            return this.call('/products');
        },
        
        // Create product
        createProduct: function(productData) {
            return this.call('/products', {
                method: 'POST',
                body: JSON.stringify(productData)
            });
        },
        
        // Update product
        updateProduct: function(productId, productData) {
            return this.call(`/products/${productId}`, {
                method: 'PUT',
                body: JSON.stringify(productData)
            });
        },
        
        // Delete product
        deleteProduct: function(productId) {
            return this.call(`/products/${productId}`, {
                method: 'DELETE'
            });
        }
    }
};

// Initialize the app when the script loads
App.init();

// Export for use in other scripts
window.App = App;
