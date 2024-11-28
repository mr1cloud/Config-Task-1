import unittest
from main import ShellEmulator


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.emulator = ShellEmulator("pc", "testing.tar", "log.txt")

    def test_ls_1(self):
        # Case 1: ls
        self.assertIn("home\ninfo\ntest1.txt\ntest2.txt", self.emulator.ls())

    def test_ls_2(self):
        # Case 2: ls /
        self.assertIn("documents\ndownloads\ntest1.txt", self.emulator.ls("/home"))

    def test_cd_1(self):
        # Case 1: cd
        self.assertEqual(self.emulator.cd(""), "Changed directory to /")

    def test_cd_2(self):
        # Case 2: cd /home/downloads
        self.assertEqual(self.emulator.cd("/home/downloads"), "Changed directory to /home/downloads")

    def test_cp_1(self):
        # Case 1: cp
        self.emulator.cp("test1.txt", "test3.txt")
        self.assertIn("test3.txt", self.emulator.ls("/"))

    def test_cp_2(self):
        # Case 2: cp /home/test2.txt /home/downloads/test2.txt
        self.emulator.cp("/home/test1.txt", "/home/downloads/test4.txt")
        self.assertIn("test4.txt", self.emulator.ls("/home/downloads"))


if __name__ == '__main__':
    suite = unittest.TestSuite()

    tests = [MyTestCase("test_ls_1"), MyTestCase("test_ls_2"), MyTestCase("test_cd_1"), MyTestCase("test_cd_2"),
             MyTestCase("test_cp_1"), MyTestCase("test_cp_2")]

    suite.addTests(tests)

    runner = unittest.TextTestRunner()

    runner.run(suite)
