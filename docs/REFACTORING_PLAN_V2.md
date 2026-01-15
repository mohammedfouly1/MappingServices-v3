# Refactoring Plan v2.0

**Date:** January 15, 2026
**Status:** Planning Phase
**Priority:** Medium-High

---

## Executive Summary

This refactoring plan addresses architectural improvements, code quality enhancements, and maintainability upgrades for the Medical Services Mapping application. The current system is **production-ready and fully functional** (100% success rate on 180 batches), so these refactorings focus on **long-term maintainability, testability, and scalability**.

### Current System Health: ✅ EXCELLENT
- Processing: 100% success rate
- Performance: ~35 minutes for 180 batches
- Token efficiency: 31% cost savings
- All optimizations active and verified

---

## Priority Levels

- **P0 (Critical)**: Blocks future development or causes production issues
- **P1 (High)**: Significantly improves code quality or performance
- **P2 (Medium)**: Nice-to-have improvements
- **P3 (Low)**: Optional enhancements

---

## Phase 1: Architecture Improvements (P1)

### 1.1 Eliminate Global State in `result_processor.py`

**Priority:** P1
**Effort:** Medium (2-3 hours)
**Impact:** High - Enables testing, prevents race conditions

**Current Issues:**
```python
# result_processor.py - Lines 12-26
df_api_call = pd.DataFrame(...)  # Global DataFrame
df_api_mapping = pd.DataFrame(...)  # Global DataFrame
seen_first_codes = {}  # Global dictionary
_result_processor_lock = threading.Lock()  # Global lock
```

**Problems:**
- Makes unit testing impossible (can't isolate state)
- Hidden dependencies (functions depend on global state)
- Thread safety requires explicit locking
- Can't run multiple independent processing sessions
- Difficult to reset state between runs

**Proposed Solution:**
Create a `ResultProcessor` class to encapsulate state:

```python
class ResultProcessor:
    """Manages mapping results with deduplication and DataFrame storage."""

    def __init__(self):
        self.df_api_call = pd.DataFrame(columns=[...])
        self.df_api_mapping = pd.DataFrame(columns=[...])
        self.seen_first_codes = {}
        self._lock = threading.RLock()

    def reset(self):
        """Reset all internal state"""
        with self._lock:
            self.df_api_call = pd.DataFrame(columns=[...])
            self.df_api_mapping = pd.DataFrame(columns=[...])
            self.seen_first_codes = {}

    def process_mappings(self, mappings, response, elapsed_time, verbose=True):
        """Process mappings with deduplication"""
        with self._lock:
            # Current ProcessMappingResults logic here
            pass

    def get_dataframes(self):
        """Thread-safe DataFrame access"""
        with self._lock:
            return {
                'ApiCall': self.df_api_call.copy(),
                'ApiMapping': self.df_api_mapping.copy()
            }
```

**Benefits:**
- Easy to test (create instance, test methods, discard)
- Clear ownership of state
- Can run multiple processors in parallel if needed
- Thread safety built into class design
- Explicit initialization and reset

**Migration Path:**
1. Create `ResultProcessor` class
2. Update `session/state_manager.py` to create instance
3. Update all callers to use instance methods
4. Add deprecation warnings to global functions
5. Remove global functions after migration

---

### 1.2 Convert Config to Instance-Based Configuration

**Priority:** P1
**Effort:** Medium (2-3 hours)
**Impact:** High - Enables multiple configurations, testing

**Current Issues:**
```python
# config.py - Lines 7-210
class Config:
    """Configuration settings with Streamlit Cloud support"""

    # Class variables (shared across all usage)
    provider = settings.get("provider", "OpenAI")
    model = settings.get("model", "gpt-4o")
    temperature = settings.get("temperature", 0.2)
    # ... all configuration as class variables
```

**Problems:**
- Can't test with different configurations simultaneously
- Global state makes testing difficult
- Can't easily compare configuration scenarios
- Risk of accidental modification from anywhere
- Hard to implement configuration profiles

**Proposed Solution:**
Create instance-based configuration with class factory:

```python
@dataclass
class AppConfig:
    """Instance-based configuration with validation"""

    provider: str
    model: str
    temperature: float
    top_p: float
    max_tokens: int
    threshold: int
    max_batch_size: int
    max_concurrent_batches: int
    api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None

    def __post_init__(self):
        """Validate configuration on creation"""
        errors = self._validate()
        if errors:
            raise ValueError(f"Invalid configuration: {errors}")

    def _validate(self) -> List[str]:
        """Validate all configuration values"""
        errors = []
        if not 0.0 <= self.temperature <= 1.0:
            errors.append(f"Temperature must be 0-1, got {self.temperature}")
        # ... more validation
        return errors

    @classmethod
    def from_streamlit_secrets(cls) -> 'AppConfig':
        """Load configuration from Streamlit secrets"""
        return cls(
            provider=st.secrets.get("provider", "OpenAI"),
            model=st.secrets.get("model", "gpt-4o"),
            # ... load all settings
        )

    @classmethod
    def from_env(cls) -> 'AppConfig':
        """Load configuration from environment variables"""
        return cls(
            provider=os.getenv("PROVIDER", "OpenAI"),
            model=os.getenv("MODEL", "gpt-4o"),
            # ... load all settings
        )

    @classmethod
    def default(cls) -> 'AppConfig':
        """Get default configuration"""
        return cls(
            provider="OpenAI",
            model="gpt-4o",
            temperature=0.2,
            # ... default values
        )

class ConfigFactory:
    """Factory for creating and managing configurations"""

    _current: Optional[AppConfig] = None

    @classmethod
    def get_current(cls) -> AppConfig:
        """Get current configuration (lazy initialization)"""
        if cls._current is None:
            cls._current = AppConfig.default()
        return cls._current

    @classmethod
    def set_current(cls, config: AppConfig):
        """Set current configuration"""
        cls._current = config

    @classmethod
    def load_from_streamlit(cls) -> AppConfig:
        """Load and set configuration from Streamlit"""
        config = AppConfig.from_streamlit_secrets()
        cls.set_current(config)
        return config
```

**Benefits:**
- Easy to test with different configurations
- Immutable configuration (dataclass with frozen=True)
- Validation at creation time
- Support for configuration profiles
- Clear configuration lifecycle

**Migration Path:**
1. Create new `AppConfig` dataclass
2. Create `ConfigFactory` for backward compatibility
3. Update all `Config.attribute` to `ConfigFactory.get_current().attribute`
4. Add compatibility layer for gradual migration
5. Remove old `Config` class after migration

---

### 1.3 Separate API Client from Business Logic

**Priority:** P1
**Effort:** Medium (3-4 hours)
**Impact:** High - Better testability, cleaner architecture

**Current Issues:**
- `api_mapping.py` (439 lines) mixes:
  - API client initialization
  - API calls
  - Response parsing
  - Error handling
  - Business logic (mapping, deduplication)
  - Console output

**Proposed Solution:**
Split into focused modules:

```
api/
├── __init__.py
├── client.py          # API client abstraction
├── openai_client.py   # OpenAI-specific implementation
├── openrouter_client.py  # OpenRouter-specific implementation
└── exceptions.py      # Custom API exceptions

services/
├── __init__.py
├── mapping_service.py  # Business logic for mapping
└── response_parser.py  # Parse API responses
```

**Example Structure:**

```python
# api/client.py
class APIClient(ABC):
    """Abstract base class for API clients"""

    @abstractmethod
    def create_completion(self, prompt: str, config: AppConfig) -> APIResponse:
        """Create a completion with the given prompt"""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Get provider name"""
        pass

# api/openai_client.py
class OpenAIClient(APIClient):
    """OpenAI API client implementation"""

    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def create_completion(self, prompt: str, config: AppConfig) -> APIResponse:
        # Implementation
        pass

# services/mapping_service.py
class MappingService:
    """Service for performing medical service mappings"""

    def __init__(self, api_client: APIClient, result_processor: ResultProcessor):
        self.api_client = api_client
        self.result_processor = result_processor

    def perform_mapping(
        self,
        first_group: List[Dict],
        second_group: List[Dict],
        prompt: str,
        config: AppConfig
    ) -> MappingResult:
        """Perform mapping using API"""
        # Business logic here
        pass
```

**Benefits:**
- Easy to test (mock API client)
- Easy to add new providers (implement APIClient interface)
- Single Responsibility Principle
- Clear separation of concerns
- Can unit test business logic without API calls

---

## Phase 2: Code Quality Improvements (P1-P2)

### 2.1 Eliminate `safe_print()` Workaround

**Priority:** P1
**Effort:** Small (1 hour)
**Impact:** Medium - Cleaner code, consistent logging

**Current Issue:**
```python
# api_mapping.py - Lines 18-41
def safe_print(*args, **kwargs):
    """
    Safe print function that catches NoSessionContext errors.
    """
    try:
        import builtins
        builtins.print(*args, **kwargs)
    except Exception as e:
        if 'NoSessionContext' in str(type(e).__name__):
            # Extract message from args
            message = ' '.join(str(arg) for arg in args)
            # Clean ANSI color codes for logger
            import re
            clean_message = re.sub(r'\x1b\[[0-9;]+m', '', message)
            logger.debug(f"[print suppressed in async context] {clean_message}")
```

**Problems:**
- Workaround for architectural issue
- Inconsistent output (sometimes print, sometimes logger)
- ANSI color codes in production logs
- Hard to control verbosity

**Proposed Solution:**
Create a proper `OutputWriter` abstraction:

```python
class OutputWriter(ABC):
    """Abstract output writer for progress messages"""

    @abstractmethod
    def info(self, message: str):
        """Write info message"""
        pass

    @abstractmethod
    def warning(self, message: str):
        """Write warning message"""
        pass

    @abstractmethod
    def error(self, message: str):
        """Write error message"""
        pass

class StreamlitOutputWriter(OutputWriter):
    """Output writer for Streamlit UI"""

    def __init__(self, console_capture):
        self.console = console_capture

    def info(self, message: str):
        # Write to console capture (which handles NoSessionContext)
        self.console.write(message)

class LoggerOutputWriter(OutputWriter):
    """Output writer using Python logger"""

    def __init__(self, logger):
        self.logger = logger

    def info(self, message: str):
        self.logger.info(self._clean_ansi(message))

    def _clean_ansi(self, text: str) -> str:
        import re
        return re.sub(r'\x1b\[[0-9;]+m', '', text)
```

**Benefits:**
- Proper abstraction
- Easy to test
- Consistent behavior
- Can control output destination
- No workarounds needed

---

### 2.2 Break Down Large Functions

**Priority:** P2
**Effort:** Medium (3-4 hours)
**Impact:** Medium - Better readability, maintainability

**Large Functions to Refactor:**

1. **`PerformMapping()` (api_mapping.py: 439 lines)**
   - Split into: validate_inputs, prepare_prompt, call_api, parse_response

2. **`parse_optimized_response()` (api_mapping.py: 156 lines)**
   - Split into: extract_json, parse_json, repair_truncated_json

3. **`ProcessMappingResults()` (result_processor.py: 188 lines)**
   - Split into: extract_token_usage, process_mappings, calculate_statistics

**Example Refactoring:**

```python
# Before: One 439-line function
def PerformMapping(first_group, second_group, prompt, verbose=True, ...):
    # 439 lines of code
    pass

# After: Focused functions
class MappingService:
    def perform_mapping(self, first_group, second_group, prompt, config):
        """Orchestrate mapping process"""
        self._validate_inputs(first_group, second_group, prompt)
        api_prompt = self._prepare_prompt(first_group, second_group, prompt, config)
        response = self._call_api(api_prompt, config)
        mappings = self._parse_response(response, config)
        return self._create_result(mappings, response)

    def _validate_inputs(self, first_group, second_group, prompt):
        """Validate inputs (10 lines)"""
        pass

    def _prepare_prompt(self, first_group, second_group, prompt, config):
        """Prepare API prompt (30 lines)"""
        pass

    def _call_api(self, prompt, config):
        """Make API call with retry logic (40 lines)"""
        pass

    def _parse_response(self, response, config):
        """Parse and validate response (50 lines)"""
        pass
```

**Benefits:**
- Easy to understand each function
- Easy to test each piece independently
- Easy to reuse components
- Better error handling per step
- Improved maintainability

---

### 2.3 Standardize Error Handling

**Priority:** P2
**Effort:** Medium (2-3 hours)
**Impact:** Medium - Consistent error handling

**Current Issue:**
Mixed error handling patterns:
- Some functions return None on error
- Some functions raise exceptions
- Some functions print errors
- Inconsistent error messages

**Proposed Solution:**
Create custom exception hierarchy and consistent patterns:

```python
# exceptions.py
class MappingServiceError(Exception):
    """Base exception for mapping service"""
    pass

class ConfigurationError(MappingServiceError):
    """Invalid configuration"""
    pass

class APIError(MappingServiceError):
    """API-related errors"""
    def __init__(self, message: str, provider: str, model: str, original_error: Exception = None):
        super().__init__(message)
        self.provider = provider
        self.model = model
        self.original_error = original_error

class DataValidationError(MappingServiceError):
    """Data validation errors"""
    pass

class ParseError(MappingServiceError):
    """Response parsing errors"""
    pass

# Usage pattern
class MappingService:
    def perform_mapping(self, ...):
        try:
            # ... perform mapping
            return result
        except OpenAI.RateLimitError as e:
            raise APIError(
                "Rate limit exceeded",
                provider=config.provider,
                model=config.model,
                original_error=e
            )
        except json.JSONDecodeError as e:
            raise ParseError(f"Failed to parse API response: {e}")
```

**Benefits:**
- Consistent error handling
- Better error messages
- Easy to catch specific errors
- Can log structured error data
- Better user experience

---

## Phase 3: Testing Infrastructure (P2)

### 3.1 Add Unit Test Suite

**Priority:** P2
**Effort:** Large (8-10 hours)
**Impact:** High - Confidence in changes

**Proposed Structure:**
```
tests/
├── __init__.py
├── conftest.py              # Pytest fixtures
├── test_config.py           # Config tests
├── test_models.py           # Data model tests
├── test_result_processor.py # Result processor tests
├── test_mapping_service.py  # Mapping service tests
├── test_api_clients.py      # API client tests
├── test_batch_dispatcher.py # Batch processing tests
└── fixtures/
    ├── sample_data.json
    ├── sample_response.json
    └── sample_config.json
```

**Example Tests:**

```python
# tests/test_result_processor.py
import pytest
from models import MappingItem
from services.result_processor import ResultProcessor

@pytest.fixture
def processor():
    """Create fresh processor for each test"""
    return ResultProcessor()

def test_process_new_mapping(processor):
    """Test processing a new mapping"""
    mappings = [{
        "First Group Code": "LAB001",
        "First Group Name": "Complete Blood Count",
        "Second Group Code": "CBC",
        "Second Group Name": "CBC Test",
        "similarity score": 95,
        "reason for similarity score": "Exact match"
    }]

    result = processor.process_mappings(mappings, mock_response, 1.5)

    assert len(result['mappings']) == 1
    assert result['statistics']['unique_mappings'] == 1
    assert result['statistics']['mapped_count'] == 1

def test_deduplication_keeps_best_score(processor):
    """Test that deduplication keeps highest score"""
    mapping1 = {
        "First Group Code": "LAB001",
        "First Group Name": "Complete Blood Count",
        "Second Group Code": "CBC1",
        "Second Group Name": "CBC Test 1",
        "similarity score": 80,
        "reason for similarity score": "Good match"
    }
    mapping2 = {
        "First Group Code": "LAB001",
        "First Group Name": "Complete Blood Count",
        "Second Group Code": "CBC2",
        "Second Group Name": "CBC Test 2",
        "similarity score": 95,
        "reason for similarity score": "Better match"
    }

    processor.process_mappings([mapping1], mock_response1, 1.0)
    result = processor.process_mappings([mapping2], mock_response2, 1.0)

    # Should keep the better score (95)
    df = processor.get_dataframes()['ApiMapping']
    assert len(df) == 1
    assert df.iloc[0]['Similarity Score'] == 95
    assert df.iloc[0]['Second Group Code'] == 'CBC2'
```

**Benefits:**
- Confidence in refactoring
- Catch regressions early
- Document expected behavior
- Enable safe refactoring
- Improve code quality

---

### 3.2 Add Integration Tests

**Priority:** P2
**Effort:** Medium (4-5 hours)
**Impact:** Medium - Catch integration issues

**Test Scenarios:**
1. End-to-end mapping with mock API
2. Batch processing with concurrency
3. Rate limiting behavior
4. Error recovery and retry
5. Deduplication across batches

```python
# tests/integration/test_end_to_end.py
def test_complete_mapping_workflow():
    """Test complete mapping workflow"""
    # Setup
    config = AppConfig.default()
    processor = ResultProcessor()
    api_client = MockAPIClient()  # Mock that returns realistic responses
    service = MappingService(api_client, processor)

    # Load test data
    first_group = load_fixture('first_group.json')
    second_group = load_fixture('second_group.json')
    prompt = load_fixture('prompt.txt')

    # Execute
    result = service.perform_mapping(first_group, second_group, prompt, config)

    # Verify
    assert result is not None
    assert len(result['mappings']) > 0
    assert result['statistics']['unique_mappings'] > 0
```

---

## Phase 4: Performance & Scalability (P3)

### 4.1 Add Caching Layer

**Priority:** P3
**Effort:** Medium (3-4 hours)
**Impact:** Medium - Reduce API costs, faster retries

**Proposed Solution:**
Add caching for API responses:

```python
class CachedMappingService:
    """Mapping service with caching"""

    def __init__(self, service: MappingService, cache: Cache):
        self.service = service
        self.cache = cache

    def perform_mapping(self, first_group, second_group, prompt, config):
        """Perform mapping with caching"""
        cache_key = self._generate_cache_key(first_group, second_group, prompt, config)

        # Check cache
        cached = self.cache.get(cache_key)
        if cached:
            logger.info(f"Cache hit for {cache_key}")
            return cached

        # Call service
        result = self.service.perform_mapping(first_group, second_group, prompt, config)

        # Store in cache
        self.cache.set(cache_key, result, ttl=3600)  # 1 hour

        return result
```

**Benefits:**
- Reduce API costs on retries
- Faster development/testing
- Can replay past runs
- Useful for debugging

---

### 4.2 Add Progress Tracking Database

**Priority:** P3
**Effort:** Large (6-8 hours)
**Impact:** Medium - Better resume capability

**Proposed Solution:**
Store progress in SQLite database:

```python
class ProcessingDatabase:
    """SQLite database for tracking processing progress"""

    def __init__(self, db_path: str):
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS batch_runs (
                id INTEGER PRIMARY KEY,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                total_batches INTEGER,
                status TEXT
            )
        """)

        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS batch_results (
                id INTEGER PRIMARY KEY,
                run_id INTEGER,
                batch_index INTEGER,
                status TEXT,
                mappings_count INTEGER,
                completed_at TIMESTAMP,
                FOREIGN KEY (run_id) REFERENCES batch_runs(id)
            )
        """)

    def create_run(self, total_batches: int) -> int:
        """Create new processing run"""
        cursor = self.conn.execute(
            "INSERT INTO batch_runs (started_at, total_batches, status) VALUES (?, ?, ?)",
            (datetime.now(), total_batches, 'running')
        )
        return cursor.lastrowid

    def get_completed_batches(self, run_id: int) -> Set[int]:
        """Get set of completed batch indices"""
        cursor = self.conn.execute(
            "SELECT batch_index FROM batch_results WHERE run_id = ? AND status = 'completed'",
            (run_id,)
        )
        return {row[0] for row in cursor.fetchall()}
```

**Benefits:**
- Resume interrupted processing
- Track historical runs
- Analyze performance trends
- Better error recovery

---

## Phase 5: Documentation & Developer Experience (P2-P3)

### 5.1 Add Type Hints Throughout

**Priority:** P2
**Effort:** Medium (4-5 hours)
**Impact:** Medium - Better IDE support, fewer bugs

**Current State:**
Some modules have type hints, many don't

**Proposed:**
Add complete type hints to all modules:

```python
# Before
def perform_mapping(first_group, second_group, prompt, verbose=True):
    pass

# After
def perform_mapping(
    first_group: List[Dict[str, Any]],
    second_group: List[Dict[str, Any]],
    prompt: str,
    verbose: bool = True,
    config: Optional[AppConfig] = None
) -> Optional[MappingResult]:
    pass
```

**Benefits:**
- Better IDE autocomplete
- Catch type errors early (with mypy)
- Self-documenting code
- Easier refactoring

---

### 5.2 Add API Documentation

**Priority:** P3
**Effort:** Small (2-3 hours)
**Impact:** Low - Better documentation

**Proposed:**
Add Sphinx documentation or mkdocs:

```
docs/
├── index.md
├── api/
│   ├── config.md
│   ├── models.md
│   ├── services.md
│   └── batch_processing.md
├── guides/
│   ├── getting_started.md
│   ├── configuration.md
│   └── troubleshooting.md
└── architecture.md
```

---

## Implementation Strategy

### Recommended Order:

1. **Phase 1 (P1 - Architecture)** - Foundation for everything else
   - 1.1 ResultProcessor class (2-3 hours)
   - 1.2 AppConfig dataclass (2-3 hours)
   - 1.3 Separate API clients (3-4 hours)
   - **Total: 7-10 hours**

2. **Phase 2 (P1-P2 - Code Quality)** - Clean up while refactoring
   - 2.1 OutputWriter abstraction (1 hour)
   - 2.2 Break down large functions (3-4 hours)
   - 2.3 Standardize error handling (2-3 hours)
   - **Total: 6-8 hours**

3. **Phase 3 (P2 - Testing)** - Ensure quality
   - 3.1 Unit test suite (8-10 hours)
   - 3.2 Integration tests (4-5 hours)
   - **Total: 12-15 hours**

4. **Phase 4 (P3 - Performance)** - Optional optimizations
   - 4.1 Caching layer (3-4 hours)
   - 4.2 Progress database (6-8 hours)
   - **Total: 9-12 hours**

5. **Phase 5 (P2-P3 - Documentation)** - Polish
   - 5.1 Type hints (4-5 hours)
   - 5.2 API documentation (2-3 hours)
   - **Total: 6-8 hours**

### Total Effort Estimate:
- **Phase 1-2 (Critical)**: 13-18 hours
- **Phase 3 (Important)**: 12-15 hours
- **Phase 4-5 (Optional)**: 15-20 hours
- **Grand Total**: 40-53 hours

---

## Risk Assessment

### Low Risk Refactorings:
- Adding type hints (doesn't change behavior)
- Adding tests (validates current behavior)
- Documentation (no code changes)

### Medium Risk Refactorings:
- Breaking down large functions (behavior must stay same)
- Standardizing error handling (changes error flow)
- Adding caching (must not affect correctness)

### High Risk Refactorings:
- Converting global state to instances (major architectural change)
- Separating API clients (touches core functionality)
- Converting Config to instances (used everywhere)

### Risk Mitigation:
1. **Write tests first** for critical functions
2. **Incremental migration** - keep backward compatibility
3. **Feature flags** - enable new code gradually
4. **Comprehensive testing** after each phase
5. **Git branches** - one phase per branch
6. **Code review** - have another developer review

---

## Success Criteria

### Phase 1 Complete When:
- [ ] `ResultProcessor` class implemented and tested
- [ ] All callers migrated to use `ResultProcessor` instance
- [ ] `AppConfig` dataclass implemented with validation
- [ ] All `Config.x` references updated to use instance
- [ ] API clients separated into focused modules
- [ ] Zero regression in functionality
- [ ] All existing features work as before

### Phase 2 Complete When:
- [ ] All large functions broken down to <100 lines
- [ ] `safe_print()` removed, replaced with `OutputWriter`
- [ ] Custom exception hierarchy in place
- [ ] All error handling follows consistent pattern
- [ ] Code passes linting (pylint, flake8)

### Phase 3 Complete When:
- [ ] 80%+ unit test coverage on core logic
- [ ] Integration tests for main workflows
- [ ] All tests passing
- [ ] Tests run in CI/CD pipeline

### Phase 4 Complete When:
- [ ] Caching layer implemented (optional)
- [ ] Progress database implemented (optional)
- [ ] Performance metrics show improvement

### Phase 5 Complete When:
- [ ] All public functions have type hints
- [ ] mypy passes with no errors
- [ ] API documentation generated
- [ ] Developer guide written

---

## Backward Compatibility

### Maintaining Compatibility:

```python
# Example: Gradual migration with deprecation warnings

# Old global function (deprecated)
def ProcessMappingResults(mappings, response, elapsed_time, verbose=True, reset_before_processing=True):
    """
    DEPRECATED: Use ResultProcessor class instead.

    This function will be removed in v3.0
    """
    import warnings
    warnings.warn(
        "ProcessMappingResults() is deprecated, use ResultProcessor.process_mappings() instead",
        DeprecationWarning,
        stacklevel=2
    )

    # Use new implementation internally
    processor = _get_global_processor()
    return processor.process_mappings(mappings, response, elapsed_time, verbose)

# Helper for backward compatibility
_global_processor = None
def _get_global_processor():
    global _global_processor
    if _global_processor is None:
        _global_processor = ResultProcessor()
    return _global_processor
```

---

## Rollback Plan

If refactoring causes issues:

1. **Git revert** - Immediate rollback to previous version
2. **Feature flags** - Disable new code, use old code path
3. **Hot fix** - Fix critical issues in refactored code
4. **Incremental rollback** - Rollback one phase at a time

---

## Monitoring During Refactoring

Track these metrics:

1. **Functionality**
   - Processing success rate (should stay 100%)
   - Average batch time (should stay ~11.7 seconds)
   - Total processing time (should stay ~35 minutes for 180 batches)

2. **Code Quality**
   - Lines of code per function (target: <100)
   - Test coverage (target: >80%)
   - Cyclomatic complexity (target: <10 per function)
   - Number of global variables (target: 0)

3. **Performance**
   - Memory usage
   - CPU usage
   - API latency

---

## Questions to Answer Before Starting

1. **Do we need backward compatibility?**
   - If yes, use deprecation warnings and gradual migration
   - If no, can do breaking changes faster

2. **What's the testing strategy?**
   - Write tests before refactoring? (safer)
   - Write tests after refactoring? (faster)
   - Hybrid approach?

3. **Can we pause feature development?**
   - Refactoring is easier without parallel features
   - Need to coordinate with team

4. **What's the timeline?**
   - 1-2 weeks for Phase 1-2 (critical)?
   - 3-4 weeks for Phase 1-3 (important)?
   - 6-8 weeks for all phases (complete)?

---

## Next Steps

1. **Review this plan** with team/stakeholders
2. **Prioritize phases** based on needs
3. **Create git branch** for refactoring work
4. **Write initial tests** for critical functions
5. **Start with Phase 1.1** (ResultProcessor)
6. **Incremental progress** with frequent commits

---

## Conclusion

This refactoring plan addresses:
- ✅ **Architecture**: Eliminate global state, proper abstractions
- ✅ **Code Quality**: Break down large functions, consistent patterns
- ✅ **Testing**: Comprehensive test suite
- ✅ **Performance**: Caching, progress tracking
- ✅ **Documentation**: Type hints, API docs

The current system is production-ready (100% success rate). These refactorings focus on **long-term maintainability and scalability** rather than fixing bugs.

**Recommended Start:** Phase 1 (Architecture) - Foundation for everything else

---

**Document Version:** 2.0
**Last Updated:** January 15, 2026
**Status:** Ready for Review
