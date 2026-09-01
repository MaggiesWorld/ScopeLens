from pathlib import Path

from scopelens.relevance import (
    normalize_search_terms,
    score_relevance,
    terms_are_related,
)

from scopelens.relevance import explain_relevance


def test_scores_matching_filename():
    score = score_relevance(
        Path("auth/login_service.py"),
        "login authentication",
    )

    assert score > 0


def test_scores_unrelated_file_zero():
    score = score_relevance(
        Path("reports/monthly_report.py"),
        "login authentication",
    )

    assert score == 0

def test_scores_matching_file_content(tmp_path):
    test_file = tmp_path / "service.py"

    test_file.write_text(
        "def authenticate_user():\n"
        "    return login_user()"
    )

    score = score_relevance(
        test_file,
        "login authentication",
    )

    assert score > 0

def test_normalizes_search_terms():
    terms = normalize_search_terms(
        "Login, authentication & user-session!"
    )

    assert "login" in terms
    assert "authentication" in terms
    assert "user" in terms
    assert "session" in terms

def test_exact_phrase_scores_higher(tmp_path):
    phrase_file = tmp_path / "phrase.py"
    term_file = tmp_path / "term.py"

    phrase_file.write_text(
        "login authentication workflow"
    )

    term_file.write_text(
        "login process with separate authentication logic"
    )

    phrase_score = score_relevance(
        phrase_file,
        "login authentication",
    )

    term_score = score_relevance(
        term_file,
        "login authentication",
    )

    assert phrase_score > term_score

def test_related_word_forms():
    assert terms_are_related(
        "authenticate",
        "authentication",
    )

def test_unrelated_words():
    assert not terms_are_related(
        "authentication",
        "reporting",
    )

def test_related_word_form_increases_relevance(tmp_path):
    test_file = tmp_path / "service.py"

    test_file.write_text(
        "def authenticate_user():\n"
        "    pass"
    )

    score = score_relevance(
        test_file,
        "authentication",
    )

    assert score > 0

def test_explains_relevance(tmp_path):
    test_file = tmp_path / "login_service.py"

    test_file.write_text(
        "def authenticate_user():\n"
        "    pass"
    )

    explanation = explain_relevance(
        test_file,
        "login authentication",
    )

    assert "login" in explanation["matched_path_terms"]
    assert "authentication" not in explanation["matched_path_terms"]