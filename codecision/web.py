"""Local participant study interface and telemetry API."""

from __future__ import annotations

import argparse
import csv
import io
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, Response, jsonify, render_template, request

from .agents import HumanResponse, SimulatedAI
from .config import ExperimentConfig, PolicyName
from .engine import CodecisionEngine
from .storage import StudyStore
from .tasks import ThreatEvent, generate_events
from .trust import update_trust


@dataclass
class LiveSession:
    session_id: str
    policy: PolicyName
    events: list[ThreatEvent]
    ai: SimulatedAI
    engine: CodecisionEngine
    index: int = 0
    recent_errors: list[int] = field(default_factory=list)
    records: list[dict[str, object]] = field(default_factory=list)
    pending: tuple[object, ThreatEvent, object] | None = None

    @property
    def error_rate(self) -> float:
        return sum(self.recent_errors[-12:]) / max(1, len(self.recent_errors[-12:]))


def create_app(database: Path = Path("study_data/pilot.db"), trials: int = 24) -> Flask:
    app = Flask(__name__)
    app.config["JSON_SORT_KEYS"] = False
    store = StudyStore(database)
    sessions: dict[str, LiveSession] = {}

    @app.get("/")
    def index() -> str:
        return render_template("index.html")

    @app.post("/api/session")
    def start_session() -> tuple[Response, int] | Response:
        payload = request.get_json(silent=True) or {}
        if payload.get("consent") is not True:
            return jsonify({"error": "informed consent is required"}), 400
        requested = payload.get("condition")
        try:
            policy = PolicyName(requested) if requested else secrets.choice(list(PolicyName)[:3])
        except ValueError:
            return jsonify({"error": "unknown condition"}), 400
        session_id = secrets.token_urlsafe(12)
        seed = secrets.randbelow(1_000_000)
        config = ExperimentConfig(trials_per_condition=trials)
        live = LiveSession(
            session_id,
            policy,
            generate_events(trials, seed),
            SimulatedAI(config.ai_skill, seed + 200),
            CodecisionEngine(config, policy, seed),
        )
        sessions[session_id] = live
        store.create_session(session_id, policy.value, datetime.now(timezone.utc).isoformat())
        return jsonify(
            {"session_id": session_id, "condition": policy.value, "trial": _next_trial(live)}
        )

    @app.post("/api/decision")
    def decision() -> tuple[Response, int] | Response:
        payload = request.get_json(silent=True) or {}
        live = sessions.get(str(payload.get("session_id", "")))
        if live is None:
            return jsonify({"error": "unknown or expired session"}), 404
        if live.index >= len(live.events):
            return jsonify({"error": "session already complete"}), 409
        try:
            human = HumanResponse(
                decision=int(payload["decision"]),
                confidence=float(payload["confidence"]),
                latency_seconds=float(payload["latency_seconds"]),
                hesitation=float(payload.get("hesitation", 0)),
                revisions=int(payload.get("revisions", 0)),
                workload=float(payload.get("workload", 0.5)),
            )
        except (KeyError, TypeError, ValueError):
            return jsonify({"error": "invalid decision telemetry"}), 400
        event = live.events[live.index]
        ai = live.ai.decide(event, shifted=live.index >= int(len(live.events) * 0.75))
        record, intervention, uncertainty = live.engine.process(
            event, human, ai, live.error_rate, live.index + 1, simulate_contest=False
        )
        if intervention.mode.value == "override" and intervention.contestable:
            live.pending = (record, event, intervention)
            return jsonify(
                {
                    "requires_resolution": True,
                    "intervention": {
                        "mode": intervention.mode.value,
                        "ai_decision": record.ai_decision,
                        "human_decision": record.human_decision,
                        "explanation": intervention.explanation,
                    },
                }
            )
        stored = record.to_dict()
        stored["synthetic"] = 0
        live.records.append(stored)
        live.recent_errors.append(int(not record.correct))
        store.save_trial(live.session_id, live.index + 1, event.event_id, stored)
        live.index += 1
        complete = live.index >= len(live.events)
        if complete:
            store.complete(live.session_id)
        return jsonify(
            {
                "result": {
                    "intervention_mode": intervention.mode.value,
                    "final_decision": record.final_decision,
                    "correct": bool(record.correct),
                    "uncertainty": uncertainty.score,
                    "trust": record.trust_after,
                    "explanation": intervention.explanation,
                    "contestable": intervention.contestable,
                },
                "complete": complete,
                "next_trial": None if complete else _next_trial(live),
            }
        )

    @app.post("/api/resolve")
    def resolve_override() -> tuple[Response, int] | Response:
        payload = request.get_json(silent=True) or {}
        live = sessions.get(str(payload.get("session_id", "")))
        if live is None or live.pending is None:
            return jsonify({"error": "no override is awaiting resolution"}), 409
        record, event, _intervention = live.pending
        contested = bool(payload.get("contest"))
        record.contested = int(contested)
        record.accepted = int(not contested)
        record.final_decision = record.human_decision if contested else record.ai_decision
        record.correct = int(record.final_decision == event.ground_truth)
        record.unnecessary_override = int(
            not contested
            and record.human_decision == event.ground_truth
            and record.ai_decision != event.ground_truth
        )
        live.engine.trust = update_trust(
            record.trust_before,
            record.ai_decision == event.ground_truth,
            True,
            not contested,
        )
        record.trust_after = live.engine.trust
        live.pending = None
        stored = record.to_dict()
        stored["synthetic"] = 0
        live.records.append(stored)
        live.recent_errors.append(int(not record.correct))
        store.save_trial(live.session_id, live.index + 1, event.event_id, stored)
        live.index += 1
        complete = live.index >= len(live.events)
        if complete:
            store.complete(live.session_id)
        return jsonify(
            {
                "result": {
                    "intervention_mode": "override",
                    "correct": bool(record.correct),
                    "trust": record.trust_after,
                    "explanation": (
                        "Override contested; human decision restored."
                        if contested
                        else "Override accepted; AI decision applied."
                    ),
                },
                "complete": complete,
                "next_trial": None if complete else _next_trial(live),
            }
        )

    @app.get("/api/export/<session_id>.csv")
    def export_session(session_id: str) -> tuple[Response, int] | Response:
        live = sessions.get(session_id)
        if live is None or not live.records:
            return jsonify({"error": "no session data available"}), 404
        stream = io.StringIO()
        writer = csv.DictWriter(stream, fieldnames=list(live.records[0]))
        writer.writeheader()
        writer.writerows(live.records)
        return Response(
            stream.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": f"attachment; filename={session_id}.csv"},
        )

    @app.delete("/api/session/<session_id>")
    def delete_session(session_id: str) -> Response:
        sessions.pop(session_id, None)
        return jsonify({"deleted": store.delete_session(session_id)})

    return app


def _next_trial(session: LiveSession) -> dict[str, object]:
    event = session.events[session.index]
    visible = event.public_view()
    visible["trial_index"] = session.index + 1
    visible["total_trials"] = len(session.events)
    return visible


def main() -> None:
    parser = argparse.ArgumentParser(description="Launch the local codecision study")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5050)
    parser.add_argument("--trials", type=int, default=24)
    parser.add_argument("--database", type=Path, default=Path("study_data/pilot.db"))
    args = parser.parse_args()
    create_app(args.database, args.trials).run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()
