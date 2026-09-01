from pathlib import Path

from scopelens.ignore_rules import should_ignore


def test_ignores_virtual_environment():
    assert should_ignore(
        Path(".venv/Lib/site-packages/example.py")
    )


def test_ignores_node_modules():
    assert should_ignore(
        Path("frontend/node_modules/example.js")
    )


def test_does_not_ignore_source():
    assert not should_ignore(
        Path("src/scopelens/inspector.py")
    )

def test_custom_ignore_rules():
    assert should_ignore(
        Path("generated/output.py"),
        ignored_names={"generated"},
    )