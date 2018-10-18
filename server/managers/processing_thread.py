import threading
import queue

from . import Manager


class ProcessingThread(Manager):
    def __init__(self, *args):
        super().__init__(*args)
        self.queue = queue.Queue()

    def start(self):
        self.thread = threading.Thread(target=self.run, name="proc-thread")
        self.thread.start()
        self.bus.subscribe("process", self.put)
        self.bus.subscribe("process-sync", self.put_sync)

    def run(self):
        self.logger.info("Processing thread starting")
        while True:
            item = self.queue.get()
            if item is None:
                self.logger.info("Processing thread stopping")
                return

            try:
                ret = item[0](*item[1], **item[2])
            except Exception as e:
                self.logger.error("Exception in processing thread", exc_info=True)
                if len(item) == 5:
                    item[4][0] = e
            else:
                if len(item) == 5:
                    item[4][1] = ret
            finally:
                if len(item) == 5:
                    item[3].set()

    def put(self, func, *args, **kwargs):
        self.queue.put((func, args, kwargs))

    def put_sync(self, func, *args, **kwargs):
        event = threading.Event()
        holder = [None, None]
        self.queue.put((func, args, kwargs, event, holder))
        event.wait()
        if holder[0]:
            raise holder[0]
        else:
            return holder[1]

    def stop(self):
        self.bus.unsubscribe("process", self.put)
        self.queue.put(None)
