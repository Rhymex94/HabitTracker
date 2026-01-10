# Habit Tracker

A full-stack habit tracking application designed to help users create, monitor, and maintain habits with flexible tracking options and progress visualization.

## Features

- **User Authentication**: Secure JWT-based authentication with session management
- **Flexible Habit Types**:
  - Binary habits (yes/no completion)
  - Quantitative habits with custom units (e.g., "Run 5 km", "Practice 30 minutes")
  - ABOVE/BELOW success criteria for different habit goals
- **Time Frames**: Track habits daily, weekly, monthly, or yearly
- **Progress Tracking**:
  - Visual progress indicators
  - Current period completion status
  - Streak tracking
- **Statistics Dashboard**: View completion rates and progress trends
- **Responsive UI**: Clean, intuitive interface built with React

## Technology Stack

### Backend
- **Framework**: Flask 3.0
- **ORM**: SQLAlchemy 3.1
- **Database**: MySQL 8.0
- **Authentication**: JWT (PyJWT 2.8)
- **Password Hashing**: bcrypt 4.1
- **Testing**: pytest with pytest-flask

### Frontend
- **Framework**: React 19
- **Language**: TypeScript 5.8
- **Build Tool**: Vite 6.3
- **HTTP Client**: Axios 1.9
- **Routing**: React Router 7.6

### Infrastructure
- **Containerization**: Docker with Docker Compose
- **Database Migrations**: Flask-Migrate (Alembic)

## Development Setup

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ and npm (for frontend development)
- Git

### Getting Started

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd HabitTracker
   ```

2. **Set up environment variables**

   Copy the example environment file and configure for development:
   ```bash
   cp .env.example .env
   ```

   The `.env` file should contain:
   ```bash
   ENVIRONMENT=development
   ```

   This tells the application to use the default development SECRET_KEY. See the Security section for more details.

3. **Start the backend services**

   From the project root:
   ```bash
   docker compose up
   ```

   This will:
   - Build the Flask backend
   - Start MySQL 8.0 database
   - Run database migrations
   - Start the backend on `http://localhost:8320`

4. **Install and run the frontend**

   In a new terminal, navigate to the frontend directory:
   ```bash
   cd frontend-web
   npm install
   npm run dev
   ```

   The frontend will start on `http://localhost:5173`

5. **Access the application**

   Open your browser and navigate to `http://localhost:5173`

### Running Tests

**Backend tests:**
```bash
# Run all tests
docker exec habittracker-backend-1 python -m pytest tests/ -v

# Run specific test file
docker exec habittracker-backend-1 python -m pytest tests/test_habits.py -v

# Run specific test
docker exec habittracker-backend-1 python -m pytest tests/test_habits.py::test_create_habit -v
```

**Frontend:**
```bash
cd frontend-web
npm run lint
```

## Production Deployment

### Security Requirements

**CRITICAL: SECRET_KEY Configuration**

The application requires a `SECRET_KEY` environment variable for JWT token signing. By default, the application assumes production mode and will **fail to start** if `SECRET_KEY` is not set.

**For Production:**

1. Generate a secure secret key:
   ```bash
   python -c 'import secrets; print(secrets.token_hex(32))'
   ```

2. Set the environment variable:
   ```bash
   export SECRET_KEY=your-generated-secret-key-here
   ```

   Or add it to your deployment environment configuration.

**For Development:**

Set `ENVIRONMENT=development` in your `.env` file to use the default development key. This is already configured if you followed the setup steps above.

### Environment Variables

Required for production:

- `SECRET_KEY`: JWT token signing key (required, no default in production)
- `DATABASE_URL`: MySQL connection string (default: `mysql+pymysql://user:password@db/habits_db`)
- `FRONTEND_ORIGIN`: CORS allowed origin (default: `http://localhost:3000`)

Optional:

- `ENVIRONMENT`: Set to `development` to allow default SECRET_KEY (never use in production)
- `FLASK_ENV`: Flask environment mode

### Database Setup

1. **Create MySQL database**:
   ```sql
   CREATE DATABASE habits_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

2. **Run migrations**:
   ```bash
   flask db upgrade
   ```

### Deployment Checklist

- [ ] Set `SECRET_KEY` environment variable with a secure random key
- [ ] Configure `DATABASE_URL` for production MySQL instance
- [ ] Set `FRONTEND_ORIGIN` to your production frontend URL
- [ ] **Do NOT** set `ENVIRONMENT=development` in production
- [ ] Use a production WSGI server (e.g., Gunicorn, uWSGI) instead of Flask development server
- [ ] Enable HTTPS/TLS for all traffic
- [ ] Configure database connection pooling for production load
- [ ] Set up regular database backups
- [ ] Review and configure CORS origins appropriately
- [ ] Enable rate limiting for authentication endpoints (recommended)

### Docker Production Build

For production, you'll want to:

1. Remove the volume mounts in `docker-compose.yml` (they're for development hot-reloading)
2. Set proper production environment variables
3. Use a production-grade WSGI server
4. Consider using docker-compose.prod.yml with production configurations

## Project Structure

```
HabitTracker/
├── backend/                 # Flask backend application
│   ├── app/
│   │   ├── routes/         # API endpoints
│   │   │   ├── auth.py     # Authentication endpoints
│   │   │   ├── habits.py   # Habit CRUD operations
│   │   │   ├── progress.py # Progress tracking
│   │   │   └── stats.py    # Statistics and analytics
│   │   ├── models.py       # SQLAlchemy models
│   │   ├── auth.py         # JWT authentication logic
│   │   ├── utils.py        # Helper functions (streak calculation, etc.)
│   │   └── config.py       # Application configuration
│   ├── migrations/         # Database migration files
│   ├── tests/              # Backend test suite
│   └── requirements.txt    # Python dependencies
├── frontend-web/           # React frontend application
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── context/        # React context (auth, etc.)
│   │   ├── api/            # API client configuration
│   │   └── styles/         # CSS stylesheets
│   └── package.json        # Node.js dependencies
├── docker-compose.yml      # Development environment setup
├── .env                    # Local environment variables (not committed)
├── .env.example            # Environment variables template
└── README.md              # This file
```

## API Documentation

The backend exposes a RESTful API with the following endpoints:

### Authentication
- `POST /api/auth/signup` - Create new user account
- `POST /api/auth/login` - Authenticate and receive JWT token
- `GET /api/auth/verify` - Verify JWT token validity

### Habits
- `GET /api/habits` - List all user's habits with completion status
- `POST /api/habits` - Create new habit
- `PATCH /api/habits/:id` - Update habit
- `DELETE /api/habits/:id` - Delete habit

### Progress
- `GET /api/progress` - Get progress entries (filterable by habit and date range)
- `POST /api/progress` - Create progress entry
- `DELETE /api/progress/:id` - Delete progress entry

### Statistics
- `GET /api/stats` - Get aggregated statistics and streaks for all habits

All endpoints except signup and login require JWT authentication via `Authorization: Bearer <token>` header.

## Development Notes

### Database Migrations

When modifying models:

```bash
# Generate migration
docker exec habittracker-backend-1 flask db migrate -m "Description of changes"

# Apply migration
docker exec habittracker-backend-1 flask db upgrade

# Rollback migration
docker exec habittracker-backend-1 flask db downgrade
```

### Code Quality

- Backend follows PEP 8 style guidelines
- Frontend uses ESLint with React-specific rules
- All security-critical code has comprehensive test coverage

## Troubleshooting

**Backend won't start with SECRET_KEY error:**
- Ensure `.env` file exists with `ENVIRONMENT=development`
- Or set `SECRET_KEY` environment variable explicitly

**Database connection errors:**
- Ensure MySQL container is running: `docker ps`
- Check DATABASE_URL is correct in docker-compose.yml or .env
- Wait a few seconds after starting MySQL before starting backend

**CORS errors in frontend:**
- Verify `FRONTEND_ORIGIN` matches your frontend URL
- Check browser console for specific CORS error messages

**Tests failing:**
- Ensure you're running tests inside the container
- Check that database is accessible
- Review test output for specific failures

## Contributing

1. Write tests for new features
2. Ensure all tests pass before submitting changes
3. Follow existing code style and patterns
4. Update documentation for API changes

## License

[Add your license information here]

## Support

[Add support contact information or issue tracker link here]
