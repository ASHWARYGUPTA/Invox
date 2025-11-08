# Quick Reference - Common Commands

## Backend Commands

### Starting the Backend

```bash
cd backend2
source venv/bin/activate
uvicorn app.main:app --reload --port 8001

# Or use the start script
./start_backend.sh
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View current migration
alembic current

# View migration history
alembic history
```

### Database Management

```bash
# Connect to database
psql -U invox_user -d invox_db

# Common SQL queries
SELECT * FROM users;
SELECT * FROM accounts;
SELECT * FROM sessions;

# Drop all tables (careful!)
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
```

### Python Virtual Environment

```bash
# Create venv
python3 -m venv venv

# Activate venv
source venv/bin/activate  # Linux/macOS
.\venv\Scripts\activate   # Windows

# Deactivate venv
deactivate

# Install dependencies
pip install -r requirements.txt

# Update requirements
pip freeze > requirements.txt
```

## Frontend Commands

### Development

```bash
# Install dependencies
pnpm install

# Start dev server
pnpm dev

# Build for production
pnpm build

# Start production server
pnpm start
```

### Environment Setup

```bash
# Copy environment template
cp .env.local.example .env.local

# Generate NextAuth secret
openssl rand -base64 32
```

## Docker Commands (Future)

```bash
# Build backend image
docker build -t invox-backend2 ./backend2

# Run backend container
docker run -p 8001:8001 invox-backend2

# Docker Compose (create docker-compose.yml first)
docker-compose up -d
docker-compose down
docker-compose logs -f
```

## Testing Commands

### Backend Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v
```

### Frontend Testing

```bash
# Run tests
pnpm test

# Run tests in watch mode
pnpm test:watch

# Run E2E tests
pnpm test:e2e
```

## Debugging

### Check Ports

```bash
# Check if port is in use
lsof -i :8001
lsof -i :3000

# Kill process on port
kill -9 $(lsof -t -i :8001)
```

### View Logs

```bash
# Backend logs (if logging to file)
tail -f backend2/logs/app.log

# PostgreSQL logs
tail -f /var/log/postgresql/postgresql-*.log

# System logs
journalctl -u postgresql -f
```

### Environment Variables

```bash
# Print all env vars
printenv

# Print specific var
echo $DATABASE_URL

# Set env var temporarily
export DATABASE_URL="postgresql://..."
```

## Git Commands

```bash
# Check status
git status

# Commit changes
git add .
git commit -m "Description"

# Create branch
git checkout -b feature/backend2

# Push to remote
git push origin feature/backend2
```

## PostgreSQL Commands

```bash
# Create database
createdb invox_db

# Drop database
dropdb invox_db

# Create user
createuser invox_user -P

# Grant privileges
psql -c "GRANT ALL PRIVILEGES ON DATABASE invox_db TO invox_user"

# Backup database
pg_dump invox_db > backup.sql

# Restore database
psql invox_db < backup.sql
```

## API Testing with HTTPie

```bash
# Install httpie
pip install httpie

# Test OAuth callback
http POST localhost:8001/api/v1/auth/oauth/callback \
  email=test@example.com \
  name="Test User" \
  provider=google \
  provider_account_id=123456

# Get current user
http GET localhost:8001/api/v1/users/me \
  Authorization:"Bearer YOUR_TOKEN"

# Update user
http PUT localhost:8001/api/v1/users/me \
  Authorization:"Bearer YOUR_TOKEN" \
  name="New Name"
```

## Performance Monitoring

```bash
# Check backend performance
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8001/health

# Monitor database connections
psql -c "SELECT * FROM pg_stat_activity;"

# Monitor system resources
htop
docker stats  # if using Docker
```

## Security

```bash
# Generate secure random string
openssl rand -hex 32

# Hash a password (Python)
python -c "from passlib.context import CryptContext; print(CryptContext(schemes=['bcrypt']).hash('password'))"

# Check for security vulnerabilities
pip-audit  # Install: pip install pip-audit
```

## Useful Aliases

Add to your `~/.bashrc` or `~/.zshrc`:

```bash
# Backend
alias backend2='cd ~/path/to/invox/backend2 && source venv/bin/activate'
alias start-backend='cd ~/path/to/invox/backend2 && ./start_backend.sh'

# Database
alias db-connect='psql -U invox_user -d invox_db'
alias db-migrate='alembic upgrade head'
alias db-rollback='alembic downgrade -1'

# Frontend
alias start-frontend='cd ~/path/to/invox && pnpm dev'

# Combined
alias start-all='start-backend & sleep 5 && start-frontend'
```

## Emergency Commands

### Reset Everything

```bash
# Drop database and recreate
dropdb invox_db && createdb invox_db

# Remove all migrations and recreate
rm -rf backend2/alembic/versions/*.py
cd backend2
alembic revision --autogenerate -m "Initial"
alembic upgrade head

# Reinstall backend dependencies
cd backend2
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Reinstall frontend dependencies
rm -rf node_modules
pnpm install
```

### Check Everything

```bash
# Backend health
curl http://localhost:8001/health

# Database connection
psql -U invox_user -d invox_db -c "SELECT 1"

# Frontend
curl http://localhost:3000

# Check all services
echo "Backend:" && curl -s http://localhost:8001/health | jq
echo "Database:" && psql -U invox_user -d invox_db -c "SELECT 1"
echo "Frontend:" && curl -s http://localhost:3000 | grep -q "<!DOCTYPE html" && echo "OK"
```

## Pro Tips

1. **Use tmux/screen** to run backend and frontend in same terminal
2. **Set up git hooks** for pre-commit checks
3. **Use environment profiles** for dev/staging/production
4. **Keep backups** of your database regularly
5. **Monitor logs** in real-time during development
6. **Use API documentation** at /docs for testing
7. **Version your migrations** properly with descriptive names
8. **Test OAuth flow** in incognito mode to avoid cache issues
