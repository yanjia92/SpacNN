from unittest import TestCase
from util.AnnotationHelper import singleton


@singleton
class Singleton(object):
    def __init__(self, obj):
        self.obj = obj


class NotSingleton(object):
    def __init__(self, obj):
        self.obj = obj


class Test(TestCase):
    def setUp(self):
        self.singleton1 = Singleton(1)
        self.singleton2 = Singleton(2)
        self.non_singleton1 = NotSingleton(1)
        self.non_singleton2 = NotSingleton(2)

    def test(self):
        self.assertEqual(self.singleton1.obj, self.singleton2.obj)
        self.assertNotEqual(self.non_singleton1.obj, self.non_singleton2.obj)