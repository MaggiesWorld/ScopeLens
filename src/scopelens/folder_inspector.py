from pathlib import Path
from scopelens.candidate_classifier import classify_candidate
from scopelens.relevance import score_relevance
from scopelens.ignore_rules import should_ignore
from scopelens.models import DiscoveryItem

DEFAULT_MAX_FILE_SIZE = 1_000_000

def inspect_folder(
    path: Path,
    description: str | None = None,
    ignored_names: set[str] | None = None,
    max_file_size: int = DEFAULT_MAX_FILE_SIZE,
) -> dict:
    items = []

    for child in path.rglob("*"):
        if should_ignore(
            child.relative_to(path),
            ignored_names=ignored_names,
        ):
            continue
        item = DiscoveryItem(
            name=child.relative_to(path).as_posix(),
            type="file" if child.is_file() else "folder",
        )

        if child.is_file():
            item.category = classify_candidate(child)

        if child.is_file():
            item.size_bytes = child.stat().st_size

            if item.size_bytes > max_file_size:
                item.skipped = True
                item.skip_reason = "file_too_large"
                items.append(item)
                continue

            item.category = classify_candidate(child)

            if description:
                item.relevance_score = score_relevance(
                    child,
                    description,
                )

        items.append(item)

    return {
        "items": items,
        "item_count": len(items),
    }