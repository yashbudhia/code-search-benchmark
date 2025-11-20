"""Example: Automated Greb MCP evaluation.

This script provides a template for automated evaluation of Greb MCP.
Customize the _call_greb_mcp() method based on your Greb setup.

Usage:
    python examples/evaluate_greb_automated.py
"""

import json
import sys
import subprocess
from pathlib import Path
from typing import List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from benchmark.evaluation.engine import EvaluationEngine
from benchmark.metrics.calculator import MetricsCalculator
from benchmark.reporting.report_generator import ReportGenerator
from benchmark.models import GoldSet, TestCase, ComplexityLevel
from benchmark.agents.mcp_agent import GrebMCPAgent


class AutomatedGrebAgent(GrebMCPAgent):
    """Automated Greb agent with customizable MCP interface."""
    
    def __init__(self, greb_command: str = None, greb_api_url: str = None):
        """Initialize automated Greb agent.
        
        Args:
            greb_command: CLI command template (e.g., "greb search '{query}' --repo {repo}")
            greb_api_url: API URL if Greb exposes HTTP interface
        """
        super().__init__()
        self.greb_command = greb_command
        self.greb_api_url = greb_api_url
        self.name = "Greb-Automated"
    
    def _call_greb_mcp(self, query: str) -> List[str]:
        """Call Greb MCP tool automatically.
        
        Customize this method based on your Greb setup.
        """
        
        # Method 1: CLI Interface
        if self.greb_command:
            return self._call_via_cli(query)
        
        # Method 2: HTTP API
        if self.greb_api_url:
            return self._call_via_api(query)
        
        # Method 3: Direct MCP (customize this)
        return self._call_via_mcp(query)
    
    def _call_via_cli(self, query: str) -> List[str]:
        """Call Greb via CLI command.
        
        Example command templates:
        - "greb search '{query}' --repo {repo}"
        - "greb-cli --query '{query}' --path {repo} --format json"
        """
        try:
            # Build command
            command = self.greb_command.format(
                query=query,
                repo=self.repo_path
            )
            
            print(f"  Executing: {command}")
            
            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                print(f"  ⚠️  Command failed: {result.stderr}")
                return []
            
            # Parse output (customize based on your output format)
            output = result.stdout.strip()
            
            # If JSON output
            if output.startswith('{') or output.startswith('['):
                data = json.loads(output)
                if isinstance(data, list):
                    return data
                return data.get('files', [])
            
            # If line-separated output
            files = [line.strip() for line in output.split('\n') if line.strip()]
            return files
            
        except subprocess.TimeoutExpired:
            print(f"  ⚠️  Command timed out")
            return []
        except Exception as e:
            print(f"  ⚠️  Error: {e}")
            return []
    
    def _call_via_api(self, query: str) -> List[str]:
        """Call Greb via HTTP API.
        
        Example API endpoints:
        - POST http://localhost:8080/search
        - POST http://localhost:3000/api/greb/search
        """
        try:
            import requests
            
            print(f"  Calling API: {self.greb_api_url}")
            
            response = requests.post(
                self.greb_api_url,
                json={
                    "query": query,
                    "repo_path": self.repo_path,
                    "max_results": 20
                },
                timeout=30
            )
            
            response.raise_for_status()
            data = response.json()
            
            # Customize based on your API response format
            if isinstance(data, list):
                return data
            return data.get('files', [])
            
        except Exception as e:
            print(f"  ⚠️  API Error: {e}")
            return []
    
    def _call_via_mcp(self, query: str) -> List[str]:
        """Call Greb via MCP protocol.
        
        Customize this based on how you access MCP in your environment.
        """
        # TODO: Implement MCP call
        # This depends on your MCP setup
        
        # Example: If you have a Python MCP client
        # from mcp_client import MCPClient
        # client = MCPClient()
        # result = client.call_tool("greb_search", {
        #     "query": query,
        #     "repo": self.repo_path
        # })
        # return result.get("files", [])
        
        print(f"  ⚠️  MCP interface not implemented")
        return []


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
    """Main evaluation function."""
    
    # ========================================
    # CONFIGURATION - CUSTOMIZE THIS
    # ========================================
    
    GOLD_SET_PATH = "test_gold_set.json"
    REPO_PATH = "test-repo"
    OUTPUT_DIR = "results/greb_automated"
    
    # Choose your Greb interface method:
    
    # Option 1: CLI Command
    GREB_CLI_COMMAND = "greb search '{query}' --repo {repo} --format json"
    
    # Option 2: HTTP API
    GREB_API_URL = None  # e.g., "http://localhost:8080/search"
    
    # ========================================
    
    print("="*60)
    print("Automated Greb MCP Evaluation")
    print("="*60)
    
    # Load gold set
    print(f"\n📂 Loading gold set...")
    try:
        gold_set = load_gold_set(GOLD_SET_PATH)
        print(f"✓ Loaded {len(gold_set.test_cases)} test cases")
    except FileNotFoundError:
        print(f"❌ Error: Gold set not found at {GOLD_SET_PATH}")
        print("\nGenerate a gold set first:")
        print(f"  benchmark generate --repo {REPO_PATH} --output {GOLD_SET_PATH} --max-commits 50")
        return
    
    # Initialize agent
    print(f"\n🤖 Initializing Greb agent...")
    agent = AutomatedGrebAgent(
        greb_command=GREB_CLI_COMMAND,
        greb_api_url=GREB_API_URL
    )
    agent.initialize(REPO_PATH)
    print(f"✓ Agent initialized: {agent.name}")
    
    # Run evaluation
    print(f"\n🚀 Running evaluation...")
    print(f"   Test cases: {len(gold_set.test_cases)}")
    print(f"   Repository: {REPO_PATH}\n")
    
    engine = EvaluationEngine(
        gold_set,
        agent,
        num_runs=1,
        timeout_seconds=60,
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
    print("="*60)


if __name__ == "__main__":
    main()
