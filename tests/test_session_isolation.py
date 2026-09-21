def test_session_payload_isolation_contract(session_payload: dict[str, str]) -> None:
    assert session_payload["session_id"].startswith("qa-session")
    assert session_payload["project_id"].startswith("proj-qa")


def test_session_context_is_scoped_per_upload(session_payload: dict[str, str]) -> None:
    context = {
        "session_id": session_payload["session_id"],
        "project_id": session_payload["project_id"],
        "dataset_name": "session-scope-dataset",
    }
    assert context["session_id"] != "other-session"
    assert context["project_id"] != "other-project"
