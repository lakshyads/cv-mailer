# Contributing to CV Mailer

Want to implement any of the features from our [Roadmap](ROADMAP.md)? Here's how to get started.

---

## 🤝 Contributing Process

1. **Open an issue** to discuss the feature
   - Check if the feature is already being worked on
   - Discuss approach and implementation details
   - Get feedback before starting work

2. **Create a feature branch** from `main`

   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Follow existing code style**
   - Use Black for code formatting
   - Use isort for import sorting
   - Follow type hints (mypy)
   - Follow existing code patterns

4. **Add tests** for new functionality
   - Unit tests for services, parsers, utils
   - Integration tests for database, APIs
   - API tests using FastAPI TestClient
   - Update test coverage

5. **Update relevant documentation**
   - Update API documentation if adding endpoints
   - Update user guides if adding user-facing features
   - Update CHANGELOG.md with your changes
   - Add/update feature specs in roadmap/features/ if applicable

6. **Submit a pull request**
   - Clear description of changes
   - Reference related issues
   - Ensure all tests pass
   - Request review from maintainers

---

## 🔧 Development Setup

```bash
# Clone the repository
git clone https://github.com/lakshyads/cv-mailer.git
cd cv-mailer

# Install in development mode
pip install -e ".[dev]"
```

This installs:

- The CV Mailer package in editable mode
- All development dependencies (testing, linting, formatting)

---

## ✅ Code Quality Standards

We use several tools to maintain code quality:

```bash
# Format code (Black)
black src/ tests/

# Sort imports (isort)
isort src/ tests/

# Type checking (mypy)
mypy src/

# Linting (flake8)
flake8 src/

# Run tests (pytest)
pytest
```

**Before submitting a PR, ensure:**

- ✅ All code is formatted with Black
- ✅ Imports are sorted with isort
- ✅ Type checking passes with mypy
- ✅ No linting errors from flake8
- ✅ All tests pass with pytest

---

## 📝 Feature Request Template

To request a new feature, open an issue using this template:

**Title**: `[Feature Request] <Brief Description>`

**Content**:

```markdown
## Description
What feature would you like to see?

## Use Case
Why is this feature needed? What problem does it solve?

## Proposed Solution
How would you implement this?

## Alternatives
What alternatives have you considered?

## Additional Context
Any other information, mockups, or examples?
```

---

## 🎯 Feature Implementation Guide

When implementing a feature from the roadmap:

1. **Review the feature spec**
   - Read the detailed feature spec in `docs/roadmap/features/`
   - Understand the requirements and scope
   - Check dependencies on other features

2. **Design before coding**
   - Plan the database changes (if any)
   - Design API endpoints (if any)
   - Plan UI components (if any)
   - Consider backward compatibility

3. **Follow the architecture**
   - Service layer for business logic
   - Repository layer for data access
   - API routers for endpoints
   - Follow existing patterns

4. **Write comprehensive tests**
   - Test happy paths
   - Test error cases
   - Test edge cases
   - Maintain or improve test coverage

5. **Update documentation**
   - API documentation (if adding endpoints)
   - User guides (if adding user-facing features)
   - CHANGELOG.md
   - Update feature status in roadmap

---

## 📚 Related Documentation

- **[Roadmap](ROADMAP.md)** - Overview of planned features
- **[Architecture Guide](../design/ARCHITECTURE.md)** - System architecture and design patterns
- **[API Guide](../API_GUIDE.md)** - REST API documentation
- **[Setup Guide](../SETUP_GUIDE.md)** - Development environment setup
- **[Changelog](../CHANGELOG.md)** - Feature history and changes

---

## 📧 Contact

- **Issues**: <https://github.com/lakshyads/cv-mailer/issues>
- **Email**: <lakshyads.96@gmail.com>
- **LinkedIn**: <https://www.linkedin.com/in/lakshya-dev-singh>

---

**Thank you for contributing to CV Mailer!** 🎉
