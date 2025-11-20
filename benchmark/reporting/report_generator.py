"""Report generation and export functionality for benchmark results."""

import json
import csv
import os
from typing import Dict, Optional
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.figure

from benchmark.models import EvaluationResults, AggregateMetrics, TestResult
from benchmark.metrics.calculator import MetricsCalculator


class ReportGenerator:
    """Generates reports and visualizations from evaluation results."""
    
    def __init__(self, evaluation_results: EvaluationResults, metrics: AggregateMetrics):
        """Initialize the report generator.
        
        Args:
            evaluation_results: Complete evaluation results for an agent
            metrics: Aggregate metrics computed from the results
        """
        self.results = evaluation_results
        self.metrics = metrics
        self.calculator = MetricsCalculator()
    
    def export_json(self, output_path: str) -> None:
        """Export detailed results in JSON format.
        
        Args:
            output_path: Path to output JSON file
        """
        # Calculate F1 scores for each result
        detailed_results = []
        for result in self.results.results:
            f1_score = self.calculator.calculate_f1_score(
                set(result.retrieved_files),
                set(result.ground_truth_files)
            )
            
            detailed_results.append({
                "test_case_id": result.test_case_id,
                "retrieved_files": result.retrieved_files,
                "ground_truth_files": result.ground_truth_files,
                "f1_score": round(f1_score, 4),
                "latency_ms": round(result.latency_ms, 2)
            })
        
        output_data = {
            "agent_name": self.results.agent_name,
            "timestamp": self.results.timestamp,
            "aggregate_metrics": {
                "mean_f1": round(self.metrics.mean_f1, 4),
                "median_f1": round(self.metrics.median_f1, 4),
                "std_f1": round(self.metrics.std_f1, 4),
                "p50_latency_ms": round(self.metrics.p50_latency, 2),
                "p90_latency_ms": round(self.metrics.p90_latency, 2),
                "p99_latency_ms": round(self.metrics.p99_latency, 2)
            },
            "total_test_cases": len(self.results.results),
            "results": detailed_results
        }
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    def export_csv(self, output_path: str) -> None:
        """Export results in CSV format for analysis.
        
        Args:
            output_path: Path to output CSV file
        """
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write header
            writer.writerow([
                'test_case_id',
                'agent_name',
                'retrieved_files',
                'ground_truth_files',
                'f1_score',
                'latency_ms'
            ])
            
            # Write data rows
            for result in self.results.results:
                f1_score = self.calculator.calculate_f1_score(
                    set(result.retrieved_files),
                    set(result.ground_truth_files)
                )
                
                writer.writerow([
                    result.test_case_id,
                    self.results.agent_name,
                    '|'.join(result.retrieved_files),  # Join with pipe separator
                    '|'.join(result.ground_truth_files),
                    round(f1_score, 4),
                    round(result.latency_ms, 2)
                ])
    
    def export_markdown(self, output_path: str) -> None:
        """Export human-readable summary in Markdown format.
        
        Args:
            output_path: Path to output Markdown file
        """
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            # Header
            f.write(f"# Benchmark Results: {self.results.agent_name}\n\n")
            f.write(f"**Generated:** {self.results.timestamp}\n\n")
            f.write(f"**Total Test Cases:** {len(self.results.results)}\n\n")
            
            # Aggregate Metrics Section
            f.write("## Aggregate Metrics\n\n")
            f.write("### Accuracy (F1 Score)\n\n")
            f.write("| Metric | Value |\n")
            f.write("|--------|-------|\n")
            f.write(f"| Mean F1 | {self.metrics.mean_f1:.4f} |\n")
            f.write(f"| Median F1 | {self.metrics.median_f1:.4f} |\n")
            f.write(f"| Std Dev F1 | {self.metrics.std_f1:.4f} |\n\n")
            
            f.write("### Latency (milliseconds)\n\n")
            f.write("| Percentile | Latency (ms) |\n")
            f.write("|------------|-------------|\n")
            f.write(f"| p50 (Median) | {self.metrics.p50_latency:.2f} |\n")
            f.write(f"| p90 | {self.metrics.p90_latency:.2f} |\n")
            f.write(f"| p99 | {self.metrics.p99_latency:.2f} |\n\n")
            
            # Methodology Section
            f.write("## Methodology\n\n")
            f.write("### Evaluation Process\n\n")
            f.write("1. **Test Case Execution**: Each test case query was executed against the retrieval agent\n")
            f.write("2. **Timing**: Latency measured from query submission to complete result retrieval\n")
            f.write("3. **Multiple Runs**: Each query executed multiple times; median latency reported\n")
            f.write("4. **Randomization**: Test cases executed in random order to prevent bias\n\n")
            
            f.write("### Metrics Calculation\n\n")
            f.write("**F1 Score**: Harmonic mean of precision and recall\n")
            f.write("- Precision = (Correctly Retrieved Files) / (Total Retrieved Files)\n")
            f.write("- Recall = (Correctly Retrieved Files) / (Total Ground Truth Files)\n")
            f.write("- F1 = 2 × (Precision × Recall) / (Precision + Recall)\n\n")
            
            f.write("**Latency Percentiles**:\n")
            f.write("- p50: 50% of queries completed within this time\n")
            f.write("- p90: 90% of queries completed within this time\n")
            f.write("- p99: 99% of queries completed within this time\n\n")
            
            # Sample Results Section
            f.write("## Sample Results\n\n")
            f.write("| Test Case ID | F1 Score | Latency (ms) | Retrieved | Ground Truth |\n")
            f.write("|--------------|----------|--------------|-----------|-------------|\n")
            
            # Show first 10 results as samples
            for result in self.results.results[:10]:
                f1_score = self.calculator.calculate_f1_score(
                    set(result.retrieved_files),
                    set(result.ground_truth_files)
                )
                
                f.write(f"| {result.test_case_id} | {f1_score:.4f} | {result.latency_ms:.2f} | "
                       f"{len(result.retrieved_files)} | {len(result.ground_truth_files)} |\n")
            
            if len(self.results.results) > 10:
                f.write(f"\n*Showing 10 of {len(self.results.results)} total results*\n")
    
    def generate_visualizations(self, output_dir: str) -> Dict[str, str]:
        """Generate visualization charts and save as PNG files.
        
        Args:
            output_dir: Directory to save visualization files
            
        Returns:
            Dictionary mapping visualization names to file paths
        """
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        visualization_paths = {}
        
        # Generate F1 score histogram
        f1_path = os.path.join(output_dir, "f1_distribution.png")
        self._plot_f1_histogram(f1_path)
        visualization_paths["f1_distribution"] = f1_path
        
        # Generate latency distribution histogram
        latency_path = os.path.join(output_dir, "latency_distribution.png")
        self._plot_latency_histogram(latency_path)
        visualization_paths["latency_distribution"] = latency_path
        
        # Generate accuracy vs latency scatter plot
        scatter_path = os.path.join(output_dir, "accuracy_vs_latency.png")
        self._plot_accuracy_vs_latency(scatter_path)
        visualization_paths["accuracy_vs_latency"] = scatter_path
        
        return visualization_paths
    
    def _plot_f1_histogram(self, output_path: str) -> None:
        """Create F1 score distribution histogram.
        
        Args:
            output_path: Path to save the histogram PNG
        """
        # Calculate F1 scores
        f1_scores = [
            self.calculator.calculate_f1_score(
                set(result.retrieved_files),
                set(result.ground_truth_files)
            )
            for result in self.results.results
        ]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Plot histogram
        ax.hist(f1_scores, bins=20, edgecolor='black', alpha=0.7, color='steelblue')
        
        # Add mean line
        mean_f1 = self.metrics.mean_f1
        ax.axvline(mean_f1, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_f1:.4f}')
        
        # Labels and title
        ax.set_xlabel('F1 Score', fontsize=12)
        ax.set_ylabel('Frequency', fontsize=12)
        ax.set_title(f'F1 Score Distribution - {self.results.agent_name}', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Save figure
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
    
    def _plot_latency_histogram(self, output_path: str) -> None:
        """Create latency distribution histogram.
        
        Args:
            output_path: Path to save the histogram PNG
        """
        # Extract latencies
        latencies = [result.latency_ms for result in self.results.results]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Plot histogram
        ax.hist(latencies, bins=20, edgecolor='black', alpha=0.7, color='forestgreen')
        
        # Add percentile lines
        ax.axvline(self.metrics.p50_latency, color='blue', linestyle='--', linewidth=2, 
                  label=f'p50: {self.metrics.p50_latency:.2f}ms')
        ax.axvline(self.metrics.p90_latency, color='orange', linestyle='--', linewidth=2,
                  label=f'p90: {self.metrics.p90_latency:.2f}ms')
        ax.axvline(self.metrics.p99_latency, color='red', linestyle='--', linewidth=2,
                  label=f'p99: {self.metrics.p99_latency:.2f}ms')
        
        # Labels and title
        ax.set_xlabel('Latency (ms)', fontsize=12)
        ax.set_ylabel('Frequency', fontsize=12)
        ax.set_title(f'Latency Distribution - {self.results.agent_name}', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Save figure
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
    
    def _plot_accuracy_vs_latency(self, output_path: str) -> None:
        """Create accuracy vs latency scatter plot.
        
        Args:
            output_path: Path to save the scatter plot PNG
        """
        # Calculate F1 scores and extract latencies
        f1_scores = []
        latencies = []
        
        for result in self.results.results:
            f1_score = self.calculator.calculate_f1_score(
                set(result.retrieved_files),
                set(result.ground_truth_files)
            )
            f1_scores.append(f1_score)
            latencies.append(result.latency_ms)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Plot scatter
        scatter = ax.scatter(latencies, f1_scores, alpha=0.6, s=50, c='purple', edgecolors='black', linewidth=0.5)
        
        # Add reference lines
        ax.axhline(self.metrics.mean_f1, color='red', linestyle='--', linewidth=1, 
                  alpha=0.5, label=f'Mean F1: {self.metrics.mean_f1:.4f}')
        ax.axvline(self.metrics.p50_latency, color='blue', linestyle='--', linewidth=1,
                  alpha=0.5, label=f'Median Latency: {self.metrics.p50_latency:.2f}ms')
        
        # Labels and title
        ax.set_xlabel('Latency (ms)', fontsize=12)
        ax.set_ylabel('F1 Score', fontsize=12)
        ax.set_title(f'Accuracy vs Latency - {self.results.agent_name}', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Set y-axis limits for better visualization
        ax.set_ylim(-0.05, 1.05)
        
        # Save figure
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
