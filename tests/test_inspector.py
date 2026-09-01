from scopelens.inspector import inspect_target
from scopelens.models import InspectionOptions


def test_inspect_folder():
    result = inspect_target(".")

    assert result.target_type == "folder"
    assert result.name

def test_inspect_folder_classifies_files(tmp_path):
    test_file = tmp_path / "example.py"
    test_file.write_text("print('hello')")

    result = inspect_target(tmp_path)

    file_item = next(
        item
        for item in result.details["items"]
        if item.name == "example.py"
    )

    assert file_item.category == "source"

def test_inspection_returns_collated_candidates(tmp_path):
    relevant_file = tmp_path / "service.py"
    irrelevant_file = tmp_path / "report.py"

    relevant_file.write_text(
        "def authenticate_user():\n"
        "    return login_user()"
    )

    irrelevant_file.write_text(
        "def generate_report():\n"
        "    pass"
    )

    result = inspect_target(
        tmp_path,
        options=InspectionOptions(
            description="login authentication",
        ),
    )

    assert len(result.candidates) == 1
    assert result.candidates[0].name == "service.py"

def test_inspection_result_is_serializable(tmp_path):
    test_file = tmp_path / "sample.py"
    test_file.write_text("print('hello')")

    result = inspect_target(tmp_path)

    payload = result.to_dict()

    assert isinstance(payload["path"], str)
    assert payload["target_type"] == "folder"
    assert isinstance(payload["candidates"], list)

def test_large_file_is_skipped(tmp_path):
    large_file = tmp_path / "huge.txt"
    large_file.write_text("x" * 200)

    result = inspect_target(
        tmp_path,
        options=InspectionOptions(
            description="anything",
            max_file_size=100,
        ),
    )

    item = next(
        item
        for item in result.details["items"]
        if item.name == "huge.txt"
    )

    assert item.skipped is True
    assert item.skip_reason == "file_too_large"

def test_inspection_includes_summary(tmp_path):
    test_file = tmp_path / "login.py"
    test_file.write_text("login authentication")

    result = inspect_target(
        tmp_path,
        options=InspectionOptions(
            description="login authentication",
        ),
    )

    assert result.summary["item_count"] >= 1
    assert result.summary["candidate_count"] == 1

def test_inspection_summary_includes_categories(tmp_path):
    source_file = tmp_path / "login.py"
    config_file = tmp_path / "config.json"

    source_file.write_text("login authentication")
    config_file.write_text("{}")

    result = inspect_target(
        tmp_path,
        options=InspectionOptions(
            description="login authentication",
        ),
    )

    assert result.summary["category_counts"]["source"] == 1
    assert result.summary["category_counts"]["configuration"] == 1
    assert result.summary["top_relevance_score"] > 0

def test_minimum_relevance_score_filters_candidates(tmp_path):
    strong_file = tmp_path / "login_authentication.py"
    weak_file = tmp_path / "session.py"

    strong_file.write_text(
        "login authentication"
    )

    weak_file.write_text(
        "authentication"
    )

    result = inspect_target(
        tmp_path,
        options=InspectionOptions(
            description="login authentication",
            minimum_relevance_score=4,
        ),
    )

    candidate_names = [
        candidate.name
        for candidate in result.candidates
    ]

    assert "login_authentication.py" in candidate_names
    assert "session.py" not in candidate_names

def test_direct_file_inspection_uses_description(tmp_path):
    test_file = tmp_path / "login.py"
    test_file.write_text(
        "def authenticate_user():\n"
        "    pass"
    )

    result = inspect_target(
        test_file,
        options=InspectionOptions(
            description="login authentication",
        ),
    )

    assert result.details["relevance_score"] > 0

def test_direct_file_returns_candidate(tmp_path):
    test_file = tmp_path / "login.py"
    test_file.write_text(
        "def authenticate_user():\n"
        "    pass"
    )

    result = inspect_target(
        test_file,
        options=InspectionOptions(
            description="login authentication",
        ),
    )

    assert len(result.candidates) == 1
    assert result.candidates[0].name == "login.py"
    assert result.candidates[0].relevance_score > 0

def test_direct_file_candidate_is_bounded(tmp_path):
    test_file = tmp_path / "large.py"
    test_file.write_text("login " * 5000)

    result = inspect_target(
        test_file,
        options=InspectionOptions(
            description="login",
        ),
    )

    candidate = result.candidates[0]

    assert candidate.truncated is True
    assert len(candidate.content) <= 12000

def test_direct_large_file_uses_relevant_snippet(tmp_path):
    test_file = tmp_path / "large.py"

    test_file.write_text(
        ("noise\n" * 5000)
        + "def authenticate_user():\n"
        + "    return login_user()\n"
    )

    result = inspect_target(
        test_file,
        options=InspectionOptions(
            description="login authentication",
        ),
    )

    candidate = result.candidates[0]

    assert candidate.truncated is True
    assert "authenticate_user" in candidate.content

def test_direct_file_respects_max_file_size(tmp_path):
    test_file = tmp_path / "large.py"
    test_file.write_text(
        "def login_user():\n"
        + ("    pass\n" * 100)
    )

    result = inspect_target(
        test_file,
        options=InspectionOptions(
            description="login",
            max_file_size=10,
        ),
    )

    assert result.candidates == []

def test_direct_file_reports_size_skip_reason(tmp_path):
    test_file = tmp_path / "large.py"
    test_file.write_text("login " * 100)

    result = inspect_target(
        test_file,
        options=InspectionOptions(
            description="login",
            max_file_size=10,
        ),
    )

    assert result.details["skipped"] is True
    assert result.details["skip_reason"] == "file_too_large"
    assert result.candidates == []

def test_direct_file_skip_is_counted_in_summary(tmp_path):
    test_file = tmp_path / "large.py"
    test_file.write_text("login " * 100)

    result = inspect_target(
        test_file,
        options=InspectionOptions(
            description="login",
            max_file_size=10,
        ),
    )

    assert result.summary["skipped_count"] == 1

def test_direct_file_category_is_counted_in_summary(tmp_path):
    test_file = tmp_path / "login.py"
    test_file.write_text(
        "def login_user():\n"
        "    pass"
    )

    result = inspect_target(
        test_file,
        options=InspectionOptions(
            description="login",
        ),
    )

    assert result.summary["category_counts"]["source"] == 1

def test_folder_inspection_includes_structure(tmp_path):
    src = tmp_path / "src"
    src.mkdir()

    test_file = src / "login.py"
    test_file.write_text("def login_user(): pass")

    result = inspect_target(tmp_path)

    structure_paths = {
        item.path
        for item in result.details["structure"].items
    }

    assert "src" in structure_paths
    assert "src/login.py" in structure_paths

def test_folder_summary_includes_structure_metrics(tmp_path):
    for index in range(5):
        test_file = tmp_path / f"file_{index}.py"
        test_file.write_text("pass")

    result = inspect_target(
        tmp_path,
        options=InspectionOptions(
            max_structure_items=2,
        ),
    )

    assert result.summary["structure_items"] == 2
    assert result.summary["structure_total_discovered"] == 5
    assert result.summary["structure_truncated"] is True

def test_direct_json_inspection_includes_facts(tmp_path):
    test_file = tmp_path / "config.json"

    test_file.write_text(
        '{"browser": "chrome", "timeout": 30}'
    )

    result = inspect_target(test_file)

    assert result.details["facts"]["root_type"] == "dict"
    assert result.details["facts"]["top_level_keys"] == [
        "browser",
        "timeout",
    ]
    assert result.details["facts"]["item_count"] == 2
    assert result.details["facts"]["extraction_status"] == "success"

def test_direct_json_facts_survive_serialization(tmp_path):
    test_file = tmp_path / "config.json"

    test_file.write_text(
        '{"browser": "chrome", "timeout": 30}'
    )

    result = inspect_target(test_file)
    serialized = result.to_dict()

    facts = serialized["details"]["facts"]

    assert facts["root_type"] == "dict"
    assert facts["top_level_keys"] == [
        "browser",
        "timeout",
    ]
    assert facts["item_count"] == 2
    assert facts["extraction_status"] == "success"

def test_folder_inspection_includes_project_facts(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text(
        "print('hello')"
    )
    (tmp_path / "config.json").write_text(
        '{"enabled": true}'
    )

    result = inspect_target(tmp_path)

    facts = result.details["project_facts"]

    assert facts["file_count"] == 2
    assert facts["folder_count"] == 1
    assert facts["extensions"] == {
        ".json": 1,
        ".py": 1,
    }