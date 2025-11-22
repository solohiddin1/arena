Arena — Simple setup and registration guide
=========================================

This README explains how to set up and run the Django project locally and how to register a user using the API. The instructions are written for someone who is not familiar with Python.

Prerequisites
-------------
- A recent Linux or macOS machine (the project was developed on Linux).
- Python 3.11 installed. Verify with:

```bash
python --version
```

- Git (optional, for cloning the repository).

Quick setup (step-by-step)
--------------------------

1. Open a terminal and change to the project folder. If you cloned the repo, `cd` into it. Example:

```bash
cd ~/files/arena
```

2. Create a Python virtual environment (this keeps dependencies isolated):

```bash
python -m venv venv
```

3. Activate the virtual environment:

```bash
# If using zsh or bash
source venv/bin/activate
```

4. Install required Python packages:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

5. Configure environment variables (email, secret key, etc.)

This project reads settings from `config/config.py`. If the repository includes an example config (like `.env.example`), copy it and edit. Otherwise, ensure the following are set as environment variables in your shell or create a `config/config.py` with appropriate values.

- Minimum values to set as environment variables:
  - `SECRET_KEY` — Django secret key (any long random string for development)
  - `DEBUG` — `True` for development
  - Email settings if you want to send OTP emails: `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS`

You can set them in the shell like this (development only):

```bash
export SECRET_KEY='dev-secret-key'
export DEBUG=True
# Example SMTP settings (only if you want emails to be sent):
export EMAIL_HOST='smtp.example.com'
export EMAIL_PORT=587
export EMAIL_HOST_USER='you@example.com'
export EMAIL_HOST_PASSWORD='yourpassword'
export EMAIL_USE_TLS=True
```

6. Apply database migrations:

```bash
python manage.py migrate
```

7. (Optional) Create a superuser to access the admin site:

```bash
python manage.py createsuperuser
```

8. Run the development server:

```bash
python manage.py runserver
```

The server will be available at `http://127.0.0.1:8000/` by default.

How to register a user (API)
----------------------------

The project exposes a registration endpoint at `/api/user/auth/register/` (POST). The endpoint expects JSON. Below is a minimal example using `curl`.

Example request:

```bash
curl -X POST http://127.0.0.1:8000/api/user/auth/register/ \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "user@example.com",
    "password": "yourpassword",
    "first_name": "John",
    "lang": "UZ"
  }'
```

If registration succeeds the API will return a JSON response that includes the user's `id`, `email`, and other info, and an OTP (if email OTP flow is enabled). The server may send an email with an OTP code to the provided email address; check the server logs if the SMTP settings are not configured.

Troubleshooting common issues
-----------------------------
- IntegrityError on `users_user.username`: If you see an error about a UNIQUE constraint for `username`, it means a user was created without a unique `username`. Workarounds:
  - Use the provided registration endpoint (it now sets `username` for you).
  - If you create users manually, ensure the `username` is unique (e.g., set it to the same value as `email`).

- Email not delivered: For development you can skip SMTP configuration and check the server console for the OTP code, or configure a real SMTP account.

- I don't know Python: follow these exact commands in the terminal. Activate the virtualenv first before running `manage.py` commands.

Useful commands summary
-----------------------
- Activate virtualenv: `source venv/bin/activate`
- Install deps: `pip install -r requirements.txt`
- Migrate DB: `python manage.py migrate`
- Run server: `python manage.py runserver`
- Create superuser: `python manage.py createsuperuser`

If you'd like, I can also add a `.env.example` file and a short script to set environment variables for development. Let me know which option you prefer.

---
Small note: This README contains minimal development steps — do not use these settings in production as-is (especially `DEBUG` and plain SMTP credentials). If you need a production-ready guide, I can expand the instructions.
