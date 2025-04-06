const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

// Try to load electron in a way that works in both packaged and development environments
let electronApp = null;
try {
    const electron = require('electron');
    electronApp = electron.app || (electron.remote && electron.remote.app);
} catch (e) {
    // Not running in Electron environment
    console.log('Not running in Electron environment');
}

// Initialize express app
const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, '.')));

// Get the proper path for the database file
function getDatabasePath() {
    let dbPath = './optical_shop.db';
    
    // If running in Electron (packaged app)
    if (electronApp) {
        const userDataPath = electronApp.getPath('userData');
        dbPath = path.join(userDataPath, 'optical_shop.db');
        
        // Ensure the directory exists
        if (!fs.existsSync(userDataPath)) {
            fs.mkdirSync(userDataPath, { recursive: true });
        }
        
        console.log('Using database at:', dbPath);
    } else {
        console.log('Running in development mode, using local database');
    }
    
    return dbPath;
}

// Connect to SQLite database
const db = new sqlite3.Database(getDatabasePath(), (err) => {
    if (err) {
        console.error('Error connecting to database:', err.message);
    } else {
        console.log('Connected to the optical shop database.');
        createTables();
    }
});

// Create database tables if they don't exist
function createTables() {
    // Customers table
    db.run(`CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        date TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )`);

    // Prescriptions table
    db.run(`CREATE TABLE IF NOT EXISTS prescriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        right_sph TEXT,
        right_cyl TEXT,
        right_axe TEXT,
        right_add TEXT,
        left_sph TEXT,
        left_cyl TEXT,
        left_axe TEXT,
        left_add TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers (id) ON DELETE CASCADE
    )`);

    // Products table
    db.run(`CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        frame_name TEXT,
        lens_name TEXT,
        frame_cost REAL,
        lens_cost REAL,
        total_cost REAL,
        FOREIGN KEY (customer_id) REFERENCES customers (id) ON DELETE CASCADE
    )`);
}

// API Routes

// Get all customers
app.get('/api/customers', (req, res) => {
    const query = `
        SELECT c.*, p.frame_name, p.lens_name, p.total_cost 
        FROM customers c
        LEFT JOIN products p ON c.id = p.customer_id
        ORDER BY c.date DESC
    `;
    
    db.all(query, [], (err, rows) => {
        if (err) {
            res.status(500).json({ error: err.message });
            return;
        }
        res.json(rows);
    });
});

// Get customer by ID with prescription and product details
app.get('/api/customers/:id', (req, res) => {
    const id = req.params.id;
    
    db.get('SELECT * FROM customers WHERE id = ?', [id], (err, customer) => {
        if (err) {
            res.status(500).json({ error: err.message });
            return;
        }
        
        if (!customer) {
            res.status(404).json({ error: 'Customer not found' });
            return;
        }
        
        db.get('SELECT * FROM prescriptions WHERE customer_id = ?', [id], (err, prescription) => {
            if (err) {
                res.status(500).json({ error: err.message });
                return;
            }
            
            db.get('SELECT * FROM products WHERE customer_id = ?', [id], (err, product) => {
                if (err) {
                    res.status(500).json({ error: err.message });
                    return;
                }
                
                res.json({
                    ...customer,
                    prescription: prescription || {},
                    product: product || {}
                });
            });
        });
    });
});

// Add new customer with prescription and product details
app.post('/api/customers', (req, res) => {
    const { name, phone, date, prescription, frameName, lensName, frameCost, lensCost, totalCost } = req.body;
    
    if (!name) {
        res.status(400).json({ error: 'Customer name is required' });
        return;
    }
    
    db.serialize(() => {
        // Insert customer
        db.run(
            'INSERT INTO customers (name, phone, date) VALUES (?, ?, ?)',
            [name, phone, date],
            function(err) {
                if (err) {
                    res.status(500).json({ error: err.message });
                    return;
                }
                
                const customerId = this.lastID;
                
                // Insert prescription
                const {
                    rightSph, rightCyl, rightAxe, rightAdd,
                    leftSph, leftCyl, leftAxe, leftAdd
                } = prescription || {};
                
                db.run(
                    `INSERT INTO prescriptions (
                        customer_id, right_sph, right_cyl, right_axe, right_add,
                        left_sph, left_cyl, left_axe, left_add
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
                    [customerId, rightSph, rightCyl, rightAxe, rightAdd, leftSph, leftCyl, leftAxe, leftAdd],
                    function(err) {
                        if (err) {
                            res.status(500).json({ error: err.message });
                            return;
                        }
                        
                        // Insert product details
                        db.run(
                            `INSERT INTO products (
                                customer_id, frame_name, lens_name, frame_cost, lens_cost, total_cost
                            ) VALUES (?, ?, ?, ?, ?, ?)`,
                            [customerId, frameName, lensName, frameCost, lensCost, totalCost],
                            function(err) {
                                if (err) {
                                    res.status(500).json({ error: err.message });
                                    return;
                                }
                                
                                res.json({ 
                                    message: 'Customer added successfully',
                                    customerId 
                                });
                            }
                        );
                    }
                );
            }
        );
    });
});

// Update customer with prescription and product details
app.put('/api/customers/:id', (req, res) => {
    const id = req.params.id;
    const { name, phone, date, prescription, frameName, lensName, frameCost, lensCost, totalCost } = req.body;
    
    if (!name) {
        res.status(400).json({ error: 'Customer name is required' });
        return;
    }
    
    db.serialize(() => {
        // Update customer
        db.run(
            'UPDATE customers SET name = ?, phone = ?, date = ? WHERE id = ?',
            [name, phone, date, id],
            function(err) {
                if (err) {
                    res.status(500).json({ error: err.message });
                    return;
                }
                
                if (this.changes === 0) {
                    res.status(404).json({ error: 'Customer not found' });
                    return;
                }
                
                // Update prescription
                const {
                    rightSph, rightCyl, rightAxe, rightAdd,
                    leftSph, leftCyl, leftAxe, leftAdd
                } = prescription || {};
                
                db.run(
                    `UPDATE prescriptions SET 
                        right_sph = ?, right_cyl = ?, right_axe = ?, right_add = ?,
                        left_sph = ?, left_cyl = ?, left_axe = ?, left_add = ?
                    WHERE customer_id = ?`,
                    [rightSph, rightCyl, rightAxe, rightAdd, leftSph, leftCyl, leftAxe, leftAdd, id],
                    function(err) {
                        if (err) {
                            res.status(500).json({ error: err.message });
                            return;
                        }
                        
                        // If no prescription record exists, create one
                        if (this.changes === 0) {
                            db.run(
                                `INSERT INTO prescriptions (
                                    customer_id, right_sph, right_cyl, right_axe, right_add,
                                    left_sph, left_cyl, left_axe, left_add
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
                                [id, rightSph, rightCyl, rightAxe, rightAdd, leftSph, leftCyl, leftAxe, leftAdd]
                            );
                        }
                        
                        // Update product details
                        db.run(
                            `UPDATE products SET 
                                frame_name = ?, lens_name = ?, frame_cost = ?, lens_cost = ?, total_cost = ?
                            WHERE customer_id = ?`,
                            [frameName, lensName, frameCost, lensCost, totalCost, id],
                            function(err) {
                                if (err) {
                                    res.status(500).json({ error: err.message });
                                    return;
                                }
                                
                                // If no product record exists, create one
                                if (this.changes === 0) {
                                    db.run(
                                        `INSERT INTO products (
                                            customer_id, frame_name, lens_name, frame_cost, lens_cost, total_cost
                                        ) VALUES (?, ?, ?, ?, ?, ?)`,
                                        [id, frameName, lensName, frameCost, lensCost, totalCost]
                                    );
                                }
                                
                                res.json({ message: 'Customer updated successfully' });
                            }
                        );
                    }
                );
            }
        );
    });
});

// Delete customer (will cascade to prescription and products)
app.delete('/api/customers/:id', (req, res) => {
    const id = req.params.id;
    
    db.run('DELETE FROM customers WHERE id = ?', [id], function(err) {
        if (err) {
            res.status(500).json({ error: err.message });
            return;
        }
        
        if (this.changes === 0) {
            res.status(404).json({ error: 'Customer not found' });
            return;
        }
        
        res.json({ message: 'Customer deleted successfully' });
    });
});

// Search customers
app.get('/api/search', (req, res) => {
    const searchTerm = `%${req.query.term || ''}%`;
    
    const query = `
        SELECT c.*, p.frame_name, p.lens_name, p.total_cost 
        FROM customers c
        LEFT JOIN products p ON c.id = p.customer_id
        WHERE c.name LIKE ? OR c.phone LIKE ? OR p.frame_name LIKE ? OR p.lens_name LIKE ?
        ORDER BY c.date DESC
    `;
    
    db.all(query, [searchTerm, searchTerm, searchTerm, searchTerm], (err, rows) => {
        if (err) {
            res.status(500).json({ error: err.message });
            return;
        }
        res.json(rows);
    });
});

// Serve the main HTML file
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
}); 