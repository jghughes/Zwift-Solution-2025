"""Verify (or with --fix, rewrite) every copy of the import-root list.

Source roots are derived from the file system: every folder that directly contains .py files.
That list must be identical in these places, because none of the tools can share it:

* [tool.ruff] src
* [tool.mypy] mypy_path
* [tool.pyright] extraPaths
* [tool.pytest.ini_options] pythonpath (only if present)
* <SearchPath> in every .pyproj

Usage (from anywhere): python tools/check_import_roots.py [--fix]
Exit code 0 = all copies match, 1 = drift found (or fixed, with --fix).
"""

import os
import re
import sys
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PYPROJECT = REPO_ROOT / "pyproject.toml"
MYPY_PREFIX = "$MYPY_CONFIG_FILE_DIR/"
SEARCH_PATH_RE = re.compile(r"(<SearchPath>)(.*?)(</SearchPath>)", re.DOTALL)
# This folder holds repo tooling, not importable application modules.
EXCLUDED_DIRS = {"tools", "node_modules", "__pycache__"}


def discover_roots() -> list[str]:
    roots: list[str] = []
    for current, dirs, files in os.walk(REPO_ROOT):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in EXCLUDED_DIRS]
        folder = Path(current)
        if folder != REPO_ROOT and any(f.endswith(".py") for f in files):
            roots.append(folder.relative_to(REPO_ROOT).as_posix())
    return sorted(roots)


def read_toml_lists() -> dict[str, list[str]]:
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    tool = data["tool"]
    found = {
        "[tool.ruff] src": list(tool["ruff"]["src"]),
        "[tool.mypy] mypy_path": [p.removeprefix(MYPY_PREFIX) for p in tool["mypy"]["mypy_path"]],
        "[tool.pyright] extraPaths": list(tool["pyright"]["extraPaths"]),
    }
    pythonpath = tool.get("pytest", {}).get("ini_options", {}).get("pythonpath")
    if pythonpath is not None:
        found["[tool.pytest.ini_options] pythonpath"] = list(pythonpath)
    return found


def read_pyproj_lists() -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for pyproj in sorted(REPO_ROOT.glob("*/*.pyproj")):
        match = SEARCH_PATH_RE.search(pyproj.read_text(encoding="utf-8-sig"))
        entries = match.group(2).split(";") if match else []
        resolved = [
            (pyproj.parent / e.strip()).resolve().relative_to(REPO_ROOT).as_posix() for e in entries if e.strip()
        ]
        found[f"{pyproj.name} SearchPath"] = resolved
    return found


def pyproj_search_path(pyproj: Path, roots: list[str]) -> str:
    own = [r for r in roots if (REPO_ROOT / r).is_relative_to(pyproj.parent)]
    others = [r for r in roots if r not in own]
    return ";".join(os.path.relpath(REPO_ROOT / r, pyproj.parent) for r in own + others)


def replace_search_path(content: str, search_path: str) -> str:
    return SEARCH_PATH_RE.sub(lambda m: m.group(1) + search_path + m.group(3), content)


def rewrite_toml_array(text: str, key: str, roots: list[str], prefix: str) -> str:
    newline = "\r\n" if "\r\n" in text else "\n"
    items = "".join(f'    "{prefix}{r}",{newline}' for r in roots)
    pattern = re.compile(rf"(^{re.escape(key)} = \[\r?\n)(.*?)(^\])", re.MULTILINE | re.DOTALL)
    new_text, count = pattern.subn(lambda m: m.group(1) + items + m.group(3), text, count=1)
    if count != 1:
        raise SystemExit(f"Cannot find a multi-line '{key} = [' array in pyproject.toml")
    return new_text


def fix(roots: list[str], toml_lists: dict[str, list[str]]) -> None:
    text = PYPROJECT.read_bytes().decode("utf-8")
    text = rewrite_toml_array(text, "src", roots, "")
    text = rewrite_toml_array(text, "mypy_path", roots, MYPY_PREFIX)
    text = rewrite_toml_array(text, "extraPaths", roots, "")
    if "[tool.pytest.ini_options] pythonpath" in toml_lists:
        text = rewrite_toml_array(text, "pythonpath", roots, "")
    PYPROJECT.write_bytes(text.encode("utf-8"))

    for pyproj in sorted(REPO_ROOT.glob("*/*.pyproj")):
        raw = pyproj.read_bytes()
        content = raw.decode("utf-8-sig")
        updated = replace_search_path(content, pyproj_search_path(pyproj, roots))
        if updated != content:
            bom = b"\xef\xbb\xbf" if raw.startswith(b"\xef\xbb\xbf") else b""
            pyproj.write_bytes(bom + updated.encode("utf-8"))


def find_drift(roots: list[str]) -> list[str]:
    problems: list[str] = []
    expected = set(roots)
    for name, paths in {**read_toml_lists(), **read_pyproj_lists()}.items():
        actual = set(paths)
        if missing := sorted(expected - actual):
            problems.append(f"{name}: missing {missing}")
        if extra := sorted(actual - expected):
            problems.append(f"{name}: unexpected {extra}")
        if len(paths) != len(actual):
            problems.append(f"{name}: contains duplicate entries")
    return problems


def main(argv: list[str]) -> int:
    roots = discover_roots()
    problems = find_drift(roots)
    if not problems:
        print(f"Import roots in sync ({len(roots)} roots).")
        return 0
    if "--fix" not in argv:
        print("Import roots have drifted from the folders that contain .py files:")
        for problem in problems:
            print(f"  - {problem}")
        print("Run: python tools/check_import_roots.py --fix")
        return 1
    fix(roots, read_toml_lists())
    remaining = find_drift(roots)
    if remaining:
        print("Could not fix:\n  - " + "\n  - ".join(remaining))
        return 1
    print(f"Fixed {len(problems)} drifted list(s). Review the diff.")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
