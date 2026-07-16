import uuid

from injector import inject
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.mongodb import MongoDBSaver
from langgraph.constants import START, END
from langgraph.graph import StateGraph
from pymongo import MongoClient

from application.service.node.NodeList import NodeList
from src.application.service.node.eval.EvalNode import EvalNode
from src.infrastructure.adapters.mongo.MongoStore import MongoStore
from src.application.service.graph.GraphService import GraphService
from application.service.node.process.Node import Node
from src.domain.model.state.StateData import State


class GraphServiceImpl(GraphService):

    @inject
    def __init__(self, retriever_node: Node,
                 context_node: Node,
                 summarize_node: Node,
                 mongo_client: MongoClient,
                 global_error_node: Node,
                 clarification_more_info_node: EvalNode,
                 mongo_store: MongoStore):
        self._retriever_node = retriever_node
        self._context_node = context_node
        self._summarize_node = summarize_node
        self._mongo_client = mongo_client
        self._mongo_db_saver = MongoDBSaver(mongo_client)
        self._global_error_node = global_error_node
        self._mongo_store = mongo_store
        # Esto esta mal la config es en cada ejecucion
        self._clarification_more_info_node = clarification_more_info_node
        self._graph_app = self._init_graph()

    def invoke_graph(self, query: str, conversation_id: str):
        config = RunnableConfig(configurable={"thread_id": uuid.uuid4()})
        config["configurable"]["custom_mongo_store"] = self._mongo_store.get_store()
        result = self._graph_app.invoke({"user_query": query, "conversation_id": conversation_id}, config=config)
        return result.get("llm_response")

    def _init_graph(self):
        graph = StateGraph(State)
        graph.set_node_defaults(error_handler=self._global_error_node.as_graph_node)
        graph.add_node(NodeList.RETRIEVER, self._retriever_node.as_graph_node)
        graph.add_node(NodeList.SUMMARIZE, self._summarize_node.as_graph_node)
        graph.add_node(NodeList.GLOBAL_ERROR, self._global_error_node.as_graph_node)
        graph.add_conditional_edges(START,
                                    self._clarification_more_info_node.route
                                    )
        graph.add_edge(NodeList.RETRIEVER, NodeList.SUMMARIZE)
        graph.add_edge(NodeList.SUMMARIZE, END)
        # buscar como meter un store para tener la conversacion en memoria
        return graph.compile(checkpointer=self._mongo_db_saver, store=self._mongo_store.get_store())
