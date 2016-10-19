from azure.mgmt.resource import ResourceManagementClient

from cmazure.credentials import AzureCredentials


def test_login():
    creds = AzureCredentials.make_from_environment()
    resource_manager = ResourceManagementClient(creds.get_service_principal(),
                                                creds.subscription_id)
    list(resource_manager.resource_groups.list())
