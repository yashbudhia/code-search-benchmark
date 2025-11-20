# Greb MCP Improvement Recommendations

**Based on:** Benchmark testing with 4 queries across 2 repositories
**Current Performance:** F1 = 0.256 (2.5x better than keyword baseline)
**Target Performance:** F1 = 0.60-0.70 (6-7x better than baseline)

---

## 🎯 Top 10 Improvements (Prioritized)

### 🔴 Priority 1: Critical Issues (Implement First)

#### 1. Documentation File Boosting
**Problem:** Consistently misses documentation files (0% recall on docs)

**Solution:**
```python
# Boost documentation files
if '/docs/' in file_path or file_path.endswith(('.txt', '.rst', '.md')):
    relevance_score *= 1.3

# Detect documentation queries
if any(term in query.lower() for term in ['release', 'documentation', 'changelog']):
    boost_docs_even_more()
```

**Impact:** +10-15% F1
**Effort:** Low (1-2 hours)
**ROI:** ⭐⭐⭐⭐⭐

---

#### 2. Implementation vs Test File Balance
**Problem:** Returns too many test files, misses core implementation

**Solution:**
```python
# Prioritize implementation files
def get_file_priority(file_path):
    if 'test' in file_path:
        return 1.0  # Normal priority
    elif file_path.startswith('django/') and 'test' not in file_path:
        return 1.5  # Boost implementation
    elif file_path.startswith('docs/'):
        return 1.3  # Boost docs
    return 1.0

# Apply to scoring
final_score = base_score * get_file_priority(file_path)
```

**Impact:** +15-20% F1
**Effort:** Low (2-3 hours)
**ROI:** ⭐⭐⭐⭐⭐

---

#### 3. Query Enhancement Layer
**Problem:** Vague queries get poor results

**Solution:**
```python
def enhance_query(query, repo_type='django'):
    """Automatically improve queries"""
    
    enhanced = query
    
    # Add file type hints
    if 'css' in query.lower() or 'styling' in query.lower():
        enhanced += ' static styles'
    
    if 'test' in query.lower():
        enhanced += ' tests/'
    
    # Add location hints for Django
    if repo_type == 'django':
        if 'admin' in query.lower():
            enhanced += ' contrib/admin'
        if 'model' in query.lower() and 'test' not in query.lower():
            enhanced += ' db/models'
        if 'migration' in query.lower():
            enhanced += ' db/migrations'
    
    # Remove noise words
    noise_words = ['fixed', 'added', 'updated', 'refs']
    for word in noise_words:
        enhanced = enhanced.replace(word, '')
    
    return enhanced.strip()
```

**Impact:** +20-25% F1
**Effort:** Medium (4-6 hours)
**ROI:** ⭐⭐⭐⭐⭐

---

### 🟡 Priority 2: Precision Improvements

#### 4. Stricter Relevance Thresholds
**Problem:** Too many low-relevance results (21 false positives in Query 9)

**Solution:**
```python
# Filter by minimum relevance
MIN_RELEVANCE = 0.5
results = [r for r in results if r.score >= MIN_RELEVANCE]

# Or use dynamic threshold based on top score
top_score = results[0].score
threshold = top_score * 0.5  # Within 50% of top
results = [r for r in results if r.score >= threshold]

# Limit total results
return results[:10]
```

**Impact:** +10-15% precision
**Effort:** Low (1 hour)
**ROI:** ⭐⭐⭐⭐

---

#### 5. File Type Matching
**Problem:** CSS queries find Python code (Query 13)

**Solution:**
```python
def matches_query_intent(query, file_path):
    """Check if file type matches query"""
    
    file_ext = os.path.splitext(file_path)[1]
    
    # CSS queries should find CSS
    if any(term in query.lower() for term in ['css', 'style', 'styling']):
        return file_ext == '.css'
    
    # Test queries should find tests
    if 'test' in query.lower():
        return 'test' in file_path
    
    # Python queries should find Python
    if any(term in query.lower() for term in ['class', 'method', 'function']):
        return file_ext == '.py'
    
    return True  # Default: allow

# Filter results
results = [r for r in results if matches_query_intent(query, r.path)]
```

**Impact:** +15-20% precision
**Effort:** Medium (3-4 hours)
**ROI:** ⭐⭐⭐⭐

---

### 🟢 Priority 3: Recall Improvements

#### 6. Multi-Query Strategy
**Problem:** Complex queries miss files (Query 4: only 2 of 6 files)

**Solution:**
```python
def split_complex_query(query):
    """Break into focused sub-queries"""
    
    sub_queries = [query]  # Always include original
    
    # Detect multiple concepts
    concepts = []
    if 'introspection' in query.lower():
        concepts.append('database introspection')
    if 'hstore' in query.lower():
        concepts.append('HStoreField')
    if 'postgresql' in query.lower():
        concepts.append('postgresql backend')
    
    # Create sub-queries
    for concept in concepts:
        sub_queries.append(concept)
    
    return sub_queries

# Execute all and merge
all_results = []
for sub_q in split_complex_query(query):
    results = search(sub_q)
    all_results.extend(results)

# Deduplicate and re-rank
final = deduplicate_and_merge(all_results)
```

**Impact:** +10-15% recall
**Effort:** Medium (4-5 hours)
**ROI:** ⭐⭐⭐⭐

---

#### 7. Path-Based Boosting
**Problem:** Doesn't understand project structure

**Solution:**
```python
# Django-specific path weights
PATH_WEIGHTS = {
    'django/db/models/': 1.4,           # Core models
    'django/contrib/admin/': 1.3,       # Admin
    'django/db/backends/': 1.3,         # Database backends
    'tests/': 1.1,                      # Tests
    'docs/': 1.3,                       # Documentation
    'django/contrib/postgres/': 1.2,    # PostgreSQL
}

def apply_path_boost(file_path, base_score):
    for prefix, weight in PATH_WEIGHTS.items():
        if file_path.startswith(prefix):
            return base_score * weight
    return base_score
```

**Impact:** +5-10% recall
**Effort:** Low (2 hours)
**ROI:** ⭐⭐⭐

---

### 🔵 Priority 4: Advanced Features

#### 8. Technical Term Expansion
**Problem:** Doesn't understand Django-specific terms ("attname")

**Solution:**
```python
TERM_EXPANSIONS = {
    'attname': ['attribute name', 'field.attname', 'column name', 'db_column'],
    'FK': ['foreign key', 'ForeignKey', 'relationship', 'related field'],
    'introspection': ['database introspection', 'schema inspection', 'get_field_type'],
    'constraint': ['constraint validation', 'database constraint', 'check constraint'],
}

def expand_query(query):
    """Expand technical terms"""
    expanded = [query]
    
    for term, expansions in TERM_EXPANSIONS.items():
        if term.lower() in query.lower():
            for expansion in expansions:
                expanded.append(query.replace(term, expansion))
    
    return expanded

# Search all variations
results = []
for q in expand_query(query):
    results.extend(search(q))
return deduplicate(results)
```

**Impact:** +10-15% F1
**Effort:** Medium (4-5 hours)
**ROI:** ⭐⭐⭐

---

#### 9. Result Re-Ranking
**Problem:** Correct files have lower ranks

**Solution:**
```python
def rerank_results(results, query):
    """Re-rank using multiple signals"""
    
    for result in results:
        score = result.base_score
        
        # Boost by file importance
        if is_core_implementation(result.path):
            score *= 1.3
        
        # Boost by query-file alignment
        if query_matches_file_type(query, result.path):
            score *= 1.2
        
        # Penalize generic/common files
        if is_generic_file(result.path):
            score *= 0.8
        
        # Boost by file size (larger = more important)
        if result.file_size:
            size_boost = min(1.2, 1.0 + (result.file_size / 10000))
            score *= size_boost
        
        result.final_score = score
    
    return sorted(results, key=lambda x: x.final_score, reverse=True)
```

**Impact:** +10-15% F1
**Effort:** Medium (5-6 hours)
**ROI:** ⭐⭐⭐

---

#### 10. Learning from Feedback
**Problem:** No improvement over time

**Solution:**
```python
class QueryLearner:
    """Learn from successful searches"""
    
    def __init__(self):
        self.patterns = {}  # term -> [file_patterns]
    
    def record_success(self, query, found_files, user_selected):
        """Learn from user selections"""
        terms = extract_key_terms(query)
        
        for term in terms:
            if term not in self.patterns:
                self.patterns[term] = []
            
            # Record which files users actually selected
            for file in user_selected:
                pattern = extract_pattern(file)
                self.patterns[term].append(pattern)
    
    def enhance_query(self, query):
        """Use learned patterns"""
        terms = extract_key_terms(query)
        hints = []
        
        for term in terms:
            if term in self.patterns:
                # Get most common patterns
                common = most_common(self.patterns[term], n=3)
                hints.extend(common)
        
        return query + ' ' + ' '.join(hints)
```

**Impact:** +15-20% F1 (over time)
**Effort:** High (8-10 hours)
**ROI:** ⭐⭐⭐⭐ (long-term)

---

## 📈 Implementation Roadmap

### Week 1: Quick Wins
- [ ] Documentation boosting (#1)
- [ ] Result limiting (#4)
- [ ] Path-based boosting (#7)

**Expected:** F1 = 0.256 → 0.32-0.35

### Week 2-3: Core Improvements
- [ ] Implementation vs test balance (#2)
- [ ] Query enhancement (#3)
- [ ] File type matching (#5)

**Expected:** F1 = 0.35 → 0.45-0.50

### Week 4-6: Advanced Features
- [ ] Multi-query splitting (#6)
- [ ] Technical term expansion (#8)
- [ ] Result re-ranking (#9)

**Expected:** F1 = 0.50 → 0.55-0.60

### Week 7+: Learning System
- [ ] Feedback learning (#10)
- [ ] Continuous improvement

**Expected:** F1 = 0.60 → 0.65-0.70

---

## 🧪 Testing Protocol

### After Each Improvement

1. **Re-run benchmark on same 4 queries**
   ```bash
   python examples/evaluate_copilot_greb.py
   ```

2. **Compare metrics**
   - F1 score change
   - Precision change
   - Recall change

3. **Test on new queries**
   - Try 5-10 more Django queries
   - Verify improvement generalizes

4. **Document results**
   - Update this document
   - Track progress

---

## 📊 Success Metrics

### Minimum Viable Improvement
- F1 = 0.35+ (37% improvement)
- Precision = 0.25+ (45% improvement)
- Recall = 0.60+ (3% improvement)

### Target Performance
- F1 = 0.50+ (95% improvement)
- Precision = 0.40+ (130% improvement)
- Recall = 0.70+ (20% improvement)

### Stretch Goal
- F1 = 0.70+ (170% improvement)
- Precision = 0.60+ (250% improvement)
- Recall = 0.85+ (45% improvement)

---

## 🔗 Related Documents

- **GREB_BENCHMARK_RESULTS.md** - Full benchmark results
- **DJANGO_TEST_QUERIES.md** - All 49 Django queries
- **REPOSITORY_COMPARISON.md** - Repository analysis
- **COPILOT_GREB_GUIDE.md** - Testing guide

---

## 💡 Quick Reference

### What to Fix First
1. Documentation boosting (easiest, high impact)
2. Query enhancement (medium effort, highest impact)
3. Implementation file priority (easy, high impact)

### What to Test
- Re-run Query 1, 4, 9, 13 after each change
- Measure improvement
- Test on new queries

### What to Measure
- F1 score (primary metric)
- Precision (reduce false positives)
- Recall (find more correct files)
- Relevance scores (correct files should rank higher)

---

**Status:** ✅ Ready for implementation
**Next Action:** Implement Priority 1 improvements
**Expected Timeline:** 2-6 weeks for full improvements
**Expected Outcome:** F1 = 0.60-0.70 (6-7x better than baseline)
