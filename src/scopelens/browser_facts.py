from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse, urlunparse


def build_selector_candidates(
    tag: str,
    attrs: dict,
) -> list[str]:
    selectors = []

    data_testid = attrs.get("data-testid")
    element_id = attrs.get("id")
    name = attrs.get("name")
    aria_label = attrs.get("aria-label")
    element_type = attrs.get("type")

    if data_testid:
        selectors.append(
            f'[data-testid="{data_testid}"]'
        )

    if element_id:
        selectors.append(
            f"#{element_id}"
        )

    if name:
        selectors.append(
            f'[name="{name}"]'
        )

    if aria_label:
        selectors.append(
            f'[aria-label="{aria_label}"]'
        )

    if not selectors and element_type:
        selectors.append(
            f'{tag}[type="{element_type}"]'
        )

    return selectors


class BrowserFactsParser(HTMLParser):
    def __init__(self):
        super().__init__()

        self.title = None
        self.headings = []
        self.buttons = []
        self.inputs = []
        self.links = []
        self.forms = []

        self._current_tag = None
        self._current_attrs = {}
        self._text_buffer = []
        self.testable_elements = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        if tag in {"input", "button", "select", "textarea", "a"}:
            self.testable_elements.append(
                {
                    "tag": tag,
                    "id": attrs.get("id"),
                    "name": attrs.get("name"),
                    "data_testid": attrs.get("data-testid"),
                    "aria_label": attrs.get("aria-label"),
                    "selectors": build_selector_candidates(
                        tag,
                        attrs,
                    ),
                }
            )

        if tag in {"title", "h1", "h2", "h3", "h4", "h5", "h6", "button", "a"}:
            self._current_tag = tag
            self._current_attrs = attrs
            self._text_buffer = []

        elif tag == "input":
            self.inputs.append(
                {
                    "id": attrs.get("id"),
                    "name": attrs.get("name"),
                    "type": attrs.get("type"),
                }
            )

        elif tag == "form":
            self.forms.append(
                {
                    "id": attrs.get("id"),
                }
            )

    def handle_data(self, data):
        if self._current_tag:
            self._text_buffer.append(data)

    def handle_endtag(self, tag):
        if tag != self._current_tag:
            return

        text = "".join(self._text_buffer).strip()

        if tag == "title":
            self.title = text

        elif tag.startswith("h") and len(tag) == 2:
            if text:
                self.headings.append(text)

        elif tag == "button":
            self.buttons.append(
                {
                    "text": text,
                    "id": self._current_attrs.get("id"),
                    "type": self._current_attrs.get("type"),
                }
            )

            if (
                self.testable_elements
                and self.testable_elements[-1]["tag"] == "button"
                and not self.testable_elements[-1]["selectors"]
                and text
            ):
                self.testable_elements[-1]["selectors"] = [
                    f'text="{text}"'
                ]

        elif tag == "a":
            self.links.append(
                {
                    "text": text,
                    "href": self._current_attrs.get("href"),
                }
            )

            if (
                self.testable_elements
                and self.testable_elements[-1]["tag"] == "a"
                and not self.testable_elements[-1]["selectors"]
                and text
            ):
                self.testable_elements[-1]["selectors"] = [
                    f'text="{text}"'
                ]

        self._current_tag = None
        self._current_attrs = {}
        self._text_buffer = []


def extract_browser_facts(
    html: str,
    url: str,
) -> dict:
    parser = BrowserFactsParser()
    parser.feed(html)

    base_origin = urlparse(url)

    navigable_links = []

    for link in parser.links:
        href = link.get("href")

        if not href:
            continue

        if href.startswith("#"):
            continue

        if href.lower().startswith("javascript:"):
            continue

        resolved_url = urljoin(
            url,
            href,
        )

        parsed_url = urlparse(
            resolved_url
        )

        resolved_url = urlunparse(
            parsed_url._replace(fragment="")
        )

        resolved_origin = urlparse(
            resolved_url
        )

        if (
            resolved_origin.scheme == base_origin.scheme
            and resolved_origin.netloc == base_origin.netloc
        ):
            if resolved_url not in navigable_links:
                navigable_links.append(
                    resolved_url
                )

    return {
        "url": url,
        "title": parser.title,
        "headings": parser.headings,
        "buttons": parser.buttons,
        "inputs": parser.inputs,
        "links": parser.links,
        "forms": parser.forms,
        "testable_elements": parser.testable_elements,
        "navigable_links": navigable_links,
        "extraction_status": "success",
        "extraction_reason": None,
    }