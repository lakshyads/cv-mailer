# Database Performance Optimization

**Priority**: Technical Improvement  
**Status**: SQLite Sufficient | PostgreSQL Optional  
**Phase**: Phase 5 - Scalability (Q3 2026)  
**Estimated Timeline**: Q3 2026

---

## Description

Database performance optimizations including indexes, connection pooling, query optimization, and optional PostgreSQL migration. Improves query performance and supports larger datasets.

**Current State**: SQLite with basic indexes (sufficient for current use)  
**Future State**: Optimized SQLite or PostgreSQL for production scale

**Key Goals**:
- Database indexes on frequently queried fields
- Connection pooling for API
- Query optimization (eager loading)
- Caching for expensive queries
- PostgreSQL migration (optional)

---

## Implementation Details

### Database Indexes

#### Current Indexes

Already implemented (from previous work):
- `JobApplication`: status, company_name+position, created_at, spreadsheet_row_id
- `EmailRecord`: job_application_id, status, sent_at, recipient_email
- `Recruiter`: email (unique)

#### Additional Indexes (if needed)

- Indexes on foreign keys (if not already covered)
- Composite indexes for common query patterns
- Full-text search indexes (if implementing search)

### Connection Pooling

#### SQLite

- SQLite doesn't require connection pooling (single connection)
- Multiple connections can cause locking issues
- Current approach is sufficient

#### PostgreSQL

- Use SQLAlchemy connection pooling
- Configure pool size, max overflow
- Connection pooling improves performance

### Query Optimization

#### Eager Loading

- Use `joinedload` or `selectinload` for relationships
- Avoid N+1 query problems
- Already implemented in repositories

#### Query Optimization Techniques

- Select only needed columns
- Use database-specific optimizations
- Batch operations where possible
- Use database functions for aggregation

### Caching

#### Query Result Caching

- Cache expensive queries (statistics, aggregations)
- Use Redis or in-memory cache
- Cache invalidation strategy
- TTL-based expiration

#### Implementation

- Cache statistics queries (60 seconds TTL)
- Cache application lists per filter
- Cache expensive aggregations

### PostgreSQL Migration

#### Migration Path

**Option 1**: Keep SQLite for small deployments
- SQLite is sufficient for single-user deployments
- No migration needed
- Simpler deployment

**Option 2**: Migrate to PostgreSQL
- Better for multi-user deployments
- Better concurrency support
- Better performance at scale

#### Configuration

```python
# config/settings.py
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/cv_mailer.db")
# For PostgreSQL: postgresql://user:pass@host:5432/cv_mailer
```

#### Migration Steps

1. Install PostgreSQL
2. Create database
3. Update DATABASE_URL
4. Run migrations (Alembic)
5. Test thoroughly

---

## Dependencies

- Database indexes (already implemented)
- Connection pooling (if using PostgreSQL)
- Caching layer (Redis, if implementing)
- Database migrations (Alembic, for schema changes)

---

## Related Features

- [Database Migrations](../technical-improvements/21-database-migrations.md) - For schema changes
- [Caching Layer](../technical-improvements/26-caching-layer.md) - For query caching
- Application repositories (already optimized)

---

## Benefits

- ✅ Better query performance
- ✅ Supports larger datasets
- ✅ Improved concurrency (PostgreSQL)
- ✅ Scalability
- ✅ Better production performance

---

## Success Criteria

- [ ] Database indexes are optimized
- [ ] Query performance is acceptable
- [ ] Connection pooling works (if PostgreSQL)
- [ ] Caching improves performance
- [ ] PostgreSQL migration works (if implemented)

---

**Last Updated**: January 2026

