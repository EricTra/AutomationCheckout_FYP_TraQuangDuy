const express = require("express");
const cors = require("cors");
const bodyParser = require("body-parser");

const app = express();
app.use(cors());
app.use(bodyParser.json());

// Products storage
let products = [];

// Get all products (for frontend)
app.get("/api/products", (req, res) => {
  res.json(products);
});

// Add a product (from Jetson Nano)
app.post("/api/products", (req, res) => {
  const { name, weight, price, image } = req.body;

  if (name && weight && price && image) {
    products.push({ name, weight, price, image, timestamp: Date.now() });
    res.json({ status: "success", message: "Product added", product: req.body });
  } else {
    res.status(400).json({ status: "error", message: "Invalid data format" });
  }
});

// Checkout (clear products)
app.post("/api/checkout", (req, res) => {
  products = [];
  res.json({ status: "success", message: "Checkout complete" });
});

// Start the server
const PORT = 3000;
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
