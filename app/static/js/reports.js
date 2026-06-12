document.addEventListener(
    "DOMContentLoaded",
    async () => {

        const container =
            document.getElementById(
                "reportsContainer"
            );

        try {

            const response =
                await fetch(
                    "/api/admin/reports"
                );

            const reports =
                await response.json();

            if (reports.length === 0) {

                container.innerHTML = `
                    <div class="alert alert-info">
                        No reports found.
                    </div>
                `;

                return;
            }

            container.innerHTML = reports.map(
                report => `
                    <div class="card mb-3">
                        <div class="card-body">
                            <h5>
                                Report #${report.id}
                            </h5>

                            <p>
                                <strong>Reason:</strong>
                                ${report.reason}
                            </p>

                            <p>
                                <strong>Description:</strong>
                                ${report.description}
                            </p>

                            <p>
                                <strong>Listing ID:</strong>
                                ${report.listing_id}
                            </p>

                            <p>
                                <strong>Listing ID:</strong>
                                ${report.listing_id}
                            </p>

                            <button
                                class="btn btn-danger delete-listing-btn"
                                data-listing-id="${report.listing_id}">
                                Remove Listing
                            </button>

                            <button
                                class="btn btn-secondary dismiss-report-btn"
                                data-report-id="${report.id}">
                                Dismiss Report
                            </button>
                        </div>
                    </div>
                `
            ).join("");

            document
                .querySelectorAll(".delete-listing-btn")
                .forEach(button => {

                    button.addEventListener(
                        "click",
                        async () => {

                            const listingId =
                                button.dataset.listingId;

                            const confirmed =
                                confirm(
                                    "Are you sure you want to remove this listing?"
                                );

                            if (!confirmed) {
                                return;
                            }

                            try {

                                const response =
                                    await fetch(
                                        `/api/listings/${listingId}`,
                                        {
                                            method: "DELETE"
                                        }
                                    );

                                const result =
                                    await response.json();

                                if (response.ok) {

                                    alert(
                                        result.message
                                    );

                                    location.reload();

                                } else {

                                    alert(
                                        result.error ||
                                        "Failed to remove listing."
                                    );
                                }

                            } catch {

                                alert(
                                    "Unable to remove listing."
                                );
                            }
                        }
                    );

                });

            document
                .querySelectorAll(".dismiss-report-btn")
                .forEach(button => {

                    button.addEventListener(
                        "click",
                        async () => {

                            const reportId =
                                button.dataset.reportId;

                            try {

                                const response =
                                    await fetch(
                                        `/api/admin/reports/${reportId}`,
                                        {
                                            method: "DELETE"
                                        }
                                    );

                                const result =
                                    await response.json();

                                alert(result.message);

                                location.reload();

                            } catch {

                                alert(
                                    "Failed to dismiss report."
                                );
                            }
                        }
                    );
                });
                
        } catch {

            container.innerHTML = `
                <div class="alert alert-danger">
                    Failed to load reports.
                </div>
            `;
        }
    }
);