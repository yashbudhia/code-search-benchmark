# Quick Start Guide

Get started with the Code Search Benchmark in 5 minutes.

## Installation

```bash
# Clone or navigate to the repository
cd code-search-benchmark

# Install the package
pip install -e .

# Verify installation
benchmark --version
```

## Basic Usage

### 1. Generate a Gold Set (5 minutes)

```bash
# Generate test cases from your repository
benchmark generate \
  --repo /path/to/your/repo \
  --output gold_set.json

# This will:
# - Analyze Git commit history
# - Extract feature commits
# - Generate natural language queries
# - Create ground truth file lists
```

**Output:** `gold_set.json` with test cases

### 2. Evaluate an Agent (2 minutes)

```bash
# Evaluate the keyword search baseline
benchmark evaluate \
  --gold-set gold_set.json \
  --agent keyword \
  --repo /path/to/your/repo \
  --output results/

# This will:
# - Run each test case 3 times
# - Measure F1 scores and latency
# - Generate reports and visualizations
```

**Output:** 
- `results/results.json` - Detailed results
- `results/results.csv` - Tabular data
- `results/report.md` - Summary report
- `results/*.png` - Visualizations

### 3. View Results (1 minute)

```bash
# View the summary report
cat results/report.md

# Or open in your browser
# The report includes:
# - Mean/median F1 scores
# - Latency percentiles (p50, p90, p99)
# - Visualizations
```

## Evaluating Different Agents

### Built-in Agents

```bash
# Keyword search (baseline)
benchmark evaluate --agent keyword --gold-set gold_set.json --repo /path/to/repo --output results/keyword/

# Ripgrep (fast grep)
benchmark evaluate --agent ripgrep --gold-set gold_set.json --repo /path/to/repo --output results/ripgrep/

# Silver Searcher
benchmark evaluate --agent ag --gold-set gold_set.json --repo /path/to/repo --output results/ag/
```

### LLM Agents

```bash
# OpenAI GPT-4
export OPENAI_API_KEY="your-key"
benchmark evaluate --agent openai --gold-set gold_set.json --repo /path/to/repo --output results/openai/

# Anthropic Claude
export ANTHROPIC_API_KEY="your-key"
benchmark evaluate --agent claude --gold-set gold_set.json --repo /path/to/repo --output results/claude/
```

### Compare Multiple Agents

```bash
# Compare all agents at once
benchmark compare \
  --gold-set gold_set.json \
  --agents keyword,ripgrep,openai \
  --repo /path/to/repo \
  --output comparison.md
```

## Custom Agents

### For CLI Tools (e.g., Claude Code)

1. Create your agent:

```python
# my_agent.py
from benchmark.agents.cli_agent import CLIAgent

class MyToolAgent(CLIAgent):
    def __init__(self):
        super().__init__(
            command_template='mytool search "{query}"',
            output_parser=lambda output: output.strip().split('\n'),
            name="MyTool"
        )
```

2. Evaluate it:

```python
# evaluate.py
from benchmark.evaluation.engine import EvaluationEngine
from my_agent import MyToolAgent
import json

# Load gold set
with open('gold_set.json') as f:
    gold_set = json.load(f)

# Run evaluation
agent = MyToolAgent()
agent.initialize('/path/to/repo')
engine = EvaluationEngine(gold_set, agent)
results = engine.run_evaluation()
```

### For API Services (e.g., Copilot)

```python
# my_agent.py
from benchmark.agents.api_agent import APIAgent
import os

class CopilotAgent(APIAgent):
    def __init__(self):
        super().__init__(
            api_url="https://api.github.com/copilot/search",
            api_key=os.getenv("GITHUB_TOKEN"),
            name="Copilot"
        )
```

## Configuration Files

### Create a Config File

```bash
# Generate default config
benchmark init-config --output my_config.yaml

# Edit the file
# Then use it:
benchmark generate --repo /path/to/repo --output gold_set.json --config my_config.yaml
```

### Example Config

```yaml
dataset:
  repository_path: /path/to/repo
  exclude_patterns:
    - "*.md"
    - "test_*"
  min_files: 2
  max_files: 20

evaluation:
  num_runs: 3
  timeout_seconds: 30

output:
  directory: ./results
  formats: [json, csv, markdown]
  generate_visualizations: true
```

## Common Workflows

### Workflow 1: Evaluate Your Tool

```bash
# 1. Generate gold set
benchmark generate --repo /path/to/repo --output gold_set.json

# 2. Create your agent (see examples/)
# 3. Evaluate it
python examples/evaluate_custom_agent.py

# 4. View results
cat results/custom_agent/report.md
```

### Workflow 2: Compare Tools

```bash
# 1. Generate gold set once
benchmark generate --repo /path/to/repo --output gold_set.json

# 2. Evaluate multiple agents
benchmark evaluate --agent keyword --gold-set gold_set.json --repo /path/to/repo --output results/keyword/
benchmark evaluate --agent ripgrep --gold-set gold_set.json --repo /path/to/repo --output results/ripgrep/
benchmark evaluate --agent openai --gold-set gold_set.json --repo /path/to/repo --output results/openai/

# 3. Compare results
benchmark compare --gold-set gold_set.json --agents keyword,ripgrep,openai --repo /path/to/repo --output comparison.md
```

### Workflow 3: Iterate on Your Agent

```bash
# 1. Generate small gold set for testing
benchmark generate --repo /path/to/repo --output test_gold_set.json --max-files 5

# 2. Test your agent quickly
python examples/evaluate_custom_agent.py

# 3. Iterate on your agent implementation
# 4. Re-run evaluation

# 5. Once satisfied, run on full gold set
benchmark generate --repo /path/to/repo --output full_gold_set.json
python examples/evaluate_custom_agent.py
```

## Understanding Results

### F1 Score
- **1.0** = Perfect retrieval (found all relevant files, no false positives)
- **0.5** = Found half the relevant files or had 50% false positives
- **0.0** = No relevant files found

### Latency
- **p50** = Median latency (50% of queries faster than this)
- **p90** = 90th percentile (90% of queries faster than this)
- **p99** = 99th percentile (only 1% of queries slower than this)

### Good Benchmarks
- **F1 > 0.7** = Good accuracy
- **p50 < 100ms** = Fast response
- **p99 < 500ms** = Consistent performance

## Next Steps

1. **Generate your first gold set** - Start with a small repository
2. **Evaluate the baseline** - Run keyword agent to get baseline metrics
3. **Create your custom agent** - Use examples as templates
4. **Compare and iterate** - Improve your agent based on metrics

## Resources

- [README.md](README.md) - Full documentation
- [AGENT_GUIDE.md](AGENT_GUIDE.md) - Detailed agent creation guide
- [examples/](examples/) - Example implementations
- [example_config.yaml](example_config.yaml) - Configuration template

## Troubleshooting

### "Unknown agent" error
**Solution:** Check available agents with `benchmark evaluate --help` or register your custom agent in `benchmark/cli.py`

### "Not a valid Git repository" error
**Solution:** Ensure the path points to a directory with a `.git` folder

### No test cases generated
**Solution:** Adjust filtering parameters:
```bash
benchmark generate --repo /path/to/repo --output gold_set.json --min-files 1 --max-files 50
```

### Agent returns no files
**Solution:** Check that:
1. File paths are relative to repo root
2. Paths use forward slashes (`/`)
3. Files actually exist in the repository

## Getting Help

- Check [AGENT_GUIDE.md](AGENT_GUIDE.md) for detailed instructions
- See [examples/](examples/) for working code
- Review error messages carefully - they usually indicate the issue

Happy benchmarking! 🚀
