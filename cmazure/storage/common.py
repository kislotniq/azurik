from azure.mgmt.storage import StorageManagementClient
from azure.storage.cloudstorageaccount import CloudStorageAccount


def make_storage_client(credentials):
    return StorageManagementClient(credentials.get_service_principal(),
                                   credentials.subscription_id)


def make_cloud_storage_account(account_name, account_key, sas_token):
    return CloudStorageAccount(account_name, account_key, sas_token)
