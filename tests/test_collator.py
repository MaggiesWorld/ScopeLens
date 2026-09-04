from scopelens.collator import collate_candidates
from scopelens.models import DiscoveryItem



def test_collates_relevant_files(tmp_path):
    auth_file = tmp_path / "auth.py"
    auth_file.write_text(
        "def authenticate_user():\n"
        "    pass"
    )

    items = [
        DiscoveryItem(
            name="auth.py",
            type="file",
            relevance_score=1,
        ),
    ]

    result = collate_candidates(
        root_path=tmp_path,
        items=items,
        description="authentication",
    )

    assert len(result) == 1
    assert result[0].name == "auth.py"
    assert "authenticate_user" in result[0].content

def test_truncates_large_file(tmp_path):
    large_file = tmp_path / "large.py"
    large_file.write_text("x" * 20000)

    items = [
        DiscoveryItem(
            name="large.py",
            type="file",
            relevance_score=5,
        )
    ]

    result = collate_candidates(
        root_path=tmp_path,
        items=items,
        description="large",
    )

    assert result[0].truncated is True
    assert len(result[0].content) == 12000

def test_candidates_are_ranked_by_relevance(tmp_path):
    first_file = tmp_path / "first.py"
    second_file = tmp_path / "second.py"

    first_file.write_text("login")
    second_file.write_text("login authentication")

    items = [
        DiscoveryItem(
            name="first.py",
            type="file",
            relevance_score=1,
        ),
        DiscoveryItem(
            name="second.py",
            type="file",
            relevance_score=3,
        ),
    ]

    result = collate_candidates(
        root_path=tmp_path,
        items=items,
        description="login authentication",
    )

    assert result[0].name == "second.py"

def test_limits_number_of_candidates(tmp_path):
    items = []

    for index in range(5):
        file_path = tmp_path / f"file_{index}.py"
        file_path.write_text("login authentication")

        items.append(
            DiscoveryItem(
                name=file_path.name,
                type="file",
                relevance_score=5 - index,
            )
        )

    result = collate_candidates(
        root_path=tmp_path,
        items=items,
        description="login authentication",
        max_candidates=2,
    )

    assert len(result) == 2

def test_candidate_includes_relevance_explanation(tmp_path):
    auth_file = tmp_path / "login_service.py"
    auth_file.write_text(
        "def authenticate_user():\n"
        "    pass"
    )

    items = [
        DiscoveryItem(
            name="login_service.py",
            type="file",
            relevance_score=3,
        )
    ]

    result = collate_candidates(
        root_path=tmp_path,
        items=items,
        description="login authentication",
    )

    explanation = result[0].relevance_explanation

    assert "login" in explanation["matched_path_terms"]

def test_candidate_includes_python_facts(tmp_path):
    test_file = tmp_path / "test_login.py"
    test_file.write_text(
        "def test_valid_login():\n"
        "    pass"
    )

    items = [
        DiscoveryItem(
            name="test_login.py",
            type="file",
            relevance_score=3,
        )
    ]

    result = collate_candidates(
        root_path=tmp_path,
        items=items,
        description="login",
    )

    candidate = result[0]

    assert candidate.facts["contains_tests"] is True

    assert candidate.facts["extraction_status"] == "success"
    assert candidate.facts["extraction_reason"] is None

def test_collated_json_candidate_contains_facts(tmp_path):
    test_file = tmp_path / "config.json"

    test_file.write_text(
        '{"browser": "chrome", "timeout": 30}'
    )

    items = [
        DiscoveryItem(
            name="config.json",
            type="file",
            category="configuration",
            size_bytes=test_file.stat().st_size,
            relevance_score=2,
        )
    ]

    candidates = collate_candidates(
        root_path=tmp_path,
        items=items,
        description="browser configuration",
    )

    assert len(candidates) == 1

    facts = candidates[0].facts

    assert facts["root_type"] == "dict"
    assert facts["top_level_keys"] == [
        "browser",
        "timeout",
    ]
    assert facts["item_count"] == 2
    assert facts["extraction_status"] == "success"

def test_collated_java_candidate_contains_facts(tmp_path):
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

    items = [
        DiscoveryItem(
            name="LoginTests.java",
            type="file",
            category="source",
            size_bytes=java_file.stat().st_size,
            relevance_score=5,
        )
    ]

    candidates = collate_candidates(
        root_path=tmp_path,
        items=items,
        description="login test",
    )

    assert len(candidates) == 1

    facts = candidates[0].facts

    assert facts["package"] == "tests.login"
    assert facts["classes"] == ["LoginTests"]
    assert facts["test_methods"] == ["validLogin"]
    assert facts["contains_tests"] is True

    