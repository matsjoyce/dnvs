import time
import random

from . import Plugin, RejectJob


class TestPlugin(Plugin):
    ID = "test"
    VERSION = random.choice(["1.0.0", "1.0.1"])

    def __init__(self, *args):
        super().__init__(*args)
        if random.randrange(2):
            raise RejectJob()

    def run(self):
        time.sleep(random.randrange(3, 30))

    def stop(self):
        pass


class UnavailableTestPlugin(Plugin):
    ID = "test-ua"
    VERSION = "1.0.0"

    def run(self):
        pass

    def stop(self):
        pass

    @classmethod
    def available(cls):
        return False


class Test2Plugin(Plugin):
    ID = "test2"
    VERSION = "1.0"

    def __init__(self, *args):
        super().__init__(*args)
        time.sleep(5)

    def run(self):
        pass

    def stop(self):
        pass
