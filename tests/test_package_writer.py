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