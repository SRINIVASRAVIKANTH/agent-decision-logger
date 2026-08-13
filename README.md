# 🛫 Agent Decision Logger

**A "flight recorder" and "referee" for AI agents — so you can see exactly what your agents did, and why, and resolve it when two agents disagree.**

AI agents are being deployed everywhere — but companies keep killing these projects for one repeated reason: **nobody can trust or explain what the agent actually did.** This project is a small, reusable middleware that fixes that: it wraps any agent's decisions in a transparent, auditable log, and provides a rule-based "referee" to resolve conflicts between two agents instead of letting one silently override the other.

It's intentionally domain-agnostic — the same tool is demoed here plugged into a **GIS permitting agent** and a **healthcare claims agent**, to show it works as general infrastructure, not a one-off script.

---

## Why this matters

- **40% of agentic AI projects are projected to be canceled by 2027**, largely due to unclear business value and governance challenges — not lack of capability.
- In healthcare specifically, **multi-agent systems often produce conflicting decisions**, and there's no standard way to arbitrate between them.
- In geospatial AI, agents are known to **"hallucinate" — inferring roads, zones, or facts that don't actually exist** — with no lightweight way to catch or log that.

This project targets that trust gap directly, instead of building another single-purpose chatbot.

---

## What it does

| Component | What it's for |
|---|---|
| `audit_trail/logger.py` | A Python decorator (`@audit_log`) you put on any agent function. Every call gets automatically logged: what it was asked, what it decided, why, and how long it took. |
| `audit_trail/referee.py` | When two agents disagree, `resolve()` compares their confidence and reasoning, and either auto-resolves or flags it for a human — with the full reasoning preserved. |
| `dashboard/app.py` | A simple Streamlit dashboard to browse the audit log in a readable table instead of raw JSON. |
| `examples/` | Two working demos — a GIS permit-checking agent, and a healthcare claims-vs-fraud agent conflict — showing the tool works across domains. |

---

## Demo

**1. A GIS agent's decision, fully logged:**
```
check_flood_zone("PARCEL-4521")
→ {'decision': 'deny', 'reason': 'Parcel PARCEL-4521 overlaps FEMA flood zone AE'}
```
Every call like this is automatically written to `logs/audit_log.jsonl` — no extra code needed in the agent itself.

**2. Two healthcare agents disagree, and the referee resolves it:**
```
Claims-approval-agent:  approve (confidence 0.72) — "Procedure code matches policy coverage"
Fraud-detection-agent:  deny    (confidence 0.91) — "Billing pattern matches known fraud signature"

Referee outcome: deny (resolved by higher_confidence: fraud-detection-agent)
```

![dashboard screenshot](screenshots/dashboard-view.png)

---

## Quickstart

```bash
# 1. Clone this repo
git clone https://github.com/YOUR-USERNAME/agent-decision-logger.git
cd agent-decision-logger

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run a demo agent
python examples/gis_agent_demo.py
python examples/healthcare_agent_demo.py

# 4. View the results in the dashboard
streamlit run dashboard/app.py
```

---

## How to use it in your own agent

Just add one decorator to any function your agent uses to make a decision:

```python
from audit_trail import audit_log

@audit_log(agent_name="my-agent")
def my_decision_function(input_data):
    # ...your logic...
    return {"decision": "approve", "reason": "explain why here"}
```

Every call is now automatically logged — no other changes needed.

---

## Roadmap

- [ ] Add a web-based (not just local) hosted dashboard
- [ ] Support more than 2 agents in the referee
- [ ] Add real GIS data (OpenStreetMap) to the GIS demo instead of mock data
- [ ] Add a REST API so any agent (in any language) can log to this via HTTP

---

## Why I built this

I'm a GIS/AI engineer, and I kept seeing the same problem across projects: AI agents make decisions, but nobody can easily see *why*, and when two agents disagree there's no clean process for resolving it. This is a small, focused tool that solves that specific trust gap.

## License

MIT — see [LICENSE](LICENSE).
