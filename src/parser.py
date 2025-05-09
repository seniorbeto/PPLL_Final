import ply.yacc as yacc
from lexer import ViperLexer


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

    def __init__(self, lexer: ViperLexer, route: str):
        """
        Creamos una instancia de ViperLexer y el parser Yacc.
        """
        self.lexer = lexer
        self.route = route
        self.parser = None

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
        statement : sentence
                  | type_definition
                  | function_definition
                  | NEWLINE
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = None

    def p_sentence(self, p):
        """
        sentence : expression NEWLINE
                 | assignment NEWLINE
                 | declaration NEWLINE
                 | if_statement
                 | while_statement
        """
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
        p[0] = (p[2], p[1], p[3])

    def p_expression_unary(self, p):
        """
        expression : NOT expression
                   | MINUS expression %prec MINUS
                   | PLUS expression %prec PLUS
        """
        p[0] = ("unary", p[1], p[2])

    def p_expression_literal(self, p):
        """
        expression : INT
                   | FLOAT
                   | CHAR
                   | ID
                   | TRUE
                   | FALSE
        """
        p[0] = ("literal", p[1])

    def p_expression_func_call(self, p):
        """
        expression : ID LPAREN argument_list RPAREN
        """
        p[0] = ("function_call", p[1], p[3])

    def p_argument_list(self, p):
        """
        argument_list : argument_list COMMA expression
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
        p[0] = ("reference", p[1], p[2])

    # Una referencia es la indexación de un vector o el acceso a un campo
    # de un registro. Ambas cosas pueden ser recursivas. Además, también
    # podemos tener una referencia simple (ID), por lo que referencia puede
    # ser lambda.
    def p_reference(self, p):
        """
        reference : reference LBRACKET expression RBRACKET
                  | reference DOT ID
                  |
        """
        if len(p) == 4:
            p[0] = ("index", p[2])
        elif len(p) == 3:
            p[0] = ("field", p[2])
        else:
            p[0] = (p[2], p[1])

    # En la siguiente regla contemplamos asignaciones simples y asignaciones en cadena
    def p_assignment(self, p):
        """
        assignment : ID reference EQUALS expression
                   | ID reference EQUALS assignment
        """
        if len(p) == 5:
            p[0] = ("assignment", p[1], p[3])
        else:
            p[0] = ("chain_assignment", p[1], p[3])

    def p_declaration(self, p):
        """
        declaration : INT_TYPE variable_list
                    | FLOAT_TYPE variable_list
                    | CHAR_TYPE variable_list
                    | BOOL_TYPE variable_list
                    | ID variable_list
        """
        p[0] = ("declaration", p[1], p[2])

    def p_variable_list(self, p):
        """
        variable_list : variable_list COMMA variable_declaration
                      | variable_declaration
        """
        if len(p) == 4:
            p[0] = p[1] + [p[3]]
        else:
            p[0] = [p[1]]

    def p_variable_declaration(self, p):
        """
        variable_declaration : ID assignment_declaration
                             | LBRACKET expression RBRACKET ID assignment_declaration
        """
        if len(p) == 3:
            p[0] = ("var", p[1],("assignment",p[2]))
        else:
            p[0] = ("vector_decl", p[4], p[2], ("assignment",p[5]))

    def p_assignment_declaration(self, p):
        """
        assignment_declaration : EQUALS expression
                               |
        """
        if len(p) == 3:
            p[0] = ("assign", p[2])


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
        self.parser = yacc.yacc(module=self)

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
