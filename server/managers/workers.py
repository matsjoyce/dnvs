import itertools
import json
import enum
import pprint
import functools
import threading
import cherrypy

from . import Manager


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
        self.ws.received_message = self.received_message
        self.state = WorkerState.startup
        self.current_job = None
        self.considering_job = None
        self.lock = threading.RLock()

    @property
    def address(self):
        return self.ws.address

    def json(self):
        return {
            "id": self.id,
            "address": self.address,
            "state": self.state.name,
            "current_job": self.current_job.id if self.current_job else None,
            "considering_job": self.considering_job.id if self.considering_job else None
        }

    def locked(func):
        @functools.wraps(func)
        def lock_wrapper(self, *args, **kwargs):
            with self.lock:
                return func(self, *args, **kwargs)
        return lock_wrapper

    @locked
    def received_message(self, message):
        data = json.loads(message.data)
        command = data.get("command")

        if command == "startup-complete":
            assert self.state is WorkerState.startup
            self.state = WorkerState.idle

            cherrypy.engine.publish("worker-state-change", self)

        elif command == "accept-job":
            assert data["args"]["job_id"] == self.considering_job.id
            assert self.current_job is None
            assert self.state is WorkerState.considering
            self.considering_job.accepted(self, data["args"])
            self.current_job, self.considering_job = self.considering_job, None
            self.state = WorkerState.working

            cherrypy.engine.publish("worker-state-change", self)

        elif command == "reject-job":
            assert data["args"]["job_id"] == self.considering_job.id
            assert self.current_job is None
            assert self.state is WorkerState.considering
            self.considering_job.rejected(self, data["args"])
            self.considering_job = None
            self.state = WorkerState.idle
            cherrypy.engine.publish("worker-state-change", self)

        elif command == "finished-job":
            assert data["args"]["job_id"] == self.current_job.id
            assert self.state is WorkerState.working
            self.current_job.finished(self, data["args"])
            self.current_job = None
            self.state = WorkerState.idle
            cherrypy.engine.publish("worker-state-change", self)

        elif command == "abort-job":
            assert data["args"]["job_id"] == self.current_job.id
            assert self.state is WorkerState.working
            self.current_job.aborted(self, data["args"])
            self.current_job = None
            self.state = WorkerState.idle
            cherrypy.engine.publish("worker-state-change", self)

        elif command == "fail-job":
            assert data["args"]["job_id"] == self.current_job.id
            assert self.state is WorkerState.working
            self.current_job.failed(self, data["args"])
            self.current_job = None
            self.state = WorkerState.idle
            cherrypy.engine.publish("worker-state-change", self)

        else:
            self.logger.warning(f"Unknown or unexpected command {command}: {pprint.pformat(data)}")

    @locked
    def consider(self, job):
        assert self.considering_job is None
        assert self.state is WorkerState.idle
        job.considered(self)
        self.considering_job = job
        self.state = WorkerState.considering
        self.send_command("consider-job", job_id=job.id)
        cherrypy.engine.publish("worker-state-change", self)

    def send_command(self, command, **args):
        self.ws.send(json.dumps({
            "command": command,
            "args": args
        }))

    @locked
    def disconnect(self):
        if self.state is WorkerState.working:
            self.current_job.aborted(self, {})
            self.current_job = None
        elif self.state is WorkerState.considering:
            self.considering_job.rejected(self, {})
            self.considering_job = None
        self.state = WorkerState.disconnected
        cherrypy.engine.publish("worker-state-change", self)


class WorkerManager(Manager):
    def __init__(self, bus):
        super().__init__(bus)

        self.worker_id = itertools.count()
        self.workers = {}
        self.free_workers = set()
        self.lock = threading.RLock()
        self.rfw_protection = False

    def locked(func):
        @functools.wraps(func)
        def lock_wrapper(self, *args, **kwargs):
            with self.lock:
                return func(self, *args, **kwargs)
        return lock_wrapper

    def start(self):
        self.bus.log("WM: startup")
        self.bus.subscribe("worker-connected", self.worker_connected)
        self.bus.subscribe("worker-disconnected", self.worker_disconnected)
        self.bus.subscribe("worker-state-change", self.worker_state_change)
        self.bus.subscribe("request-free-workers", self.request_free_workers)
        self.bus.subscribe("view-workers", self.view_workers)

    def view_workers(self):
        return self.workers.copy()

    @locked
    def worker_connected(self, ws):
        id = next(self.worker_id)
        self.logger.info(f"New worker connected, id={id}, ip={ws.address}")
        worker = self.workers[id] = Worker(id, ws, self.logger)
        ws.worker_id = id
        worker.send_command("startup", id=id)

    @locked
    def worker_disconnected(self, ws):
        id = ws.worker_id
        self.logger.info(f"Worker {id} disconnected")
        self.workers[id].disconnect()

    # Safety first!
    # To ensure multiple free-workers events are not being handled at once we only fire the event when a worker becomes idle.
    # The callbacks registered to free-workers must only take the workers to the considering/working state, not to the idle state.
    # This ensures that more free-workers events are not generated which could cause inefficiencies/deadlocks/assertion failures.

    def worker_state_change(self, worker):
        if worker.state == WorkerState.idle:
            self.free_workers.add(worker)
            self.request_free_workers()
        else:
            self.free_workers.discard(worker)

    @locked
    def request_free_workers(self):
        if self.rfw_protection:
            raise RuntimeError("RFW protection failure!")

        self.rfw_protection = True
        self.logger.debug(f"{len(self.free_workers)} free workers")
        if self.free_workers:
            cherrypy.engine.publish("free-workers", self.free_workers.copy())
        self.rfw_protection = False
