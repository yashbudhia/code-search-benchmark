"""CLI-based retrieval agent for command-line tools."""

import subprocess
import json
import os
import re
from typing import List, Optional
from pathlib import Path

from benchmark.agents.base import RetrievalAgent
from benchmark.models import RetrievalResult


class CLIAgent(RetrievalAgent):
    """Generic CLI-based retrieval agent.
    
    This agent executes a command-line tool and parses its output
    to extract file paths. Useful for evaluating CLI-based code search tools.
    
    Example usage:
        agent = CLIAgent(
            command_template="my-search-tool --query '{query}' --repo {repo}",
            output_parser=lambda output: output.strip().split('\\n')
        )
    """
    
    def __init__(
        self,
        command_template: str,
        output_parser: callable = None,
        timeout: int = 30,
        name: str = "CLIAgent"
    ):
        """Initialize the CLI agent.
        
        Args:
            command_template: Command template with {query} and {repo} placeholders
            output_parser: Function to parse command output into list of file paths
            timeout: Command timeout in seconds
            name: Agent name for reporting
        """
        super().__init__(name)
        self.command_template = command_template
        self.output_parser = output_parser or self._default_parser
        self.timeout = timeout
        self.repo_path = None
    
    def initialize(self, repo_path: str) -> None:
        """Store repository path."""
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
        """Execute CLI command and parse results.
        
        Args:
            query: Natural language search query
            
        Returns:
            RetrievalResult with ranked files
        """
        try:
            # Build command
            command = self.command_template.format(
                query=query,
                repo=self.repo_path
            )
            
            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=self.repo_path
            )
            
            # Parse output
            if result.returncode == 0:
                files = self.output_parser(result.stdout)
            else:
                # Try to parse stderr if stdout is empty
                files = self.output_parser(result.stderr) if result.stderr else []
            
            # Validate and normalize file paths
            validated_files = []
            for file_path in files:
                if not file_path:
                    continue
                
                # Normalize path
                normalized = file_path.strip().replace('\\', '/')
                
                # Remove leading ./ if present
                if normalized.startswith('./'):
                    normalized = normalized[2:]
                
                # Check if file exists in repo
                if normalized in self.repo_files:
                    validated_files.append(normalized)
            
            return RetrievalResult(
                files=validated_files,
                scores=[],
                metadata={
                    "command": command,
                    "return_code": result.returncode
                }
            )
            
        except subprocess.TimeoutExpired:
            return RetrievalResult(
                files=[],
                scores=[],
                metadata={"error": "Command timeout"}
            )
        except Exception as e:
            return RetrievalResult(
                files=[],
                scores=[],
                metadata={"error": str(e)}
            )
    
    def reset(self) -> None:
        """Clear any cached state."""
        pass
    
    @staticmethod
    def _default_parser(output: str) -> List[str]:
        """Default parser: one file path per line."""
        return [line.strip() for line in output.strip().split('\n') if line.strip()]


class ClaudeCodeAgent(CLIAgent):
    """Adapter for Claude Code CLI tool.
    
    This assumes Claude Code has a CLI interface that can search code.
    Adjust the command template based on actual Claude Code CLI syntax.
    
    Example:
        agent = ClaudeCodeAgent()
    """
    
    def __init__(self):
        super().__init__(
            command_template='claude-code search "{query}"',
            output_parser=self._parse_claude_output,
            name="ClaudeCode"
        )
    
    @staticmethod
    def _parse_claude_output(output: str) -> List[str]:
        """Parse Claude Code output format.
        
        Adjust this based on actual Claude Code output format.
        """
        files = []
        
        # Example: Extract file paths from output
        # Assuming format like: "Found in: path/to/file.py"
        for line in output.split('\n'):
            if 'Found in:' in line or line.endswith('.py') or line.endswith('.js'):
                # Extract file path
                match = re.search(r'[\w/.-]+\.\w+', line)
                if match:
                    files.append(match.group(0))
        
        return files


class RipgrepAgent(CLIAgent):
    """Adapter for ripgrep (rg) command-line tool.
    
    Example:
        agent = RipgrepAgent()
    """
    
    def __init__(self):
        super().__init__(
            command_template='rg -l "{query}"',
            output_parser=lambda output: output.strip().split('\n'),
            name="Ripgrep"
        )


class SilverSearcherAgent(CLIAgent):
    """Adapter for The Silver Searcher (ag) command-line tool.
    
    Example:
        agent = SilverSearcherAgent()
    """
    
    def __init__(self):
        super().__init__(
            command_template='ag -l "{query}"',
            output_parser=lambda output: output.strip().split('\n'),
            name="SilverSearcher"
        )


class CustomCLIAgent(CLIAgent):
    """Template for creating custom CLI agents.
    
    Example:
        def my_parser(output):
            # Parse your tool's output format
            return [line.split(':')[0] for line in output.split('\\n')]
        
        agent = CustomCLIAgent(
            command='my-tool search "{query}" --format json',
            parser=my_parser
        )
    """
    
    def __init__(self, command: str, parser: callable = None):
        super().__init__(
            command_template=command,
            output_parser=parser,
            name="CustomCLI"
        )
