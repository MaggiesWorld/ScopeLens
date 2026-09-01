def extract_relevant_snippets(
    content: str,
    description: str,
    context_lines: int = 2,
) -> str:
    terms = {
        term.lower()
        for term in description.split()
        if len(term) >= 3
    }

    lines = content.splitlines()

    matched_indexes = []

    for index, line in enumerate(lines):
        line_lower = line.lower()

        if any(term in line_lower for term in terms):
            matched_indexes.append(index)

    if not matched_indexes:
        return ""

    selected_indexes = set()

    for index in matched_indexes:
        start = max(0, index - context_lines)
        end = min(len(lines), index + context_lines + 1)

        selected_indexes.update(
            range(start, end)
        )

    return "\n".join(
        lines[index]
        for index in sorted(selected_indexes)
    )