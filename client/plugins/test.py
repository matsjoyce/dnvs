import time
import random

from . import Plugin, RejectJob, Value, Always, OneShot, Trigger


class TestPlugin(Plugin):
    ID = "test"
    TARGET = "network"
    VERSION = random.choice(["1.0.0", "1.0.1"])
    TRIGGERS = [
        Trigger([Value("protocol", equals=4)])
    ]

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
    TARGET = "network"
    VERSION = "3.1415"

    def run(self):
        pass

    def stop(self):
        pass

    @classmethod
    def available(cls, defs):
        return defs.get("UA", False)


class Test2Plugin(Plugin):
    ID = "test2"
    TARGET = "network"
    VERSION = "1.0"

    def __init__(self, *args):
        super().__init__(*args)
        time.sleep(5)

    def run(self):
        print(self.args)

    def stop(self):
        pass
