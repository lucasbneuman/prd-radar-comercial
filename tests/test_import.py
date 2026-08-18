import unittest


class ImportSmokeTest(unittest.TestCase):
    def test_package_version(self):
        from radar_comercial import __version__

        self.assertEqual(__version__, "0.1.0")


if __name__ == "__main__":
    unittest.main()
