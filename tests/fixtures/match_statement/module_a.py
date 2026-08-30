class Router:
    def dispatch(self, command):
        match command:
            case "start":
                return "starting"
            case "stop":
                return "stopping"
            case _:
                return "unknown"
