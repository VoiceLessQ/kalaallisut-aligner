# Tests

Comprehensive test suite for the Kalaallisut-Danish Sentence Aligner.

## Running Tests

### Run all tests
```bash
pytest tests/ -v
```

### Run with coverage report
```bash
pytest tests/ --cov=src --cov=glosser --cov-report=html --cov-report=term
```

### Run specific test file
```bash
pytest tests/test_utils.py -v
pytest tests/test_aligner.py -v
pytest tests/test_preprocessor.py -v
```

### Run tests with markers
```bash
# Skip integration tests (tests that require HFST tools)
pytest tests/ -v -m "not integration"

# Run only integration tests
pytest tests/ -v -m "integration"
```

## Test Structure

- `conftest.py` - Shared fixtures and configuration
- `test_aligner.py` - Tests for sentence alignment
- `test_utils.py` - Tests for utility functions
- `test_preprocessor.py` - Tests for preprocessing and morphology
- `README.md` - This file

## Coverage Goals

Target: >80% code coverage for all modules

Current coverage:
```bash
pytest tests/ --cov=src --cov=glosser --cov-report=term-missing
```

## Adding New Tests

When adding new tests:
1. Follow existing naming conventions (`test_*.py`)
2. Use descriptive test names (`test_function_does_something`)
3. Group related tests in classes
4. Add docstrings explaining what each test checks
5. Use fixtures from conftest.py for common setup
6. Mark integration tests with `@pytest.mark.integration`

## Continuous Integration

Tests run automatically on GitHub Actions for:
- Every push to any branch
- Every pull request

See `.github/workflows/test.yml` for CI configuration.
