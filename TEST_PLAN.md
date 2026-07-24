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

### Listings Module Test Plan - Irsyad (254573S)

### 1. Listings Management Test Plan

| Test ID | Description of test aim | Preconditions | Test Steps | Expected Results |
| :--- | :--- | :--- | :--- | :--- |
| **TC-LS-001** | Create listing successfully | User is authenticated | POST valid JSON to `/api/listings` | HTTP 201 Created |
| **TC-LS-002** | Reject incomplete listing | None | POST JSON missing mandatory fields | HTTP 400 Bad Request |
| **TC-LS-003** | Keyword search logic | Items exist in DB | GET `/api/listings?search=Physics` | Returns items matching keyword |
| **TC-LS-004** | Category filtering | Items exist in DB | GET `/api/listings?category=Electronics` | Returns items of specific category |
| **TC-LS-005** | Pagination limit (10/page) | >10 items exist | GET `/api/listings?page=1` | Returns exactly 10 items |
| **TC-LS-006** | Pagination remainder | >10 items exist | GET `/api/listings?page=2` | Returns remaining items |
| **TC-LS-007** | Update listing successfully | Valid listing exists | PUT valid JSON to `/api/listings/<id>` | HTTP 200 OK & Title updated |
| **TC-LS-008** | Soft delete functionality | Valid listing exists | DELETE to `/api/listings/<id>` | HTTP 200 OK & Item is hidden |
| **TC-LS-009** | Prevent edit of non-existent | None | PUT to invalid ID | HTTP 404 Not Found |
| **TC-LS-010** | Search empty result set | None | GET `/api/listings?search=Unknown` | HTTP 200 OK & Empty list |

### 2. Listings Security & Authorization Test Plan

| Test ID | Description of test aim | Preconditions | Test Steps | Expected Results |
| :--- | :--- | :--- | :--- | :--- |
| **TC-SEC-001** | Prevent unauthenticated listing creation | User is logged out | POST valid JSON to `/api/listings` | HTTP 401 Unauthorized |
| **TC-SEC-002** | Prevent unauthorized listing modification | User A logged in, Item owned by User B | PUT changes to `/api/listings/<user_b_item_id>` | HTTP 403 Forbidden |