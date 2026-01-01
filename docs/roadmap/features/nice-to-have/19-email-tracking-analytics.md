# Email Tracking & Analytics

**Priority**: Nice-to-Have  
**Status**: Not Started  
**Phase**: Future  
**Estimated Timeline**: TBD

---

## Description

Track email opens and link clicks using pixel tracking and link redirects. Provides insights into email engagement and recipient behavior.

**Key Goals**:
- Track email opens (pixel tracking)
- Track link clicks (redirect tracking)
- Read receipts
- Click-through rate analytics
- Engagement metrics

---

## Use Cases

1. **Engagement Tracking**: See if emails are being opened
2. **Link Analytics**: Track which links are clicked
3. **Response Prediction**: Opens/clicks may indicate interest
4. **Optimization**: Optimize emails based on engagement data
5. **Follow-up Timing**: Know when to follow up based on opens

---

## Implementation Details

### Pixel Tracking

#### Implementation

- 1x1 transparent image (tracking pixel) in email HTML
- Unique pixel URL per email
- Server endpoint to log opens
- Store open timestamp and metadata

#### Technical Details

- Generate unique tracking pixel URL per email
- Embed pixel in email HTML
- Track pixel requests (email opens)
- Store open events in database
- Handle multiple opens (first open, total opens)

#### Database Changes

- Add `EmailRecord.tracking_pixel_id` (String, unique)
- Track opens: `EmailOpen` model or extend `EmailRecord`
- Store: `email_id`, `opened_at`, `ip_address`, `user_agent`

### Link Tracking

#### Implementation

- Replace links in emails with tracking redirect URLs
- Short link format: `https://cv-mailer.com/track/abc123`
- Redirect to original URL after tracking
- Log click events

#### Technical Details

- Generate short links for email links
- Store original URL mapping
- Track click events
- Redirect to original URL
- Handle multiple clicks per link

#### Database Changes

- `TrackedLink` model: `id`, `email_id`, `original_url`, `short_code`, `click_count`
- `LinkClick` model: `id`, `link_id`, `clicked_at`, `ip_address`, `user_agent`

### Read Receipts

#### Implementation

- Optional read receipt request in email
- User confirmation for read receipt
- Not widely supported by email clients
- Limited functionality

### Analytics & Metrics

#### Metrics

- **Open Rate**: Percentage of emails opened
- **Click-Through Rate (CTR)**: Percentage of emails with clicks
- **Click Rate**: Percentage of links clicked
- **Engagement Score**: Combined metric (opens + clicks)
- **Time to Open**: Time from send to first open
- **Time to Click**: Time from send to first click

#### Analytics Dashboard

- Email engagement overview
- Open rate trends
- Click-through rate trends
- Link performance
- Engagement by application/recruiter

### Privacy Considerations

**Important**: Email tracking raises privacy concerns.

**Best Practices**:
- Inform recipients about tracking (privacy policy)
- Provide opt-out mechanism
- Respect recipient privacy
- Comply with email marketing regulations (GDPR, CAN-SPAM)
- Clear disclosure in privacy policy

---

## Technical Considerations

### Tracking Implementation

- Tracking pixel endpoint
- Link redirect endpoint
- Unique identifier generation
- Database schema for tracking data
- Analytics aggregation

### Performance

- Lightweight tracking endpoints
- Efficient database queries
- Caching for analytics
- Async processing for tracking events

### Privacy & Compliance

- Privacy policy disclosure
- Opt-out mechanism
- Data retention policies
- GDPR compliance (if applicable)
- CAN-SPAM compliance (if applicable)

---

## Dependencies

- Email HTML modification (add tracking pixel, replace links)
- Tracking endpoint implementation
- Database schema for tracking data
- Analytics service
- Privacy policy updates

---

## Related Features

- Email sending (already implemented) - Adds tracking to emails
- [Advanced Analytics](../medium-priority/09-advanced-analytics.md) - Email engagement analytics

---

## Benefits

- ✅ Email engagement insights
- ✅ Link performance tracking
- ✅ Better follow-up timing
- ✅ Email optimization data
- ✅ Response prediction

---

## Success Criteria

- [ ] Email opens are tracked correctly
- [ ] Link clicks are tracked correctly
- [ ] Analytics dashboard displays metrics
- [ ] Privacy considerations are addressed
- [ ] Performance is acceptable
- [ ] Compliance requirements are met

---

## Legal/Privacy Notes

- **Important**: Email tracking may violate privacy expectations
- Inform recipients about tracking
- Provide opt-out mechanism
- Comply with applicable regulations (GDPR, CAN-SPAM)
- Consider ethical implications
- May not work with all email clients (image blocking, link preview)

---

**Last Updated**: January 2026

