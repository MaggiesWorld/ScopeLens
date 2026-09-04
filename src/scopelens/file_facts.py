import ast
import json
import tomllib
import configparser
import csv
import xml.etree.ElementTree as ET
import re
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

def extract_java_facts(
    path: Path,
) -> dict:
    import re

    content = path.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    if len(content) > MAX_PARSE_CHARS:
        return {
            "package": None,
            "imports": [],
            "classes": [],
            "interfaces": [],
            "methods": [],
            "annotations": [],
            "test_methods": [],
            "contains_tests": False,
            "extraction_status": "skipped",
            "extraction_reason": "file_too_large",
        }

    package_match = re.search(
        r"\bpackage\s+([\w.]+)\s*;",
        content,
    )

    imports = re.findall(
        r"\bimport\s+(?:static\s+)?([\w.*]+)\s*;",
        content,
    )

    classes = re.findall(
        r"\bclass\s+(\w+)",
        content,
    )

    interfaces = re.findall(
        r"\binterface\s+(\w+)",
        content,
    )

    methods = re.findall(
        r"\b(?:public|protected|private)?\s*"
        r"(?:static\s+)?"
        r"[\w<>\[\], ?]+\s+"
        r"(\w+)\s*\([^;{}]*\)\s*\{",
        content,
    )

    annotations = re.findall(
        r"@(\w+)",
        content,
    )

    test_methods = re.findall(
        r"@Test(?:\([^)]*\))?\s*"
        r"(?:public|protected|private)?\s*"
        r"(?:static\s+)?"
        r"[\w<>\[\], ?]+\s+"
        r"(\w+)\s*\(",
        content,
    )

    return {
        "package": (
            package_match.group(1)
            if package_match
            else None
        ),
        "imports": sorted(set(imports)),
        "classes": sorted(set(classes)),
        "interfaces": sorted(set(interfaces)),
        "methods": sorted(set(methods)),
        "annotations": sorted(set(annotations)),
        "test_methods": sorted(set(test_methods)),
        "contains_tests": bool(test_methods),
        "extraction_status": "success",
        "extraction_reason": None,
    }

def extract_javascript_facts(
    path: Path,
) -> dict:
    content = path.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    empty_facts = {
        "imports": [],
        "functions": [],
        "classes": [],
        "methods": [],
        "test_functions": [],
        "describe_blocks": [],
        "contains_tests": False,
    }

    if len(content) > MAX_PARSE_CHARS:
        return {
            **empty_facts,
            "extraction_status": "skipped",
            "extraction_reason": "file_too_large",
        }

    imports = re.findall(
        r'import\s+(?:.+?\s+from\s+)?["\']([^"\']+)["\']',
        content,
    )

    functions = re.findall(
    r'\b(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(',
    content,
)

    arrow_functions = re.findall(
        r'\b(?:export\s+)?'
        r'(?:const|let|var)\s+'
        r'(\w+)'
        r'(?:\s*:\s*[\w<>\[\]|&, .]+)?'
        r'\s*=\s*'
        r'(?:async\s+)?'
        r'(?:\([^)]*\)|\w+)'
        r'(?:\s*:\s*[^=]+?)?'
        r'\s*=>',
        content,
    )

    functions.extend(arrow_functions)

    classes = re.findall(
        r'\bclass\s+(\w+)',
        content,
    )

    methods = re.findall(
        r'^\s*(?!if\b|for\b|while\b|switch\b|catch\b)'
        r'(?:async\s+)?(\w+)\s*\([^)]*\)\s*\{',
        content,
        re.MULTILINE,
    )

    test_functions = re.findall(
        r'\b(?:test|it)\s*\(\s*["\']([^"\']+)["\']',
        content,
    )

    describe_blocks = re.findall(
        r'\bdescribe\s*\(\s*["\']([^"\']+)["\']',
        content,
    )

    return {
        "imports": sorted(set(imports)),
        "functions": sorted(set(functions)),
        "classes": sorted(set(classes)),
        "methods": sorted(set(methods)),
        "test_functions": sorted(set(test_functions)),
        "describe_blocks": sorted(set(describe_blocks)),
        "contains_tests": bool(
            test_functions
            or describe_blocks
        ),
        "extraction_status": "success",
        "extraction_reason": None,
    }

def extract_csharp_facts(
    path: Path,
) -> dict:
    content = path.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    empty_facts = {
        "namespace": None,
        "usings": [],
        "classes": [],
        "interfaces": [],
        "methods": [],
        "attributes": [],
        "test_methods": [],
        "contains_tests": False,
    }

    if len(content) > MAX_PARSE_CHARS:
        return {
            **empty_facts,
            "extraction_status": "skipped",
            "extraction_reason": "file_too_large",
        }

    namespace_match = re.search(
        r"\bnamespace\s+([\w.]+)",
        content,
    )

    usings = re.findall(
        r"\busing\s+([\w.]+)\s*;",
        content,
    )

    classes = re.findall(
        r"\bclass\s+(\w+)",
        content,
    )

    interfaces = re.findall(
        r"\binterface\s+(\w+)",
        content,
    )

    methods = re.findall(
        r"\b(?:public|private|protected|internal)\s+"
        r"(?:static\s+)?"
        r"[\w<>\[\], ?]+\s+"
        r"(\w+)\s*\([^;{}]*\)\s*\{",
        content,
    )

    attributes = re.findall(
        r"\[(\w+)(?:\([^]]*\))?\]",
        content,
    )

    test_methods = re.findall(
        r"\[(?:Test|Fact|TestMethod|TestCase|Theory|DataTestMethod)(?:\([^]]*\))?\]\s*"
        r"(?:\[[^\]]+\]\s*)*"
        r"(?:public|private|protected|internal)\s+"
        r"(?:static\s+)?"
        r"[\w<>\[\], ?]+\s+"
        r"(\w+)\s*\(",
        content,
    )

    return {
        "namespace": (
            namespace_match.group(1)
            if namespace_match
            else None
        ),
        "usings": sorted(set(usings)),
        "classes": sorted(set(classes)),
        "interfaces": sorted(set(interfaces)),
        "methods": sorted(set(methods)),
        "attributes": sorted(set(attributes)),
        "test_methods": sorted(set(test_methods)),
        "contains_tests": bool(test_methods),
        "extraction_status": "success",
        "extraction_reason": None,
    }

def extract_c_cpp_facts(
    path: Path,
) -> dict:
    content = path.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    empty_facts = {
        "includes": [],
        "functions": [],
        "structs": [],
        "classes": [],
        "namespaces": [],
        "test_functions": [],
        "contains_tests": False,
    }

    if len(content) > MAX_PARSE_CHARS:
        return {
            **empty_facts,
            "extraction_status": "skipped",
            "extraction_reason": "file_too_large",
        }

    includes = re.findall(
        r'#include\s*[<"]([^>"]+)[>"]',
        content,
    )

    functions = re.findall(
        r'^\s*(?:static\s+)?'
        r'[\w:*&<>\[\]\s]+\s+'
        r'(\w+)\s*\([^;{}]*\)\s*\{',
        content,
        re.MULTILINE,
    )

    structs = re.findall(
        r'\bstruct\s+(\w+)',
        content,
    )

    classes = re.findall(
        r'\bclass\s+(\w+)',
        content,
    )

    namespaces = re.findall(
        r'\bnamespace\s+(\w+)',
        content,
    )

    test_functions = [
        name
        for name in functions
        if name.lower().startswith("test")
    ]

    gtest_functions = re.findall(
        r'\bTEST(?:_F)?\s*\(\s*'
        r'(\w+)\s*,\s*(\w+)\s*\)',
        content,
    )

    test_functions.extend(
        f"{suite}.{name}"
        for suite, name in gtest_functions
    )

    catch2_functions = re.findall(
        r'\bTEST_CASE\s*\(\s*["\']([^"\']+)["\']',
        content,
    )

    test_functions.extend(catch2_functions)

    return {
        "includes": sorted(set(includes)),
        "functions": sorted(set(functions)),
        "structs": sorted(set(structs)),
        "classes": sorted(set(classes)),
        "namespaces": sorted(set(namespaces)),
        "test_functions": sorted(set(test_functions)),
        "contains_tests": bool(test_functions),
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
    ".py": extract_python_facts,
    ".java": extract_java_facts,
    ".js": extract_javascript_facts,
    ".jsx": extract_javascript_facts,
    ".ts": extract_javascript_facts,
    ".tsx": extract_javascript_facts,
    ".cs": extract_csharp_facts,
    ".c": extract_c_cpp_facts,
    ".h": extract_c_cpp_facts,
    ".cpp": extract_c_cpp_facts,
    ".hpp": extract_c_cpp_facts,
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



