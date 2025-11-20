"""LLM-based retrieval agents using AI models for code search."""

import os
from typing import List, Optional
from pathlib import Path

from benchmark.agents.base import RetrievalAgent
from benchmark.models import RetrievalResult


class LLMAgent(RetrievalAgent):
    """Base class for LLM-based code search agents.
    
    This agent uses an LLM to understand the query and search through
    code files to find relevant matches.
    """
    
    def __init__(self, model_name: str = "gpt-4", name: str = "LLMAgent"):
        """Initialize the LLM agent.
        
        Args:
            model_name: Name of the LLM model to use
            name: Agent name for reporting
        """
        super().__init__(name)
        self.model_name = model_name
        self.repo_path = None
        self.file_contents = {}
    
    def initialize(self, repo_path: str) -> None:
        """Index repository files."""
        self.repo_path = repo_path
        self.file_contents = {}
        
        # Read all code files
        for root, dirs, files in os.walk(repo_path):
            if '.git' in dirs:
                dirs.remove('.git')
            
            for file in files:
                # Only index code files
                if self._is_code_file(file):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, repo_path)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            self.file_contents[rel_path.replace('\\', '/')] = f.read()
                    except Exception:
                        pass
    
    def retrieve(self, query: str) -> RetrievalResult:
        """Use LLM to find relevant files.
        
        Override this in subclasses to implement specific LLM logic.
        """
        raise NotImplementedError("Subclasses must implement retrieve()")
    
    def reset(self) -> None:
        """Clear any cached state."""
        pass
    
    @staticmethod
    def _is_code_file(filename: str) -> bool:
        """Check if file is a code file."""
        code_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h',
            '.cs', '.go', '.rs', '.rb', '.php', '.swift', '.kt', '.scala',
            '.r', '.m', '.sh', '.bash', '.sql', '.html', '.css', '.vue'
        }
        return any(filename.endswith(ext) for ext in code_extensions)


class OpenAIAgent(LLMAgent):
    """OpenAI-based code search agent.
    
    Uses OpenAI's API to understand queries and rank files.
    
    Example:
        agent = OpenAIAgent(
            api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-4"
        )
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        super().__init__(model_name=model, name=f"OpenAI-{model}")
        self.api_key = api_key
        self.client = None
    
    def initialize(self, repo_path: str) -> None:
        """Initialize OpenAI client and index files."""
        super().initialize(repo_path)
        
        try:
            import openai
            self.client = openai.OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("openai package required. Install with: pip install openai")
    
    def retrieve(self, query: str) -> RetrievalResult:
        """Use OpenAI to find relevant files."""
        if not self.client:
            return RetrievalResult(files=[], scores=[], metadata={"error": "Client not initialized"})
        
        try:
            # Create prompt with file list
            file_list = "\n".join([f"- {path}" for path in self.file_contents.keys()])
            
            prompt = f"""Given this query about code: "{query}"

And this list of files in the repository:
{file_list}

Return a JSON array of the top 10 most relevant file paths, ordered by relevance.
Only include the file paths, nothing else. Format: ["path1", "path2", ...]"""
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=500
            )
            
            # Parse response
            import json
            content = response.choices[0].message.content.strip()
            
            # Extract JSON array
            if content.startswith('[') and content.endswith(']'):
                files = json.loads(content)
            else:
                # Try to find JSON array in response
                import re
                match = re.search(r'\[.*\]', content, re.DOTALL)
                if match:
                    files = json.loads(match.group(0))
                else:
                    files = []
            
            # Validate files exist
            validated_files = [f for f in files if f in self.file_contents]
            
            return RetrievalResult(
                files=validated_files,
                scores=[],
                metadata={"model": self.model_name}
            )
            
        except Exception as e:
            return RetrievalResult(
                files=[],
                scores=[],
                metadata={"error": str(e)}
            )


class AnthropicAgent(LLMAgent):
    """Anthropic Claude-based code search agent.
    
    Example:
        agent = AnthropicAgent(
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            model="claude-3-opus-20240229"
        )
    """
    
    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229"):
        super().__init__(model_name=model, name=f"Claude-{model}")
        self.api_key = api_key
        self.client = None
    
    def initialize(self, repo_path: str) -> None:
        """Initialize Anthropic client and index files."""
        super().initialize(repo_path)
        
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError("anthropic package required. Install with: pip install anthropic")
    
    def retrieve(self, query: str) -> RetrievalResult:
        """Use Claude to find relevant files."""
        if not self.client:
            return RetrievalResult(files=[], scores=[], metadata={"error": "Client not initialized"})
        
        try:
            # Create prompt with file list
            file_list = "\n".join([f"- {path}" for path in self.file_contents.keys()])
            
            prompt = f"""Given this query about code: "{query}"

And this list of files in the repository:
{file_list}

Return a JSON array of the top 10 most relevant file paths, ordered by relevance.
Only include the file paths, nothing else. Format: ["path1", "path2", ...]"""
            
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=500,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse response
            import json
            content = response.content[0].text.strip()
            
            # Extract JSON array
            if content.startswith('[') and content.endswith(']'):
                files = json.loads(content)
            else:
                # Try to find JSON array in response
                import re
                match = re.search(r'\[.*\]', content, re.DOTALL)
                if match:
                    files = json.loads(match.group(0))
                else:
                    files = []
            
            # Validate files exist
            validated_files = [f for f in files if f in self.file_contents]
            
            return RetrievalResult(
                files=validated_files,
                scores=[],
                metadata={"model": self.model_name}
            )
            
        except Exception as e:
            return RetrievalResult(
                files=[],
                scores=[],
                metadata={"error": str(e)}
            )
