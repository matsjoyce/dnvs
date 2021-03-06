import itertools
import enum
import pprint
import cherrypy

from . import Manager
from .jobs import JobState


class WorkerState(enum.Enum):
    startup = 0
    idle = 1
    considering = 2
    working = 3
    disconnected = 4


class Worker:
    def __init__(self, id, ws, logger):
        self.id = id
        self.ws = ws
        self.logger = logger
        self.ws.handler = self
        self.state = WorkerState.startup
        self.current_job = None
        self.considering_job = None
        self.warnings = {}
        self.all_plugins = {}
        self.plugins = set()
        self.privileged = False

    def __str__(self):
        return f"Worker({self.id!r}, {self.address!r})"

    @property
    def address(self):
        return self.ws.address

    def json(self):
        return {
            "id": self.id,
            "address": self.address,
            "state": self.state.name,
            "current_job": self.current_job.id if self.current_job else None,
            "considering_job": self.considering_job.id if self.considering_job else None,
            "plugins": [p.id for p in self.plugins],
            "warnings": list(self.warnings.values()),
            "privileged": self.privileged
        }

    def add_active_plugin(self, plugin):
        self.plugins.add(plugin)
        cherrypy.engine.publish("worker-change", self)

    def remove_active_plugin(self, plugin):
        self.plugins.remove(plugin)
        cherrypy.engine.publish("worker-change", self)

    def add_warning(self, key, msg):
        if self.warnings.get(key) != msg:
            self.warnings[key] = msg
            cherrypy.engine.publish("worker-change", self)

    def received_message(self, data):
        command = data.get("command")

        if command == "startup-complete":
            assert self.state is WorkerState.startup
            self.state = WorkerState.idle
            self.all_plugins = {p["id"]: p for p in data["args"]["plugins"]}
            self.privileged = data["args"]["privileged"]

            cherrypy.engine.publish("worker-plugins-changed", self)
            cherrypy.engine.publish("worker-state-change", self)
            cherrypy.engine.publish("worker-change", self)

        elif command == "accept-job":
            assert data["args"]["job_id"] == self.considering_job.id
            assert self.current_job is None
            assert self.state is WorkerState.considering

            if self.considering_job.state is not JobState.stopped:
                self.considering_job.accepted(self, data["args"])

            self.current_job, self.considering_job = self.considering_job, None
            self.state = WorkerState.working

            cherrypy.engine.publish("worker-state-change", self)
            cherrypy.engine.publish("worker-change", self)

        elif command == "reject-job":
            assert data["args"]["job_id"] == self.considering_job.id
            assert self.current_job is None
            assert self.state is WorkerState.considering

            if self.considering_job.state is not JobState.stopped:
                self.considering_job.rejected(self, data["args"])
            self.considering_job = None
            self.state = WorkerState.idle
            cherrypy.engine.publish("worker-state-change", self)
            cherrypy.engine.publish("worker-change", self)

        elif command == "finished-job":
            assert data["args"]["job_id"] == self.current_job.id
            assert self.state is WorkerState.working

            if self.current_job.state is not JobState.stopped:
                self.current_job.finished(self, data["args"])
            self.current_job = None
            self.state = WorkerState.idle
            cherrypy.engine.publish("worker-state-change", self)
            cherrypy.engine.publish("worker-change", self)

        elif command == "abort-job":
            assert data["args"]["job_id"] == self.current_job.id
            assert self.state is WorkerState.working

            if self.current_job.state is not JobState.stopped:
                self.current_job.aborted(self, data["args"])
            self.current_job = None
            self.state = WorkerState.idle
            cherrypy.engine.publish("worker-state-change", self)
            cherrypy.engine.publish("worker-change", self)

        elif command == "fail-job":
            assert data["args"]["job_id"] == self.current_job.id
            assert self.state is WorkerState.working

            if self.current_job.state is not JobState.stopped:
                self.current_job.failed(self, data["args"])
            self.current_job = None
            self.state = WorkerState.idle
            cherrypy.engine.publish("worker-state-change", self)
            cherrypy.engine.publish("worker-change", self)

        elif command == "stopped-job":
            assert self.state is WorkerState.considering or self.state is WorkerState.working
            if self.state is WorkerState.considering:
                assert data["args"]["job_id"] == self.considering_job.id
            else:
                assert data["args"]["job_id"] == self.current_job.id

            self.considering_job = self.current_job = None
            self.state = WorkerState.idle
            cherrypy.engine.publish("worker-state-change", self)
            cherrypy.engine.publish("worker-change", self)

        else:
            self.logger.warning(f"Unknown or unexpected command {command}: {pprint.pformat(data)}")

    def consider(self, job):
        assert self.considering_job is None
        assert self.state is WorkerState.idle
        job.considered(self)
        self.considering_job = job
        self.state = WorkerState.considering
        self.send_command("consider-job", job_id=job.id, plugin=job.plugin.id, args=job.args)
        cherrypy.engine.publish("worker-state-change", self)
        cherrypy.engine.publish("worker-change", self)

    def job_stopped(self, job):
        assert self.considering_job is job or self.current_job is job
        self.send_command("stop-job", job_id=job.id)

    def send_command(self, command, **args):
        self.ws.send_json({
            "command": command,
            "args": args
        })

    def disconnect(self):
        if self.state is WorkerState.working:
            self.current_job.aborted(self, {})
            self.current_job = None
        elif self.state is WorkerState.considering:
            self.considering_job.rejected(self, {})
            self.considering_job = None
        self.state = WorkerState.disconnected
        cherrypy.engine.publish("worker-state-change", self)
        cherrypy.engine.publish("worker-plugins-changed", self)
        cherrypy.engine.publish("worker-change", self)


class WorkerManager(Manager):
    def __init__(self, bus):
        super().__init__(bus)

        self.worker_id = itertools.count()
        self.workers = {}
        self.free_workers = set()
        self.fw_protection = False

    def start(self):
        self.bus.log("WM: startup")
        self.bus.subscribe("worker-connected", self.worker_connected)
        self.bus.subscribe("worker-disconnected", self.worker_disconnected)
        self.bus.subscribe("worker-state-change", self.worker_state_change)
        self.bus.subscribe("view-free-workers", self.view_free_workers)
        self.bus.subscribe("view-workers", self.view_workers)

    def view_workers(self):
        return self.workers.copy()

    def worker_connected(self, ws):
        id = next(self.worker_id)
        self.logger.info(f"New worker connected, id={id}, ip={ws.address}")
        worker = self.workers[id] = Worker(id, ws, self.logger)
        ws.worker_id = id
        worker.send_command("startup", id=id)

    def worker_disconnected(self, ws):
        id = ws.worker_id
        self.logger.info(f"Worker {id} disconnected")
        self.workers[id].disconnect()

    # Safety first!
    # To ensure multiple free-workers events are not being handled at once we only fire the event when a worker
    # becomes idle. The callbacks registered to free-workers must only take the workers to the considering/working
    # state, not to the idle state. This ensures that more free-workers events are not generated which could cause
    # inefficiencies/recursion/assertion failures.

    def worker_state_change(self, worker):
        if worker.state == WorkerState.idle:
            self.free_workers.add(worker)

            if self.fw_protection:
                raise RuntimeError("FW protection failure!")

            self.fw_protection = True
            self.logger.debug(f"{len(self.free_workers)} free workers")
            try:
                if self.free_workers:
                    cherrypy.engine.publish("free-workers")
            finally:
                self.fw_protection = False
        else:
            self.free_workers.discard(worker)

    def view_free_workers(self):
        return self.free_workers.copy()
