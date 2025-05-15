



def check_compatibility(type_symbol, type_assignement):
    if type_symbol.upper() == type_assignement:
        return type_symbol
    if type_symbol == "int" and type_assignement == "FLOAT":
        return type_assignement
    if type_symbol == "float" and type_assignement == "INT":
        return type_assignement
    if type_symbol == "int" and type_assignement == "CHAR" or type_symbol == "float" and type_assignement == "CHAR":
        return type_symbol
    return False

def check_compatibility_expression(expression):
    pass



class Recordtable:
    def __init__(self):
        self._table = {}


class SymbolTable:
    def __init__(self):
        self._table = {}





