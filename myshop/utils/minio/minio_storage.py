from django.conf import settings
from django.core.files.storage import Storage


class MinioStorage(Storage):
    """自定义文件存储类"""

    def __init__(self, minio_base_url=None):
        """文件存储类的初始化方法"""
        self.minio_url = minio_base_url or settings.MINIO_URL

    def _open(self, name, mode='rb'):
        """
        打开文件时会被调用
        :param name: 文件路径
        :param mode: 文件打开方式
        :return: None
        """
        pass

    def _save(self, name, content):
        """
        保存文件时会被调用的
        :param name: 文件路径
        :param content: 文件二进制内容
        :return: None
        """
        pass

    def url(self, name):
        """
        返回文件的全路径
        :param name: 文件相对路径
        :return: 文件的全路径       
        """
        ret_url = self.minio_url + name
        return ret_url
