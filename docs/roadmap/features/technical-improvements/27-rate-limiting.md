# Rate Limiting for API

**Priority**: Technical Improvement | Needed for Production  
**Status**: Not Started  
**Phase**: Phase 5 - Scalability (Q3 2026)  
**Estimated Timeline**: Q3 2026

---

## Description

Protect API from abuse with rate limiting. Limits requests per IP address and per endpoint to prevent abuse and ensure fair usage.

**Key Goals**:
- Rate limit per IP address
- Rate limit per endpoint
- Configurable limits
- Rate limit headers in responses
- Protection from abuse

---

## Implementation Details

### Rate Limiting Library

#### slowapi (Recommended)

- FastAPI-compatible rate limiter
- Easy to use
- Flexible configuration
- Redis backend support (optional)

**Installation**:
```bash
pip install slowapi
```

### Rate Limiting Configuration

#### Global Limits

- **Per IP**: 100 requests/minute (default)
- Configurable via environment variables
- Different limits for authenticated vs. anonymous users

#### Per-Endpoint Limits

- Different limits per endpoint
- Stricter limits for expensive operations
- More lenient limits for read operations

#### Example Configuration

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.get("/applications")
@limiter.limit("100/minute")
async def list_applications():
    ...
```

### Rate Limit Headers

#### Response Headers

- `X-RateLimit-Limit`: Request limit per window
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Reset time (Unix timestamp)
- `Retry-After`: Seconds until retry (when exceeded)

### Rate Limit Exceeded Response

#### HTTP Status

- `429 Too Many Requests` when limit exceeded

#### Response Body

```json
{
  "error": "Rate limit exceeded",
  "limit": 100,
  "remaining": 0,
  "reset": 1640995200
}
```

### Storage Backend

#### Options

**In-Memory** (default):
- Simple, no external dependency
- Lost on restart
- Single process

**Redis** (recommended for production):
- Persistent across restarts
- Shared across processes
- Better for distributed deployments

### Configuration

```env
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_STORAGE=memory  # or redis
REDIS_URL=redis://localhost:6379/1  # if using Redis
```

---

## Dependencies

- slowapi library
- Redis (optional, for production)
- FastAPI integration

---

## Related Features

- [Authentication](../medium-priority/08-authentication.md) - Different limits for authenticated users
- API endpoints (rate limiting target)

---

## Benefits

- ✅ API protection from abuse
- ✅ Fair usage enforcement
- ✅ Resource protection
- ✅ Production-ready security
- ✅ Cost control

---

## Success Criteria

- [ ] Rate limiting works per IP
- [ ] Per-endpoint limits work
- [ ] Rate limit headers are included
- [ ] 429 responses work correctly
- [ ] Configuration is flexible
- [ ] Redis backend works (if used)

---

**Last Updated**: January 2026

