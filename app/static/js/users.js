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
                                </tr>
                            `
            ).join("")}

                    </tbody>

                </table>
            `;

        } catch {

            container.innerHTML = `
                <div class="alert alert-danger">
                    Failed to load users.
                </div>
            `;
        }
    }
);