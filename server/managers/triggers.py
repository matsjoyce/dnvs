import time


class Trigger:
    def __init__(self, data):
        self.conditions = [Condition.make(c) for c in data["conditions"]]
        self.schedule = Schedule.make(data["schedule"])

    def matches(self, item):
        return all(c.matches(item) for c in self.conditions)

    def next_run(self, has_run):
        return self.schedule.next_run(has_run)


class Condition:
    def matches(self, node):
        pass

    @staticmethod
    def make(cond):
        type = cond.pop("type")
        if type == "always":
            return Always(cond)
        elif type == "value":
            return Value(cond)
        raise RuntimeError()


class Always(Condition):
    def __init__(self, data):
        pass

    def matches(self, item):
        return True


class Value(Condition):
    def __init__(self, data):
        self.value = data.pop("value")
        self.checks = data

    def matches(self, item):
        value = item
        for attr in self.value.split("."):
            if attr.startswith("["):
                attr = int(attr[1:-1])
            value = value[attr]
        for name, check in self.checks.items():
            if name == "equals" and value != check:
                return False
            elif name == "in" and value not in check:
                return False
        return True


class Schedule:
    def next_run(self, has_run):
        pass

    @staticmethod
    def make(sched):
        type = sched.pop("type")
        if type == "oneshot":
            return OneShot(sched)
        raise RuntimeError()


class OneShot(Schedule):
    def __init__(self, data):
        pass

    def next_run(self, has_run):
        if not has_run:
            return time.time()
