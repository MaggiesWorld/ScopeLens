import json
from pathlib import Path

from scopelens.models import InspectionResult


def write_context_package(
    result: InspectionResult | dict,
    output_path: str | Path,
) -> Path:
    destination = Path(output_path)

    destination.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    payload = (
        result.to_dict()
        if isinstance(result, InspectionResult)
        else result
    )

    destination.write_text(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return destination