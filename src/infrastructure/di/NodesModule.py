from typing import NewType

from injector import Module, singleton

from src.application.service.node.eval.EvalNode import EvalNode
from src.application.service.node.eval.ClarificationMoreInfoEvalNode import ClarificationMoreInfoEvalNode
from src.application.service.node.GlobalErrorNode import GlobalErrorNode
from src.application.service.node.process.SummarizeNode import SummarizeNode
from src.application.service.node.process.Node import Node
from src.application.service.node.process.ContextNode import ContextNode
from src.application.service.node.process.RetrieverNode import RetrieverNode

RetrieverNodeKey = NewType('RetrieverNodeKey', Node)
ContextNodeKey = NewType('ContextNodeKey', Node)
SummarizeNodeKey = NewType('SummarizeNodeKey', Node)
GlobalErrorNodeKey = NewType('GlobalErrorNodeKey', Node)
ClarificationOrMoreInfoKey = NewType('ClarificationOrMoreInfoKey', EvalNode)

class NodesModule(Module):
    def configure(self, binder):
        binder.bind(RetrieverNodeKey, to=RetrieverNode, scope=singleton)
        binder.bind(ContextNodeKey, to=ContextNode, scope=singleton)
        binder.bind(SummarizeNodeKey, to=SummarizeNode, scope=singleton)
        binder.bind(GlobalErrorNodeKey, to=GlobalErrorNode, scope=singleton)
        binder.bind(ClarificationOrMoreInfoKey, to=ClarificationMoreInfoEvalNode, scope=singleton)