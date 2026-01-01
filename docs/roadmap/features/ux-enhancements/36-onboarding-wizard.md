# Onboarding Wizard

**Priority**: UX Enhancement  
**Status**: Not Started  
**Phase**: Future  
**Estimated Timeline**: TBD

---

## Description

Interactive setup wizard for first-time users. Guides users through initial setup, configuration, and first use of CV Mailer.

**Key Goals**:
- Step-by-step setup guidance
- Interactive configuration
- Connection testing
- First application creation
- Test email sending
- Smooth onboarding experience

---

## Implementation Details

### Wizard Steps

#### Step 1: Welcome Message

- Welcome to CV Mailer
- Overview of features
- What to expect
- Next steps introduction

#### Step 2: Check Python Version

- Verify Python version (3.11+)
- Check if requirements met
- Provide upgrade instructions if needed

#### Step 3: Create Virtual Environment

- Check if venv exists
- Offer to create venv
- Guide through activation

#### Step 4: Install Dependencies

- Check if dependencies installed
- Offer to install
- Show installation progress

#### Step 5: Configure `.env`

- Interactive prompts for configuration
- Guide through each setting
- Validate input
- Save to `.env` file

**Configuration Items**:
- Gmail credentials path
- Spreadsheet ID
- Resume file path
- Email settings
- Rate limits

#### Step 6: Set up Google Cloud Credentials

- Guide through Google Cloud setup
- OAuth flow assistance
- Credentials file placement
- Token generation

#### Step 7: Test Connections

- Test Gmail connection
- Test Sheets connection
- Verify credentials
- Show test results

#### Step 8: Create First Application

- Guide through application creation
- Sample application (optional)
- Application form assistance

#### Step 9: Send Test Email

- Generate test email
- Preview email
- Send test email
- Verify delivery

### Implementation

#### Interactive Prompts

- Use `questionary` or similar
- Step-by-step guidance
- Validation and error handling
- Skip/back options

#### CLI Command

```bash
cv-mailer setup
```

#### Progress Tracking

- Show progress through steps
- Allow skipping optional steps
- Save progress (resume later)
- Completion confirmation

---

## Dependencies

- Interactive prompt library (questionary)
- Configuration management
- Connection testing
- Application creation
- Email sending

---

## Related Features

- [Configuration Validation](../ux-enhancements/35-configuration-validation.md) - Uses connection tests
- Setup Guide (manual setup alternative)

---

## Benefits

- ✅ Easier first-time setup
- ✅ Reduced setup errors
- ✅ Better user experience
- ✅ Faster time to first use
- ✅ Guided configuration

---

## Success Criteria

- [ ] Wizard guides users through setup
- [ ] All steps work correctly
- [ ] Configuration is saved correctly
- [ ] Connections are tested
- [ ] First application is created
- [ ] Test email is sent
- [ ] Users can complete setup successfully

---

**Last Updated**: January 2026

