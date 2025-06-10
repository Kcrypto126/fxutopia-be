"""

# FxUtopia - Forex & Crypto Trading Hub API

A comprehensive FastAPI backend for a Forex & Crypto trading community platform featuring authentication, community forums, educational content, marketplace, reviews, signals, and economic calendar.

## Features

### 🔐 Authentication & Authorization

- JWT-based authentication with refresh tokens
- Social login support (Google, GitHub)
- Email verification and password reset
- Two-factor authentication (2FA)
- Role-based access control (User, Admin)

### 👥 Community & Forum

- Discussion boards with categories (Forex, Crypto, Stocks, AI Trading, General)
- Threaded comments and replies
- Post likes and reactions
- User badges and gamification
- Real-time messaging via WebSocket

### 📚 Educational Content

- Structured courses (Beginner, Intermediate, Advanced)
- Blog articles and video tutorials
- Progress tracking and completion certificates
- Searchable knowledge base

### 💼 Marketplace

- Product listings for EAs, bots, indicators, scripts
- Secure digital delivery system
- Ratings and reviews
- Payment processing integration ready
- File upload and management

### ⭐ Reviews & Ratings

- Broker and platform reviews
- Verified user reviews
- Detailed rating categories
- Helpful vote system

### 📈 Trading Signals

- Signal provider system
- Subscription management
- Performance tracking and leaderboards
- Real-time signal updates

### 📅 Economic Calendar

- Economic events with impact levels
- Country and currency filtering
- Real-time updates

### 🔧 Technical Features

- Clean Architecture pattern
- Repository and Service patterns
- Comprehensive error handling
- Rate limiting and security middleware
- File upload and processing
- Caching with Redis
- Background tasks with Celery
- WebSocket real-time communication
- Full-text search functionality
- Analytics and metrics
- Email notifications
- Database migrations with Alembic

## Technology Stack

- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Primary database
- **Redis** - Caching and task queue
- **SQLAlchemy** - ORM
- **Alembic** - Database migrations
- **Celery** - Background task processing
- **JWT** - Authentication tokens
- **Pydantic** - Data validation
- **Docker** - Containerization

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 7+

### Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd fxutopia_backend
```

2. Create virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Environment setup:

```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Database setup:

```bash
# Create database
createdb fxutopia

# Run migrations
alembic upgrade head
```

6. Start the application:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

### Docker Setup

1. Build and run with Docker Compose:

```bash
docker-compose up -d
```

This will start:

- API server on port 8000
- PostgreSQL on port 5432
- Redis on port 6379
- Celery worker and beat scheduler

## API Endpoints

### Authentication

- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/verify-email` - Verify email address
- `POST /api/v1/auth/forgot-password` - Request password reset
- `POST /api/v1/auth/reset-password` - Reset password

### Users

- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update user profile
- `POST /api/v1/users/me/avatar` - Upload avatar

### Community

- `GET /api/v1/community/posts` - Get posts
- `POST /api/v1/community/posts` - Create post
- `GET /api/v1/community/posts/{id}` - Get post by ID
- `POST /api/v1/community/posts/{id}/like` - Like/unlike post
- `POST /api/v1/community/posts/{id}/comments` - Add comment

### Education

- `GET /api/v1/education/content` - Get educational content
- `POST /api/v1/education/content` - Create content
- `GET /api/v1/education/courses` - Get courses
- `POST /api/v1/education/courses/{id}/enroll` - Enroll in course

### Marketplace

- `GET /api/v1/marketplace/products` - Get products
- `POST /api/v1/marketplace/products` - Create product
- `POST /api/v1/marketplace/products/{id}/purchase` - Purchase product

### Reviews

- `GET /api/v1/reviews` - Get reviews
- `POST /api/v1/reviews` - Create review
- `POST /api/v1/reviews/{id}/helpful` - Mark review helpful

### Signals

- `GET /api/v1/signals` - Get trading signals
- `POST /api/v1/signals` - Create signal
- `GET /api/v1/signals/providers` - Get signal providers

### Calendar

- `GET /api/v1/calendar/events` - Get economic events
- `POST /api/v1/calendar/events` - Create event (admin)

### Search

- `GET /api/v1/search` - Global search
- `GET /api/v1/search/posts` - Search posts
- `GET /api/v1/search/articles` - Search articles

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Background Tasks

```bash
# Start Celery worker
celery -A app.core.celery_app worker --loglevel=info

# Start Celery beat scheduler
celery -A app.core.celery_app beat --loglevel=info

# Monitor with Flower
celery -A app.core.celery_app flower --port=5555
```

## Configuration

Key environment variables:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost/fxutopia

# Redis
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# File Storage
UPLOAD_FOLDER=uploads
MAX_FILE_SIZE=52428800
```

## Production Deployment

### Using Docker

```bash
# Build production image
docker build -t fxutopia-api .

# Run with environment variables
docker run -p 8000:8000 --env-file .env fxutopia-api
```

### Security Considerations

- Change default SECRET_KEY
- Use environment variables for sensitive data
- Configure CORS for production domains
- Set up SSL/TLS certificates
- Configure rate limiting
- Enable database connection pooling
- Set up monitoring and logging

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Create Pull Request

## License

This project is licensed under the MIT License.

## Support

For support and questions:

- Create an issue on GitHub
- Check the API documentation at `/docs`
- Review the test files for usage examples
  """
