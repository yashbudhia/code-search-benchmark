"""Keyword-based search agent using simple grep-like matching."""

import os
from pathlib import Path
from typing import Dict, List, Set
from benchmark.agents.base import RetrievalAgent
from benchmark.models import RetrievalResult


class KeywordSearchAgent(RetrievalAgent):
    """Baseline retrieval agent using keyword matching.
    
    This agent performs simple grep-based search by:
    1. Indexing all files in the repository during initialization
    2. Searching file contents for query keywords
    3. Ranking files by number of keyword matches
    """
    
    def __init__(self, name: str = "KeywordSearch", case_sensitive: bool = False):
        """Initialize the keyword search agent.
        
        Args:
            name: Human-readable name for the agent
            case_sensitive: Whether to perform case-sensitive matching
        """
        super().__init__(name)
        self.case_sensitive = case_sensitive
        self.repo_path = None
        self.file_index: Dict[str, str] = {}  # file_path -> content
        self._query_cache: Dict[str, int] = {}  # For reset tracking
    
    def initialize(self, repo_path: str) -> None:
        """Index all files in the repository.
        
        Args:
            repo_path: Path to the Git repository to search
        """
        self.repo_path = Path(repo_path)
        self.file_index = {}
        
        # Index all text files in the repository
        for root, dirs, files in os.walk(self.repo_path):
            # Skip .git directory
            if '.git' in dirs:
                dirs.remove('.git')
            
            # Skip common non-code directories
            dirs[:] = [d for d in dirs if d not in {
                '__pycache__', 'node_modules', '.venv', 'venv', 
                'dist', 'build', '.pytest_cache'
            }]
            
            for file in files:
                file_path = Path(root) / file
                relative_path = file_path.relative_to(self.repo_path)
                
                # Try to read file content
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        self.file_index[str(relative_path)] = content
                except (IOError, UnicodeDecodeError):
                    # Skip binary files or files that can't be read
                    continue
    
    def retrieve(self, query: str) -> RetrievalResult:
        """Search for files matching the query keywords.
        
        Args:
            query: Natural language search query
            
        Returns:
            RetrievalResult with ranked files and match scores
        """
        if not self.file_index:
            return RetrievalResult(files=[], scores=[], metadata={})
        
        # Extract keywords from query (simple tokenization)
        keywords = self._extract_keywords(query)
        
        # Score each file based on keyword matches
        file_scores: Dict[str, int] = {}
        for file_path, content in self.file_index.items():
            score = self._calculate_match_score(content, keywords)
            if score > 0:
                file_scores[file_path] = score
        
        # Sort files by score (descending)
        ranked_files = sorted(file_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Extract files and scores
        files = [file_path for file_path, _ in ranked_files]
        scores = [float(score) for _, score in ranked_files]
        
        # Store in cache for reset tracking
        self._query_cache = file_scores
        
        return RetrievalResult(
            files=files,
            scores=scores,
            metadata={
                'total_matches': len(files),
                'keywords': keywords,
                'case_sensitive': self.case_sensitive
            }
        )
    
    def reset(self) -> None:
        """Clear any query-specific state."""
        self._query_cache = {}
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract searchable keywords from query.
        
        Args:
            query: Natural language query
            
        Returns:
            List of keywords to search for
        """
        # Simple tokenization: split on whitespace and common punctuation
        import re
        
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this',
            'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
        }
        
        # Tokenize
        tokens = re.findall(r'\b\w+\b', query.lower() if not self.case_sensitive else query)
        
        # Filter stop words and short tokens
        keywords = [t for t in tokens if t not in stop_words and len(t) > 2]
        
        return keywords
    
    def _calculate_match_score(self, content: str, keywords: List[str]) -> int:
        """Calculate match score for a file based on keyword occurrences.
        
        Args:
            content: File content to search
            keywords: List of keywords to match
            
        Returns:
            Match score (higher is better)
        """
        if not self.case_sensitive:
            content = content.lower()
        
        score = 0
        for keyword in keywords:
            search_term = keyword if self.case_sensitive else keyword.lower()
            # Count occurrences of each keyword
            count = content.count(search_term)
            score += count
        
        return score
