import sys
import os

from graphviz import Digraph

from lexer import ViperLexer
from parser import ViperParser
from pprint import pprint as pp
import graphviz
import ast


class Main():
    def __init__(self, route):
        self.__route = os.path.join(os.path.dirname(__file__), route)
        self.__lexer = ViperLexer(self.__route)
        self.__lexer.build()
        self.__lexer.run()
        self.__parser = ViperParser(self.__lexer, self.__route)

        result = self.__parser.parse()
        dot = Digraph(comment='Árbol Sintáctico')
        self.generate_graphviz(result, dot, node_id=0)  # Pasar node_id=0 explícitamente
        dot.render('syntax_tree.gv', view=True)
        print("Árbol sintáctico resultante:", pp(result))

    def parse_input(self,input_str):
        """Extrae la tupla del string de entrada"""
        start = input_str.find('(')
        tuple_str = input_str[start:]
        return ast.literal_eval(tuple_str)

    def print_tree(self, node, level=0):
        """Imprime el árbol en la terminal con indentación"""
        if isinstance(node, tuple):
            print(' ' * level * 2 + str(node[0]))
            for item in node[1:]:
                self.print_tree(item, level + 1)
        elif isinstance(node, list):
            for item in node:
                self.print_tree(item, level)
        else:
            # Manejo especial para \n
            display_value = 'nl' if node == '\n' else str(node)
            print(' ' * level * 2 + display_value)

    def generate_graphviz(self, tree, graph=None, parent=None, node_id=0):
        """Genera estructura para Graphviz recursivamente"""
        if graph is None:
            graph = Digraph()
            graph.node(name=str(node_id), label=str(tree[0]))
            parent = str(node_id)
            node_id = 1
        else:
            if parent is None:
                graph.node(name=str(node_id), label=str(tree[0]))
                parent = str(node_id)
                node_id += 1

        if isinstance(tree, (tuple, list)):
            for child in tree[1:] if isinstance(tree, tuple) else tree:
                if isinstance(child, (tuple, list)):
                    graph.node(name=str(node_id), label=str(child[0]))
                    if parent is not None:
                        graph.edge(parent, str(node_id))
                    new_parent = str(node_id)
                    node_id += 1
                    node_id = self.generate_graphviz(child, graph, new_parent, node_id)
                else:
                    # Manejo especial para \n
                    label = 'nl' if child == 'nl' else str(child)
                    graph.node(name=str(node_id), label=label)
                    if parent is not None:
                        graph.edge(parent, str(node_id))
                    node_id += 1
        return node_id


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 main.py <file>")
        exit(1)

    os.system("rm parser.out parsetab.py")

    Main(sys.argv[1])