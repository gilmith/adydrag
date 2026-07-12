from src.domain.model.state.StateData import LogLevel


class NodeException(Exception):

    def __init__(self, message: str, log_level: LogLevel):
        self.message = message
        self.log_level = log_level

