from pathlib import Path
import re
from difflib import SequenceMatcher

TEXT_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".java",
    ".cs",
    ".json",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".xml",
    ".md",
    ".rst",
    ".txt",
}

def normalize_search_terms(
    description: str,
) -> set[str]:
    words = re.findall(
        r"[a-zA-Z0-9_]+",
        description.lower(),
    )

    return {
        word
        for word in words
        if len(word) >= 3
    }

def normalize_phrase(
    description: str,
) -> str:
    words = re.findall(
        r"[a-zA-Z0-9_]+",
        description.lower(),
    )

    return " ".join(
        word
        for word in words
        if len(word) >= 3
    )

def terms_are_related(
    first: str,
    second: str,
    threshold: float = 0.75,
) -> bool:
    if first == second:
        return True

    if len(first) < 4 or len(second) < 4:
        return False

    similarity = SequenceMatcher(
        None,
        first,
        second,
    ).ratio()

    return similarity >= threshold

def score_relevance(
    path: Path,
    description: str,
) -> int:
    score = 0

    search_terms = normalize_search_terms(
        description
    )

    path_text = str(path).lower()

    search_phrase = normalize_phrase(
        description
    )

    for term in search_terms:
        if term in path_text:
            score += 2

    if path.suffix.lower() not in TEXT_EXTENSIONS:
        return score

    try:
        content = path.read_text(
            encoding="utf-8",
            errors="ignore",
        ).lower()
    except OSError:
        return score

    content_terms = set(
        re.findall(
            r"[a-zA-Z0-9]+",
            content,
        )
    )

    if search_phrase and search_phrase in path_text:
        score += 5

    if search_phrase and search_phrase in content:
        score += 3

    for term in search_terms:
        if term in content:
            score += 1

    for search_term in search_terms:
        if search_term in content_terms:
            continue

        if any(
            terms_are_related(
                search_term,
                content_term,
            )
            for content_term in content_terms
        ):
            score += 1

    return score

def explain_relevance(
    path: Path,
    description: str,
) -> dict:
    search_terms = normalize_search_terms(
        description
    )

    path_text = str(path).lower()

    matched_path_terms = [
        term
        for term in search_terms
        if term in path_text
    ]

    matched_content_terms = []

    if path.suffix.lower() in TEXT_EXTENSIONS:
        try:
            content = path.read_text(
                encoding="utf-8",
                errors="ignore",
            ).lower()

            matched_content_terms = [
                term
                for term in search_terms
                if term in content
            ]

        except OSError:
            pass

    return {
        "matched_path_terms": matched_path_terms,
        "matched_content_terms": matched_content_terms,
    }

