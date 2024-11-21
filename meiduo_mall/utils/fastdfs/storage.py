from django.core.files.storage import Storage
from meiduo_mall.settings import FDFS_BASE_URL


class Mystorage(Storage):
    def __init__(self):
        self.fdfs_base_url = FDFS_BASE_URL

    def _open(self, name, mode="rb"):
        pass

    def _save(self, name, content, max_length=None):
        pass

    def url(self, name):
        return self.fdfs_base_url + name
