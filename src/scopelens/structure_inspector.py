from pathlib import Path
from scopelens.models import (
    StructureItem,
    StructureResult,
)
from scopelens.ignore_rules import (
    DEFAULT_IGNORED_NAMES,
    should_ignore,
)


def inspect_structure(
    root_path: Path,
    ignored_names: set[str] | None = None,
    max_items: int = 500,
) -> StructureResult:
    items: list[StructureItem] = []
    total_discovered = 0

    ignored_names = (
        ignored_names
        if ignored_names is not None
        else DEFAULT_IGNORED_NAMES
    )

    for child in sorted(root_path.rglob("*")):
        if should_ignore(child, ignored_names):
            continue

        # Count every valid project item we discover,
        # even if we have reached the return limit.
        total_discovered += 1

        # Once the package limit is reached,
        # continue counting but don't add more items.
        if len(items) >= max_items:
            continue

        relative_path = child.relative_to(root_path)

        items.append(
            StructureItem(
                path=relative_path.as_posix(),
                type=(
                    "folder"
                    if child.is_dir()
                    else "file"
                ),
                depth=len(relative_path.parts),
            )
        )

    return StructureResult(
        items=items,
        truncated=total_discovered > len(items),
        total_discovered=total_discovered,
    )