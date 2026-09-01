from scopelens.file_facts import (
    extract_file_facts,
    extract_python_facts,
    FACT_EXTRACTORS
)


def test_extract_python_functions_and_classes(tmp_path):
    test_file = tmp_path / "login_service.py"

    test_file.write_text(
        "class LoginService:\n"
        "    def authenticate(self):\n"
        "        pass\n"
        "\n"
        "def create_session():\n"
        "    pass\n"
    )

    result = extract_python_facts(test_file)

    assert result["classes"] == [
        "LoginService",
    ]

    assert result["functions"] == [
        "authenticate",
        "create_session",
    ]

    assert result["extraction_status"] == "success"
    assert result["extraction_reason"] is None

def test_extract_python_imports(tmp_path):
    test_file = tmp_path / "service.py"

    test_file.write_text(
        "import os\n"
        "import json\n"
        "from pathlib import Path\n"
    )

    result = extract_python_facts(test_file)

    assert result["imports"] == [
        "json",
        "os",
        "pathlib",
    ]

def test_extract_python_test_functions(tmp_path):
    test_file = tmp_path / "test_login.py"

    test_file.write_text(
        "def test_valid_login():\n"
        "    pass\n"
        "\n"
        "def helper():\n"
        "    pass\n"
    )

    result = extract_python_facts(test_file)

    assert result["test_functions"] == [
        "test_valid_login",
    ]

def test_extract_python_test_classes(tmp_path):
    test_file = tmp_path / "test_login.py"

    test_file.write_text(
        "class TestLogin:\n"
        "    def test_valid_login(self):\n"
        "        pass\n"
        "\n"
        "class LoginHelper:\n"
        "    pass\n"
    )

    result = extract_python_facts(test_file)

    assert result["test_classes"] == [
        "TestLogin",
    ]

def test_extract_python_contains_tests(tmp_path):
    test_file = tmp_path / "test_login.py"

    test_file.write_text(
        "def test_valid_login():\n"
        "    pass\n"
    )

    result = extract_python_facts(test_file)

    assert result["contains_tests"] is True
    

def test_invalid_python_returns_empty_facts(tmp_path):
    test_file = tmp_path / "broken.py"

    test_file.write_text(
        "login authentication"
    )

    result = extract_python_facts(test_file)

    assert result == {
        "imports": [],
        "functions": [],
        "classes": [],
        "test_functions": [],
        "test_classes": [],
        "contains_tests": False,
        "extraction_status": "failed",
        "extraction_reason": "parse_error",
        
    }

def test_large_python_file_skips_fact_parsing(tmp_path):
    test_file = tmp_path / "large.py"

    test_file.write_text(
        "def login_user():\n"
        + ("    pass\n" * 20000)
    )

    result = extract_python_facts(test_file)

    assert result == {
        "imports": [],
        "functions": [],
        "classes": [],
        "test_functions": [],
        "test_classes": [],
        "contains_tests": False,
        "extraction_status": "skipped",
        "extraction_reason": "file_too_large",
    }

def test_extract_file_facts_routes_python(tmp_path):
    test_file = tmp_path / "login.py"

    test_file.write_text(
        "def authenticate_user():\n"
        "    pass\n"
    )

    result = extract_file_facts(test_file)

    assert "authenticate_user" in result["functions"]
    assert result["extraction_status"] == "success"

def test_extract_json_facts(tmp_path):
    test_file = tmp_path / "config.json"

    test_file.write_text(
        '{"browser": "chrome", "timeout": 30}'
    )

    result = extract_file_facts(test_file)

    assert result["top_level_keys"] == [
        "browser",
        "timeout",
    ]
    assert result["root_type"] == "dict"
    assert result["extraction_status"] == "success"

def test_invalid_json_returns_parse_error(tmp_path):
    test_file = tmp_path / "invalid.json"

    test_file.write_text(
        '{"browser": "chrome",'
    )

    result = extract_file_facts(test_file)

    assert result == {
        "top_level_keys": [],
        "root_type": None,
        "item_count": None,
        "extraction_status": "failed",
        "extraction_reason": "parse_error",
    }

def test_large_json_file_skips_fact_parsing(tmp_path):
    test_file = tmp_path / "large.json"

    test_file.write_text(
        '{"data": "' + ("x" * 100_000) + '"}'
    )

    result = extract_file_facts(test_file)

    assert result == {
        "top_level_keys": [],
        "root_type": None,
        "item_count": None,
        "extraction_status": "skipped",
        "extraction_reason": "file_too_large",
    }

def test_json_array_facts_include_item_count(tmp_path):
    test_file = tmp_path / "tests.json"

    test_file.write_text(
        '["login", "logout", "checkout"]'
    )

    result = extract_file_facts(test_file)

    assert result["root_type"] == "list"
    assert result["item_count"] == 3
    assert result["top_level_keys"] == []

def test_json_object_facts_include_item_count(tmp_path):
    test_file = tmp_path / "config.json"

    test_file.write_text(
        '{"browser": "chrome", "timeout": 30}'
    )

    result = extract_file_facts(test_file)

    assert result["root_type"] == "dict"
    assert result["item_count"] == 2

def test_extract_toml_facts(tmp_path):
    test_file = tmp_path / "pyproject.toml"

    test_file.write_text(
        '[project]\n'
        'name = "scopelens"\n'
        '\n'
        '[tool.pytest.ini_options]\n'
        'testpaths = ["tests"]\n'
    )

    result = extract_file_facts(test_file)

    assert result["top_level_keys"] == [
        "project",
        "tool",
    ]
    assert result["item_count"] == 2
    assert result["extraction_status"] == "success"

def test_invalid_toml_returns_parse_error(tmp_path):
    test_file = tmp_path / "broken.toml"

    test_file.write_text(
        '[project\n'
        'name = "scopelens"\n'
    )

    result = extract_file_facts(test_file)

    assert result == {
        "top_level_keys": [],
        "item_count": None,
        "extraction_status": "failed",
        "extraction_reason": "parse_error",
    }


def test_large_toml_file_skips_fact_parsing(tmp_path):
    test_file = tmp_path / "large.toml"

    test_file.write_text(
        'data = "' + ("x" * 100_000) + '"'
    )

    result = extract_file_facts(test_file)

    assert result == {
        "top_level_keys": [],
        "item_count": None,
        "extraction_status": "skipped",
        "extraction_reason": "file_too_large",
    }

def test_extract_ini_facts(tmp_path):
    test_file = tmp_path / "pytest.ini"

    test_file.write_text(
        "[pytest]\n"
        "testpaths = tests\n"
        "\n"
        "[coverage]\n"
        "branch = true\n"
    )

    result = extract_file_facts(test_file)

    assert result["sections"] == [
        "coverage",
        "pytest",
    ]
    assert result["section_count"] == 2
    assert result["extraction_status"] == "success"

def test_invalid_ini_returns_parse_error(tmp_path):
    test_file = tmp_path / "broken.ini"

    test_file.write_text(
        "[pytest\n"
        "testpaths = tests\n"
    )

    result = extract_file_facts(test_file)

    assert result == {
        "sections": [],
        "section_count": None,
        "extraction_status": "failed",
        "extraction_reason": "parse_error",
    }


def test_large_ini_file_skips_fact_parsing(tmp_path):
    test_file = tmp_path / "large.ini"

    test_file.write_text(
        "[settings]\n"
        'data = ' + ("x" * 100_000)
    )

    result = extract_file_facts(test_file)

    assert result == {
        "sections": [],
        "section_count": None,
        "extraction_status": "skipped",
        "extraction_reason": "file_too_large",
    }

def test_unsupported_file_type_returns_empty_facts(tmp_path):
    test_file = tmp_path / "notes.md"

    test_file.write_text(
        "# Notes\n"
        "Some documentation."
    )

    result = extract_file_facts(test_file)

    assert result == {}

def test_extract_csv_facts(tmp_path):
    test_file = tmp_path / "tests.csv"

    test_file.write_text(
        "id,title,result\n"
        "TC001,Login,Passed\n"
        "TC002,Logout,Failed\n"
    )

    result = extract_file_facts(test_file)

    assert result["columns"] == [
        "id",
        "title",
        "result",
    ]
    assert result["row_count"] == 2
    assert result["extraction_status"] == "success"

def test_empty_csv_returns_zero_rows(tmp_path):
    test_file = tmp_path / "empty.csv"

    test_file.write_text("")

    result = extract_file_facts(test_file)

    assert result == {
        "columns": [],
        "row_count": 0,
        "extraction_status": "success",
        "extraction_reason": None,
    }


def test_large_csv_file_skips_fact_parsing(tmp_path):
    test_file = tmp_path / "large.csv"

    test_file.write_text(
        "id,data\n"
        '1,"' + ("x" * 100_000) + '"\n'
    )

    result = extract_file_facts(test_file)

    assert result == {
        "columns": [],
        "row_count": None,
        "extraction_status": "skipped",
        "extraction_reason": "file_too_large",
    }

def test_invalid_csv_returns_parse_error(tmp_path):
    test_file = tmp_path / "broken.csv"

    test_file.write_text(
        'id,title\n'
        '1,"Unclosed title\n'
    )

    result = extract_file_facts(test_file)

    assert result == {
        "columns": [],
        "row_count": None,
        "extraction_status": "failed",
        "extraction_reason": "parse_error",
    }

def test_extract_xml_facts(tmp_path):
    test_file = tmp_path / "config.xml"

    test_file.write_text(
        "<project>"
        "<name>ScopeLens</name>"
        "<version>1.0</version>"
        "</project>"
    )

    result = extract_file_facts(test_file)

    assert result["root_tag"] == "project"
    assert result["child_count"] == 2
    assert result["extraction_status"] == "success"

def test_invalid_xml_returns_parse_error(tmp_path):
    test_file = tmp_path / "broken.xml"

    test_file.write_text(
        "<project>"
        "<name>ScopeLens</name>"
    )

    result = extract_file_facts(test_file)

    assert result == {
        "root_tag": None,
        "child_count": None,
        "extraction_status": "failed",
        "extraction_reason": "parse_error",
    }


def test_large_xml_file_skips_fact_parsing(tmp_path):
    test_file = tmp_path / "large.xml"

    test_file.write_text(
        "<project>"
        "<data>" + ("x" * 100_000) + "</data>"
        "</project>"
    )

    result = extract_file_facts(test_file)

    assert result == {
        "root_tag": None,
        "child_count": None,
        "extraction_status": "skipped",
        "extraction_reason": "file_too_large",
    }

def test_file_fact_dispatch_is_case_insensitive(tmp_path):
    test_file = tmp_path / "CONFIG.JSON"

    test_file.write_text(
        '{"browser": "chrome"}'
    )

    result = extract_file_facts(test_file)

    assert result["root_type"] == "dict"
    assert result["top_level_keys"] == ["browser"]
    assert result["extraction_status"] == "success"

def test_registered_fact_extractors_are_dispatchable():
    expected_extensions = {
        ".py",
        ".json",
        ".toml",
        ".ini",
        ".cfg",
        ".csv",
        ".xml",
    }

    assert set(FACT_EXTRACTORS.keys()) == expected_extensions

    assert all(
        callable(extractor)
        for extractor in FACT_EXTRACTORS.values()
    )