BASIC_FORMAT = ["int", "str", "float", "bool"] #ETC

from sem import Semantic


def check_table(datatype, existing_dict ):
    if datatype in existing_dict.keys():
        return datatype
    return ValueError("The datatype '{}' is not defined.".format(datatype))



class Vector:
    def __init__(self, name: str, size: int, datatype:str):
        self.__name = name
        self.__size = size
        self.__datatype = datatype

    def __str__(self):
        return f"Vector({self.__name}, {self.__size}, {self.__datatype})"



class Register:
    def __init__(self, name:str, **kwargs):
        self._name = name
        self._atributes = {}
        for key, value in zip(kwargs.keys(), kwargs.values()):
            self._atributes[key] = value[0] if len(value) == 1 else Vector(key,value[1], value[0])

    def __str__(self):
        str = ""
        str += f"Register({self._name})"
        for key, value in self._atributes.items():
            str += f"\n\t{key}: {value}"

        return str


class Variable:
    def __init__(self, name:str, datatype:str, existing_dict:dict):
        self._name = name
        self._datatype = datatype if BASIC_FORMAT.__contains__(datatype) else check_table(datatype, existing_dict)

    def __str__(self):
        return f"Variable({self._name}, {self._datatype})"


class Function:
    def __init__(self, name: str, return_type:str, arguments:dict, existing_dict:dict):
        self._name = name
        self._return_type = return_type if BASIC_FORMAT.__contains__(return_type) else check_table(datatype, existing_dict)
        self._arguments = []
        for arg in arguments.values():
            if BASIC_FORMAT.__contains__(arg):
                self._arguments.append(arg)
            else :
                if check_table(arg, existing_dict) != ValueError :
                    self._arguments.append(arg)


    def __str__(self):
        str = f"Function({self._name}, {self._return_type})"
        """for key, value in self._arguments.items():
            str += f"\n\t{key}: {value}"
"""
        for arg in self._arguments:
            str += f"\n\t{arg}"
        return str




datatype = {}

variable1 = Variable("var1", "int" , datatype)
print(variable1)
variable2 = Variable("var2", "float", datatype)
print(variable2)


arguments = {"b": ["int"],"a": ["char"], "c": ["Register", 3]}
c = Register("register", **arguments)
datatype[c._name] = c._atributes

print(c)

variable3 = Variable("var3", "register", datatype)
print(variable3)

func_arg = {"a": "int", "b": "char", "c": "Register"}
funcionn = Function("funcion", "int", arguments, datatype)
print(funcionn)








