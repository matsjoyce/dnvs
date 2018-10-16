import collections
import functools
import threading

from . import Manager
from .workers import WorkerState


class Plugin:
    def __init__(self, data, workers):
        self.id = data["id"]
        self.version = data["version"]
        self.workers = workers
        self.data = data

    def json(self):
        return {
            "id": self.id,
            "version": self.version,
            "workers": [w.id for w in self.workers]
        }


class Scheduler(Manager):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plugins = {}
        self.lock = threading.RLock()

    def locked(func):
        @functools.wraps(func)
        def lock_wrapper(self, *args, **kwargs):
            with self.lock:
                return func(self, *args, **kwargs)
        return lock_wrapper

    def start(self):
        self.bus.subscribe("worker-plugins-changed", self.calculate_plugins)
        self.bus.subscribe("view-plugins", self.view_plugins)

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

        for id, plugin_versions in plugins.items():
            highest_version = max(plugin_versions, key=lambda v: [int(x) for x in v.split(".")])
            self.plugins[id] = Plugin(*plugin_versions[highest_version])
            for version, (_, workers) in filter(lambda xs: xs[0] != highest_version, plugin_versions.items()):
                msg = f"Plugin '{id}' is not at the latest version ({version} < {highest_version}), it will be ignored!"
                for worker in workers:
                    if msg not in worker.warnings:
                        worker.warnings.append(msg)

        self.bus.publish("plugins-change", self.plugins)
        updated_worker.plugins = set()

        for plugin in self.plugins.values():
            if updated_worker in plugin.workers:
                updated_worker.plugins.add(plugin.id)

            self.bus.publish("job-create", plugin.id, {})

    def view_plugins(self):
        return self.plugins.copy()
