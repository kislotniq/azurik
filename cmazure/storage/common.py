from azure.mgmt.storage import StorageManagementClient


def make_storage_client(credentials):
    return StorageManagementClient(credentials.get_service_principal(),
                                   credentials.subscription_id)
