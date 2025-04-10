import graphviz
from graphviz import Digraph
import ast
import os

class TreeGen:
    def __init__(self, input_list:list, output_name:str, directory:str):
        self.__list = input_list
        self.__dot = Digraph(comment='Árbol Sintáctico')
        self.__output_name = f"{output_name}.gv"
        self.__temp = os.path.join(__file__,"")
        self.__directory = self.__temp.split("/tree_gen.py")[0] + directory
        self.generate_graphviz(self.__list, self.__dot, node_id=0)
        self.__dot.render(filename=self.__output_name,directory=self.__directory)

    def generate_graphviz(self, tree, graph=None, parent=None, node_id=0):
        """Genera estructura para Graphviz recursivamente"""
        if graph is None:
            graph = Digraph()
            label = str(tree[0]) if isinstance(tree, (list, tuple)) and tree else str(tree)
            graph.node(name=str(node_id), label=label)
            parent = str(node_id)
            node_id = 1
        else:
            if parent is None:
                label = str(tree[0]) if isinstance(tree, (list, tuple)) and tree else str(tree)
                graph.node(name=str(node_id), label=label)
                parent = str(node_id)
                node_id += 1

        if isinstance(tree, (tuple, list)):
            for child in tree[1:] if isinstance(tree, tuple) else tree:
                if isinstance(child, (tuple, list)) and child:
                    label = str(child[0])
                    graph.node(name=str(node_id), label=label)
                    if parent is not None:
                        graph.edge(parent, str(node_id))
                    new_parent = str(node_id)
                    node_id += 1
                    node_id = self.generate_graphviz(child, graph, new_parent, node_id)
                elif child is not None:
                    # Manejo especial para \n
                    label = 'nl' if child == 'nl' else str(child)
                    graph.node(name=str(node_id), label=label)
                    if parent is not None:
                        graph.edge(parent, str(node_id))
                    node_id += 1
        return node_id