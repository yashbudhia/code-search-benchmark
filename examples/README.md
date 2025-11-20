# Examples

This directory contains example scripts and agent implementations.

## Files

### `custom_agent_example.py`

Contains template implementations for various types of agents:

- **SimpleCLIAgent** - Template for any CLI-based search tool
- **ClaudeCodeCLIAgent** - Example for Claude Code CLI integration
- **GitHubCopilotAgent** - Example for GitHub Copilot API
- **CustomSearchAgent** - Example using Python libraries
- **ExternalServiceAgent** - Example for external API services

**Usage:**
```python
# Copy the agent class you need
from custom_agent_example import SimpleCLIAgent

# Modify it for your tool
class MyToolAgent(SimpleCLIAgent):
    def __init__(self):
        super().__init__()
        self.command_template = 'mytool search "{query}"'
```

### `evaluate_custom_agent.py`

Shows how to evaluate a custom agent without modifying the CLI code.

**Usage:**
```bash
# 1. Edit the script to import your agent
# 2. Update configuration (paths, etc.)
# 3. Run the script
python examples/evaluate_custom_agent.py
```

## Quick Start

### Evaluating a CLI Tool

1. Copy `SimpleCLIAgent` from `custom_agent_example.py`
2. Modify the `command_template` to match your tool's syntax
3. Adjust the `_parse_output` method to parse your tool's output
4. Use `evaluate_custom_agent.py` to run evaluation

Example:
```python
class MyToolAgent(CLIAgent):
    def __init__(self):
        super().__init__(
            command_template='mytool search "{query}" --repo {repo}',
            output_parser=lambda output: output.strip().split('\n'),
            name="MyTool"
        )
```

### Evaluating an API Service

1. Copy `ExternalServiceAgent` from `custom_agent_example.py`
2. Update the API URL and authentication
3. Modify the `retrieve` method to match the API format
4. Use `evaluate_custom_agent.py` to run evaluation

Example:
```python
class MyAPIAgent(APIAgent):
    def __init__(self):
        super().__init__(
            api_url="https://api.myservice.com/search",
            api_key=os.getenv("MY_API_KEY"),
            name="MyAPI"
        )
```

## Integration Methods

### Method 1: Direct Script (Recommended for Testing)

Use `evaluate_custom_agent.py` to test your agent without modifying the benchmark code:

```python
# In evaluate_custom_agent.py
from my_agents import MyCustomAgent

agent = MyCustomAgent()
# ... rest of evaluation
```

### Method 2: CLI Registration (Recommended for Production)

Register your agent in `benchmark/cli.py` for permanent integration:

```python
# In benchmark/cli.py
def _load_agent(agent_name: str, repo_path: str):
    from my_agents import MyCustomAgent
    
    agents = {
        "keyword": KeywordSearchAgent,
        "mycustom": MyCustomAgent,  # Add here
    }
    # ...
```

Then use via CLI:
```bash
benchmark evaluate --agent mycustom --gold-set gold_set.json --repo /path/to/repo --output results/
```

## Common Patterns

### Pattern 1: CLI Tool with JSON Output

```python
class JSONCLIAgent(CLIAgent):
    def __init__(self):
        super().__init__(
            command_template='tool search "{query}" --json',
            output_parser=self._parse_json,
            name="JSONTool"
        )
    
    @staticmethod
    def _parse_json(output: str):
        import json
        data = json.loads(output)
        return data.get("files", [])
```

### Pattern 2: API with Pagination

```python
class PaginatedAPIAgent(APIAgent):
    def retrieve(self, query: str):
        all_files = []
        page = 1
        
        while len(all_files) < 20:  # Get top 20
            response = requests.get(
                f"{self.api_url}/search",
                params={"query": query, "page": page}
            )
            
            files = response.json().get("files", [])
            if not files:
                break
            
            all_files.extend(files)
            page += 1
        
        return RetrievalResult(files=all_files[:20])
```

### Pattern 3: Agent with Caching

```python
class CachedAgent(RetrievalAgent):
    def __init__(self):
        super().__init__(name="Cached")
        self.cache = {}
    
    def retrieve(self, query: str):
        if query in self.cache:
            return self.cache[query]
        
        result = self._do_search(query)
        self.cache[query] = result
        return result
    
    def reset(self):
        self.cache.clear()  # Important!
```

## Troubleshooting

### Issue: Files not found in results

**Problem:** Your agent returns files but they're not counted in metrics.

**Solution:** Ensure file paths are:
- Relative to repository root
- Using forward slashes (`/`)
- Actually exist in the repository

```python
# Good
"src/utils/helper.py"

# Bad
"/absolute/path/src/utils/helper.py"
"src\\utils\\helper.py"
```

### Issue: Agent times out

**Problem:** Agent takes too long to respond.

**Solution:** Implement timeout handling:

```python
def retrieve(self, query: str):
    try:
        # Your search with timeout
        result = search_with_timeout(query, timeout=30)
        return RetrievalResult(files=result)
    except TimeoutError:
        return RetrievalResult(files=[], metadata={"error": "timeout"})
```

### Issue: Import errors

**Problem:** Can't import benchmark modules.

**Solution:** Add parent directory to path:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from benchmark.agents.base import RetrievalAgent
```

## Next Steps

1. Choose an example that matches your use case
2. Copy and modify the agent class
3. Test with `evaluate_custom_agent.py`
4. Register in CLI for production use
5. Run full evaluation and analyze results

For more details, see [AGENT_GUIDE.md](../AGENT_GUIDE.md) in the root directory.
