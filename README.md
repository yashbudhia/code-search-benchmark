# Code Search Benchmark System

A framework for evaluating code retrieval agents using Git commit history.

## Overview

The Code Search Benchmark System automatically generates test datasets from Git repositories and measures the accuracy and speed of code search systems. It evaluates retrieval quality using weighted F1 scores and tracks end-to-end latency.

## Project Structure

```
benchmark/
├── dataset/       # Dataset generation from Git history
├── evaluation/    # Evaluation engine and orchestration
├── metrics/       # Metrics calculation (F1 scores, latency)
├── reporting/     # Report generation and export
├── agents/        # Retrieval agent interface and implementations
└── models.py      # Core data models
```

## Installation

```bash
pip install -e .
```

### Optional Dependencies

For LLM-based query transformation:
```bash
pip install -e ".[llm]"
```

For semantic search baseline:
```bash
pip install -e ".[semantic]"
```

For development tools:
```bash
pip install -e ".[dev]"
```

## Quick Start

**New to the benchmark?** See [QUICK_START.md](QUICK_START.md) for a 5-minute tutorial.

### 1. Generate a Gold Set

Create a benchmark dataset from a Git repository:

```bash
benchmark generate --repo /path/to/your/repo --output gold_set.json
```

With custom filtering:

```bash
benchmark generate \
  --repo /path/to/your/repo \
  --output gold_set.json \
  --min-files 3 \
  --max-files 15 \
  --exclude-pattern "*.test.js" \
  --exclude-pattern "*.spec.ts"
```

### 2. Evaluate a Retrieval Agent

Run evaluation on a code search system:

```bash
benchmark evaluate \
  --gold-set gold_set.json \
  --agent keyword \
  --repo /path/to/your/repo \
  --output results/
```

This will generate:
- `results/results.json` - Detailed results
- `results/results.csv` - Tabular data
- `results/report.md` - Summary report
- `results/*.png` - Visualizations

### 3. Compare Multiple Agents

Compare different retrieval systems side-by-side:

```bash
benchmark compare \
  --gold-set gold_set.json \
  --agents keyword,semantic \
  --repo /path/to/your/repo \
  --output comparison.md
```

### 4. Using Configuration Files

Create a default configuration file:

```bash
benchmark init-config --output my_config.yaml
```

Or copy the example configuration:

```bash
cp example_config.yaml my_config.yaml
# Edit my_config.yaml with your settings
```

Then use it with the generate command:

```bash
benchmark generate --repo /path/to/repo --output gold_set.json --config my_config.yaml
```

## Available Commands

- `benchmark generate` - Generate a gold set from Git history
- `benchmark evaluate` - Evaluate a single retrieval agent
- `benchmark compare` - Compare multiple agents
- `benchmark init-config` - Create a default configuration file

Run `benchmark --help` or `benchmark <command> --help` for more details.

## Example Workflow

Here's a complete example of using the benchmark system:

```bash
# 1. Install the package
pip install -e .

# 2. Generate a gold set from your repository
benchmark generate \
  --repo /path/to/your/repo \
  --output gold_set.json \
  --min-files 2 \
  --max-files 15

# 3. Evaluate the keyword search baseline
benchmark evaluate \
  --gold-set gold_set.json \
  --agent keyword \
  --repo /path/to/your/repo \
  --output results/keyword/

# 4. View the results
cat results/keyword/report.md
```

The evaluation will output:
- **F1 Score Metrics**: Mean, median, and standard deviation
- **Latency Metrics**: p50, p90, p99 percentiles
- **Visualizations**: Histograms and scatter plots
- **Detailed Results**: JSON and CSV exports for further analysis

## Evaluating Different Agents

The benchmark supports multiple types of agents:

### Built-in Agents

- **keyword** - Simple keyword search baseline
- **ripgrep** - Fast grep-based search (requires `rg` installed)
- **ag** - Silver Searcher (requires `ag` installed)

### LLM-Based Agents

Set environment variables to enable:

```bash
# OpenAI
export OPENAI_API_KEY="your-key"
benchmark evaluate --gold-set gold_set.json --agent openai --repo /path/to/repo --output results/

# Anthropic Claude
export ANTHROPIC_API_KEY="your-key"
benchmark evaluate --gold-set gold_set.json --agent claude --repo /path/to/repo --output results/
```

### Custom Agents (Copilot, Claude Code, etc.)

See **[AGENT_GUIDE.md](AGENT_GUIDE.md)** for detailed instructions and **[examples/](examples/)** for ready-to-use templates:

**Documentation:**
- [AGENT_GUIDE.md](AGENT_GUIDE.md) - Complete guide for evaluating different agents
- [examples/README.md](examples/README.md) - Example implementations and patterns
- [examples/custom_agent_example.py](examples/custom_agent_example.py) - Agent templates
- [examples/evaluate_custom_agent.py](examples/evaluate_custom_agent.py) - Evaluation script

**Quick example for a CLI tool:**

```python
from benchmark.agents.cli_agent import CLIAgent

class MyToolAgent(CLIAgent):
    def __init__(self):
        super().__init__(
            command_template='my-tool search "{query}" --repo {repo}',
            output_parser=lambda output: output.strip().split('\n'),
            name="MyTool"
        )
```

**Quick example for an API service:**

```python
from benchmark.agents.api_agent import APIAgent

class MyAPIAgent(APIAgent):
    def __init__(self):
        super().__init__(
            api_url="https://api.myservice.com/search",
            api_key=os.getenv("MY_API_KEY"),
            name="MyAPI"
        )
```

## Requirements

- Python 3.8+
- Git repository for dataset generation

## License

MIT
