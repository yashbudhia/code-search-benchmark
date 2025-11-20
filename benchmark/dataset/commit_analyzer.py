"""Commit analysis and classification for dataset generation."""

import re
from typing import List
from git import Commit
from benchmark.models import ComplexityLevel


class CommitAnalyzer:
    """Analyzes Git commits to identify feature commits and extract metadata."""
    
    def __init__(self):
        """Initialize the CommitAnalyzer."""
        # Patterns that indicate formatting-only or trivial changes
        self.formatting_patterns = [
            r'\bformat\b',
            r'\bformatting\b',
            r'\bwhitespace\b',
            r'\bindent\b',
            r'\bstyle\b',
            r'\btypo\b',
            r'\btypos\b',
            r'\bspelling\b',
            r'\bcomment\b',
            r'\bcomments\b',
        ]
        
        # Patterns that indicate documentation-only changes
        self.doc_patterns = [
            r'\bdoc\b',
            r'\bdocs\b',
            r'\bdocumentation\b',
            r'\breadme\b',
            r'\bchangelog\b',
        ]
    
    def is_feature_commit(self, commit: Commit) -> bool:
        """
        Determine if a commit represents a feature or bug fix.
        
        Excludes:
        - Merge commits
        - Formatting-only commits
        - Documentation-only commits
        
        Args:
            commit: GitPython Commit object
            
        Returns:
            True if this is a feature commit, False otherwise
        """
        # Exclude merge commits (have multiple parents)
        if len(commit.parents) > 1:
            return False
        
        # Get commit message (lowercase for pattern matching)
        message = commit.message.lower().strip()
        
        # Check if it's a formatting-only commit
        for pattern in self.formatting_patterns:
            if re.search(pattern, message):
                # If the message only talks about formatting, exclude it
                # But allow if there are other substantial words
                if len(message.split()) < 10:  # Short messages are likely trivial
                    return False
        
        # Check if it's a documentation-only commit
        for pattern in self.doc_patterns:
            if re.search(pattern, message):
                # Check if files modified are only documentation files
                modified_files = self.extract_modified_files(commit)
                doc_extensions = {'.md', '.txt', '.rst', '.adoc'}
                doc_dirs = {'docs/', 'doc/', 'documentation/'}
                
                all_docs = all(
                    any(f.endswith(ext) for ext in doc_extensions) or
                    any(f.startswith(d) for d in doc_dirs)
                    for f in modified_files
                )
                
                if all_docs and modified_files:
                    return False
        
        return True
    
    def extract_modified_files(self, commit: Commit) -> List[str]:
        """
        Extract list of modified file paths from a commit.
        
        Args:
            commit: GitPython Commit object
            
        Returns:
            List of file paths that were modified in this commit
        """
        modified_files = []
        
        # Handle the case where commit has no parents (initial commit)
        if not commit.parents:
            # For initial commit, get all files in the tree
            for item in commit.tree.traverse():
                if item.type == 'blob':  # It's a file, not a directory
                    modified_files.append(item.path)
        else:
            # Get diff between commit and its first parent
            parent = commit.parents[0]
            diffs = parent.diff(commit)
            
            # Extract file paths from diff
            for diff in diffs:
                # Handle renamed files (a_path is old, b_path is new)
                if diff.renamed_file:
                    modified_files.append(diff.b_path)
                # Handle new files
                elif diff.new_file:
                    modified_files.append(diff.b_path)
                # Handle deleted files
                elif diff.deleted_file:
                    modified_files.append(diff.a_path)
                # Handle modified files
                else:
                    modified_files.append(diff.b_path if diff.b_path else diff.a_path)
        
        return modified_files
    
    def classify_complexity(self, file_count: int) -> ComplexityLevel:
        """
        Classify commit complexity based on number of files modified.
        
        Args:
            file_count: Number of files modified in the commit
            
        Returns:
            ComplexityLevel enum value (LOW, MEDIUM, or HIGH)
        """
        if file_count < 2:
            return ComplexityLevel.LOW
        elif file_count <= 20:
            return ComplexityLevel.MEDIUM
        else:
            return ComplexityLevel.HIGH
