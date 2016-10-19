import uuid


class StorageClient(object):

    def __init__(self, account):
        self.service = account.account.create_file_service()

    def _get_resource_reference(self, prefix):
        return '{}{}'.format(prefix, str(uuid.uuid4()).replace('-', ''))

    def _get_file_reference(self, prefix='file'):
        return self._get_resource_reference(prefix)

    def _create_share(self, prefix='share'):
        share_name = self._get_resource_reference(prefix)
        self.service.create_share(share_name)
        return share_name

    def _create_directory(self, share_name, prefix='dir'):
        dir_name = self._get_resource_reference(prefix)
        self.service.create_directory(share_name, dir_name)

    def mkdir(self, path, prefix='dir'):
        share_name = self._create_share()
        self._create_directory(share_name)
