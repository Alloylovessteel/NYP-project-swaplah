document.addEventListener(
    "DOMContentLoaded",
    async () => {

        const container =
            document.getElementById(
                "usersContainer"
            );

        try {

            const response =
                await fetch(
                    "/api/admin/users"
                );

            const users =
                await response.json();

            if (users.length === 0) {

                container.innerHTML = `
                    <div class="alert alert-info">
                        No users found.
                    </div>
                `;

                return;
            }

            container.innerHTML = `
                <table class="table table-striped">

                    <thead>
                        <tr>
                            <th>Student ID</th>
                            <th>Display Name</th>
                            <th>Email</th>
                            <th>Status</th>
                            <th>Action</th>
                        </tr>
                    </thead>

                    <tbody>

                        ${users.map(
                user => `
                                <tr>
                                    <td>${user.student_id}</td>
                                    <td>${user.display_name}</td>
                                    <td>${user.email}</td>
                                    <td>${user.account_status}</td>
                                    <td>
                                        ${
                                            user.account_status === "active"
                                            ?
                                            `<button
                                                class="btn btn-danger suspend-btn"
                                                data-id="${user.id}">
                                                Suspend
                                            </button>`
                                            :
                                            `<button
                                                class="btn btn-success unsuspend-btn"
                                                data-id="${user.id}">
                                                Unsuspend
                                            </button>`
                                        }
                                    </td>
                                </tr>
                            `
            ).join("")}

                    </tbody>

                </table>
            `;

            document
                .querySelectorAll(".suspend-btn")
                .forEach(button => {

                    button.addEventListener(
                        "click",
                        async () => {

                            const userId =
                                button.dataset.id;

                            await fetch(
                                `/api/admin/users/${userId}/suspend`,
                                {
                                    method: "PUT"
                                }
                            );

                            location.reload();
                        }
                    );
                });

            document
                .querySelectorAll(".unsuspend-btn")
                .forEach(button => {

                    button.addEventListener(
                        "click",
                        async () => {

                            const userId =
                                button.dataset.id;

                            await fetch(
                                `/api/admin/users/${userId}/unsuspend`,
                                {
                                    method: "PUT"
                                }
                            );

                            location.reload();
                        }
                    );
                });

        } catch {

            container.innerHTML = `
                <div class="alert alert-danger">
                    Failed to load users.
                </div>
            `;
        }
    }
);