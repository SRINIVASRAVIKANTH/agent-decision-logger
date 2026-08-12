"""
audit_trail.referee
--------------------
The "judge" for when two AI agents disagree.

When Agent A and Agent B each produce a decision + confidence + reasoning,
the referee compares them and either:
  1. Auto-resolves (if one agent is clearly more confident / more relevant), or
  2. Escalates to a human with both sides laid out clearly.

This is intentionally simple and rule-based — the point isn't a fancy model,
it's an auditable, explainable resolution process.
"""

from dataclasses import dataclass
from .logger import _write_entry
from datetime import datetime, timezone
import uuid


@dataclass
class AgentDecision:
    agent_name: str
    decision: str          # e.g. "approve" / "deny" / "flag"
    confidence: float       # 0.0 - 1.0
    reason: str


def resolve(decision_a: AgentDecision, decision_b: AgentDecision, confidence_gap: float = 0.15):
    """
    Compare two agent decisions.

    Returns a dict with:
      - "outcome": the resolved decision, or "ESCALATE_TO_HUMAN"
      - "resolved_by": how it was decided
      - full details of both agents' reasoning (for the audit trail)
    """
    result = {
        "event_id": str(uuid.uuid4())[:8],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "type": "referee_resolution",
        "agent_a": decision_a.__dict__,
        "agent_b": decision_b.__dict__,
    }

    if decision_a.decision == decision_b.decision:
        result["outcome"] = decision_a.decision
        result["resolved_by"] = "agreement"

    elif abs(decision_a.confidence - decision_b.confidence) >= confidence_gap:
        winner = decision_a if decision_a.confidence > decision_b.confidence else decision_b
        result["outcome"] = winner.decision
        result["resolved_by"] = f"higher_confidence ({winner.agent_name}: {winner.confidence})"

    else:
        # Confidences too close to call automatically — don't guess, ask a human
        result["outcome"] = "ESCALATE_TO_HUMAN"
        result["resolved_by"] = "confidence_too_close"

    _write_entry(result)
    return result
