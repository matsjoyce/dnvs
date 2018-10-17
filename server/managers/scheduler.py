import collections
import functools
import threading
import cherrypy

from . import Manager
from .workers import WorkerState
from .jobs import JobState
from .triggers import Trigger


class Plugin:
    def __init__(self, id):
        self.id = id
        self.version = ""
        self.triggers = []
        self.workers = []
        self.target = ""
        self.data = {}

    def __str__(self):
        return f"Plugin({self.id!r}, {self.version!r})"

    def update(self, data, workers):
        data_update = worker_update = False
        if data != self.data:
            self.version = data["version"]
            self.triggers = [Trigger(t) for t in data["triggers"]]
            self.target = data["target"]
            self.data = data
            cherrypy.engine.publish("plugin-change", self)
            data_update = True
        if workers != self.workers:
            self.workers = workers
            cherrypy.engine.publish("plugin-worker-change", self)
            worker_update = True
        return data_update, worker_update

    def json(self):
        return {
            "id": self.id,
            "version": self.version,
            "workers": [w.id for w in self.workers],
            "target": self.target
        }


class Scheduler(Manager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plugins = {}
        self.plugins_by_target = {"network": [], "node": []}
        self.lock = threading.RLock()
        self.scheduled_jobs = {}

    def locked(func):
        @functools.wraps(func)
        def lock_wrapper(self, *args, **kwargs):
            with self.lock:
                return func(self, *args, **kwargs)
        return lock_wrapper

    def start(self):
        self.bus.log("Scheduler: startup")
        self.bus.subscribe("worker-plugins-changed", self.calculate_plugins)
        self.bus.subscribe("view-plugins", self.view_plugins)
        self.bus.subscribe("network-change", self.network_evaluate)
        self.bus.subscribe("plugin-change", self.plugin_evaluate)
        self.bus.subscribe("job-completed", self.job_completed)

    @locked
    def calculate_plugins(self, updated_worker):
        workers, = self.bus.publish("view-workers")

        plugins = collections.defaultdict(lambda: collections.defaultdict(lambda: [{}, set()]))
        for plugin in self.plugins.values():
            plugins[plugin.id][plugin.version][0] = plugin.data

        for worker in workers.values():
            if worker.state not in (WorkerState.idle, WorkerState.considering, WorkerState.working):
                continue
            for plugin in worker.all_plugins.values():
                data, p_workers = plugins[plugin["id"]][plugin["version"]]
                p_workers.add(worker)
                data.update(plugin)

        has_data_updated = has_worker_update = False
        for id, plugin_versions in plugins.items():
            highest_version = max(plugin_versions, key=lambda v: [int(x) for x in v.split(".")])
            if id not in self.plugins:
                self.plugins[id] = Plugin(id)
            du, wu = self.plugins[id].update(*plugin_versions[highest_version])
            has_data_updated = has_data_updated or du
            has_worker_update = has_worker_update or wu

            for version, (_, workers) in filter(lambda xs: xs[0] != highest_version, plugin_versions.items()):
                msg = f"Plugin '{id}' is not at the latest version ({version} < {highest_version}), it will be ignored!"
                for worker in workers:
                    if msg not in worker.warnings:
                        worker.warnings.append(msg)

        updated_worker.plugins = set()

        self.plugins_by_target = {"network": set(), "node": set()}

        for plugin in self.plugins.values():
            if updated_worker in plugin.workers:
                updated_worker.plugins.add(plugin.id)
            self.plugins_by_target[plugin.target].add(plugin)

    @locked
    def network_evaluate(self, network):
        self.logger.info("Network updated, considering...")
        runnable_plugins = set()
        json = network.json()
        for plugin in self.plugins_by_target["network"]:
            for trigger in plugin.triggers:
                if trigger.matches(json):
                    runnable_plugins.add(plugin)
                    break
        self.logger.info(f"Network updated, runnable are {runnable_plugins}")
        for plugin in network.active_plugins - runnable_plugins:
            self.deschedule_plugin(network, plugin)
        for plugin in runnable_plugins - network.active_plugins:
            self.schedule_plugin(network, plugin)
        network.active_plugins = runnable_plugins
        cherrypy.engine.publish("network-active-plugins-change", network)

    @locked
    def plugin_evaluate(self, plugin):
        if plugin.target == "network":
            networks, = self.bus.publish("view-networks")
            for network in networks.values():
                json = network.json()
                for trigger in plugin.triggers:
                    if trigger.matches(json):
                        self.schedule_plugin(network, plugin)
                        network.active_plugins.add(plugin)
                        cherrypy.engine.publish("network-active-plugins-change", network)
                        break
                else:
                    if plugin in network.active_plugins:
                        self.deschedule_plugin(network, plugin)
                        network.active_plugins.remove(plugin)
                        cherrypy.engine.publish("network-active-plugins-change", network)
        elif plugin.target == "node":
            pass

    def schedule_plugin(self, network, plugin):
        self.logger.info(f"Scheduling {plugin} for {network}")
        if plugin.id in network.active_jobs:
            network.active_jobs.pop(plugin.id).stop()
        job, = self.bus.publish("job-create", plugin.id, {
            "network": network.json()
        })
        network.active_jobs[plugin.id] = job
        network.jobs.add(job)
        self.logger.debug(f"Done, {job}")

    def deschedule_plugin(self, network, plugin):
        self.logger.info(f"Descheduling {plugin} for {network}")
        if plugin.id in network.active_jobs:
            network.active_jobs.pop(plugin.id).stop()

    @locked
    def job_completed(self, job):
        networks, = self.bus.publish("view-networks")
        item = networks[job.args["network"]["id"]]
        plugin = self.plugins[job.plugin]
        self.logger.info(f"Scheduled job {job} for {item} with {plugin} has completed")
        item.active_jobs.pop(plugin.id)
        item.run_plugins.add(plugin)
        cherrypy.engine.publish("network-active-plugins-change", item)

    def view_plugins(self):
        return self.plugins.copy()
