# Authentication Configuration

## Backend (.env)

```bash
# Security
SECRET_KEY=your-super-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/xinhai

# CORS
ALLOWED_ORIGINS=http://localhost:8080,https://yourdomain.com

# Optional: Redis for session storage
REDIS_URL=redis://localhost:6379/0
```

## Frontend (.env)

```bash
# API
VITE_API_URL=http://localhost:8000

# Optional: Analytics
VITE_ANALYTICS_ID=your-analytics-id
```

## Database Setup

```bash
# Create database
createdb xinhai

# Run migrations (if using Alembic)
alembic upgrade head

# Or create tables manually
python -c "from backend.src.xinhai.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

## Security Checklist

- [ ] Change SECRET_KEY in production
- [ ] Use HTTPS in production
- [ ] Enable CORS only for trusted origins
- [ ] Set up rate limiting
- [ ] Configure database with SSL
- [ ] Enable 2FA (optional enhancement)
- [ ] Set up logging and monitoring
- [ ] Regular security audits
