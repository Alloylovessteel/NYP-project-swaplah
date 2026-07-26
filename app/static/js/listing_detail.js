function renderStars(average) {
    const rounded = Math.round(average);
    let stars = "";
    for (let i = 1; i <= 5; i++) {
        stars += i <= rounded ? "\u2605" : "\u2606";
    }
    return stars;
}

async function loadSellerRating(sellerId) {
    const block = document.getElementById("sellerRatingBlock");
    if (!block) return;

    try {
        const response = await fetch(`/api/users/${sellerId}/reviews`);
        if (!response.ok) throw new Error("Unable to load rating");

        const data = await response.json();

        if (!data.review_count) {
            block.innerHTML = `<span class="text-muted">No ratings yet (New Trader)</span>`;
            return;
        }

        const starsHtml = renderStars(data.average_rating);
        block.innerHTML = `
            <span class="text-warning">${starsHtml}</span>
            <span class="fw-semibold">${data.average_rating}</span>
            <span class="text-muted">(${data.review_count} review${data.review_count === 1 ? "" : "s"})</span>
        `;
    } catch (error) {
        block.innerHTML = `<span class="text-muted">Rating unavailable</span>`;
    }
}

document.addEventListener("DOMContentLoaded", async () => {
    const container = document.getElementById("detailContainer");

    try {
        const response = await fetch(`/api/listings/${LISTING_ID}`);
        if (!response.ok) throw new Error("Item not found");

        const item = await response.json();

        // 1. Authorization Logic
        const isOwner = item.seller_id === CURRENT_USER_ID;

        // 2. Prepare the Edit button only if the user is the owner
        let editButtonHtml = "";
        if (isOwner) {
            editButtonHtml = `<a href="/edit-listing/${item.id}" class="btn btn-outline-secondary">Edit My Listing</a>`;
        }

        // 3. Build the UI
        container.innerHTML = `
            <div class="col-md-6">
                <img src="${item.image_url}" class="img-fluid rounded shadow" alt="${item.title}">
            </div>
            <div class="col-md-6">
                <nav aria-label="breadcrumb">
                    <ol class="breadcrumb">
                        <li class="breadcrumb-item"><a href="/marketplace">Marketplace</a></li>
                        <li class="breadcrumb-item active">${item.category}</li>
                    </ol>
                </nav>
                <h1 class="display-5 fw-bold">${item.title}</h1>
                <p class="text-muted">Listed on: ${new Date(item.listing_date).toLocaleDateString()}</p>
                <h3 class="text-success mb-4">$${item.price}</h3>
                
                <div class="mb-4">
                    <h5>Description</h5>
                    <p>${item.description}</p>
                    <span class="badge bg-secondary p-2">Condition: ${item.condition}</span>
                </div>

                <div class="card border-primary">
                    <div class="card-body">
                        <h5 class="card-title text-primary">Contact Seller</h5>
                        <hr>
                        <p class="mb-1"><strong>Name:</strong> ${item.seller_info ? item.seller_info.display_name : "Anonymous"}</p>
                        <div id="sellerRatingBlock" class="mb-2 small text-muted">Loading rating&hellip;</div>
                        <p class="mb-1"><strong>Email:</strong> <a href="mailto:${item.seller_info ? item.seller_info.email : ""}">${item.seller_info ? item.seller_info.email : "N/A"}</a></p>
                        <p class="mb-0"><strong>Phone:</strong> ${item.seller_info ? item.seller_info.contact_number : "N/A"}</p>
                    </div>
                </div>
                
                <div class="mt-4 d-grid gap-2">
                    ${isOwner ? "" : `
                    <button
                        class="btn btn-primary btn-lg"
                        data-bs-toggle="modal"
                        data-bs-target="#offerModal">
                        Make an Offer
                    </button>`}

                    <button
                        class="btn btn-outline-danger"
                        data-bs-toggle="modal"
                        data-bs-target="#reportModal">
                        Report Listing
                    </button>

                    ${editButtonHtml}
                </div>

                <!-- Report Modal -->
                <div class="modal fade" id="reportModal" tabindex="-1">
                    <div class="modal-dialog">
                        <div class="modal-content">

                            <div class="modal-header">
                                <h5 class="modal-title">Report Listing</h5>
                                <button
                                    type="button"
                                    class="btn-close"
                                    data-bs-dismiss="modal">
                                </button>
                            </div>

                            <div class="modal-body">

                                <div class="mb-3">
                                    <label class="form-label">Reason</label>

                                    <select
                                        class="form-select"
                                        id="reportReason">

                                        <option value="">Select Reason</option>
                                        <option value="Spam">Spam</option>
                                        <option value="Scam">Scam</option>
                                        <option value="Inappropriate Content">
                                            Inappropriate Content
                                        </option>
                                        <option value="Duplicate Listing">
                                            Duplicate Listing
                                        </option>

                                    </select>
                                </div>

                                <div class="mb-3">
                                    <label class="form-label">Description</label>

                                    <textarea
                                        class="form-control"
                                        id="reportDescription"
                                        rows="4">
                                    </textarea>
                                </div>

                            </div>

                            <div class="modal-footer">

                                <button
                                    type="button"
                                    class="btn btn-secondary"
                                    data-bs-dismiss="modal">
                                    Cancel
                                </button>

                                <button
                                    type="button"
                                    class="btn btn-danger"
                                    id="submitReportBtn">
                                    Submit Report
                                </button>

                            </div>

                        </div>
                    </div>
                </div>

                <!-- Offer Modal -->
                <div class="modal fade" id="offerModal" tabindex="-1">
                    <div class="modal-dialog">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">Make an Offer</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <div class="mb-3">
                                    <label class="form-label">Your Offer Price ($)</label>
                                    <input type="number" class="form-control" id="offerPrice" min="0" step="0.01">
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                                <button type="button" class="btn btn-primary" id="submitOfferBtn">Submit Offer</button>
                            </div>
                        </div>
                    </div>
                </div>

            </div>
        `;

        if (item.seller_id) {
            loadSellerRating(item.seller_id);
        }

        const reportButton = document.getElementById("submitReportBtn");

        if (reportButton) {
            reportButton.addEventListener("click", async () => {
                const reason = document.getElementById("reportReason").value;
                const description = document.getElementById("reportDescription").value;

                if (!reason || !description.trim()) {
                    alert("Please provide a reason and description.");
                    return;
                }

                try {
                    const response = await fetch("/api/reports", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            listing_id: item.id,
                            reason,
                            description
                        })
                    });

                    const result = await response.json();

                    if (response.ok) {
                        alert(result.message);
                        location.reload();
                    } else {
                        alert(result.error || "Failed to submit report.");
                    }
                } catch {
                    alert("Unable to submit report.");
                }
            });
        }

        const offerButton = document.getElementById("submitOfferBtn");

        if (offerButton) {
            offerButton.addEventListener("click", async () => {
                const offerPrice = document.getElementById("offerPrice").value;

                if (!offerPrice) {
                    alert("Please enter an offer price.");
                    return;
                }

                try {
                    const response = await fetch("/api/offers", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            listing_id: item.id,
                            offer_price: offerPrice
                        })
                    });

                    const result = await response.json();

                    if (response.ok) {
                        alert(result.message);
                        bootstrap.Modal.getInstance(document.getElementById("offerModal")).hide();
                    } else {
                        alert(result.error || "Failed to submit offer.");
                    }
                } catch {
                    alert("Unable to submit offer.");
                }
            });
        }

    } catch (error) {
        container.innerHTML = `
            <div class="alert alert-danger w-100">
                <h4>Error 404</h4>
                <p>Sorry, the listing you are looking for does not exist or has been deleted.</p>
                <a href="/marketplace" class="btn btn-outline-danger">Back to Marketplace</a>
            </div>`;
    }
});