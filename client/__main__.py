"""
Usage:
    dvns-client [--address=<address>] [--port=<port>] [--processes=<processes>] [--threads=<threads>]

Options:
    -a, --address=<address>         [default: 0.0.0.0]
    -p, --port=<port>               [default: 9000]
    --processes=<processes>         [default: 1]
    --threads=<threads>             [default: 1]
"""


import docopt
import sys
import pathlib
import iridescence
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import itertools
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

try:
    from . import Worker
except ImportError:
    from client import Worker


def run(args):
    try:
        while True:
            ws = Worker(f"ws://{args['--address']}:{args['--port']}/api/ws/worker", protocols=["http-only", "chat"])
            try:
                ws.connect()
            except IOError:
                pass
            else:
                ws.run_forever()
            time.sleep(5)
    except KeyboardInterrupt:
        ws.close()


def run_threads(args):
    num_threads = int(args["--threads"])
    if num_threads == 1:
        run(args)
    else:
        with ThreadPoolExecutor(max_workers=num_threads) as ex:
            ex.map(run, itertools.repeat(args, num_threads))


def run_processes(args):
    num_processes = int(args["--processes"])
    if num_processes == 1:
        run_threads(args)
    else:
        with ProcessPoolExecutor(max_workers=num_processes) as ex:
            ex.map(run_threads, itertools.repeat(args, num_processes))


if __name__ == "__main__":
    iridescence.quick_setup()
    args = docopt.docopt(__doc__)
    run_processes(args)
