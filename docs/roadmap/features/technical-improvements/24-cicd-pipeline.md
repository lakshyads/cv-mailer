# CI/CD Pipeline

**Priority**: Technical Improvement  
**Status**: Not Started  
**Phase**: Phase 5 - Scalability (Q3 2026)  
**Estimated Timeline**: Q3 2026

---

## Description

Automated testing and deployment pipeline. Runs linting, testing, and builds on every commit. Enables automated quality checks and deployment.

**Key Goals**:
- Automated linting and formatting checks
- Automated test execution
- Docker image builds
- Deployment automation (optional)
- Quality gates

---

## Implementation Details

### Platform Options

#### GitHub Actions

- **Pros**: Integrated with GitHub, easy setup
- **File**: `.github/workflows/ci.yml`

#### GitLab CI

- **Pros**: Integrated with GitLab, flexible
- **File**: `.gitlab-ci.yml`

**Recommendation**: GitHub Actions (if using GitHub)

### Pipeline Stages

#### Lint Stage

**Tools**:
- `black` - Code formatting
- `isort` - Import sorting
- `flake8` - Linting
- `mypy` - Type checking

**Commands**:
```bash
black --check src/ tests/
isort --check src/ tests/
flake8 src/
mypy src/
```

#### Test Stage

**Tools**:
- `pytest` - Test execution
- `pytest-cov` - Coverage reporting

**Commands**:
```bash
pytest tests/ --cov=src/cv_mailer --cov-report=xml
```

#### Build Stage

**Docker Build** (if using Docker):
```bash
docker build -t cv-mailer:${{ github.sha }} .
```

#### Deploy Stage (Optional)

- Deploy to staging/production
- Conditional on branch/tag
- Manual approval for production

### GitHub Actions Workflow

#### Example Workflow

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install black isort flake8 mypy
      - run: black --check src/ tests/
      - run: isort --check src/ tests/
      - run: flake8 src/
      - run: mypy src/

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -e ".[dev]"
      - run: pytest tests/ --cov --cov-report=xml
      - uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: docker build -t cv-mailer:${{ github.sha }} .
```

### Quality Gates

- Linting must pass
- All tests must pass
- Coverage threshold (e.g., 80%)
- Type checking must pass

### Deployment (Optional)

- Staging deployment on merge to `develop`
- Production deployment on tag/release
- Manual approval for production
- Rollback capability

---

## Dependencies

- GitHub/GitLab repository
- CI/CD platform (GitHub Actions, GitLab CI)
- Test suite (pytest)
- Linting tools (black, isort, flake8, mypy)
- Docker (if building images)

---

## Related Features

- [Testing Suite](../technical-improvements/22-testing-suite.md) - CI runs tests
- [Docker Support](../technical-improvements/23-docker-support.md) - CI builds Docker images

---

## Benefits

- ✅ Automated quality checks
- ✅ Early bug detection
- ✅ Consistent code quality
- ✅ Automated deployment
- ✅ Team collaboration

---

## Success Criteria

- [ ] Linting runs on every commit
- [ ] Tests run on every commit
- [ ] Build succeeds on CI
- [ ] Quality gates are enforced
- [ ] Deployment works (if configured)

---

**Last Updated**: January 2026

