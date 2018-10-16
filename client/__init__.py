import logging
import json
import pprint
import time
import random

from ws4py.client.threadedclient import WebSocketClient

from .plugins import load_plugins, RejectJob, FailJob


logger = logging.getLogger(__name__)


class Worker(WebSocketClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def opened(self):
        logger.info("Connected")

    def closed(self, code, reason=None):
        logger.info(f"Disconnected: {code} {reason.decode() if isinstance(reason, bytes) else reason}")

    def received_message(self, message):
        data = json.loads(message.data)
        command = data.get("command")
        if command == "startup":
            self.id = data["args"]["id"]
            self.plugins = load_plugins()
            for plugin in self.plugins.values():
                logger.debug(f"{plugin.ID}: {plugin.VERSION}")

            logger.info(f"Startup complete, assigned worker id {self.id}")
            self.send_command("startup-complete", plugins=[pl.info() for pl in self.plugins.values()])

        elif command == "consider-job":
            jobid = data["args"]["job_id"]
            plugin = data["args"]["plugin"]
            logger.info(f"Offered job {jobid} using plugin {plugin}")
            cls = self.plugins[plugin]
            logger.debug(cls)
            try:
                job = cls(data["args"]["args"])
            except RejectJob:
                logger.info("Job rejected")
                self.send_command("reject-job", job_id=jobid)
            except Exception:
                logger.error("Job rejected by exception", exc_info=True)
                self.send_command("reject-job", job_id=jobid)
            else:
                logger.info("Job accepted")
                self.send_command("accept-job", job_id=jobid)
                try:
                    job.run()
                except FailJob:
                    logger.info("Job failed")
                    self.send_command("fail-job", job_id=jobid)
                except Exception:
                    logger.error("Job reFailedjected by exception", exc_info=True)
                    self.send_command("fail-job", job_id=jobid)
                else:
                    logger.info("Job finished")
                    self.send_command("finished-job", job_id=jobid)

        else:
            logger.warning(f"Unknown or unexpected command {command}: {pprint.pformat(data)}")

    def send_command(self, command, **args):
        self.send(json.dumps({
            "command": command,
            "args": args
        }))
