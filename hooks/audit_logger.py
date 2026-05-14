"""
hooks/audit_logger.py

Post-analysis hook — runs automatically after every /analyze-contract execution.
Appends a structured JSON record to the audit log.

In a HIPAA-compliant clinical environment, every AI-assisted contract analysis
must be traceable: who ran it, on what document, what was found, when.
This hook enforces that requirement automatically — the analyst doesn't have
to remember to log anything.
"""

import json
import sys
import os
from datetime import datetime, timezone


def log_analysis(result: dict, contract_path: str):
    log_path = os.environ.get("AUDIT_LOG_PATH", "./logs/contract_analysis.jsonl")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "contract_file": contract_path,
        "study_type": result.get("study_type"),
        "confidence_pct": result.get("confidence"),
        "master_items_loaded": result.get("master_items_loaded"),
        "items_found": result.get("items_found"),
        "items_missing": result.get("items_missing"),
        "clauses_flagged": result.get("clauses_flagged"),
        "analyst": os.environ.get("USER", "unknown"),
        "model": "claude-sonnet-4-20250514",
        "skill_version": "1.0.0"
    }

    with open(log_path, "a") as f:
        f.write(json.dumps(record) + "\n")

    print(f"[audit_logger] Record written to {log_path}", file=sys.stderr)


if __name__ == "__main__":
    # Called by Claude Code hook system after skill completion
    # Reads result JSON from stdin
    try:
        result = json.loads(sys.stdin.read())
        contract_path = sys.argv[1] if len(sys.argv) > 1 else "unknown"
        log_analysis(result, contract_path)
    except Exception as e:
        print(f"[audit_logger] Warning: logging failed — {e}", file=sys.stderr)
