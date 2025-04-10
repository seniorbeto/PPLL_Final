import sys
import os

EXPORT_TREE = False
try:
    from graphviz import Digraph
    from tree_gen import TreeGen
    EXPORT_TREE = True
except ImportError:
    pass

from lexer import ViperLexer
from parser import ViperParser
from pprint import pprint as pp


class Main:
    def __init__(self, route):
        self.__route = os.path.join(os.path.dirname(__file__), route)
        self.__lexer = ViperLexer(self.__route)
        self.__lexer.build()
        self.__lexer.run()
        self.__parser = ViperParser(self.__lexer, self.__route)
        result = self.__parser.parse()

        # Únicamente exporamos el árbol si se ha importado graphviz
        if not EXPORT_TREE:
            pp(result)
        else:
            self.__output_filename = self.__route.split("/input/")[-1].replace(".vip", "")
            try:
                TreeGen(result,self.__output_filename, "/tree_gen/")
            except Exception as e:
                print(f"[ERROR] {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 main.py <file>")
        exit(1)

    os.system("rm parser.out parsetab.py")
    os.system("rm -rf ./tree_gen/*")

    Main(sys.argv[1])