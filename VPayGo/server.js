const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');

const app = express();
const port = process.env.PORT || 3000;

app.use(cors());
app.use(bodyParser.json());
app.use(express.static('client')); // Serve frontend files

let products = []; // Store detected products

// Default route
app.get('/', (req, res) => {
    res.send("Server is running successfully!");
});

// Add a new product
app.post('/api/products', (req, res) => {
    const product = req.body;
    console.log('Received product:', product);
    products.push(product);
    res.json({ message: 'Product added successfully', product });
});

// Get all products
app.get('/api/products', (req, res) => {
    res.json(products);
});

// Clear products (for testing/checkout)
app.delete('/api/products', (req, res) => {
    products = [];
    res.json({ message: 'Products cleared' });
});

app.listen(port, () => {
    console.log(`Server running on http://localhost:${port}`);
});
