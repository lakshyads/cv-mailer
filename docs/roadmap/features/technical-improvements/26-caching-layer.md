# Caching Layer

**Priority**: Technical Improvement  
**Status**: Not Started  
**Phase**: Phase 5 - Scalability (Q3 2026)  
**Estimated Timeline**: Q3 2026

---

## Description

Cache expensive operations to improve performance. Caches statistics, application lists, and other frequently accessed data to reduce database load and improve response times.

**Key Goals**:
- Cache expensive queries
- Reduce database load
- Improve API response times
- Configurable cache expiration
- Cache invalidation strategy

---

## Implementation Details

### Caching Technology

#### Redis (Recommended)

- **Pros**: Fast, scalable, persistent, advanced features
- **Cons**: Requires Redis server
- **Use Case**: Production deployments

#### In-Memory Cache (Alternative)

- **Pros**: Simple, no external dependency
- **Cons**: Lost on restart, single process
- **Use Case**: Development, small deployments

**Recommendation**: Redis for production, in-memory for development

### Cache Use Cases

#### Statistics Caching

- Cache statistics queries (60 seconds TTL)
- Expensive aggregations
- Status breakdowns
- Response rate calculations

#### Application Lists

- Cache filtered application lists per filter combination
- Short TTL (10-30 seconds)
- Invalidate on application updates

#### Sheets Data

- Cache Google Sheets data (if applicable)
- Per-sheet caching
- TTL based on update frequency

#### Template Renders

- Cache rendered email templates
- Key: template + data hash
- Longer TTL (5-10 minutes)

### Implementation

#### FastAPI Cache

Use `fastapi-cache2` or similar:

```python
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

@cache(expire=60)
async def get_statistics():
    ...
```

#### Manual Caching

```python
import redis
from functools import wraps

redis_client = redis.Redis(...)

def cache_result(key_prefix, ttl=60):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{key_prefix}:{hash((args, kwargs))}"
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator
```

### Cache Invalidation

#### Strategies

- **TTL-based**: Automatic expiration
- **Manual invalidation**: Invalidate on updates
- **Event-based**: Invalidate on specific events
- **Key-based**: Invalidate specific cache keys

#### Invalidation Triggers

- Application created/updated/deleted
- Email sent
- Status changed
- Statistics recalculated

### Configuration

#### Redis Configuration

```env
REDIS_URL=redis://localhost:6379/0
CACHE_TTL_STATISTICS=60
CACHE_TTL_APPLICATIONS=30
CACHE_ENABLED=true
```

#### Cache Settings

- Enable/disable caching
- TTL per cache type
- Cache key prefixes
- Redis connection settings

---

## Dependencies

- Redis (if using Redis)
- FastAPI cache library (fastapi-cache2)
- Cache invalidation logic

---

## Related Features

- [Database Performance](../technical-improvements/25-database-performance.md) - Caching reduces database load
- Statistics service (caching target)
- Application service (caching target)

---

## Benefits

- ✅ Improved API response times
- ✅ Reduced database load
- ✅ Better scalability
- ✅ Cost reduction (fewer DB queries)
- ✅ Better user experience

---

## Success Criteria

- [ ] Caching reduces database load
- [ ] API response times improve
- [ ] Cache invalidation works correctly
- [ ] Configuration is flexible
- [ ] Performance is acceptable

---

**Last Updated**: January 2026

