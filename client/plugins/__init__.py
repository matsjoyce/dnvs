import abc
import pathlib
import traceback
import importlib
import logging
import threading


REGISTERED_PLUGINS = {}
PLUGINS_PATH = pathlib.Path(__file__).parent


logger = logging.getLogger(__name__)


class Plugin(abc.ABC):
    def __init__(self, args):
        super().__init__()
        self.args = args

    @abc.abstractmethod
    def run(self):
        pass

    @abc.abstractmethod
    def stop(self):
        pass

    @classmethod
    def available(cls):
        return True

    @classmethod
    def __init_subclass__(cls):
        assert "ID" in cls.__dict__
        assert "VERSION" in cls.__dict__

        if cls.available():
            REGISTERED_PLUGINS[cls.ID] = cls
        else:
            logger.warning(f"Plugin {cls} is not available")

    @classmethod
    def info(cls):
        return {
            "id": cls.ID,
            "version": cls.VERSION
        }


class RejectJob(RuntimeError):
    pass


class FailJob(RuntimeError):
    pass


def load_module(path):
    path = path.relative_to(PLUGINS_PATH.parent.parent)
    module_name = ".".join(path.parent.parts + (path.stem,))
    logger.info(f"Loading module {module_name}")
    try:
        module = importlib.import_module(module_name, __package__ + ".plugins")
    except Exception:
        logger.error(f"Loading module {module_name} failed:", exc_info=True)


def load_directory(path):
    if path.name.startswith("__") or path.name.startswith("."):
        return
    elif path.is_dir():
        if (path / "__init__.py").exists():
            load_module(path)
        for subpath in path.iterdir():
            load_directory(subpath)
    elif path.suffix == ".py":
        load_module(path)


lp_lock = threading.Lock()


def load_plugins():
    with lp_lock:
        if not REGISTERED_PLUGINS:
            load_directory(PLUGINS_PATH)
        return REGISTERED_PLUGINS
