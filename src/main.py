import sys
import os
from lexer import ViperLexer
from parser import ViperParser

class Main():
    def __init__(self, route):
        self.__route = os.path.join(os.path.dirname(__file__), route)
        self.__lexer = ViperLexer(self.__route)
        self.__lexer.build()
        self.__lexer.run()
        self.__parser = ViperParser(self.__lexer, self.__route)

        result = self.__parser.parse()
        print("Árbol sintáctico resultante:", result)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 main.py <file>")
        exit(1)

    Main(sys.argv[1])