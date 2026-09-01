from scopelens.file_inspector import inspect_file
from scopelens.folder_inspector import inspect_folder
from scopelens.models import (
    InspectionOptions,
    InspectionResult,
    Candidate,
)
from scopelens.target_resolver import resolve_target
from scopelens.relevance import explain_relevance
from scopelens.snippet_extractor import extract_relevant_snippets
from scopelens.collator import (
    collate_candidates,
    MAX_CONTENT_CHARS,
)
from scopelens.structure_inspector import inspect_structure
from scopelens.project_facts import extract_project_facts

def inspect_target(
    path: str,
    options: InspectionOptions | None = None,
) -> InspectionResult:
    target = resolve_target(path)

    options = options or InspectionOptions()

    if target.target_type == "file":
        details = inspect_file(
            target.path,
            description=options.description,
        )

        if details["size_bytes"] > options.max_file_size:
            details["skipped"] = True
            details["skip_reason"] = "file_too_large"
            candidates = []
        else:
            candidates = []

            if (
                options.description
                and details["relevance_score"]
                >= options.minimum_relevance_score
            ):
                content = target.path.read_text(
                    encoding="utf-8",
                    errors="ignore",
                )

                truncated = len(content) > MAX_CONTENT_CHARS

                if truncated:
                    snippets = extract_relevant_snippets(
                        content,
                        options.description,
                    )

                    if snippets:
                        content = snippets[:MAX_CONTENT_CHARS]
                    else:
                        content = content[:MAX_CONTENT_CHARS]

                candidates = [
                    Candidate(
                        name=target.path.name,
                        type="file",
                        category=details["category"],
                        size_bytes=details["size_bytes"],
                        relevance_score=details["relevance_score"],
                        content=content,
                        truncated=truncated,
                        relevance_explanation=explain_relevance(
                            target.path,
                            options.description,
                        ),
                         facts=details.get("facts", {}),

                    )
                ]

    else:
        details = inspect_folder(
            target.path,
            description=options.description,
            ignored_names=options.ignored_names,
            max_file_size=options.max_file_size,
        )

        structure = inspect_structure(
            target.path,
            ignored_names=options.ignored_names,
            max_items=options.max_structure_items,
        )

        details["structure"] = structure

        project_facts = extract_project_facts(
            structure
        )

        details["project_facts"] = project_facts

        candidates = collate_candidates(
            root_path=target.path,
            items=details["items"],
            description=options.description or "",
            max_candidates=options.max_candidates,
            minimum_score=options.minimum_relevance_score,
        )

    category_counts: dict[str, int] = {}

    skipped_count = (
        1
        if target.target_type == "file"
        and details.get("skipped") is True
        else 0
    )

    if (
        target.target_type == "file"
        and details.get("category")
    ):
        category = details["category"]

        category_counts[category] = (
            category_counts.get(category, 0) + 1
        )

    for item in details.get("items", []):
        if item.category:
            category_counts[item.category] = (
                category_counts.get(item.category, 0) + 1
            )

        if item.skipped:
            skipped_count += 1

    structure_items = 0
    structure_total_discovered = 0
    structure_truncated = False

    if target.target_type == "folder":
        structure = details.get("structure")

        if structure:
            structure_items = len(structure.items)
            structure_total_discovered = (
                structure.total_discovered
            )
            structure_truncated = structure.truncated

    summary = {
        "item_count": details.get("item_count", 0),
        "candidate_count": len(candidates),
        "skipped_count": skipped_count,
        "category_counts": category_counts,
        "top_relevance_score": (
            candidates[0].relevance_score
            if candidates
            else 0
        ),
        "structure_items": structure_items,
        "structure_total_discovered": structure_total_discovered,
        "structure_truncated": structure_truncated,
    }

    return InspectionResult(
        path=target.path,
        target_type=target.target_type,
        name=target.path.name,
        details=details,
        candidates=candidates,
        summary=summary,
    )