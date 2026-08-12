"""
Demo: two healthcare agents disagree on an insurance claim,
and the referee resolves it.

Run with:  python examples/healthcare_agent_demo.py
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from audit_trail import resolve, AgentDecision

# Agent A: a claims-approval agent
claims_agent = AgentDecision(
    agent_name="claims-approval-agent",
    decision="approve",
    confidence=0.72,
    reason="Procedure code matches policy coverage rules."
)

# Agent B: a fraud-detection agent
fraud_agent = AgentDecision(
    agent_name="fraud-detection-agent",
    decision="deny",
    confidence=0.91,
    reason="Billing pattern matches known upcoding fraud signature."
)

if __name__ == "__main__":
    result = resolve(claims_agent, fraud_agent)
    print("Referee decision:")
    print(f"  Outcome:     {result['outcome']}")
    print(f"  Resolved by: {result['resolved_by']}")
    print("\nFull reasoning from both agents was written to logs/audit_log.jsonl.")
