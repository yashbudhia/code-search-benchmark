# Quick GitHub Commands Reference

## ✅ Already Done

```bash
✓ git init                                    # Repository initialized
✓ git add .                                   # Files staged
✓ git commit -m "Initial commit..."          # Initial commit created
```

## 🚀 Next Steps to Push to GitHub

### Step 1: Create Repository on GitHub

**Option A: Using GitHub Website**
1. Go to https://github.com/new
2. Repository name: `code-search-benchmark`
3. Description: `A framework for evaluating code retrieval agents using Git commit history`
4. Choose Public or Private
5. **DO NOT** check "Initialize with README" (we already have one)
6. Click "Create repository"

**Option B: Using GitHub CLI** (if installed)
```bash
gh repo create code-search-benchmark --public --source=. --remote=origin --push
```

### Step 2: Connect and Push (After creating on GitHub)

Replace `YOUR_USERNAME` with your GitHub username:

```bash
# Add remote
git remote add origin https://github.com/YOUR_USERNAME/code-search-benchmark.git

# Verify remote
git remote -v

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 3: Verify

Visit: `https://github.com/YOUR_USERNAME/code-search-benchmark`

## 📝 Daily Git Workflow

### Making Changes

```bash
# 1. Check what changed
git status

# 2. Add changes
git add .                    # Add all changes
git add filename.py          # Add specific file

# 3. Commit changes
git commit -m "Description of what you changed"

# 4. Push to GitHub
git push
```

### Pulling Latest Changes

```bash
# Get latest changes from GitHub
git pull
```

## 🔧 Common Commands

### Viewing History

```bash
git log                      # View commit history
git log --oneline           # Compact view
git log --graph --oneline   # Visual graph
```

### Checking Status

```bash
git status                  # See what's changed
git diff                    # See detailed changes
git diff filename.py        # Changes in specific file
```

### Undoing Changes

```bash
# Discard changes in a file (before staging)
git checkout -- filename.py

# Unstage a file (after git add)
git reset HEAD filename.py

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes) - CAREFUL!
git reset --hard HEAD~1
```

### Branches

```bash
# Create new branch
git checkout -b feature/new-feature

# Switch branches
git checkout main

# List branches
git branch

# Delete branch
git branch -d feature/new-feature
```

## 🔐 Authentication

### Using HTTPS (Recommended)

```bash
# First time pushing, you'll be prompted for credentials
git push

# GitHub will ask for:
# - Username: your_github_username
# - Password: use a Personal Access Token (not your password!)
```

**Create Personal Access Token:**
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo` (full control)
4. Copy the token and use it as password

### Using SSH (Alternative)

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Add to GitHub: https://github.com/settings/keys
# Copy your public key:
cat ~/.ssh/id_ed25519.pub

# Change remote to SSH
git remote set-url origin git@github.com:YOUR_USERNAME/code-search-benchmark.git
```

## 📦 Repository Structure

Your GitHub repo will contain:

```
code-search-benchmark/
├── benchmark/              # Main package code
├── examples/              # Example scripts
├── .kiro/specs/          # Kiro specifications
├── README.md             # Main documentation
├── QUICK_START.md        # Quick start guide
├── AGENT_GUIDE.md        # Agent creation guide
├── CONTRIBUTING.md       # Contribution guidelines
├── LICENSE               # MIT License
├── pyproject.toml        # Package configuration
└── example_config.yaml   # Configuration example
```

## 🎯 Quick Reference

| Task | Command |
|------|---------|
| Check status | `git status` |
| Add all changes | `git add .` |
| Commit changes | `git commit -m "message"` |
| Push to GitHub | `git push` |
| Pull from GitHub | `git pull` |
| View history | `git log --oneline` |
| Create branch | `git checkout -b branch-name` |
| Switch branch | `git checkout branch-name` |
| Undo changes | `git checkout -- filename` |

## 🆘 Troubleshooting

### "Permission denied" error

**Solution:** Set up authentication (Personal Access Token or SSH key)

### "Repository not found" error

**Solution:** Check remote URL: `git remote -v`

### "Merge conflict" error

**Solution:**
```bash
# 1. Open conflicted files and resolve conflicts
# 2. Add resolved files
git add .
# 3. Commit
git commit -m "Resolved merge conflicts"
```

### "Detached HEAD" state

**Solution:**
```bash
git checkout main
```

## 📚 Resources

- [GitHub Docs](https://docs.github.com/)
- [Git Cheat Sheet](https://education.github.com/git-cheat-sheet-education.pdf)
- [GitHub CLI](https://cli.github.com/)

## 🎉 After Pushing to GitHub

Your repository will be live at:
```
https://github.com/YOUR_USERNAME/code-search-benchmark
```

Others can install it with:
```bash
pip install git+https://github.com/YOUR_USERNAME/code-search-benchmark.git
```

---

**Current Status:** ✅ Local repository ready, waiting for GitHub remote setup
