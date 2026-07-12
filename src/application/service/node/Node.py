from abc import ABC, abstractmethod
from datetime import datetime

from pydantic import BaseModel

from src.application.service.exception.NodeException import NodeException
from src.domain.model.state.StateData import LogMeta, LogLevel, State


class Node(ABC):

    def __init__(self):
        self.name = self.__class__.__name__

    def template_method(self, state: State) -> State:
        log_entry = LogMeta(
            node_name=self.name,
            info=f"{self.name}: Iniciando ejecución",
            level=LogLevel.INFO,
            start_time=datetime.now()
        )
        try:
            result = self.execute(state)
            log_entry.info += ": Finalizado"
            log_entry.end_time = datetime.now()
            state.logs.append(log_entry)
            return result
        except NodeException as e:
            log_entry.end_time = datetime.now()
            log_entry.level = e.log_level
            log_entry.info += e.message
            state.logs.append(log_entry)
            raise e

    @abstractmethod
    def execute(self, state: State) -> State:
        """
            Metodo absolutamente abstrcto al final es un patron comando en bonito
        """
        pass

    def as_graph_node(self, state: BaseModel) -> BaseModel:
        """Método adaptador para LangGraph."""
        # Aquí puedes llamar a tu método run() u orquestador interno
        return self.template_method(state)