import os
from account import StorageAccount


class StorageClient(object):

    def __init__(self, credentials, resource_group_name, storage_account_name):
        self.account = StorageAccount(credentials,
                                      resource_group_name,
                                      storage_account_name)

        self.service = self.account.account.create_file_service()

    def upload(self, source, dest):





