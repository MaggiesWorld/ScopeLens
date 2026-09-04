import json

from scopelens.inspector import inspect_target
from scopelens.package_writer import write_context_package
from scopelens.models import InspectionOptions


def test_writes_context_package(tmp_path):
    source_dir = tmp_path / "source"
    source_dir.mkdir()

    test_file = source_dir / "login.py"
    test_file.write_text(
        "def login_user():\n"
        "    return authenticate_user()"
    )

    result = inspect_target(
        source_dir,
        options=InspectionOptions(
            description="login authentication",
        ),
    )

    output_file = tmp_path / "context.json"

    written_path = write_context_package(
        result,
        output_file,
    )

    assert written_path.exists()

    payload = json.loads(
        written_path.read_text(
            encoding="utf-8"
        )
    )

    assert payload["target_type"] == "folder"
    assert len(payload["candidates"]) == 1

def test_context_package_includes_structure(tmp_path):
    project = tmp_path / "project"
    project.mkdir()

    src = project / "src"
    src.mkdir()

    test_file = src / "login.py"
    test_file.write_text("def login_user(): pass")

    result = inspect_target(project)

    output_file = tmp_path / "context.json"

    write_context_package(
        result,
        output_file,
    )

    data = json.loads(
        output_file.read_text(
            encoding="utf-8",
        )
    )

    structure = data["details"]["structure"]

    paths = {
        item["path"]
        for item in structure["items"]
    }

    assert "src" in paths
    assert "src/login.py" in paths

    assert structure["truncated"] is False
    assert structure["total_discovered"] >= 2

    assert data["summary"]["structure_items"] >= 2
    assert data["summary"]["structure_total_discovered"] >= 2
    assert data["summary"]["structure_truncated"] is False

def test_written_package_includes_json_facts(tmp_path):
    test_file = tmp_path / "config.json"

    test_file.write_text(
        '{"browser": "chrome", "timeout": 30}'
    )

    result = inspect_target(test_file)

    output_file = tmp_path / "context-package.json"

    write_context_package(
        result,
        output_file,
    )

    package = json.loads(
        output_file.read_text(
            encoding="utf-8"
        )
    )

    facts = package["details"]["facts"]

    assert facts["root_type"] == "dict"
    assert facts["top_level_keys"] == [
        "browser",
        "timeout",
    ]
    assert facts["item_count"] == 2
    assert facts["extraction_status"] == "success"

def test_written_folder_package_includes_project_facts(tmp_path):
    project = tmp_path / "project"
    project.mkdir()

    src = project / "src"
    src.mkdir()

    (src / "app.py").write_text(
        "print('hello')"
    )

    (project / "config.json").write_text(
        '{"enabled": true}'
    )

    result = inspect_target(project)

    output_file = tmp_path / "context-package.json"

    write_context_package(
        result,
        output_file,
    )

    package = json.loads(
        output_file.read_text(
            encoding="utf-8"
        )
    )

    facts = package["details"]["project_facts"]

    assert facts["file_count"] == 2
    assert facts["folder_count"] == 1
    assert facts["extensions"] == {
        ".json": 1,
        ".py": 1,
    }

def test_written_java_package_includes_facts(tmp_path):
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

    result = inspect_target(
        java_file,
        InspectionOptions(
            description="login test",
        ),
    )

    output_file = tmp_path / "context.json"

    write_context_package(
        result,
        output_file,
    )

    package = json.loads(
        output_file.read_text(encoding="utf-8")
    )

    facts = package["details"]["facts"]

    assert facts["package"] == "tests.login"
    assert facts["classes"] == ["LoginTests"]
    assert facts["test_methods"] == ["validLogin"]
    assert facts["contains_tests"] is True

def test_write_context_package_preserves_csharp_facts(tmp_path):
    source_file = tmp_path / "LoginTests.cs"

    source_file.write_text(
        """
using NUnit.Framework;

namespace Demo.Tests
{
    public class LoginTests
    {
        [Test]
        public void ValidLogin()
        {
        }
    }
}
""",
        encoding="utf-8",
    )

    result = inspect_target(
        str(source_file),
        InspectionOptions(
            description="login test",
        ),
    )

    output_file = tmp_path / "context.json"

    write_context_package(
        result,
        output_file,
    )

    package = json.loads(
        output_file.read_text(
            encoding="utf-8",
        )
    )

    facts = package["candidates"][0]["facts"]

    assert facts["namespace"] == "Demo.Tests"
    assert facts["classes"] == [
        "LoginTests",
    ]
    assert facts["test_methods"] == [
        "ValidLogin",
    ]
    assert facts["contains_tests"] is True

def test_write_context_package_preserves_cpp_facts(tmp_path):
    source_file = tmp_path / "calculator_test.cpp"

    source_file.write_text(
        """
#include <gtest/gtest.h>

namespace demo
{
    class Calculator
    {
    public:
        int add(int a, int b)
        {
            return a + b;
        }
    };
}

TEST(CalculatorTests, AddsNumbers)
{
    EXPECT_EQ(3, 1 + 2);
}
""",
        encoding="utf-8",
    )

    result = inspect_target(
        str(source_file),
        InspectionOptions(
            description="calculator test",
        ),
    )

    output_file = tmp_path / "context.json"

    write_context_package(
        result,
        output_file,
    )

    package = json.loads(
        output_file.read_text(
            encoding="utf-8",
        )
    )

    facts = package["candidates"][0]["facts"]

    assert facts["includes"] == [
        "gtest/gtest.h",
    ]
    assert facts["classes"] == [
        "Calculator",
    ]
    assert facts["namespaces"] == [
        "demo",
    ]
    assert facts["test_functions"] == [
        "CalculatorTests.AddsNumbers",
    ]
    assert facts["contains_tests"] is True
def test_write_context_package_accepts_browser_context(tmp_path):
    browser_context = {
        "target_type": "browser",
        "start_url": "https://example.com/",
        "page_count": 1,
        "pages": [
            {
                "url": "https://example.com/",
                "title": "Home",
                "testable_elements": [
                    {
                        "tag": "button",
                        "selectors": [
                            "#save",
                        ],
                    }
                ],
            }
        ],
    }

    output_file = tmp_path / "browser-context.json"

    written_path = write_context_package(
        browser_context,
        output_file,
    )

    package = json.loads(
        written_path.read_text(
            encoding="utf-8",
        )
    )

    assert package["target_type"] == "browser"
    assert package["start_url"] == "https://example.com/"
    assert package["page_count"] == 1
    assert package["pages"][0]["title"] == "Home"