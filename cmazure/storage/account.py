from azure.mgmt.storage.models import (
    StorageAccountCreateParameters,
    Sku,
    SkuName,
    Kind
)


def get_account(storage_client, resource_group, name):
    try:
        return storage_client.storage_accounts.get_properties(resource_group.name,
                                                              name)
    except:
        return None


def check_name_availability(storage_client, name):
    available = storage_client.storage_accounts.check_name_availability(name)
    if not available:
        raise Exception("Storage account %s is not available: %s" %
                        (name, available.reason))
    return True


def create_account(storage_client, resource_group, name, region_name):
    future = storage_client.storage_accounts.create(
        resource_group.name,
        name,
        StorageAccountCreateParameters(
            sku=Sku(SkuName.standard_ragrs),
            kind=Kind.storage,
            location=region_name
        )
    )
    future.result()
    return get_account(storage_client, resource_group, name)


def delete_account(storage_client, resource_group, name):
    storage_client.storage_accounts.delete(resource_group.name, name)


def list_accounts(storage_client, resource_group):
    return storage_client.storage_accounts.list_by_resource_group(resource_group.name)


def use_account(storage_client, resource_group, name):
    account = get_account(storage_client, resource_group, name)
    if not account and check_name_availability(storage_client, name):
        account = create_account(storage_client,
                                 resource_group,
                                 name,
                                 resource_group.location)
