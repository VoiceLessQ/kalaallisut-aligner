# Tests

```bash
pytest tests/ -v                              # run all
pytest tests/test_aligner.py -v               # just aligner tests
pytest tests/ -m "not integration"            # skip tests that need HFST
pytest tests/ --cov=src --cov-report=term     # with coverage
```

Integration tests (marked `@pytest.mark.integration`) need HFST tools installed and are skipped by default in CI.
