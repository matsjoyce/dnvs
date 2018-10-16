import enum
import itertools
import threading
import functools
import cherrypy

from . import Manager


class JobState(enum.Enum):
    pending = 0
    consideration = 1
    running = 2
    finished = 3
    failed = 4


class Job:
    def __init__(self, id, logger, plugin, args):
        self.id = id
        self.logger = logger
        self.args = args
        self.plugin = plugin
        self.rejected_by = set()
        self.considered_by = None
        self.performed_by = None
        self.state = JobState.pending
        self.lock = threading.RLock()

    def json(self):
        return {
            "id": self.id,
            "state": self.state.name,
            "args": self.args,
            "plugin": self.plugin,
            "rejected_by": [w.id for w in self.rejected_by],
            "considered_by": self.considered_by.id if self.considered_by else None,
            "performed_by": self.performed_by.id if self.performed_by else None,
        }

    def worker_can_perform(self, worker):
        if worker in self.rejected_by:
            return False
        if self.plugin not in worker.plugins:
            return False
        return True

    def locked(func):
        @functools.wraps(func)
        def lock_wrapper(self, *args, **kwargs):
            with self.lock:
                return func(self, *args, **kwargs)
        return lock_wrapper

    @locked
    def considered(self, worker):
        assert self.state == JobState.pending
        self.considered_by = worker
        self.state = JobState.consideration
        cherrypy.engine.publish("job-state-change", self)

    @locked
    def accepted(self, worker, args):
        assert self.state == JobState.consideration
        self.considered_by = None
        self.performed_by = worker
        self.state = JobState.running
        cherrypy.engine.publish("job-state-change", self)

    @locked
    def rejected(self, worker, args):
        assert self.state == JobState.consideration
        self.considered_by = None
        self.rejected_by.add(worker)
        self.state = JobState.pending
        cherrypy.engine.publish("job-state-change", self)

    @locked
    def finished(self, worker, args):
        assert self.state == JobState.running
        self.state = JobState.finished
        cherrypy.engine.publish("job-state-change", self)

    @locked
    def failed(self, worker, args):
        assert self.state == JobState.running
        self.state = JobState.failed
        cherrypy.engine.publish("job-state-change", self)

    @locked
    def aborted(self, worker, args):
        assert self.state == JobState.running
        self.performed_by = None
        self.state = JobState.pending
        cherrypy.engine.publish("job-state-change", self)


class JobManager(Manager):
    def __init__(self, bus):
        super().__init__(bus)

        self.job_id = itertools.count()
        self.jobs = {}

    def start(self):
        self.bus.log("JM: startup")
        self.bus.subscribe("free-workers", self.free_workers)
        self.bus.subscribe("view-jobs", self.view_jobs)
        self.bus.subscribe("job-create", self.create_job)

    def view_jobs(self):
        return self.jobs.copy()

    def create_job(self, plugin, args):
        id = next(self.job_id)
        self.logger.info(f"New job, id={id}, plugin={plugin}")
        job = self.jobs[id] = Job(id, self.logger, plugin, args)
        self.bus.publish("free-workers")

    def free_workers(self):
        workers, = self.bus.publish("view-free-workers")
        for job in sorted(filter(lambda j: j.state is JobState.pending, self.jobs.values()), key=lambda j: j.id):
            for worker in filter(lambda w: job.worker_can_perform(w), workers):
                worker.consider(job)
                workers.discard(worker)
                break
