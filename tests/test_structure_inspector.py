from scopelens.structure_inspector import inspect_structure


def test_inspect_structure_returns_project_tree(tmp_path):
    src = tmp_path / "src"
    src.mkdir()

    auth = src / "auth"
    auth.mkdir()

    login_file = auth / "login.py"
    login_file.write_text("pass")

    result = inspect_structure(tmp_path)

    paths = {
        item.path
        for item in result.items
    }

    assert "src" in paths
    assert "src/auth" in paths
    assert "src/auth/login.py" in paths

def test_inspect_structure_ignores_default_noise(tmp_path):
    git_dir = tmp_path / ".git"
    git_dir.mkdir()

    git_file = git_dir / "config"
    git_file.write_text("noise")

    src = tmp_path / "src"
    src.mkdir()

    result = inspect_structure(tmp_path)

    paths = {
        item.path
        for item in result.items
    }

    assert ".git" not in paths
    assert ".git/config" not in paths
    assert "src" in paths

def test_inspect_structure_respects_max_items(tmp_path):
    for index in range(10):
        test_file = tmp_path / f"file_{index}.py"
        test_file.write_text("pass")

    result = inspect_structure(
        tmp_path,
        max_items=3,
    )

    assert len(result.items) == 3
    assert result.truncated is True  