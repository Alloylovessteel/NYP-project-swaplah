## Complete Dependency Inventory (pip freeze export)

| Component Name | Version | Ecosystem | Purpose / Usage in SwapLah |
| :--- | :--- | :--- | :--- |
| **astroid** | 3.0.3 | PyPI (Python) | Underlying parsing library used by Pylint for static code analysis. |
| **attrs** | 26.1.0 | PyPI (Python) | Classes without boilerplate; dependency for testing and tooling. |
| **blinker** | 1.9.0 | PyPI (Python) | Fast, simple object-to-object and signal-emitter signaling system for Flask. |
| **certifi** | 2026.7.22 | PyPI (Python) | Provides Mozilla's root certificates for validating SSL/TLS requests. |
| **cffi** | 2.1.0 | PyPI (Python) | Foreign Function Interface for Python calling C code. |
| **charset-normalizer** | 3.4.9 | PyPI (Python) | The Unicode Character Encoding Detector. |
| **click** | 8.4.1 | PyPI (Python) | Command line library used heavily under-the-hood by Flask. |
| **colorama** | 0.4.6 | PyPI (Python) | Cross-platform colored terminal text (used by pytest/pylint outputs). |
| **coverage** | 7.15.2 | PyPI (Python) | Measures code test coverage during pytest runs. |
| **dill** | 0.4.1 | PyPI (Python) | Serialization of python objects (supporting advanced pylint tasks). |
| **Flask** | 3.1.3 | PyPI (Python) | Core web application micro-framework. |
| **Flask-SQLAlchemy** | 3.1.1 | PyPI (Python) | Extension that adds SQLAlchemy support to Flask. |
| **greenlet** | 3.5.1 | PyPI (Python) | Lightweight in-process concurrent programming (SQLAlchemy async helper). |
| **h11** | 0.16.0 | PyPI (Python) | Pure-Python HTTP/1.1 protocol implementation. |
| **idna** | 3.18 | PyPI (Python) | Internationalized Domain Names in Applications (IDNA) support. |
| **iniconfig** | 2.3.0 | PyPI (Python) | Access to ini files for pytest configuration. |
| **isort** | 5.13.2 | PyPI (Python) | Python utility/library to sort imports automatically. |
| **itsdangerous** | 2.2.0 | PyPI (Python) | Safely sign data (used for session tokens and security in Flask). |
| **Jinja2** | 3.1.6 | PyPI (Python) | Full-featured template engine for Python, powering Flask HTML rendering. |
| **MarkupSafe** | 3.0.3 | PyPI (Python) | Safely add untrusted strings to HTML/XML (prevents XSS vulnerabilities). |
| **mccabe** | 0.7.0 | PyPI (Python) | McCabe complexity checker plugin for Pylint (enforces <10 complexity). |
| **outcome** | 1.3.0.post0 | PyPI (Python) | Capture the outcome of a function call (Trio ecosystem). |
| **packaging** | 26.2 | PyPI (Python) | Core utilities for Python packages. |
| **platformdirs** | 4.10.0 | PyPI (Python) | Determines appropriate platform-specific dirs (user cache, logs). |
| **pluggy** | 1.6.0 | PyPI (Python) | Plugin and hook calling mechanism for pytest. |
| **pycparser** | 3.0 | PyPI (Python) | C parser in Python (dependency of cffi). |
| **Pygments** | 22.0.0 | PyPI (Python) | Generic syntax highlighter. |
| **pylint** | 3.0.2 | PyPI (Python) | Static code analysis tool used in the CI pipeline for quality gates. |
| **PySocks** | 1.7.1 | PyPI (Python) | SOCKS proxy client module for Python. |
| **pytest** | 8.4.2 | PyPI (Python) | Testing framework for unit and API tests. |
| **pytest-cov** | 7.1.0 | PyPI (Python) | Pytest plugin for measuring test coverage percentage. |
| **python-dotenv** | 1.1.1 | PyPI (Python) | Reads key-value pairs from `.env` and adds them to environment variables. |
| **requests** | 2.34.2 | PyPI (Python) | HTTP library for Python. |
| **selenium** | 4.46.0 | PyPI (Python) | Web browser automation library for end-to-end UI testing. |
| **sniffio** | 1.3.1 | PyPI (Python) | Sniff out which async library your code is running under. |
| **sortedcontainers** | 2.4.0 | PyPI (Python) | Sorted container types. |
| **SQLAlchemy** | 2.0.50 | PyPI (Python) | The Python SQL Toolkit and Object Relational Mapper. |
| **tomlkit** | 0.15.0 | PyPI (Python) | Style-preserving TOML library for Python. |
| **trio** | 0.33.0 | PyPI (Python) | Friendly async/await concurrency library. |
| **trio-websocket** | 0.12.2 | PyPI (Python) | WebSocket library for Trio. |
| **typing_extensions** | 4.15.0 | PyPI (Python) | Backported type hints. |
| **urllib3** | 2.7.0 | PyPI (Python) | HTTP client with thread-safe connection pooling. |
| **webdriver-manager** | 4.1.2 | PyPI (Python) | Automated management of browser drivers (ChromeDriver) for Selenium. |
| **websocket-client** | 1.9.0 | PyPI (Python) | WebSocket client for Python. |
| **Werkzeug** | 3.1.8 | PyPI (Python) | Comprehensive WSGI web application library powering Flask's request/response objects. |
| **wsproto** | 1.3.2 | PyPI (Python) | WebSockets protocol state machine. |

---

## Data Storage & Environment
* **Database Engine:** SQLite (Local file `swaplah.db` for production/dev; in-memory `sqlite:///:memory:` for testing).
* **Frontend Layer:** HTML5, CSS3, Bootstrap 5 (CDN), and vanilla JavaScript.
* **CI/CD Platform:** GitLab CI/CD (Executing automated linting, unit tests, API tests, and UI tests).