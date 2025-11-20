"""Query transformation for converting commit messages to user-style queries."""

import re
import os
from typing import Optional


class QueryTransformer:
    """Transforms commit messages into natural language queries."""
    
    def __init__(self, use_llm: bool = False, llm_provider: Optional[str] = None):
        """
        Initialize the QueryTransformer.
        
        Args:
            use_llm: Whether to use LLM-based transformation (requires API keys)
            llm_provider: LLM provider to use ('openai' or 'anthropic')
        """
        self.use_llm = use_llm
        self.llm_provider = llm_provider
        
        # Technical prefixes to remove (including scope like fix(auth):)
        self.technical_prefixes = [
            r'^fix(\([^)]+\))?:\s*',
            r'^feat(\([^)]+\))?:\s*',
            r'^feature(\([^)]+\))?:\s*',
            r'^chore(\([^)]+\))?:\s*',
            r'^docs(\([^)]+\))?:\s*',
            r'^style(\([^)]+\))?:\s*',
            r'^refactor(\([^)]+\))?:\s*',
            r'^test(\([^)]+\))?:\s*',
            r'^build(\([^)]+\))?:\s*',
            r'^ci(\([^)]+\))?:\s*',
            r'^perf(\([^)]+\))?:\s*',
            r'^revert(\([^)]+\))?:\s*',
            r'^\[fix\]\s*',
            r'^\[feat\]\s*',
            r'^\[feature\]\s*',
            r'^\[chore\]\s*',
            r'^\[docs\]\s*',
            r'^\[style\]\s*',
            r'^\[refactor\]\s*',
            r'^\[test\]\s*',
            r'^\[build\]\s*',
            r'^\[ci\]\s*',
            r'^\[perf\]\s*',
        ]
        
        # Initialize LLM client if requested
        self._llm_client = None
        if use_llm:
            self._initialize_llm_client()
    
    def _initialize_llm_client(self):
        """Initialize the LLM client based on provider."""
        if self.llm_provider == 'openai':
            try:
                import openai
                api_key = os.getenv('OPENAI_API_KEY')
                if api_key:
                    self._llm_client = openai.OpenAI(api_key=api_key)
            except ImportError:
                pass  # Will fallback to rule-based
        elif self.llm_provider == 'anthropic':
            try:
                import anthropic
                api_key = os.getenv('ANTHROPIC_API_KEY')
                if api_key:
                    self._llm_client = anthropic.Anthropic(api_key=api_key)
            except ImportError:
                pass  # Will fallback to rule-based
    
    def commit_message_to_query(self, message: str) -> str:
        """
        Transform a commit message into a user-style query.
        
        First attempts LLM-based transformation if enabled and available,
        then falls back to rule-based transformation.
        
        Args:
            message: Raw commit message
            
        Returns:
            Transformed query string suitable for code search
        """
        # Try LLM-based transformation first if enabled
        if self.use_llm and self._llm_client:
            try:
                llm_query = self._llm_transform(message)
                if llm_query:
                    return llm_query
            except Exception:
                # Fallback to rule-based on any error
                pass
        
        # Use rule-based transformation
        return self._rule_based_transform(message)
    
    def _rule_based_transform(self, message: str) -> str:
        """
        Apply rule-based transformation to commit message.
        
        Steps:
        1. Remove technical prefixes (fix:, feat:, etc.)
        2. Take only the first line (subject line)
        3. Handle special characters
        4. Clean up whitespace
        5. Convert to natural language style
        
        Args:
            message: Raw commit message
            
        Returns:
            Cleaned and transformed query
        """
        # Take only the first line (subject line)
        query = message.split('\n')[0].strip()
        
        # Remove technical prefixes
        for prefix_pattern in self.technical_prefixes:
            query = re.sub(prefix_pattern, '', query, flags=re.IGNORECASE)
        
        # Remove issue/ticket references like (#123), [JIRA-456], etc.
        query = re.sub(r'\(#\d+\)', '', query)
        query = re.sub(r'\[[\w]+-\d+\]', '', query)
        query = re.sub(r'#\d+', '', query)
        
        # Handle special characters
        # Replace underscores and hyphens with spaces (but keep them in code-like terms)
        query = re.sub(r'([a-z])_([a-z])', r'\1 \2', query)
        
        # Remove excessive punctuation
        query = re.sub(r'[^\w\s\-\.]', ' ', query)
        
        # Clean up multiple spaces
        query = re.sub(r'\s+', ' ', query)
        
        # Trim and ensure it's not empty
        query = query.strip()
        
        if not query:
            return message.strip()  # Return original if transformation resulted in empty string
        
        return query
    
    def _llm_transform(self, message: str) -> Optional[str]:
        """
        Use LLM to transform commit message to natural language query.
        
        Args:
            message: Raw commit message
            
        Returns:
            LLM-generated query or None if transformation fails
        """
        if not self._llm_client:
            return None
        
        prompt = f"""Convert this Git commit message into a natural language search query that a developer might use to find the relevant code files.

Commit message: {message}

Return only the search query, nothing else. Make it concise and focused on what code changes were made."""
        
        try:
            if self.llm_provider == 'openai':
                response = self._llm_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that converts commit messages to search queries."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=100,
                    temperature=0.3
                )
                return response.choices[0].message.content.strip()
            
            elif self.llm_provider == 'anthropic':
                response = self._llm_client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=100,
                    temperature=0.3,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.content[0].text.strip()
        
        except Exception:
            return None
        
        return None
