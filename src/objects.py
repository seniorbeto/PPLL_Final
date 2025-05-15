# objects.py
# Modelo de los nodos AST para Viper

# Excepción semántica general
class SemanticError(Exception):
    pass

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
        if isinstance(self.value, str):
            return 'char'
        raise SemanticError("Tipo de literal desconocido: %r" % self.value)

class VariableRef(Expression):
    def __init__(self, name):
        self.name = name
        # ref_chain para futuros accesos a campos o índices
        self.ref_chain = []

    def add_field(self, field_name):
        self.ref_chain.append(('field', field_name))
        return self

    def add_index(self, index_expr):
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

# ——— Record (definición de tipo) ————————————————————————————————————

class Record:
    def __init__(self, name, fields):
        # fields: dict nombre_campo -> tipo (string)
        self.name = name
        self.fields = fields
