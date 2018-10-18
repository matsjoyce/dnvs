
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
        self.bus.subscribe("worker-change", self.worker_change)
        self.bus.subscribe("network-change", self.network_change)
        self.bus.subscribe("network-active-plugins-change", self.network_change)
        self.bus.subscribe("plugin-change", self.plugins_change)
        self.bus.subscribe("plugin-worker-change", self.plugins_change)

    def broadcast_connected(self, ws):
        with ws.lock:
            self.clients.add(ws)
            jobs, = self.bus.publish("view-jobs")
            workers, = self.bus.publish("view-workers")
            plugins, = self.bus.publish("view-plugins")
            networks, = self.bus.publish("view-networks")
            for job in jobs.values():
                ws.send_json({
                    "type": "job",
                    "data": job.json()
                })
            for worker in workers.values():
                ws.send_json({
                    "type": "worker",
                    "data": worker.json()
                })
            for plugin in plugins.values():
                ws.send_json({
                    "type": "plugin",
                    "data": plugin.json()
                })
            for network in networks.values():
                ws.send_json({
                    "type": "network",
                    "data": network.json()
                })

    def broadcast_disconnected(self, ws):
        self.clients.discard(ws)

    def job_state_change(self, job):
        self.broadcast("job", job.json())

    def worker_change(self, worker):
        self.broadcast("worker", worker.json())

    def plugins_change(self, plugin):
        self.broadcast("plugin", plugin.json())

    def network_change(self, network):
        self.broadcast("network", network.json())

    def broadcast(self, type, data):
        for client in self.clients:
            try:
                client.send_json({
                    "type": type,
                    "data": data
                })
            except IOError:
                pass
