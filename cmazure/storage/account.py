from azure.mgmt.storage.models import (
    StorageAccountCreateParameters,
    Sku,
    SkuName,
    Kind
)


def get_account(storage_client, resource_group_name, name):
    return storage_client.storage_accounts.get_properties(resource_group_name,
                                                          name)


def check_name_availability(storage_client, name):
    available = storage_client.storage_accounts.check_name_availability(name)
    if not available:
        raise Exception("Storage account %s is not available: %s" %
                        (name, available.reason))
    return True


def create_account(storage_client, resource_group_name, name, location):
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
    return get_account(storage_client, resource_group_name, name)


def delete_account(storage_client, resource_group_name, name):
    storage_client.storage_accounts.delete(resource_group_name, name)


def list_accounts(storage_client, resource_group_name):
    return storage_client.storage_accounts.list_by_resource_group_name(resource_group_name)


def use_account(storage_client, resource_group_name, name, location):
    try:
        return get_account(storage_client, resource_group_name, name)
    except:
        if check_name_availability(storage_client, name):
            return create_account(storage_client,
                                  resource_group_name,
                                  name, location)
