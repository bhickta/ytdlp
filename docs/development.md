# Development Guide

## Setup Development Environment

### Prerequisites

- Python 3.11+
- Git
- UV (recommended) or pip

### Clone and Install

```bash
# Clone repository
git clone <repository-url>
cd ytdlp

# Create virtual environment with uv
uv venv
source .venv/bin/activate

# Install with dev dependencies
uv pip install -e ".[dev]"
```

### Dev Dependencies

- **ruff** - Fast linter
- **black** - Code formatter
- **isort** - Import sorter
- **mypy** - Type checker
- **pytest** - Testing framework
- **pytest-cov** - Coverage reporting

## Code Quality

### Linting

```bash
# Check code
ruff check src/

# Auto-fix issues
ruff check --fix src/
```

### Formatting

```bash
# Format code
black src/

# Check formatting
black --check src/
```

### Import Sorting

```bash
# Sort imports
isort src/

# Check imports
isort --check src/
```

### Type Checking

```bash
# Run mypy
mypy src/
```

### All Checks

```bash
# Run everything
ruff check src/ && black --check src/ && isort --check src/ && mypy src/
```

## Testing

### Run Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=ytdlp_subs --cov-report=term-missing

# HTML coverage report
pytest --cov=ytdlp_subs --cov-report=html
# Open htmlcov/index.html

# Verbose output
pytest -v

# Specific test file
pytest tests/test_models.py

# Specific test
pytest tests/test_models.py::test_video_id_validation
```

### Writing Tests

**Test structure:**
```
tests/
├── unit/
│   ├── test_models.py
│   ├── test_services.py
│   └── test_repositories.py
├── integration/
│   └── test_orchestrator.py
└── conftest.py
```

**Example unit test:**
```python
# tests/unit/test_models.py
import pytest
from ytdlp_subs.domain.models import VideoId

def test_video_id_valid():
    vid = VideoId("dQw4w9WgXcQ")
    assert str(vid) == "dQw4w9WgXcQ"
    assert vid.url == "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

def test_video_id_invalid():
    with pytest.raises(ValueError):
        VideoId("invalid")
```

**Example integration test:**
```python
# tests/integration/test_orchestrator.py
import pytest
from ytdlp_subs.application.use_cases.download_orchestrator import DownloadOrchestrator

@pytest.fixture
def mock_repositories():
    # Create mock repositories
    pass

def test_download_orchestrator(mock_repositories):
    orchestrator = DownloadOrchestrator(...)
    progress = orchestrator.execute("channel_url")
    assert progress.total_videos > 0
```

## Project Structure

```
ytdlp/
├── src/ytdlp_subs/
│   ├── domain/              # Core business logic
│   ├── application/         # Use cases
│   ├── infrastructure/      # External concerns
│   └── presentation/        # User interface
├── tests/                   # Test suite
├── docs/                    # Documentation
├── pyproject.toml          # Project config
└── README.md               # Main readme
```

## Contributing

### Workflow

1. **Create branch**
   ```bash
   git checkout -b feature/my-feature
   ```

2. **Make changes**
   - Follow SOLID principles
   - Add type hints
   - Write tests
   - Update docs

3. **Run checks**
   ```bash
   ruff check src/
   black src/
   isort src/
   mypy src/
   pytest
   ```

4. **Commit**
   ```bash
   git add .
   git commit -m "feat: add my feature"
   ```

5. **Push and PR**
   ```bash
   git push origin feature/my-feature
   # Create pull request on GitHub
   ```

### Commit Messages

Follow conventional commits:

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `refactor:` - Code refactoring
- `test:` - Tests
- `chore:` - Maintenance

**Examples:**
```
feat: add Portuguese language support
fix: handle missing subtitle gracefully
docs: update usage guide with examples
refactor: extract filename generation logic
test: add unit tests for VideoId
chore: update dependencies
```

## Adding Features

### Add New Language

1. **Update enum:**
   ```python
   # src/ytdlp_subs/domain/models.py
   class SubtitleLanguage(str, Enum):
       # ... existing
       PORTUGUESE = "pt"
   ```

2. **Add test:**
   ```python
   def test_portuguese_language():
       lang = SubtitleLanguage.PORTUGUESE
       assert lang.value == "pt"
   ```

3. **Update docs:**
   - Add to supported languages list
   - Add example usage

### Add New File Processor

1. **Create service:**
   ```python
   # src/ytdlp_subs/application/services/my_processor.py
   class MyProcessor(IFileProcessorService):
       def process_file(self, input_file: Path) -> Path:
           # Implementation
           return output_file
   ```

2. **Add to container:**
   ```python
   # src/ytdlp_subs/application/container.py
   @property
   def my_processor(self) -> MyProcessor:
       if self._my_processor is None:
           self._my_processor = MyProcessor()
       return self._my_processor
   ```

3. **Add tests:**
   ```python
   def test_my_processor():
       processor = MyProcessor()
       result = processor.process_file(input_file)
       assert result.exists()
   ```

## Debugging

### Enable Debug Logging

```bash
ytdlp-subs "URL" --log-level DEBUG --log-file debug.log
```

### Use Python Debugger

```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or use built-in breakpoint()
breakpoint()
```

### Common Issues

**Import errors:**
```bash
# Reinstall in editable mode
uv pip install -e .
```

**Type errors:**
```bash
# Check with mypy
mypy src/ytdlp_subs/path/to/file.py
```

## Performance

### Profiling

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# Your code here

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)
```

### Memory Profiling

```bash
pip install memory-profiler

# Add @profile decorator to function
python -m memory_profiler script.py
```

## Release Process

1. **Update version**
   ```python
   # src/ytdlp_subs/__init__.py
   __version__ = "1.1.0"
   
   # pyproject.toml
   version = "1.1.0"
   ```

2. **Update changelog**
   ```markdown
   # CHANGELOG.md
   ## [1.1.0] - 2026-01-29
   ### Added
   - New feature X
   ### Fixed
   - Bug Y
   ```

3. **Tag release**
   ```bash
   git tag -a v1.1.0 -m "Release v1.1.0"
   git push origin v1.1.0
   ```

4. **Build and publish**
   ```bash
   # Build
   python -m build
   
   # Publish to PyPI
   python -m twine upload dist/*
   ```

## Resources

- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Pytest Documentation](https://docs.pytest.org/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
