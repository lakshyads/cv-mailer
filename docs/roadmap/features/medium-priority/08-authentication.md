# Authentication & Authorization

**Priority**: Medium (Reprioritized from High)  
**Status**: Not Started  
**Phase**: Phase 6 - Enterprise (Q4 2026)  
**Estimated Timeline**: Q4 2026 (or earlier if deploying publicly)

---

## Description

Secure API access for production deployment. Implements OAuth2 with JWT tokens, user registration/login, role-based access control (RBAC), and API key management. This feature is essential for multi-user deployments or public API access.

**Priority Note**: Reprioritized to Medium - defer until conversation features are complete. High priority only if deploying publicly before conversation features are implemented.

**Key Goals**:
- Secure API access with authentication
- User registration and login
- Role-based access control
- API key management for integrations
- Multi-user support

---

## Use Cases

1. **Public Deployment**: Secure API access when deploying publicly
2. **Multi-User Support**: Multiple users accessing the same instance
3. **API Integrations**: API keys for third-party integrations
4. **Access Control**: Role-based permissions for different users
5. **Security**: Protect sensitive application data

---

## Implementation Details

### Authentication Methods

#### OAuth2 with JWT Tokens

- OAuth2 password flow for user authentication
- JWT tokens for stateless authentication
- Refresh tokens for token renewal
- Token expiration and refresh logic
- Secure token storage (HTTP-only cookies or secure storage)

#### User Registration/Login

- User registration endpoint
- Email verification (optional)
- Password reset functionality
- Login endpoint with credential validation
- Session management

#### API Key Management

- Generate API keys for integrations
- Revoke API keys
- API key authentication middleware
- Rate limiting per API key
- Track API key usage

### Role-Based Access Control (RBAC)

#### Roles

- **Admin**: Full access to all features and settings
- **User**: Standard user access (manage own applications)
- **Read-only**: View-only access
- **API User**: API-only access with limited permissions

#### Permissions

- Application CRUD operations
- Email sending permissions
- Settings access
- Statistics access
- API access levels

### Tech Stack

- **JWT**: `python-jose` for JWT token handling
- **Password Hashing**: `passlib` with bcrypt
- **FastAPI Security**: FastAPI Security utilities
- **Database**: User and session models

### Database Changes

#### New Models

**User Model**:
- `id` (Integer, primary key)
- `email` (String, unique, indexed)
- `username` (String, unique, optional)
- `hashed_password` (String)
- `is_active` (Boolean, default: true)
- `is_admin` (Boolean, default: false)
- `role` (Enum: admin, user, read_only, api_user)
- `created_at` (DateTime)
- `updated_at` (DateTime)
- `last_login` (DateTime, nullable)

**API Key Model**:
- `id` (Integer, primary key)
- `user_id` (Integer, ForeignKey)
- `key` (String, unique, indexed)
- `name` (String) - User-friendly name for the key
- `is_active` (Boolean, default: true)
- `created_at` (DateTime)
- `last_used_at` (DateTime, nullable)
- `usage_count` (Integer, default: 0)

**Session Model** (optional, if using database sessions):
- `id` (Integer, primary key)
- `user_id` (Integer, ForeignKey)
- `token` (String, unique)
- `expires_at` (DateTime)
- `created_at` (DateTime)

### API Endpoints

#### Authentication Endpoints

- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login (returns JWT token)
- `POST /api/v1/auth/refresh` - Refresh JWT token
- `POST /api/v1/auth/logout` - Logout (invalidate token)
- `POST /api/v1/auth/forgot-password` - Request password reset
- `POST /api/v1/auth/reset-password` - Reset password with token

#### User Management Endpoints

- `GET /api/v1/auth/me` - Get current user info
- `PUT /api/v1/auth/me` - Update current user
- `PUT /api/v1/auth/change-password` - Change password

#### API Key Endpoints

- `GET /api/v1/auth/api-keys` - List user's API keys
- `POST /api/v1/auth/api-keys` - Generate new API key
- `DELETE /api/v1/auth/api-keys/{id}` - Revoke API key

#### Admin Endpoints (if admin role)

- `GET /api/v1/admin/users` - List all users
- `PUT /api/v1/admin/users/{id}` - Update user
- `DELETE /api/v1/admin/users/{id}` - Delete user

### Security Considerations

#### Password Security

- Hash passwords with bcrypt (via passlib)
- Enforce password complexity requirements
- Password strength validation
- Rate limiting on login attempts
- Account lockout after failed attempts

#### Token Security

- Secure JWT secret key (environment variable)
- Token expiration (short-lived access tokens)
- Refresh token rotation
- Token revocation capability
- HTTPS-only token transmission

#### API Security

- API key validation
- Rate limiting per user/API key
- CORS configuration
- Input validation and sanitization
- SQL injection prevention (already handled by SQLAlchemy)

---

## Dependencies

- `python-jose` for JWT
- `passlib[bcrypt]` for password hashing
- FastAPI Security utilities
- Database models for User, API Key, Session
- Authentication middleware
- Password reset email functionality (if implementing email verification)

---

## Related Features

- [Settings Page](../high-priority/04-settings-page.md) - User-specific settings
- [Notification System](../medium-priority/14-notification-system.md) - User notifications
- Multi-user support (implicit requirement)

---

## Benefits

- ✅ Secure API access for production
- ✅ Multi-user support capability
- ✅ API key management for integrations
- ✅ Role-based access control
- ✅ Industry-standard authentication
- ✅ Production-ready security

---

## Success Criteria

- [ ] Users can register and login
- [ ] JWT tokens are issued and validated correctly
- [ ] API keys can be generated and revoked
- [ ] Role-based access control works
- [ ] Password reset functionality works
- [ ] Security best practices are followed
- [ ] Multi-user isolation works correctly
- [ ] Performance is acceptable (auth doesn't slow down API)

---

## Migration Strategy

For existing single-user deployments:
- Optional: Create default admin user during migration
- Existing data can be associated with default user
- No breaking changes for single-user setups
- Migration script to create initial user

---

**Last Updated**: January 2026

