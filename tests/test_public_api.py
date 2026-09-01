import scopelens


def test_public_api(tmp_path):
    print(f"Temporary path: {tmp_path}")

    source_dir = tmp_path / "source"
    source_dir.mkdir()

    source_file = source_dir / "login.py"
    source_file.write_text(
        "def login_user():\n"
        "    return authenticate_user()"
    )

    result = scopelens.inspect_target(
        source_dir,
        options=scopelens.InspectionOptions(
            description="login authentication",
        ),
    )

    assert result.candidates