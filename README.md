# SwapLah

SwapLah is a web-based student co-op marketplace where NYP students can buy, sell, and swap pre-owned items such as textbooks, lab equipment, electronics, stationery, and clothing.

Built with Flask (backend), SQLite (database), and Bootstrap (frontend), as part of IT2112 26S1.

## Team

**Team 1** - IT2112-07

## Tech Stack

- **Backend:** Python 3.9, Flask
- **Database:** SQLite (via Flask-SQLAlchemy)
- **Frontend:** HTML5, Bootstrap
- **Testing:** Pytest (unit + API), Selenium (UI)
- **CI/CD:** GitLab Pipelines (lint, test, security scan)

## Getting Started

### Prerequisites
- Python 3.9+
- pip

### Installation

```bash
git clone https://gitlab.com/nyp-sg/pet/it2112/26s1/it2112-07/assignment/team_1/swaplah.git
cd swaplah
pip install -r requirements.txt
```

### Running the app

```bash
python run.py
```

The app runs at `http://127.0.0.1:5000`.

### Running tests

```bash
python -m pytest tests/unit/
python -m pytest tests/api/
```

### Environment variables

Copy `.env.example` to `.env` and fill in any required secrets before running the app.

## Features

| Module | Description | Owner |
|---|---|---|
| User Accounts | Registration, login/logout, session timeout, view/edit profile | Shamreen (241011Z) |
| Item Listings | Create, browse, search, filter, edit, soft-delete listings | Irsyad |
| Offers & Transactions | Submit offers, accept/reject, transaction history | Ashlyn |
| Reviews & Ratings | Star ratings and comments after completed transactions | Aloysius |
| Reporting & Admin | Report listings, admin review, suspend users | Nann |

---

## Module: User Accounts

Handles student registration, authentication, session management, and profile management.

### Endpoints

| Method | Endpoint | Description | Auth required |
|---|---|---|---|
| POST | `/api/register` | Register a new student account | No |
| POST | `/api/login` | Log in and start a session | No |
| POST | `/api/logout` | Clear the current session | No |
| GET | `/api/profile` | View the logged-in user's profile | Yes |
| PUT | `/api/profile` | Edit the logged-in user's profile | Yes |

### Business rules

- Only NYP email addresses (`*.nyp.edu.sg`) are accepted at registration.
- Passwords are hashed with Werkzeug's `generate_password_hash` - never stored in plaintext.
- Duplicate `email` or `student_id` at registration is rejected.
- `email` and `student_id` cannot be changed via the edit profile endpoint.
- Sessions are marked permanent and expire after 30 minutes of inactivity (`PERMANENT_SESSION_LIFETIME`).
- Suspended accounts (`account_status = 'suspended'`) cannot log in.

### Example: Register

```json
POST /api/register
{
  "student_id": "S1234567",
  "first_name": "Jane",
  "last_name": "Tan",
  "display_name": "Jane T",
  "email": "jane.tan@nyp.edu.sg",
  "contact_number": "91234567",
  "password": "SecurePass123!"
}
```

Response `201`:
```json
{ "message": "Registration successful" }
```

### Example: Login

```json
POST /api/login
{
  "email": "jane.tan@nyp.edu.sg",
  "password": "SecurePass123!"
}
```

Response `200`:
```json
{ "message": "Login successful", "user_id": 1 }
```

### Tests

- `tests/unit/test_registration.py` - email validation, password hashing, duplicate detection
- `tests/unit/test_login.py` - password verification, account status defaults
- `tests/api/test_registration_api.py` - registration endpoint, positive + negative cases
- `tests/api/test_login_api.py` - login/logout endpoint, positive + negative cases
- `tests/api/test_view_profile_api.py` - view profile, auth enforcement
- `tests/api/test_edit_profile_api.py` - edit profile, field-level restrictions
- `tests/api/test_session_timeout_api.py` - session timeout configuration and enforcement

---

## Definition of Done (DoD)

- [ ] **Feature Branch:** Code is pushed to a dedicated feature branch, not `main`.
- [ ] **Code Quality:** All Python code passes Pylint (score >= 7.0).
- [ ] **Testing:** Unit, API, and UI tests are developed and passing in the CI/CD pipeline.
- [ ] **AI Transparency:** AI usage is logged in `AI/<student_id>_AI_LOG.md` with prompt and rationale.
- [ ] **Peer Review:** Merge Request (MR) is created, reviewed, and approved by at least one other team member.
- [ ] **Validation:** All Acceptance Criteria (AC) for the issue are verified and ticked.
- [ ] **Regression Testing:** No regression; existing features are confirmed to work.
- [ ] **Closure:** Issue is moved to "Done" on the GitLab board and MR is merged to `main`.
