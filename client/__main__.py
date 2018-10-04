"""
Usage:
    dvns-client [--address=<address>] [--port=<port>]

Options:
    -a, --address=<address>         [default: 0.0.0.0]
    -p, --port=<port>               [default: 9000]
"""


import docopt
import sys
import pathlib
import iridescence

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

try:
    from . import run
except ImportError:
    from client import run

iridescence.quick_setup()

args = docopt.docopt(__doc__)

run(args["--address"], int(args["--port"]))
