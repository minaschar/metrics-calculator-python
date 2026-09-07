"""Attribute read passed as an argument, not called.

`scheduler.run` is a bound-method reference handed to `register(...)` and
also just returned -- neither is a call -- so `App` has MPC 0 and is not
coupled to `Scheduler` through it.
"""


class Scheduler:
    def run(self):
        return 0


class App:
    def wire(self, scheduler, register):
        register(scheduler.run)
        return scheduler.run
