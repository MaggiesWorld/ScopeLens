from scopelens.target_resolver import resolve_target


def test_resolve_folder():
    target = resolve_target(".")

    assert target.target_type == "folder"

def test_resolve_file(tmp_path):
    test_file = tmp_path / "sample.txt"
    test_file.write_text("ScopeLens test")

    target = resolve_target(test_file)

    assert target.target_type == "file"