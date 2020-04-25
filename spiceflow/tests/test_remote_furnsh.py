import unittest
from spiceflow.furnsh import remote_furnsh


class TestCase(unittest.TestCase):
    def test_remote_furnsh(self):
        url = (
            "http://darts.isas.jaxa.jp/pub/pds3/"
            "sln-l-spice-6-v1.0/slnsp_1000/extras/mk/SEL_V02.TM"
        )
        remote_furnsh(
            url, "selene_test.tm",
        )


if __name__ == "__main__":
    unittest.main()
