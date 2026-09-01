"""
REST API routes for Kalki.

Provides endpoints for:
- Alert submission and retrieval
- Incident management
- Playbook execution
- System metrics
"""

from __future__ import annotations

import json
from typing import Any

try:
    from flask import Flask, Blueprint, request, jsonify, Response
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False

from kalki.ingest import ingest_log
from kalki.triage import triage_alert
from kalki.investigate import investigate_alert
from kalki.correlate import correlate_alerts
from kalki.schemas import AlertStatus, OCSFAlert, Severity
from kalki.store import alert_store, incident_store


def create_api_app() -> Any:
    """Create and configure the Flask API application."""
    if not HAS_FLASK:
        raise ImportError("Flask is required for the API. Install with: pip install flask")

    app = Flask(__name__)
    api = Blueprint("api", __name__, url_prefix="/api/v1")

    # ── Alert endpoints ──────────────────────────────────────────

    @api.route("/alerts", methods=["POST"])
    def submit_alert():
        """Submit a raw log for ingestion and triage."""
        data = request.get_json(force=True)
        raw_log = data.get("raw_log", "")
        if not raw_log:
            return jsonify({"error": "raw_log field is required"}), 400

        alert = ingest_log(raw_log)
        alert = triage_alert(alert)
        alert_store.update(alert)

        return jsonify({
            "alert_id": alert.alert_id,
            "severity": alert.severity.name,
            "verdict": alert.verdict.value,
            "status": alert.status.value,
            "mitre_tactic": alert.mitre_tactic,
            "mitre_technique": alert.mitre_technique,
        }), 201

    @api.route("/alerts", methods=["GET"])
    def list_alerts():
        """List alerts with optional filtering."""
        status = request.args.get("status")
        severity = request.args.get("severity")
        limit = int(request.args.get("limit", 50))

        status_filter = AlertStatus(status) if status else None
        severity_filter = Severity[severity.upper()] if severity else None

        alerts = alert_store.list_all(
            status=status_filter,
            severity=severity_filter,
            limit=limit,
        )
        return jsonify({
            "count": len(alerts),
            "alerts": [a.to_dict() for a in alerts],
        })

    @api.route("/alerts/<alert_id>", methods=["GET"])
    def get_alert(alert_id: str):
        """Get a specific alert by ID."""
        alert = alert_store.get(alert_id)
        if not alert:
            return jsonify({"error": "Alert not found"}), 404
        return jsonify(alert.to_dict())

    @api.route("/alerts/<alert_id>/investigate", methods=["POST"])
    def investigate(alert_id: str):
        """Run investigation on an alert."""
        alert = alert_store.get(alert_id)
        if not alert:
            return jsonify({"error": "Alert not found"}), 404
        report = investigate_alert(alert)
        return jsonify(report.to_dict())

    # ── Incident endpoints ───────────────────────────────────────

    @api.route("/incidents", methods=["GET"])
    def list_incidents():
        """List all incidents."""
        status = request.args.get("status")
        incidents = incident_store.list_all(status=status)
        return jsonify({
            "count": len(incidents),
            "incidents": [i.to_dict() for i in incidents],
        })

    @api.route("/incidents/<incident_id>", methods=["GET"])
    def get_incident(incident_id: str):
        """Get a specific incident."""
        incident = incident_store.get(incident_id)
        if not incident:
            return jsonify({"error": "Incident not found"}), 404
        return jsonify(incident.to_dict())

    @api.route("/correlate", methods=["POST"])
    def run_correlation():
        """Trigger correlation engine on current alerts."""
        incidents = correlate_alerts()
        return jsonify({
            "incidents_created": len(incidents),
            "incidents": [i.to_dict() for i in incidents],
        })

    @api.route("/incidents/<incident_id>/report", methods=["GET"])
    def generate_report(incident_id: str):
        """Generate a downloadable Markdown report for the incident."""
        incident = incident_store.get(incident_id)
        if not incident:
            return jsonify({"error": "Incident not found"}), 404
            
        md = [f"# Incident Report: {incident.incident_id}"]
        md.append(f"**Severity**: {incident.severity.name}")
        md.append(f"**Kill Chain Phase**: {incident.kill_chain_phase or 'Unknown'}")
        md.append(f"**Mitre Tactics**: {', '.join(incident.mitre_tactics) if incident.mitre_tactics else 'None'}")
        md.append(f"**Correlated Alerts**: {len(incident.alert_ids)}")
        md.append(f"**Status**: {incident.status}")
        
        all_iocs = []
        all_timeline = []
        all_recs = []
        lm_detected = False
        
        for aid in incident.alert_ids:
            alert = alert_store.get(aid)
            if alert:
                report = investigate_alert(alert)
                all_iocs.extend(report.iocs)
                all_timeline.extend(report.timeline)
                all_recs.extend(report.recommendations)
                if report.lateral_movement_detected:
                    lm_detected = True
                    
        # Deduplicate
        seen_iocs = set()
        uniq_iocs = []
        for ioc in all_iocs:
            key = (ioc.ioc_type, ioc.value)
            if key not in seen_iocs:
                seen_iocs.add(key)
                uniq_iocs.append(ioc)
                
        uniq_recs = list(dict.fromkeys(all_recs))
        
        md.append("\n## Lateral Movement")
        md.append(f"{'Detected' if lm_detected else 'None detected'}")
        
        md.append("\n## Indicators of Compromise (IOCs)")
        if uniq_iocs:
            for ioc in uniq_iocs:
                md.append(f"- **{ioc.ioc_type}**: {ioc.value} (Confidence: {ioc.confidence})")
        else:
            md.append("None extracted.")
            
        md.append("\n## Timeline")
        # Sort and dedup timeline
        seen_times = set()
        for ev in sorted(all_timeline, key=lambda x: x["timestamp"]):
            key = (ev["timestamp"], ev["alert_id"])
            if key not in seen_times:
                seen_times.add(key)
                md.append(f"- **{ev['timestamp']}** [{ev['severity']}] (Alert {ev['alert_id']}): {ev['activity']}")
                
        md.append("\n## Recommendations")
        for rec in uniq_recs:
            md.append(f"- {rec}")
            
        if incident.assigned_playbook:
            md.append(f"\n## Playbook Execution")
            md.append(f"Assigned Playbook: {incident.assigned_playbook}")
            
        content = "\n".join(md)
        return Response(
            content,
            mimetype="text/markdown",
            headers={"Content-Disposition": f"attachment;filename=incident_{incident_id}.md"}
        )

    # ── Metrics endpoint ─────────────────────────────────────────

    @api.route("/metrics", methods=["GET"])
    def metrics():
        """System metrics and health."""
        alerts = alert_store.list_all(limit=10000)
        severity_dist = {}
        status_dist = {}
        for alert in alerts:
            severity_dist[alert.severity.name] = severity_dist.get(alert.severity.name, 0) + 1
            status_dist[alert.status.value] = status_dist.get(alert.status.value, 0) + 1

        return jsonify({
            "total_alerts": alert_store.count(),
            "total_incidents": incident_store.count(),
            "severity_distribution": severity_dist,
            "status_distribution": status_dist,
        })

    # ── Batch ingestion ──────────────────────────────────────────

    @api.route("/ingest/batch", methods=["POST"])
    def batch_ingest():
        """Ingest multiple raw logs at once."""
        data = request.get_json(force=True)
        logs = data.get("logs", [])
        if not logs:
            return jsonify({"error": "logs array is required"}), 400

        results = []
        for raw in logs:
            alert = ingest_log(raw)
            alert = triage_alert(alert)
            alert_store.update(alert)
            results.append({
                "alert_id": alert.alert_id,
                "severity": alert.severity.name,
                "verdict": alert.verdict.value,
            })

        return jsonify({"ingested": len(results), "alerts": results}), 201

    # ── Simulation endpoint ──────────────────────────────────────

    @api.route("/simulate", methods=["POST"])
    def run_simulation():
        """Run the demo simulation directly inside the Flask process to populate the dashboard."""
        import threading
        from kalki.cli import run_demo
        def _run():
            try:
                run_demo("sample_data/demo_fixed.log")
            except Exception as e:
                print(f"Simulation error: {e}")
        threading.Thread(target=_run).start()
        return jsonify({"status": "Simulation started in background"}), 200

    # ── Endpoint Agent endpoint ──────────────────────────────────

    agent_state = {"running": False}

    @api.route("/agent/toggle", methods=["POST"])
    def toggle_agent():
        """Start or stop the real-time endpoint agent."""
        data = request.get_json(force=True, silent=True) or {}
        action = data.get("action")
        
        if action == "start":
            if not agent_state["running"]:
                agent_state["running"] = True
                import threading
                import sys
                import os
                # Add project root to path
                root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
                if root_dir not in sys.path:
                    sys.path.append(root_dir)
                try:
                    from endpoint_agent import run_agent_loop
                    threading.Thread(target=run_agent_loop, args=(lambda: agent_state["running"],)).start()
                except ImportError:
                    agent_state["running"] = False
                    return jsonify({"error": "endpoint_agent module not found"}), 500
            return jsonify({"status": "running"}), 200
            
        elif action == "stop":
            agent_state["running"] = False
            return jsonify({"status": "stopped"}), 200
            
        return jsonify({"status": "running" if agent_state["running"] else "stopped"}), 200

    app.register_blueprint(api)
    return app
