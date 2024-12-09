const API_URL = "http://localhost:3000/api/products";

// Fetch products from server
async function fetchProducts() {
  const response = await fetch(API_URL);
  const products = await response.json();

  const tableBody = document.getElementById("product-list");
  tableBody.innerHTML = ""; // Clear previous content

  products.forEach((p) => {
    const row = `
      <tr>
        <td><img src="assets/${p.image}" alt="${p.name}" width="50"></td>
        <td>${p.name}</td>
        <td>${p.weight}</td>
        <td>${p.price}</td>
      </tr>
    `;
    tableBody.innerHTML += row;
  });
}

// Send request to clear products (checkout)
async function checkout() {
  await fetch("http://localhost:3000/api/checkout", { method: "POST" });
  fetchProducts();
  alert("Checkout Complete!");
}

// Event listeners
document.getElementById("checkout-btn").addEventListener("click", checkout);
setInterval(fetchProducts, 1000); // Auto-refresh every 1 second
