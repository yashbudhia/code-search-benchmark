"""Example: Creating custom agents for different tools.

This file contains example implementations for various code search tools.
Copy and modify these examples to create your own agents.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from benchmark.agents.base import RetrievalAgent
from benchmark.agents.cli_agent import CLIAgent
from benchmark.agents.api_agent import APIAgent
from benchmark.models import RetrievalResult


# Example 1: Simple CLI Tool Agent
class SimpleCLIAgent(CLIAgent):
    """Example: Adapt any CLI search tool.
    
    Replace the command with your tool's syntax.
    """
    
    def __init__(self):
        super().__init__(
            # Adjust this command to match your tool
            command_template='your-tool search "{query}" --path {repo}',
            output_parser=self._parse_output,
            name="YourTool"
        )
    
    @staticmethod
    def _parse_output(output: str):
        """Parse your tool's output format.
        
        Adjust this based on how your tool outputs results.
        """
        files = []
        for line in output.split('\n'):
            line = line.strip()
            if line and (line.endswith('.py') or line.endswith('.js')):
                files.append(line)
        return files


# Example 2: Claude Code CLI Agent
class ClaudeCodeCLIAgent(CLIAgent):
    """Example: Adapt Claude Code CLI (hypothetical).
    
    Adjust based on actual Claude Code CLI syntax.
    """
    
    def __init__(self):
        super().__init__(
            command_template='claude code search "{query}"',
            output_parser=self._parse_claude_output,
            name="ClaudeCodeCLI"
        )
    
    @staticmethod
    def _parse_claude_output(output: str):
        """Parse Claude Code output."""
        import re
        files = []
        
        # Example: Extract file paths from output
        # Adjust regex based on actual output format
        for line in output.split('\n'):
            # Look for file paths
            match = re.search(r'[\w/.-]+\.(py|js|ts|java|cpp|go|rs)', line)
            if match:
                files.append(match.group(0))
        
        return files


# Example 3: GitHub Copilot API Agent
class GitHubCopilotAgent(APIAgent):
    """Example: GitHub Copilot API integration.
    
    Note: This is a template. Adjust based on actual Copilot API.
    """
    
    def __init__(self, github_token: str = None):
        token = github_token or os.getenv("GITHUB_TOKEN")
        
        super().__init__(
            api_url="https://api.github.com/copilot/search",  # Example URL
            api_key=token,
            headers={
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            },
            name="GitHubCopilot"
        )
    
    def retrieve(self, query: str) -> RetrievalResult:
        """Custom retrieval for Copilot API."""
        # Implement Copilot-specific API call
        # This is a placeholder - adjust based on actual API
        
        try:
            import requests
            
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={
                    "query": query,
                    "repository": self.repo_path,
                    "max_results": 20
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                files = data.get("files", [])
                
                return RetrievalResult(
                    files=files,
                    scores=[],
                    metadata={"source": "copilot"}
                )
            else:
                return RetrievalResult(
                    files=[],
                    metadata={"error": f"HTTP {response.status_code}"}
                )
                
        except Exception as e:
            return RetrievalResult(
                files=[],
                metadata={"error": str(e)}
            )


# Example 4: Custom Python Library Agent
class CustomSearchAgent(RetrievalAgent):
    """Example: Use a Python library for code search.
    
    This shows how to integrate any Python-based search library.
    """
    
    def __init__(self):
        super().__init__(name="CustomSearch")
        self.index = None
        self.repo_path = None
    
    def initialize(self, repo_path: str):
        """Build search index."""
        self.repo_path = repo_path
        
        # Example: Build a simple index
        self.index = {}
        
        for root, dirs, files in os.walk(repo_path):
            if '.git' in dirs:
                dirs.remove('.git')
            
            for file in files:
                if self._is_code_file(file):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, repo_path)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read().lower()
                            self.index[rel_path.replace('\\', '/')] = content
                    except Exception:
                        pass
    
    def retrieve(self, query: str) -> RetrievalResult:
        """Search using custom logic."""
        query_lower = query.lower()
        query_terms = query_lower.split()
        
        # Score files based on term matches
        scores = {}
        for file_path, content in self.index.items():
            score = sum(1 for term in query_terms if term in content)
            if score > 0:
                scores[file_path] = score
        
        # Sort by score
        ranked_files = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        # Return top 10
        files = [f for f, _ in ranked_files[:10]]
        file_scores = [s for _, s in ranked_files[:10]]
        
        return RetrievalResult(
            files=files,
            scores=file_scores,
            metadata={"total_matches": len(scores)}
        )
    
    def reset(self):
        """Clear any caches."""
        pass
    
    @staticmethod
    def _is_code_file(filename: str) -> bool:
        """Check if file is a code file."""
        code_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c',
            '.cs', '.go', '.rs', '.rb', '.php', '.swift', '.kt'
        }
        return any(filename.endswith(ext) for ext in code_extensions)


# Example 5: Wrapper for External Service
class ExternalServiceAgent(RetrievalAgent):
    """Example: Call an external service or API.
    
    Use this pattern for any external code search service.
    """
    
    def __init__(self, service_url: str, api_key: str = None):
        super().__init__(name="ExternalService")
        self.service_url = service_url
        self.api_key = api_key
        self.repo_path = None
    
    def initialize(self, repo_path: str):
        """Setup connection to external service."""
        self.repo_path = repo_path
        
        # Example: Register repository with service
        # self._register_repo(repo_path)
    
    def retrieve(self, query: str) -> RetrievalResult:
        """Query external service."""
        try:
            import requests
            
            response = requests.post(
                f"{self.service_url}/search",
                json={
                    "query": query,
                    "repo": self.repo_path
                },
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return RetrievalResult(
                    files=data.get("files", []),
                    scores=data.get("scores", []),
                    metadata={"service": "external"}
                )
            else:
                return RetrievalResult(files=[], metadata={"error": "service_error"})
                
        except Exception as e:
            return RetrievalResult(files=[], metadata={"error": str(e)})
    
    def reset(self):
        """Clear service-side caches if needed."""
        # Example: Call service reset endpoint
        # requests.post(f"{self.service_url}/reset")
        pass


# Usage Example
if __name__ == "__main__":
    print("Example Custom Agents")
    print("=" * 50)
    print("\nTo use these agents:")
    print("1. Copy the agent class you want to use")
    print("2. Modify it for your specific tool/service")
    print("3. Register it in benchmark/cli.py or use evaluate_custom_agent.py")
    print("\nAvailable examples:")
    print("  - SimpleCLIAgent: For any CLI tool")
    print("  - ClaudeCodeCLIAgent: For Claude Code CLI")
    print("  - GitHubCopilotAgent: For GitHub Copilot API")
    print("  - CustomSearchAgent: For Python libraries")
    print("  - ExternalServiceAgent: For external APIs")
