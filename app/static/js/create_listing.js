document.getElementById('createListingForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const messageDiv = document.getElementById('message');
    const data = {
        title: document.getElementById('title').value,
        description: document.getElementById('description').value,
        price: document.getElementById('price').value,
        category: document.getElementById('category').value,
        condition: document.getElementById('condition').value,
        image_url: document.getElementById('image_url').value
    };

    try {
        const response = await fetch('/api/listings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            messageDiv.innerHTML = `<div class="alert alert-success">Listing created! Redirecting to marketplace...</div>`;
            // Scroll to top so they see the message
            window.scrollTo(0, 0); 
            setTimeout(() => window.location.href = '/marketplace', 2000);
        } else {
            const err = await response.json();
            messageDiv.innerHTML = `<div class="alert alert-danger">Error: ${err.error}</div>`;
        }
    } catch (error) {
        messageDiv.innerHTML = `<div class="alert alert-danger">Failed to connect to server.</div>`;
    }
});
