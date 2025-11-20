# Implementation Plan

- [x] 1. Set up project structure and core data models





  - Create directory structure: `benchmark/` with subdirectories for `dataset/`, `evaluation/`, `metrics/`, `reporting/`, and `agents/`
  - Implement core data models: `TestCase`, `GoldSet`, `TestResult`, `AggregateMetrics`, `EvaluationResults`, `ComplexityLevel` enum
  - Create `FilterConfig` configuration dataclass
  - Set up `pyproject.toml` with dependencies: GitPython, pandas, matplotlib, pydantic, click, pytest
  - _Requirements: 1.5, 2.5, 6.1_

- [x] 2. Implement Git commit analysis and filtering






  - [x] 2.1 Create CommitAnalyzer class with feature commit detection

    - Implement `is_feature_commit()` method that excludes merge commits, formatting-only commits, and documentation-only commits
    - Implement `extract_modified_files()` method using GitPython to get file paths from commit diffs
    - Implement `classify_complexity()` method based on file count thresholds
    - _Requirements: 1.1, 1.2, 2.2, 2.3_
  
  - [x] 2.2 Implement commit filtering logic


    - Create file pattern matching using glob patterns from `FilterConfig.exclude_patterns`
    - Filter commits based on `min_files` and `max_files` configuration
    - Apply exclusion rules for config files, docs, and test files
    - _Requirements: 1.1, 2.1, 2.4_

- [-] 3. Build query transformation system


  - [x] 3.1 Create QueryTransformer class



    - Implement `commit_message_to_query()` method with rule-based transformation (remove technical prefixes like "fix:", "feat:", convert to natural language)
    - Add optional LLM-based transformation using OpenAI/Anthropic API with fallback to rule-based
    - Handle special characters and formatting in commit messages
    - _Requirements: 1.3, 1.4_
  
  - [ ]* 3.2 Write unit tests for query transformation
    - Test transformation of various commit message formats
    - Test handling of special characters and edge cases
    - Test LLM fallback behavior
    - _Requirements: 1.4_

- [x] 4. Implement dataset generation pipeline






  - [x] 4.1 Create DatasetGenerator class

    - Implement `__init__()` to accept repo_path and FilterConfig
    - Implement `generate_gold_set()` method that orchestrates commit analysis, filtering, and query transformation
    - Implement `filter_commits()` method using CommitAnalyzer
    - Generate unique test case IDs and extract metadata (commit hash, timestamp)
    - _Requirements: 1.1, 1.5, 2.5_
  
  - [x] 4.2 Implement Gold Set persistence


    - Create JSON serialization for GoldSet with proper formatting
    - Include metadata: repository name, generation timestamp, commit counts
    - Validate output format matches design specification
    - _Requirements: 1.5, 2.5, 6.1_
  
  - [ ]* 4.3 Write integration tests for dataset generation
    - Create synthetic Git repository with known commits
    - Test end-to-end gold set generation
    - Verify filtering and exclusion rules work correctly
    - _Requirements: 1.1, 1.2, 1.5_

- [x] 5. Create retrieval agent interface and baseline implementations




  - [x] 5.1 Define RetrievalAgent abstract base class


    - Implement abstract methods: `initialize()`, `retrieve()`, `reset()`
    - Create `RetrievalResult` dataclass with files, scores, and metadata
    - Add interface validation in agent registration
    - _Requirements: 5.1, 5.2_
  
  - [x] 5.2 Implement KeywordSearchAgent baseline


    - Create simple grep-based search using file content matching
    - Implement `initialize()` to index repository files
    - Implement `retrieve()` to search and rank files by keyword matches
    - Implement `reset()` to clear any query-specific state
    - _Requirements: 5.1, 5.2_
  
  - [ ]* 5.3 Write tests for agent interface
    - Test that agents properly implement required methods
    - Test reset() clears state between queries
    - Test invalid agent registration is rejected
    - _Requirements: 5.1, 5.2_

- [x] 6. Build evaluation engine with timing and orchestration





  - [x] 6.1 Create EvaluationEngine class


    - Implement `__init__()` to accept GoldSet and RetrievalAgent
    - Implement `run_evaluation()` with test case randomization
    - Add timing logic using `time.perf_counter_ns()` for microsecond precision
    - Execute each query multiple times (configurable, default 3) and record median latency
    - Call `agent.reset()` between test cases to prevent state leakage
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 5.3, 5.4_
  
  - [x] 6.2 Implement timeout and error handling

    - Add configurable timeout per query (default 30 seconds)
    - Catch and log agent exceptions without stopping evaluation
    - Mark failed queries with error status in results
    - Validate agent responses (check files exist, normalize paths)
    - _Requirements: 5.4_
  
  - [ ]* 6.3 Write integration tests for evaluation engine
    - Test evaluation with mock agent
    - Verify timing accuracy
    - Test timeout handling
    - Test error recovery
    - _Requirements: 4.1, 4.2, 4.3, 5.3, 5.4_

- [x] 7. Implement metrics calculation system




  - [x] 7.1 Create MetricsCalculator class


    - Implement `calculate_f1_score()` with precision and recall calculation
    - Handle edge cases: empty sets, no overlap
    - Implement `calculate_partial_match_score()` for directory-level matches
    - _Requirements: 3.1, 3.2, 3.3, 3.4_
  
  - [x] 7.2 Implement aggregate statistics


    - Implement `aggregate_metrics()` to compute mean, median, std dev for F1 scores
    - Calculate latency percentiles: p50, p90, p99
    - Create `AggregateMetrics` dataclass with all summary statistics
    - _Requirements: 3.5, 4.5_
  
  - [ ]* 7.3 Write unit tests for metrics calculation
    - Test F1 score with known precision/recall values
    - Test partial matching logic
    - Test percentile calculations with edge cases
    - Test aggregate statistics computation
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [x] 8. Build report generation and export system





  - [x] 8.1 Create ReportGenerator class

    - Implement `export_json()` for detailed results with proper formatting
    - Implement `export_csv()` with columns: test_case_id, agent_name, retrieved_files, ground_truth_files, f1_score, latency_ms
    - Implement `export_markdown()` with summary tables and methodology description
    - _Requirements: 6.1, 6.2, 6.5_
  
  - [x] 8.2 Implement visualization generation


    - Create F1 score histogram using matplotlib
    - Create latency distribution histogram
    - Create accuracy vs latency scatter plot
    - Save visualizations as PNG files in output directory
    - _Requirements: 6.3_
  
  - [ ]* 8.3 Write tests for report generation
    - Test JSON export format matches specification
    - Test CSV export has correct columns
    - Test markdown generation includes all sections
    - Test visualization creation
    - _Requirements: 6.1, 6.2, 6.3, 6.5_

- [x] 9. Create CLI interface and configuration system



  - [x] 9.1 Implement CLI commands using Click


    - Create `generate` command for gold set generation with arguments: --repo, --output, --config
    - Create `evaluate` command for running evaluation with arguments: --gold-set, --agent, --output
    - Create `compare` command for multi-agent comparison with arguments: --gold-set, --agents, --output
    - Add help text and argument validation
    - _Requirements: 6.4_
  
  - [x] 9.2 Implement YAML configuration loading


    - Create configuration parser for benchmark_config.yaml
    - Validate configuration schema
    - Provide sensible defaults for optional parameters
    - Support agent-specific configuration sections
    - _Requirements: 2.4, 6.4_
  
  - [ ]* 9.3 Write CLI integration tests
    - Test each CLI command with sample inputs
    - Test configuration file parsing
    - Test error messages for invalid inputs
    - _Requirements: 6.4_

- [ ] 10. Add error handling and validation throughout
  - Implement repository validation (check .git directory exists)
  - Add commit parsing error handling with logging
  - Add query transformation fallback logic
  - Validate agent responses (file existence, path normalization)
  - Add comprehensive logging throughout pipeline
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 5.4_

- [ ] 11. Create example agents and usage documentation
  - [ ] 11.1 Implement SemanticSearchAgent example
    - Use sentence-transformers for embedding-based retrieval
    - Implement file content embedding and similarity search
    - Add configuration for model selection and top_k results
    - _Requirements: 5.1, 5.5_
  
  - [ ] 11.2 Create README with usage examples
    - Document installation instructions
    - Provide example commands for each CLI operation
    - Include sample configuration file
    - Document how to implement custom agents
    - _Requirements: 6.4, 6.5_
  
  - [ ]* 11.3 Create example notebooks
    - Create Jupyter notebook demonstrating dataset generation
    - Create notebook showing evaluation and analysis
    - Include visualization examples
    - _Requirements: 6.1, 6.2, 6.3_
