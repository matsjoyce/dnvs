import shutil
import subprocess
import time
import xml.etree.ElementTree as ET

from . import Plugin, RejectJob, Value, Always, OneShot, Trigger


class NmapPingScan(Plugin):
    ID = "nmap-ping-scan"
    VERSION = "1.0.0." + str(time.time())
    TARGET = "network"

    @classmethod
    def available(cls, defs):
        return shutil.which("nmap") is not None

    def run(self):
        cmd = ["nmap", "-sn", "-oX", "-", "-n", self.args["network"]["network"]]
        self.logger.info(f"Running {cmd}")
        output = subprocess.check_output(cmd)
        root = ET.fromstring(output.decode())
        for host in root.iter("host"):
            self.logger.info(host.find("address").get("addr"))
