# Contributing to Code Search Benchmark

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/code-search-benchmark.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Install in development mode: `pip install -e ".[dev]"`

## Development Setup

```bash
# Install with all dependencies
pip install -e ".[dev,llm,semantic]"

# Run tests
pytest

# Format code
black benchmark/
ruff check benchmark/
```

## How to Contribute

### Reporting Bugs

Open an issue with:
- Clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version)

### Suggesting Features

Open an issue with:
- Clear description of the feature
- Use case and motivation
- Proposed implementation (optional)

### Contributing Code

1. **Write tests** for new features
2. **Follow code style** (black + ruff)
3. **Update documentation** if needed
4. **Keep commits focused** - one logical change per commit
5. **Write clear commit messages**

### Adding New Agents

To contribute a new agent implementation:

1. Create agent in `benchmark/agents/`
2. Inherit from `RetrievalAgent`
3. Implement required methods: `initialize()`, `retrieve()`, `reset()`
4. Add tests in `tests/agents/`
5. Update documentation in `AGENT_GUIDE.md`
6. Add example usage in `examples/`

Example:
```python
# benchmark/agents/my_agent.py
from benchmark.agents.base import RetrievalAgent
from benchmark.models import RetrievalResult

class MyAgent(RetrievalAgent):
    def initialize(self, repo_path: str) -> None:
        # Setup code
        pass
    
    def retrieve(self, query: str) -> RetrievalResult:
        # Search logic
        return RetrievalResult(files=[], scores=[])
    
    def reset(self) -> None:
        # Clear state
        pass
```

### Improving Documentation

Documentation improvements are always welcome:
- Fix typos or unclear explanations
- Add examples
- Improve code comments
- Update guides with new patterns

## Code Style

- Use **black** for formatting (line length: 100)
- Use **ruff** for linting
- Follow **PEP 8** conventions
- Write **docstrings** for public functions/classes
- Add **type hints** where appropriate

## Testing

- Write tests for new features
- Ensure existing tests pass
- Aim for good test coverage
- Use pytest fixtures for common setup

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=benchmark

# Run specific test
pytest tests/test_metrics.py
```

## Pull Request Process

1. Update documentation if needed
2. Add tests for new features
3. Ensure all tests pass
4. Update CHANGELOG.md (if applicable)
5. Submit PR with clear description

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Testing
How was this tested?

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Code formatted (black)
- [ ] Linting passed (ruff)
```

## Project Structure

```
benchmark/
├── agents/          # Retrieval agent implementations
├── dataset/         # Dataset generation from Git
├── evaluation/      # Evaluation engine
├── metrics/         # Metrics calculation
├── reporting/       # Report generation
├── models.py        # Core data models
├── config.py        # Configuration loading
└── cli.py           # Command-line interface

examples/            # Example scripts and agents
tests/              # Test suite
docs/               # Additional documentation
```

## Questions?

- Open an issue for questions
- Check existing issues and PRs
- Review documentation in README.md and AGENT_GUIDE.md

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Help others learn and grow

Thank you for contributing! 🎉
