![Videoflix Logo](app_auth/logo/app_auth/logo_icon.png)

# Backend Project Videoflix - Netflix clone

This is the backend for a Django REST API application.  
The project is based on Django and Django REST Framework and uses a classic app structure (e.g. app_auth, ...).  

Videoflix is a streaming platform for videos, taking inspiration from Netflix. Users can create accounts, verify their email to activate their profiles, reset passwords if forgotten, and enjoy videos at multiple resolutions with adjustable playback speeds in the built-in player.

This repository hosts the backend of the application, developed using Django and Django REST Framework, leveraging JWT for authentication and ffmpeg for video processing and encoding.


### Features

- **User Authentication**: Register, login, and logout functionality with HttpOnly Cookies
- **Email verification and account activation**: Mails send to user when user registers, and account activation is required.
- **Reset Password**: Password reset via email with secure token
- **Video conversion**: Video conversion to multiple resolutions
- **Video Streaming**: Video streaming with HLS and DASH formats

---

## Project Structure

```
backend-quizly/
│
├── core/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── app_auth/
│   ├── __init__.py
│   ├── models.py
│   ├── api/
│   │   ├── authentications.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── utils.py
│   ├── api/
│   │   ├── logo_icon.png
│   │   └── logo_icon.svg
│   ├── templates/
│   │   ├── confirm_account.html
│   │   ├── confirm_account.txt
│   │   ├── reset_password.html
│   │   ├── reset_password.txt
│   │   ├── welcome_message.html
│   │   └── welcome_message.txt
│   └── tests/
│       ├── test_login.py
│       ├── test_email.py
│       ├── test_cookies.py
│       └── test_registration.py
│
├── app_videos/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── signals.py
│   ├── tasks.py
│   ├── api/
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── permissions.py
│   │   └── urls.py
│   └── tests/
│       ├── __init__.py
│       ├── test_quizCreate.py
│       └── test_quizzes.py
│
├── media/
│   └── temp/
│
├── .coveragerc
├── .dockerignore
├── backend.Dockerfile
├── backend.entrypoint.sh
├── conftest.py
├── docker-compose.yml
├── requirements.txt
├── manage.py                    
├── pytest.ini
└── .env
```

---

## Environment Setup

Create a .env file in the root folder with the following variables:

```
SECRET_KEY=yourSecretDjangoKey
DEBUG=True

DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_PASSWORD=adminpassword
DJANGO_SUPERUSER_EMAIL=admin@example.com

FRONTEND_URL=http://127.0.0.1:5500

ALLOWED_HOSTS=127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500

DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=db
DB_PORT=5432

REDIS_HOST=redis
REDIS_LOCATION=redis://redis:6379/1
REDIS_PORT=6379
REDIS_DB=0

EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email_user
EMAIL_HOST_PASSWORD=your_email_user_password
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
DEFAULT_FROM_EMAIL=default_from_email
```

Make sure to replace placeholders with your actual keys.

---

## Requirements

- Python 3.13+
- FFmpeg (für yt-dlp/Whisper)
- Docker ([install Docker](https://docs.docker.com/get-docker/))

---

## Install Dependencies

All required Python packages are listed in requirements.txt.
They include Django, DRF, JWT authentication, DRF Spectacular (Swagger/OpenAPI),

---

## Install / Activate Environment & install Packages

```
python -m venv venv
source venv/bin/activate  # Linux / Mac
venv\Scripts\activate     # Windows
```

```
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Run Using Docker Compose

Make sure Docker Desktop (or your Docker application) is running.

To build the images and start the containers for the first time:
```
docker-compose up --build
```

To start the containers without rebuilding (useful after the first build):
```
docker-compose up
```

The backend will be exposed on http://localhost:8000.

---

## Database

For production and containerized environments, the project uses PostgreSQL as the database backend. The Docker image includes postgresql-client and postgresql-dev packages, ensuring compatibility with PostgreSQL services.

PostgreSQL provides powerful and reliable relational database support, including advanced features like concurrency, robust data integrity, and scalability, making it ideal for production use.

The Docker setup installs necessary PostgreSQL client libraries to connect seamlessly to a dedicated PostgreSQL container or server, allowing efficient database management in a fully containerized deployment.

This setup ensures a smooth transition from lightweight SQLite development databases to full-featured PostgreSQL production databases with minimal configuration changes.

---

## Running Tests

Tests are written using pytest and pytest-django.

# Run all tests
Start your docker container
```
docker-compose up
```
```
docker-compose run --rm test  
```

---

## API Documentation

Swagger/OpenAPI documentation is automatically generated using drf-spectacular.

Once the server is running, you can access it at:

http://localhost:8000/schema/
http://localhost:8000/swagger/
http://localhost:8000/redoc/

---

## License

MIT License – see [LICENSE](LICENSE)  