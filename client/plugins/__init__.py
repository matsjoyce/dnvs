import abc
import pathlib
import importlib
import logging
import threading


REGISTERED_PLUGINS = set()
PLUGINS_PATH = pathlib.Path(__file__).parent


logger = logging.getLogger(__name__)

NOT_GIVEN = object()


class Condition:
    pass


class Always(Condition):
    def json(self):
        return {
            "type": "always"
        }


class Value(Condition):
    def __init__(self, value, equals=NOT_GIVEN, in_=NOT_GIVEN):
        self.value = value
        self.equals = equals
        self.in_ = in_

    def json(self):
        data = {
            "type": "value",
            "value": self.value,
        }
        if self.equals is not NOT_GIVEN:
            data["equals"] = self.equals
        if self.in_ is not NOT_GIVEN:
            data["in"] = self.in_
        return data


class Schedule:
    pass


class OneShot(Schedule):
    def json(self):
        return {
            "type": "oneshot"
        }


class Trigger:
    def __init__(self, conditions, schedule=OneShot()):
        self.conditions = conditions
        self.schedule = schedule

    def json(self):
        return {
            "conditions": [c.json() for c in self.conditions],
            "schedule": self.schedule.json()
        }


class PluginMeta(abc.ABCMeta):
    def __new__(mcls, name, bases, namespace, **kwargs):
        cls = super().__new__(mcls, name, bases, namespace, **kwargs)

        if not cls.__abstractmethods__:
            assert "ID" in cls.__dict__
            assert "VERSION" in cls.__dict__
            assert hasattr(cls, "TARGET") and cls.TARGET in ("network", "node")
            if not hasattr(cls, "TRIGGERS"):
                cls.TRIGGERS = [Trigger(conditions=[Always()], schedule=OneShot())]

            REGISTERED_PLUGINS.add(cls)
        return cls


class Plugin(metaclass=PluginMeta):
    def __init__(self, args, defs):
        super().__init__()
        self.args = args
        self.defs = defs
        self.logger = logging.getLogger(self.__class__.__module__)

    @abc.abstractmethod
    def run(self):
        pass

    def stop(self):
        pass

    @classmethod
    def available(cls, defs):
        return True

    @classmethod
    def info(cls):
        return {
            "id": cls.ID,
            "target": cls.TARGET,
            "version": cls.VERSION,
            "triggers": [c.json() for c in cls.TRIGGERS]
        }


class RejectJob(RuntimeError):
    pass


class FailJob(RuntimeError):
    pass


class StopJob(BaseException):
    pass


def load_module(path):
    path = path.relative_to(PLUGINS_PATH.parent.parent)
    module_name = ".".join(path.parent.parts + (path.stem,))
    logger.info(f"Loading module {module_name}")
    try:
        importlib.import_module(module_name, __package__ + ".plugins")
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
