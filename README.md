# Secure File Sharing Application - README

## Overview

This is a **Secure File Sharing Application** designed for safe and efficient file storage and sharing developed as a part of Interview process at Abnormal Security. It incorporates user authentication, role-based access control, and file encryption for maximum security. Built using **Django** (back-end), and **SQLite** (database), the application adheres to production-ready security practices.

---

## Features

1. **User Authentication**
   - Secure login and registration with email verification.
   - Multi-factor authentication (MFA) for added security.

2. **Role-Based Access Control (RBAC)**
   - Permissions and roles to control access to sensitive operations.

3. **File Upload and Encryption**
   - AES-256 encryption of uploaded files.
   - Files stored securely with metadata for integrity verification.

4. **Secure File Sharing**
   - Role-based file sharing with specific users.
   - Integrity checks for file downloads.

5. **Audit Logging**
   - Track file uploads, downloads, and sharing activities.

6. **Real-Time Collaboration**
   - Notifications for shared files.
   - User-based activity feeds.

---

## Tech Stack

### Backend
- **Django**
  - Authentication and permissions.
  - File encryption using a custom utility.
  - REST API endpoints for front-end integration.

- **SQLite**
  - Default database for development purposes.

### Frontend
- **HTML, CSS, JS**
  - Django's built-in template engine to render HTML pages dynamically. Templates are located in the templates directory and are styled using CSS for responsive and user-friendly design.

### Others
- **AES-256 Encryption**
  - Ensures file confidentiality and integrity.

- **Docker (optional)**
  - Containerized deployment.

---

## Setup Instructions

### Prerequisites
1. Python 3.10 or later
2. Node.js and npm
3. SQLite (pre-installed with Python)
4. Virtual environment tools (e.g., `venv`)

### Backend Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/secure-file-sharing.git
   cd secure-file-sharing
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

6. Start the development server:
   ```bash
   python manage.py runserver
   ```
---

## Key Endpoints

### Authentication
- **POST** `/register/` - User registration
- **POST** `/login/` - User login
- **POST** `/logout/` - User logout

### File Operations
- **GET** `/files/` - List uploaded files
- **POST** `/files/upload/` - Upload files
- **POST** `/files/share/<file_id>/` - Share files with specific users
- **GET** `/files/download/<file_id>/` - Download files

### Admin
- **GET** `/admin/` - Admin panel for user and file management.

---

## Security Measures
1. **Authentication**
   - Secure password hashing using Django's built-in `PBKDF2`.

2. **Encryption**
   - Files encrypted with AES-256 before storage.
   - Integrity verified on every download.

3. **Input Validation**
   - Strict validation for form submissions and APIs.

4. **Session Management**
   - Secure cookies and CSRF protection.

5. **Role-Based Permissions**
   - Granular access control with Django's `permission_required`.

---

## Deployment (Optional with Docker)
1. Build the Docker containers:
   ```bash
   docker-compose build
   ```

2. Start the application:
   ```bash
   docker-compose up
   ```

3. Access the application:
   - `http://localhost:8000`

---
