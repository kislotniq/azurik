import os
from azure.common.credentials import ServicePrincipalCredentials


def make_from_environment(client_id_env="AZURE_CLIENT_ID",
                          client_secret_env="AZURE_CLIENT_SECRET",
                          tenant_id_env="AZURE_TENANT_ID"):
    """Make credentials object using environment variables

    Default are AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID
    """
    return make(os.environ[client_id_env],
                os.environ[client_secret_env],
                os.environ[tenant_id_env])


def make(client_id, secret, tenant):
    return ServicePrincipalCredentials(
        client_id=client_id,
        secret=secret,
        tenant=tenant
    )
