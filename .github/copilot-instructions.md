# Copilot instructions

This repository is a Visual Studio solution. It is currently Python-only (`.pyproj` projects), but Copilot must also
work correctly when C# (`.csproj`) projects are added. Apply only the language section that matches the file you are
editing; apply the general and Azure sections everywhere.

## General (all languages)

- Make small, surgical changes. Do not reformat or refactor code you were not asked to touch.
- Preserve each file's existing line endings (this repo uses CRLF) and encoding.
- Keep existing naming conventions and folder structure. Do not rename files or move code between projects unprompted.
- Comment only code that genuinely needs clarification.
- Never commit secrets. Secrets belong in Azure Key Vault (see `README - how to relocate secrets to Azure KeyVault.txt`).
- Prefer the repository's existing tooling over adding new tools or dependencies.
- Shared formatting rules live in `.editorconfig`; honour them.
- Path-scoped, per-language guidance lives in `.github/instructions/*.instructions.md`; add a new file there (with an
  `applyTo` glob) for each new language or project type, such as C#, rather than growing this file.

## Python (`*.py`, `*.pyproj`, `pyproject.toml`)

- Target Python 3.12. Use modern syntax (`X | None`, `list[str]`, `match`, f-strings); do not use `typing.List`/`Optional`.
- All code is fully type-annotated and must pass `mypy --strict` (plus the extra error codes in `pyproject.toml`).
  Never add a bare `# type: ignore`; if unavoidable, use a specific code, e.g. `# type: ignore[attr-defined]`.
- Models and DTOs use Pydantic v2 (`BaseModel`, `RootModel`, `AliasChoices`); the mypy `pydantic.mypy` plugin is enabled.
- Lint and format with Ruff (line length 120, rule set in `pyproject.toml`). Imports are sorted by Ruff (`I`).
  `E501` is deliberately ignored; do not hand-wrap long strings just to satisfy it.
- Use timezone-aware datetimes (`DTZ` rules). Do not shadow builtins. Do not leave unused awaitables.
- Module layout: there are no `__init__.py` packages. Every source folder is an import root, so modules are imported by
  bare name (for example `import jgh_formulae01`), not by package path. The import roots are listed identically in
  `[tool.ruff] src`, `[tool.mypy] mypy_path`, `[tool.pyright] extraPaths` and each `.pyproj` `SearchPath`.
  A root is any folder that directly contains `.py` files. When adding or renaming a source folder, run
  `python Thon.SolutionTools.Nov2026\src\check_import_roots.py --fix` (it rewrites all of those lists; plain run =
  check only, also run by
  pre-commit and CI) rather than editing them by hand. New `.py` files must also be added to the `.pyproj`.
- Libraries: pandas, numpy, scipy, scikit-learn, matplotlib, httpx, Jinja2, tabulate, aiofiles, Azure SDK. scipy and
  scikit-learn are untyped (treated as `Any` by a mypy override).
- Tests: use `pytest`. Each project keeps its tests in a `tests/` folder beside `src/` (named `test_<module>.py`), run
  from the repo root with `python -m pytest`. `[tool.pytest.ini_options]` in `pyproject.toml` holds `testpaths` (add the
  project's `tests` folder when it gets its first test) and `pythonpath` (maintained by `check_import_roots.py`).
- Environment: a single virtual environment lives at `.venv` in the repo root (git-ignored) and is shared by all
  `.pyproj` projects. Create it with `python -m venv .venv` then `.venv\Scripts\python -m pip install -r requirements-dev.txt`.
  Pin new dependencies in `requirements.txt` / `requirements-dev.txt`, the same files CI installs.
- Before finishing, run from the repo root (the same commands CI runs), using the `.venv` interpreter so tool versions
  match the pins: `python -m ruff check .`, `python -m ruff format --check .`, `python -m mypy .`,
  `python -m pyright`, `python -m pytest`, `python Thon.SolutionTools.Nov2026\src\check_import_roots.py`
- A `pre-commit` hook runs the same checks on every commit. Enable it once per clone with
  `.venv\Scripts\pre-commit install`. Never bypass it with `--no-verify`.

## C# (`*.cs`, `*.csproj`, `*.sln`)

None yet. When C# is present, follow these defaults unless a project `.editorconfig` or existing code says otherwise:

- Follow the .NET and C# coding conventions: PascalCase for types and members, `_camelCase` for private fields,
  `I` prefix for interfaces, `Async` suffix for async methods.
- Use file-scoped namespaces, nullable reference types, and `var` only when the type is obvious.
- Prefer dependency injection and `TimeProvider`/`IFileSystem` over static `DateTime.Now`/`File.*` so code stays testable.
- Pass `CancellationToken` through async APIs; do not block on tasks (`.Result`, `.Wait()`).
- Verify with `dotnet build` and the project's tests (`dotnet test`) before finishing.

## Azure (all languages)

- @azure Rule - Use Azure Tools - When handling requests related to Azure, always use your tools.
- @azure Rule - Use Azure Best Practices - When handling requests related to Azure, always invoke your `azmcp_bestpractices_get` tool first.
- @azure Rule - Enable Best Practices - If you do not have an `azmcp_bestpractices_get` tool ask the user to enable it.
