import itertools
import ipaddress
import cherrypy

from . import Manager


class Network:
    def __init__(self, id, logger, network):
        self.id = id
        self.network = network
        self.logger = logger
        self.active_plugins = set()
        self.run_plugins = set()
        self.jobs = set()
        self.active_jobs = {}
        cherrypy.engine.publish("network-change", self)

    def __str__(self):
        return f"Network({self.id!r}, {self.network!r})"

    def json(self):
        return {
            "id": self.id,
            "network": str(self.network),
            "addresses": self.network.num_addresses,
            "protocol": self.network.version,
            "active_plugins": [p.id for p in self.active_plugins],
            "run_plugins": [p.id for p in self.run_plugins],
            "jobs": [j.id for j in self.jobs],
            "active_jobs": [j.id for j in self.active_jobs.values()]
        }


class NetworkManager(Manager):
    def __init__(self, bus):
        super().__init__(bus)

        self.network_id = itertools.count()
        self.networks = {}

    def start(self):
        self.bus.log("NM: startup")
        self.bus.subscribe("view-networks", self.view_networks)
        self.bus.subscribe("network-create", self.create_network)

    def view_networks(self):
        return self.networks.copy()

    def create_network(self, spec):
        id = next(self.network_id)
        net = ipaddress.ip_network(spec)
        self.logger.info(f"New network, id={id}, network={net}")
        network = self.networks[id] = Network(id, self.logger, net)
        return network
