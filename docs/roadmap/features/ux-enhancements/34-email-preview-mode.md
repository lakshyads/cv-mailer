# Email Preview Mode (CLI)

**Priority**: UX Enhancement  
**Status**: Partially Covered by Email Editing  
**Phase**: Future  
**Estimated Timeline**: TBD

---

## Description

CLI command to preview emails before sending. Allows testing email templates, variable substitution, and sending test emails.

**Note**: Basic preview is now part of [Email Editing & Customization](../high-priority/03-email-editing-customization.md) feature (web UI). This adds CLI preview mode.

**Key Goals**:
- Preview emails from CLI
- Test variable substitution
- HTML preview in browser
- Send test email to self
- Template testing

---

## Implementation Details

### CLI Command

```bash
cv-mailer preview --application-id 1
```

### Features

#### HTML Preview in Browser

- Generate email HTML
- Open in default browser
- Show rendered email
- Test email rendering

#### Variable Substitution Preview

- Show template with variables substituted
- Test different data scenarios
- Validate template syntax

#### Preview with Different Data

- Preview with sample data
- Preview with application data
- Custom data override
- Multiple preview scenarios

#### Send Test Email to Self

- Send preview email to your own email
- Test email delivery
- Test email formatting
- Verify email content

### Implementation

- Email template rendering
- Variable substitution
- HTML generation
- Browser opening
- Test email sending

---

## Dependencies

- Email template service
- Email sending service
- Browser opening (webbrowser module)
- Application data access

---

## Related Features

- [Email Editing & Customization](../high-priority/03-email-editing-customization.md) - Web UI preview
- Email templates (preview target)

---

## Benefits

- ✅ Test emails before sending
- ✅ Verify template rendering
- ✅ Test variable substitution
- ✅ Better email quality

---

## Success Criteria

- [ ] Email preview works from CLI
- [ ] Browser preview opens correctly
- [ ] Variable substitution works
- [ ] Test email sending works

---

**Last Updated**: January 2026

