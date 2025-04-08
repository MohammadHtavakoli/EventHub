
### EventHub An Event Management System - Documentation

## Project Summary

The Event Management System is a Django REST Framework-based backend application that allows users to create, manage, and participate in events. The system implements role-based access control with three user types:

1. **Event Creator**: Can create and manage events, view participants  
2. **Regular User**: Can view events, join/leave events, view their participation  
3. **Admin**: Has full access to manage all aspects of the system

Key features include:

- JWT authentication  
- Event creation and management  
- Event participation with capacity limits  
- Advanced filtering and search  
- Comprehensive activity logging

## API Endpoints

### Authentication

| Endpoint                    | Method | Description             | Request Body                                                  | Response                                                     |
|----------------------------|--------|-------------------------|---------------------------------------------------------------|--------------------------------------------------------------|
| `/api/users/token/`        | POST   | Login and get JWT token | `{"email": "user@example.com", "password": "password123"}`    | `{"access": "token", "refresh": "token", "user_details": {...}}` |
| `/api/users/token/refresh/`| POST   | Refresh JWT token       | `{"refresh": "token"}`                                        | `{"access": "token"}`                                        |

### Users

| Endpoint           | Method | Description       | Access        |
|--------------------|--------|-------------------|---------------|
| `/api/users/`      | POST   | Register new user | Public        |
| `/api/users/me/`   | GET    | Get current user  | Authenticated |

### Events

| Endpoint                                | Method     | Description                                        | Access                                            |
|-----------------------------------------|------------|----------------------------------------------------|---------------------------------------------------|
| `/api/events/`                          | GET        | List events                                        | Public (open events), Authenticated (all events) |
| `/api/events/`                          | POST       | Create event                                       | Event Creator                                     |
| `/api/events/{id}/`                     | GET        | Get event details                                  | Public (open events), Authenticated (all events) |
| `/api/events/{id}/`                     | PUT/PATCH  | Update event                                       | Event Creator (own events), Admin                |
| `/api/events/{id}/`                     | DELETE     | Delete event                                       | Event Creator (own events with no participants), Admin |
| `/api/events/{id}/participants/`        | GET        | List participants                                  | Event Creator (own events), Admin                |
| `/api/events/{id}/join/`                | POST       | Join event                                         | Authenticated                                     |
| `/api/events/{id}/leave/`               | POST       | Leave event                                        | Authenticated                                     |

### Logs

| Endpoint        | Method | Description        | Access                                           |
|-----------------|--------|--------------------|--------------------------------------------------|
| `/api/logs/`    | GET    | List logs          | Admin (all logs), Event Creator (own event logs), User (participated event logs) |

## How to Use the Project

### Prerequisites

- Python 3.8+  
- PostgreSQL  
- Git

### Setup and Installation

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/EventHub.git
cd EventHub
```

2. **Create and activate a virtual environment**

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Create PostgreSQL database**

```sql
-- Log into PostgreSQL
psql -U postgres

-- Create database
CREATE DATABASE event_management;
CREATE USER event_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE event_management TO event_user;
\q
```

5. **Configure environment variables**

```bash
# Copy example environment file
cp .env.example .env
```

Edit `.env` file with your database settings:

```
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=event_management
DB_USER=event_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

6. **Apply migrations**

```bash
python manage.py migrate
```

7. **Create a superuser**

```bash
python manage.py createsuperuser
```

8. **Run the development server**

```bash
python manage.py runserver
```

9. **Access the API**

- API: [http://127.0.0.1:8000/api/](http://127.0.0.1:8000/api/)
- Admin interface: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
- API documentation: [http://127.0.0.1:8000/swagger/](http://127.0.0.1:8000/swagger/) or [http://127.0.0.1:8000/redoc/](http://127.0.0.1:8000/redoc/)

### Basic Usage Examples

#### 1. Register a new user

```bash
curl -X POST http://127.0.0.1:8000/api/users/   -H "Content-Type: application/json"   -d '{
    "email": "user@example.com",
    "username": "user1",
    "password": "password123",
    "password2": "password123",
    "first_name": "John",
    "last_name": "Doe",
    "role": "EVENT_CREATOR"
  }'
```

#### 2. Login and get token

```bash
curl -X POST http://127.0.0.1:8000/api/users/token/   -H "Content-Type: application/json"   -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

#### 3. Create an event

```bash
curl -X POST http://127.0.0.1:8000/api/events/   -H "Authorization: Bearer <your_token>"   -H "Content-Type: application/json"   -d '{
    "name": "Tech Conference 2023",
    "description": "Annual technology conference",
    "capacity": 100,
    "date": "2023-12-15T09:00:00Z",
    "location": "Convention Center",
    "status": "OPEN"
  }'
```

#### 4. Join an event

```bash
curl -X POST http://127.0.0.1:8000/api/events/1/join/   -H "Authorization: Bearer <your_token>"
```

#### 5. List events with filtering

```bash
# List all open events
curl -X GET "http://127.0.0.1:8000/api/events/?status=OPEN"   -H "Authorization: Bearer <your_token>"

# List events with remaining capacity
curl -X GET "http://127.0.0.1:8000/api/events/?has_capacity=true"   -H "Authorization: Bearer <your_token>"

# List upcoming events
curl -X GET "http://127.0.0.1:8000/api/events/?upcoming=true"   -H "Authorization: Bearer <your_token>"

# List events created by current user
curl -X GET "http://127.0.0.1:8000/api/events/?created=true"   -H "Authorization: Bearer <your_token>"

# List events joined by current user
curl -X GET "http://127.0.0.1:8000/api/events/?joined=true"   -H "Authorization: Bearer <your_token>"
```

### Business Rules

1. **Event Creation**:
    - Users can only have a limited number of open events (default: 5)  
    - Event capacity must be a positive integer  

2. **Event Participation**:
    - Users cannot join closed or canceled events  
    - Users cannot join an event that has reached its capacity  
    - Users cannot join an event they have already joined  

3. **Event Deletion**:
    - Events with participants cannot be deleted  

### Deployment

For production deployment:

1. **Set up a production environment**:
    - Set `DEBUG=False` in your environment variables  
    - Generate a strong `SECRET_KEY`  
    - Configure `ALLOWED_HOSTS` with your domain  

2. **Set up a production database**:
    - Configure PostgreSQL with proper settings  
    - Set up database backups  

3. **Set up a production web server**:
    - Install and configure Nginx  
    - Set up Gunicorn as the application server  

4. **Run with Gunicorn**

```bash
gunicorn EventHub.wsgi:application --bind 0.0.0.0:8000
```

5. **Configure Nginx**

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /path/to/your/project;
    }

    location / {
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://localhost:8000;
    }
}
```

6. **Set up SSL/TLS**

- Obtain SSL certificates (e.g., using Let's Encrypt)  
- Configure HTTPS in Nginx  

## API Documentation

For detailed API documentation, access the Swagger or ReDoc interfaces when the application is running:

- Swagger UI: [http://127.0.0.1:8000/swagger/](http://127.0.0.1:8000/swagger/)
- ReDoc: [http://127.0.0.1:8000/redoc/](http://127.0.0.1:8000/redoc/)

## Author
Mohammad Hasan Tavakoli