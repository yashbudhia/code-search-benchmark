# Repository Comparison for Benchmarking

## Two Gold Sets Available

### 1. Requests Library (test_gold_set.json)
**Repository:** Python HTTP library
**Path:** `D:/code/bench/test-repo`
**Test Cases:** 11
**Focus:** Infrastructure and configuration changes

### 2. Django Framework (django_gold_set.json)
**Repository:** Python web framework  
**Path:** `D:/code/bench/django-repo`
**Test Cases:** 49
**Focus:** Actual code changes and bug fixes

---

## Detailed Comparison

| Aspect | Requests | Django |
|--------|----------|--------|
| **Repository Size** | ~26K commits | ~551K commits |
| **Files** | ~100 files | ~6,990 files |
| **Test Cases** | 11 | 49 |
| **Commits Analyzed** | 50 | 100 |
| **Language** | Python | Python |
| **Type** | Library | Framework |

---

## Query Type Comparison

### Requests Queries (Infrastructure-Heavy)

**Examples:**
- "Bump actions setup-python from 5.6.0 to 6.0.0"
- "Bump actions checkout from 4.2.0 to 5.0.0"
- "Add support for Python 3.14 and drop support for Python 3.8"
- "Add Trusted Publishing Release Workflow"

**Characteristics:**
- ✅ Simple, clear intent
- ❌ Mostly workflow/config files
- ❌ Less actual code
- ❌ Version bumps dominate

**Expected Greb Performance:** 
- May struggle with workflow files
- Better with code-related queries

---

### Django Queries (Code-Heavy)

**Examples:**
- "Fixed -- Extended fields.E004 system check for unordered iterables."
- "Fixed -- Escaped attributes in Stylesheet.__str__."
- "Fixed -- Checked for applied replaced migrations recursively."
- "Refs -- Added introspection support for PostgreSQL HStoreField."

**Characteristics:**
- ✅ Actual code changes
- ✅ Bug fixes and features
- ✅ Clear semantic meaning
- ✅ Mix of core code and tests

**Expected Greb Performance:**
- Should perform much better
- Semantic understanding helps
- Code structure is clearer

---

## File Type Distribution

### Requests Repository

| File Type | Count | Percentage |
|-----------|-------|------------|
| Workflow files (.yml) | 40% | GitHub Actions |
| Documentation (.md, .rst) | 30% | Docs |
| Python code (.py) | 20% | Source |
| Config files | 10% | Various |

### Django Repository

| File Type | Count | Percentage |
|-----------|-------|------------|
| Python code (.py) | 70% | Source & tests |
| Documentation (.txt, .rst) | 15% | Docs |
| Templates (.html) | 10% | Django templates |
| Static files (.css, .js) | 5% | Admin assets |

---

## Complexity Distribution

### Requests

| Complexity | Count | Files Range |
|------------|-------|-------------|
| Medium | 11 | 2-7 files |
| Low | 0 | - |
| High | 0 | - |

**Average:** 3.2 files per query

### Django

| Complexity | Count | Files Range |
|------------|-------|-------------|
| Medium | 49 | 2-7 files |
| Low | 0 | - |
| High | 0 | - |

**Average:** 3.1 files per query

---

## Which Repository to Use?

### Use Requests If:
- ✅ Testing workflow/config file search
- ✅ Quick evaluation (11 queries)
- ✅ Simple baseline test
- ✅ Infrastructure-focused agents

### Use Django If:
- ✅ Testing code search capabilities
- ✅ Comprehensive evaluation (49 queries)
- ✅ Real-world code scenarios
- ✅ Semantic understanding test
- ✅ Production-grade codebase

---

## Recommendation for Greb Testing

### Start with Django! 🎯

**Reasons:**
1. **Better for code search** - Greb is designed for code, not configs
2. **More test cases** - 49 vs 11 gives better statistics
3. **Realistic scenarios** - Actual bug fixes and features
4. **Semantic queries** - "Fixed constraint validation" vs "Bump version"
5. **Code structure** - Clear modules, tests, and documentation

### Testing Strategy

**Phase 1: Quick Test (5 queries)**
```bash
# Test first 5 Django queries manually
# See if Greb understands code semantics
```

**Phase 2: Small Batch (10 queries)**
```bash
# Run 10 queries to get initial metrics
# Compare with keyword baseline
```

**Phase 3: Full Evaluation (49 queries)**
```bash
# Run complete evaluation
# Generate comprehensive report
```

**Phase 4: Compare Repositories**
```bash
# Run both Requests and Django
# Analyze performance differences
```

---

## Expected Results

### Keyword Baseline (Already Tested)

**Requests:**
- Mean F1: 0.114
- p50 Latency: 16.27ms

**Django (Predicted):**
- Mean F1: ~0.10-0.15 (similar)
- p50 Latency: ~15-20ms

### Greb (Expected)

**Requests:**
- Mean F1: 0.15-0.30 (modest improvement)
- Struggles with workflow files

**Django:**
- Mean F1: 0.40-0.70 (significant improvement)
- Better semantic understanding
- Clearer code structure

---

## Files Available

1. **test_gold_set.json** - Requests (11 queries)
2. **django_gold_set.json** - Django (49 queries)
3. **test-repo/** - Requests repository
4. **django-repo/** - Django repository

---

## Quick Start Commands

### Evaluate Django with Greb (Manual)
```bash
python examples/evaluate_copilot_greb.py
# Update script to use:
# - GOLD_SET_PATH = "django_gold_set.json"
# - REPO_PATH = "django-repo"
```

### Evaluate Django with Greb (Automated)
```bash
python examples/evaluate_greb_automated.py
# Update configuration for Django
```

### Compare Both Repositories
```bash
# Run evaluation on both
# Compare results
# Analyze which types of queries work best
```

---

## Summary

✅ **Two repositories ready for testing**
✅ **60 total test cases** (11 + 49)
✅ **Different query types** (infrastructure vs code)
✅ **Comprehensive coverage** of real-world scenarios

**Recommendation:** Start with Django for better Greb evaluation! 🚀
