import unittest

import stactools.bc_dem


class TestModule(unittest.TestCase):
    def test_version(self):
        self.assertIsNotNone(stactools.bc_dem.__version__)
