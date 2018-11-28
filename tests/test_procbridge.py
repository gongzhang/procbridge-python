import unittest
import procbridge as pb
from server import PORT
from server import delegate


class TestProcBridge(unittest.TestCase):

    server = None

    @classmethod
    def setUpClass(cls):
        try:
            cls.server = pb.Server('0.0.0.0', PORT, delegate)
            cls.server.start()
        except OSError:
            print("use existing server on port {}".format(PORT))
            cls.server = None

    @classmethod
    def tearDownClass(cls):
        if cls.server is not None:
            cls.server.stop()
            cls.server = None

    def setUp(self):
        self.client = pb.Client('127.0.0.1', PORT)

    def tearDown(self):
        self.client = None

    def testNone(self):
        reply = self.client.request(None, None)
        self.assertIsNone(reply)
        reply = self.client.request("echo", None)
        self.assertIsNone(reply)
        reply = self.client.request(None, "hello")
        self.assertIsNone(reply)

    def testEcho(self):
        reply = self.client.request("echo", 123)
        self.assertEqual(123, reply)
        reply = self.client.request("echo", 3.14)
        self.assertEqual(3.14, reply)
        reply = self.client.request("echo", "hello")
        self.assertEqual("hello", reply)
        reply = self.client.request("echo", ["a", "b"])
        self.assertEqual(["a", "b"], reply)
        reply = self.client.request("echo", {"key": "value"})
        self.assertEqual({"key": "value"}, reply)

    def testSum(self):
        reply = self.client.request("sum", [1, 2, 3, 4])
        self.assertEqual(10, reply)

    def testError(self):
        try:
            self.client.request("err")
        except pb.ServerError as err:
            self.assertEqual("generated error", err.message)
        else:
            self.fail()

    def testBigPayload(self):
        with open('article.txt', encoding='utf-8') as f:
            text = f.read()
            reply = self.client.request("echo", text)
            self.assertEqual(text, reply)


if __name__ == '__main__':
    unittest.main()
