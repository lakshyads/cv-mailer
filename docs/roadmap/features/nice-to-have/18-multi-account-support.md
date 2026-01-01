# Multi-Account Support

**Priority**: Nice-to-Have  
**Status**: Not Started  
**Phase**: Phase 6 - Enterprise (Q4 2026)  
**Estimated Timeline**: Q4 2026

---

## Description

Manage multiple Gmail accounts from a single CV Mailer instance. Enables using different email addresses for different job types, A/B testing from addresses, and managing regional accounts.

**Key Goals**:
- Support multiple Gmail accounts
- Account selection per application
- Per-account rate limits
- Unified dashboard
- Account switching

---

## Use Cases

1. **Different Email Addresses**: Use different emails for different job types (tech vs. non-tech)
2. **A/B Testing**: Test different from addresses for response rates
3. **Regional Accounts**: Manage accounts for different regions
4. **Account Separation**: Separate personal and professional job applications
5. **Account Management**: Manage multiple accounts in one place

---

## Implementation Details

### Account Management

#### Multiple OAuth Tokens

- Store multiple OAuth tokens securely
- Associate tokens with account identifiers
- Token refresh per account
- Account authentication management

#### Account Configuration

- Account name/identifier
- Account email address
- Account type/category (optional)
- Default account selection
- Account active/inactive status

### Account Selection

#### Per-Application Account

- Select Gmail account when creating application
- Store account association with application
- Use selected account for email sending
- Account selection in email composer

#### Default Account

- Set default account for new applications
- Fallback to default if no account selected
- Per-application override

### Rate Limiting

#### Per-Account Rate Limits

- Track rate limits per account
- Separate daily email limits per account
- Per-account rate limit enforcement
- Rate limit status per account

#### Unified Rate Limiting

- Option: Shared rate limits across accounts
- Option: Per-account rate limits
- Configurable rate limiting strategy

### Unified Dashboard

#### Account Switching

- Switch between accounts in UI
- Filter applications by account
- Account-specific statistics
- Unified view or account-separated view

#### Statistics

- Per-account statistics
- Aggregate statistics across accounts
- Account comparison
- Account performance metrics

### Database Changes

#### Account Model

- `id`, `name`, `email`, `oauth_token` (encrypted)
- `is_active`, `is_default`
- `created_at`, `updated_at`

#### Application-Account Association

- Add `account_id` to `JobApplication` model
- Link applications to accounts
- Account filtering and queries

---

## Technical Considerations

### OAuth Token Storage

- Store tokens securely (encrypted)
- Token refresh per account
- Handle token expiration
- Account authentication errors

### Email Sending

- Use correct account token for sending
- Account selection in email service
- Error handling per account
- Account-specific email tracking

### User Experience

- Clear account selection UI
- Account indicators in UI
- Easy account switching
- Account management interface

---

## Dependencies

- OAuth token management (multiple tokens)
- Email service updates (account selection)
- Database schema updates
- UI components for account management
- Rate limiting updates

---

## Related Features

- Gmail Integration (already implemented) - Extends with multiple accounts
- [Authentication](../medium-priority/08-authentication.md) - May integrate with user accounts
- Application Management (already implemented) - Account association

---

## Benefits

- ✅ Flexibility in email address usage
- ✅ A/B testing capabilities
- ✅ Account separation and organization
- ✅ Unified management
- ✅ Regional account support

---

## Success Criteria

- [ ] Multiple Gmail accounts can be configured
- [ ] Account selection works per application
- [ ] Per-account rate limiting works
- [ ] Unified dashboard displays correctly
- [ ] Account switching works smoothly
- [ ] Token management is secure

---

**Last Updated**: January 2026

