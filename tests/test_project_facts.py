from scopelens.models import (
    StructureItem,
    StructureResult,
)
from scopelens.project_facts import extract_project_facts


def test_extract_project_facts():
    structure = StructureResult(
        items=[
            StructureItem(
                path="src",
                type="folder",
                depth=1,
            ),
            StructureItem(
                path="src/app.py",
                type="file",
                depth=2,
            ),
            StructureItem(
                path="src/config.json",
                type="file",
                depth=2,
            ),
            StructureItem(
                path="tests/test_app.py",
                type="file",
                depth=2,
            ),
        ],
        truncated=False,
        total_discovered=4,
    )

    result = extract_project_facts(structure)

    assert result["file_count"] == 3
    assert result["folder_count"] == 1
    assert result["extensions"] == {
        ".py": 2,
        ".json": 1,
    }