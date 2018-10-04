import logging
import json
import pprint
import time
import random

from ws4py.client.threadedclient import WebSocketClient


logger = logging.getLogger(__name__)


class Worker(WebSocketClient):
    def opened(self):
        logger.info("Connected")

    def closed(self, code, reason=None):
        logger.info(f"Disconnected: {code} {reason.decode() if isinstance(reason, bytes) else reason}")

    def received_message(self, message):
        data = json.loads(message.data)
        command = data.get("command")
        if command == "startup":
            self.id = data["args"]["id"]
            logger.info(f"Startup complete, assigned worker id {self.id}")
            self.send_command("startup-complete")

        elif command == "consider-job":
            jobid = data["args"]["job_id"]
            logger.info(f"Offered job {jobid}")
            if self.consider_job(jobid):
                logger.info("Job accepted")
                self.send_command("accept-job", job_id=jobid)
                if self.perform_job(jobid):
                    logger.info("Job finished")
                    self.send_command("finished-job", job_id=jobid)
                else:
                    logger.info("Job failed")
                    self.send_command("fail-job", job_id=jobid)
            else:
                logger.info("Job rejected")
                self.send_command("reject-job", job_id=jobid)

        else:
            logger.warning(f"Unknown or unexpected command {command}: {pprint.pformat(data)}")

    def consider_job(self, job):
        return random.randrange(0, 2)

    def perform_job(self, job):
        time.sleep(5)
        return True

    def send_command(self, command, **args):
        self.send(json.dumps({
            "command": command,
            "args": args
        }))


def run(address, port):
    try:
        ws = Worker(f'ws://{address}:{port}/api/ws/worker', protocols=['http-only', 'chat'])
        ws.connect()
        ws.run_forever()
    except KeyboardInterrupt:
        ws.close()
