"""Command-line interface for the Code Search Benchmark System."""

import click
import json
import os
from pathlib import Path
from typing import Optional

from benchmark.dataset.dataset_generator import DatasetGenerator
from benchmark.models import FilterConfig, GoldSet, TestCase
from benchmark.evaluation.engine import EvaluationEngine
from benchmark.metrics.calculator import MetricsCalculator
from benchmark.reporting.report_generator import ReportGenerator
from benchmark.config import load_config, create_default_config


@click.group()
@click.version_option(version="0.1.0")
def main():
    """Code Search Benchmark System - Evaluate code retrieval agents using Git history."""
    pass


@main.command()
@click.option(
    "--repo",
    required=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Path to the Git repository to analyze"
)
@click.option(
    "--output",
    required=True,
    type=click.Path(),
    help="Output path for the generated gold set JSON file"
)
@click.option(
    "--config",
    type=click.Path(exists=True),
    help="Path to YAML configuration file (optional)"
)
@click.option(
    "--min-files",
    type=int,
    default=2,
    help="Minimum number of files in a commit to include (default: 2)"
)
@click.option(
    "--max-files",
    type=int,
    default=20,
    help="Maximum number of files in a commit to include (default: 20)"
)
@click.option(
    "--exclude-pattern",
    multiple=True,
    help="File patterns to exclude (can be specified multiple times)"
)
def generate(
    repo: str,
    output: str,
    config: Optional[str],
    min_files: int,
    max_files: int,
    exclude_pattern: tuple
):
    """Generate a gold set dataset from Git repository history.
    
    Example:
        benchmark generate --repo /path/to/repo --output gold_set.json
    """
    click.echo(f"Generating gold set from repository: {repo}")
    
    # Load configuration
    filter_config = _load_filter_config(config, min_files, max_files, exclude_pattern)
    
    # Validate repository
    if not os.path.exists(os.path.join(repo, ".git")):
        click.echo(f"Error: {repo} is not a valid Git repository", err=True)
        raise click.Abort()
    
    try:
        # Generate dataset
        generator = DatasetGenerator(repo, filter_config)
        gold_set = generator.generate_gold_set()
        
        # Save to file
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(_serialize_gold_set(gold_set), f, indent=2)
        
        click.echo(f"✓ Generated {len(gold_set.test_cases)} test cases")
        click.echo(f"✓ Saved gold set to: {output}")
        
    except Exception as e:
        click.echo(f"Error generating gold set: {e}", err=True)
        raise click.Abort()


@main.command()
@click.option(
    "--output",
    default="benchmark_config.yaml",
    type=click.Path(),
    help="Output path for the configuration file (default: benchmark_config.yaml)"
)
def init_config(output: str):
    """Create a default configuration file template.
    
    Example:
        benchmark init-config --output my_config.yaml
    """
    try:
        create_default_config(output)
        click.echo(f"✓ Created default configuration file: {output}")
        click.echo("Edit this file to customize your benchmark settings.")
    except Exception as e:
        click.echo(f"Error creating config file: {e}", err=True)
        raise click.Abort()


@main.command()
@click.option(
    "--gold-set",
    required=True,
    type=click.Path(exists=True),
    help="Path to the gold set JSON file"
)
@click.option(
    "--agent",
    required=True,
    help="Name of the retrieval agent to evaluate (e.g., 'keyword')"
)
@click.option(
    "--repo",
    required=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Path to the repository for the agent to search"
)
@click.option(
    "--output",
    required=True,
    type=click.Path(),
    help="Output directory for evaluation results"
)
@click.option(
    "--num-runs",
    type=int,
    default=3,
    help="Number of times to run each query for latency measurement (default: 3)"
)
@click.option(
    "--timeout",
    type=int,
    default=30,
    help="Timeout in seconds for each query (default: 30)"
)
def evaluate(
    gold_set: str,
    agent: str,
    repo: str,
    output: str,
    num_runs: int,
    timeout: int
):
    """Run evaluation on a retrieval agent using a gold set.
    
    Example:
        benchmark evaluate --gold-set gold_set.json --agent keyword --repo /path/to/repo --output results/
    """
    click.echo(f"Loading gold set from: {gold_set}")
    
    try:
        # Load gold set
        with open(gold_set, 'r') as f:
            gold_set_data = json.load(f)
        gold_set_obj = _deserialize_gold_set(gold_set_data)
        
        click.echo(f"Loaded {len(gold_set_obj.test_cases)} test cases")
        
        # Load agent
        retrieval_agent = _load_agent(agent, repo)
        click.echo(f"Initialized agent: {agent}")
        
        # Run evaluation
        click.echo(f"Running evaluation (num_runs={num_runs}, timeout={timeout}s)...")
        engine = EvaluationEngine(gold_set_obj, retrieval_agent)
        eval_results = engine.run_evaluation(num_runs=num_runs, timeout=timeout)
        
        # Calculate metrics
        calculator = MetricsCalculator()
        aggregate_metrics = calculator.aggregate_metrics(eval_results.results)
        
        # Generate reports
        output_dir = Path(output)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        report_gen = ReportGenerator(eval_results, aggregate_metrics)
        report_gen.export_json(str(output_dir / "results.json"))
        report_gen.export_csv(str(output_dir / "results.csv"))
        report_gen.export_markdown(str(output_dir / "report.md"))
        report_gen.generate_visualizations(str(output_dir))
        
        # Print summary
        click.echo("\n" + "="*50)
        click.echo("EVALUATION SUMMARY")
        click.echo("="*50)
        click.echo(f"Agent: {agent}")
        click.echo(f"Test Cases: {len(eval_results.results)}")
        click.echo(f"\nAccuracy Metrics:")
        click.echo(f"  Mean F1:   {aggregate_metrics.mean_f1:.3f}")
        click.echo(f"  Median F1: {aggregate_metrics.median_f1:.3f}")
        click.echo(f"  Std Dev:   {aggregate_metrics.std_f1:.3f}")
        click.echo(f"\nLatency Metrics (ms):")
        click.echo(f"  p50: {aggregate_metrics.p50_latency:.2f}")
        click.echo(f"  p90: {aggregate_metrics.p90_latency:.2f}")
        click.echo(f"  p99: {aggregate_metrics.p99_latency:.2f}")
        click.echo(f"\n✓ Results saved to: {output}")
        
    except Exception as e:
        click.echo(f"Error during evaluation: {e}", err=True)
        raise click.Abort()


@main.command()
@click.option(
    "--gold-set",
    required=True,
    type=click.Path(exists=True),
    help="Path to the gold set JSON file"
)
@click.option(
    "--agents",
    required=True,
    help="Comma-separated list of agent names to compare (e.g., 'keyword,semantic')"
)
@click.option(
    "--repo",
    required=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    help="Path to the repository for agents to search"
)
@click.option(
    "--output",
    required=True,
    type=click.Path(),
    help="Output path for comparison report"
)
@click.option(
    "--num-runs",
    type=int,
    default=3,
    help="Number of times to run each query (default: 3)"
)
def compare(
    gold_set: str,
    agents: str,
    repo: str,
    output: str,
    num_runs: int
):
    """Compare multiple retrieval agents side-by-side.
    
    Example:
        benchmark compare --gold-set gold_set.json --agents keyword,semantic --repo /path/to/repo --output comparison.md
    """
    agent_names = [a.strip() for a in agents.split(",")]
    click.echo(f"Comparing {len(agent_names)} agents: {', '.join(agent_names)}")
    
    try:
        # Load gold set
        with open(gold_set, 'r') as f:
            gold_set_data = json.load(f)
        gold_set_obj = _deserialize_gold_set(gold_set_data)
        
        click.echo(f"Loaded {len(gold_set_obj.test_cases)} test cases")
        
        # Evaluate each agent
        all_results = []
        all_metrics = []
        
        for agent_name in agent_names:
            click.echo(f"\nEvaluating agent: {agent_name}")
            
            # Load agent
            retrieval_agent = _load_agent(agent_name, repo)
            
            # Run evaluation
            engine = EvaluationEngine(gold_set_obj, retrieval_agent)
            eval_results = engine.run_evaluation(num_runs=num_runs)
            
            # Calculate metrics
            calculator = MetricsCalculator()
            aggregate_metrics = calculator.aggregate_metrics(eval_results.results)
            
            all_results.append(eval_results)
            all_metrics.append((agent_name, aggregate_metrics))
            
            click.echo(f"  Mean F1: {aggregate_metrics.mean_f1:.3f}, p50 Latency: {aggregate_metrics.p50_latency:.2f}ms")
        
        # Generate comparison report
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        _generate_comparison_report(output_path, all_metrics, gold_set_obj)
        
        click.echo(f"\n✓ Comparison report saved to: {output}")
        
    except Exception as e:
        click.echo(f"Error during comparison: {e}", err=True)
        raise click.Abort()


# Helper functions

def _load_filter_config(
    config_path: Optional[str],
    min_files: int,
    max_files: int,
    exclude_patterns: tuple
) -> FilterConfig:
    """Load filter configuration from file or CLI arguments."""
    if config_path:
        try:
            config = load_config(config_path)
            click.echo(f"Loaded configuration from: {config_path}")
            return config.dataset
        except Exception as e:
            click.echo(f"Warning: Failed to load config file: {e}", err=True)
            click.echo("Falling back to CLI arguments")
    
    # Use CLI arguments
    patterns = list(exclude_patterns) if exclude_patterns else [
        "*.md", "*.json", "test_*", "docs/*"
    ]
    
    return FilterConfig(
        exclude_patterns=patterns,
        min_files=min_files,
        max_files=max_files,
        include_merge_commits=False
    )


def _load_agent(agent_name: str, repo_path: str):
    """Load and initialize a retrieval agent by name."""
    from benchmark.agents.keyword_search import KeywordSearchAgent
    from benchmark.agents.cli_agent import RipgrepAgent, SilverSearcherAgent
    
    # Agent registry
    agents = {
        "keyword": KeywordSearchAgent,
        "ripgrep": RipgrepAgent,
        "ag": SilverSearcherAgent,
    }
    
    # Try to load optional agents
    try:
        from benchmark.agents.llm_agent import OpenAIAgent, AnthropicAgent
        
        # Add LLM agents if API keys are available
        if os.getenv("OPENAI_API_KEY"):
            agents["openai"] = lambda: OpenAIAgent(
                api_key=os.getenv("OPENAI_API_KEY"),
                model=os.getenv("OPENAI_MODEL", "gpt-4")
            )
        
        if os.getenv("ANTHROPIC_API_KEY"):
            agents["claude"] = lambda: AnthropicAgent(
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                model=os.getenv("ANTHROPIC_MODEL", "claude-3-opus-20240229")
            )
    except ImportError:
        pass
    
    if agent_name not in agents:
        available = ", ".join(agents.keys())
        raise ValueError(f"Unknown agent '{agent_name}'. Available agents: {available}")
    
    agent_class = agents[agent_name]
    agent = agent_class() if callable(agent_class) else agent_class
    agent.initialize(repo_path)
    
    return agent


def _serialize_gold_set(gold_set: GoldSet) -> dict:
    """Convert GoldSet to JSON-serializable dict."""
    return {
        "test_cases": [
            {
                "id": tc.id,
                "commit_hash": tc.commit_hash,
                "query": tc.query,
                "ground_truth_files": tc.ground_truth_files,
                "complexity": tc.complexity.value,
                "timestamp": tc.timestamp
            }
            for tc in gold_set.test_cases
        ],
        "metadata": gold_set.metadata
    }


def _deserialize_gold_set(data: dict) -> GoldSet:
    """Convert JSON dict to GoldSet object."""
    from benchmark.models import ComplexityLevel
    
    test_cases = [
        TestCase(
            id=tc["id"],
            commit_hash=tc["commit_hash"],
            query=tc["query"],
            ground_truth_files=tc["ground_truth_files"],
            complexity=ComplexityLevel(tc["complexity"]),
            timestamp=tc["timestamp"]
        )
        for tc in data["test_cases"]
    ]
    
    return GoldSet(
        test_cases=test_cases,
        metadata=data["metadata"]
    )


def _generate_comparison_report(output_path: Path, metrics_list, gold_set):
    """Generate a markdown comparison report."""
    with open(output_path, 'w') as f:
        f.write("# Agent Comparison Report\n\n")
        f.write(f"**Test Cases:** {len(gold_set.test_cases)}\n\n")
        f.write("## Summary\n\n")
        f.write("| Agent | Mean F1 | Median F1 | Std Dev | p50 Latency (ms) | p90 Latency (ms) | p99 Latency (ms) |\n")
        f.write("|-------|---------|-----------|---------|------------------|------------------|------------------|\n")
        
        for agent_name, metrics in metrics_list:
            f.write(f"| {agent_name} | {metrics.mean_f1:.3f} | {metrics.median_f1:.3f} | "
                   f"{metrics.std_f1:.3f} | {metrics.p50_latency:.2f} | "
                   f"{metrics.p90_latency:.2f} | {metrics.p99_latency:.2f} |\n")
        
        f.write("\n## Analysis\n\n")
        f.write("This report compares multiple retrieval agents on the same gold set.\n")
        f.write("Higher F1 scores indicate better accuracy, while lower latency indicates faster performance.\n")


if __name__ == "__main__":
    main()
