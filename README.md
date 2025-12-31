# Doctor Appointment Management API

A production-ready RESTful API for managing doctor appointments with full authentication and role-based access control (RBAC).

## 🛠 Tech Stack

- **Language**: Python 3.12+ with modern type hinting
- **Web Framework**: FastAPI
- **Database**: PostgreSQL (via Docker)
- **ORM**: SQLAlchemy (Async)
- **Authentication**: JWT (JSON Web Tokens)
- **Testing**: Pytest with async support

## 📋 Features

### Authentication & Authorization
- User registration (Doctor / Patient)
- Login with JWT token generation
- Forgot password (mock flow)
- Secure API endpoints with JWT authentication
- Role-based access control (RBAC)

### Doctor Operations
- Set availability (time slots)
- View upcoming appointments

### Patient Operations
- List all doctors
- View doctor availability
- Book appointments (with double-booking prevention)
- Cancel own appointments

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Docker and Docker Compose
- pip

### Setup Instructions

1. **Clone the repository**
```bash
git clone <repository-url>
cd final_assesment
```

2. **Create environment file**

Create a `.env` file in the root directory with the following configuration:
```bash
# Database Configuration
DATABASE_URL=postgresql+asyncpg://appointment_user:appointment_pass@localhost:5432/appointment_db

# JWT Configuration
SECRET_KEY=your-secret-key-change-in-production-use-a-long-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Important**: Replace `your-secret-key-change-in-production-use-a-long-random-string` with a strong, random secret key for production use.

3. **Start PostgreSQL database with Docker**
```bash
docker-compose up -d
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Run the application**
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

6. **Access API documentation**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🧪 Running Tests

```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

## 📡 API Endpoints

### Authentication

#### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "email": "doctor@example.com",
  "password": "securepassword123",
  "role": "Doctor",
  "name": "Dr. John Doe"
}
```

#### Login
```http
POST /auth/login
Content-Type: application/json

{
  "email": "doctor@example.com",
  "password": "securepassword123"
}
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Forgot Password (Mock)
```http
POST /auth/forgot-password
Content-Type: application/json

{
  "email": "doctor@example.com"
}
```

### Doctors

#### List All Doctors
```http
GET /doctors
Authorization: Bearer <token>
```

#### Get Doctor Availability
```http
GET /doctors/{doctor_id}/availability
Authorization: Bearer <token>
```

#### Set Availability (Doctor Only)
```http
POST /doctors/availability
Authorization: Bearer <doctor_token>
Content-Type: application/json

{
  "start_time": "2024-01-15T09:00:00Z",
  "end_time": "2024-01-15T17:00:00Z"
}
```

#### Get Upcoming Appointments (Doctor Only)
```http
GET /doctors/appointments/upcoming
Authorization: Bearer <doctor_token>
```

### Appointments

#### Book Appointment (Patient Only)
```http
POST /appointments
Authorization: Bearer <patient_token>
Content-Type: application/json

{
  "doctor_id": 1,
  "availability_id": 1,
  "appointment_time": "2024-01-15T10:00:00Z"
}
```

#### Get My Appointments
```http
GET /appointments/my-appointments
Authorization: Bearer <token>
```

#### Cancel Appointment (Patient Only)
```http
POST /appointments/{appointment_id}/cancel
Authorization: Bearer <patient_token>
```

## 🏗 Architecture

### Project Structure
```
final_assesment/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration settings
│   ├── database.py           # Database connection and session management
│   ├── models.py             # SQLAlchemy models
│   ├── schemas.py            # Pydantic schemas for request/response validation
│   ├── middleware/
│   │   ├── __init__.py
│   │   └── auth_middleware.py  # JWT authentication and RBAC middleware
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── user_repository.py
│   │   ├── availability_repository.py
│   │   └── appointment_repository.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py      # Authentication logic
│   │   ├── doctor_service.py    # Doctor business logic
│   │   └── patient_service.py   # Patient business logic
│   └── routers/
│       ├── __init__.py
│       ├── auth.py              # Authentication endpoints
│       ├── doctors.py            # Doctor endpoints
│       └── appointments.py       # Appointment endpoints
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Pytest fixtures
│   ├── test_auth.py          # Authentication tests
│   ├── test_doctors.py       # Doctor service tests
│   └── test_appointments.py # Appointment booking tests
├── docker-compose.yml        # PostgreSQL database setup
├── requirements.txt          # Python dependencies
├── pytest.ini               # Pytest configuration
└── README.md
```

### Design Patterns

#### Service/Repository Pattern
The application follows a clean architecture with clear separation of concerns:

- **Repositories**: Handle all database operations (CRUD)
- **Services**: Contain business logic and orchestrate repository calls
- **Routers**: Handle HTTP requests/responses and delegate to services

#### Authentication Flow

1. **Registration**:
   - User provides email, password, role, and name
   - Password is hashed using bcrypt
   - User is created in database

2. **Login**:
   - User provides email and password
   - Password is verified against stored hash
   - JWT token is generated with user info (email, user_id, role)
   - Token is returned to client

3. **Protected Endpoints**:
   - Client includes JWT token in `Authorization: Bearer <token>` header
   - Middleware validates token and extracts user information
   - Role-based access control checks user permissions

#### RBAC Design

The system implements role-based access control with two roles:

- **Doctor**: Can set availability and view appointments
- **Patient**: Can view doctors, check availability, and book/cancel appointments

Access control is enforced at the middleware level using the `require_role` decorator:

```python
@router.post("/doctors/availability")
async def set_availability(
    ...,
    current_user: dict = Depends(require_role([UserRole.DOCTOR]))
):
    # Only doctors can access this endpoint
```

### Security Features

1. **Password Hashing**: Uses bcrypt with automatic salting
2. **JWT Tokens**: Secure token-based authentication
3. **Token Expiration**: Configurable token expiration time
4. **Input Validation**: Pydantic schemas validate all requests
5. **SQL Injection Prevention**: SQLAlchemy ORM prevents SQL injection
6. **Double-Booking Prevention**: Business logic prevents conflicting appointments

### Database Models

- **User**: Stores user information (email, password_hash, role, name)
- **Availability**: Stores doctor availability time slots
- **Appointment**: Links patients to doctors with specific time slots

## 🔒 Security Considerations

- Passwords are never stored in plain text
- JWT tokens include expiration time
- All business endpoints require authentication
- Role-based access control prevents unauthorized actions
- Input validation prevents malicious data injection

## 📝 Testing

The test suite includes:
- Unit tests for authentication service
- Integration tests for booking logic
- API endpoint tests
- Double-booking prevention tests
- RBAC permission tests

Run tests:
```bash
pytest
```

## 🐳 Docker

The database runs in a Docker container. To stop it:
```bash
docker-compose down
```

To remove volumes (clears database):
```bash
docker-compose down -v
```

## 📚 Additional Notes

- The API uses async/await throughout for better performance
- All datetime operations use timezone-aware timestamps
- The forgot password endpoint is a mock (doesn't send emails)
- Availability slots are automatically marked as unavailable when booked
- Cancelled appointments restore availability slots

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is part of a final assessment assignment.

