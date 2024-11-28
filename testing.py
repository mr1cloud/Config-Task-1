import unittest
from main import ShellEmulator


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.emulator = ShellEmulator("pc", "testing.tar", "log.txt")

    def test_ls(self):
        # Case 1: ls
        self.assertEqual(self.emulator.ls(), "home\ninfo\ntest1.txt\ntest2.txt")

        # Case 2: ls /
        self.assertEqual(self.emulator.ls("/home"), "documents\ndownloads\ntest3.txt")

    def test_cd(self):
        # Case 1: cd
        self.assertEqual(self.emulator.cd(""), "Changed directory to /")

        # Case 2: cd /home/downloads
        self.assertEqual(self.emulator.cd("/home/downloads"), "Changed directory to /home/downloads")

    def test_cp(self):
        # Case 1: cp
        self.emulator.cp("test1.txt", "test3.txt")
        self.assertIn("test3.txt", self.emulator.ls("/"))

        # Case 2: cp /home/test2.txt /home/downloads/test2.txt
        self.emulator.cp("/home/test1.txt", "/home/downloads/test4.txt")
        self.assertIn("test4.txt", self.emulator.ls("/home/downloads"))


if __name__ == '__main__':
    unittest.main()
