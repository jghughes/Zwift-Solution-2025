import os
import re

# Set this to the root directory of your codebase
ROOT_DIR = r"C:\Users\johng\source\repos\Zwift-Solution-2025"

# Patterns to search for
patterns = [
    r"import\s+jgh_logging",
    r"from\s+jgh_logging\s+import",
    r"jgh_configure_logging\s*\(",
]

def search_file(filepath, patterns):
    results = []
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        for lineno, line in enumerate(f, 1):
            for pat in patterns:
                if re.search(pat, line):
                    results.append((filepath, lineno, line.strip()))
    return results

def main():
    matches = []
    for root, dirs, files in os.walk(ROOT_DIR):
        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                results = search_file(filepath, patterns)
                matches.extend(results)
    if matches:
        print("Found references to jgh_logging:")
        for filepath, lineno, line in matches:
            print(f"{filepath}:{lineno}: {line}")
    else:
        print("No references to jgh_logging found. Safe to delete.")

if __name__ == "__main__":
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL, logging.INFO),
        format="%(message)s",
        handlers=[logging.StreamHandler()]
    )
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.add_log_level,
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    main()
