"""Commit filtering logic for dataset generation."""

import fnmatch
from typing import List
from git import Commit
from benchmark.models import FilterConfig
from benchmark.dataset.commit_analyzer import CommitAnalyzer


class CommitFilter:
    """Filters commits based on configuration rules."""
    
    def __init__(self, config: FilterConfig, analyzer: CommitAnalyzer):
        """
        Initialize the CommitFilter.
        
        Args:
            config: FilterConfig with exclusion patterns and file count limits
            analyzer: CommitAnalyzer instance for extracting file information
        """
        self.config = config
        self.analyzer = analyzer
    
    def should_include_commit(self, commit: Commit) -> bool:
        """
        Determine if a commit should be included in the dataset.
        
        Applies filtering rules:
        - Feature commit detection (excludes merge, formatting, docs-only)
        - File count limits (min_files, max_files)
        - File pattern exclusions (exclude_patterns)
        
        Args:
            commit: GitPython Commit object
            
        Returns:
            True if commit should be included, False otherwise
        """
        # First check if it's a feature commit
        if not self.analyzer.is_feature_commit(commit):
            return False
        
        # Extract modified files
        modified_files = self.analyzer.extract_modified_files(commit)
        
        # Check file count limits
        file_count = len(modified_files)
        if file_count < self.config.min_files or file_count > self.config.max_files:
            return False
        
        # Check if all files match exclusion patterns
        if self._all_files_excluded(modified_files):
            return False
        
        return True
    
    def _all_files_excluded(self, files: List[str]) -> bool:
        """
        Check if all files in the list match exclusion patterns.
        
        Args:
            files: List of file paths
            
        Returns:
            True if all files should be excluded, False otherwise
        """
        if not files:
            return True
        
        # Check each file against exclusion patterns
        for file_path in files:
            if not self._matches_exclusion_pattern(file_path):
                # Found at least one file that doesn't match exclusion patterns
                return False
        
        # All files matched exclusion patterns
        return True
    
    def _matches_exclusion_pattern(self, file_path: str) -> bool:
        """
        Check if a file path matches any exclusion pattern.
        
        Uses glob-style pattern matching:
        - * matches any characters within a path segment
        - ** matches any characters across path segments
        - ? matches a single character
        
        Args:
            file_path: File path to check
            
        Returns:
            True if file matches any exclusion pattern, False otherwise
        """
        # Normalize path separators to forward slashes for consistent matching
        normalized_path = file_path.replace('\\', '/')
        
        for pattern in self.config.exclude_patterns:
            # Normalize pattern as well
            normalized_pattern = pattern.replace('\\', '/')
            
            # Handle directory patterns (ending with /)
            if normalized_pattern.endswith('/'):
                # Check if file is in this directory
                if normalized_path.startswith(normalized_pattern):
                    return True
            # Handle wildcard patterns
            elif '**' in normalized_pattern:
                # Convert ** to match across directories
                regex_pattern = normalized_pattern.replace('**', '*')
                if fnmatch.fnmatch(normalized_path, regex_pattern):
                    return True
            else:
                # Standard glob matching
                if fnmatch.fnmatch(normalized_path, normalized_pattern):
                    return True
                
                # Also check if pattern matches the filename only
                filename = normalized_path.split('/')[-1]
                if fnmatch.fnmatch(filename, normalized_pattern):
                    return True
        
        return False
    
    def filter_commits(self, commits: List[Commit]) -> List[Commit]:
        """
        Filter a list of commits based on configuration rules.
        
        Args:
            commits: List of GitPython Commit objects
            
        Returns:
            Filtered list of commits that meet inclusion criteria
        """
        return [commit for commit in commits if self.should_include_commit(commit)]
