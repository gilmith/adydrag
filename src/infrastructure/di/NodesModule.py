from typing import NewType

from injector import Module, singleton

from src.application.service.node.SummarizeNode import SummarizeNode
from src.application.service.node.Node import Node
from src.application.service.node.ContextNode import ContextNode
from src.application.service.node.RetrieverNode import RetrieverNode

RetrieverNodeKey = NewType('RetrieverNodeKey', Node)
ContextNodeKey = NewType('ContextNodeKey', Node)
SummarizeNodeKey = NewType('SummarizeNodeKey', Node)


class NodesModule(Module):
    def configure(self, binder):
        binder.bind(RetrieverNodeKey, to=RetrieverNode, scope=singleton)
        binder.bind(ContextNodeKey, to=ContextNode, scope=singleton)
        binder.bind(SummarizeNodeKey, to=SummarizeNode, scope=singleton)