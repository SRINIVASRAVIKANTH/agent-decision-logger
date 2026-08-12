"""
Simple dashboard to view the audit trail log in a readable table.

Run with:  streamlit run dashboard/app.py
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
import pandas as pd
from audit_trail.logger import read_log

st.set_page_config(page_title="Agent Audit Trail", layout="wide")
st.title("🛫 Agent Audit Trail — Flight Recorder for AI Agents")
st.caption("Every decision your AI agents make, with the reasoning behind it.")

entries = read_log(limit=200)

if not entries:
    st.info("No log entries yet. Run one of the example scripts first, e.g.:\n\n"
            "`python examples/gis_agent_demo.py`")
else:
    df = pd.DataFrame(entries)
    st.dataframe(df, use_container_width=True)

    st.subheader("Raw entries")
    for entry in reversed(entries):
        with st.expander(f"{entry.get('timestamp', '')} — {entry.get('agent', entry.get('type', 'event'))}"):
            st.json(entry)
