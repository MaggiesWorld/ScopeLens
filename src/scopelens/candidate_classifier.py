from pathlib import Path


SOURCE_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".java",
    ".cs",
    ".cpp",
    ".c",
    ".go",
    ".rs",
}

CONFIG_EXTENSIONS = {
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".xml",
}

DOCUMENTATION_EXTENSIONS = {
    ".md",
    ".rst",
    ".txt",
}

DATA_EXTENSIONS = {
    ".csv",
    ".xlsx",
    ".xls",
    ".parquet",
}

BINARY_EXTENSIONS = {
    ".exe",
    ".dll",
    ".so",
    ".bin",
}


def classify_candidate(path: Path) -> str:
    extension = path.suffix.lower()
    name = path.name.lower()

    if "test" in name:
        return "test"

    if extension in SOURCE_EXTENSIONS:
        return "source"

    if extension in CONFIG_EXTENSIONS:
        return "configuration"

    if extension in DOCUMENTATION_EXTENSIONS:
        return "documentation"

    if extension in DATA_EXTENSIONS:
        return "data"

    if extension in BINARY_EXTENSIONS:
        return "binary"

    return "unknown"