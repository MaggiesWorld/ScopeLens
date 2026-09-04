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
        ".java",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".json",
        ".toml",
        ".ini",
        ".cfg",
        ".csv",
        ".xml",
        ".cs",
        ".c",
        ".h",
        ".cpp",
        ".hpp",
    }

    assert set(FACT_EXTRACTORS.keys()) == expected_extensions

    assert all(
        callable(extractor)
        for extractor in FACT_EXTRACTORS.values()
    )

def test_extract_java_facts(tmp_path):
    java_file = tmp_path / "LoginTests.java"

    java_file.write_text(
        """
package tests.login;

import org.testng.annotations.Test;
import org.openqa.selenium.WebDriver;

public class LoginTests {

    @Test
    public void validLogin() {
    }

    public void logout() {
    }
}
""",
        encoding="utf-8",
    )

    facts = extract_file_facts(java_file)

    assert facts["package"] == "tests.login"
    assert facts["imports"] == [
        "org.openqa.selenium.WebDriver",
        "org.testng.annotations.Test",
    ]
    assert facts["classes"] == ["LoginTests"]
    assert facts["interfaces"] == []
    assert facts["methods"] == [
        "logout",
        "validLogin",
    ]
    assert facts["annotations"] == ["Test"]
    assert facts["test_methods"] == ["validLogin"]
    assert facts["contains_tests"] is True
    assert facts["extraction_status"] == "success"
    assert facts["extraction_reason"] is None

def test_extract_java_facts_large_file(tmp_path):
    java_file = tmp_path / "Large.java"

    java_file.write_text(
        "public class Large {\n"
        + ("public void testMethod() {}\n" * 10000)
        + "}",
        encoding="utf-8",
    )

    facts = extract_file_facts(java_file)

    assert facts["package"] is None
    assert facts["imports"] == []
    assert facts["classes"] == []
    assert facts["interfaces"] == []
    assert facts["methods"] == []
    assert facts["annotations"] == []
    assert facts["test_methods"] == []
    assert facts["contains_tests"] is False
    assert facts["extraction_status"] == "skipped"
    assert facts["extraction_reason"] == "file_too_large"


def test_extract_java_facts_without_test_annotations(tmp_path):
    java_file = tmp_path / "LoginService.java"

    java_file.write_text(
        """
package services.login;

public class LoginService {

    public void login() {
    }
}
""",
        encoding="utf-8",
    )

    facts = extract_file_facts(java_file)

    assert facts["classes"] == ["LoginService"]
    assert facts["methods"] == ["login"]
    assert facts["test_methods"] == []
    assert facts["contains_tests"] is False
    assert facts["extraction_status"] == "success"

def test_extract_java_interface_and_annotations(tmp_path):
    java_file = tmp_path / "LoginPage.java"

    java_file.write_text(
        """
package pages;

import org.testng.annotations.BeforeMethod;

public interface LoginActions {
    void login();
}

public class LoginPage implements LoginActions {

    @BeforeMethod
    public void setup() {
    }

    public void login() {
    }
}
""",
        encoding="utf-8",
    )

    facts = extract_file_facts(java_file)

    assert facts["package"] == "pages"
    assert facts["classes"] == ["LoginPage"]
    assert facts["interfaces"] == ["LoginActions"]
    assert facts["methods"] == [
        "login",
        "setup",
    ]
    assert facts["annotations"] == ["BeforeMethod"]
    assert facts["test_methods"] == []
    assert facts["contains_tests"] is False

def test_extract_java_junit_test_method(tmp_path):
    java_file = tmp_path / "CheckoutTests.java"

    java_file.write_text(
        """
package tests.checkout;

import org.junit.jupiter.api.Test;

public class CheckoutTests {

    @Test
    void successfulCheckout() {
    }

    void helperMethod() {
    }
}
""",
        encoding="utf-8",
    )

    facts = extract_file_facts(java_file)

    assert facts["imports"] == [
        "org.junit.jupiter.api.Test",
    ]
    assert facts["classes"] == ["CheckoutTests"]
    assert facts["methods"] == [
        "helperMethod",
        "successfulCheckout",
    ]
    assert facts["test_methods"] == [
        "successfulCheckout",
    ]
    assert facts["contains_tests"] is True

def test_extract_java_static_imports_and_generic_methods(tmp_path):
    java_file = tmp_path / "UserService.java"

    java_file.write_text(
        """
package services;

import java.util.List;
import static org.junit.jupiter.api.Assertions.assertEquals;

public class UserService {

    public List<String> getUsers() {
        return null;
    }

    private static String getUserName() {
        return "Maggie";
    }
}
""",
        encoding="utf-8",
    )

    facts = extract_file_facts(java_file)

    assert facts["imports"] == [
        "java.util.List",
        "org.junit.jupiter.api.Assertions.assertEquals",
    ]
    assert facts["classes"] == ["UserService"]
    assert facts["methods"] == [
        "getUserName",
        "getUsers",
    ]
    assert facts["contains_tests"] is False

def test_extract_javascript_facts(tmp_path):
    js_file = tmp_path / "login.test.js"

    js_file.write_text(
        """
import { login } from "./auth.js";
import UserService from "./UserService.js";

export function authenticateUser() {
    return login();
}

class LoginPage {
    submitLogin() {
    }
}

describe("Login", () => {
    test("valid login", () => {
    });
});
""",
        encoding="utf-8",
    )

    facts = extract_file_facts(js_file)

    assert facts["imports"] == [
        "./UserService.js",
        "./auth.js",
    ]
    assert facts["functions"] == [
        "authenticateUser",
    ]
    assert facts["classes"] == [
        "LoginPage",
    ]
    assert facts["methods"] == [
        "submitLogin",
    ]
    assert facts["test_functions"] == [
        "valid login",
    ]
    assert facts["describe_blocks"] == [
        "Login",
    ]
    assert facts["contains_tests"] is True
    assert facts["extraction_status"] == "success"
    assert facts["extraction_reason"] is None

def test_extract_typescript_facts(tmp_path):
    ts_file = tmp_path / "checkout.spec.ts"

    ts_file.write_text(
        """
import { test, expect } from "@playwright/test";
import { CheckoutPage } from "./CheckoutPage";

export async function createOrder() {
}

class PaymentService {
    async processPayment() {
    }
}

test("successful checkout", async () => {
});
""",
        encoding="utf-8",
    )

    facts = extract_file_facts(ts_file)

    assert facts["imports"] == [
        "./CheckoutPage",
        "@playwright/test",
    ]
    assert facts["functions"] == [
        "createOrder",
    ]
    assert facts["classes"] == [
        "PaymentService",
    ]
    assert facts["methods"] == [
        "processPayment",
    ]
    assert facts["test_functions"] == [
        "successful checkout",
    ]
    assert facts["contains_tests"] is True
    assert facts["extraction_status"] == "success"

def test_large_javascript_file_skips_fact_parsing(tmp_path):
    js_file = tmp_path / "large.js"

    js_file.write_text(
        "function testFunction() {}\n" * 10000,
        encoding="utf-8",
    )

    facts = extract_file_facts(js_file)

    assert facts["imports"] == []
    assert facts["functions"] == []
    assert facts["classes"] == []
    assert facts["methods"] == []
    assert facts["test_functions"] == []
    assert facts["describe_blocks"] == []
    assert facts["contains_tests"] is False
    assert facts["extraction_status"] == "skipped"
    assert facts["extraction_reason"] == "file_too_large"

def test_extract_javascript_arrow_functions(tmp_path):
    js_file = tmp_path / "auth.js"

    js_file.write_text(
        """
export const authenticateUser = async () => {
};

const logoutUser = () => {
};
""",
        encoding="utf-8",
    )

    facts = extract_file_facts(js_file)

    assert facts["functions"] == [
        "authenticateUser",
        "logoutUser",
    ]

def test_extract_typescript_arrow_function_with_return_type(tmp_path):
    ts_file = tmp_path / "auth.ts"

    ts_file.write_text(
        """
export const authenticateUser = async (
    username: string,
    password: string
): Promise<boolean> => {
    return true;
};
""",
        encoding="utf-8",
    )

    facts = extract_file_facts(ts_file)

    assert facts["functions"] == [
        "authenticateUser",
    ]

def test_extract_javascript_single_parameter_arrow_function(tmp_path):
    js_file = tmp_path / "users.js"

    js_file.write_text(
        """
const normalizeUser = user => {
    return user;
};
""",
        encoding="utf-8",
    )

    facts = extract_file_facts(js_file)

    assert facts["functions"] == [
        "normalizeUser",
    ]

def test_extract_typescript_typed_arrow_function(tmp_path):
    ts_file = tmp_path / "auth.ts"

    ts_file.write_text(
        """
type AuthHandler = (user: string) => Promise<boolean>;

const authenticateUser: AuthHandler = async (user) => {
    return true;
};
""",
        encoding="utf-8",
    )

    facts = extract_file_facts(ts_file)

    assert facts["functions"] == [
        "authenticateUser",
    ]

def test_extract_csharp_basic_facts(tmp_path):
    cs_file = tmp_path / "LoginTests.cs"

    cs_file.write_text(
        """
using System;
using NUnit.Framework;

namespace Demo.Tests
{
    [TestFixture]
    public class LoginTests
    {
        [Test]
        public void ValidLogin()
        {
        }

        private void Helper()
        {
        }
    }
}
""",
        encoding="utf-8",
    )

    facts = extract_file_facts(cs_file)

    assert facts["namespace"] == "Demo.Tests"
    assert facts["usings"] == [
        "NUnit.Framework",
        "System",
    ]
    assert facts["classes"] == [
        "LoginTests",
    ]
    assert facts["methods"] == [
        "Helper",
        "ValidLogin",
    ]
    assert facts["attributes"] == [
        "Test",
        "TestFixture",
    ]
    assert facts["test_methods"] == [
        "ValidLogin",
    ]
    assert facts["contains_tests"] is True

def test_extract_csharp_interface_and_async_method(tmp_path):
    cs_file = tmp_path / "AuthService.cs"

    cs_file.write_text(
        """
using System.Threading.Tasks;

namespace Demo.Services
{
    public interface IAuthService
    {
        Task<bool> AuthenticateAsync();
    }

    public class AuthService : IAuthService
    {
        public async Task<bool> AuthenticateAsync()
        {
            return true;
        }
    }
}
""",
        encoding="utf-8",
    )

    facts = extract_file_facts(cs_file)

    assert facts["interfaces"] == [
        "IAuthService",
    ]
    assert facts["classes"] == [
        "AuthService",
    ]
    assert facts["methods"] == [
        "AuthenticateAsync",
    ]

def test_extract_csharp_parameterized_test_method(tmp_path):
    cs_file = tmp_path / "CalculatorTests.cs"

    cs_file.write_text(
        """
using NUnit.Framework;

namespace Demo.Tests
{
    public class CalculatorTests
    {
        [TestCase(1, 2, 3)]
        public void AddsNumbers(int a, int b, int expected)
        {
        }
    }
}
""",
        encoding="utf-8",
    )

    facts = extract_file_facts(cs_file)

    assert facts["attributes"] == [
        "TestCase",
    ]
    assert facts["test_methods"] == [
        "AddsNumbers",
    ]
    assert facts["contains_tests"] is True

def test_extract_csharp_xunit_theory_method(tmp_path):
    cs_file = tmp_path / "CalculatorTests.cs"

    cs_file.write_text(
        """
using Xunit;

namespace Demo.Tests
{
    public class CalculatorTests
    {
        [Theory]
        [InlineData(1, 2, 3)]
        public void AddsNumbers(int a, int b, int expected)
        {
        }
    }
}
""",
        encoding="utf-8",
    )

    facts = extract_file_facts(cs_file)

    assert facts["attributes"] == [
        "InlineData",
        "Theory",
    ]
    assert facts["test_methods"] == [
        "AddsNumbers",
    ]
    assert facts["contains_tests"] is True

def test_extract_csharp_mstest_data_method(tmp_path):
    cs_file = tmp_path / "CalculatorTests.cs"

    cs_file.write_text(
        """
using Microsoft.VisualStudio.TestTools.UnitTesting;

namespace Demo.Tests
{
    [TestClass]
    public class CalculatorTests
    {
        [DataTestMethod]
        [DataRow(1, 2, 3)]
        public void AddsNumbers(int a, int b, int expected)
        {
        }
    }
}
""",
        encoding="utf-8",
    )

    facts = extract_file_facts(cs_file)

    assert facts["attributes"] == [
        "DataRow",
        "DataTestMethod",
        "TestClass",
    ]
    assert facts["test_methods"] == [
        "AddsNumbers",
    ]
    assert facts["contains_tests"] is True

def test_extract_csharp_large_file_is_skipped(tmp_path):
    cs_file = tmp_path / "LargeFile.cs"

    cs_file.write_text(
        "x" * 100_001,
        encoding="utf-8",
    )

    facts = extract_file_facts(cs_file)

    assert facts["namespace"] is None
    assert facts["usings"] == []
    assert facts["classes"] == []
    assert facts["interfaces"] == []
    assert facts["methods"] == []
    assert facts["attributes"] == []
    assert facts["test_methods"] == []
    assert facts["contains_tests"] is False
    assert facts["extraction_status"] == "skipped"
    assert facts["extraction_reason"] == "file_too_large"

def test_extract_c_basic_facts(tmp_path):
    c_file = tmp_path / "calculator.c"

    c_file.write_text(
        """
#include <stdio.h>
#include "calculator.h"

int add(int a, int b)
{
    return a + b;
}

static void reset(void)
{
}
""",
        encoding="utf-8",
    )

    facts = extract_file_facts(c_file)

    assert facts["includes"] == [
        "calculator.h",
        "stdio.h",
    ]
    assert facts["functions"] == [
        "add",
        "reset",
    ]
    assert facts["structs"] == []
    assert facts["classes"] == []
    assert facts["namespaces"] == []
    assert facts["contains_tests"] is False

def test_extract_cpp_basic_facts(tmp_path):
    cpp_file = tmp_path / "calculator.cpp"

    cpp_file.write_text(
        """
#include <vector>
#include "calculator.hpp"

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
""",
        encoding="utf-8",
    )

    facts = extract_file_facts(cpp_file)

    assert facts["includes"] == [
        "calculator.hpp",
        "vector",
    ]
    assert facts["classes"] == [
        "Calculator",
    ]
    assert facts["namespaces"] == [
        "demo",
    ]
    assert facts["functions"] == [
        "add",
    ]

def test_extract_c_struct_and_test_function(tmp_path):
    c_file = tmp_path / "calculator_test.c"

    c_file.write_text(
        """
struct CalculatorState
{
    int value;
};

void test_addition(void)
{
}
""",
        encoding="utf-8",
    )

    facts = extract_file_facts(c_file)

    assert facts["structs"] == [
        "CalculatorState",
    ]
    assert facts["test_functions"] == [
        "test_addition",
    ]
    assert facts["contains_tests"] is True

def test_extract_cpp_googletest_functions(tmp_path):
    cpp_file = tmp_path / "calculator_test.cpp"

    cpp_file.write_text(
        """
#include <gtest/gtest.h>

TEST(CalculatorTests, AddsNumbers)
{
    EXPECT_EQ(3, 1 + 2);
}

TEST_F(CalculatorFixture, ResetsValue)
{
    EXPECT_EQ(0, 0);
}
""",
        encoding="utf-8",
    )

    facts = extract_file_facts(cpp_file)

    assert facts["test_functions"] == [
        "CalculatorFixture.ResetsValue",
        "CalculatorTests.AddsNumbers",
    ]
    assert facts["contains_tests"] is True

def test_extract_cpp_catch2_test_case(tmp_path):
    cpp_file = tmp_path / "calculator_test.cpp"

    cpp_file.write_text(
        """
#include <catch2/catch_test_macros.hpp>

TEST_CASE("adds numbers")
{
    REQUIRE(1 + 2 == 3);
}
""",
        encoding="utf-8",
    )

    facts = extract_file_facts(cpp_file)

    assert facts["test_functions"] == [
        "adds numbers",
    ]
    assert facts["contains_tests"] is True

def test_extract_c_cpp_large_file_is_skipped(tmp_path):
    cpp_file = tmp_path / "LargeFile.cpp"

    cpp_file.write_text(
        "x" * 100_001,
        encoding="utf-8",
    )

    facts = extract_file_facts(cpp_file)

    assert facts["includes"] == []
    assert facts["functions"] == []
    assert facts["structs"] == []
    assert facts["classes"] == []
    assert facts["namespaces"] == []
    assert facts["test_functions"] == []
    assert facts["contains_tests"] is False
    assert facts["extraction_status"] == "skipped"
    assert facts["extraction_reason"] == "file_too_large"