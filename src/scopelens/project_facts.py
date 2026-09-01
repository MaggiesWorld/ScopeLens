from scopelens.models import StructureResult


def extract_project_facts(
    structure: StructureResult,
) -> dict:
    files = [
        item
        for item in structure.items
        if item.type == "file"
    ]

    folders = [
        item
        for item in structure.items
        if item.type == "folder"
    ]

    extensions: dict[str, int] = {}

    for item in files:
        if "." not in item.path:
            continue

        extension = "." + item.path.rsplit(".", 1)[1].lower()

        extensions[extension] = (
            extensions.get(extension, 0) + 1
        )

    return {
        "file_count": len(files),
        "folder_count": len(folders),
        "extensions": extensions,
    }