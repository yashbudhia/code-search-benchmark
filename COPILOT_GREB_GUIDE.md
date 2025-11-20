# Testing Copilot with Greb MCP

This guide shows you how to evaluate GitHub Copilot's code search using the Greb MCP tool.

## Prerequisites

1. ✅ Gold set generated (you already have `test_gold_set.json`)
2. ✅ Test repository cloned (you have `test-repo`)
3. ⚠️  Greb MCP configured in Kiro
4. ⚠️  Access to Greb MCP tool

## Quick Start

### Option 1: Manual Evaluation (Easiest)

Use this if you want to manually run queries in Kiro and copy results:

```bash
python examples/evaluate_copilot_greb.py
```

**How it works:**
1. Script shows you each query
2. You run the query in Kiro with Greb MCP
3. You copy the file paths returned
4. You paste them into the script
5. Script calculates metrics automatically

**Steps:**
1. Run the script
2. For each query, do this in Kiro:
   - Use Greb MCP to search for the query
   - Copy the file paths returned
   - Paste them into the terminal (one per line)
   - Press Enter on empty line to continue
3. View results in `results/copilot_greb/`

### Option 2: Automated Evaluation (Requires Setup)

Use this if Greb has a CLI or API interface:

```bash
python examples/evaluate_greb_automated.py
```

**Setup required:**

Edit `examples/evaluate_greb_automated.py` and configure:

```python
# If Greb has a CLI:
GREB_CLI_COMMAND = "greb search '{query}' --repo {repo} --format json"

# OR if Greb has an API:
GREB_API_URL = "http://localhost:8080/search"
```

## Customization

### Method 1: CLI Interface

If Greb has a command-line interface:

```python
from benchmark.agents.mcp_agent import GrebMCPAgent

class MyGrebAgent(GrebMCPAgent):
    def _call_greb_mcp(self, query: str):
        import subprocess
        result = subprocess.run(
            ['greb', 'search', query, '--repo', self.repo_path],
            capture_output=True,
            text=True
        )
        return result.stdout.strip().split('\n')
```

### Method 2: HTTP API

If Greb exposes an HTTP API:

```python
from benchmark.agents.mcp_agent import GrebMCPAgent
import requests

class MyGrebAgent(GrebMCPAgent):
    def _call_greb_mcp(self, query: str):
        response = requests.post(
            "http://localhost:8080/search",
            json={"query": query, "repo": self.repo_path}
        )
        return response.json().get('files', [])
```

### Method 3: Direct MCP Protocol

If you have access to MCP client:

```python
from benchmark.agents.mcp_agent import GrebMCPAgent
from mcp_client import MCPClient  # Your MCP client library

class MyGrebAgent(GrebMCPAgent):
    def __init__(self):
        super().__init__()
        self.mcp_client = MCPClient()
    
    def _call_greb_mcp(self, query: str):
        result = self.mcp_client.call_tool("greb_search", {
            "query": query,
            "repo_path": self.repo_path
        })
        return result.get("files", [])
```

## Understanding Greb MCP in Kiro

### What is Greb?

Greb is a code search tool that can be accessed through MCP (Model Context Protocol) in Kiro.

### How to Use Greb in Kiro

1. **Check if Greb is configured:**
   - Open Kiro settings
   - Look for MCP servers
   - Verify Greb is listed and enabled

2. **Test Greb manually:**
   - In Kiro chat, try: "Use Greb to search for authentication logic"
   - Or use the MCP tool directly if available

3. **Find Greb's interface:**
   - Check if Greb has a CLI: `greb --help`
   - Check if Greb has an API: Look for HTTP endpoints
   - Check Kiro's MCP documentation for Greb usage

## Example Workflow

### Step 1: Generate Gold Set (Already Done!)

You already have `test_gold_set.json` with 11 test cases.

### Step 2: Run Manual Evaluation

```bash
python examples/evaluate_copilot_greb.py
```

**Example interaction:**
```
🔍 Query: Bump actions setup-python from 5.6.0 to 6.0.0
📁 Repository: test-repo

⚠️  MANUAL STEP REQUIRED:
1. Run this query in Kiro with Greb MCP
2. Copy the file paths returned
3. Enter them below (one per line, empty line to finish):

.github/workflows/lint.yml
.github/workflows/publish.yml
.github/workflows/run-tests.yml
[press Enter on empty line]

✓ Recorded 3 files for this query
```

### Step 3: View Results

After completing all queries, check:

```bash
# View summary
cat results/copilot_greb/report.md

# View detailed data
cat results/copilot_greb/results.csv

# View visualizations
ls results/copilot_greb/*.png
```

## Comparing with Baseline

Compare Greb's performance with the keyword baseline:

```bash
# You already have keyword baseline results
cat test_results/report.md

# Compare with Greb results
cat results/copilot_greb/report.md
```

**Expected improvements:**
- Higher F1 scores (better accuracy)
- Fewer false positives
- Better understanding of semantic queries

## Troubleshooting

### "Greb not found"

**Problem:** Greb MCP tool is not accessible.

**Solutions:**
1. Check Kiro MCP settings
2. Verify Greb server is running
3. Test Greb manually in Kiro first

### "Files not validated"

**Problem:** Greb returns files that don't exist in the repository.

**Solutions:**
1. Check file path format (should be relative to repo root)
2. Ensure paths use forward slashes (`/`)
3. Verify repository path is correct

### "Timeout errors"

**Problem:** Greb takes too long to respond.

**Solutions:**
1. Increase timeout in script:
   ```python
   engine = EvaluationEngine(..., timeout_seconds=120)
   ```
2. Test with smaller gold set first
3. Check Greb server performance

## Advanced Usage

### Batch Evaluation

Evaluate multiple repositories:

```python
repos = ["test-repo", "another-repo", "third-repo"]
for repo in repos:
    # Generate gold set
    # Run evaluation
    # Compare results
```

### Custom Metrics

Add custom metrics to track:

```python
# Track query types
semantic_queries = [tc for tc in test_cases if "find" in tc.query.lower()]
keyword_queries = [tc for tc in test_cases if "bump" in tc.query.lower()]

# Analyze performance by query type
```

### Integration with CI/CD

Run benchmark automatically:

```bash
# In your CI pipeline
benchmark generate --repo $REPO --output gold_set.json --max-commits 100
python examples/evaluate_greb_automated.py
# Upload results to dashboard
```

## Next Steps

1. **Run manual evaluation** to test Greb
2. **Analyze results** and compare with baseline
3. **Automate** if Greb has CLI/API
4. **Iterate** on Greb configuration for better results
5. **Compare** with other agents (OpenAI, Claude, etc.)

## Resources

- **Greb Documentation:** Check Kiro's MCP documentation
- **MCP Protocol:** https://modelcontextprotocol.io/
- **Benchmark Guide:** See [AGENT_GUIDE.md](AGENT_GUIDE.md)
- **Examples:** See [examples/](examples/) directory

## Questions?

- Check if Greb is properly configured in Kiro
- Test Greb manually before running benchmark
- Start with manual evaluation to understand the flow
- Customize based on your Greb setup

Happy benchmarking! 🚀
