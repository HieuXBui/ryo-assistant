# Contributing to Ryo AI Assistant

Thank you for your interest in contributing to Ryo AI Assistant! This document provides guidelines and information for contributors.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Create a feature branch** for your changes
4. **Make your changes** following the guidelines below
5. **Test your changes** thoroughly
6. **Submit a pull request**

## Development Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```bash
   cp config/env.example config/.env
   # Edit config/.env with your API keys
   ```

3. Run the application:
   ```bash
   python core/main.py
   ```

## Code Style Guidelines

### Python Code
- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to all functions and classes
- Keep functions focused and concise
- Use type hints where appropriate

### Example:
```python
def process_audio(audio_data: bytes, sample_rate: int = 16000) -> str:
    """
    Process audio data and return transcribed text.
    
    Args:
        audio_data: Raw audio bytes
        sample_rate: Audio sample rate in Hz
        
    Returns:
        Transcribed text string
    """
    # Implementation here
    pass
```

## Testing

### Running Tests
```bash
# Run all tests
python -m pytest

# Run specific test file
python test_voice_commands.py

# Run with coverage
python -m pytest --cov=core --cov=voice --cov=ai
```

### Writing Tests
- Write tests for new features
- Ensure existing tests pass
- Use descriptive test names
- Mock external dependencies

## Pull Request Guidelines

### Before Submitting
1. **Test thoroughly** - Ensure all functionality works
2. **Update documentation** - Update README, docstrings, etc.
3. **Check code style** - Run linters and formatters
4. **Update tests** - Add tests for new features

### Pull Request Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Refactoring

## Testing
- [ ] All tests pass
- [ ] New tests added
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No breaking changes
- [ ] Environment variables documented
```

## Issue Reporting

When reporting issues, please include:

1. **Operating System** and version
2. **Python version**
3. **Steps to reproduce**
4. **Expected vs actual behavior**
5. **Error messages** (if any)
6. **Screenshots** (if applicable)

## Feature Requests

When suggesting new features:

1. **Describe the use case** clearly
2. **Explain the benefit** to users
3. **Consider implementation** complexity
4. **Check existing issues** for duplicates

## Code of Conduct

- Be respectful and inclusive
- Help others learn and grow
- Provide constructive feedback
- Focus on the code, not the person

## Getting Help

- Check existing issues and discussions
- Join our community discussions
- Ask questions in issues or discussions

Thank you for contributing to Ryo AI Assistant! 🎉 