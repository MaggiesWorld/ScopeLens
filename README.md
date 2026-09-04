# ScopeLens

**ScopeLens is a reusable inspection and context-discovery engine for source code, projects, and browser-based applications.**

It discovers what exists in a target, identifies potentially relevant information, extracts deterministic facts, and produces a compact context package that can be consumed by AI systems, development tools, QA platforms, or other applications.

ScopeLens is intentionally application-agnostic. It performs discovery and interrogation; the consuming application decides what to do with the results.

## Why ScopeLens?

AI-assisted development and QA tools often send far more context to an LLM than is actually necessary.

ScopeLens provides a deterministic inspection layer before that interaction.

Instead of handing an entire project or application to an AI system, ScopeLens can:

1. Discover the target.
2. Filter irrelevant content.
3. Extract useful structural facts.
4. Identify relevant candidates and snippets.
5. Produce a bounded, JSON-safe context package.

This helps reduce unnecessary context while preserving information useful to downstream systems.

## Features

### Source and Project Interrogation

ScopeLens can inspect individual files, folders, and source projects.

Capabilities include:

- File and folder discovery
- Project structure inspection
- Ignore rules
- Candidate classification
- Deterministic relevance scoring
- Relevant snippet extraction
- File-level facts
- Project-level facts
- Bounded context generation
- JSON-safe serialization
- Context package generation

### Supported Source Languages

ScopeLens 0.1 includes deterministic fact extraction for:

- Python
- Java
- JavaScript
- TypeScript
- C#
- C
- C++

Depending on the language, ScopeLens can discover information such as:

- imports and dependencies
- classes and interfaces
- methods and functions
- namespaces and packages
- annotations and attributes
- test methods and test functions
- testing-related structures

### Browser Interrogation

ScopeLens can interrogate a running Chrome browser using the Chrome DevTools Protocol (CDP).

Browser discovery includes:

- Pages
- Headings
- Links
- Buttons
- Inputs
- Forms
- Testable elements
- Candidate selectors
- Same-origin navigable links

Selector discovery favors stable selectors such as:

1. `data-testid`
2. element ID
3. name
4. `aria-label`
5. tag/type
6. visible text fallback

Traversal is bounded by configurable page and depth limits.

### Authenticated Browser Interrogation

ScopeLens also supports basic credential-based browser authentication.

Runtime credentials can be supplied along with selectors for:

- username
- password
- submit control

Credentials are used during browser interaction and are not included in the returned ScopeLens context package.

## Requirements

- Python 3.11 or newer
- Google Chrome for browser interrogation
- `websocket-client >= 1.8.0`

## Installation

Install the package:

```bash
pip install scopelens
```

For local development:

```bash
pip install -e .
```

## Quick Start

### Inspect a File or Folder

```python
from scopelens import inspect_target

result = inspect_target("path/to/project")

print(result.target_type)
print(result.candidates)
```

ScopeLens determines whether the supplied target is a file or folder and performs the appropriate interrogation.

### Browser Interrogation

Chrome must be running with remote debugging enabled.

Example on Windows:

```powershell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" `
  --remote-debugging-port=9222 `
  --remote-allow-origins=http://localhost:9222 `
  --user-data-dir="$env:TEMP\scopelens-chrome" `
  https://example.com
```

Then:

```python
from scopelens import interrogate_browser

context = interrogate_browser(
    "http://localhost:9222",
    max_pages=3,
    max_depth=1,
)

print(context["target_type"])
print(context["pages"])
```

### Authenticated Browser Interrogation

```python
from scopelens import interrogate_browser

context = interrogate_browser(
    "http://localhost:9222",
    start_url="https://example.com/login",
    username_selector="#username",
    username="my-user",
    password_selector="#password",
    password="my-password",
    submit_selector="#login",
    max_pages=3,
    max_depth=1,
)
```

Authentication values are runtime inputs and are not returned in the generated context.

## Context Packages

ScopeLens results can be written as JSON context packages for use by downstream applications.

```python
from scopelens import inspect_target
from scopelens.package_writer import write_context_package

result = inspect_target("path/to/project")

write_context_package(
    result,
    "output/context.json",
)
```

Browser interrogation results can also be written using the same package writer.

## Design Philosophy

ScopeLens separates **discovery** from **decision-making**.

Its responsibility is:

> What exists, and what appears relevant?

It deliberately does not decide:

> What should an AI agent, QA system, or development tool do with it?

This separation allows ScopeLens to remain reusable across different applications and workflows.

## ScopeLens 0.1

Version 0.1 establishes the initial foundation for:

- deterministic source interrogation
- multi-language source fact extraction
- relevance-based context discovery
- bounded context generation
- Chrome/CDP browser interrogation
- same-origin browser traversal
- basic authenticated browser interrogation
- reusable JSON context packages

Future versions can extend these capabilities without coupling ScopeLens to a specific consuming application.

## License

See [LICENSE](LICENSE).