import sys
import os

from lexer import ViperLexer
from parser import ViperParser
from pprint import pprint as pp


class Main:
    def __init__(self, route):
        self.__route = os.path.join(os.path.dirname(__file__), route)

        # Para habiliar el preprocesador, cambiar el siguiente argumento a True
        self.__lexer = ViperLexer(self.__route, allow_preprocess=False)
        self.__lexer.build()
        self.__lexer.run()

        self.__parser = ViperParser(self.__lexer)
        result = self.__parser.parse()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 main.py <file>")
        exit(1)

    Main(sys.argv[1])
