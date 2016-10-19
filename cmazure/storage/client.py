import os


class StorageClient(object):

    def __init__(self, account):
        self.service = account.create_file_service()

    def create_share(self, name):
        self.service.create_share(name)

    def create_directory(self, share_name, name):
        self.service.create_directory(share_name, name)

    def mkdir(self, share_name, path):
        self.create_share(share_name)
        self.create_directory(share_name, path)

    def mkdirp(self, share_name, path):
        dirs = list(os.path.split(path))

        for i in range(0, len(dirs)):
            d = '/'.join(dirs[:i + 1])
            self.mkdir(share_name, d)

    def callback(self, current, total):
        print('Progress: %s%%' % (current / total * 100))

    def upload(self, share_name, path):
        path = os.path.abspath(path)
        dirname = os.path.dirname(path)[1:]
        basename = os.path.basename(path)

        self.create_share(share_name)
        self.mkdirp(share_name, dirname)
        self.service.create_file_from_path(share_name,
                                           dirname,
                                           basename,
                                           path,
                                           progress_callback=self.callback)

    def download(self, share_name, path):
        path = os.path.abspath(path)
        dirname = os.path.dirname(path)[1:]
        basename = os.path.basename(path)

        self.service.get_file_to_path(share_name,
                                      dirname,
                                      basename,
                                      path,
                                      progress_callback=self.callback)
