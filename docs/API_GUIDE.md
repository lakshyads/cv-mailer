# CV Mailer API Guide

Complete guide to the CV Mailer REST API built with FastAPI.

> 📖 **Other Documentation**: [Quick Start](QUICK_START.md) | [Setup Guide](SETUP_GUIDE.md) | [Architecture](design/ARCHITECTURE.md)

## Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
- [API Endpoints](#api-endpoints)
- [Authentication](#authentication)
- [Request/Response Format](#requestresponse-format)
- [Error Handling](#error-handling)
- [Examples](#examples)
- [Integration Guide](#integration-guide)

## Overview

The CV Mailer API provides RESTful endpoints for:

- Managing job applications
- Viewing email records
- Managing recruiter contacts
- Accessing statistics and analytics

**Base URL**: `http://localhost:8000`  
**API Version**: v1  
**Documentation**: <http://localhost:8000/docs> (Swagger UI)  
**Alternative Docs**: <http://localhost:8000/redoc>

## Getting Started

### Installation

```bash
# Install with API dependencies
pip install -e ".[api]"

# Or install all dependencies
pip install -e ".[dev]"
```

### Starting the Server

```bash
# Using the provided command
cv-mailer-api

# Or using uvicorn directly
uvicorn cv_mailer.api.app:app --reload

# Custom host and port
uvicorn cv_mailer.api.app:app --host 0.0.0.0 --port 8080
```

### Verify Installation

```bash
# Check health
curl http://localhost:8000/health

# Response:
{
  "status": "healthy",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/health"
}
```

## API Endpoints

### Health Check

**GET** `/health`

Check if the API is running.

**Response**:

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/health"
}
```

### Applications

#### List Applications

**GET** `/api/v1/applications`

List all job applications with optional filtering.

**Query Parameters**:

- `status` (optional): Filter by status (draft, reached_out, applied, etc.)
- `limit` (optional): Maximum results (default: 50, max: 200)
- `offset` (optional): Skip N results (default: 0)

**Example Request**:

```bash
curl "http://localhost:8000/api/v1/applications?status=reached_out&limit=10"
```

**Response**:

```json
{
  "total": 42,
  "limit": 10,
  "offset": 0,
  "items": [
    {
      "id": 1,
      "company_name": "Presight",
      "position": "Software Engineer",
      "status": "reached_out",
      "location": "Dubai, UAE",
      "job_posting_url": "https://...",
      "created_at": "2024-01-15T10:30:00",
      "reached_out_at": "2024-01-15T11:00:00",
      "applied_at": null,
      "closed_at": null
    }
  ]
}
```

#### Get Application Details

**GET** `/api/v1/applications/{application_id}`

Get details of a specific job application.

**Path Parameters**:

- `application_id`: ID of the application

**Example Request**:

```bash
curl http://localhost:8000/api/v1/applications/1
```

**Response**:

```json
{
  "id": 1,
  "company_name": "Presight",
  "position": "Software Engineer",
  "status": "reached_out",
  "location": "Dubai, UAE",
  "job_posting_url": "https://...",
  "notes": null,
  "created_at": "2024-01-15T10:30:00",
  "reached_out_at": "2024-01-15T11:00:00",
  "applied_at": null,
  "closed_at": null,
  "recruiters": [
    {
      "id": 1,
      "name": "Alice Johnson",
      "email": "alice@presight.ai"
    },
    {
      "id": 2,
      "name": "Bob Smith",
      "email": "bob@presight.ai"
    }
  ],
  "emails_count": 2
}
```

#### Update Application Status

**PUT** `/api/v1/applications/{application_id}/status`

Update the status of a job application.

**Path Parameters**:

- `application_id`: ID of the application

**Request Body**:

```json
{
  "status": "applied",
  "notes": "Submitted application via their portal"
}
```

**Response**:

```json
{
  "message": "Application status updated successfully"
}
```

**Status Values**:

- `draft` - Not yet contacted
- `reached_out` - Initial email sent
- `applied` - Formally applied
- `interview_scheduled` - Interview scheduled
- `in_progress` - Interview process ongoing
- `closed` - Process completed
- `rejected` - Rejected
- `accepted` - Offer accepted

### Emails

#### Get Application Emails

**GET** `/api/v1/applications/{application_id}/emails`

Get all emails sent for a specific job application.

**Path Parameters**:

- `application_id`: ID of the application

**Example Request**:

```bash
curl http://localhost:8000/api/v1/applications/1/emails
```

**Response**:

```json
{
  "application_id": 1,
  "total": 3,
  "emails": [
    {
      "id": 1,
      "email_type": "first_contact",
      "status": "sent",
      "recipient_email": "alice@presight.ai",
      "recipient_name": "Alice Johnson",
      "subject": "Application for Software Engineer at Presight",
      "is_follow_up": false,
      "follow_up_number": 0,
      "created_at": "2024-01-15T11:00:00",
      "sent_at": "2024-01-15T11:00:05"
    },
    {
      "id": 2,
      "email_type": "follow_up",
      "status": "sent",
      "recipient_email": "alice@presight.ai",
      "recipient_name": "Alice Johnson",
      "subject": "Following up: Software Engineer at Presight",
      "is_follow_up": true,
      "follow_up_number": 1,
      "created_at": "2024-01-22T10:00:00",
      "sent_at": "2024-01-22T10:00:03"
    }
  ]
}
```

#### List All Emails

**GET** `/api/v1/emails`

List all email records with optional filtering.

**Query Parameters**:

- `status` (optional): Filter by status (sent, failed, pending, bounced)
- `limit` (optional): Maximum results (default: 50, max: 200)
- `offset` (optional): Skip N results (default: 0)

**Example Request**:

```bash
curl "http://localhost:8000/api/v1/emails?status=sent&limit=20"
```

**Response**:

```json
{
  "total": 156,
  "limit": 20,
  "offset": 0,
  "emails": [
    {
      "id": 1,
      "job_application_id": 1,
      "email_type": "first_contact",
      "status": "sent",
      "recipient_email": "alice@presight.ai",
      "recipient_name": "Alice Johnson",
      "subject": "Application for Software Engineer at Presight",
      "created_at": "2024-01-15T11:00:00",
      "sent_at": "2024-01-15T11:00:05"
    }
  ]
}
```

### Recruiters

#### List Recruiters

**GET** `/api/v1/recruiters`

List all recruiter contacts.

**Query Parameters**:

- `limit` (optional): Maximum results (default: 100, max: 500)
- `offset` (optional): Skip N results (default: 0)

**Example Request**:

```bash
curl http://localhost:8000/api/v1/recruiters
```

**Response**:

```json
{
  "total": 45,
  "limit": 100,
  "offset": 0,
  "recruiters": [
    {
      "id": 1,
      "name": "Alice Johnson",
      "email": "alice@presight.ai",
      "applications_count": 1
    },
    {
      "id": 2,
      "name": "Bob Smith",
      "email": "bob@techcorp.com",
      "applications_count": 2
    }
  ]
}
```

#### Get Recruiter Details

**GET** `/api/v1/recruiters/{recruiter_id}`

Get details of a specific recruiter.

**Path Parameters**:

- `recruiter_id`: ID of the recruiter

**Example Request**:

```bash
curl http://localhost:8000/api/v1/recruiters/1
```

**Response**:

```json
{
  "id": 1,
  "name": "Alice Johnson",
  "email": "alice@presight.ai",
  "applications": [
    {
      "id": 1,
      "company_name": "Presight",
      "position": "Software Engineer",
      "status": "reached_out"
    }
  ]
}
```

### Statistics

#### Get Full Statistics

**GET** `/api/v1/statistics`

Get complete application statistics.

**Example Request**:

```bash
curl http://localhost:8000/api/v1/statistics
```

**Response**:

```json
{
  "total_applications": 42,
  "total_emails_sent": 156,
  "follow_ups_sent": 38,
  "by_status": {
    "draft": 5,
    "reached_out": 20,
    "applied": 10,
    "interview_scheduled": 4,
    "in_progress": 2,
    "closed": 1,
    "rejected": 8,
    "accepted": 1
  }
}
```

#### Get Summary Statistics

**GET** `/api/v1/statistics/summary`

Get summary statistics.

**Example Request**:

```bash
curl http://localhost:8000/api/v1/statistics/summary
```

**Response**:

```json
{
  "total_applications": 42,
  "total_emails_sent": 156,
  "follow_ups_sent": 38,
  "by_status": {
    "draft": 5,
    "reached_out": 20,
    "applied": 10,
    "interview_scheduled": 4,
    "in_progress": 2,
    "closed": 1,
    "rejected": 8,
    "accepted": 1
  }
}
```

## Authentication

Currently, the API does not require authentication as it's designed for local use.

**Future Enhancement**: OAuth2/JWT authentication for multi-user deployments.

**Security Note**: If exposing the API publicly, implement authentication:

```python
# api/dependencies.py
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def verify_token(credentials = Depends(security)):
    # Verify JWT token
    ...
```

## Request/Response Format

### Content Type

All requests and responses use JSON:

```sh
Content-Type: application/json
```

### Date Format

All dates use ISO 8601 format:

```json
{
  "created_at": "2024-01-15T10:30:00"
}
```

### Pagination

Endpoints that return lists support pagination:

```sh
GET /api/v1/applications?limit=20&offset=40
```

Response includes pagination metadata:

```json
{
  "total": 156,
  "limit": 20,
  "offset": 40,
  "items": [...]
}
```

### Filtering

Some endpoints support filtering:

```sh
GET /api/v1/applications?status=reached_out
GET /api/v1/emails?status=sent
```

## Error Handling

### Error Response Format

```json
{
  "detail": "Application not found"
}
```

### HTTP Status Codes

| Code | Meaning |
| - | - |
| 200 | OK - Request successful |
| 400 | Bad Request - Invalid parameters |
| 404 | Not Found - Resource doesn't exist |
| 422 | Unprocessable Entity - Validation error |
| 500 | Internal Server Error |

### Common Errors

**404 Not Found**:

```bash
curl http://localhost:8000/api/v1/applications/9999
```

```json
{
  "detail": "Application not found"
}
```

**400 Bad Request**:

```bash
curl "http://localhost:8000/api/v1/applications?status=invalid_status"
```

```json
{
  "detail": "Invalid status: invalid_status"
}
```

## Examples

### Python Client

```python
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Get all applications
response = requests.get(f"{BASE_URL}/applications")
applications = response.json()

print(f"Total applications: {applications['total']}")
for app in applications['items']:
    print(f"- {app['company_name']}: {app['position']} ({app['status']})")

# Get specific application
app_id = 1
response = requests.get(f"{BASE_URL}/applications/{app_id}")
app = response.json()

print(f"\nApplication #{app_id}:")
print(f"Company: {app['company_name']}")
print(f"Position: {app['position']}")
print(f"Recruiters: {', '.join(r['name'] for r in app['recruiters'])}")

# Update application status
response = requests.put(
    f"{BASE_URL}/applications/{app_id}/status",
    json={"status": "applied", "notes": "Submitted via company portal"}
)
print(f"\nStatus updated: {response.json()}")

# Get statistics
response = requests.get(f"{BASE_URL}/statistics/summary")
stats = response.json()

print(f"\nStatistics:")
print(f"Total Applications: {stats['total_applications']}")
print(f"Total Emails Sent: {stats['total_emails_sent']}")
print(f"Follow-ups Sent: {stats['follow_ups_sent']}")
```

### JavaScript/TypeScript

```typescript
const BASE_URL = 'http://localhost:8000/api/v1';

// Get all applications
async function getApplications() {
  const response = await fetch(`${BASE_URL}/applications`);
  const data = await response.json();
  
  console.log(`Total applications: ${data.total}`);
  data.items.forEach(app => {
    console.log(`- ${app.company_name}: ${app.position} (${app.status})`);
  });
}

// Update application status
async function updateApplicationStatus(id: number, status: string, notes?: string) {
  const response = await fetch(`${BASE_URL}/applications/${id}/status`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ status, notes })
  });
  
  const result = await response.json();
  console.log(result.message);
}

// Get statistics
async function getStatistics() {
  const response = await fetch(`${BASE_URL}/statistics/summary`);
  const stats = await response.json();
  
  console.log('Statistics:', stats);
  return stats;
}

// Usage
getApplications();
updateApplicationStatus(1, 'applied', 'Submitted via portal');
getStatistics();
```

### cURL Examples

```bash
# List applications
curl http://localhost:8000/api/v1/applications

# Filter by status
curl "http://localhost:8000/api/v1/applications?status=reached_out"

# Pagination
curl "http://localhost:8000/api/v1/applications?limit=10&offset=20"

# Get specific application
curl http://localhost:8000/api/v1/applications/1

# Update application status
curl -X PUT http://localhost:8000/api/v1/applications/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "applied", "notes": "Submitted via company portal"}'

# Get emails for application
curl http://localhost:8000/api/v1/applications/1/emails

# List all emails
curl http://localhost:8000/api/v1/emails

# List recruiters
curl http://localhost:8000/api/v1/recruiters

# Get statistics
curl http://localhost:8000/api/v1/statistics/summary
```

## Integration Guide

### Building a Web Dashboard

**Step 1**: Start the API server

```bash
cv-mailer-api
```

**Step 2**: Create React/Vue/Svelte frontend

**Example React Component**:

```tsx
// components/ApplicationsList.tsx
import { useEffect, useState } from 'react';

interface Application {
  id: number;
  company_name: string;
  position: string;
  status: string;
}

export default function ApplicationsList() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/api/v1/applications')
      .then(r => r.json())
      .then(data => {
        setApplications(data.items);
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <div>
      <h1>Job Applications</h1>
      <table>
        <thead>
          <tr>
            <th>Company</th>
            <th>Position</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {applications.map(app => (
            <tr key={app.id}>
              <td>{app.company_name}</td>
              <td>{app.position}</td>
              <td>{app.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

### Mobile App Integration

Use the same API endpoints from React Native, Flutter, or native apps:

```dart
// Flutter example
import 'package:http/http.dart' as http;
import 'dart:convert';

Future<List<Application>> fetchApplications() async {
  final response = await http.get(
    Uri.parse('http://localhost:8000/api/v1/applications')
  );
  
  if (response.statusCode == 200) {
    final data = jsonDecode(response.body);
    return (data['items'] as List)
        .map((json) => Application.fromJson(json))
        .toList();
  } else {
    throw Exception('Failed to load applications');
  }
}
```

### Webhooks (Future Enhancement)

For real-time updates, consider adding webhooks:

```python
# api/routers/webhooks.py
@router.post("/webhooks/register")
async def register_webhook(url: str, events: List[str]):
    # Store webhook URL
    # Trigger on events: email_sent, status_changed, etc.
    ...
```

### CORS Configuration

For web frontends on different domains, CORS is already configured:

```python
# api/app.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Production**: Restrict `allow_origins` to your domain.

## API Documentation

### Interactive Documentation

When the server is running, visit:

- **Swagger UI**: <http://localhost:8000/docs>
  - Interactive API explorer
  - Try endpoints directly
  - See request/response schemas

- **ReDoc**: <http://localhost:8000/redoc>
  - Clean, readable documentation
  - Better for sharing with team

### OpenAPI Schema

Get the OpenAPI schema:

```bash
curl http://localhost:8000/openapi.json > api-schema.json
```

Use this schema to:

- Generate client libraries
- Import into Postman
- Create API mocks

## Performance Considerations

### Database Connection Pooling

For production, consider connection pooling:

```python
# utils/database.py
from sqlalchemy.pool import QueuePool

def get_engine():
    return create_engine(
        database_url,
        poolclass=QueuePool,
        pool_size=10,
        max_overflow=20
    )
```

### Caching

Add caching for expensive queries:

```python
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

@router.get("/statistics/summary")
@cache(expire=60)  # Cache for 60 seconds
async def get_summary():
    ...
```

### Rate Limiting

Protect API from abuse:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/v1/applications")
@limiter.limit("100/minute")
async def list_applications():
    ...
```

## Deployment

### Using Docker

```dockerfile
# Dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . .

RUN pip install -e ".[api]"

EXPOSE 8000
CMD ["cv-mailer-api"]
```

```bash
docker build -t cv-mailer-api .
docker run -p 8000:8000 cv-mailer-api
```

### Using Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - DATABASE_PATH=/app/data/cv_mailer.db
```

### Production Considerations

- Use PostgreSQL instead of SQLite
- Enable authentication/authorization
- Configure proper CORS origins
- Add rate limiting
- Set up monitoring (Sentry, DataDog)
- Use HTTPS (reverse proxy with Nginx)

## Support

- **Issues**: <https://github.com/lakshyads/cv-mailer/issues>
- **Documentation**: This file and `/docs`
- **API Docs**: <http://localhost:8000/docs> (when running)

## Version History

- **v1.0.0** (December 2025): Initial API release
  - Complete CRUD for applications
  - Email records management
  - Recruiter management
  - Statistics endpoints
  - Auto-generated documentation

## Future Enhancements

- [ ] Authentication (OAuth2/JWT)
- [ ] Webhooks for real-time updates
- [ ] Batch operations
- [ ] Export to CSV/PDF
- [ ] Email template management via API
- [ ] Schedule email sending
- [ ] Analytics dashboard data
- [ ] LinkedIn integration
- [ ] Calendar integration for interviews
