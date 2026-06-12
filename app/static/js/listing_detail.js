document.addEventListener("DOMContentLoaded", async () => {
    const container = document.getElementById("detailContainer");

    try {
        const response = await fetch(`/api/listings/${LISTING_ID}`);
        if (!response.ok) throw new Error("Item not found");

        const item = await response.json();

        // 1. Authorization Logic (Mocked for Week 8)
        // We assume User ID 1 is the 'Logged In' user until Shamreen merges Auth
        const isOwner = item.seller_id === 1;

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
                        <p class="mb-1"><strong>Email:</strong> <a href="mailto:${item.seller_info ? item.seller_info.email : ""}">${item.seller_info ? item.seller_info.email : "N/A"}</a></p>
                        <p class="mb-0"><strong>Phone:</strong> ${item.seller_info ? item.seller_info.contact_number : "N/A"}</p>
                    </div>
                </div>
                
                <div class="mt-4 d-grid gap-2">
                    <button class="btn btn-primary btn-lg">Make an Offer</button>

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

            </div>
        `;

        const reportButton =
            document.getElementById("submitReportBtn");

        if (reportButton) {

            reportButton.addEventListener(
                "click",
                async () => {

                    const reason =
                        document.getElementById("reportReason").value;

                    const description =
                        document.getElementById("reportDescription").value;

                    if (!reason || !description.trim()) {

                        alert(
                            "Please provide a reason and description."
                        );

                        return;
                    }

                    try {

                        const response = await fetch(
                            "/api/reports",
                            {
                                method: "POST",

                                headers: {
                                    "Content-Type": "application/json"
                                },

                                body: JSON.stringify({
                                    listing_id: item.id,
                                    reason,
                                    description
                                })
                            }
                        );

                        const result =
                            await response.json();

                        if (response.ok) {

                            alert(result.message);

                            location.reload();

                        } else {

                            alert(
                                result.error ||
                                "Failed to submit report."
                            );
                        }

                    } catch {

                        alert(
                            "Unable to submit report."
                        );
                    }
                }
            );
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
