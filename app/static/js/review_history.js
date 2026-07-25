let currentUserId = null;

function renderStars(average) {
    const rounded = Math.round(average);
    let stars = "";
    for (let i = 1; i <= 5; i++) {
        stars += i <= rounded ? "\u2605" : "\u2606";
    }
    return stars;
}

function formatDate(isoString) {
    return new Date(isoString).toLocaleDateString();
}

async function loadPendingReviews() {
    const list = document.getElementById("pendingReviewsList");

    try {
        const response = await fetch("/api/reviews/pending");
        if (response.status === 401) {
            window.location.href = "/login";
            return;
        }
        if (!response.ok) throw new Error("Failed to load pending reviews");

        const data = await response.json();
        currentUserId = data.user_id;

        if (!data.pending_reviews.length) {
            list.innerHTML = `<p class="text-muted">You're all caught up - no reviews pending.</p>`;
        } else {
            list.innerHTML = data.pending_reviews.map((pending) => `
                <div class="card mb-2">
                    <div class="card-body d-flex justify-content-between align-items-center">
                        <div>
                            <strong>${pending.counterpart_display_name || "Unknown user"}</strong>
                            <span class="text-muted"> &middot; ${pending.your_role === "buyer" ? "you bought from them" : "you sold to them"}</span>
                            ${pending.listing_title ? `<div class="text-muted small">${pending.listing_title}</div>` : ""}
                            <div class="text-muted small">Completed ${formatDate(pending.completed_at)}</div>
                        </div>
                        <button
                            class="btn btn-outline-primary btn-sm leave-review-btn"
                            data-transaction-id="${pending.transaction_id}"
                            data-counterpart-name="${pending.counterpart_display_name || "this user"}">
                            Leave a Review
                        </button>
                    </div>
                </div>
            `).join("");

            document.querySelectorAll(".leave-review-btn").forEach((btn) => {
                btn.addEventListener("click", () => openReviewModal(
                    btn.dataset.transactionId,
                    btn.dataset.counterpartName
                ));
            });
        }

        if (currentUserId) {
            loadReceivedReviews(currentUserId);
        }
    } catch (error) {
        list.innerHTML = `<p class="text-danger">Unable to load pending reviews right now.</p>`;
    }
}

async function loadReceivedReviews(userId) {
    const summary = document.getElementById("receivedReviewsSummary");
    const list = document.getElementById("receivedReviewsList");

    try {
        const response = await fetch(`/api/users/${userId}/reviews`);
        if (!response.ok) throw new Error("Failed to load reviews");

        const data = await response.json();

        if (!data.review_count) {
            summary.innerHTML = `<span class="text-muted">No ratings yet (New Trader)</span>`;
            list.innerHTML = "";
            return;
        }

        summary.innerHTML = `
            <span class="text-warning fs-5">${renderStars(data.average_rating)}</span>
            <span class="fw-semibold">${data.average_rating}</span>
            <span class="text-muted">(${data.review_count} review${data.review_count === 1 ? "" : "s"})</span>
        `;

        list.innerHTML = data.reviews.map((review) => `
            <div class="border-bottom py-2">
                <span class="text-warning">${renderStars(review.rating)}</span>
                <span class="text-muted small ms-2">${formatDate(review.created_at)}</span>
                ${review.comment ? `<p class="mb-0">${review.comment}</p>` : ""}
            </div>
        `).join("");
    } catch (error) {
        list.innerHTML = `<p class="text-danger">Unable to load reviews right now.</p>`;
    }
}

function openReviewModal(transactionId, counterpartName) {
    document.getElementById("reviewTransactionId").value = transactionId;
    document.getElementById("reviewModalSubtitle").textContent = `How was your experience with ${counterpartName}?`;
    document.getElementById("reviewComment").value = "";
    document.getElementById("reviewError").classList.add("d-none");
    setStarRating(0);

    const modal = new bootstrap.Modal(document.getElementById("reviewModal"));
    modal.show();
}

function setStarRating(value) {
    document.getElementById("reviewRating").value = value;
    document.querySelectorAll("#starPicker .star").forEach((star) => {
        const starValue = parseInt(star.dataset.value, 10);
        star.innerHTML = starValue <= value ? "\u2605" : "\u2606";
    });
}

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("#starPicker .star").forEach((star) => {
        star.addEventListener("click", () => {
            setStarRating(parseInt(star.dataset.value, 10));
        });
    });

    document.getElementById("submitReviewBtn").addEventListener("click", async () => {
        const errorBox = document.getElementById("reviewError");
        errorBox.classList.add("d-none");

        const transactionId = parseInt(document.getElementById("reviewTransactionId").value, 10);
        const rating = parseInt(document.getElementById("reviewRating").value, 10);
        const comment = document.getElementById("reviewComment").value.trim();

        if (!rating) {
            errorBox.textContent = "Please select a star rating.";
            errorBox.classList.remove("d-none");
            return;
        }

        try {
            const response = await fetch("/api/reviews", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    transaction_id: transactionId,
                    rating,
                    comment: comment || null
                })
            });

            const result = await response.json();

            if (!response.ok) {
                errorBox.textContent = result.error || "Unable to submit review.";
                errorBox.classList.remove("d-none");
                return;
            }

            bootstrap.Modal.getInstance(document.getElementById("reviewModal")).hide();
            loadPendingReviews();
        } catch (error) {
            errorBox.textContent = "Something went wrong. Please try again.";
            errorBox.classList.remove("d-none");
        }
    });

    loadPendingReviews();
});