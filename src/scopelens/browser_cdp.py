import json
import urllib.request
import urllib.error
import websocket
import time

from scopelens.browser_facts import extract_browser_facts

def discover_page_targets(
    debugger_url: str,
) -> list[dict]:
    endpoint = f"{debugger_url.rstrip('/')}/json"

    try:
        with urllib.request.urlopen(endpoint) as response:
            targets = json.loads(
                response.read().decode("utf-8")
            )
    except urllib.error.URLError as exc:
        raise ConnectionError(
            "Unable to connect to Chrome debugging endpoint"
        ) from exc
    except json.JSONDecodeError as exc:
        raise ValueError(
            "Invalid response from Chrome debugging endpoint"
        ) from exc

    return [
        {
            "id": target["id"],
            "title": target.get("title"),
            "url": target.get("url"),
            "websocket_url": target.get(
                "webSocketDebuggerUrl"
            ),
        }
        for target in targets
        if target.get("type") == "page"
    ]

def send_cdp_command(
    websocket_url: str,
    method: str,
    params: dict | None = None,
) -> dict:
    command_id = 1

    payload = {
        "id": command_id,
        "method": method,
        "params": params or {},
    }

    try:
        connection = websocket.create_connection(
            websocket_url
        )
    except OSError as exc:
        raise ConnectionError(
            "Unable to connect to Chrome DevTools Protocol"
        ) from exc

    try:
        connection.send(
            json.dumps(payload)
        )

        while True:
            try:
                response = json.loads(
                    connection.recv()
                )
            except json.JSONDecodeError as exc:
                raise ValueError(
                    "Invalid response from Chrome DevTools Protocol"
                ) from exc

            if response.get("id") != command_id:
                continue

            if "error" in response:
                raise RuntimeError(
                    response["error"]
                )

            return response.get(
                "result",
                {},
            )
    finally:
        connection.close()

def evaluate_expression(
    websocket_url: str,
    expression: str,
):
    response = send_cdp_command(
        websocket_url=websocket_url,
        method="Runtime.evaluate",
        params={
            "expression": expression,
            "returnByValue": True,
        },
    )

    return (
        response
        .get("result", {})
        .get("value")
    )

def set_input_value(
    websocket_url: str,
    selector: str,
    value: str,
) -> None:
    selector_json = json.dumps(selector)
    value_json = json.dumps(value)

    expression = f"""
    (() => {{
        const element = document.querySelector({selector_json});

        if (!element) {{
            throw new Error("Input element not found");
        }}

        element.value = {value_json};
        element.dispatchEvent(
            new Event("input", {{ bubbles: true }})
        );
        element.dispatchEvent(
            new Event("change", {{ bubbles: true }})
        );
    }})()
    """

    evaluate_expression(
        websocket_url=websocket_url,
        expression=expression,
    )

def click_element(
    websocket_url: str,
    selector: str,
) -> None:
    selector_json = json.dumps(selector)

    expression = f"""
    (() => {{
        const element = document.querySelector({selector_json});

        if (!element) {{
            throw new Error("Element not found");
        }}

        element.click();
    }})()
    """

    evaluate_expression(
        websocket_url=websocket_url,
        expression=expression,
    )

def login_with_credentials(
    websocket_url: str,
    username_selector: str,
    username: str,
    password_selector: str,
    password: str,
    submit_selector: str,
    timeout: float = 10,
) -> None:
    set_input_value(
        websocket_url=websocket_url,
        selector=username_selector,
        value=username,
    )

    set_input_value(
        websocket_url=websocket_url,
        selector=password_selector,
        value=password,
    )

    original_url = get_current_url(
        websocket_url=websocket_url,
    )

    click_element(
        websocket_url=websocket_url,
        selector=submit_selector,
    )

    if original_url:
        wait_for_url_change(
            websocket_url=websocket_url,
            original_url=original_url,
            timeout=timeout,
        )

    wait_for_document_ready(
        websocket_url=websocket_url,
        timeout=timeout,
    )

def get_page_html(
    websocket_url: str,
) -> str | None:
    return evaluate_expression(
        websocket_url=websocket_url,
        expression="document.documentElement.outerHTML",
    )

def get_current_url(
    websocket_url: str,
) -> str | None:
    return evaluate_expression(
        websocket_url=websocket_url,
        expression="window.location.href",
    )

def inspect_page(
    websocket_url: str,
    url: str,
) -> dict:
    html = get_page_html(
        websocket_url=websocket_url,
    )

    facts = extract_browser_facts(
        html=html or "",
        url=url,
    )

    facts["contains_testable_elements"] = bool(
        facts.get("testable_elements")
    )

    return facts

def inspect_first_page(
    debugger_url: str,
) -> dict:
    targets = discover_page_targets(
        debugger_url=debugger_url,
    )

    if not targets:
        raise RuntimeError(
            "No Chrome page targets available"
        )

    usable_target = next(
        (
            target
            for target in targets
            if target.get("websocket_url")
        ),
        None,
    )

    if usable_target is None:
        raise RuntimeError(
            "No usable Chrome page targets available"
        )

    return inspect_page(
        websocket_url=usable_target["websocket_url"],
        url=usable_target["url"],
    )

def inspect_pages(
    debugger_url: str,
    max_pages: int | None = None,
) -> list[dict]:

    if max_pages is not None and max_pages <= 0:
        raise ValueError(
            "max_pages must be greater than zero"
        )
    
    targets = discover_page_targets(
        debugger_url=debugger_url,
    )

    usable_targets = [
        target
        for target in targets
        if target.get("websocket_url")
    ]

    if max_pages is not None:
        usable_targets = usable_targets[:max_pages]

    return [
        inspect_page(
            websocket_url=target["websocket_url"],
            url=target["url"],
        )
        for target in usable_targets
    ]

def navigate_page(
    websocket_url: str,
    url: str,
) -> dict:
    return send_cdp_command(
        websocket_url=websocket_url,
        method="Page.navigate",
        params={
            "url": url,
        },
    )

def wait_for_page_load(
    websocket_url: str,
    timeout: float = 10,
) -> None:
    connection = websocket.create_connection(
        websocket_url,
        timeout=timeout,
    )

    with connection:
        while True:
            try:
                response = json.loads(
                    connection.recv()
                )
            except websocket.WebSocketTimeoutException as exc:
                raise TimeoutError(
                    "Timed out waiting for page load"
                ) from exc

            if response.get("method") == "Page.loadEventFired":
                return

def wait_for_document_ready(
    websocket_url: str,
    timeout: float = 10,
    poll_interval: float = 0.1,
) -> None:
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        state = evaluate_expression(
            websocket_url=websocket_url,
            expression="document.readyState",
        )

        if state == "complete":
            return

        time.sleep(poll_interval)

    raise TimeoutError(
        "Timed out waiting for document readiness"
    )

def wait_for_url_change(
    websocket_url: str,
    original_url: str,
    timeout: float = 10,
    poll_interval: float = 0.1,
) -> str:
    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        current_url = get_current_url(
            websocket_url=websocket_url,
        )

        if current_url and current_url != original_url:
            return current_url

        time.sleep(poll_interval)

    raise TimeoutError(
        "Timed out waiting for URL change"
    )

def navigate_and_inspect(
    websocket_url: str,
    url: str,
    timeout: float = 10,
) -> dict:
    navigate_page(
        websocket_url=websocket_url,
        url=url,
    )

    wait_for_document_ready(
        websocket_url=websocket_url,
        timeout=timeout,
    )

    return inspect_page(
        websocket_url=websocket_url,
        url=url,
    )

def traverse_pages(
    websocket_url: str,
    start_url: str,
    max_pages: int = 10,
    max_depth: int = 1,
    timeout: float = 10,
) -> list[dict]:
    if max_pages <= 0:
        raise ValueError(
            "max_pages must be greater than zero"
        )

    if max_depth < 0:
        raise ValueError(
            "max_depth must be zero or greater"
        )

    visited = set()
    pending = [
        (start_url, 0),
    ]
    pages = []

    while pending and len(pages) < max_pages:
        url, depth = pending.pop(0)

        if url in visited:
            continue

        visited.add(url)

        facts = navigate_and_inspect(
            websocket_url=websocket_url,
            url=url,
            timeout=timeout,
        )

        pages.append(facts)

        if depth < max_depth:
            for link in facts.get(
                "navigable_links",
                [],
            ):
                if (
                    link not in visited
                    and all(
                        pending_url != link
                        for pending_url, _ in pending
                    )
                ):
                    pending.append(
                        (link, depth + 1)
                    )

    return pages

def traverse_first_page(
    debugger_url: str,
    max_pages: int = 10,
    max_depth: int = 1,
    timeout: float = 10,
) -> list[dict]:

    if max_pages <= 0:
        raise ValueError(
            "max_pages must be greater than zero"
        )

    if max_depth < 0:
        raise ValueError(
            "max_depth must be zero or greater"
        )
    
    targets = discover_page_targets(
        debugger_url=debugger_url,
    )

    usable_target = next(
        (
            target
            for target in targets
            if target.get("websocket_url")
        ),
        None,
    )

    if usable_target is None:
        raise RuntimeError(
            "No usable Chrome page targets available"
        )

    return traverse_pages(
        websocket_url=usable_target["websocket_url"],
        start_url=usable_target["url"],
        max_pages=max_pages,
        max_depth=max_depth,
        timeout=timeout,
    )

def build_browser_context(
    start_url: str,
    pages: list[dict],
) -> dict:
    return {
        "target_type": "browser",
        "start_url": start_url,
        "page_count": len(pages),
        "pages": pages,
    }

def interrogate_browser(
    debugger_url: str,
    start_url: str | None = None,
    max_pages: int = 10,
    max_depth: int = 1,
    timeout: float = 10,
    username_selector: str | None = None,
    username: str | None = None,
    password_selector: str | None = None,
    password: str | None = None,
    submit_selector: str | None = None,
) -> dict:

    auth_values = [
        username_selector,
        username,
        password_selector,
        password,
        submit_selector,
    ]

    if any(auth_values) and not all(auth_values):
        raise ValueError(
            "Incomplete browser authentication configuration"
        )
 
    if all(
        [
            username_selector,
            username,
            password_selector,
            password,
            submit_selector,
        ]
    ):
        targets = discover_page_targets(
            debugger_url=debugger_url,
        )

        usable_target = next(
            (
                target
                for target in targets
                if target.get("websocket_url")
            ),
            None,
        )

        if usable_target is None:
            raise RuntimeError(
                "No usable Chrome page targets available"
            )

        if start_url:
            navigate_and_inspect(
                websocket_url=usable_target["websocket_url"],
                url=start_url,
                timeout=timeout,
            )

        login_with_credentials(
            websocket_url=usable_target["websocket_url"],
            username_selector=username_selector,
            username=username,
            password_selector=password_selector,
            password=password,
            submit_selector=submit_selector,
            timeout=timeout,
        )

        current_url = get_current_url(
            websocket_url=usable_target["websocket_url"],
        )

        pages = traverse_pages(
            websocket_url=usable_target["websocket_url"],
            start_url=current_url or start_url or usable_target["url"],
            max_pages=max_pages,
            max_depth=max_depth,
            timeout=timeout,
        )
    else:
        pages = traverse_first_page(
            debugger_url=debugger_url,
            max_pages=max_pages,
            max_depth=max_depth,
            timeout=timeout,
        )

    resolved_start_url = start_url

    if resolved_start_url is None and pages:
        resolved_start_url = pages[0].get("url")

    return build_browser_context(
        start_url=resolved_start_url,
        pages=pages,
    )