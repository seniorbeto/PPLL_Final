import ply.yacc as yacc
from lexer import ViperLexer

from objects import *
from tables import Recordtable, SymbolTable


class ViperParser:
    """
    Parser para el lenguaje Viper, usando PLY.
    """

    # Importamos la lista de tokens desde el lexer.
    tokens = ViperLexer.tokens

    # ------------------------------------------------------------
    # Precedencias y asociatividades
    # ------------------------------------------------------------
    precedence = (
        ("left", "OR", "AND"),
        ("left", "EQ", "GT", "LT", "GE", "LE"),
        ("left", "PLUS", "MINUS"),
        ("left", "TIMES", "DIVIDE"),
        ("right", "NOT"),
    )

    def __init__(self, lexer: ViperLexer):
        """
        Creamos una instancia de ViperLexer y el parser Yacc.
        """
        self.lexer = lexer
        self.route = self.lexer.parser_input_file
        self.parser = None

        self.record_table = Recordtable()
        self.symbol_table = SymbolTable()

    # ------------------------------------------------------------
    # Reglas de la gramática (sin cambiar la definición)
    # ------------------------------------------------------------

    # Axioma de la gramática (puede ser vacío)
    def p_program(self, p):
        """
        program : statement_list
                |
        """
        # Unificamos la salida: si no hay statements, devolvemos lista vacía
        statements = p[1] if len(p) > 1 and p[1] else []
        p[0] = ("program", statements)

    # Lista de sentencias
    def p_statement_list(self, p):
        """
        statement_list : statement_list statement
                       | statement
        """
        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = [p[1]]

    # ------------------------------------------------------------------
    # statement
    # ------------------------------------------------------------------
    def p_statement(self, p):
        """
        statement : sentence NEWLINE
                  | type_definition NEWLINE
                  | function_definition NEWLINE
                  | NEWLINE
        """
        self.symbol_table._scope = "statement"
        if len(p) == 3:
            p[0] = p[1]
        else:
            p[0] = None

    def p_sentence_list(self, p):
        """
        sentence_list : sentence_list sentence NEWLINE
                      | sentence NEWLINE
        """
        if len(p) == 4:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = [p[1]]

    def p_sentence(self, p):
        """
        sentence : expression
                 | assignment
                 | declaration
                 | if_statement
                 | while_statement
        """
        self.symbol_table._scope = "sentence"
        p[0] = p[1]

    def p_expression_binary(self, p):
        """
        expression : expression PLUS expression
                   | expression MINUS expression
                   | expression TIMES expression
                   | expression DIVIDE expression
                   | expression EQ expression
                   | expression GT expression
                   | expression LT expression
                   | expression GE expression
                   | expression LE expression
                   | expression AND expression
                   | expression OR expression
        """
        p[0] = BinaryExpr(p[2], p[1], p[3])

    def p_expression_unary(self, p):
        """
        expression : NOT expression
                   | MINUS expression %prec MINUS
                   | PLUS expression %prec PLUS
        """
        p[0] = UnaryExpr(p[2], p[1])

    def p_expression_literal(self, p):
        """
        expression : INT
                   | FLOAT
                   | CHAR
                   | TRUE
                   | FALSE
        """
        p[0] = Literal(p[1])

    def p_expression_func_call(self, p):
        """
        expression : ID LPAREN function_call_argument_list RPAREN
        """
        p[0] = FunctionCall(p[1], p[3])

    def p_function_call_argument_list(self, p):
        """
        function_call_argument_list : expression COMMA function_call_argument_list
                                    | expression
                                    |
        """
        if len(p) == 4:
            p[0] = p[1] + [p[3]]
        elif len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = []

    def p_expression_parentheses(self, p):
        """
        expression : LPAREN expression RPAREN
        """
        p[0] = p[2]

    def p_expression_reference(self, p):
        """
        expression : ID reference
        """
        var = VariableRef(p[1])
        print(f"var es {var}")

        print(f"p2 de expresion reference es {p[2]}")
        # P[1] es la lista de accesos a campos o índices recursivos
        # DENTRO DE ADD_FIELD O ADD_INDEX SE VERIFICA QUE NO EXISTA ANTES
        # EN LA TABLA DE SÍMBOLOS
        for kind, payload in p[2]:
            if kind == 'field':
                var.add_field(payload, self.symbol_table, self.record_table)
            else:  # 'index'
                var.add_index(payload, self.symbol_table, self.record_table)

        p[0] = var

    # Una referencia es la indexación de un vector o el acceso a un campo
    # de un registro. Ambas cosas pueden ser recursivas. Además, también
    # podemos tener una referencia simple (ID), por lo que referencia puede
    # ser lambda.
    def p_reference(self, p):
        """
        reference : LBRACKET expression RBRACKET reference
                  | DOT ID reference
                  |
        """
        # Caso en el que no hay más accesos
        if len(p) == 1:
            p[0] = []
            return

        # Caso vector
        if p[1] == '[':
            # p[2] = expresión del índice, p[4] = resto de la cadena
            p[0] = [('index', p[2])] + p[4]
        else:
            # Caso campo
            p[0] = [('field', p[2])] + p[3]

    # En la siguiente regla contemplamos asignaciones simples y asignaciones en cadena
    def p_assignment(self, p):
        """
        assignment : ID reference EQUALS expression
                   | ID reference EQUALS assignment
        """
        identifier = p[1]
        reference = p[2]
        value = p[4]
        if reference == []:
            var = self.symbol_table.lookup_variable(identifier)
            if var is None:
                print("SEMANTIC ERROR DETECTED IN ASSIGNMENT:")
                print(f"\tVariable {identifier} not found.")
            else:
                if isinstance(value, VariableRef) and self.record_table.exists(value) == False:
                    # SI ES UNA REFERENCIA QUE NO ESTA EN LA TABLA DE REGISTROS NO ES NADA, ERROR SEMANTICO
                    print("SEMANTIC ERROR DETECTED IN ASSIGNMENT:")
                    print(f"\tInvalid assignment to variable '{identifier}'. Attribute: {value} is not defined")
                else:
                    #COMPROBACION DE DATATYPE == VALOR ASIGNADO
                    if var.datatype != value.infer_type(var.datatype, value):
                        print("SEMANTIC ERROR DETECTED IN ASSIGNMENT:")
                        print(f"\tIncompatible types: {var.datatype.upper()} and {value.infer_type(var.datatype, value).upper()}")
                        print(f"\tVariables Affected: {identifier}")
        p[0] = ("assignment", p[1], p[2], p[4])


    def p_declaration(self, p):
        """
        declaration : INT_TYPE variable_list
                   | FLOAT_TYPE variable_list
                   | BOOL_TYPE variable_list
                   | CHAR_TYPE variable_list
                   | ID variable_list
        """
        datatype = p[1]
        variables = p[2]

        #DE HABER VALOR, SE GUARDA EN EL ÚLTIMO ELEMENTO DE VARIABLES
        if variables[-1].value != None:
            type = variables[-1].value.infer_type(datatype, variables[-1].value)
            if type != datatype and type!= SemanticError:
                print("SEMANTIC ERROR DETECTED IN DECLARATION AND ASSIGNEMENT:")
                print(f"\tIncompatible types: {datatype.upper()} and {variables[-1].value.infer_type(datatype, variables[-1].value).upper()}")
                print(f"\tVariables Affected: {', '.join(var.name for var in variables)}")
            else:
                for var in variables:
                    var.datatype = datatype
                    var.value = type
                    self.symbol_table.add_variable(var) if self.symbol_table._scope == "statement" else None
        else:
            #Hay que verificar que el tipo declarado sea correcto, pese a que el valor sea nulo
            if datatype not in self.record_table._basic_symbols and self.record_table.exists(datatype) == False:
                print("SEMANTIC ERROR DETECTED IN DECLARATION:")
                print(f"\tRecord {datatype} not found.")
                print(f"\tVariables Affected: {', '.join(var.name for var in variables)}")
            else:
                for var in variables:
                    var.datatype = datatype
                    self.symbol_table.add_variable(var) if self.symbol_table._scope == "statement" else None




        p[0] = ("declaration", datatype, variables) # Esto es para acumular algo

    def p_declaration_list(self, p):
        """
        declaration_list : declaration_list declaration NEWLINE
                         | declaration NEWLINE
        """
        if len(p) == 4:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = [p[1]]

    def p_variable_list(self, p):
        """
        variable_list : variable_list COMMA variable_declaration
                      | variable_declaration
        """
        list_variable = []
        if len(p) == 4:
            # p[0] = p[1] + [p[3]]
            p[0] = p[1] + [p[3]]
        else:
            # p[0] = [p[1]]
            p[0] = [p[1]]

    def p_variable_declaration(self, p):
        """
        variable_declaration : ID assignment_declaration
                             | LBRACKET expression RBRACKET ID assignment_declaration
        """
        if len(p) == 3:
            name = p[1]
            init = p[2]
            p[0] = (name, init)
            p[0] = Variable(name, None, init)
        else:
            size = p[2]
            name = p[4]
            init = p[5]
            p[0] = ((name, size), init)


    def p_assignment_declaration(self, p):
        """
        assignment_declaration : EQUALS expression
                               |
        """
        if len(p) == 3:
            p[0] = p[2]
        else:
            p[0] = None

    # En el "if" hacemos distinción entre el "if" y el "if-else". Consideramos
    # obligatorio el uso de un salto de línea entre el "if" y el "else" porque
    # es lo que se especifica en el enunciado.
    def p_if_statement(self, p):
        """
        if_statement : IF expression COLON LBRACE NEWLINE sentence_list RBRACE
                     | IF expression COLON LBRACE NEWLINE sentence_list RBRACE ELSE COLON LBRACE NEWLINE sentence_list RBRACE
        """
        if len(p) == 8:
            p[0] = ("if", p[2], p[6])
        else:
            p[0] = ("if_else", p[2], p[6], p[12])

    def p_while_statement(self, p):
        """
        while_statement : WHILE expression COLON LBRACE NEWLINE sentence_list RBRACE
        """
        p[0] = ("while", p[2], p[6])

    def p_type_definition(self,p):
        """
        type_definition : type_definition_header type_definition_body
        """
        print(f"type_definition body es {p[2]}")
        type_name = p[1]
        fields_declared = p[2]
        fields = []
        for field in fields_declared:
            #DE MOMENTO EL ELEMENTO VARIABLE O LO QUE COÑO SEA ESTÄ EN FIELD[2][0]
            for elems in field[2]:
                fields.append(elems)
        self.record_table.add_record(type_name, tuple(fields))
        print(self.record_table)
        p[0] = ("type_definition", p[2])

    def p_type_definition_header(self, p):
        """
        type_definition_header : TYPE ID COLON LBRACE NEWLINE
        """
        self.symbol_table._scope = "Type Definition"
        p[0] = p[2]


    def p_type_definition_body(self, p):
        """
        type_definition_body : declaration_list RBRACE
        """
        p[0] = p[1]

    def p_function_definition(self, p):
        """
        function_definition : DEF function_type ID LPAREN argument_list RPAREN COLON LBRACE NEWLINE sentence_list RETURN sentence RBRACE
        """
        p[0] = ("function_definition", p[2], p[3], p[5], p[10], p[12])

    def p_function_type(self, p):
        """
        function_type : INT_TYPE
                      | FLOAT_TYPE
                      | BOOL_TYPE
                      | CHAR_TYPE
                      | ID
        """
        p[0] = p[1]

    def p_argument_list(self, p):
        """
        argument_list : declaration SEMICOLON argument_list
                      | declaration
                      |
        """
        if len(p) == 4:
            p[0] = p[1] + [p[3]]
        elif len(p) == 2:
            p[0] = [p[1]]
        else:
            p[0] = []

    # ------------------------------------------------------------------
    # Manejo de errores sintácticos
    # ------------------------------------------------------------------
    def p_error(self, p):
        if p:
            # Obtener línea exacta usando la posición del token
            line_start = p.lexer.lexdata.rfind("\n", 0, p.lexpos) + 1
            line_end = p.lexer.lexdata.find("\n", p.lexpos)
            line = p.lexer.lexdata[line_start:line_end]
            line_num = p.lineno
            # No entendemos por qué hay que dividirlo entre dos para obtener la
            # línea. Fue una idea feliz que funcionó épicamente.
            print(f"Error sintáctico en línea:")
            print(f">>> {line}")
            print(f"    {' ' * (p.lexpos - line_start)}^")
        else:
            print("Error sintáctico al final del archivo.")

    def build(self, **kwargs):
        """
        Construye el parser con ply.yacc, usando las reglas definidas.
        """
        self.parser = yacc.yacc(module=self, debug=True, **kwargs)

    def parse(self):
        """
        Realiza el análisis sintáctico (parse) sobre el 'input_data'
        y retorna el árbol resultante (o None si hay error).
        """
        if not self.parser:
            self.build()

        with open(self.route, "r") as file:
            input_data = file.read()

        if not input_data.endswith("\n"):
            input_data += "\n"

        return self.parser.parse(input_data, lexer=self.lexer.lexer)
