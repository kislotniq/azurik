from azure.mgmt.storage import StorageManagementClient

from azure.mgmt.storage.models import (
    StorageAccountCreateParameters,
    Sku,
    SkuName,
    Kind
)


class StorageAccount:

    def __init__(self, credentials, resource_group_name, name):

        self.client = StorageManagementClient(credentials.get_service_principal(),
                                              credentials.subscription_id)

        self.account = self.use(resource_group_name, name)

        if not self.account and self.checkAvailability(name):
            self.account = self.create(resource_group_name, name)

    def use(self, resource_group_name, name):
        self.account = self.client.storage_accounts.get_properties(resource_group_name,
                                                                   name)
        return self.account

    def checkAvailability(self, name):
        available = self.client.storage_accounts.check_name_availability(name)
        if not available:
            raise Exception("Storage account %s is not available: %s" %
                            (name, available.reason))
        return True

    def create(self, resource_group_name, name, location):
        future = self.client.storage_accounts.create(
            resource_group_name,
            name,
            StorageAccountCreateParameters(
                sku=Sku(SkuName.standard_ragrs),
                kind=Kind.storage,
                location=location
            )
        )
        future.result()
        self.account = self.use(resource_group_name, name)
