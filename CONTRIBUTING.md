# Contributing to Books Store

Thank you for your interest in contributing to the Books Store project! This document provides guidelines and information for contributors.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Code Review Process](#code-review-process)
- [Reporting Bugs](#reporting-bugs)
- [Feature Requests](#feature-requests)

## Getting Started

### Prerequisites

Before contributing, ensure you have the following installed:

- **Python 3.13.5** with uv
- **Docker** and **Docker Compose**
- **Git** for version control

### Development Environment Setup

1. **Fork and Clone the Repository**
   ```bash
   git clone https://github.com/your-username/books_store.git
   cd books_store
   ```

2. **Set Up Environment Variables**
   ```bash
   cp .env.example .env
   # Edit .env with your local configuration
   ```

3. **Start Services with Docker**
   ```bash
   docker-compose up --build
   ```

## Development Setup

### Local Development

### Database Migrations

The project uses Alembic for database migrations:

```bash
cd alembic_migrations
alembic upgrade head
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

## Code Standards

### Python Code Style

We follow PEP 8 with some modifications:

- **Line Length**: 88 characters (Black formatter)
- **Import Order**: isort
- **Type Hints**: Required for all function parameters and return values
- **Docstrings**: Google style docstrings

### Code Formatting

We use ruff tool to maintain code quality:

```bash
# Install development dependencies
pip install black isort ruff

# Lint code
ruff check .
ruff check --fix .

### File Structure

Follow the existing project structure:

```
service_name/
├── main.py
├── pyproject.toml
├── requirements.txt
└── src/
    ├── core/
    │   ├── config.py
    │   ├── logging.py
    │   └── utils.py
    └── services/
        ├── db/
        │   ├── database.py
        │   ├── models/
        │   └── schemas/
        ├── routers/
        └── server.py
```

### Naming Conventions

- **Files**: snake_case (`user_router.py`)
- **Classes**: PascalCase (`UserRouter`)
- **Functions/Methods**: snake_case (`get_user_by_id`)
- **Constants**: UPPER_SNAKE_CASE (`MAX_RETRY_COUNT`)
- **Database Tables**: snake_case (`users`, `product_types`)

### API Design Guidelines

- **RESTful Endpoints**: Use standard HTTP methods
- **Status Codes**: Use appropriate HTTP status codes
- **Error Responses**: Consistent error format
- **Pagination**: Implement for list endpoints
- **Filtering**: Support query parameters for filtering

## Reporting Bugs

### Bug Report Template

When reporting bugs, please include:

```markdown
## Bug Description
Brief description of the issue.

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

## Expected Behavior
What you expected to happen.

## Actual Behavior
What actually happened.

## Environment
- OS: [e.g., Ubuntu 22.04]
- Python Version: [e.g., 3.11.5]
- Docker Version: [e.g., 24.0.5]
- Service: [e.g., server, authorizer, gateway]

## Additional Information
Any other context, logs, or screenshots.
```

## Feature Requests

### Feature Request Template

```markdown
## Feature Description
Clear description of the requested feature.

## Use Case
Why this feature is needed and how it would be used.

## Proposed Solution
Your suggested implementation approach.

## Alternatives Considered
Other approaches you've considered.

## Additional Context
Any other relevant information.
```

Thank you for contributing to the Books Store project! 🚀
