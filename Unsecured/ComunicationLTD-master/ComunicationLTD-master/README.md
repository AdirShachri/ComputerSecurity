
                              
# Comunication LTD - Django Web Application

The project incorporates secure authentication, password management, and customer registration functionalities while implementing measures against common security vulnerabilities.

---

## Features

### **User Authentication**
- **Registration**
  - Allows users to create accounts.
  - Enforces strong password requirements (length, special characters, uppercase, lowercase).
  - Stores passwords using HMAC + Salt.
- **Login**
  - Supports user authentication with username and password.
  - Implements account lockout after 3 failed login attempts for 2 minutes.
  - Sends an account lockout notification email to users.
- **Password Reset**
  - Sends a password reset token (SHA-1) to the user's email.
  - Allows users to reset their password using the token.
  - Prevents reuse of the last 3 passwords.
- **Password Change**
  - Allows logged-in users to update their passwords.
  - Enforces strong password requirements.

### **Customer Management**
- Add new customers with details like name, email, and phone number.
- View a list of all registered customers.

### **Security Features**
- Passwords stored using HMAC + Salt.
- CSRF protection enabled by default.
- Protection against SQL injection using parameterized queries.
- Optional demonstration of SQL injection and XSS vulnerabilities for educational purposes.
- Countermeasures against XSS and SQL injection:
  - Use of Django's `safe` rendering only in specific cases.
  - Parameterized queries to prevent SQL injection.

---

## Installation

### Prerequisites
- Python 3.10+
- Virtual environment tool (e.g., `venv` or `virtualenv`)
- Django 3.2 or higher

### Steps
1. Clone the repository:
    ```bash
    git clone <repository_url>
    cd ComunicationLTD
    ```

2. Create and activate a virtual environment:
    ```bash
    python -m venv env
    source env/bin/activate  # On Windows: env\Scripts\activate
    ```


4. Apply database migrations:
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

5. Create a superuser account:
    ```bash
    python manage.py createsuperuser
    ```

6. Run the development server:
    ```bash
    python manage.py runserver
    ```

7. Access the application:
    Open your browser and navigate to `http://127.0.0.1:8000`.

---


## Usage

### Admin Panel
To access the admin panel:
1. Go to `http://127.0.0.1:8000/admin/`
2. Log in with the superuser credentials.

### User Features
- **Register:** Create an account.
- **Login:** Access the system.
- **Forgot Password:** Reset your password via email.
- **Change Password:** Update your password securely.
- **Customer Management:** Add and view customer information.




