# Contributing to ShadowLink

Thank you for your interest in contributing to ShadowLink! This document provides guidelines and information for contributors.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- Basic understanding of URL shortening and web security concepts

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/yourusername/shadowlink.git
   cd shadowlink
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Development Dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Verify Installation**
   ```bash
   pytest
   shadowlink --version
   ```

## Development Workflow

### Branch Naming

- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring
- `test/description` - Test improvements

### Making Changes

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**
   - Write clean, readable code
   - Follow existing code style
   - Add appropriate comments and docstrings

3. **Add Tests**
   ```bash
   # Add tests in tests/ directory
   # Run tests to ensure they pass
   pytest tests/test_your_feature.py
   ```

4. **Update Documentation**
   - Update README.md if needed
   - Add docstrings to new functions/classes
   - Update CHANGELOG.md

### Code Quality Standards

#### Code Formatting
```bash
# Format code with Black
black shadowlink/ tests/

# Check formatting
black --check shadowlink/ tests/
```

#### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=shadowlink --cov-report=html

# Run specific test categories
pytest -m "not slow"  # Skip slow tests
pytest -m integration  # Run only integration tests
```

## Code Style Guidelines

### Python Code Style

- Follow PEP 8 guidelines
- Use Black for code formatting (line length: 100)
- Use type hints for all function parameters and return values
- Write comprehensive docstrings using Google style

#### Example Function

```python
def validate_url(url: str) -> Optional[Match[str]]:
    """Validate if the provided string is a syntactically correct HTTP(S) URL.
    
    Args:
        url: The URL string to validate
        
    Returns:
        A regex match object if valid, None otherwise
        
    Raises:
        ValidationError: If the URL format is invalid
        
    Example:
        >>> validate_url("https://example.com")
        <re.Match object; span=(0, 19), match='https://example.com'>
    """
    # Implementation here
```

### Documentation Style

- Use clear, concise language
- Include code examples where helpful
- Keep line length reasonable (80-100 characters)
- Use proper Markdown formatting

## Testing Guidelines

### Test Structure

```
tests/
├── __init__.py
├── test_shadowlink.py      # Core functionality tests
├── test_cli.py             # CLI interface tests
├── test_config.py          # Configuration tests
├── test_exceptions.py      # Exception handling tests
└── test_integration.py     # Integration tests
```

### Writing Tests

1. **Test Naming**: Use descriptive names
   ```python
   def test_validate_url_with_valid_https_url():
   def test_validate_url_raises_error_for_invalid_format():
   ```

2. **Test Categories**: Use pytest markers
   ```python
   @pytest.mark.slow
   def test_network_dependent_feature():
       pass
   
   @pytest.mark.integration
   def test_full_workflow():
       pass
   ```

3. **Fixtures**: Use fixtures for common test data
   ```python
   @pytest.fixture
   def sample_urls():
       return {
           'valid': ['https://example.com', 'http://test.org'],
           'invalid': ['not-a-url', 'ftp://invalid.com']
       }
   ```

### Test Coverage

- Aim for >90% test coverage
- Test both success and failure cases
- Include edge cases and boundary conditions
- Mock external dependencies

## Pull Request Process

### Before Submitting

1. **Run Full Test Suite**
   ```bash
   pytest
   ```

2. **Check Code Quality**
   ```bash
   black --check shadowlink/ tests/
   ```

3. **Update Documentation**
   - Update README.md if needed
   - Add/update docstrings
   - Update CHANGELOG.md

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring
- [ ] Performance improvement

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Test coverage maintained/improved

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
```

### Review Process

1. **Automated Checks**: All CI checks must pass
2. **Code Review**: At least one maintainer review required
3. **Testing**: Verify tests cover new functionality
4. **Documentation**: Ensure documentation is updated

## Bug Reports

### Before Reporting

1. Check existing issues
2. Verify bug with latest version
3. Test with minimal reproduction case

### Bug Report Template

```markdown
**Bug Description**
Clear description of the bug

**To Reproduce**
Steps to reproduce the behavior:
1. Run command '...'
2. Enter input '...'
3. See error

**Expected Behavior**
What you expected to happen

**Environment**
- OS: [e.g., Ubuntu 20.04]
- Python version: [e.g., 3.10.5]
- ShadowLink version: [e.g., 0.0.1]

**Additional Context**
Any other context about the problem
```

## Feature Requests

### Feature Request Template

```markdown
**Feature Description**
Clear description of the proposed feature

**Use Case**
Why is this feature needed? What problem does it solve?

**Proposed Solution**
How should this feature work?

**Alternatives Considered**
Other solutions you've considered

**Additional Context**
Any other context or screenshots
```

## Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH`
- Major: Breaking changes
- Minor: New features (backward compatible)
- Patch: Bug fixes (backward compatible)

### Release Checklist

1. Update version in `shadowlink/version.py`
2. Update `CHANGELOG.md`
3. Run full test suite
4. Create release tag
5. Build and publish to PyPI

## Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help others learn and grow
- Maintain professional communication

### Getting Help

- **GitHub Discussions**: General questions and discussions
- **GitHub Issues**: Bug reports and feature requests
- **Email**: Direct contact for sensitive issues

## Resources

### Documentation
- [Python Style Guide (PEP 8)](https://pep8.org/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [pytest Documentation](https://docs.pytest.org/)

### Tools
- [Black Code Formatter](https://black.readthedocs.io/)

Thank you for contributing to ShadowLink! 🎉
