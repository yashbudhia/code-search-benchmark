"""Evaluation engine for executing benchmark tests and measuring performance."""

import time
import random
import statistics
import logging
import os
from typing import List, Optional
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

from benchmark.models import (
    GoldSet,
    TestCase,
    TestResult,
    EvaluationResults,
    RetrievalResult
)
from benchmark.agents.base import RetrievalAgent, validate_agent


logger = logging.getLogger(__name__)


class EvaluationEngine:
    """Orchestrates test execution and measures retrieval performance."""
    
    def __init__(
        self,
        gold_set: GoldSet,
        agent: RetrievalAgent,
        num_runs: int = 3,
        timeout_seconds: int = 30,
        repo_path: Optional[str] = None
    ):
        """Initialize the evaluation engine.
        
        Args:
            gold_set: Collection of test cases to evaluate
            agent: Retrieval agent to test
            num_runs: Number of times to execute each query (default: 3)
            timeout_seconds: Maximum time per query in seconds (default: 30)
            repo_path: Path to repository for file validation
        """
        validate_agent(agent)
        
        self.gold_set = gold_set
        self.agent = agent
        self.num_runs = max(1, num_runs)
        self.timeout_seconds = timeout_seconds
        self.repo_path = repo_path
        self.results: List[TestResult] = []
    
    def run_evaluation(self, randomize: bool = True) -> EvaluationResults:
        """Execute all test cases with timing and error handling.
        
        Args:
            randomize: Whether to randomize test case order (default: True)
            
        Returns:
            EvaluationResults containing all test results and metadata
        """
        logger.info(f"Starting evaluation with agent: {self.agent.name}")
        logger.info(f"Test cases: {len(self.gold_set.test_cases)}, Runs per query: {self.num_runs}")
        
        test_cases = self._randomize_order(self.gold_set.test_cases) if randomize else self.gold_set.test_cases
        
        for idx, test_case in enumerate(test_cases, 1):
            logger.info(f"Evaluating test case {idx}/{len(test_cases)}: {test_case.id}")
            
            # Reset agent state between test cases
            try:
                self.agent.reset()
            except Exception as e:
                logger.error(f"Error resetting agent for test case {test_case.id}: {e}")
            
            # Execute query multiple times and collect latencies
            latencies = []
            retrieved_files = []
            error_occurred = False
            
            for run in range(self.num_runs):
                try:
                    result = self._execute_query_with_timeout(test_case.query)
                    
                    if result is None:
                        # Timeout occurred
                        logger.warning(f"Timeout on test case {test_case.id}, run {run + 1}")
                        error_occurred = True
                        break
                    
                    latency_ms, retrieval_result = result
                    latencies.append(latency_ms)
                    
                    # Use results from first successful run
                    if run == 0:
                        retrieved_files = self._validate_and_normalize_files(
                            retrieval_result.files,
                            test_case.id
                        )
                
                except Exception as e:
                    logger.error(f"Error executing query for test case {test_case.id}, run {run + 1}: {e}")
                    error_occurred = True
                    break
            
            # Record result
            if error_occurred or not latencies:
                # Mark as failed with empty results
                median_latency = -1.0  # Negative indicates error/timeout
                retrieved_files = []
                logger.warning(f"Test case {test_case.id} failed or timed out")
            else:
                median_latency = statistics.median(latencies)
            
            test_result = TestResult(
                test_case_id=test_case.id,
                retrieved_files=retrieved_files,
                ground_truth_files=test_case.ground_truth_files,
                latency_ms=median_latency
            )
            
            self.results.append(test_result)
        
        logger.info(f"Evaluation complete. Total results: {len(self.results)}")
        
        return EvaluationResults(
            results=self.results,
            agent_name=self.agent.name,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
    
    def _execute_query_with_timeout(self, query: str) -> Optional[tuple]:
        """Execute a single query with timeout protection.
        
        Args:
            query: Search query to execute
            
        Returns:
            Tuple of (latency_ms, RetrievalResult) or None if timeout
        """
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(self._execute_query, query)
            
            try:
                result = future.result(timeout=self.timeout_seconds)
                return result
            except FuturesTimeoutError:
                logger.warning(f"Query timed out after {self.timeout_seconds}s: {query[:50]}...")
                return None
            except Exception as e:
                logger.error(f"Unexpected error during query execution: {e}")
                raise
    
    def _execute_query(self, query: str) -> tuple:
        """Execute a single query and measure latency.
        
        Args:
            query: Search query to execute
            
        Returns:
            Tuple of (latency_ms, RetrievalResult)
        """
        start_time = time.perf_counter_ns()
        retrieval_result = self.agent.retrieve(query)
        end_time = time.perf_counter_ns()
        
        latency_ms = (end_time - start_time) / 1_000_000  # Convert nanoseconds to milliseconds
        
        return latency_ms, retrieval_result
    
    def _validate_and_normalize_files(self, files: List[str], test_case_id: str) -> List[str]:
        """Validate and normalize file paths from agent response.
        
        Args:
            files: List of file paths from agent
            test_case_id: ID of current test case for logging
            
        Returns:
            List of validated and normalized file paths
        """
        if not files:
            return []
        
        validated_files = []
        
        for file_path in files:
            # Normalize path separators
            normalized_path = file_path.replace('\\', '/')
            
            # Remove leading slashes
            normalized_path = normalized_path.lstrip('/')
            
            # Validate file exists if repo_path is provided
            if self.repo_path:
                full_path = os.path.join(self.repo_path, normalized_path)
                if not os.path.exists(full_path):
                    logger.debug(f"File does not exist: {normalized_path} (test case: {test_case_id})")
                    # Still include it - might be from a different commit
            
            validated_files.append(normalized_path)
        
        return validated_files
    
    def _randomize_order(self, test_cases: List[TestCase]) -> List[TestCase]:
        """Shuffle test cases to prevent order bias.
        
        Args:
            test_cases: Original list of test cases
            
        Returns:
            Shuffled copy of test cases
        """
        shuffled = test_cases.copy()
        random.shuffle(shuffled)
        return shuffled
