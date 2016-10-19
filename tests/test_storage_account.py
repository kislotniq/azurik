import cmazure.storage.account
import cmazure.storage.common
import cmazure.common
from cmazure.credentials import AzureCredentials


def test_create():
    creds = AzureCredentials.make_from_environment()
    storage_client = cmazure.storage.common.make_storage_client(creds)

    resource_client = cmazure.common.make_resource_client(creds)

    resource_group = cmazure.common.create_resource_group(resource_client,
                                                          "test-resource-group",
                                                          "westus")
    cmazure.storage.account.use_account(storage_client, resource_group, "brighttestaccount")
