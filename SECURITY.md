# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.2.x   | :white_check_mark: |
| 1.1.x   | :white_check_mark: |
| 1.0.x   | :x:                |

## Security Measures

### Authentication & Authorization

- **OAuth2 Client Credentials Flow**: All ETIM API requests use OAuth2 authentication
- **Token Caching**: Access tokens are cached in Redis with appropriate TTLs
- **Automatic Token Refresh**: Tokens are automatically refreshed before expiration
- **No Hardcoded Credentials**: All credentials are managed through environment variables

### Data Security

- **Environment Variables**: All sensitive configuration (API credentials) must be provided via `.env` file
- **Gitignore Protection**: `.env` files are excluded from version control
- **No Credential Logging**: Credentials are never logged or exposed in error messages
- **Redis Isolation**: Redis is only accessible within the Docker network

### Network Security

- **Docker Network Isolation**: Services communicate within a private Docker network
- **Port Exposure**:
  - Redis port 6379: Exposed for local development (bind to localhost only in production)
  - Redis Commander port 8081: Web UI for cache monitoring (disable in production)
  - MCP Server: stdio-based, no network exposure

### Code Security

- **No Dynamic Code Execution**: No use of `eval()`, `exec()`, or `__import__()`
- **No Command Injection**: No shell command execution (`subprocess`, `os.system()`)
- **No Unsafe Deserialization**: No use of `pickle` or similar
- **Dependency Management**: All dependencies specified in `requirements.txt`
- **Async/Await Architecture**: Modern async Python prevents common concurrency issues

### Production Deployment Recommendations

1. **Bind Redis to localhost only**:
   ```yaml
   redis:
     ports:
       - "127.0.0.1:6379:6379"  # Only accessible from host
   ```

2. **Disable Redis Commander in production**:
   ```bash
   docker-compose up redis mcp-server  # Omit redis-commander
   ```

3. **Use strong Redis password**:
   ```env
   REDIS_PASSWORD=your_strong_password_here
   ```

4. **Restrict file permissions**:
   ```bash
   chmod 600 .env  # Only owner can read/write
   ```

5. **Keep dependencies updated**:
   ```bash
   pip list --outdated
   pip install --upgrade package_name
   ```

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please follow these steps:

1. **DO NOT** open a public GitHub issue
2. **DO NOT** disclose the vulnerability publicly until it has been addressed
3. **Email the maintainers** with details:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will:
- Acknowledge receipt within 48 hours
- Provide an initial assessment within 5 business days
- Work on a fix and keep you updated on progress
- Credit you in the security advisory (unless you prefer to remain anonymous)

## Security Audit Summary

**Last Audit**: 2025-10-12
**Auditor**: Project Maintainer with Claude Code assistance

### Audit Findings

✅ **No Critical Issues Found**

- No hardcoded credentials in source code
- No dangerous Python functions (eval, exec, etc.)
- No SQL injection vectors (no database)
- No command injection vectors
- All sensitive data uses environment variables
- `.env` properly excluded from git
- Docker configuration follows best practices
- Redis isolated to Docker network
- OAuth2 token management implemented correctly

### Verified Secure Practices

- ✅ Environment-based configuration
- ✅ OAuth2 authentication with automatic refresh
- ✅ Secure credential storage (environment variables)
- ✅ No credentials in logs or error messages
- ✅ Docker network isolation
- ✅ Structured logging (Loguru)
- ✅ Async/await throughout (no concurrency issues)
- ✅ Type hints for code safety
- ✅ Comprehensive error handling

## Dependencies Security

This project uses the following third-party dependencies:

- `fastmcp` - MCP server framework (official Anthropic SDK)
- `httpx` - Async HTTP client (widely used, actively maintained)
- `redis` - Redis client (official Redis Python client)
- `pydantic` - Data validation (industry standard)
- `pydantic-settings` - Settings management
- `loguru` - Logging library
- `python-dotenv` - Environment variable loading

All dependencies are actively maintained and have strong security track records.

## Contact

For security concerns, please contact the project maintainers through GitHub.

---

**Note**: This security policy applies to the ETIM MCP Server codebase only. Security of the ETIM API itself is managed by ETIM International.
