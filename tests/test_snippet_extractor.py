from scopelens.snippet_extractor import (
    extract_relevant_snippets,
)


def test_extracts_relevant_section():
    content = """
unrelated line
another unrelated line
def login_user():
    return authenticate_user()
more unrelated content
"""

    result = extract_relevant_snippets(
        content,
        "login authentication",
    )

    assert "login_user" in result
    assert "authenticate_user" in result