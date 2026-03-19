import os
from datetime import datetime, timezone


def collect_gcp_resources():
    """
    GCP collector. Requires one environment variable in your .env file:
      GOOGLE_APPLICATION_CREDENTIALS_JSON — contents of your service account JSON key

    Setup guide is in README.md under 'Connecting GCP'.

    Status: credentials not yet configured — returns empty scaffold.
    When credentials are present this will collect:
      - Compute Engine instances
      - Cloud Storage buckets
      - Cloud Functions
      - GKE clusters
      - Cloud SQL instances
      - BigQuery datasets
    """

    gcp_creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS_JSON")
    gcp_project = os.environ.get("GCP_PROJECT_ID")

    if not gcp_creds or not gcp_project:
        return {
            "provider": "gcp",
            "region": "not configured",
            "scanned_at": datetime.now(timezone.utc).isoformat(),
            "connected": False,
            "message": "Add GOOGLE_APPLICATION_CREDENTIALS_JSON and GCP_PROJECT_ID to your .env file to connect GCP.",
            "services": [],
            "summary": {
                "total_resources": 0,
                "total_cost": 0.0,
                "paid_services": 0,
                "free_services": 0,
            }
        }

    # When you are ready to wire GCP:
    # pip install google-cloud-compute google-cloud-storage google-cloud-functions
    # import json
    # from google.oauth2 import service_account
    # creds_dict = json.loads(gcp_creds)
    # credentials = service_account.Credentials.from_service_account_info(creds_dict)

    return {
        "provider": "gcp",
        "region": "not configured",
        "scanned_at": datetime.now(timezone.utc).isoformat(),
        "connected": False,
        "message": "GCP credentials not configured.",
        "services": [],
        "summary": {
            "total_resources": 0,
            "total_cost": 0.0,
            "paid_services": 0,
            "free_services": 0,
        }
    }
