from pathlib import Path


DEFAULT_IGNORED_NAMES = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    "dist",
    "build",
}


def should_ignore(
    path: Path,
    ignored_names: set[str] | None = None,
) -> bool:
    names = {
        name.lower()
        for name in (
            ignored_names
            or DEFAULT_IGNORED_NAMES
        )
    }

    return any(
        part.lower() in names
        for part in path.parts
    )