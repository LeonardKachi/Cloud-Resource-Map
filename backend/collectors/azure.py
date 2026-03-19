import os
from datetime import datetime, timezone


def collect_azure_resources():
    """
    Azure collector. Requires three environment variables in your .env file:
      AZURE_TENANT_ID       — from your Azure Active Directory
      AZURE_CLIENT_ID       — from your Service Principal
      AZURE_CLIENT_SECRET   — from your Service Principal
      AZURE_SUBSCRIPTION_ID — your subscription ID

    Setup guide is in README.md under 'Connecting Azure'.

    Status: credentials not yet configured — returns empty scaffold.
    When credentials are present this will collect:
      - Virtual Machines
      - Blob Storage accounts
      - Azure Functions
      - Azure SQL databases
      - Virtual Networks
      - AKS clusters
    """

    tenant_id   = os.environ.get("AZURE_TENANT_ID")
    client_id   = os.environ.get("AZURE_CLIENT_ID")
    secret      = os.environ.get("AZURE_CLIENT_SECRET")
    sub_id      = os.environ.get("AZURE_SUBSCRIPTION_ID")

    if not all([tenant_id, client_id, secret, sub_id]):
        return {
            "provider": "azure",
            "region": "not configured",
            "scanned_at": datetime.now(timezone.utc).isoformat(),
            "connected": False,
            "message": "Add AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, and AZURE_SUBSCRIPTION_ID to your .env file to connect Azure.",
            "services": [],
            "summary": {
                "total_resources": 0,
                "total_cost": 0.0,
                "paid_services": 0,
                "free_services": 0,
            }
        }

    # When you are ready to wire Azure:
    # pip install azure-mgmt-compute azure-mgmt-storage azure-mgmt-network azure-identity
    # from azure.identity import ClientSecretCredential
    # from azure.mgmt.compute import ComputeManagementClient
    # credential = ClientSecretCredential(tenant_id, client_id, secret)
    # compute_client = ComputeManagementClient(credential, sub_id)
    # vms = list(compute_client.virtual_machines.list_all())

    return {
        "provider": "azure",
        "region": "not configured",
        "scanned_at": datetime.now(timezone.utc).isoformat(),
        "connected": False,
        "message": "Azure credentials not configured.",
        "services": [],
        "summary": {
            "total_resources": 0,
            "total_cost": 0.0,
            "paid_services": 0,
            "free_services": 0,
        }
    }
