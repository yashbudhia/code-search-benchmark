# Agent Evaluation Guide

This guide explains how to evaluate different code search systems using the benchmark.

## Quick Start

### Built-in Agents

The benchmark includes several ready-to-use agents:

```bash
# Keyword search baseline
benchmark evaluate --gold-set gold_set.json --agent keyword --repo /path/to/repo --output results/

# Ripgrep (if installed)
benchmark evaluate --gold-set gold_set.json --agent ripgrep --repo /path/to/repo --output results/

# Silver Searcher (if installed)
benchmark evaluate --gold-set gold_set.json --agent ag --repo /path/to/repo --output results/
```

### LLM-Based Agents

For OpenAI or Anthropic agents, set environment variables:

```bash
# OpenAI (GPT-4)
export OPENAI_API_KEY="your-key-here"
export OPENAI_MODEL="gpt-4"  # Optional, defaults to gpt-4
benchmark evaluate --gold-set gold_set.json --agent openai --repo /path/to/repo --output results/

# Anthropic (Claude)
export ANTHROPIC_API_KEY="your-key-here"
export ANTHROPIC_MODEL="claude-3-opus-20240229"  # Optional
benchmark evaluate --gold-set gold_set.json --agent claude --repo /path/to/repo --output results/
```

## Creating Custom Agents

### 1. CLI-Based Agents (e.g., Claude Code, Copilot CLI)

For command-line tools, create a custom CLI agent:

```python
# my_agents.py
from benchmark.agents.cli_agent import CLIAgent

class ClaudeCodeAgent(CLIAgent):
    """Adapter for Claude Code CLI."""
    
    def __init__(self):
        super().__init__(
            # Adjust command to match your CLI tool's syntax
            command_template='claude-code search "{query}" --repo {repo}',
            output_parser=self._parse_output,
            name="ClaudeCode"
        )
    
    @staticmethod
    def _parse_output(output: str):
        """Parse your tool's output format."""
        # Example: Extract file paths from output
        files = []
        for line in output.split('\n'):
            if line.endswith('.py') or line.endswith('.js'):
                files.append(line.strip())
        return files

# Register in CLI
# Add to benchmark/cli.py _load_agent() function:
# from my_agents import ClaudeCodeAgent
# agents["claude-code"] = ClaudeCodeAgent
```

### 2. API-Based Agents (e.g., GitHub Copilot, Codeium)

For API-based services:

```python
# my_agents.py
from benchmark.agents.api_agent import APIAgent
import os

class CopilotAgent(APIAgent):
    """GitHub Copilot adapter."""
    
    def __init__(self):
        super().__init__(
            api_url="https://api.github.com/copilot/search",
            api_key=os.getenv("GITHUB_TOKEN"),
            name="GitHubCopilot"
        )
    
    def retrieve(self, query: str):
        """Custom retrieval logic for Copilot API."""
        # Implement Copilot-specific API calls
        # See benchmark/agents/api_agent.py for examples
        return super().retrieve(query)
```

### 3. Python Library Agents

For tools with Python APIs:

```python
# my_agents.py
from benchmark.agents.base import RetrievalAgent
from benchmark.models import RetrievalResult

class MyCustomAgent(RetrievalAgent):
    """Custom agent using a Python library."""
    
    def __init__(self):
        super().__init__(name="MyCustom")
        self.search_engine = None
    
    def initialize(self, repo_path: str):
        """Setup your search engine."""
        # Initialize your search library
        from my_search_lib import SearchEngine
        self.search_engine = SearchEngine(repo_path)
        self.search_engine.index()
    
    def retrieve(self, query: str):
        """Execute search."""
        results = self.search_engine.search(query)
        
        # Extract file paths from results
        files = [r.file_path for r in results]
        scores = [r.score for r in results]
        
        return RetrievalResult(
            files=files,
            scores=scores,
            metadata={"engine": "my_search_lib"}
        )
    
    def reset(self):
        """Clear caches between queries."""
        if self.search_engine:
            self.search_engine.clear_cache()
```

## Registering Custom Agents

### Option 1: Modify CLI (Permanent)

Edit `benchmark/cli.py` and add your agent to the registry:

```python
def _load_agent(agent_name: str, repo_path: str):
    from benchmark.agents.keyword_search import KeywordSearchAgent
    from my_agents import ClaudeCodeAgent, CopilotAgent  # Import your agents
    
    agents = {
        "keyword": KeywordSearchAgent,
        "claude-code": ClaudeCodeAgent,  # Add here
        "copilot": CopilotAgent,         # Add here
    }
    # ... rest of function
```

### Option 2: Python Script (Temporary)

Create a custom evaluation script:

```python
# evaluate_custom.py
from benchmark.dataset.dataset_generator import DatasetGenerator
from benchmark.evaluation.engine import EvaluationEngine
from benchmark.metrics.calculator import MetricsCalculator
from benchmark.reporting.report_generator import ReportGenerator
from benchmark.models import GoldSet
import json

from my_agents import ClaudeCodeAgent  # Your custom agent

# Load gold set
with open('gold_set.json', 'r') as f:
    gold_set_data = json.load(f)
# ... deserialize gold set

# Initialize your agent
agent = ClaudeCodeAgent()
agent.initialize('/path/to/repo')

# Run evaluation
engine = EvaluationEngine(gold_set, agent)
results = engine.run_evaluation(num_runs=3)

# Calculate metrics
calculator = MetricsCalculator()
metrics = calculator.aggregate_metrics(results.results)

# Generate reports
report_gen = ReportGenerator(results, metrics)
report_gen.export_json('results/results.json')
report_gen.export_csv('results/results.csv')
report_gen.export_markdown('results/report.md')

print(f"Mean F1: {metrics.mean_f1:.3f}")
print(f"p50 Latency: {metrics.p50_latency:.2f}ms")
```

## Real-World Examples

### Example 1: Evaluating Ripgrep

```bash
# Make sure ripgrep is installed
rg --version

# Run evaluation
benchmark evaluate \
  --gold-set gold_set.json \
  --agent ripgrep \
  --repo /path/to/repo \
  --output results/ripgrep/
```

### Example 2: Evaluating OpenAI GPT-4

```bash
# Set API key
export OPENAI_API_KEY="sk-..."

# Run evaluation
benchmark evaluate \
  --gold-set gold_set.json \
  --agent openai \
  --repo /path/to/repo \
  --output results/openai/
```

### Example 3: Comparing Multiple Agents

```bash
# Compare keyword, ripgrep, and OpenAI
benchmark compare \
  --gold-set gold_set.json \
  --agents keyword,ripgrep,openai \
  --repo /path/to/repo \
  --output comparison.md
```

## Agent Interface Requirements

All agents must implement three methods:

```python
class MyAgent(RetrievalAgent):
    def initialize(self, repo_path: str) -> None:
        """Called once before evaluation starts.
        
        Use this to:
        - Index repository files
        - Load models or embeddings
        - Setup API clients
        - Perform any expensive one-time setup
        """
        pass
    
    def retrieve(self, query: str) -> RetrievalResult:
        """Called for each test case.
        
        Args:
            query: Natural language search query
            
        Returns:
            RetrievalResult with:
            - files: List of file paths (relative to repo root)
            - scores: Optional confidence scores
            - metadata: Optional additional info
        """
        pass
    
    def reset(self) -> None:
        """Called between test cases.
        
        Use this to:
        - Clear query-specific caches
        - Reset any state that might affect next query
        - Ensure fair evaluation without state leakage
        """
        pass
```

## Tips for Accurate Evaluation

1. **File Path Format**: Always return paths relative to repo root with forward slashes
   ```python
   # Good
   "src/utils/helper.py"
   
   # Bad
   "/absolute/path/to/src/utils/helper.py"
   "src\\utils\\helper.py"  # Windows backslashes
   ```

2. **Timeout Handling**: Implement timeouts in your agent to prevent hanging
   ```python
   def retrieve(self, query: str):
       try:
           # Your search logic with timeout
           result = search_with_timeout(query, timeout=30)
       except TimeoutError:
           return RetrievalResult(files=[], metadata={"error": "timeout"})
   ```

3. **Error Handling**: Return empty results on errors, don't raise exceptions
   ```python
   def retrieve(self, query: str):
       try:
           # Your search logic
           return RetrievalResult(files=files)
       except Exception as e:
           return RetrievalResult(files=[], metadata={"error": str(e)})
   ```

4. **State Management**: Ensure `reset()` clears all caches
   ```python
   def reset(self):
       self.query_cache.clear()
       self.result_cache.clear()
       # Clear any other stateful data
   ```

## Troubleshooting

### Agent Not Found

```
Error: Unknown agent 'myagent'. Available agents: keyword, ripgrep
```

**Solution**: Register your agent in `benchmark/cli.py` or use a custom evaluation script.

### Import Errors

```
ImportError: No module named 'openai'
```

**Solution**: Install required dependencies:
```bash
pip install openai  # For OpenAI agents
pip install anthropic  # For Claude agents
```

### File Path Validation Failures

If your agent returns files but they're not counted:

1. Check file paths are relative to repo root
2. Ensure forward slashes (not backslashes)
3. Verify files actually exist in the repository

### API Rate Limits

For API-based agents, you may hit rate limits:

```python
def retrieve(self, query: str):
    import time
    
    # Add retry logic with backoff
    for attempt in range(3):
        try:
            return self._call_api(query)
        except RateLimitError:
            time.sleep(2 ** attempt)  # Exponential backoff
    
    return RetrievalResult(files=[], metadata={"error": "rate_limit"})
```

## Next Steps

1. Create your custom agent following the examples above
2. Test it on a small gold set first
3. Run full evaluation and analyze results
4. Compare against baseline agents
5. Iterate and improve your agent based on metrics

For more examples, see:
- `benchmark/agents/keyword_search.py` - Simple baseline
- `benchmark/agents/cli_agent.py` - CLI tool adapters
- `benchmark/agents/api_agent.py` - API service adapters
- `benchmark/agents/llm_agent.py` - LLM-based agents
