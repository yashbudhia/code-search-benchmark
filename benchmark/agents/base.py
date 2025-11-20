"""Abstract base class for retrieval agents."""

from abc import ABC, abstractmethod
from benchmark.models import RetrievalResult


class RetrievalAgent(ABC):
    """Abstract interface that all retrieval agents must implement."""
    
    def __init__(self, name: str = None):
        """Initialize the agent with an optional name.
        
        Args:
            name: Human-readable name for the agent
        """
        self.name = name or self.__class__.__name__
    
    @abstractmethod
    def initialize(self, repo_path: str) -> None:
        """Setup agent with repository context.
        
        This method is called once before evaluation begins to allow
        the agent to index files, load models, or perform other setup.
        
        Args:
            repo_path: Path to the Git repository to search
        """
        pass
    
    @abstractmethod
    def retrieve(self, query: str) -> RetrievalResult:
        """Execute search and return ranked files.
        
        Args:
            query: Natural language search query
            
        Returns:
            RetrievalResult containing ranked file paths and optional scores
        """
        pass
    
    @abstractmethod
    def reset(self) -> None:
        """Clear any caching or state between queries.
        
        This method is called between test cases to ensure no state
        leakage affects evaluation results.
        """
        pass


def validate_agent(agent: RetrievalAgent) -> bool:
    """Validate that an agent properly implements the required interface.
    
    Args:
        agent: Agent instance to validate
        
    Returns:
        True if agent is valid
        
    Raises:
        TypeError: If agent doesn't implement RetrievalAgent
        AttributeError: If agent is missing required methods
    """
    if not isinstance(agent, RetrievalAgent):
        raise TypeError(f"Agent must inherit from RetrievalAgent, got {type(agent)}")
    
    required_methods = ['initialize', 'retrieve', 'reset']
    for method_name in required_methods:
        if not hasattr(agent, method_name):
            raise AttributeError(f"Agent missing required method: {method_name}")
        
        method = getattr(agent, method_name)
        if not callable(method):
            raise AttributeError(f"Agent.{method_name} must be callable")
    
    return True
