import unittest
import procbridge as pb

PORT = 8000


class TestProcBridge(unittest.TestCase):

    server = None

    @classmethod
    def setUpClass(cls):
        cls.server = pb.Server('0.0.0.0', PORT, cls.delegate)
        cls.server.start()
        pass

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()

    @staticmethod
    def delegate(api, arg):
        if api == 'hello':
            return 'hello'
        pass

    def setUp(self):
        self.client = pb.Client('127.0.0.1', PORT)

    def tearDown(self):
        self.client = None

    def test_1(self):
        reply = self.client.request('hello', {'name': 'Gong'})
        self.assertEqual('hello', reply)

    def test_2(self):
        self.assertTrue(True)


if __name__ == '__main__':
    unittest.main()
