# objects.py
# Modelo de los nodos
from tkinter.messagebox import RETRY

from exception import SemanticError

# Nodo base para todas las expresiones
class Expression:
    def infer_type(self, symbols, records):
        """Inferir y devolver el tipo de la expresión usando las tablas:
           symbols: tabla de símbolos de variables/funciones
           records: tabla de definiciones de records."""
        raise NotImplementedError()

# ——— Expr. atómicas ——————————————————————————————————————————————

class Literal(Expression):
    def __init__(self, value):
        self.value = value

    def infer_type(self, symbols, records):
        if isinstance(self.value, bool):
            return 'bool'
        if isinstance(self.value, int):
            return 'int'
        if isinstance(self.value, float):
            return 'float'

        if self.value == "true" or self.value == "false":
            return 'bool'
        if isinstance(self.value, str):
            return 'char'
        raise SemanticError("Tipo de literal desconocido: %r" % self.value)

    def __str__(self):
        return f"Literal({self.value})"

    def __repr__(self):
        return f"Literal({self.value})"

class VariableRef(Expression):
    def __init__(self, name):
        self.name = name
        # ref_chain para futuros accesos a campos o índices
        self.ref_chain = []

    def add_field(self, field_name, symbols, records):
        # 1. Inferimos el tipo actual de esta referencia
        base_type = self.infer_type(symbols, records)
        # 2. Comprobamos que es un record conocido
        record_def = records.lookup(base_type)
        if record_def is None:
            raise SemanticError(f"Tipo `{base_type}` no es un record")
        # 3. Comprobamos que el campo existe
        if field_name not in record_def.fields:
            raise SemanticError(f"Field `{field_name}` no existe en record `{base_type}`")
        # 4. Finalmente, registramos el acceso
        self.ref_chain.append(('field', field_name))
        return self

    def add_index(self, index_expr, symbols, records):
        # 1. Comprobamos el índice es un int
        idx_type = index_expr.infer_type(symbols, records)
        if idx_type != 'int':
            raise SemanticError(f"Índice de vector debe ser `int` (vino `{idx_type}`)")
        # 2. Inferimos el tipo actual y comprobamos que es vector
        base_type = self.infer_type(symbols, records)
        if not base_type.endswith('[]'):
            raise SemanticError(f"Tipo `{base_type}` no es un vector")
        # 3. Registramos el acceso
        self.ref_chain.append(('index', index_expr))
        return self

    def infer_type(self, symbols, records):
        # buscar variable
        var = symbols.lookup_variable(self.name)
        if not var:
            raise SemanticError("Variable no declarada: %s" % self.name)
        t = var.datatype
        # resolver cada acceso secuencialmente
        for kind, payload in self.ref_chain:
            if kind == 'field':
                rec = records.lookup(t)
                if not rec:
                    raise SemanticError("Tipo %s no es un record" % t)
                fields = rec.fields
                if payload not in fields:
                    raise SemanticError("Field %s no existe en %s" % (payload, t))
                t = fields[payload]
            elif kind == 'index':
                # payload es una Expression
                idx_type = payload.infer_type(symbols, records)
                if idx_type != 'int':
                    raise SemanticError("Índice no es int sino %s" % idx_type)
                # asumimos que el tipo vector acaba en []
                if not t.endswith('[]'):
                    raise SemanticError("Tipo %s no es vector" % t)
                t = t[:-2]  # sacamos el tipo del elemento
        return t

    def __repr__(self):
        result = f"{self.name}"
        for kind, payload in self.ref_chain:
            if kind == 'field':
                result += f".{payload}"
            elif kind == 'index':
                result += f"[{payload}]"
        return result

class FunctionCall(Expression):
    def __init__(self, name, args):
        self.name = name
        self.args = args

    def infer_type(self, symbols, records):
        func = symbols.lookup_function(self.name)
        if not func:
            raise SemanticError("Función no declarada: %s" % self.name)
        # comprobar número de argumentos
        if len(self.args) != len(func.parameters):
            raise SemanticError("Función %s espera %d args, tuvo %d" %
                                (self.name, len(func.parameters), len(self.args)))
        # comprobar tipos
        for expr, expected in zip(self.args, func.parameters):
            actual = expr.infer_type(symbols, records)
            if actual != expected:
                raise SemanticError("Param %s: esperado %s, obtenido %s" %
                                    (self.name, expected, actual))
        return func.return_type

class BinaryExpr(Expression):
    def __init__(self, op, left, right):
        self.op = op        # '+', '-', '*', '/', '==', '>', '<=', 'and', 'or',...
        self.left = left    # Expression
        self.right = right  # Expression

    def infer_type(self, symbols, records):
        lt = self.left.infer_type(symbols, records)
        rt = self.right.infer_type(symbols, records)
        # Aritméticas
        if self.op in ('+', '-', '*', '/'):
            if lt in ('int','float') and rt in ('int','float'):
                return 'float' if 'float' in (lt,rt) else 'int'
            #Hay que tener en cuenta los chars tmb. Char se puede convertir a int o float
            if lt == 'char' and rt in ('int','float'):
                return 'float' if 'float' in rt else 'int'
            if lt in ('int','float') and rt == 'char':
                return 'float' if 'float' in lt else 'int'


        # Relacionales
        if self.op in ('==','!=','>','<','>=','<='):
            if lt == rt:
                return 'bool'
        # Lógicas
        if self.op in ('and','or'):
            if lt == 'bool' and rt == 'bool':
                return 'bool'
        #raise SemanticError(f"Operador '{self.op}' no válido para tipos {lt} y {rt}")
        return SemanticError

    def __str__(self):
        return f"BinaryExpr({self.left}, {self.op}, {self.right})"

    def __repr__(self):
        return f"BinaryExpr({self.left}, {self.op}, {self.right})"

class UnaryExpr(Expression):
    def __init__(self, op, expr):
        self.op = op       # '-', '+', 'not'
        self.expr = expr   # Expression

    def infer_type(self, symbols, records):
        t = self.expr.infer_type(symbols, records)
        if self.op in ('-','+'):
            if t in ('int','float'):
                return t
        if self.op == 'not':
            if t == 'bool':
                return 'bool'
        raise SemanticError(f"Operador unario '{self.op}' no válido para tipo {t}")

    def __str__(self):
        return f"UnaryExpr({self.op},{self.expr})"

class Record:
    def __init__(self, name, fields):
        # fields: dict nombre_campo -> tipo (string)
        self.name = name
        self.fields = fields

class Variable:
    def __init__(self, name, datatype, value):
        self.name = name          # identificador
        self.datatype = datatype  # 'int', 'float', 'bool', 'char', 'Pair', 'int[]', etc.
        self.value = value

    def __str__(self):
        return f"Variable({self.name},{self.datatype},{self.value})"
    def __repr__(self):
        return f"Variable({self.name},{self.datatype},{self.value})"

# Definición de función (metadatos en tabla de símbolos)
class Function:
    def __init__(self, name, parameters, return_type):
        self.name = name                 # identificador
        self.parameters = parameters     # lista de tipos de parámetros, e.g. ['int','float']
        self.return_type = return_type   # tipo de retorno, e.g. 'bool'
