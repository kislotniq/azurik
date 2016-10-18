import os
from azure.common.credentials import ServicePrincipalCredentials


class AzureCredentials(object):
    def __init__(self, client_id, secret, tenant, subscription_id):
        self.client_id = client_id
        self.secret = secret
        self.tenant = tenant
        self.subscription_id = subscription_id

    @classmethod
    def make_from_environment(cls,
                              client_id_env="AZURE_CLIENT_ID",
                              client_secret_env="AZURE_CLIENT_SECRET",
                              tenant_id_env="AZURE_TENANT_ID",
                              subscription_id_env="AZURE_SUBSCRIPTION_ID"):
        """Make credentials object using environment variables

        Default are AZURE_CLIENT_ID, AZURE_CLIENT_SECRET, AZURE_TENANT_ID
        """
        return cls(os.environ[client_id_env],
                   os.environ[client_secret_env],
                   os.environ[tenant_id_env],
                   os.environ[subscription_id_env])

    def get_service_principal(self):
        return ServicePrincipalCredentials(
            client_id=self.client_id,
            secret=self.secret,
            tenant=self.tenant
        )
