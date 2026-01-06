# RentalApp API (Django)

A production-oriented REST API for a short-term housing rental platform in Germany.

---

## Project Goals

- Provide a full-featured backend for a rental marketplace
- Model real-world booking and review workflows
- Enforce strict business rules and role-based permissions
- Serve as a portfolio-ready, production-like backend project

---

## Core Features

- User registration and authentication (JWT, HttpOnly cookies)
- Role-based access:
  - **Tenant** — book properties, leave reviews
  - **Owner** — manage listings, confirm bookings
  - **Admin** — platform administration
- Property listings:
  - Full CRUD for owners
  - Search and filtering by city, price, housing type
- Booking system:
  - Date validation and overlap protection
  - Confirmation flow (pending → confirmed / cancelled)
  - Owners cannot book their own listings
- Reviews and ratings:
  - Allowed **only after completed bookings**
  - One review per listing per user
- Favorites (wishlist)
- Listing view history and popularity tracking

---

## Business Logic Highlights

- Confirmed bookings block date ranges
- Pending bookings do not block availability
- Reviews require verified stays
- Addresses follow German validation rules:
  - ZIP code format
  - City name validation
  - Federal states as enums
- Permissions enforced at both API and domain levels

---

## 🛠 Tech Stack

- **Python 3.13**
- **Django 5.x**
- **Django REST Framework**
- **MySQL 8.0**
- **Simple JWT** (cookie-based authentication)
- **drf-spectacular** (OpenAPI / Swagger)
- **Docker & Docker Compose**
- **AWS EC2** (deployment-ready)

---

## Project Structure
```
RentalApp/
├── core/ # Shared logic, enums, validators
├── users/ # User model, authentication, favorites
├── listings/ # Listings, addresses, amenities, history
├── bookings/ # Booking workflows and status logic
├── reviews/ # Reviews and ratings
├── RentalApp/ # Project settings and URLs
├── .env      # Not in git
├── .env.example
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── factory_data.py # Test data generator
```
---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/RentalApp.git
cd RentalApp
```

### 2. Create virtual environment & install dependencies

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or .venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 3. Environment variables

**Create a .env file:**
```
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

MYSQL_DATABASE=rentdb
MYSQL_USER=rentuser
MYSQL_PASSWORD=your_password
MYSQL_ROOT_PASSWORD=your_root_password
MYSQL_HOST=localhost
MYSQL_PORT=3306
```

### 4. Run migrations and Docker

```bash
docker-compose up -d
python manage.py migrate
python manage.py createsuperuser
python factory_data.py
```

### 5. Start server


```
python manage.py runserver
```

## API Documentation

### All endpoints, request schemas, and authentication flows are documented via Swagger.

Swagger UI: http://127.0.0.1:8000/api/docs/

Admin panel: http://127.0.0.1:8000/admin/

## Authentication & Security

- JWT access & refresh tokens

- Tokens stored in HttpOnly cookies

- Protection against XSS

- Role-based permissions for all critical actions

## Testing
```
python manage.py test
```

### Test coverage includes:

- Users and authentication

- Listings and permissions

- Booking workflows

- Reviews and validation rules

## Deployment

The application is fully containerized and ready for deployment on AWS EC2.

### AWS EC2 Setup

1. **Launch EC2 instance**
   - AMI: Amazon Linux 2023
   - Instance type: t2.micro (free tier)
   - Security Group: ports 22, 80, 8000

2. **Install Docker on server**
```bash
sudo yum install docker -y
sudo service docker start
sudo usermod -aG docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

3. **Deploy application**
```bash
cd /opt/RentalApp
# Create .env with DEBUG=False and ALLOWED_HOSTS=
sudo docker-compose up -d --build
