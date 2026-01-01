# Docker Support

**Priority**: Technical Improvement  
**Status**: Not Started  
**Phase**: Phase 5 - Scalability (Q3 2026)  
**Estimated Timeline**: Q3 2026

---

## Description

Containerize the application for easy deployment and consistent environments. Provides Dockerfile and docker-compose setup for the application, database, and optional services.

**Key Goals**:
- Dockerize Python application
- Docker Compose for multi-container setup
- Easy deployment
- Consistent environments
- Production-ready containerization

---

## Implementation Details

### Dockerfile

#### Python Application Dockerfile

**Multi-stage build** (recommended):
- Build stage: Install dependencies
- Runtime stage: Minimal image with application

**Key Components**:
- Python base image
- Application code
- Dependencies installation
- Environment configuration
- Entry point

#### Example Structure

```dockerfile
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["cv-mailer-api"]
```

### Docker Compose

#### Services

**Application Service**:
- Python application container
- Environment variables
- Volume mounts (data, logs, credentials)
- Port mapping

**Database Service** (optional):
- PostgreSQL or SQLite volume
- Database initialization
- Data persistence

**Redis Service** (optional, if using):
- Redis for caching/queues
- Data persistence

#### docker-compose.yml Structure

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./.env:/app/.env
    environment:
      - DATABASE_URL=postgresql://...
  
  db:
    image: postgres:15
    volumes:
      - db_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=cv_mailer
      - POSTGRES_USER=cv_mailer
      - POSTGRES_PASSWORD=...
```

### .dockerignore

Exclude unnecessary files from Docker build:
- `__pycache__/`
- `*.pyc`
- `.git/`
- `venv/`
- `*.log`
- `.env` (mount separately)
- `node_modules/` (if frontend is separate)

### Configuration

#### Environment Variables

- Mount `.env` file or use environment variables
- Database connection
- API keys and credentials
- Application configuration

#### Volume Mounts

- `data/`: Database files
- `logs/`: Log files
- `.env`: Configuration (or use environment variables)
- `assets/`: Resume files (optional)
- `credentials.json`: OAuth credentials (mount securely)

### Deployment

#### Build

```bash
docker build -t cv-mailer .
```

#### Run

```bash
docker-compose up -d
```

#### Production Considerations

- Use specific image tags (not `latest`)
- Health checks
- Resource limits
- Security best practices
- Secrets management

---

## Dependencies

- Docker and Docker Compose
- Application code
- Configuration files
- Credentials (mount securely)

---

## Related Features

- All features (containerization affects entire application)
- [CI/CD Pipeline](../technical-improvements/24-cicd-pipeline.md) - Can build Docker images

---

## Benefits

- ✅ Easy deployment
- ✅ Consistent environments
- ✅ Production-ready
- ✅ Scalability
- ✅ Isolation

---

## Success Criteria

- [ ] Application runs in Docker container
- [ ] Docker Compose setup works
- [ ] Environment configuration works
- [ ] Data persistence works
- [ ] Logs are accessible
- [ ] Production-ready configuration

---

**Last Updated**: January 2026

