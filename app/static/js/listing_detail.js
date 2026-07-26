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
        // Load listing details
        const listingResponse = await fetch(`/api/listings/${LISTING_ID}`);

<<<<<<< HEAD
        const item = await response.json();

        // 1. Authorization Logic
        const isOwner = item.seller_id === CURRENT_USER_ID;

        // 2. Prepare the Edit button only if the user is the owner
        let editButtonHtml = "";
        if (isOwner) {
            editButtonHtml = `<a href="/edit-listing/${item.id}" class="btn btn-outline-secondary">Edit My Listing</a>`;
=======
        if (!listingResponse.ok) {
            throw new Error("Listing not found");
>>>>>>> feature/offers-transactions
        }

        const item = await listingResponse.json();

        // Check whether the logged-in user owns this listing.
        // The offers endpoint returns 200 only for the listing owner.
        const offersResponse = await fetch(
            `/api/listings/${LISTING_ID}/offers`
        );

        const isOwner = offersResponse.ok;
        let receivedOffers = [];

        if (isOwner) {
            const offersData = await offersResponse.json();
            receivedOffers = offersData.offers || [];
        }

        const editButtonHtml = isOwner
            ? `
                <a
                    href="/edit-listing/${item.id}"
                    class="btn btn-outline-secondary">
                    Edit My Listing
                </a>
            `
            : "";

        const makeOfferButtonHtml = !isOwner
            ? `
                <button
                    class="btn btn-primary btn-lg"
                    id="makeOfferBtn">
                    Make an Offer
                </button>
            `
            : "";

        const offersSectionHtml = isOwner
            ? `
                <div class="card mt-4">
                    <div class="card-body">
                        <h5 class="card-title">Offers Received</h5>
                        <hr>
                        <div id="sellerOffersContainer"></div>
                    </div>
                </div>
            `
            : "";

        container.innerHTML = `
            <div class="col-md-6">
                <img
                    src="${item.image_url}"
                    class="img-fluid rounded shadow"
                    alt="${item.title}">
            </div>

            <div class="col-md-6">
                <nav aria-label="breadcrumb">
                    <ol class="breadcrumb">
                        <li class="breadcrumb-item">
                            <a href="/marketplace">Marketplace</a>
                        </li>
                        <li class="breadcrumb-item active">
                            ${item.category}
                        </li>
                    </ol>
                </nav>

                <h1 class="display-5 fw-bold">${item.title}</h1>

                <p class="text-muted">
                    Listed on:
                    ${new Date(item.listing_date).toLocaleDateString()}
                </p>

                <h3 class="text-success mb-4">$${item.price}</h3>

                <div class="mb-4">
                    <h5>Description</h5>
                    <p>${item.description}</p>

                    <span class="badge bg-secondary p-2">
                        Condition: ${item.condition}
                    </span>
                </div>

                <div class="card border-primary">
                    <div class="card-body">
                        <h5 class="card-title text-primary">
                            Contact Seller
                        </h5>

                        <hr>
<<<<<<< HEAD
                        <p class="mb-1"><strong>Name:</strong> ${item.seller_info ? item.seller_info.display_name : "Anonymous"}</p>
                        <div id="sellerRatingBlock" class="mb-2 small text-muted">Loading rating&hellip;</div>
                        <p class="mb-1"><strong>Email:</strong> <a href="mailto:${item.seller_info ? item.seller_info.email : ""}">${item.seller_info ? item.seller_info.email : "N/A"}</a></p>
                        <p class="mb-0"><strong>Phone:</strong> ${item.seller_info ? item.seller_info.contact_number : "N/A"}</p>
=======

                        <p class="mb-1">
                            <strong>Name:</strong>
                            ${
                                item.seller_info
                                    ? item.seller_info.display_name
                                    : "Anonymous"
                            }
                        </p>

                        <p class="mb-1">
                            <strong>Email:</strong>
                            <a href="mailto:${
                                item.seller_info
                                    ? item.seller_info.email
                                    : ""
                            }">
                                ${
                                    item.seller_info
                                        ? item.seller_info.email
                                        : "N/A"
                                }
                            </a>
                        </p>

                        <p class="mb-0">
                            <strong>Phone:</strong>
                            ${
                                item.seller_info
                                    ? item.seller_info.contact_number
                                    : "N/A"
                            }
                        </p>
>>>>>>> feature/offers-transactions
                    </div>
                </div>

                ${offersSectionHtml}

                <div class="mt-4 d-grid gap-2">
<<<<<<< HEAD
                    ${isOwner ? "" : `
                    <button
                        class="btn btn-primary btn-lg"
                        data-bs-toggle="modal"
                        data-bs-target="#offerModal">
                        Make an Offer
                    </button>`}
=======
                    ${makeOfferButtonHtml}
>>>>>>> feature/offers-transactions

                    <button
                        class="btn btn-outline-danger"
                        data-bs-toggle="modal"
                        data-bs-target="#reportModal">
                        Report Listing
                    </button>

                    ${editButtonHtml}
                </div>

                <div
                    class="modal fade"
                    id="reportModal"
                    tabindex="-1">

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
                                    <label class="form-label">
                                        Reason
                                    </label>

                                    <select
                                        class="form-select"
                                        id="reportReason">

                                        <option value="">
                                            Select Reason
                                        </option>
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
                                    <label class="form-label">
                                        Description
                                    </label>

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
<<<<<<< HEAD

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
=======
            </div>
        `;

        // Display offers to the seller
        if (isOwner) {
            displaySellerOffers(receivedOffers);
        }

        // Buyer makes an offer
        const makeOfferButton =
            document.getElementById("makeOfferBtn");

        if (makeOfferButton) {
            makeOfferButton.addEventListener("click", async () => {
                const enteredPrice = prompt(
                    "Enter your offer price:"
                );

                if (enteredPrice === null) {
                    return;
                }

                const offerPrice = Number(enteredPrice);

                if (!enteredPrice.trim() || offerPrice <= 0) {
                    alert("Please enter a valid offer price.");
                    return;
                }

                try {
                    const response = await fetch("/api/offers", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({
                            listing_id: item.id,
                            offer_price: offerPrice
                        })
                    });

                    const result = await response.json();

                    if (response.ok) {
                        alert(result.message);
                    } else {
                        alert(
                            result.error ||
                            "Unable to create offer."
                        );
                    }
                } catch (error) {
                    alert("Unable to create offer.");
                }
            });
        }

        // Submit report
        const reportButton =
            document.getElementById("submitReportBtn");

        if (reportButton) {
            reportButton.addEventListener("click", async () => {
                const reason =
                    document.getElementById("reportReason").value;

                const description =
                    document
                        .getElementById("reportDescription")
                        .value
                        .trim();

                if (!reason || !description) {
                    alert(
                        "Please provide a reason and description."
                    );
>>>>>>> feature/offers-transactions
                    return;
                }

                try {
                    const response = await fetch("/api/reports", {
                        method: "POST",
<<<<<<< HEAD
                        headers: { "Content-Type": "application/json" },
=======
                        headers: {
                            "Content-Type": "application/json"
                        },
>>>>>>> feature/offers-transactions
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
<<<<<<< HEAD
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
=======
                        alert(
                            result.error ||
                            "Failed to submit report."
                        );
                    }
                } catch (error) {
                    alert("Unable to submit report.");
                }
            });
>>>>>>> feature/offers-transactions
        }

    } catch (error) {
        container.innerHTML = `
            <div class="alert alert-danger w-100">
                <h4>Error 404</h4>

                <p>
                    Sorry, the listing you are looking for does
                    not exist or has been deleted.
                </p>

                <a
                    href="/marketplace"
                    class="btn btn-outline-danger">
                    Back to Marketplace
                </a>
            </div>
        `;
    }
<<<<<<< HEAD
});
=======
});


function displaySellerOffers(offers) {
    const offersContainer =
        document.getElementById("sellerOffersContainer");

    if (!offersContainer) {
        return;
    }

    if (offers.length === 0) {
        offersContainer.innerHTML = `
            <p class="text-muted mb-0">
                No offers have been received yet.
            </p>
        `;
        return;
    }

    offersContainer.innerHTML = offers
        .map((offer) => {
            const price = offer.offer_price !== null
                ? `$${Number(offer.offer_price).toFixed(2)}`
                : "No price offered";

            const swapListing = offer.swap_listing_id
                ? `
                    <p class="mb-1">
                        <strong>Swap listing:</strong>
                        ${offer.swap_listing_id}
                    </p>
                `
                : "";

            const actionButtons = offer.status === "pending"
                ? `
                    <button
                        class="btn btn-success btn-sm offer-action"
                        data-offer-id="${offer.id}"
                        data-action="accept">
                        Accept
                    </button>

                    <button
                        class="btn btn-outline-danger btn-sm offer-action"
                        data-offer-id="${offer.id}"
                        data-action="reject">
                        Reject
                    </button>
                `
                : "";

            return `
                <div class="border rounded p-3 mb-3">
                    <p class="mb-1">
                        <strong>Buyer ID:</strong>
                        ${offer.buyer_id}
                    </p>

                    <p class="mb-1">
                        <strong>Offer:</strong>
                        ${price}
                    </p>

                    ${swapListing}

                    <p class="mb-2">
                        <strong>Status:</strong>
                        <span class="badge bg-secondary">
                            ${offer.status}
                        </span>
                    </p>

                    <div class="d-flex gap-2">
                        ${actionButtons}
                    </div>
                </div>
            `;
        })
        .join("");

    document
        .querySelectorAll(".offer-action")
        .forEach((button) => {
            button.addEventListener("click", async () => {
                const offerId = button.dataset.offerId;
                const action = button.dataset.action;

                await updateOffer(offerId, action);
            });
        });
}


async function updateOffer(offerId, action) {
    try {
        const response = await fetch(
            `/api/offers/${offerId}/${action}`,
            {
                method: "POST"
            }
        );

        const result = await response.json();

        if (response.ok) {
            alert(result.message);
            location.reload();
        } else {
            alert(
                result.error ||
                `Unable to ${action} offer.`
            );
        }
    } catch (error) {
        alert(`Unable to ${action} offer.`);
    }
}
>>>>>>> feature/offers-transactions
