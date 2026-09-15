from codecision.web import create_app


def test_consent_is_required(tmp_path) -> None:
    client = create_app(tmp_path / "study.db", trials=2).test_client()
    response = client.post("/api/session", json={"consent": False})
    assert response.status_code == 400


def test_session_decision_export_and_deletion(tmp_path) -> None:
    client = create_app(tmp_path / "study.db", trials=1).test_client()
    started = client.post(
        "/api/session", json={"consent": True, "condition": "adaptive_codecision"}
    )
    session = started.get_json()
    result = client.post(
        "/api/decision",
        json={
            "session_id": session["session_id"],
            "decision": 1,
            "confidence": 0.6,
            "latency_seconds": 2.4,
            "hesitation": 0.2,
            "revisions": 0,
        },
    )
    assert result.status_code == 200
    assert result.get_json()["complete"] is True
    assert client.get(f"/api/export/{session['session_id']}.csv").status_code == 200
    deleted = client.delete(f"/api/session/{session['session_id']}")
    assert deleted.get_json()["deleted"] is True
