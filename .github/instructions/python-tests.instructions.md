---
applyTo: "**/test_*.py,**/*_test.py,**/tests/**/*.py"
---

# Python tests

- Use `pytest` (the `.pyproj` `TestFramework` is `Pytest`); write plain functions and `assert`, not `unittest.TestCase`.
- Tests are fully type-annotated and must pass `mypy --strict` like production code.
- No real network, Azure or clock access: use `httpx.MockTransport`, `tmp_path` and fixed timezone-aware datetimes.
- Source folders are import roots without packages, so import modules by bare name.
- Add new test files to the owning `.pyproj`.
