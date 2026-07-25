document.addEventListener('DOMContentLoaded', async () => {
    const form = document.getElementById('editListingForm');
    const messageDiv = document.getElementById('message');
    const deleteBtn = document.getElementById('confirmDeleteBtn');

    // 1. Fetch current data to pre-fill the form
    try {
        const response = await fetch(`/api/listings/${LISTING_ID}`);
        const item = await response.json();

        document.getElementById('title').value = item.title;
        document.getElementById('description').value = item.description;
        document.getElementById('price').value = item.price;
        document.getElementById('category').value = item.category;
        document.getElementById('condition').value = item.condition;
        document.getElementById('image_url').value = item.image_url;
    } catch (err) {
        messageDiv.innerHTML = `<div class="alert alert-danger">Error loading item data.</div>`;
    }

    // 2. Handle Update (PUT)
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const updatedData = {
            title: document.getElementById('title').value,
            description: document.getElementById('description').value,
            price: document.getElementById('price').value,
            category: document.getElementById('category').value,
            condition: document.getElementById('condition').value,
            image_url: document.getElementById('image_url').value
        };

        const response = await fetch(`/api/listings/${LISTING_ID}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updatedData)
        });

        if (response.ok) {
            messageDiv.innerHTML = `<div class="alert alert-success">Update successful! Redirecting...</div>`;
            setTimeout(() => window.location.href = `/listings/${LISTING_ID}`, 2000);
        } else {
            const err = await response.json();
            messageDiv.innerHTML = `<div class="alert alert-danger">Error: ${err.error}</div>`;
        }
    });

    // 3. Handle Soft-Delete (DELETE)
    deleteBtn.addEventListener('click', async () => {
        const response = await fetch(`/api/listings/${LISTING_ID}`, { method: 'DELETE' });
        if (response.ok) {
            window.location.href = '/marketplace';
        } else {
            const err = await response.json();
            messageDiv.innerHTML = `<div class="alert alert-danger">Error: ${err.error}</div>`;
        }
    });
});
