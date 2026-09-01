from kalki.cli import run_demo
from kalki.api.routes import create_api_app
from kalki.store import incident_store

def main():
    print("Running demo to populate in-memory store...")
    run_demo()
    
    incidents = incident_store.list_all()
    if not incidents:
        print("No incidents found after demo.")
        return
        
    incident_id = incidents[0].incident_id
    print(f"\nFetching report for incident {incident_id} via API...")
    
    app = create_api_app()
    with app.test_client() as client:
        res = client.get(f"/api/v1/incidents/{incident_id}/report")
        print("\n" + "="*50)
        print("HTTP STATUS:", res.status_code)
        print("HEADERS:")
        for k, v in res.headers.items():
            print(f"  {k}: {v}")
        print("="*50)
        print(res.data.decode('utf-8'))
        print("="*50)

if __name__ == "__main__":
    main()
