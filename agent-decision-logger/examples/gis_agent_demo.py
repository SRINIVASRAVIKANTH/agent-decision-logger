"""
Demo: a tiny GIS permit-checking agent, wrapped with the audit trail.

Run with:  python examples/gis_agent_demo.py
Then check logs/audit_log.jsonl or run the dashboard to see the result.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from audit_trail import audit_log

# Pretend "flood zone database" — in a real project this would be a
# GeoPandas/PostGIS spatial query against real FEMA flood zone data.
FAKE_FLOOD_ZONES = {
    "PARCEL-4521": "AE",   # high risk flood zone
    "PARCEL-9981": None,   # no flood zone
}


@audit_log(agent_name="gis-permit-agent")
def check_flood_zone(parcel_id: str) -> dict:
    zone = FAKE_FLOOD_ZONES.get(parcel_id)
    if zone:
        return {
            "decision": "deny",
            "reason": f"Parcel {parcel_id} overlaps FEMA flood zone {zone}"
        }
    return {
        "decision": "approve",
        "reason": f"Parcel {parcel_id} has no flood zone overlap"
    }


if __name__ == "__main__":
    print(check_flood_zone("PARCEL-4521"))
    print(check_flood_zone("PARCEL-9981"))
    print("\nDone. Every call above was written to logs/audit_log.jsonl automatically.")
