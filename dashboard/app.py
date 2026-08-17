"""
Agent Decision Logger — Audit Dashboard

Run with:  streamlit run dashboard/app.py
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd
from audit_trail.logger import read_log

st.set_page_config(
    page_title="Agent Decision Logger",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
    <style>
        .main { background-color: #fafafa; }
        .block-container { padding-top: 2rem; }
        [data-testid="stMetricValue"] { font-size: 1.9rem; font-weight: 600; }
        h1 { font-weight: 700; letter-spacing: -0.5px; }
        .subtitle { color: #6b7280; font-size: 1.05rem; margin-top: -0.6rem; }
        div[data-testid="stExpander"] { border: 1px solid #e5e7eb; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

st.title("Agent Decision Logger")
st.markdown('<p class="subtitle">Audit dashboard — every decision your AI agents made, and why.</p>', unsafe_allow_html=True)
st.write("")

entries = read_log(limit=500)

if not entries:
    st.info("No log entries yet. Run one of the example scripts first, e.g. `python examples/gis_agent_demo.py`")
    st.stop()

df = pd.DataFrame(entries)

total_events = len(df)
decision_events = df[df["type"].isna()] if "type" in df.columns else df
successes = (decision_events["status"] == "success").sum() if "status" in decision_events.columns else 0
referee_events = (df["type"] == "referee_resolution").sum() if "type" in df.columns else 0
agents_involved = decision_events["agent"].nunique() if "agent" in decision_events.columns else 0
success_rate = f"{(successes / max(len(decision_events), 1)) * 100:.0f}%"

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Events Logged", total_events)
col2.metric("Agent Decisions", len(decision_events))
col3.metric("Success Rate", success_rate)
col4.metric("Referee Resolutions", int(referee_events))
col5.metric("Distinct Agents", int(agents_involved))

st.write("")
st.divider()

if "agent" in decision_events.columns and not decision_events["agent"].dropna().empty:
    st.subheader("Decisions by agent")
    st.caption("Counts individual logged decisions. Referee-resolved conflicts (see below) are tracked separately.")
    agent_counts = decision_events["agent"].value_counts().reset_index()
    agent_counts.columns = ["Agent", "Number of Decisions"]
    st.bar_chart(agent_counts, x="Agent", y="Number of Decisions")

st.write("")
st.subheader("Decision log")

agent_options = ["All agents"] + sorted(decision_events["agent"].dropna().unique().tolist()) if "agent" in decision_events.columns else ["All agents"]
selected_agent = st.selectbox("Filter by agent", agent_options)

display_df = decision_events if selected_agent == "All agents" else decision_events[decision_events["agent"] == selected_agent]

show_cols = [c for c in ["timestamp", "agent", "action", "status", "reasoning"] if c in display_df.columns]
st.dataframe(display_df[show_cols] if show_cols else display_df, use_container_width=True, hide_index=True)

st.write("")

referee_df = df[df["type"] == "referee_resolution"] if "type" in df.columns else pd.DataFrame()
if not referee_df.empty:
    st.subheader("Referee resolutions")
    st.caption("Cases where two agents disagreed, and how the Referee resolved each one.")
    for _, row in referee_df.iterrows():
        a, b = row["agent_a"], row["agent_b"]
        with st.container(border=True):
            c1, c2, c3 = st.columns([1, 1, 1])
            c1.markdown(f"**{a['agent_name']}**\n\n{a['decision']} (confidence {a['confidence']})\n\n_{a['reason']}_")
            c2.markdown(f"**{b['agent_name']}**\n\n{b['decision']} (confidence {b['confidence']})\n\n_{b['reason']}_")
            c3.markdown(f"**Outcome: {row['outcome']}**\n\nResolved by: {row['resolved_by']}")
    st.write("")

with st.expander("View raw log entries (full JSON)"):
    for entry in reversed(entries):
        label = f"{entry.get('timestamp', '')} — {entry.get('agent', entry.get('type', 'event'))}"
        st.markdown(f"**{label}**")
        st.json(entry)
        st.write("")
