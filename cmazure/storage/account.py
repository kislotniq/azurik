from azure.mgmt.storage.models import (
    StorageAccountCreateParameters,
    Sku,
    SkuName,
    Kind
)


def get_account(storage_client, resource_group_name, name):
    try:
        return storage_client.storage_accounts.get_properties(resource_group_name,
                                                              name)
    except:
        return None


def check_name_availability(storage_client, name):
    available = storage_client.storage_accounts.check_name_availability(name)
    if not available:
        raise Exception("Storage account %s is not available: %s" %
                        (name, available.reason))
    return True


def create_account(storage_client, resource_group_name, name, location="westus"):
    future = storage_client.storage_accounts.create(
        resource_group_name,
        name,
        StorageAccountCreateParameters(
            sku=Sku(SkuName.standard_ragrs),
            kind=Kind.storage,
            location=location
        )
    )
    future.result()
    return get_account(resource_group_name, name)


def delete_account(storage_client, resource_group_name, name):
    storage_client.storage_accounts.delete(resource_group_name, name)


def list_accounts(storage_client, resource_group_name):
    return storage_client.storage_accounts.list_by_resource_group(resource_group_name)


def use_account(storage_client, resource_group_name, name):
    account = get_account(storage_client, resource_group_name, name)
    if not account and check_name_availability(storage_client, name):
        account = create_account(storage_client, resource_group_name, name)
