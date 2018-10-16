
from . import Manager


class BroadcastManager(Manager):
    def __init__(self, bus):
        super().__init__(bus)

        self.clients = set()

    def start(self):
        self.bus.log("BM: startup")
        self.bus.subscribe("broadcast-connected", self.broadcast_connected)
        self.bus.subscribe("broadcast-disconnected", self.broadcast_disconnected)
        self.bus.subscribe("job-state-change", self.job_state_change)
        self.bus.subscribe("worker-state-change", self.worker_state_change)
        self.bus.subscribe("plugins-change", self.plugins_change)

    def broadcast_connected(self, ws):
        self.clients.add(ws)

    def broadcast_disconnected(self, ws):
        self.clients.discard(ws)

    def job_state_change(self, job):
        self.broadcast("job", job.json())

    def worker_state_change(self, worker):
        self.broadcast("worker", worker.json())

    def plugins_change(self, plugins):
        self.broadcast("plugins", [p.json() for p in plugins.values()])

    def broadcast(self, type, data):
        for client in self.clients:
            try:
                client.send_json({
                    "type": type,
                    "data": data
                })
            except IOError:
                pass
