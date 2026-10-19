
# ✳ BLOOM. — Social Media Platform

### Connect. Share. Grow.

BLOOM is a modern social media web application developed using Django as part of the CodeAlpha Full Stack Development Internship.

The platform provides a welcoming space where users can share moments, discover people, and build meaningful connections.

## ✨ Features

- User registration, login, and logout
- Personalized user profiles with bios and profile pictures
- Create posts with text and images
- Interactive feed displaying recent posts
- Like and comment on posts
- Follow and unfollow other users
- Explore community members
- Search for users by name or username
- Responsive user interface
- Django administration panel

## 🛠 Technologies Used

- Python
- Django
- HTML5
- CSS3
- SQLite
- Pillow
- Git and GitHub

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Aline302/codealpha_tasks.git
cd codealpha_tasks/Task-2-Social-Media
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 5. Configure environment variables

Create a `.env` file in the project root:

```dotenv
DJANGO_SECRET_KEY=your-generated-django-secret-key
DJANGO_DEBUG=True
```

Generate a secret key with:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 6. Apply migrations

```bash
python manage.py migrate
```

### 7. Run the application

```bash
python manage.py runserver
```

Visit:

http://127.0.0.1:8000/

## 📸 Screenshots

Screenshots of the application will be added to the `screenshots/` directory.

## 🌸 About the Project

BLOOM combines essential social networking functionality with a clean, modern, pastel-inspired interface.

The application was built to demonstrate full-stack web development, database management, authentication, and interactive user experiences.

## 👩‍💻 Developer

Aline Charafeddine

Software Engineering Student

CodeAlpha — Full Stack Development Internship

October 2026
