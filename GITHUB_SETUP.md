# GitHub Repository Setup Guide

This guide walks you through creating a GitHub repository for the Code Search Benchmark project.

## Step 1: Initialize Git Repository

If you haven't already initialized git:

```bash
# Navigate to your project directory
cd /path/to/code-search-benchmark

# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Code Search Benchmark System"
```

## Step 2: Create GitHub Repository

### Option A: Using GitHub Web Interface

1. Go to [github.com](https://github.com)
2. Click the **+** icon in the top right
3. Select **New repository**
4. Fill in the details:
   - **Repository name**: `code-search-benchmark`
   - **Description**: `A framework for evaluating code retrieval agents using Git commit history`
   - **Visibility**: Public or Private (your choice)
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
5. Click **Create repository**

### Option B: Using GitHub CLI

```bash
# Install GitHub CLI if needed: https://cli.github.com/

# Create repository
gh repo create code-search-benchmark --public --source=. --remote=origin

# Or for private repository
gh repo create code-search-benchmark --private --source=. --remote=origin
```

## Step 3: Connect Local Repository to GitHub

After creating the repository on GitHub, connect your local repository:

```bash
# Add GitHub as remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/code-search-benchmark.git

# Verify remote
git remote -v

# Push to GitHub
git branch -M main
git push -u origin main
```

## Step 4: Verify Upload

Check that everything uploaded correctly:

```bash
# Visit your repository
# https://github.com/YOUR_USERNAME/code-search-benchmark

# You should see:
# - All source code files
# - README.md displayed on the main page
# - Documentation files
# - Examples directory
```

## Step 5: Configure Repository Settings (Optional)

### Add Topics

Add topics to help others discover your repository:

1. Go to your repository on GitHub
2. Click the gear icon next to "About"
3. Add topics: `code-search`, `benchmark`, `retrieval`, `evaluation`, `python`, `git`

### Set Up Branch Protection (Recommended)

1. Go to **Settings** → **Branches**
2. Add rule for `main` branch:
   - Require pull request reviews
   - Require status checks to pass
   - Require branches to be up to date

### Enable Issues and Discussions

1. Go to **Settings** → **General**
2. Enable **Issues** for bug reports and feature requests
3. Enable **Discussions** for community Q&A

## Step 6: Add Repository Badges (Optional)

Add badges to your README.md:

```markdown
# Code Search Benchmark System

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[Rest of README...]
```

## Step 7: Create Releases (When Ready)

When you're ready to release a version:

```bash
# Tag a release
git tag -a v0.1.0 -m "Initial release"
git push origin v0.1.0
```

Then create a release on GitHub:
1. Go to **Releases** → **Create a new release**
2. Select the tag `v0.1.0`
3. Add release notes
4. Publish release

## Common Git Commands

### Daily Workflow

```bash
# Check status
git status

# Add changes
git add .

# Commit changes
git commit -m "Description of changes"

# Push to GitHub
git push

# Pull latest changes
git pull
```

### Working with Branches

```bash
# Create new branch
git checkout -b feature/new-feature

# Switch branches
git checkout main

# Merge branch
git merge feature/new-feature

# Delete branch
git branch -d feature/new-feature
```

### Undoing Changes

```bash
# Discard changes in working directory
git checkout -- filename

# Unstage file
git reset HEAD filename

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1
```

## Repository Structure on GitHub

Your repository will look like this:

```
code-search-benchmark/
├── .github/              # GitHub-specific files (optional)
│   ├── workflows/        # GitHub Actions (CI/CD)
│   └── ISSUE_TEMPLATE/   # Issue templates
├── benchmark/            # Main package
├── examples/             # Example scripts
├── tests/               # Test suite (if added)
├── .gitignore           # Git ignore rules
├── .kiro/               # Kiro specs (optional to include)
├── AGENT_GUIDE.md       # Agent creation guide
├── CONTRIBUTING.md      # Contribution guidelines
├── LICENSE              # MIT License
├── QUICK_START.md       # Quick start guide
├── README.md            # Main documentation
├── example_config.yaml  # Configuration example
└── pyproject.toml       # Package configuration
```

## Sharing Your Repository

### Installation Instructions for Users

Users can install directly from GitHub:

```bash
# Install from GitHub
pip install git+https://github.com/YOUR_USERNAME/code-search-benchmark.git

# Or clone and install
git clone https://github.com/YOUR_USERNAME/code-search-benchmark.git
cd code-search-benchmark
pip install -e .
```

### Sharing with Others

Share your repository URL:
```
https://github.com/YOUR_USERNAME/code-search-benchmark
```

## Next Steps

1. **Add CI/CD** - Set up GitHub Actions for automated testing
2. **Write Tests** - Add comprehensive test suite
3. **Documentation** - Add more examples and tutorials
4. **Community** - Encourage contributions and feedback
5. **Publish to PyPI** - Make it installable via `pip install code-search-benchmark`

## Troubleshooting

### Authentication Issues

If you have authentication problems:

```bash
# Use SSH instead of HTTPS
git remote set-url origin git@github.com:YOUR_USERNAME/code-search-benchmark.git

# Or use GitHub CLI
gh auth login
```

### Large Files

If you have large files (>100MB):

```bash
# Use Git LFS
git lfs install
git lfs track "*.bin"
git add .gitattributes
```

### Sensitive Data

If you accidentally committed sensitive data:

```bash
# Remove from history
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch path/to/sensitive/file" \
  --prune-empty --tag-name-filter cat -- --all

# Force push
git push origin --force --all
```

## Resources

- [GitHub Docs](https://docs.github.com/)
- [Git Documentation](https://git-scm.com/doc)
- [GitHub CLI](https://cli.github.com/)
- [Git LFS](https://git-lfs.github.com/)

## Questions?

- Check [GitHub Docs](https://docs.github.com/)
- Open an issue in your repository
- Ask in GitHub Discussions

Happy coding! 🚀
