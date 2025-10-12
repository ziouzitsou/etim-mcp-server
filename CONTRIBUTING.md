# Contributing to ETIM MCP Server

Thank you for your interest in contributing to the ETIM MCP Server! We welcome contributions from the community and are grateful for your support.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)
- [Feature Requests](#feature-requests)

## Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Set up your development environment (see below)
4. Create a new branch for your changes
5. Make your changes and commit them
6. Push to your fork and submit a pull request

## Development Setup

### Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose
- ETIM API credentials (for testing)

### Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/etim-mcp-server.git
   cd etim-mcp-server
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env and add your ETIM API credentials
   ```

5. **Start Redis**:
   ```bash
   docker run -d -p 6379:6379 redis:7-alpine
   ```

6. **Run the server**:
   ```bash
   python -m mcp run src.etim_mcp.server:mcp
   ```

## Making Changes

### Code Style

- Follow PEP 8 guidelines for Python code
- Use type hints where appropriate
- Write docstrings for all public functions and classes
- Keep functions focused and modular

### Commit Messages

- Use clear and descriptive commit messages
- Start with a verb in imperative mood (e.g., "Add", "Fix", "Update")
- Reference issue numbers when applicable
- Example:
  ```
  Add support for batch class queries

  - Implement get_class_details_many endpoint
  - Add caching support
  - Update documentation

  Closes #123
  ```

### Branch Naming

Use descriptive branch names:
- `feature/add-new-tool` - for new features
- `fix/authentication-bug` - for bug fixes
- `docs/update-readme` - for documentation updates
- `refactor/cache-layer` - for refactoring

## Testing

### Running Tests

```bash
# Run all tests
python tests/test_phase2_tools.py

# Test specific endpoints
docker-compose exec mcp-server python tests/test_new_tools.py
```

### Writing Tests

- Add tests for all new features
- Ensure tests pass before submitting a PR
- Test both success and error cases
- Mock external API calls when appropriate

## Submitting Changes

1. **Update documentation**: Ensure README.md and other docs reflect your changes
2. **Test thoroughly**: Run all tests and verify functionality
3. **Commit your changes**: Use clear, descriptive commit messages
4. **Push to your fork**: `git push origin feature/your-feature-name`
5. **Open a Pull Request**:
   - Provide a clear title and description
   - Reference any related issues
   - Explain the changes and their purpose
   - Include screenshots if applicable

### Pull Request Checklist

- [ ] Code follows the project's style guidelines
- [ ] All tests pass
- [ ] New features include tests
- [ ] Documentation has been updated
- [ ] Commit messages are clear and descriptive
- [ ] PR description explains the changes clearly

## Reporting Issues

### Bug Reports

When reporting bugs, please include:

- **Description**: Clear description of the bug
- **Steps to reproduce**: Detailed steps to recreate the issue
- **Expected behavior**: What you expected to happen
- **Actual behavior**: What actually happened
- **Environment**:
  - OS (Linux, macOS, Windows)
  - Python version
  - Docker version
  - ETIM MCP Server version
- **Logs**: Relevant error messages or logs
- **Screenshots**: If applicable

### Security Issues

**Do not** report security vulnerabilities through public GitHub issues. Instead, please send an email to the maintainers.

## Feature Requests

We welcome feature requests! When submitting a feature request:

1. **Check existing issues**: Ensure the feature hasn't already been requested
2. **Describe the feature**: Provide a clear description of the proposed feature
3. **Explain the use case**: Why would this feature be useful?
4. **Provide examples**: Mock-ups, code examples, or similar implementations
5. **Consider alternatives**: Discuss alternative approaches

## Areas Where We Need Help

We're particularly interested in contributions in these areas:

- 📝 **Documentation**: Improving guides, examples, and API documentation
- 🧪 **Testing**: Adding test coverage, integration tests, stress tests
- 🎨 **Examples**: Creating example integrations and use cases
- 🌍 **Localization**: Supporting more ETIM languages
- 🚀 **Performance**: Optimizing caching, API calls, and response times
- 🔧 **Tools**: Adding new MCP tools for ETIM endpoints
- 🐛 **Bug fixes**: Addressing reported issues

## Questions?

- Open a [GitHub Discussion](https://github.com/ziouzitsou/etim-mcp-server/discussions) for questions
- Check existing issues and pull requests
- Read the [README.md](README.md) for project documentation

## Recognition

Contributors will be acknowledged in:
- GitHub contributors page
- Release notes
- Project README (for significant contributions)

Thank you for contributing to ETIM MCP Server! 🎉
