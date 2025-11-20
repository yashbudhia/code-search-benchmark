# Greb MCP Improvement Recommendations

**Based on:** Benchmark testing on Django and VS Code repositories  
**Current Performance:** F1 = 0.067-0.256 (6.7%-25.6%)  
**Target Performance:** F1 = 0.50-0.70 (50%-70%)  
**Date:** November 20, 2025

---

## 📊 Key Findings from Benchmarks

### Current Greb Performance

| Repository | Best F1 Score | Worst F1 Score | Average |
|------------|---------------|----------------|---------|
| **Django** | 0.444 | 0.080 | 0.256 |
| **VS Code** | 0.167 | 0.000 | 0.067 |

### Critical Issues Identified

1. **❌ Misses test files consistently** - Found 0/6 test files across all queries
2. **❌ Misses documentation files** - Found 0/3 docs files
3. **❌ Struggles with CSS files** - Found 0/2 CSS files in nested directories
4. **❌ Too many false positives** - Returns 10-30 files when only 2-4 are relevant
5. **❌ Path depth issues** - Struggles with deeply nested files
6. **✅ Good at finding implementation files** - When query is specific

---

## 🚀 Priority 1: Quick Wins (Implement First)

### 1. Add File Type Boosting

**Problem:** Greb doesn't prioritize test files, docs, or CSS files appropriately.

**Solution:** Boost relevance scores based on file patterns in the query.

```python
def _boost_file_types(self, query: str, files: List[str], scores: List[float]) -> List[float]:
    """Boost scores for files matching query intent.
    
    Args:
        query: The search query
        files: List of file paths
        scores: Current relevance scores
        
    Returns:
        Adjusted scores with file type boosting
    """
    boosted_scores = scores.copy()
    
    # Detect query intent
    query_lower = query.lower()
    is_test_query = any(word in query_lower for word in ['test', 'testing', 'spec', 'unittest'])
    is_doc_query = any(word in query_lower for word in ['doc', 'documentation', 'readme', 'guide'])
    is_css_query = any(word in query_lower for word in ['css', 'style', 'styling', 'stylesheet'])
    
    for i, file_path in enumerate(files):
        file_lower = file_path.lower()
        
        # Boost test files when query mentions tests
        if is_test_query and ('test' in file_lower or 'spec' in file_lower):
            boosted_scores[i] *= 2.0
        
        # Boost documentation files when query mentions docs
        if is_doc_query and any(doc in file_lower for doc in ['doc', 'readme', 'guide', 'changelog']):
            boosted_scores[i] *= 2.0
        
        # Boost CSS files when query mentions styling
        if is_css_query and file_lower.endswith('.css'):
            boosted_scores[i] *= 2.0
        
        # Penalize unrelated file types
        if is_test_query and 'test' not in file_lower:
            boosted_scores[i] *= 0.5
        
        if is_css_query and not file_lower.endswith(('.css', '.scss', '.less')):
            boosted_scores[i] *= 0.3
    
    return boosted_scores
```

**Expected Impact:** +15-20% F1 score improvement

---

### 2. Implement Result Limiting with Confidence Threshold

**Problem:** Greb returns too many low-relevance files (10-30 when only 2-4 are relevant).

**Solution:** Filter results by relevance threshold and limit count.

```python
def _filter_results(self, files: List[str], scores: List[float], 
                   max_results: int = 10, min_score: float = 0.3) -> tuple:
    """Filter results by relevance and limit count.
    
    Args:
        files: List of file paths
        scores: Relevance scores (0-1)
        max_results: Maximum number of results to return
        min_score: Minimum relevance score threshold
        
    Returns:
        Tuple of (filtered_files, filtered_scores)
    """
    if not scores:
        # If no scores, return top N files
        return files[:max_results], scores[:max_results] if scores else []
    
    # Filter by minimum score
    filtered = [(f, s) for f, s in zip(files, scores) if s >= min_score]
    
    # Sort by score descending
    filtered.sort(key=lambda x: x[1], reverse=True)
    
    # Limit to max results
    filtered = filtered[:max_results]
    
    if filtered:
        files, scores = zip(*filtered)
        return list(files), list(scores)
    
    return [], []
```

**Expected Impact:** +10-15% precision improvement, +5-10% F1 improvement

---

### 3. Add Path-Based Relevance Boosting

**Problem:** Greb doesn't understand that files in the same directory are often related.

**Solution:** Boost files that share path components with high-scoring files.

```python
def _boost_related_paths(self, files: List[str], scores: List[float]) -> List[float]:
    """Boost files in same directories as high-scoring files.
    
    Args:
        files: List of file paths
        scores: Current relevance scores
        
    Returns:
        Adjusted scores with path boosting
    """
    if not scores or len(files) < 2:
        return scores
    
    boosted_scores = scores.copy()
    
    # Find high-confidence files (top 20% of scores)
    threshold = sorted(scores, reverse=True)[min(len(scores)//5, len(scores)-1)]
    high_conf_files = [f for f, s in zip(files, scores) if s >= threshold]
    
    # Extract directory paths from high-confidence files
    high_conf_dirs = set()
    for file_path in high_conf_files:
        parts = file_path.split('/')
        # Add all parent directories
        for i in range(1, len(parts)):
            high_conf_dirs.add('/'.join(parts[:i]))
    
    # Boost files in same directories
    for i, file_path in enumerate(files):
        file_dir = '/'.join(file_path.split('/')[:-1])
        
        # Check if file is in a high-confidence directory
        if file_dir in high_conf_dirs:
            # Boost by 20%
            boosted_scores[i] *= 1.2
        
        # Check for partial path matches
        for hc_dir in high_conf_dirs:
            if hc_dir in file_path and hc_dir != file_dir:
                # Smaller boost for partial matches
                boosted_scores[i] *= 1.1
                break
    
    return boosted_scores
```

**Expected Impact:** +5-10% recall improvement

---

## 🎯 Priority 2: Medium-Term Improvements

### 4. Implement Multi-Query Strategy

**Problem:** Complex queries (like "MCP titles look like regular tool titles") confuse Greb.

**Solution:** Break complex queries into multiple simpler queries and merge results.

```python
def _split_complex_query(self, query: str) -> List[str]:
    """Split complex query into multiple simpler queries.
    
    Args:
        query: Original complex query
        
    Returns:
        List of simpler queries
    """
    queries = [query]  # Always include original
    
    # Extract key technical terms (CamelCase, snake_case, specific patterns)
    import re
    
    # Find CamelCase identifiers
    camel_case = re.findall(r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b', query)
    
    # Find snake_case identifiers
    snake_case = re.findall(r'\b[a-z]+(?:_[a-z]+)+\b', query)
    
    # Find file extensions
    extensions = re.findall(r'\b\w+\.(ts|js|py|css|html|md)\b', query)
    
    # Create focused queries
    if camel_case:
        queries.append(' '.join(camel_case))
    
    if snake_case:
        queries.append(' '.join(snake_case))
    
    if extensions:
        queries.append(' '.join(extensions))
    
    # Extract quoted phrases
    quoted = re.findall(r'"([^"]+)"', query)
    queries.extend(quoted)
    
    return list(set(queries))  # Remove duplicates

def retrieve_multi_query(self, query: str) -> RetrievalResult:
    """Execute multiple queries and merge results.
    
    Args:
        query: Original search query
        
    Returns:
        Merged RetrievalResult
    """
    queries = self._split_complex_query(query)
    
    all_files = {}  # file -> max_score
    
    for sub_query in queries:
        result = self.retrieve(sub_query)
        
        # Merge results, keeping highest score for each file
        for file, score in zip(result.files, result.scores or [1.0] * len(result.files)):
            if file not in all_files or score > all_files[file]:
                all_files[file] = score
    
    # Sort by score
    sorted_results = sorted(all_files.items(), key=lambda x: x[1], reverse=True)
    files, scores = zip(*sorted_results) if sorted_results else ([], [])
    
    return RetrievalResult(
        files=list(files),
        scores=list(scores),
        metadata={"queries_used": queries, "strategy": "multi_query"}
    )
```

**Expected Impact:** +10-15% F1 improvement on complex queries

---

### 5. Add Query Enhancement Layer

**Problem:** Vague queries like "fix" or "support skills" don't provide enough context.

**Solution:** Automatically enhance queries with context.

```python
def _enhance_query(self, query: str) -> str:
    """Enhance vague queries with additional context.
    
    Args:
        query: Original query
        
    Returns:
        Enhanced query with more context
    """
    query_lower = query.lower()
    
    # Detect vague action words
    vague_actions = {
        'fix': 'bug fix implementation',
        'add': 'feature implementation',
        'remove': 'code removal refactor',
        'update': 'code update modification',
        'implement': 'implementation code',
        'support': 'feature support implementation'
    }
    
    # Replace vague words with more specific terms
    enhanced = query
    for vague, specific in vague_actions.items():
        if vague in query_lower and len(query.split()) < 5:
            enhanced = enhanced.replace(vague, specific)
    
    # Add file type hints if missing
    if not any(ext in query_lower for ext in ['.ts', '.js', '.py', '.css', 'test', 'doc']):
        # Try to infer file type from context
        if any(word in query_lower for word in ['class', 'function', 'method', 'interface']):
            enhanced += ' implementation file'
        elif any(word in query_lower for word in ['style', 'css', 'layout']):
            enhanced += ' CSS stylesheet'
        elif any(word in query_lower for word in ['test', 'spec', 'unit']):
            enhanced += ' test file'
    
    return enhanced
```

**Expected Impact:** +5-10% F1 improvement on vague queries

---

### 6. Implement Caching and Incremental Search

**Problem:** Repeated searches are slow and wasteful.

**Solution:** Cache results and use incremental refinement.

```python
import hashlib
from functools import lru_cache

class GrebMCPAgent(MCPAgent):
    def __init__(self):
        super().__init__(mcp_tool_name="greb_search", name="GrebMCP")
        self._cache = {}
        self._cache_hits = 0
        self._cache_misses = 0
    
    def _get_cache_key(self, query: str) -> str:
        """Generate cache key for query."""
        return hashlib.md5(f"{self.repo_path}:{query}".encode()).hexdigest()
    
    def retrieve(self, query: str) -> RetrievalResult:
        """Execute search with caching."""
        cache_key = self._get_cache_key(query)
        
        # Check cache
        if cache_key in self._cache:
            self._cache_hits += 1
            return self._cache[cache_key]
        
        self._cache_misses += 1
        
        # Execute search
        result = self._execute_search(query)
        
        # Cache result
        self._cache[cache_key] = result
        
        return result
    
    def get_cache_stats(self) -> dict:
        """Get cache performance statistics."""
        total = self._cache_hits + self._cache_misses
        hit_rate = self._cache_hits / total if total > 0 else 0
        
        return {
            "hits": self._cache_hits,
            "misses": self._cache_misses,
            "hit_rate": hit_rate,
            "cache_size": len(self._cache)
        }
```

**Expected Impact:** 50-70% latency reduction on repeated queries

---

## 🔬 Priority 3: Advanced Improvements

### 7. Add Learning from Successful Searches

**Problem:** Greb doesn't learn from which queries work well.

**Solution:** Track successful query patterns and use them to improve future searches.

```python
class GrebMCPAgent(MCPAgent):
    def __init__(self):
        super().__init__(mcp_tool_name="greb_search", name="GrebMCP")
        self._successful_patterns = {}  # pattern -> success_rate
    
    def record_success(self, query: str, found_files: List[str], expected_files: List[str]):
        """Record successful query patterns.
        
        Args:
            query: The query used
            found_files: Files returned by Greb
            expected_files: Files that were expected
        """
        # Calculate success metrics
        found_set = set(found_files)
        expected_set = set(expected_files)
        
        precision = len(found_set & expected_set) / len(found_set) if found_set else 0
        recall = len(found_set & expected_set) / len(expected_set) if expected_set else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
        
        # Extract patterns from successful queries
        if f1 > 0.5:  # Only learn from good results
            patterns = self._extract_patterns(query)
            for pattern in patterns:
                if pattern not in self._successful_patterns:
                    self._successful_patterns[pattern] = []
                self._successful_patterns[pattern].append(f1)
    
    def _extract_patterns(self, query: str) -> List[str]:
        """Extract reusable patterns from query."""
        import re
        patterns = []
        
        # Extract technical terms
        camel_case = re.findall(r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)+\b', query)
        patterns.extend(camel_case)
        
        # Extract file type mentions
        file_types = re.findall(r'\b(test|doc|css|implementation|interface)\b', query.lower())
        patterns.extend(file_types)
        
        return patterns
    
    def _apply_learned_patterns(self, query: str) -> str:
        """Enhance query using learned successful patterns."""
        # Find patterns in current query
        current_patterns = self._extract_patterns(query)
        
        # Find related successful patterns
        related_patterns = []
        for pattern in current_patterns:
            if pattern in self._successful_patterns:
                avg_success = sum(self._successful_patterns[pattern]) / len(self._successful_patterns[pattern])
                if avg_success > 0.6:
                    related_patterns.append(pattern)
        
        # Enhance query with successful patterns
        if related_patterns:
            query += " " + " ".join(related_patterns)
        
        return query
```

**Expected Impact:** +10-15% F1 improvement over time

---

## 📝 Implementation Plan

### Week 1: Quick Wins
1. ✅ Implement file type boosting
2. ✅ Add result filtering and limiting
3. ✅ Test on 5-10 benchmark queries
4. ✅ Measure improvement

**Expected Result:** F1 = 0.35-0.45 (35-45%)

### Week 2: Medium-Term
1. ✅ Implement path-based boosting
2. ✅ Add multi-query strategy
3. ✅ Implement query enhancement
4. ✅ Test on full benchmark suite

**Expected Result:** F1 = 0.50-0.60 (50-60%)

### Week 3: Advanced
1. ✅ Add caching layer
2. ✅ Implement learning system
3. ✅ Fine-tune all parameters
4. ✅ Final benchmark run

**Expected Result:** F1 = 0.60-0.70 (60-70%)

---

## 🔧 Updated MCP Agent Implementation

Here's the complete updated `GrebMCPAgent` class with all improvements:

```python
class GrebMCPAgent(MCPAgent):
    """Enhanced Greb MCP agent with improved accuracy and speed."""
    
    def __init__(self):
        super().__init__(mcp_tool_name="greb_search", name="GrebMCP")
        self._cache = {}
        self._successful_patterns = {}
        self._cache_hits = 0
        self._cache_misses = 0
    
    def retrieve(self, query: str) -> RetrievalResult:
        """Execute search with all enhancements."""
        # Check cache first
        cache_key = self._get_cache_key(query)
        if cache_key in self._cache:
            self._cache_hits += 1
            return self._cache[cache_key]
        
        self._cache_misses += 1
        
        try:
            # Enhance query
            enhanced_query = self._enhance_query(query)
            enhanced_query = self._apply_learned_patterns(enhanced_query)
            
            # Execute search (possibly multi-query)
            if self._is_complex_query(query):
                result = self._retrieve_multi_query(enhanced_query)
            else:
                result = self._retrieve_single(enhanced_query)
            
            # Apply all boosting strategies
            files, scores = result.files, result.scores or [1.0] * len(result.files)
            
            # 1. File type boosting
            scores = self._boost_file_types(query, files, scores)
            
            # 2. Path-based boosting
            scores = self._boost_related_paths(files, scores)
            
            # 3. Filter and limit results
            files, scores = self._filter_results(files, scores, max_results=10, min_score=0.3)
            
            result = RetrievalResult(
                files=files,
                scores=scores,
                metadata={
                    **result.metadata,
                    "enhanced_query": enhanced_query,
                    "original_query": query,
                    "improvements_applied": ["file_type_boost", "path_boost", "filtering"]
                }
            )
            
            # Cache result
            self._cache[cache_key] = result
            
            return result
            
        except Exception as e:
            return RetrievalResult(
                files=[],
                scores=[],
                metadata={"error": str(e), "tool": "greb_mcp"}
            )
    
    # ... (include all the helper methods from above)
```

---

## 📊 Expected Performance Improvements

| Improvement | Current F1 | Expected F1 | Gain |
|-------------|-----------|-------------|------|
| **Baseline (Current)** | 0.067-0.256 | - | - |
| **+ Quick Wins** | - | 0.35-0.45 | +30-40% |
| **+ Medium-Term** | - | 0.50-0.60 | +50-60% |
| **+ Advanced** | - | 0.60-0.70 | +60-70% |

### Latency Improvements

| Operation | Current | With Caching | Improvement |
|-----------|---------|--------------|-------------|
| **First Query** | ~16ms | ~16ms | 0% |
| **Repeated Query** | ~16ms | ~1ms | **94%** |
| **Similar Query** | ~16ms | ~8ms | **50%** |

---

## 🧪 Testing Strategy

### 1. Unit Tests
```python
def test_file_type_boosting():
    agent = GrebMCPAgent()
    files = ["src/test.py", "src/main.py", "docs/readme.md"]
    scores = [0.5, 0.5, 0.5]
    
    # Test query mentions "test"
    boosted = agent._boost_file_types("find test cases", files, scores)
    assert boosted[0] > boosted[1]  # test.py should be boosted

def test_result_filtering():
    agent = GrebMCPAgent()
    files = ["a.py", "b.py", "c.py"]
    scores = [0.9, 0.4, 0.2]
    
    filtered_files, filtered_scores = agent._filter_results(
        files, scores, max_results=2, min_score=0.3
    )
    
    assert len(filtered_files) == 2
    assert "c.py" not in filtered_files  # Below threshold
```

### 2. Integration Tests
```bash
# Run on benchmark suite
python -m pytest tests/test_greb_improvements.py

# Run on specific test cases
python examples/evaluate_greb_automated.py --test-improvements
```

### 3. A/B Testing
```python
# Compare old vs new implementation
from benchmark.evaluation.engine import EvaluationEngine

old_agent = GrebMCPAgent()  # Without improvements
new_agent = EnhancedGrebMCPAgent()  # With improvements

results_old = engine.evaluate(old_agent, gold_set)
results_new = engine.evaluate(new_agent, gold_set)

print(f"Old F1: {results_old.f1_score:.3f}")
print(f"New F1: {results_new.f1_score:.3f}")
print(f"Improvement: {(results_new.f1_score - results_old.f1_score) / results_old.f1_score * 100:.1f}%")
```

---

## 🎯 Success Metrics

### Accuracy Targets
- ✅ **F1 Score:** 0.60+ (currently 0.067-0.256)
- ✅ **Precision:** 0.70+ (currently 0.037-0.333)
- ✅ **Recall:** 0.60+ (currently 0.000-0.667)

### Speed Targets
- ✅ **First Query:** <20ms (currently ~16ms) ✓
- ✅ **Cached Query:** <2ms (currently ~16ms)
- ✅ **Cache Hit Rate:** >50% after 10 queries

### User Experience
- ✅ **Relevant Results:** Top 5 results should include 80%+ of expected files
- ✅ **False Positives:** <30% of returned files should be irrelevant
- ✅ **Query Success Rate:** 70%+ of queries should find at least 1 expected file

---

## 📚 Next Steps

1. **Implement Quick Wins** (Week 1)
   - Start with file type boosting
   - Add result filtering
   - Test on 5 benchmark queries

2. **Measure Baseline** (Week 1)
   - Run full benchmark suite
   - Document current performance
   - Identify worst-performing queries

3. **Iterate and Improve** (Weeks 2-3)
   - Implement medium-term improvements
   - A/B test each improvement
   - Fine-tune parameters

4. **Deploy and Monitor** (Week 4)
   - Roll out to production
   - Monitor real-world performance
   - Collect user feedback

---

## 🔗 Related Documents

- **GREB_BENCHMARK_RESULTS.md** - Current benchmark results
- **VSCODE_TEST_QUERIES.md** - VS Code test cases
- **DJANGO_TEST_QUERIES.md** - Django test cases
- **benchmark/agents/mcp_agent.py** - Current implementation

---

**Last Updated:** November 20, 2025  
**Status:** Ready for Implementation 🚀
