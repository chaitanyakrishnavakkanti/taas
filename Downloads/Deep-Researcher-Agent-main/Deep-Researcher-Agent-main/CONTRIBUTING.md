# Contributing to Deep Researcher Agent

Thank you for your interest in contributing to Deep Researcher Agent! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic knowledge of Python, AI/ML, and Streamlit

### Development Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Deep-Researcher-Agent.git
   cd Deep-Researcher-Agent
   ```

3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install -e .[dev]  # Install development dependencies
   ```

5. **Run the application**:
   ```bash
   python run_app.py
   ```

## 🎯 How to Contribute

### Types of Contributions

- **Bug Fixes**: Fix existing issues
- **Feature Additions**: Add new functionality
- **Documentation**: Improve README, code comments, or guides
- **Performance**: Optimize existing code
- **Testing**: Add or improve tests
- **UI/UX**: Improve the Streamlit interface

### Contribution Process

1. **Check existing issues** and pull requests
2. **Create an issue** if you're planning a significant change
3. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. **Make your changes** following the coding standards
5. **Test your changes** thoroughly
6. **Commit your changes**:
   ```bash
   git commit -m "Add: Brief description of changes"
   ```
7. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
8. **Create a Pull Request** on GitHub

## 📝 Coding Standards

### Python Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write docstrings for all functions and classes
- Keep functions small and focused
- Use meaningful variable and function names

### Code Formatting

We use `black` for code formatting:

```bash
black .
```

### Linting

We use `flake8` for linting:

```bash
flake8 .
```

### Type Checking

We use `mypy` for type checking:

```bash
mypy .
```

## 🧪 Testing

### Running Tests

```bash
pytest
```

### Test Coverage

Aim for high test coverage, especially for new features:

```bash
pytest --cov=utils --cov-report=html
```

### Writing Tests

- Write tests for new functionality
- Test edge cases and error conditions
- Use descriptive test names
- Keep tests simple and focused

## 📚 Documentation

### Code Documentation

- Write clear docstrings for all functions and classes
- Include parameter descriptions and return values
- Add type hints for better code understanding
- Comment complex logic

### README Updates

- Update README.md for new features
- Include usage examples
- Update installation instructions if needed
- Add screenshots for UI changes

## 🐛 Bug Reports

### Before Reporting

1. Check if the issue already exists
2. Try to reproduce the issue
3. Check the latest version
4. Gather relevant information

### Bug Report Template

```markdown
**Bug Description**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected Behavior**
A clear description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment**
- OS: [e.g., Windows 10, macOS 12, Ubuntu 20.04]
- Python version: [e.g., 3.9.7]
- Streamlit version: [e.g., 1.28.0]

**Additional Context**
Add any other context about the problem here.
```

## ✨ Feature Requests

### Before Requesting

1. Check if the feature already exists
2. Consider if it fits the project's scope
3. Think about implementation complexity
4. Consider user impact

### Feature Request Template

```markdown
**Feature Description**
A clear description of the feature you'd like to see.

**Use Case**
Describe the use case and why this feature would be useful.

**Proposed Solution**
A clear description of what you want to happen.

**Alternatives**
Describe any alternative solutions or workarounds you've considered.

**Additional Context**
Add any other context or screenshots about the feature request.
```

## 🏗️ Architecture Guidelines

### Adding New AI Models

1. Create a new synthesizer class in `utils/`
2. Follow the existing pattern in `simple_ai_synthesizer.py`
3. Add error handling and fallbacks
4. Update the reasoning engine to use the new model
5. Add tests for the new functionality

### Adding New Document Types

1. Update the `ingest.py` module
2. Add parsing logic for the new format
3. Update the UI to show the new file type
4. Add tests for the new parser
5. Update documentation

### UI/UX Improvements

1. Follow Streamlit best practices
2. Maintain responsive design
3. Use consistent styling
4. Test on different screen sizes
5. Ensure accessibility

## 📋 Pull Request Guidelines

### Before Submitting

- [ ] Code follows the project's style guidelines
- [ ] Self-review of your code
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] No merge conflicts

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added (if applicable)
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No merge conflicts
```

## 🤝 Community Guidelines

### Be Respectful

- Use welcoming and inclusive language
- Be respectful of differing viewpoints
- Accept constructive criticism gracefully
- Focus on what's best for the community

### Be Constructive

- Provide helpful feedback
- Suggest improvements
- Ask questions when unclear
- Share knowledge and experience

## 📞 Getting Help

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Code Review**: For feedback on pull requests

## 🎉 Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- GitHub contributors page

Thank you for contributing to Deep Researcher Agent! 🚀
