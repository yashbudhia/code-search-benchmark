"""Configuration loading and validation for the benchmark system."""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

from benchmark.models import FilterConfig


@dataclass
class EvaluationConfig:
    """Configuration for evaluation execution."""
    num_runs: int = 3
    timeout_seconds: int = 30
    randomize_order: bool = True


@dataclass
class AgentConfig:
    """Configuration for a retrieval agent."""
    name: str
    class_name: str
    config: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OutputConfig:
    """Configuration for output generation."""
    directory: str = "./benchmark_results"
    formats: list = field(default_factory=lambda: ["json", "csv", "markdown"])
    generate_visualizations: bool = True


@dataclass
class BenchmarkConfig:
    """Complete benchmark configuration."""
    dataset: FilterConfig
    evaluation: EvaluationConfig
    agents: list[AgentConfig]
    output: OutputConfig
    repository_path: Optional[str] = None


def load_config(config_path: str) -> BenchmarkConfig:
    """Load benchmark configuration from YAML file.
    
    Args:
        config_path: Path to the YAML configuration file
        
    Returns:
        BenchmarkConfig object with validated configuration
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config is invalid
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_file, 'r') as f:
        data = yaml.safe_load(f)
    
    if not data:
        raise ValueError("Configuration file is empty")
    
    # Parse dataset configuration
    dataset_config = data.get("dataset", {})
    filter_config = FilterConfig(
        exclude_patterns=dataset_config.get("exclude_patterns", [
            "*.md", "*.json", "test_*", "docs/*"
        ]),
        min_files=dataset_config.get("min_files", 2),
        max_files=dataset_config.get("max_files", 20),
        include_merge_commits=dataset_config.get("include_merge_commits", False)
    )
    
    # Parse evaluation configuration
    eval_config_data = data.get("evaluation", {})
    eval_config = EvaluationConfig(
        num_runs=eval_config_data.get("num_runs", 3),
        timeout_seconds=eval_config_data.get("timeout_seconds", 30),
        randomize_order=eval_config_data.get("randomize_order", True)
    )
    
    # Parse agent configurations
    agents_data = data.get("agents", [])
    agents = []
    for agent_data in agents_data:
        if "name" not in agent_data or "class" not in agent_data:
            raise ValueError("Each agent must have 'name' and 'class' fields")
        
        agents.append(AgentConfig(
            name=agent_data["name"],
            class_name=agent_data["class"],
            config=agent_data.get("config", {})
        ))
    
    # Parse output configuration
    output_data = data.get("output", {})
    output_config = OutputConfig(
        directory=output_data.get("directory", "./benchmark_results"),
        formats=output_data.get("formats", ["json", "csv", "markdown"]),
        generate_visualizations=output_data.get("generate_visualizations", True)
    )
    
    # Get repository path if specified
    repo_path = dataset_config.get("repository_path")
    
    return BenchmarkConfig(
        dataset=filter_config,
        evaluation=eval_config,
        agents=agents,
        output=output_config,
        repository_path=repo_path
    )


def create_default_config(output_path: str) -> None:
    """Create a default configuration file template.
    
    Args:
        output_path: Path where the config file should be created
    """
    default_config = {
        "dataset": {
            "repository_path": "/path/to/repo",
            "exclude_patterns": [
                "*.md",
                "*.json",
                "test_*",
                "docs/*"
            ],
            "min_files": 2,
            "max_files": 20,
            "include_merge_commits": False
        },
        "evaluation": {
            "num_runs": 3,
            "timeout_seconds": 30,
            "randomize_order": True
        },
        "agents": [
            {
                "name": "keyword_search",
                "class": "KeywordSearchAgent",
                "config": {
                    "case_sensitive": False
                }
            }
        ],
        "output": {
            "directory": "./benchmark_results",
            "formats": ["json", "csv", "markdown"],
            "generate_visualizations": True
        }
    }
    
    with open(output_path, 'w') as f:
        yaml.dump(default_config, f, default_flow_style=False, sort_keys=False)
