"""Example: Evaluate Copilot with Greb MCP.

This script shows how to evaluate GitHub Copilot's code search
using the Greb MCP tool in Kiro.

Prerequisites:
1. Greb MCP server configured in Kiro
2. Gold set generated from a repository
3. Access to the repository being searched

Usage:
    python examples/evaluate_copilot_greb.py
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from benchmark.evaluation.engine import EvaluationEngine
from benchmark.metrics.calculator import MetricsCalculator
from benchmark.reporting.report_generator import ReportGenerator
from benchmark.models import GoldSet, TestCase, ComplexityLevel
from benchmark.agents.mcp_agent import GrebMCPAgent


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


class CopilotGrebAgent(GrebMCPAgent):
    """Custom agent that uses Copilot with Greb MCP.
    
    This implementation shows how to integrate with Greb MCP
    through Kiro's interface.
    """
    
    def __init__(self):
        super().__init__()
        self.name = "Copilot-Greb"
    
    def _call_greb_mcp(self, query: str):
        """Call Greb MCP tool through Kiro.
        
        IMPLEMENTATION OPTIONS:
        
        Option 1: Manual Testing
        -----------------------
        For manual testing, you can:
        1. Run the query in Kiro with Greb MCP
        2. Copy the file paths returned
        3. Return them here
        
        Option 2: Kiro MCP Client (if available)
        ----------------------------------------
        If Kiro provides a Python client for MCP:
        
        from kiro_mcp import MCPClient
        client = MCPClient()
        result = client.call_tool("greb_search", {
            "query": query,
            "repo_path": self.repo_path
        })
        return result.get("files", [])
        
        Option 3: HTTP API (if Greb exposes one)
        ----------------------------------------
        import requests
        response = requests.post(
            "http://localhost:PORT/search",
            json={"query": query, "repo": self.repo_path}
        )
        return response.json().get("files", [])
        
        Option 4: CLI Wrapper
        --------------------
        import subprocess
        result = subprocess.run(
            ["greb", "search", query, "--repo", self.repo_path],
            capture_output=True,
            text=True
        )
        return result.stdout.strip().split('\n')
        """
        
        # TODO: Implement based on your Greb MCP setup
        # For now, this is a placeholder that shows the structure
        
        print(f"\n🔍 Query: {query}")
        print(f"📁 Repository: {self.repo_path}")
        print("\n⚠️  MANUAL STEP REQUIRED:")
        print("1. Run this query in Kiro with Greb MCP")
        print("2. Copy the file paths returned")
        print("3. Enter them below (one per line, empty line to finish):")
        
        files = []
        while True:
            line = input().strip()
            if not line:
                break
            files.append(line)
        
        return files


def main():
    """Main evaluation function."""
    
    # Configuration
    GOLD_SET_PATH = "test_gold_set.json"
    REPO_PATH = "test-repo"
    OUTPUT_DIR = "results/copilot_greb"
    
    print("="*60)
    print("Copilot + Greb MCP Evaluation")
    print("="*60)
    
    # Load gold set
    print(f"\n📂 Loading gold set from: {GOLD_SET_PATH}")
    try:
        gold_set = load_gold_set(GOLD_SET_PATH)
        print(f"✓ Loaded {len(gold_set.test_cases)} test cases")
    except FileNotFoundError:
        print(f"❌ Error: Gold set not found at {GOLD_SET_PATH}")
        print("\nGenerate a gold set first:")
        print(f"  benchmark generate --repo {REPO_PATH} --output {GOLD_SET_PATH} --max-commits 50")
        return
    
    # Initialize agent
    print(f"\n🤖 Initializing Copilot-Greb agent...")
    agent = CopilotGrebAgent()
    agent.initialize(REPO_PATH)
    print(f"✓ Agent initialized: {agent.name}")
    
    # Run evaluation
    print(f"\n🚀 Running evaluation...")
    print(f"   Test cases: {len(gold_set.test_cases)}")
    print(f"   Runs per query: 1")
    print(f"   Repository: {REPO_PATH}")
    
    print("\n" + "="*60)
    print("MANUAL EVALUATION MODE")
    print("="*60)
    print("\nFor each query, you'll need to:")
    print("1. Run the query in Kiro with Greb MCP")
    print("2. Copy the file paths returned")
    print("3. Paste them into the prompt")
    print("\nPress Enter to start...")
    input()
    
    engine = EvaluationEngine(
        gold_set,
        agent,
        num_runs=1,
        timeout_seconds=300,  # 5 minutes per query for manual input
        repo_path=REPO_PATH
    )
    
    eval_results = engine.run_evaluation()
    print(f"\n✓ Completed {len(eval_results.results)} test cases")
    
    # Calculate metrics
    print(f"\n📊 Calculating metrics...")
    calculator = MetricsCalculator()
    metrics = calculator.aggregate_metrics(eval_results.results)
    
    # Generate reports
    print(f"\n📝 Generating reports...")
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(parents=True, exist_ok=True)
    
    report_gen = ReportGenerator(eval_results, metrics)
    report_gen.export_json(str(output_path / "results.json"))
    report_gen.export_csv(str(output_path / "results.csv"))
    report_gen.export_markdown(str(output_path / "report.md"))
    report_gen.generate_visualizations(str(output_path))
    
    # Print summary
    print("\n" + "="*60)
    print("EVALUATION SUMMARY")
    print("="*60)
    print(f"Agent: {agent.name}")
    print(f"Test Cases: {len(eval_results.results)}")
    print(f"\n📈 Accuracy Metrics:")
    print(f"  Mean F1:   {metrics.mean_f1:.3f}")
    print(f"  Median F1: {metrics.median_f1:.3f}")
    print(f"  Std Dev:   {metrics.std_f1:.3f}")
    print(f"\n⏱️  Latency Metrics (ms):")
    print(f"  p50: {metrics.p50_latency:.2f}")
    print(f"  p90: {metrics.p90_latency:.2f}")
    print(f"  p99: {metrics.p99_latency:.2f}")
    print(f"\n✓ Results saved to: {OUTPUT_DIR}")
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
