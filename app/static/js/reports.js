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
                        </div>
                    </div>
                `
            ).join("");

        } catch {

            container.innerHTML = `
                <div class="alert alert-danger">
                    Failed to load reports.
                </div>
            `;
        }
    }
);