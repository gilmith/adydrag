from enum import Enum


class NodeList(str, Enum):

    # PROCESS NODES
    RETRIEVER = "retriever",
    SUMMARIZE = "summarize",
    REQUESTION = "requestion",
    K_NEAREST_NEIGHBORS = "k_nearest_neighbors",
    # EVAL NODES
    CLARIFICATION_OR_MORE_INFO = "clarification_or_more_info",
    # ERROR NODE
    GLOBAL_ERROR = "global_error"