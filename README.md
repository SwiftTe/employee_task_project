# Employee Task Management and Productivity Analytics System

A comprehensive backend system for managing employee tasks and analyzing productivity metrics using Django, Django REST Framework, Celery, and PostgreSQL.

## Features

### Core Functionality
- **User Management**: Role-based access control (Admin, Manager, Employee)
- **Task Management**: Complete task lifecycle with assignments, status tracking, and comments
- **Project Management**: Organize tasks into projects with progress tracking
- **Analytics Dashboard**: Real-time productivity metrics and performance insights
- **Background Processing**: Automated reports and notifications using Celery

### Technical Features
- **RESTful APIs**: Comprehensive API endpoints with JWT authentication
- **Role-Based Permissions**: Granular access control for different user roles
- **File Attachments**: Support for task-related file uploads
- **Time Tracking**: Log hours spent on tasks with detailed analytics
- **Audit Trail**: Complete history of task changes and actions
- **Email Notifications**: Automated task updates and deadline reminders

## Technology Stack

- **Backend**: Django 4.2.7, Django REST Framework 3.14.0
- **Database**: PostgreSQL 15
- **Authentication**: JWT (JSON Web Tokens)
- **Background Tasks**: Celery with Redis
- **Containerization**: Docker & Docker Compose
- **Testing**: Pytest with Django integration
- **Web Server**: Gunicorn (production), Django development server
- **Reverse Proxy**: Nginx

## Project Structure

```
employee_task_project/
├── employee_task_system/     # Main Django project
│   ├── settings.py          # Django settings with all configurations
│   ├── urls.py              # Main URL routing
│   ├── celery.py            # Celery configuration
│   └── wsgi.py             # WSGI configuration
├── users/                   # User management app
│   ├── models.py            # Custom User model
│   ├── serializers.py       # User API serializers
│   ├── views.py             # User API views
│   ├── permissions.py       # Custom permissions
│   └── urls.py             # User URLs
├── tasks/                   # Task management app
│   ├── models.py            # Task, Project, Comment models
│   ├── serializers.py       # Task API serializers
│   ├── views.py             # Task API views
│   └── urls.py             # Task URLs
├── analytics/               # Analytics app
│   ├── models.py            # Analytics and metrics models
│   ├── serializers.py       # Analytics serializers
│   ├── views.py             # Analytics API views
│   └── urls.py             # Analytics URLs
├── tests/                   # Test suite
│   ├── conftest.py          # Pytest configuration and fixtures
│   ├── test_users.py        # User tests
│   ├── test_tasks.py        # Task tests
│   └── test_analytics.py    # Analytics tests
├── docker-compose.yml        # Development environment
├── docker-compose.prod.yml   # Production environment
├── Dockerfile              # Docker image configuration
├── nginx.conf              # Nginx configuration
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Installation and Setup

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd employee_task_project
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure database**
   - Create PostgreSQL database `employee_task_db`
   - Update database settings in `employee_task_system/settings.py`

5. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start development server**
   ```bash
   python manage.py runserver
   ```

### Docker Setup

1. **Development environment**
   ```bash
   docker-compose up --build
   ```

2. **Production environment**
   ```bash
   docker-compose -f docker-compose.prod.yml up --build
   ```

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout
- `GET /api/auth/profile/` - User profile
- `GET /api/auth/` - List users (Manager/Admin only)

### Tasks
- `GET /api/tasks/` - List tasks
- `POST /api/tasks/` - Create task
- `GET /api/tasks/{id}/` - Task details
- `PUT /api/tasks/{id}/` - Update task
- `DELETE /api/tasks/{id}/` - Delete task
- `POST /api/tasks/{id}/assign/` - Assign task
- `POST /api/tasks/{id}/update-status/` - Update task status

### Projects
- `GET /api/tasks/projects/` - List projects
- `POST /api/tasks/projects/` - Create project
- `GET /api/tasks/projects/{id}/` - Project details

### Analytics
- `GET /api/analytics/summary/` - Dashboard summary (Manager/Admin)
- `GET /api/analytics/employee-performance/` - Employee metrics
- `GET /api/analytics/project-performance/` - Project metrics
- `POST /api/analytics/generate-report/` - Generate performance report

## User Roles and Permissions

### Admin
- Full system access
- User management
- All analytics access
- System configuration

### Manager
- Task creation and assignment
- Team performance analytics
- Project management
- Employee skill ratings

### Employee
- View assigned tasks
- Update task status
- Log time entries
- View own performance metrics

## Background Tasks

The system includes automated background tasks for:

- **Daily productivity reports** (11:59 PM)
- **Project analytics updates** (12:05 AM)
- **Task delay analysis** (12:10 AM)
- **Overdue task notifications** (9:00 AM)
- **Department analytics** (11:30 PM)

## Testing

Run the test suite:
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=.

# Run specific test file
pytest tests/test_users.py

# Run with markers
pytest -m unit  # Unit tests only
pytest -m integration  # Integration tests only
```

## Environment Variables

Key environment variables:

```bash
DEBUG=True/False
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@host:port/dbname
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
DEFAULT_FROM_EMAIL=noreply@company.com
```

## Production Deployment

1. **Environment setup**
   - Set `DEBUG=False`
   - Configure production database
   - Set secure `SECRET_KEY`
   - Configure email settings

2. **Static files**
   ```bash
   python manage.py collectstatic --noinput
   ```

3. **Database migrations**
   ```bash
   python manage.py migrate
   ```

4. **Start services**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

## Monitoring and Maintenance

- **Health checks**: Database and Redis health monitoring
- **Logging**: Comprehensive logging for debugging
- **Performance metrics**: Real-time analytics dashboard
- **Backup strategies**: Regular database backups recommended

## Contributing

1. Fork the repository
2. Create feature branch
3. Write tests for new features
4. Ensure all tests pass
5. Submit pull request

## License

This project is licensed under the MIT License.

## Support

For technical support or questions, please contact the development team.

---

**Note**: This is a final year project demonstrating backend engineering concepts including system design, database modeling, API development, background processing, and performance analytics.
