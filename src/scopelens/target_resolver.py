from pathlib import Path

from scopelens.models import InspectionTarget


def resolve_target(path: str | Path) -> InspectionTarget:
    target_path = Path(path).resolve()

    if not target_path.exists():
        raise FileNotFoundError(
            f"Target does not exist: {target_path}"
        )

    if target_path.is_file():
        target_type = "file"

    elif target_path.is_dir():
        target_type = "folder"

    else:
        raise ValueError(
            f"Unsupported target type: {target_path}"
        )

    return InspectionTarget(
        path=target_path,
        target_type=target_type,
    )