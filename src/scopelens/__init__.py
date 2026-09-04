from scopelens.inspector import inspect_target
from scopelens.models import InspectionOptions
from scopelens.package_writer import write_context_package
from scopelens.browser_cdp import interrogate_browser

__version__ = "0.1.0"

__all__ = [
    "inspect_target",
    "InspectionOptions",
    "write_context_package",
    "interrogate_browser",
]