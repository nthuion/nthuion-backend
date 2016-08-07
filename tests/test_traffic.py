from .base import WebTest


class SmokeTest(WebTest):

    def test_set_up_class_is_working(self):
        self.ts.ping()

    def test_setup_1(self):
        assert 1 == self.ts.sadd('1', '2')

    def test_setup_2(self):
        """make sure that tearDown cleans the db correctly"""
        assert 1 == self.ts.sadd('1', '2')
