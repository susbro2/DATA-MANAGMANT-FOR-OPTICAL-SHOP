// API URL - Now works in both development and Electron environments
const API_URL = 'http://localhost:3000/api';

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Set default date to today
    document.getElementById('date').valueAsDate = new Date();
    
    // Load saved customers from server
    loadCustomersList();
    
    // Add event listeners to buttons
    document.getElementById('saveButton').addEventListener('click', saveCustomer);
    document.getElementById('clearButton').addEventListener('click', clearForm);
    document.getElementById('searchButton').addEventListener('click', searchCustomers);
    
    // Add event listeners for cost calculation
    document.getElementById('frameCost').addEventListener('input', calculateTotal);
    document.getElementById('lensCost').addEventListener('input', calculateTotal);
});

// Function to calculate total cost
function calculateTotal() {
    const frameCost = parseFloat(document.getElementById('frameCost').value) || 0;
    const lensCost = parseFloat(document.getElementById('lensCost').value) || 0;
    
    const totalCost = frameCost + lensCost;
    document.getElementById('totalCost').value = totalCost.toFixed(2);
}

// Function to save customer data
async function saveCustomer() {
    // Get all form values
    const customerData = {
        name: document.getElementById('customerName').value,
        phone: document.getElementById('phoneNumber').value,
        date: document.getElementById('date').value,
        prescription: {
            rightSph: document.getElementById('rightSph').value,
            rightCyl: document.getElementById('rightCyl').value,
            rightAxe: document.getElementById('rightAxe').value,
            rightAdd: document.getElementById('rightAdd').value,
            leftSph: document.getElementById('leftSph').value,
            leftCyl: document.getElementById('leftCyl').value,
            leftAxe: document.getElementById('leftAxe').value,
            leftAdd: document.getElementById('leftAdd').value
        },
        frameName: document.getElementById('frameName').value,
        lensName: document.getElementById('lensName').value,
        frameCost: parseFloat(document.getElementById('frameCost').value) || 0,
        lensCost: parseFloat(document.getElementById('lensCost').value) || 0,
        totalCost: parseFloat(document.getElementById('totalCost').value) || 0
    };
    
    // Validate required fields
    if (!customerData.name) {
        alert('Please enter the customer name');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/customers`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(customerData)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to save customer');
        }
        
        const result = await response.json();
        
        // Refresh the customers list
        loadCustomersList();
        
        // Clear the form
        clearForm();
        
        alert('Customer data saved successfully!');
    } catch (error) {
        alert(`Error: ${error.message}`);
        console.error('Error saving customer:', error);
    }
}

// Function to load and display customers list
async function loadCustomersList() {
    const customerList = document.getElementById('customerList');
    customerList.innerHTML = '<p>Loading customers...</p>';
    
    try {
        const response = await fetch(`${API_URL}/customers`);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to load customers');
        }
        
        const customers = await response.json();
        
        customerList.innerHTML = '';
        
        if (customers.length === 0) {
            customerList.innerHTML = '<p>No customers found.</p>';
            return;
        }
        
        // Create customer cards
        customers.forEach(customer => {
            const customerCard = document.createElement('div');
            customerCard.className = 'customer-card';
            customerCard.setAttribute('data-id', customer.id);
            
            customerCard.innerHTML = `
                <h4>${customer.name}</h4>
                <p>Phone: ${customer.phone || 'N/A'}</p>
                <p>Date: ${formatDate(customer.date)}</p>
                <p>Frame: ${customer.frame_name || 'N/A'}</p>
                <p>Total Cost: ₹${customer.total_cost || '0'}</p>
            `;
            
            // Add click event to load customer details when clicked
            customerCard.addEventListener('click', () => loadCustomerDetails(customer.id));
            
            customerList.appendChild(customerCard);
        });
    } catch (error) {
        customerList.innerHTML = `<p>Error loading customers: ${error.message}</p>`;
        console.error('Error loading customers:', error);
    }
}

// Function to load customer details into the form
async function loadCustomerDetails(customerId) {
    try {
        const response = await fetch(`${API_URL}/customers/${customerId}`);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to load customer details');
        }
        
        const customer = await response.json();
        
        // Fill the form with customer data
        document.getElementById('date').value = customer.date || '';
        document.getElementById('customerName').value = customer.name || '';
        document.getElementById('phoneNumber').value = customer.phone || '';
        
        // Prescription
        const prescription = customer.prescription || {};
        document.getElementById('rightSph').value = prescription.right_sph || '';
        document.getElementById('rightCyl').value = prescription.right_cyl || '';
        document.getElementById('rightAxe').value = prescription.right_axe || '';
        document.getElementById('rightAdd').value = prescription.right_add || '';
        
        document.getElementById('leftSph').value = prescription.left_sph || '';
        document.getElementById('leftCyl').value = prescription.left_cyl || '';
        document.getElementById('leftAxe').value = prescription.left_axe || '';
        document.getElementById('leftAdd').value = prescription.left_add || '';
        
        // Product details
        const product = customer.product || {};
        document.getElementById('frameName').value = product.frame_name || '';
        document.getElementById('lensName').value = product.lens_name || '';
        
        // Costs
        document.getElementById('frameCost').value = product.frame_cost || '';
        document.getElementById('lensCost').value = product.lens_cost || '';
        document.getElementById('totalCost').value = product.total_cost || '';
        
        // Change the save button to update
        const saveButton = document.getElementById('saveButton');
        saveButton.textContent = 'Update Customer';
        saveButton.setAttribute('data-mode', 'update');
        saveButton.setAttribute('data-id', customerId);
        
        // Change the event listener
        saveButton.removeEventListener('click', saveCustomer);
        saveButton.addEventListener('click', () => updateCustomer(customerId));
    } catch (error) {
        alert(`Error: ${error.message}`);
        console.error('Error loading customer details:', error);
    }
}

// Function to update an existing customer
async function updateCustomer(customerId) {
    // Get updated form values
    const customerData = {
        name: document.getElementById('customerName').value,
        phone: document.getElementById('phoneNumber').value,
        date: document.getElementById('date').value,
        prescription: {
            rightSph: document.getElementById('rightSph').value,
            rightCyl: document.getElementById('rightCyl').value,
            rightAxe: document.getElementById('rightAxe').value,
            rightAdd: document.getElementById('rightAdd').value,
            leftSph: document.getElementById('leftSph').value,
            leftCyl: document.getElementById('leftCyl').value,
            leftAxe: document.getElementById('leftAxe').value,
            leftAdd: document.getElementById('leftAdd').value
        },
        frameName: document.getElementById('frameName').value,
        lensName: document.getElementById('lensName').value,
        frameCost: parseFloat(document.getElementById('frameCost').value) || 0,
        lensCost: parseFloat(document.getElementById('lensCost').value) || 0,
        totalCost: parseFloat(document.getElementById('totalCost').value) || 0
    };
    
    // Validate required fields
    if (!customerData.name) {
        alert('Please enter the customer name');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/customers/${customerId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(customerData)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to update customer');
        }
        
        // Refresh the customers list
        loadCustomersList();
        
        // Clear the form and reset the save button
        clearForm();
        
        alert('Customer data updated successfully!');
    } catch (error) {
        alert(`Error: ${error.message}`);
        console.error('Error updating customer:', error);
    }
}

// Function to search customers
async function searchCustomers() {
    const searchTerm = document.getElementById('searchInput').value.trim();
    const customerList = document.getElementById('customerList');
    
    customerList.innerHTML = '<p>Searching...</p>';
    
    try {
        let url = `${API_URL}/customers`;
        if (searchTerm) {
            url = `${API_URL}/search?term=${encodeURIComponent(searchTerm)}`;
        }
        
        const response = await fetch(url);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to search customers');
        }
        
        const customers = await response.json();
        
        customerList.innerHTML = '';
        
        if (customers.length === 0) {
            customerList.innerHTML = '<p>No matching customers found.</p>';
            return;
        }
        
        // Create customer cards for search results
        customers.forEach(customer => {
            const customerCard = document.createElement('div');
            customerCard.className = 'customer-card';
            customerCard.setAttribute('data-id', customer.id);
            
            customerCard.innerHTML = `
                <h4>${customer.name}</h4>
                <p>Phone: ${customer.phone || 'N/A'}</p>
                <p>Date: ${formatDate(customer.date)}</p>
                <p>Frame: ${customer.frame_name || 'N/A'}</p>
                <p>Total Cost: ₹${customer.total_cost || '0'}</p>
            `;
            
            // Add click event to load customer details when clicked
            customerCard.addEventListener('click', () => loadCustomerDetails(customer.id));
            
            customerList.appendChild(customerCard);
        });
    } catch (error) {
        customerList.innerHTML = `<p>Error searching customers: ${error.message}</p>`;
        console.error('Error searching customers:', error);
    }
}

// Function to clear the form
function clearForm() {
    // Reset all inputs
    document.getElementById('date').valueAsDate = new Date();
    document.getElementById('customerName').value = '';
    document.getElementById('phoneNumber').value = '';
    
    document.getElementById('rightSph').value = '';
    document.getElementById('rightCyl').value = '';
    document.getElementById('rightAxe').value = '';
    document.getElementById('rightAdd').value = '';
    
    document.getElementById('leftSph').value = '';
    document.getElementById('leftCyl').value = '';
    document.getElementById('leftAxe').value = '';
    document.getElementById('leftAdd').value = '';
    
    document.getElementById('frameName').value = '';
    document.getElementById('lensName').value = '';
    
    document.getElementById('frameCost').value = '';
    document.getElementById('lensCost').value = '';
    document.getElementById('totalCost').value = '';
    
    // Reset save button
    const saveButton = document.getElementById('saveButton');
    saveButton.textContent = 'Save Customer';
    saveButton.removeAttribute('data-mode');
    saveButton.removeAttribute('data-id');
    
    // Reset event listener
    saveButton.removeEventListener('click', updateCustomer);
    saveButton.addEventListener('click', saveCustomer);
}

// Helper function to format date in a readable format
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString();
} 