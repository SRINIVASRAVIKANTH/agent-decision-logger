"""
audit_trail.logger
-------------------
The "flight recorder" for AI agents.

Wrap ANY function (an agent's tool call, a decision function, an API call)
with @audit_log and every call gets written to a structured, human-readable
log: what it was asked, what it decided, and why.

Usage:
    from audit_trail.logger import audit_log

    @audit_log(agent_name="gis-permit-agent")
    def check_flood_zone(parcel_id: str) -> dict:
        # ... your agent logic ...
        return {
            "decision": "deny",
            "reason": "Parcel overlaps FEMA flood zone AE"
        }
"""

import json
import time
import functools
import uuid
from pathlib import Path
from datetime import datetime, timezone

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "audit_log.jsonl"


def _write_entry(entry: dict) -> None:
    """Append one JSON line to the audit log (JSONL = one JSON object per line)."""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, default=str) + "\n")


def audit_log(agent_name: str):
    """
    Decorator that logs every call to the wrapped function.

    It captures:
      - a unique event id
      - timestamp
      - which agent made the call
      - the function name (what tool/action was used)
      - the inputs given
      - the output returned
      - how long it took
      - whether it errored, and what the error was

    If the function returns a dict containing a "reason" or "explanation"
    key, that's pulled out and stored as the human-readable justification.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            event_id = str(uuid.uuid4())[:8]
            started = time.time()
            timestamp = datetime.now(timezone.utc).isoformat()

            entry = {
                "event_id": event_id,
                "timestamp": timestamp,
                "agent": agent_name,
                "action": func.__name__,
                "inputs": {"args": args, "kwargs": kwargs},
            }

            try:
                result = func(*args, **kwargs)
                entry["output"] = result
                entry["status"] = "success"

                # Pull out a human-readable reason if the agent provided one
                if isinstance(result, dict):
                    entry["reasoning"] = result.get("reason") or result.get("explanation")

                return result

            except Exception as e:
                entry["status"] = "error"
                entry["error"] = str(e)
                raise

            finally:
                entry["duration_ms"] = round((time.time() - started) * 1000, 2)
                _write_entry(entry)

        return wrapper
    return decorator


def read_log(limit: int = 50) -> list:
    """Read the most recent `limit` audit log entries (newest last)."""
    if not LOG_FILE.exists():
        return []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()[-limit:]
    return [json.loads(line) for line in lines]
