"""Core data models for the benchmark system."""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from enum import Enum


class ComplexityLevel(Enum):
    """Classification of test case complexity based on file count."""
    LOW = "low"      # < 2 files
    MEDIUM = "medium"  # 2-20 files
    HIGH = "high"    # > 20 files


@dataclass
class TestCase:
    """Represents a single benchmark test case."""
    id: str
    commit_hash: str
    query: str
    ground_truth_files: List[str]
    complexity: ComplexityLevel
    timestamp: str


@dataclass
class GoldSet:
    """Collection of test cases with metadata."""
    test_cases: List[TestCase]
    metadata: Dict[str, Any]


@dataclass
class TestResult:
    """Results from evaluating a single test case."""
    test_case_id: str
    retrieved_files: List[str]
    ground_truth_files: List[str]
    latency_ms: float


@dataclass
class AggregateMetrics:
    """Summary statistics across all test results."""
    mean_f1: float
    median_f1: float
    std_f1: float
    p50_latency: float
    p90_latency: float
    p99_latency: float


@dataclass
class EvaluationResults:
    """Complete evaluation results for an agent."""
    results: List[TestResult]
    agent_name: str
    timestamp: str


@dataclass
class FilterConfig:
    """Configuration for filtering commits during dataset generation."""
    exclude_patterns: List[str] = field(default_factory=lambda: [
        "*.md", "*.json", "test_*", "docs/*"
    ])
    min_files: int = 2
    max_files: int = 20
    include_merge_commits: bool = False


@dataclass
class RetrievalResult:
    """Result from a retrieval agent query."""
    files: List[str]  # Ranked list of file paths
    scores: List[float] = field(default_factory=list)  # Confidence scores (optional)
    metadata: Dict[str, Any] = field(default_factory=dict)  # Agent-specific info
