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
    def __init__(self, id, logger):
        self.id = id
        self.logger = logger
        self.rejected_by = set()
        self.considered_by = None
        self.performed_by = None
        self.state = JobState.pending
        self.lock = threading.RLock()

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
        self.preformed_by = worker
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
        self.preformed_by = None
        self.state = JobState.pending
        cherrypy.engine.publish("job-state-change", self)


class JobManager(Manager):
    def __init__(self, bus):
        super().__init__(bus)

        self.job_id = itertools.count()
        self.jobs = {}

        for i in range(10):
            self.add_job()

    def start(self):
        self.bus.subscribe("free-workers", self.free_workers)
        self.bus.subscribe("view-jobs", self.view_jobs)

    def view_jobs(self):
        return self.jobs.copy()

    def add_job(self, *args, **kwargs):
        id = next(self.job_id)
        self.logger.info(f"New job, id={id}")
        job = self.jobs[id] = Job(id, self.logger, *args, **kwargs)
        self.bus.publish("request-free-workers")

    def free_workers(self, workers):
        for job in sorted(filter(lambda j: j.state is JobState.pending, self.jobs.values()), key=lambda j: j.id):
            for worker in filter(lambda w: w not in job.rejected_by, workers):
                worker.consider(job)
                workers.discard(worker)
                break
