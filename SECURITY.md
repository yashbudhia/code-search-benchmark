# Security Policy

## Reporting Security Issues

If you discover a security vulnerability, please email the maintainers directly rather than opening a public issue.

## Best Practices

### API Keys and Secrets

**Never commit API keys or secrets to the repository.**

✅ **Do:**
- Use environment variables for API keys
- Store secrets in `.env` files (which are gitignored)
- Use configuration files that reference environment variables
- Document required environment variables in README

❌ **Don't:**
- Hardcode API keys in source code
- Commit `.env` files
- Include API keys in example files
- Share credentials in issues or pull requests

### Example: Using API Keys Safely

```python
import os

# Good - Use environment variables
api_key = os.getenv("OPENAI_API_KEY")

# Bad - Never hardcode
# api_key = "sk-1234567890abcdef"
```

### Setting Environment Variables

**Linux/Mac:**
```bash
export OPENAI_API_KEY="your-key-here"
export ANTHROPIC_API_KEY="your-key-here"
```

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="your-key-here"
$env:ANTHROPIC_API_KEY="your-key-here"
```

**Windows (CMD):**
```cmd
set OPENAI_API_KEY=your-key-here
set ANTHROPIC_API_KEY=your-key-here
```

### Using .env Files

Create a `.env` file (already gitignored):

```bash
# .env
OPENAI_API_KEY=your-key-here
ANTHROPIC_API_KEY=your-key-here
GITHUB_TOKEN=your-token-here
```

Load in Python:
```python
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
```

## Protected Files

The following files are automatically excluded from git:

- `.env` and `.env.local` - Environment variables
- `test-api-*.ps1` - API test scripts
- Any files containing credentials

## If You Accidentally Commit Secrets

If you accidentally commit API keys or secrets:

1. **Immediately revoke/rotate the exposed credentials**
2. **Remove from git history:**
   ```bash
   # Remove file from all commits
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch path/to/file" \
     --prune-empty --tag-name-filter cat -- --all
   
   # Force push (if already pushed to GitHub)
   git push origin --force --all
   ```

3. **Verify removal:**
   ```bash
   git log --all --full-history -- path/to/file
   ```

## GitHub Security Features

Enable these on your repository:

1. **Secret Scanning** - Automatically detects committed secrets
2. **Dependabot Alerts** - Notifies about vulnerable dependencies
3. **Code Scanning** - Identifies security vulnerabilities

## Dependencies

Keep dependencies up to date:

```bash
# Check for updates
pip list --outdated

# Update packages
pip install --upgrade package-name
```

## Reporting Issues

For security issues, contact the maintainers privately.

For general bugs, open an issue on GitHub.

## Security Checklist

Before pushing to GitHub:

- [ ] No API keys in code
- [ ] No passwords or tokens in files
- [ ] `.env` files are gitignored
- [ ] Test scripts with credentials are excluded
- [ ] Environment variables documented in README
- [ ] Dependencies are up to date

## Resources

- [GitHub Security Best Practices](https://docs.github.com/en/code-security)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
