from exception import SemanticError

class Recordtable:
    def __init__(self):
        # mapea nombre de record -> Record
        self._table = {}
        self._basic_symbols = ("int", "float", "char", "bool")

    def add_record(self, type_name, fields):
        """Añade una definición de Record.
        record: instancia de objects.Record"""

        if type_name in self._table:
            raise SemanticError(f"Record '{type_name}' ya definido")
        self._table[type_name] = fields


    def lookup(self, name):
        """Devuelve el Record con ese nombre o None si no existe"""
        return self._table.get(name)

    def exists(self, name):
        """Comprueba si un Record está definido"""
        return name in self._table

    def __str__(self):
        return f"Record Table: {self._table}"


class SymbolTable:
    def __init__(self):
        # tablas separadas para variables y funciones
        self._variables = {}
        self._functions = {}
        self._scope = ""

    # ——— Variables ———————————————————————————————————————————
    def add_variable(self, variable):
        """Añade una Variable.
        variable: instancia de objects.Variable"""
        name = variable.name
        if name in self._variables:
            raise SemanticError(f"Variable '{name}' ya definida")
        self._variables[name] = variable

    def lookup_variable(self, name):
        """Devuelve la Variable con ese nombre o None si no existe"""
        return self._variables.get(name)

    def exists_variable(self, name):
        """Comprueba si una variable está definida"""
        return name in self._variables


    # ——— Funciones ———————————————————————————————————————————
    def add_function(self, function):
        """Añade una Function.
        function: instancia de objects.Function"""
        name = function.name
        if name in self._functions:
            print("SEMANTIC ERROR DETECTED")
            print(SemanticError(f"\tFUNCTION '{name}' IS ALREADY DEFINED"))
            print("")
        else:
            self._functions[name] = function

    def lookup_function(self, name):
        """Devuelve la Function con ese nombre o None si no existe"""
        return self._functions.get(name)

    def exists_function(self, name):
        """Comprueba si una función está definida"""
        return name in self._functions

    # ——— Genéricos ————————————————————————————————————————————
    def clear(self):
        """Vací­a ambas tablas"""
        self._variables.clear()
        self._functions.clear()

    def __str__(self):
        return f"SymbolTable({self._variables}, {self._functions})"
