from pathlib import Path
from scopelens.candidate_classifier import classify_candidate
from scopelens.relevance import score_relevance
from scopelens.file_facts import extract_file_facts


def inspect_file(
    path: Path,
    description: str | None = None,
) -> dict:

    facts = extract_file_facts(path)

    return {
        "name": path.name,
        "extension": path.suffix.lower(),
        "size_bytes": path.stat().st_size,
        "category": classify_candidate(path),
        "relevance_score": (
            score_relevance(path, description)
            if description
            else 0
        ),
        "facts": facts,
    }