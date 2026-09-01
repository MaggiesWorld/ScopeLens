import json
from pathlib import Path

from scopelens.models import InspectionResult


def write_context_package(
    result: InspectionResult,
    output_path: str | Path,
) -> Path:
    destination = Path(output_path)

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination.write_text(
        json.dumps(
            result.to_dict(),
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return destination