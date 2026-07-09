# SwapLah Test Plan

## User Accounts - Shamreen Rizmiya (241011Z)

| Test ID | Feature | Description | Precondition | Steps | Expected Result |
|---------|---------|-------------|--------------|-------|-----------------|
| TC01 | Registration | Valid registration with NYP email | None | POST /api/register with valid NYP email and all fields | Returns 201, user created |
| TC02 | Registration | Non-NYP email rejected | None | POST /api/register with gmail.com email | Returns 400, "Only NYP email addresses are accepted" |
| TC03 | Registration | Missing required field | None | POST /api/register without password field | Returns 400, "Field 'password' is required" |
| TC04 | Registration | Duplicate email rejected | User already registered | POST /api/register with same email again | Returns 400, "Email already registered" |
| TC05 | Login | Valid login | User registered | POST /api/login with correct email and password | Returns 200, login successful |
| TC06 | Login | Wrong password rejected | User registered | POST /api/login with correct email, wrong password | Returns 401, "Invalid email or password" |
| TC07 | Login | Suspended account blocked | User suspended | POST /api/login with correct credentials | Returns 403, "Your account has been suspended" |
| TC08 | Session | Access protected route without login | Not logged in | GET /api/profile without session | Returns 401, "Unauthorized" |
| TC09 | View Profile | View own profile when logged in | User logged in | GET /api/profile | Returns 200 with user details |
| TC10 | Edit Profile | Update display name and contact | User logged in | PUT /api/profile with new display name | Returns 200, profile updated |
| TC11 | Edit Profile | Email cannot be changed | User logged in | PUT /api/profile with new email | Email remains unchanged |
| TC12 | Logout | Valid logout | User logged in | POST /api/logout | Returns 200, session cleared |