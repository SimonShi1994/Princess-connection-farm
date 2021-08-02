import unittest

from app import create_app


class TestAccount(unittest.TestCase):

    def setUp(self):
        """在执行具体的测试方法前，先被调用"""
        self.client = create_app().test_client()

    def test_crud_success_case(self):
        # TODO 先解决相对路径问题, 目前会把文件创建到这个路径下面
        pass
        # response = self.client.get("/api/account", data={})
        # resp_dict = json.loads(response.data)
