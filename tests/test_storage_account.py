from cmazure.storage.account import StorageAccount
from cmazure.credentials import AzureCredentials


def test_create():
    creds = AzureCredentials.make_from_environment()

    resource_group_name = "test-resource-group"
    StorageAccount(creds, resource_group_name, "brightazuretestgroup")
