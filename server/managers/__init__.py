import logging


class Manager:
    MANAGERS = set()
    PRIORITY = 10

    def __init__(self, bus):
        self.bus = bus
        self.logger = logging.getLogger(self.__class__.__module__)

    def subscribe(self):
        for channel in self.bus.listeners:
            method = getattr(self, channel, None)
            if method is not None:
                self.bus.subscribe(channel, method, priority=self.PRIORITY)

    def unsubscribe(self):
        for channel in self.bus.listeners:
            method = getattr(self, channel, None)
            if method is not None:
                self.bus.unsubscribe(channel, method, priority=self.PRIORITY)

    @classmethod
    def __init_subclass__(cls):
        Manager.MANAGERS.add(cls)

    @staticmethod
    def register_managers(bus):
        for manager in Manager.MANAGERS:
            manager(bus).subscribe()


from . import workers, jobs, broadcasting, scheduler  # noqa
