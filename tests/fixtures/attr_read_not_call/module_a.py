"""Attribute read passed as an argument, not called.

`scheduler.run` is a bound-method *reference* handed to `register(...)`,
not a call. The pre-rewrite MethodsCalledNodeVisitor walked every Call's
whole subtree and recorded `scheduler.run` anyway (because `run` is a
method name in the project), inflating MPC and CBO (Phase 5, item 4).
"""


class Scheduler:
    def run(self):
        return 0


class App:
    def wire(self, scheduler, register):
        register(scheduler.run)
        return scheduler.run
