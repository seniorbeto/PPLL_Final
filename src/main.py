import sys
import os

try:
    from graphviz import Digraph
    from tree_gen import TreeGen
except ImportError:
    pass

from lexer import ViperLexer
from parser import ViperParser
from pprint import pprint as pp


class Main:
    def __init__(self, route, export_tree):
        self.__route = os.path.join(os.path.dirname(__file__), route)
        self.__lexer = ViperLexer(self.__route, allow_preprocess=True)
        self.__lexer.build()
        self.__lexer.run()
        self.__parser = ViperParser(self.__lexer)
        result = self.__parser.parse()

        # Únicamente exporamos el árbol si se ha importado graphviz
        if not export_tree:
            pp(result)
        else:
            self.__output_filename = route.replace(".vip", "")
            try:
                TreeGen(result,self.__output_filename, "/tree_gen/")
            except Exception as e:
                print(f"[ERROR] {e}")

if __name__ == "__main__":
    if len(sys.argv) not in [2, 3] or (len(sys.argv) == 3 and sys.argv[2] != "true"):
        print("Usage: python3 main.py <file> <print_graph>")
        print("Argument <print_graph> is optional. If provided, it must be \"true\"")
        print(" and package graphviz needs to be installed.")
        print(" This will export the graph to a separate file.")
        print(" If not provided, the syntax tree will be printed to the console.")
        exit(1)

    export_tree = False
    if len(sys.argv) == 3 and sys.argv[2] == "true":
        try:
            from graphviz import Digraph
            from tree_gen import TreeGen
            export_tree = True
        except ImportError:
            print("[ERROR] graphviz package not installed. Please install it with pip.")
            exit(1)

    os.system("rm parser.out parsetab.py")

    Main(sys.argv[1],export_tree)