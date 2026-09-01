import scopelens


def test_ranks_relevant_project_files(tmp_path):
    project = tmp_path / "sample_project"
    project.mkdir()

    auth_dir = project / "auth"
    auth_dir.mkdir()

    reports_dir = project / "reports"
    reports_dir.mkdir()

    login_service = auth_dir / "login_service.py"
    login_service.write_text(
        "def authenticate_user(username, password):\n"
        "    return create_session(username)\n"
    )

    session_service = auth_dir / "session.py"
    session_service.write_text(
        "def create_session(user):\n"
        "    return {'user': user}\n"
    )

    report_file = reports_dir / "monthly_report.py"
    report_file.write_text(
        "def generate_monthly_report():\n"
        "    pass\n"
    )

    result = scopelens.inspect_target(
        project,
        options=scopelens.InspectionOptions(
            description="login authentication session",
            max_candidates=5,
        ),
    )

    for candidate in result.candidates:
        print(
            candidate.name,
            candidate.relevance_score,
        )

    assert result.candidates

    candidate_names = [
        candidate.name
        for candidate in result.candidates
    ]

    assert "auth/login_service.py" in candidate_names
    assert "auth/session.py" in candidate_names

    assert candidate_names.index(
        "auth/login_service.py"
    ) < candidate_names.index(
        "reports/monthly_report.py"
    ) if "reports/monthly_report.py" in candidate_names else True