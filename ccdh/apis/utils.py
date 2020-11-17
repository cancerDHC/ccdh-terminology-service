from typing import List

from py2neo import Node
from flask import jsonify
import json


def marshal_node_list(node_list: List[Node]) -> object:
    return jsonify(node_list)


def marshall_node(node: Node) -> object:
    return jsonify(node)
