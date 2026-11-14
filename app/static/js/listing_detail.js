function renderStars(average) {
    const rounded = Math.round(average);
    let stars = "";
    for (let i = 1; i <= 5; i++) stars += i <= rounded ? "★" : "☆";
    return stars;
}

async function loadSellerRating(sellerId) {
    const block = document.getElementById("sellerRatingBlock");
    if (!block) return;
    try {
        const response = await fetch("/api/users/" + sellerId + "/reviews");
        if (!response.ok) throw new Error("Unable to load rating");
        const data = await response.json();
        if (!data.review_count) {
            block.innerHTML = '<span class="text-muted">No ratings yet (New Trader)</span>';
            return;
        }
        block.innerHTML = '<span class="text-warning">' + renderStars(data.average_rating) +
            '</span> <span class="fw-semibold">' + data.average_rating +
            '</span> <span class="text-muted">(' + data.review_count + ' review' +
            (data.review_count === 1 ? '' : 's') + ')</span>';
    } catch (error) {
        block.innerHTML = '<span class="text-muted">Rating unavailable</span>';
    }
}

document.addEventListener("DOMContentLoaded", async () => {
    const container = document.getElementById("detailContainer");
    try {
        const listingResponse = await fetch("/api/listings/" + LISTING_ID);
        if (!listingResponse.ok) throw new Error("Listing not found");
        const item = await listingResponse.json();
        const isOwner = Number(item.seller_id) === Number(CURRENT_USER_ID);
        let receivedOffers = [];
        if (isOwner) {
            const offersResponse = await fetch("/api/listings/" + LISTING_ID + "/offers");
            if (offersResponse.ok) {
                const offersData = await offersResponse.json();
                receivedOffers = offersData.offers || [];
            }
        }
        const pendingCount = receivedOffers.filter(offer => offer.status === "pending").length;
        const seller = item.seller_info || {};
        const html = '<div class="col-md-6"><img src="' + item.image_url + '" class="img-fluid rounded shadow" alt="' + item.title + '"></div>' +
            '<div class="col-md-6"><nav aria-label="breadcrumb"><ol class="breadcrumb"><li class="breadcrumb-item"><a href="/marketplace">Marketplace</a></li><li class="breadcrumb-item active">' + item.category + '</li></ol></nav>' +
            '<h1 class="display-5 fw-bold">' + item.title + '</h1><p class="text-muted">Listed on: ' + new Date(item.listing_date).toLocaleDateString() + '</p>' +
            '<h3 class="text-success mb-4">$' + item.price + '</h3><div class="mb-4"><h5>Description</h5><p>' + item.description + '</p><span class="badge bg-secondary p-2">Condition: ' + item.condition + '</span></div>' +
            '<div class="card border-primary"><div class="card-body"><h5 class="card-title text-primary">Contact Seller</h5><hr>' +
            '<p class="mb-1"><strong>Name:</strong> ' + (seller.display_name || 'Anonymous') + '</p><div id="sellerRatingBlock" class="mb-2 small text-muted">Loading rating…</div>' +
            '<p class="mb-1"><strong>Email:</strong> <a href="mailto:' + (seller.email || '') + '">' + (seller.email || 'N/A') + '</a></p>' +
            '<p class="mb-0"><strong>Phone:</strong> ' + (seller.contact_number || 'N/A') + '</p></div></div>' +
            (isOwner ? '<div class="card mt-4"><div class="card-body"><h5 class="card-title">Offers Received' + (pendingCount ? ' <span class="badge bg-danger ms-2">' + pendingCount + ' pending</span>' : '') + '</h5><hr><div id="sellerOffersContainer"></div></div></div>' : '') +
            '<div class="mt-4 d-grid gap-2">' + (isOwner ? '' : '<button class="btn btn-primary btn-lg" id="makeOfferBtn">Make an Offer</button>') +
            '<button class="btn btn-outline-danger" data-bs-toggle="modal" data-bs-target="#reportModal">Report Listing</button>' +
            (isOwner ? '<a href="/edit-listing/' + item.id + '" class="btn btn-outline-secondary">Edit My Listing</a>' : '') + '</div>' +
            '<div class="modal fade" id="reportModal" tabindex="-1"><div class="modal-dialog"><div class="modal-content"><div class="modal-header"><h5 class="modal-title">Report Listing</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>' +
            '<div class="modal-body"><div class="mb-3"><label class="form-label" for="reportReason">Reason</label><select class="form-select" id="reportReason"><option value="">Select Reason</option><option value="Spam">Spam</option><option value="Scam">Scam</option><option value="Inappropriate Content">Inappropriate Content</option><option value="Duplicate Listing">Duplicate Listing</option></select></div>' +
            '<div class="mb-3"><label class="form-label" for="reportDescription">Description</label><textarea class="form-control" id="reportDescription" rows="4"></textarea></div></div><div class="modal-footer"><button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button><button type="button" class="btn btn-danger" id="submitReportBtn">Submit Report</button></div></div></div></div></div>';
        container.innerHTML = html;
        if (item.seller_id) loadSellerRating(item.seller_id);
        if (isOwner) displaySellerOffers(receivedOffers);
        const makeOfferButton = document.getElementById("makeOfferBtn");
        if (makeOfferButton) makeOfferButton.addEventListener("click", async () => {
            const enteredPrice = prompt("Enter your offer price:");
            if (enteredPrice === null) return;
            const offerPrice = Number(enteredPrice);
            if (!enteredPrice.trim() || !Number.isFinite(offerPrice) || offerPrice <= 0) {
                alert("Please enter a valid offer price.");
                return;
            }
            try {
                const response = await fetch("/api/offers", {
                    method: "POST", headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ listing_id: item.id, offer_price: offerPrice })
                });
                const result = await response.json();
                if (response.ok) alert(result.message);
                else alert(result.error || "Unable to create offer.");
            } catch (error) { alert("Unable to create offer."); }
        });
        document.getElementById("submitReportBtn").addEventListener("click", async () => {
            const reason = document.getElementById("reportReason").value;
            const description = document.getElementById("reportDescription").value.trim();
            if (!reason || !description) {
                alert("Please provide a reason and description.");
                return;
            }
            try {
                const response = await fetch("/api/reports", {
                    method: "POST", headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ listing_id: item.id, reason, description })
                });
                const result = await response.json();
                if (response.ok) { alert(result.message); location.reload(); }
                else alert(result.error || "Failed to submit report.");
            } catch (error) { alert("Unable to submit report."); }
        });
    } catch (error) {
        container.innerHTML = '<div class="alert alert-danger w-100"><h4>Error 404</h4><p>Sorry, the listing you are looking for does not exist or has been deleted.</p><a href="/marketplace" class="btn btn-outline-danger">Back to Marketplace</a></div>';
    }
});

function displaySellerOffers(offers) {
    const offersContainer = document.getElementById("sellerOffersContainer");
    if (!offersContainer) return;
    if (!offers.length) {
        offersContainer.innerHTML = '<p class="text-muted mb-0">No offers have been received yet.</p>';
        return;
    }
    offersContainer.innerHTML = offers.map(offer => {
        const price = offer.offer_price !== null ? '$' + Number(offer.offer_price).toFixed(2) : 'No price offered';
        const swapListing = offer.swap_listing_id ? '<p class="mb-1"><strong>Swap listing:</strong> ' + (offer.swap_listing_title || '(listing no longer available)') + '</p>' : '';
        const actions = offer.status === 'pending' ? '<button class="btn btn-success btn-sm offer-action" data-offer-id="' + offer.id + '" data-action="accept">Accept</button> <button class="btn btn-outline-danger btn-sm offer-action" data-offer-id="' + offer.id + '" data-action="reject">Reject</button>' : '';
        return '<div class="border rounded p-3 mb-3"><p class="mb-1"><strong>Buyer:</strong> ' + (offer.buyer_display_name || ('Buyer #' + offer.buyer_id)) + '</p><p class="mb-1"><strong>Offer:</strong> ' + price + '</p>' + swapListing + '<p class="mb-2"><strong>Status:</strong> <span class="badge bg-secondary">' + offer.status + '</span></p><div class="d-flex gap-2">' + actions + '</div></div>';
    }).join('');
    document.querySelectorAll('.offer-action').forEach(button => button.addEventListener('click', () => updateOffer(button.dataset.offerId, button.dataset.action)));
}

async function updateOffer(offerId, action) {
    try {
        const response = await fetch('/api/offers/' + offerId + '/' + action, { method: 'POST' });
        const result = await response.json();
        if (response.ok) { alert(result.message); location.reload(); }
        else alert(result.error || ('Unable to ' + action + ' offer.'));
    } catch (error) { alert('Unable to ' + action + ' offer.'); }
}