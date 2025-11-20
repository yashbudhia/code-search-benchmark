"""Metrics calculator for F1 scores and latency statistics."""

import statistics
from typing import List, Set
from benchmark.models import TestResult, AggregateMetrics


class MetricsCalculator:
    """Calculates accuracy and latency metrics for benchmark results."""
    
    def calculate_f1_score(self, retrieved: Set[str], ground_truth: Set[str]) -> float:
        """
        Calculate F1 score from retrieved and ground truth file sets.
        
        Args:
            retrieved: Set of file paths returned by the retrieval agent
            ground_truth: Set of actual relevant file paths
            
        Returns:
            F1 score between 0.0 and 1.0
        """
        # Handle edge case: both sets are empty (perfect match)
        if not retrieved and not ground_truth:
            return 1.0
        
        # Handle edge case: one set is empty (no overlap possible)
        if not retrieved or not ground_truth:
            return 0.0
        
        # Calculate intersection
        correct = retrieved & ground_truth
        
        # Calculate precision: ratio of correct retrievals to total retrievals
        precision = len(correct) / len(retrieved)
        
        # Calculate recall: ratio of correct retrievals to total ground truth
        recall = len(correct) / len(ground_truth)
        
        # Handle edge case: no overlap
        if precision + recall == 0:
            return 0.0
        
        # Calculate F1 score using harmonic mean
        f1 = 2 * (precision * recall) / (precision + recall)
        
        return f1
    
    def calculate_partial_match_score(self, retrieved: str, ground_truth: Set[str]) -> float:
        """
        Calculate partial credit for directory-level matches.
        
        Awards partial credit when a retrieved directory path matches
        the beginning of ground truth file paths.
        
        Args:
            retrieved: A single retrieved path (potentially a directory)
            ground_truth: Set of ground truth file paths
            
        Returns:
            Partial match score (0.5 for partial match, 0.0 for no match)
        """
        # Check if any ground truth file starts with the retrieved path
        for gt_file in ground_truth:
            if gt_file.startswith(retrieved):
                return 0.5  # Partial credit for directory match
        
        return 0.0
    
    def aggregate_metrics(self, results: List[TestResult]) -> AggregateMetrics:
        """
        Compute aggregate statistics across all test results.
        
        Args:
            results: List of TestResult objects from evaluation
            
        Returns:
            AggregateMetrics with summary statistics
        """
        # Calculate F1 scores for all results
        f1_scores = [
            self.calculate_f1_score(
                set(result.retrieved_files),
                set(result.ground_truth_files)
            )
            for result in results
        ]
        
        # Extract latencies
        latencies = [result.latency_ms for result in results]
        
        # Calculate F1 statistics
        mean_f1 = statistics.mean(f1_scores) if f1_scores else 0.0
        median_f1 = statistics.median(f1_scores) if f1_scores else 0.0
        std_f1 = statistics.stdev(f1_scores) if len(f1_scores) > 1 else 0.0
        
        # Calculate latency percentiles
        p50_latency = self._percentile(latencies, 0.50) if latencies else 0.0
        p90_latency = self._percentile(latencies, 0.90) if latencies else 0.0
        p99_latency = self._percentile(latencies, 0.99) if latencies else 0.0
        
        return AggregateMetrics(
            mean_f1=mean_f1,
            median_f1=median_f1,
            std_f1=std_f1,
            p50_latency=p50_latency,
            p90_latency=p90_latency,
            p99_latency=p99_latency
        )
    
    def _percentile(self, data: List[float], p: float) -> float:
        """
        Calculate the percentile value from a list of numbers.
        
        Args:
            data: List of numeric values
            p: Percentile as a decimal (e.g., 0.90 for 90th percentile)
            
        Returns:
            The value at the specified percentile
        """
        if not data:
            return 0.0
        
        sorted_data = sorted(data)
        index = int(len(sorted_data) * p)
        # Ensure index is within bounds
        index = min(index, len(sorted_data) - 1)
        
        return sorted_data[index]
