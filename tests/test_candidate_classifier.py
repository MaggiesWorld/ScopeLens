from pathlib import Path
from scopelens.candidate_classifier import classify_candidate


def test_classify_source_file():
    result = classify_candidate(
        Path("example.py")
    )

    assert result == "source"


def test_classify_test_file():
    result = classify_candidate(
        Path("test_login.py")
    )

    assert result == "test"


def test_classify_configuration_file():
    result = classify_candidate(
        Path("pyproject.toml")
    )

    assert result == "configuration"