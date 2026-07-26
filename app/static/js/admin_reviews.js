function renderStars(rating) {
    let stars = "";
    for (let i = 1; i <= 5; i++) {
        stars += i <= rating ? "\u2605" : "\u2606";
    }
    return stars;
}

document.addEventListener("DOMContentLoaded", async () => {
    const container = document.getElementById("reviewsContainer");

    try {
        const response = await fetch("/api/admin/reviews");

        if (response.status === 401 || response.status === 403) {
            container.innerHTML = `
                <div class="alert alert-danger">
                    You do not have permission to view this page.
                </div>
            `;
            return;
        }

        const reviews = await response.json();

        if (reviews.length === 0) {
            container.innerHTML = `
                <div class="alert alert-info">
                    No reviews found.
                </div>
            `;
            return;
        }

        container.innerHTML = reviews.map((review) => `
            <div class="card mb-3 ${review.is_deleted ? "border-danger" : ""}">
                <div class="card-body">
                    <h5>
                        Review #${review.id}
                        ${review.is_deleted ? '<span class="badge bg-danger ms-2">Deleted</span>' : ""}
                    </h5>

                    <p><span class="text-warning">${renderStars(review.rating)}</span></p>

                    <p><strong>From:</strong> ${review.reviewer_display_name || "Unknown user"}
                       (ID ${review.reviewer_id})</p>

                    <p><strong>About:</strong> ${review.reviewee_display_name || "Unknown user"}
                       (ID ${review.reviewee_id})</p>

                    <p><strong>Comment:</strong> ${review.comment ? review.comment : "<em>No comment</em>"}</p>

                    <p class="text-muted small">Posted ${new Date(review.created_at).toLocaleString()}</p>

                    <button
                        class="btn btn-danger delete-review-btn"
                        data-review-id="${review.id}"
                        ${review.is_deleted ? "disabled" : ""}>
                        ${review.is_deleted ? "Deleted" : "Delete Review"}
                    </button>
                </div>
            </div>
        `).join("");

        document.querySelectorAll(".delete-review-btn").forEach((button) => {
            button.addEventListener("click", async () => {
                const reviewId = button.dataset.reviewId;

                const confirmed = confirm(
                    "Remove this review from the marketplace? It will stay visible here as deleted."
                );

                if (!confirmed) {
                    return;
                }

                // Disable immediately so the button can't be double-clicked
                // while the request is in flight.
                button.disabled = true;

                try {
                    const response = await fetch(`/api/admin/reviews/${reviewId}/delete`, {
                        method: "PUT"
                    });

                    const result = await response.json();

                    if (!response.ok) {
                        alert(result.error || "Failed to delete review.");
                        button.disabled = false;
                        return;
                    }

                    button.textContent = "Deleted";
                    button.closest(".card").classList.add("border-danger");
                    const title = button.closest(".card").querySelector("h5");
                    if (title && !title.querySelector(".badge")) {
                        title.insertAdjacentHTML(
                            "beforeend",
                            ' <span class="badge bg-danger ms-2">Deleted</span>'
                        );
                    }
                } catch {
                    alert("Unable to delete review.");
                    button.disabled = false;
                }
            });
        });

    } catch {
        container.innerHTML = `
            <div class="alert alert-danger">
                Failed to load reviews.
            </div>
        `;
    }
});