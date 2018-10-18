"""
Usage:
    dvns-server [--address=<address>] [--port=<port>] [--log=<logspec>]...

Options:
    -a, --address=<address>         [default: 0.0.0.0]
    -p, --port=<port>               [default: 9000]
    -l, --log=<logspec>
"""


import docopt
import sys
import pathlib
import iridescence
import logging

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

try:
    from . import run
except ImportError:
    from server import run

iridescence.quick_setup()

args = docopt.docopt(__doc__)

for logspec in args["--log"]:
    module, level = logspec.split(":")
    level = getattr(logging, level.upper())
    logging.getLogger(module).setLevel(level)

run(args["--address"], int(args["--port"]))
