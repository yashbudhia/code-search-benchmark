"""Dataset generation pipeline for creating benchmark test cases from Git history."""

import hashlib
import json
from datetime import datetime
from typing import List
from pathlib import Path
from git import Repo, Commit

from benchmark.models import FilterConfig, GoldSet, TestCase, ComplexityLevel
from benchmark.dataset.commit_analyzer import CommitAnalyzer
from benchmark.dataset.commit_filter import CommitFilter
from benchmark.dataset.query_transformer import QueryTransformer


class DatasetGenerator:
    """Orchestrates the generation of benchmark datasets from Git repositories."""
    
    def __init__(self, repo_path: str, config: FilterConfig):
        """
        Initialize the DatasetGenerator.
        
        Args:
            repo_path: Path to the Git repository
            config: FilterConfig with exclusion patterns and file count limits
        """
        self.repo_path = repo_path
        self.config = config
        
        # Initialize components
        self.analyzer = CommitAnalyzer()
        self.filter = CommitFilter(config, self.analyzer)
        self.transformer = QueryTransformer()
        
        # Load the Git repository
        self.repo = Repo(repo_path)
    
    def generate_gold_set(self) -> GoldSet:
        """
        Generate a complete gold set from the repository.
        
        Orchestrates the full pipeline:
        1. Extract all commits from repository
        2. Filter commits based on configuration
        3. Transform commit messages to queries
        4. Create test cases with metadata
        5. Package into GoldSet with metadata
        
        Returns:
            GoldSet containing all generated test cases and metadata
        """
        # Get all commits from the repository
        all_commits = list(self.repo.iter_commits())
        total_commits = len(all_commits)
        
        # Filter commits based on configuration
        filtered_commits = self.filter_commits(all_commits)
        
        # Generate test cases from filtered commits
        test_cases = []
        for commit in filtered_commits:
            test_case = self._create_test_case(commit)
            if test_case:
                test_cases.append(test_case)
        
        # Create metadata
        repo_name = Path(self.repo_path).name
        metadata = {
            "repository": repo_name,
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "total_commits_analyzed": total_commits,
            "test_cases_generated": len(test_cases)
        }
        
        return GoldSet(test_cases=test_cases, metadata=metadata)
    
    def filter_commits(self, commits: List[Commit]) -> List[Commit]:
        """
        Filter commits using the CommitFilter.
        
        Args:
            commits: List of GitPython Commit objects
            
        Returns:
            Filtered list of commits that meet inclusion criteria
        """
        return self.filter.filter_commits(commits)
    
    def _create_test_case(self, commit: Commit) -> TestCase:
        """
        Create a TestCase from a Git commit.
        
        Args:
            commit: GitPython Commit object
            
        Returns:
            TestCase with generated ID, query, ground truth files, and metadata
        """
        # Generate unique test case ID from commit hash
        test_case_id = self._generate_test_case_id(commit)
        
        # Extract commit metadata
        commit_hash = commit.hexsha
        timestamp = datetime.fromtimestamp(commit.committed_date).isoformat() + "Z"
        
        # Transform commit message to query
        query = self.transformer.commit_message_to_query(commit.message)
        
        # Extract ground truth files
        ground_truth_files = self.analyzer.extract_modified_files(commit)
        
        # Classify complexity
        complexity = self.analyzer.classify_complexity(len(ground_truth_files))
        
        return TestCase(
            id=test_case_id,
            commit_hash=commit_hash,
            query=query,
            ground_truth_files=ground_truth_files,
            complexity=complexity,
            timestamp=timestamp
        )
    
    def _generate_test_case_id(self, commit: Commit) -> str:
        """
        Generate a unique test case ID from commit hash.
        
        Uses first 8 characters of commit SHA for readability.
        
        Args:
            commit: GitPython Commit object
            
        Returns:
            Unique test case ID string
        """
        return commit.hexsha[:8]
    
    def save_gold_set(self, gold_set: GoldSet, output_path: str) -> None:
        """
        Save GoldSet to JSON file with proper formatting.
        
        Args:
            gold_set: GoldSet to save
            output_path: Path to output JSON file
        """
        # Convert GoldSet to dictionary format
        gold_set_dict = {
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
        
        # Ensure output directory exists
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write to JSON file with proper formatting
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(gold_set_dict, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def load_gold_set(input_path: str) -> GoldSet:
        """
        Load GoldSet from JSON file.
        
        Args:
            input_path: Path to input JSON file
            
        Returns:
            GoldSet loaded from file
        """
        with open(input_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert dictionary to GoldSet
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
        
        return GoldSet(test_cases=test_cases, metadata=data["metadata"])
