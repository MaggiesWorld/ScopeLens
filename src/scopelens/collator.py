from pathlib import Path
from scopelens.snippet_extractor import (
    extract_relevant_snippets,
)
from scopelens.relevance import explain_relevance
from scopelens.models import Candidate, DiscoveryItem
from scopelens.file_facts import extract_file_facts

MAX_CONTENT_CHARS = 12000

def collate_candidates(
    root_path: Path,
    items: list[DiscoveryItem],
    description: str,
    minimum_score: int = 1,
    max_candidates: int = 10,
) -> list[Candidate]:
    candidates = []

    for item in items:
        if (
            item.type != "file"
            or item.relevance_score < minimum_score
        ):
            continue

        file_path = root_path / item.name

        try:
            content = file_path.read_text(
                encoding="utf-8",
                errors="ignore",
            )

            if len(content) > MAX_CONTENT_CHARS:
                content = content[:MAX_CONTENT_CHARS]
        except OSError:
            content = ""

        original_length = len(content)

        if original_length > MAX_CONTENT_CHARS:
            relevant_content = extract_relevant_snippets(
                content=content,
                description=description,
            )

            content = (
                relevant_content
                if relevant_content
                else content[:MAX_CONTENT_CHARS]
            )

        facts = extract_file_facts(file_path)

        candidates.append(
            Candidate(
                name=item.name,
                type=item.type,
                category=item.category,
                size_bytes=item.size_bytes,
                relevance_score=item.relevance_score,
                content=content,
                truncated=file_path.stat().st_size > MAX_CONTENT_CHARS,
                relevance_explanation=explain_relevance(
                    file_path,
                    description,
                ),
                facts=facts,
            )
        )

        candidates.sort(
            key=lambda item: item.relevance_score,
            reverse=True,
        )

    return candidates[:max_candidates]