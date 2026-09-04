from scopelens.file_inspector import inspect_file

def test_inspect_file_includes_category(tmp_path):
    test_file = tmp_path / "login.py"
    test_file.write_text("print('hello')")

    result = inspect_file(test_file)

    assert result["name"] == "login.py"
    assert result["category"] == "source"

def test_inspect_file_includes_relevance(tmp_path):
    test_file = tmp_path / "login.py"
    test_file.write_text(
        "def authenticate_user():\n"
        "    pass"
    )

    result = inspect_file(
        test_file,
        description="login authentication",
    )

    assert result["relevance_score"] > 0

def test_inspect_python_file_includes_facts(tmp_path):
    test_file = tmp_path / "test_login.py"

    test_file.write_text(
        "import os\n"
        "\n"
        "class TestLogin:\n"
        "    def test_valid_login(self):\n"
        "        pass\n"
    )

    result = inspect_file(test_file)

    assert result["facts"]["imports"] == ["os"]
    assert result["facts"]["test_classes"] == ["TestLogin"]
    assert result["facts"]["test_functions"] == ["test_valid_login"]
    assert result["facts"]["contains_tests"] is True

    assert result["facts"]["extraction_status"] == "success"
    assert result["facts"]["extraction_reason"] is None

def test_json_file_inspection_contains_facts(tmp_path):
    test_file = tmp_path / "config.json"

    test_file.write_text(
        '{"browser": "chrome", "timeout": 30}'
    )

    result = inspect_file(test_file)

    facts = result["facts"]

    assert facts["root_type"] == "dict"
    assert facts["top_level_keys"] == [
        "browser",
        "timeout",
    ]
    assert facts["item_count"] == 2
    assert facts["extraction_status"] == "success"

def test_java_file_inspection_contains_facts(tmp_path):
    java_file = tmp_path / "LoginTests.java"

    java_file.write_text(
        """
package tests.login;

import org.testng.annotations.Test;

public class LoginTests {

    @Test
    public void validLogin() {
    }
}
""",
        encoding="utf-8",
    )

    details = inspect_file(
        java_file,
        description="login test",
    )

    facts = details["facts"]

    assert facts["package"] == "tests.login"
    assert facts["classes"] == ["LoginTests"]
    assert facts["test_methods"] == ["validLogin"]
    assert facts["contains_tests"] is True