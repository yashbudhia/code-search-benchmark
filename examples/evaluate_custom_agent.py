"""Example: Evaluate a custom agent without modifying the CLI.

This script shows how to evaluate your own custom agent
without needing to modify the benchmark CLI code.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path to import benchmark
sys.path.insert(0, str(Path(__file__).parent.parent))

from benchmark.evaluation.engine import EvaluationEngine
from benchmark.metrics.calculator import MetricsCalculator
from benchmark.reporting.report_generator import ReportGenerator
from benchmark.models import GoldSet, TestCase, ComplexityLevel

# Import your custom agent
# from my_agents import MyCustomAgent


def load_gold_set(gold_set_path: str) -> GoldSet:
    """Load gold set from JSON file."""
    with open(gold_set_path, 'r') as f:
        data = json.load(f)
    
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


def main():
    # Configuration
    GOLD_SET_PATH = "gold_set.json"
    REPO_PATH = "/path/to/your/repo"
    OUTPUT_DIR = "results/custom_agent"
    
    print("Loading gold set...")
    gold_set = load_gold_set(GOLD_SET_PATH)
    print(f"Loaded {len(gold_set.test_cases)} test cases")
    
    # Initialize your custom agent
    print("\nInitializing agent...")
    # agent = MyCustomAgent()
    
    # For this example, use the keyword agent
    from benchmark.agents.keyword_search import KeywordSearchAgent
    agent = KeywordSearchAgent()
    
    agent.initialize(REPO_PATH)
    print(f"Agent initialized: {agent.name}")
    
    # Run evaluation
    print("\nRunning evaluation...")
    engine = EvaluationEngine(gold_set, agent)
    results = engine.run_evaluation(num_runs=3, timeout=30)
    print(f"Completed {len(results.results)} test cases")
    
    # Calculate metrics
    print("\nCalculating metrics...")
    calculator = MetricsCalculator()
    metrics = calculator.aggregate_metrics(results.results)
    
    # Generate reports
    print("\nGenerating reports...")
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)
    
    report_gen = ReportGenerator(results, metrics)
    report_gen.export_json(str(output_path / "results.json"))
    report_gen.export_csv(str(output_path / "results.csv"))
    report_gen.export_markdown(str(output_path / "report.md"))
    report_gen.generate_visualizations(str(output_path))
    
    # Print summary
    print("\n" + "="*50)
    print("EVALUATION SUMMARY")
    print("="*50)
    print(f"Agent: {agent.name}")
    print(f"Test Cases: {len(results.results)}")
    print(f"\nAccuracy Metrics:")
    print(f"  Mean F1:   {metrics.mean_f1:.3f}")
    print(f"  Median F1: {metrics.median_f1:.3f}")
    print(f"  Std Dev:   {metrics.std_f1:.3f}")
    print(f"\nLatency Metrics (ms):")
    print(f"  p50: {metrics.p50_latency:.2f}")
    print(f"  p90: {metrics.p90_latency:.2f}")
    print(f"  p99: {metrics.p99_latency:.2f}")
    print(f"\nResults saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
