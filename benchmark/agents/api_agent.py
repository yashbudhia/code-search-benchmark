"""API-based retrieval agent for services like GitHub Copilot, Codeium, etc."""

import os
import requests
import time
from typing import List, Optional
from pathlib import Path

from benchmark.agents.base import RetrievalAgent
from benchmark.models import RetrievalResult


class APIAgent(RetrievalAgent):
    """Generic API-based retrieval agent.
    
    This agent can be used to evaluate any code search API that accepts
    a query and returns a list of file paths.
    
    Example usage:
        agent = APIAgent(
            api_url="https://api.example.com/search",
            api_key=os.getenv("API_KEY"),
            headers={"Content-Type": "application/json"}
        )
    """
    
    def __init__(
        self,
        api_url: str,
        api_key: Optional[str] = None,
        headers: Optional[dict] = None,
        timeout: int = 30,
        name: str = "APIAgent"
    ):
        """Initialize the API agent.
        
        Args:
            api_url: Base URL for the search API
            api_key: API key for authentication (optional)
            headers: Additional HTTP headers (optional)
            timeout: Request timeout in seconds
            name: Agent name for reporting
        """
        super().__init__(name)
        self.api_url = api_url
        self.api_key = api_key
        self.timeout = timeout
        self.headers = headers or {}
        self.repo_path = None
        
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
    
    def initialize(self, repo_path: str) -> None:
        """Store repository path for context."""
        self.repo_path = repo_path
        
        # Get list of all files in repo for validation
        self.repo_files = set()
        for root, dirs, files in os.walk(repo_path):
            # Skip .git directory
            if '.git' in dirs:
                dirs.remove('.git')
            
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, repo_path)
                self.repo_files.add(rel_path.replace('\\', '/'))
    
    def retrieve(self, query: str) -> RetrievalResult:
        """Execute search via API.
        
        Args:
            query: Natural language search query
            
        Returns:
            RetrievalResult with ranked files
        """
        try:
            # Prepare request payload
            payload = {
                "query": query,
                "repository": self.repo_path,
                "max_results": 20
            }
            
            # Make API request
            response = requests.post(
                self.api_url,
                json=payload,
                headers=self.headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Parse response
            data = response.json()
            files = data.get("files", [])
            scores = data.get("scores", [])
            
            # Validate and normalize file paths
            validated_files = []
            validated_scores = []
            
            for i, file_path in enumerate(files):
                # Normalize path separators
                normalized = file_path.replace('\\', '/')
                
                # Check if file exists in repo
                if normalized in self.repo_files:
                    validated_files.append(normalized)
                    if scores and i < len(scores):
                        validated_scores.append(scores[i])
            
            return RetrievalResult(
                files=validated_files,
                scores=validated_scores,
                metadata={
                    "api_url": self.api_url,
                    "response_time_ms": response.elapsed.total_seconds() * 1000
                }
            )
            
        except requests.exceptions.RequestException as e:
            # Return empty result on API failure
            return RetrievalResult(
                files=[],
                scores=[],
                metadata={"error": str(e)}
            )
    
    def reset(self) -> None:
        """Clear any cached state."""
        # API agents are typically stateless
        pass


class CopilotAgent(APIAgent):
    """GitHub Copilot code search adapter.
    
    Note: This is a template. You'll need to adapt it to the actual
    Copilot API endpoints and authentication method.
    
    Example:
        agent = CopilotAgent(api_key=os.getenv("GITHUB_TOKEN"))
    """
    
    def __init__(self, api_key: str):
        super().__init__(
            api_url="https://api.github.com/copilot/search",  # Example URL
            api_key=api_key,
            name="GitHubCopilot"
        )
    
    def retrieve(self, query: str) -> RetrievalResult:
        """Execute Copilot-specific search.
        
        Override this method to match Copilot's actual API format.
        """
        # TODO: Implement actual Copilot API integration
        # This is a placeholder showing the structure
        
        return super().retrieve(query)


class CodeiumAgent(APIAgent):
    """Codeium code search adapter.
    
    Example:
        agent = CodeiumAgent(api_key=os.getenv("CODEIUM_API_KEY"))
    """
    
    def __init__(self, api_key: str):
        super().__init__(
            api_url="https://api.codeium.com/search",  # Example URL
            api_key=api_key,
            name="Codeium"
        )
