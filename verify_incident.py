import os
from kalki.cli import run_demo
from kalki.store import incident_store

def verify():
    # Ensure silent demo run to just get the final state
    run_demo("sample_data/demo_fixed.log")
    
    print("\n" + "="*50)
    print("VERIFICATION OF INCIDENT ALERT COUNTS")
    print("="*50)
    incidents = incident_store.list_all()
    for inc in incidents:
        print(f"Incident ID: {inc.incident_id}")
        print(f"Severity: {inc.severity.name}")
        print(f"Kill Chain: {inc.kill_chain_phase}")
        print(f"Alert Count: {len(inc.alert_ids)}")
        print("-" * 30)

if __name__ == "__main__":
    verify()
