import time
import random

from . import Plugin


class TestPlugin(Plugin):
    NAME = "test"
    VERSION = "1.0.0"

    def run(self):
        time.sleep(random.randrange(5, 20))

    def stop(self):
        pass


class UnavailableTestPlugin(Plugin):
    NAME = "test-ua"
    VERSION = "1.0.0"

    def run(self):
        pass

    def stop(self):
        pass

    @classmethod
    def available(cls):
        return False
