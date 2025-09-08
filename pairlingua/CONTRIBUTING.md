# Contributing to PairLingua

Thank you for your interest in contributing to PairLingua! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

1. **Fork the repository**
2. **Clone your fork**: `git clone https://github.com/your-username/pairlingua.git`
3. **Create a branch**: `git checkout -b feature/your-feature-name`
4. **Set up development environment**: `make setup`

## 🛠️ Development Setup

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Local Development
```bash
# Start all services
make up

# Run backend tests
make test-backend

# Run frontend tests
make test-frontend

# Format code
make format
```

## 📝 Code Style

### Backend (Python)
- Use **Black** for formatting
- Use **flake8** for linting
- Use **isort** for import sorting
- Follow **PEP 8** guidelines
- Maximum line length: 88 characters

### Frontend (TypeScript/React)
- Use **Prettier** for formatting
- Use **ESLint** for linting
- Follow **Airbnb** style guide
- Use **TypeScript** for type safety

### General Guidelines
- Write descriptive commit messages
- Keep functions and classes small and focused
- Add docstrings for Python functions
- Add JSDoc comments for TypeScript functions
- Write tests for new features

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest --cov=app tests/
```

### Frontend Tests
```bash
cd frontend
npm test -- --coverage
```

### Test Coverage
- Maintain at least **80%** test coverage
- Write unit tests for business logic
- Write integration tests for API endpoints
- Write E2E tests for critical user flows

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Description**: Clear description of the issue
2. **Steps to reproduce**: Step-by-step instructions
3. **Expected behavior**: What should happen
4. **Actual behavior**: What actually happens
5. **Environment**: OS, browser, Docker version
6. **Screenshots**: If applicable

## ✨ Feature Requests

For feature requests, please provide:

1. **Problem**: What problem does this solve?
2. **Solution**: Describe your proposed solution
3. **Alternatives**: Alternative solutions considered
4. **Use cases**: Specific use cases and examples

## 🔄 Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new features
3. **Ensure all tests pass**
4. **Update changelog** if applicable
5. **Request review** from maintainers

### Pull Request Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass
- [ ] New tests added
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Changes generate no new warnings
```

## 🏗️ Architecture Guidelines

### Backend
- Follow **Clean Architecture** principles
- Use **dependency injection**
- Separate **business logic** from API layers
- Use **Pydantic** for data validation
- Use **Alembic** for database migrations

### Frontend
- Use **functional components** with hooks
- Follow **component composition** patterns
- Use **TypeScript** for type safety
- Use **Redux Toolkit** for state management
- Use **React Query** for server state

## 📚 Documentation

- Update README if adding new features
- Add docstrings to Python functions
- Add comments for complex logic
- Update API documentation
- Add examples for new functionality

## 🚦 Continuous Integration

All pull requests must pass:
- **Linting** checks
- **Unit tests**
- **Integration tests**
- **Type checking**
- **Security scans**

## 📋 Issue Labels

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Improvements to documentation
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention needed
- `question`: Further information requested

## 🎯 Development Focus Areas

Current focus areas for contributions:

1. **Learning Algorithm**: Improve SM-2 implementation
2. **Gamification**: Add more achievements and rewards
3. **Mobile Experience**: Improve mobile responsiveness
4. **Performance**: Optimize database queries and frontend
5. **Accessibility**: Improve a11y compliance
6. **Testing**: Increase test coverage
7. **Documentation**: Improve guides and examples

## 🤝 Code of Conduct

This project adheres to a Code of Conduct. By participating, you agree to uphold this code.

### Our Standards

**Positive behavior includes:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on community benefits
- Showing empathy towards others

**Unacceptable behavior includes:**
- Harassment or discriminatory language
- Trolling, insulting, or derogatory comments
- Personal or political attacks
- Public or private harassment
- Publishing others' private information

## 📞 Questions?

- Open an issue for bug reports or feature requests
- Use GitHub Discussions for questions and ideas
- Join our community chat for real-time help

Thank you for contributing to PairLingua! 🎉
