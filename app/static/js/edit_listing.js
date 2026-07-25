document.addEventListener('DOMContentLoaded', async () => {
    const form = document.getElementById('editListingForm');
    const messageDiv = document.getElementById('message');
    const deleteBtn = document.getElementById('confirmDeleteBtn');

    // 1. Fetch current data to pre-fill the form
    try {
        const response = await fetch(`/api/listings/${LISTING_ID}`);
        if (!response.ok) throw new Error("Failed to fetch listing data");

        const item = await response.json();

        // Populate the form fields explicitly
        document.getElementById('title').value = item.title || '';
        document.getElementById('description').value = item.description || '';
        document.getElementById('price').value = item.price || '';
        document.getElementById('category').value = item.category || 'Textbooks';
        document.getElementById('condition').value = item.condition || 'New';
        document.getElementById('image_url').value = item.image_url || '';

    } catch (err) {
        console.error(err);
        messageDiv.innerHTML = `<div class="alert alert-danger">Error loading item data.</div>`;
    }

    // 2. Handle Update (PUT)
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const priceVal = document.getElementById('price').value.trim();

        // --- FRONTEND PRICE VALIDATION ---
        const isFreeOrSwap = priceVal.toLowerCase() === "free" || priceVal.toLowerCase() === "swap only";
        const isValidNumber = !isNaN(priceVal) && priceVal !== "";

        if (!isFreeOrSwap && !isValidNumber) {
            messageDiv.innerHTML = `<div class="alert alert-danger">Price must be a valid number, 'Free', or 'Swap Only'.</div>`;
            window.scrollTo(0, 0);
            return;
        }
        // ---------------------------------

        const updatedData = {
            title: document.getElementById('title').value,
            description: document.getElementById('description').value,
            price: priceVal,
            category: document.getElementById('category').value,
            condition: document.getElementById('condition').value,
            image_url: document.getElementById('image_url').value
        };

        try {
            const response = await fetch(`/api/listings/${LISTING_ID}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updatedData)
            });

            if (response.ok) {
                messageDiv.innerHTML = `<div class="alert alert-success">Update successful! Redirecting...</div>`;
                window.scrollTo(0, 0);
                setTimeout(() => window.location.href = `/listings/${LISTING_ID}`, 2000);
            } else {
                const err = await response.json();
                messageDiv.innerHTML = `<div class="alert alert-danger">Error: ${err.error}</div>`;
                window.scrollTo(0, 0);
            }
        } catch (error) {
            console.error(error);
            messageDiv.innerHTML = `<div class="alert alert-danger">Failed to connect to server.</div>`;
            window.scrollTo(0, 0);
        }
    });

    // 3. Handle Soft-Delete (DELETE)
    if (deleteBtn) {
        deleteBtn.addEventListener('click', async () => {
            try {
                const response = await fetch(`/api/listings/${LISTING_ID}`, { 
                    method: 'DELETE' 
                });

                if (response.ok) {
                    window.location.href = '/marketplace';
                } else {
                    const err = await response.json();
                    messageDiv.innerHTML = `<div class="alert alert-danger">Error deleting: ${err.error}</div>`;
                    window.scrollTo(0, 0);
                }
            } catch (error) {
                console.error(error);
                messageDiv.innerHTML = `<div class="alert alert-danger">Failed to connect to server for deletion.</div>`;
                window.scrollTo(0, 0);
            }
        });
    }
});
