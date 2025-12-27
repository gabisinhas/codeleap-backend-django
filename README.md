# CodeLeap Django Backend

A Django REST API built for the CodeLeap frontend challenge, providing CRUD operations for posts with authentication and security best practices.

---

## 🚀 Features
- Create, list, update, and delete posts
- Posts ordered by creation date
- JWT authentication
- Only the post author can edit or delete their posts
- CSRF protection enabled
- JSON-based API

---

## 📚 API Endpoints

| Method | Endpoint             | Description         |
|--------|----------------------|---------------------|
| POST   | `/createpost/`       | Create a post       |
| GET    | `/listposts/`        | List all posts      |
| PATCH  | `/editpost/<id>/`    | Edit a post         |
| DELETE | `/deletepost/<id>/`  | Delete a post       |
| GET    | `/csrf/`             | Get CSRF token      |

---

## ⚙️ Setup

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

## 🔐 Authentication
- Login via `/auth/login/` to obtain a JWT token.
- Send the token in requests:
  ```
  Authorization: Bearer <your_jwt_token>
  ```

---

## 📁 Project Structure
- `core/` – Models, views, serializers, and routes
- `codeleap_backend_django/` – Project settings

---

Developed for the CodeLeap challenge.
