import ast
import json
import tomllib
import configparser
import csv
import xml.etree.ElementTree as ET
from pathlib import Path

MAX_PARSE_CHARS = 100_000


def extract_python_facts(
    path: Path,
) -> dict:
    content = path.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    if len(content) > MAX_PARSE_CHARS:
        return {
            "imports": [],
            "functions": [],
            "classes": [],
            "test_functions": [],
            "test_classes": [],
            "contains_tests": False,
            "extraction_status": "skipped",
            "extraction_reason": "file_too_large",
        }

    try:
        tree = ast.parse(content)
    except (SyntaxError, MemoryError):
        return {
            "imports": [],
            "functions": [],
            "classes": [],
            "test_functions": [],
            "test_classes": [],
            "contains_tests": False,
            "extraction_status": "failed",
            "extraction_reason": "parse_error",
        }

    functions: list[str] = []
    classes: list[str] = []
    imports: list[str] = []
    test_functions: list[str] = []
    test_classes: list[str] = []

    for node in ast.walk(tree):
        if isinstance(
            node,
            (ast.FunctionDef, ast.AsyncFunctionDef),
        ):
            functions.append(node.name)

            if node.name.startswith("test_"):
                test_functions.append(node.name)

        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)

            if node.name.startswith("Test"):
                test_classes.append(node.name)

        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)

    return {
        "imports": sorted(set(imports)),
        "functions": sorted(functions),
        "classes": sorted(classes),
        "test_functions": sorted(test_functions),
        "test_classes": sorted(test_classes),
        "contains_tests": bool(
            test_functions
            or test_classes
        ),
        "extraction_status": "success",
        "extraction_reason": None,
    }

def extract_json_facts(
    path: Path,
) -> dict:
    content = path.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    if len(content) > MAX_PARSE_CHARS:
        return {
            "top_level_keys": [],
            "root_type": None,
            "extraction_status": "skipped",
            "extraction_reason": "file_too_large",
            "item_count": None,
        }

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return {
            "top_level_keys": [],
            "root_type": None,
            "item_count": None,
            "extraction_status": "failed",
            "extraction_reason": "parse_error",
        }

    top_level_keys = (
        sorted(data.keys())
        if isinstance(data, dict)
        else []
    )

    return {
        "top_level_keys": top_level_keys,
        "root_type": type(data).__name__,
        "item_count": (
            len(data)
            if isinstance(data, (dict, list))
            else None
        ),
        "extraction_status": "success",
        "extraction_reason": None,
    }

def extract_ini_facts(
    path: Path,
) -> dict:
    content = path.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    if len(content) > MAX_PARSE_CHARS:
        return {
            "sections": [],
            "section_count": None,
            "extraction_status": "skipped",
            "extraction_reason": "file_too_large",
        }

    parser = configparser.ConfigParser()

    try:
        parser.read_string(content)
    except configparser.Error:
        return {
            "sections": [],
            "section_count": None,
            "extraction_status": "failed",
            "extraction_reason": "parse_error",
        }

    sections = parser.sections()

    return {
        "sections": sorted(sections),
        "section_count": len(sections),
        "extraction_status": "success",
        "extraction_reason": None,
    }

def extract_toml_facts(
    path: Path,
) -> dict:
    content = path.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    if len(content) > MAX_PARSE_CHARS:
        return {
            "top_level_keys": [],
            "item_count": None,
            "extraction_status": "skipped",
            "extraction_reason": "file_too_large",
        }

    try:
        data = tomllib.loads(content)
    except tomllib.TOMLDecodeError:
        return {
            "top_level_keys": [],
            "item_count": None,
            "extraction_status": "failed",
            "extraction_reason": "parse_error",
        }

    return {
        "top_level_keys": sorted(data.keys()),
        "item_count": len(data),
        "extraction_status": "success",
        "extraction_reason": None,
    }

def extract_csv_facts(
    path: Path,
) -> dict:
    content = path.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    if len(content) > MAX_PARSE_CHARS:
        return {
            "columns": [],
            "row_count": None,
            "extraction_status": "skipped",
            "extraction_reason": "file_too_large",
        }

    try:
        rows = list(
            csv.reader(
                content.splitlines(),
                strict=True,
            )
        )
    except csv.Error:
        return {
            "columns": [],
            "row_count": None,
            "extraction_status": "failed",
            "extraction_reason": "parse_error",
        }

    if not rows:
        return {
            "columns": [],
            "row_count": 0,
            "extraction_status": "success",
            "extraction_reason": None,
        }

    return {
        "columns": rows[0],
        "row_count": len(rows) - 1,
        "extraction_status": "success",
        "extraction_reason": None,
    }

def extract_xml_facts(
    path: Path,
) -> dict:
    content = path.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    if len(content) > MAX_PARSE_CHARS:
        return {
            "root_tag": None,
            "child_count": None,
            "extraction_status": "skipped",
            "extraction_reason": "file_too_large",
        }

    try:
        root = ET.fromstring(content)
    except ET.ParseError:
        return {
            "root_tag": None,
            "child_count": None,
            "extraction_status": "failed",
            "extraction_reason": "parse_error",
        }

    return {
        "root_tag": root.tag,
        "child_count": len(root),
        "extraction_status": "success",
        "extraction_reason": None,
    }

FACT_EXTRACTORS = {
    ".py": extract_python_facts,
    ".json": extract_json_facts,
    ".toml": extract_toml_facts,
    ".ini": extract_ini_facts,
    ".cfg": extract_ini_facts,
    ".csv": extract_csv_facts,
    ".xml": extract_xml_facts,
}

def extract_file_facts(
    path: Path,
) -> dict:
    extractor = FACT_EXTRACTORS.get(
        path.suffix.lower()
    )

    if extractor is None:
        return {}

    return extractor(path)



