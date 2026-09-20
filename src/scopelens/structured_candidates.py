import json
from typing import Any

from scopelens.models import Candidate
from scopelens.relevance import score_text_relevance


def build_json_item_candidates(
    data: Any,
    description: str,
    minimum_score: int = 1,
) -> list[Candidate]:
    """Build relevance candidates from list items inside JSON objects."""

    if not isinstance(data, dict):
        return []

    candidates = []

    for collection_name, collection in data.items():
        if not isinstance(collection, list):
            continue

        for index, item in enumerate(collection):
            if not isinstance(item, dict):
                continue

            content = json.dumps(
                item,
                indent=2,
            )

            relevance_score = score_text_relevance(
                content,
                description,
            )

            if relevance_score < minimum_score:
                continue

            identifier = str(
                item.get("id")
                or item.get("name")
                or f"{collection_name}[{index}]"
            )

            candidates.append(
                Candidate(
                    name=identifier,
                    type="json_item",
                    category=collection_name,
                    size_bytes=len(
                        content.encode("utf-8")
                    ),
                    relevance_score=relevance_score,
                    content=content,
                    truncated=False,
                    relevance_explanation={
                        "collection": collection_name,
                    },
                    facts={
                        "collection": collection_name,
                        "index": index,
                    },
                )
            )

    candidates.sort(
        key=lambda candidate: candidate.relevance_score,
        reverse=True,
    )

    return candidates