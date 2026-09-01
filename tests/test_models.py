from scopelens.models import (
    DiscoveryItem,
    Candidate,
    InspectionResult,
    StructureItem,
    StructureResult,
)


def test_discovery_item_serializes():
    item = DiscoveryItem(
        name="auth/login.py",
        type="file",
        category="source",
        size_bytes=120,
        relevance_score=4,
    )

    result = item.to_dict()

    assert result["name"] == "auth/login.py"
    assert result["category"] == "source"
    assert result["relevance_score"] == 4
    assert result["skipped"] is False

def test_candidate_serializes():
    candidate = Candidate(
        name="auth/login.py",
        type="file",
        category="source",
        size_bytes=120,
        relevance_score=4,
        content="def login(): pass",
        truncated=False,
        relevance_explanation={
            "matched_path_terms": ["login"],
            "matched_content_terms": [],
        },
        facts={
            "contains_tests": False,
            "extraction_status": "success",
            "extraction_reason": None,
        },
    )

    result = candidate.to_dict()

    assert result["name"] == "auth/login.py"
    assert result["relevance_score"] == 4
    assert result["truncated"] is False
    assert result["facts"] == candidate.facts

def test_inspection_result_serializes_structure_items(tmp_path):
    result = InspectionResult(
        path=tmp_path,
        target_type="folder",
        name="project",
        details={
            "structure": StructureResult(
                items=[
                    StructureItem(
                        path="src/login.py",
                        type="file",
                        depth=2,
                    )
                ],
                truncated=True,
                total_discovered=10,
            )
        },
        candidates=[],
        summary={},
    )

    data = result.to_dict()

    assert data["details"]["structure"]["items"][0]["path"] == "src/login.py"
    assert data["details"]["structure"]["items"][0]["type"] == "file"
    assert data["details"]["structure"]["items"][0]["depth"] == 2

    assert data["details"]["structure"]["truncated"] is True
    assert data["details"]["structure"]["total_discovered"] == 10


def test_structure_result_serializes():
    result = StructureResult(
        items=[
            StructureItem(
                path="src/login.py",
                type="file",
                depth=2,
            )
        ],
        truncated=True,
        total_discovered=10,
    )

    data = result.to_dict()

    assert data["truncated"] is True
    assert data["total_discovered"] == 10
    assert data["items"][0]["path"] == "src/login.py"