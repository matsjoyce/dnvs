import logging
import json
import pprint
import threading

from ws4py.client.threadedclient import WebSocketClient

from .plugins import load_plugins, RejectJob, FailJob, StopJob
from .async_exc import async_raise


logger = logging.getLogger(__name__)


class Worker(WebSocketClient):
    def __init__(self, *args, definitions=[], **kwargs):
        super().__init__(*args, **kwargs)
        self.job = None
        self.definitions = dict(x.split("=", 1) if "=" in x else (x, True) for x in definitions)
        self.plugins = {}
        print(self.definitions)

    def opened(self):
        logger.info("Connected")

    def closed(self, code, reason=None):
        logger.info(f"Disconnected: {code} {reason.decode() if isinstance(reason, bytes) else reason}")

    def received_message(self, message):
        data = json.loads(message.data)
        command = data.get("command")
        if command == "startup":
            self.id = data["args"]["id"]
            for plugin in load_plugins():
                if plugin.available(self.definitions):
                    self.plugins[plugin.ID] = plugin
                    logger.debug(f"{plugin.ID}: {plugin.VERSION}")
                else:
                    logger.warning(f"Plugin {plugin} is not available")

            logger.info(f"Startup complete, assigned worker id {self.id}")
            self.send_command("startup-complete", plugins=[pl.info() for pl in self.plugins.values()])

        elif command == "consider-job":
            self.job_thread = threading.Thread(target=self.consider_job, args=(data,))
            self.job_thread.start()

        elif command == "stop-job":
            if self.job:
                logger.warning(f"Stopping job {self.job}")
                self.job.stop()
                async_raise(self.job_thread, StopJob)

        else:
            logger.warning(f"Unknown or unexpected command {command}: {pprint.pformat(data)}")

    def consider_job(self, data):
        try:
            jobid = data["args"]["job_id"]
            plugin = data["args"]["plugin"]
            logger.info(f"Offered job {jobid} using plugin {plugin}")
            cls = self.plugins[plugin]

            try:
                self.job = cls(data["args"]["args"], self.definitions)
            except RejectJob:
                logger.info("Job rejected")
                self.send_command("reject-job", job_id=jobid)
                return
            except Exception:
                logger.error("Job rejected by exception", exc_info=True)
                self.send_command("reject-job", job_id=jobid)
                return

            logger.info("Job accepted")
            self.send_command("accept-job", job_id=jobid)
            try:
                self.job.run()
            except FailJob:
                logger.info("Job failed")
                self.send_command("fail-job", job_id=jobid)
            except Exception:
                logger.error("Job failed by exception", exc_info=True)
                self.send_command("fail-job", job_id=jobid)
            else:
                logger.info("Job finished")
                self.send_command("finished-job", job_id=jobid)
        except StopJob:
            logger.info("Job stopped")
            self.send_command("stopped-job", job_id=jobid)
            return
        finally:
            self.job = None

    def send_command(self, command, **args):
        self.send(json.dumps({
            "command": command,
            "args": args
        }))
