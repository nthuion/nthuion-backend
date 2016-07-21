import unittest


class IntrospectionTest(unittest.TestCase):

    def test_dry_run(self):
        import nthuion.introspect
        list(nthuion.introspect.r1())
