document.getElementById("btn-outline-secondary").addEventListener("click", function () {
    var productId = document.getElementById("product-id").value;
    var quantity = document.getElementById("quantity").value;

    // Send a POST request to the server with the product ID and quantity as data
    fetch("/add-to-cart", {
        method: "POST",
        body: JSON.stringify({ productId: productId, quantity: quantity }),
        headers: {
            "Content-Type": "application/json"
        }
    });
});