"""MCP-based retrieval agent for testing tools like Greb."""

import os
import json
import subprocess
from typing import List, Optional
from pathlib import Path

from benchmark.agents.base import RetrievalAgent
from benchmark.models import RetrievalResult


class MCPAgent(RetrievalAgent):
    """Agent that uses MCP (Model Context Protocol) tools for code search.
    
    This agent can interface with MCP servers like Greb to perform code search.
    """
    
    def __init__(self, mcp_tool_name: str = "greb_search", name: str = "MCPAgent"):
        """Initialize the MCP agent.
        
        Args:
            mcp_tool_name: Name of the MCP tool to use (e.g., "greb_search")
            name: Agent name for reporting
        """
        super().__init__(name)
        self.mcp_tool_name = mcp_tool_name
        self.repo_path = None
        self.repo_files = set()
    
    def initialize(self, repo_path: str) -> None:
        """Store repository path and index files."""
        self.repo_path = os.path.abspath(repo_path)
        
        # Get list of all files in repo for validation
        self.repo_files = set()
        for root, dirs, files in os.walk(repo_path):
            if '.git' in dirs:
                dirs.remove('.git')
            
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, repo_path)
                self.repo_files.add(rel_path.replace('\\', '/'))
    
    def retrieve(self, query: str) -> RetrievalResult:
        """Execute search using MCP tool.
        
        This method should be overridden by specific MCP tool implementations.
        
        Args:
            query: Natural language search query
            
        Returns:
            RetrievalResult with ranked files
        """
        raise NotImplementedError("Subclasses must implement retrieve()")
    
    def reset(self) -> None:
        """Clear any cached state."""
        pass
    
    def _validate_files(self, files: List[str]) -> List[str]:
        """Validate and normalize file paths.
        
        Args:
            files: List of file paths to validate
            
        Returns:
            List of validated and normalized file paths
        """
        validated = []
        for file_path in files:
            if not file_path:
                continue
            
            # Normalize path
            normalized = file_path.strip().replace('\\', '/')
            
            # Remove leading ./ if present
            if normalized.startswith('./'):
                normalized = normalized[2:]
            
            # Make relative to repo if absolute
            if os.path.isabs(normalized):
                try:
                    normalized = os.path.relpath(normalized, self.repo_path).replace('\\', '/')
                except ValueError:
                    # Path is on different drive, skip it
                    continue
            
            # Check if file exists in repo
            if normalized in self.repo_files:
                validated.append(normalized)
        
        return validated


class GrebMCPAgent(MCPAgent):
    """Agent that uses Greb MCP tool for code search.
    
    This agent interfaces with the Greb MCP server to perform semantic code search.
    
    Example usage:
        agent = GrebMCPAgent()
        agent.initialize('/path/to/repo')
        result = agent.retrieve('find authentication logic')
    """
    
    def __init__(self):
        super().__init__(mcp_tool_name="greb_search", name="GrebMCP")
    
    def retrieve(self, query: str) -> RetrievalResult:
        """Execute search using Greb MCP tool.
        
        Args:
            query: Natural language search query
            
        Returns:
            RetrievalResult with ranked files from Greb
        """
        try:
            # Call Greb MCP tool via Kiro's MCP interface
            # This assumes you have Greb MCP configured in Kiro
            
            # Option 1: If Greb returns file paths directly
            files = self._call_greb_mcp(query)
            
            # Validate and normalize file paths
            validated_files = self._validate_files(files)
            
            return RetrievalResult(
                files=validated_files,
                scores=[],
                metadata={
                    "tool": "greb_mcp",
                    "query": query,
                    "total_results": len(files),
                    "validated_results": len(validated_files)
                }
            )
            
        except Exception as e:
            return RetrievalResult(
                files=[],
                scores=[],
                metadata={"error": str(e), "tool": "greb_mcp"}
            )
    
    def _call_greb_mcp(self, query: str) -> List[str]:
        """Call Greb MCP tool to perform search.
        
        This method needs to be implemented based on how you access
        the Greb MCP tool. Options:
        
        1. Via Kiro's MCP interface (if available)
        2. Via direct API call to Greb
        3. Via CLI wrapper
        
        Args:
            query: Search query
            
        Returns:
            List of file paths from Greb
        """
        # TODO: Implement actual Greb MCP call
        # This is a placeholder that you'll need to customize
        
        # Example: If Greb has a CLI interface
        # result = subprocess.run(
        #     ['greb', 'search', query, '--repo', self.repo_path, '--format', 'json'],
        #     capture_output=True,
        #     text=True,
        #     timeout=30
        # )
        # data = json.loads(result.stdout)
        # return data.get('files', [])
        
        # Example: If using MCP directly
        # You might need to use Kiro's MCP client or make HTTP requests
        
        raise NotImplementedError(
            "You need to implement _call_greb_mcp() based on how you access Greb. "
            "See the comments in this method for examples."
        )


class CopilotMCPAgent(MCPAgent):
    """Agent that uses GitHub Copilot with MCP for code search.
    
    This agent can interface with Copilot's code search capabilities
    through MCP if available.
    """
    
    def __init__(self):
        super().__init__(mcp_tool_name="copilot_search", name="CopilotMCP")
    
    def retrieve(self, query: str) -> RetrievalResult:
        """Execute search using Copilot MCP.
        
        Args:
            query: Natural language search query
            
        Returns:
            RetrievalResult with ranked files from Copilot
        """
        try:
            # Call Copilot MCP tool
            files = self._call_copilot_mcp(query)
            
            # Validate and normalize file paths
            validated_files = self._validate_files(files)
            
            return RetrievalResult(
                files=validated_files,
                scores=[],
                metadata={
                    "tool": "copilot_mcp",
                    "query": query,
                    "total_results": len(files),
                    "validated_results": len(validated_files)
                }
            )
            
        except Exception as e:
            return RetrievalResult(
                files=[],
                scores=[],
                metadata={"error": str(e), "tool": "copilot_mcp"}
            )
    
    def _call_copilot_mcp(self, query: str) -> List[str]:
        """Call Copilot MCP tool to perform search.
        
        Args:
            query: Search query
            
        Returns:
            List of file paths from Copilot
        """
        # TODO: Implement Copilot MCP call
        raise NotImplementedError(
            "You need to implement _call_copilot_mcp() based on your Copilot MCP setup."
        )


class ManualMCPAgent(MCPAgent):
    """Agent for manually testing MCP tools.
    
    This agent allows you to manually provide results from MCP tools
    for testing purposes.
    """
    
    def __init__(self, results_callback=None):
        """Initialize manual MCP agent.
        
        Args:
            results_callback: Function that takes a query and returns list of files
        """
        super().__init__(mcp_tool_name="manual", name="ManualMCP")
        self.results_callback = results_callback
        self.query_results = {}
    
    def set_results(self, query: str, files: List[str]):
        """Manually set results for a query.
        
        Args:
            query: The query string
            files: List of file paths to return for this query
        """
        self.query_results[query] = files
    
    def retrieve(self, query: str) -> RetrievalResult:
        """Retrieve manually set results.
        
        Args:
            query: Natural language search query
            
        Returns:
            RetrievalResult with manually provided files
        """
        # Try callback first
        if self.results_callback:
            try:
                files = self.results_callback(query)
                validated_files = self._validate_files(files)
                return RetrievalResult(
                    files=validated_files,
                    scores=[],
                    metadata={"tool": "manual_callback", "query": query}
                )
            except Exception as e:
                pass
        
        # Try pre-set results
        if query in self.query_results:
            files = self.query_results[query]
            validated_files = self._validate_files(files)
            return RetrievalResult(
                files=validated_files,
                scores=[],
                metadata={"tool": "manual_preset", "query": query}
            )
        
        # No results available
        return RetrievalResult(
            files=[],
            scores=[],
            metadata={
                "error": "No results set for this query",
                "tool": "manual",
                "query": query
            }
        )
