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
        ('left', 'OR', 'AND'),
        ('left', 'EQ', 'GT', 'LT', 'GE', 'LE'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'TIMES', 'DIVIDE'),
        ('right', 'NOT'),
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
        statement : declaration NEWLINE
                  | assignment NEWLINE
                  | if_statement
                  | TYPE register
                  | while_statement
                  | COMMENT NEWLINE
                  | MLCOMMENT NEWLINE
                  | funct_decl
                  | funct_call NEWLINE
                  | NEWLINE
        """
        # Si es una ´declaración de un registro es el único
        # caso distinto
        if len(p) == 3 and "register" in p[2]:
            p[0] = p[2]

        else:
            p[0] = p[1]

    # Sentencia de declaración
    def p_declaration(self, p):
        """
        declaration : INT_TYPE var_list
                    | FLOAT_TYPE var_list
                    | CHAR_TYPE var_list
                    | BOOL_TYPE var_list
                    | ID var_list
        """
        p[0] = ("declaration", p[1], p[2])

    def p_register(self, p):
        """
        register : ID COLON block
        """
        # Ejemplo: ("register", "MiRegistro", ("block", [...]))
        p[0] = ("register", p[1], p[3])

    # TODO
    # Declaración de variable (o vector)
    def p_var_decl(self, p):
        """
        var_decl : ID decl_assign
                 | LBRACKET expression RBRACKET ID decl_assign
        """
        if len(p) == 3:
            p[0] = ("var", p[1],("assignment",p[2]))
        else:
            p[0] = ("vector_decl", p[4], p[2], ("assignment",p[5]))  # p[4] es el ID, p[2] es el tamaño



    #TODO
    def p_decl_assign(self, p):
        """
        decl_assign : EQUALS expression
                    |
        """
        if len(p) == 3:
            p[0] = ("assign", p[2])

    # Lista de variables
    def p_var_list(self, p):
        """
        var_list : var_list COMMA var_decl
                 | var_decl
        """
        if len(p) == 4:
            p[0] = p[1] + [p[3]]
        else:
            p[0] = [p[1]]

    # Sentencia de asignación
    def p_assignment(self, p):
        """
        assignment : reference EQUALS assignment
                   | reference EQUALS expression
        """
        if isinstance(p[3], tuple) and p[3][0] in ("assign", "assign_recursive"):
            p[0] = ("assign_recursive", p[1], p[3])
        else:
            p[0] = ("assign", p[1], p[3])

    def p_reference(self, p):
        """
        reference : ID rest_ref
        """
        ref = ("id", p[1])
        if p[2] is None:
            p[0] = ref
        else:
            p[0] = (p[2][0], ref, *p[2][1:])

    def p_rest_ref(self, p):
        """
        rest_ref :
                 | DOT ID rest_ref
                 | LBRACKET expression RBRACKET rest_ref
        """
        if len(p) == 1:
            p[0] = None  # fin de la referencia
        elif len(p) == 4:
            # Caso DOT ID rest_ref
            if p[3] is None:
                p[0] = ("dot", ("id", p[2]))
            else:
                p[0] = ("dot", ("id", p[2]), p[3])
        else:
            # Caso LBRACKET expression RBRACKET rest_ref
            if p[4] is None:
                p[0] = ("index", p[2])
            else:
                p[0] = ("index", p[2], p[4])


    # -------------------------------------------------------------------
    # Estructura de declaración de funciones
    # def <Tipo de retorno> <Id_funcion> "(" <lista_argumentos> ")" ":" <BLOQUE_FUNC>
    #
    # BLOQUE_FUNC es del tipo:
    # "{" <BLOQUE_SENTENCIAS> return <SENTENCIA> "}"
    def p_funct_decl(self, p):
        """
        funct_decl : DEF type_funct ID LPAREN arg_funct RPAREN COLON block_funct
        """
        # Ejemplo de nodo: ("funct_decl", return_type, function_name, args, block)
        p[0] = ("funct_decl", p[2], p[3], p[5], p[8])

    # Llamada a funciones
    def p_funct_call(self, p):
        """
        funct_call : ID LPAREN arg_funct_call RPAREN
        """
        # Ej: ("funct_call", "miFuncion", [expr, expr, ...])
        p[0] = ("funct_call", p[1], p[3])

    #TODO
    def p_arg_funct_call(self, p):
        """
        arg_funct_call : expression COMMA arg_funct_call
                       | expression
                       |
        """
        if len(p) == 4:
            # p[1] es expression, p[3] es lista
            # Convertimos todo a lista unificada
            # Cuidado: p[1] es una tupla, p[3] es la lista de expresiones
            if not isinstance(p[3], list):
                p[3] = [p[3]]
            p[0] = [p[1]] + p[3]
        elif len(p) == 2:
            p[0] = [p[1]]


    def p_type_funct(self, p):
        """
        type_funct : INT_TYPE
                   | FLOAT_TYPE
                   | BOOL_TYPE
                   | CHAR_TYPE
                   | ID
        """
        p[0] = ("type_funct", p[1])

    # TODO
    # Argumentos de función
    def p_arg_funct(self, p):
        """
        arg_funct : type_funct arg_funct2
                  |
        """
        # Para simplificar la estructura, se puede hacer:
        if len(p) > 1:
            p[0] = ("arg_funct", "type", p[1], "args", p[2])

    # TODO
    def p_arg_funct2(self, p):
        """
        arg_funct2 : ID extra another
        """
        # Para simplificar la estructura, se puede hacer:
        p[0] = ((p[1]) , (p[2] or []) , (p[3] or []))

    # TODO
    def p_arg_funct_rec(self,p):
        """
        arg_funct_rec : type_funct ID extra another
        """
        p[0] = ([(p[1], p[2])] + (p[3] or []) + (p[4] or []))

    # Extra (coma y más IDs)
    def p_extra(self, p):
        """
        extra : COMMA ID extra
              |
        """
        if len(p) == 1:
            p[0] = []
        else:
            p[0] = [(None, p[2])] + (p[3] or [])

    def p_another(self, p):
        """
        another : SEMICOLON arg_funct_rec
                |
        """
        if len(p) == 1:
            p[0] = []
        else:
            # p[2] es ("arg_funct_rec", [ ... ])
            p[0] = [p[2]]

    # Bloque de función
    def p_block_funct(self, p):
        """
        block_funct : newlines LBRACE statement_list funct_ret RBRACE NEWLINE
        """
        # p[3] es la lista de statements, p[4] es el return
        p[0] = ("block_funct", p[3], p[4])

    def p_funct_ret(self, p):
        """
        funct_ret : RETURN expression newlines
        """
        # p[0] = ("return", "x")
        p[0] = ("funct_ret", p[2])

    def p_newlines(self, p):
        """
        newlines : NEWLINE
                 |
        """
        # Podemos ignorarlos
        p[0] = None

    # ------------------------------------------------------------------
    # if_statement
    # ------------------------------------------------------------------
    def p_if_statement(self, p):
        """
        if_statement : IF expression COLON block else
        """
        # p[2] es la condición, p[4] el bloque, p[5] el else (o None)
        p[0] = ("if_statement", p[2], p[4], p[5])

    def p_else(self, p):
        """
        else  : newlines ELSE COLON block
              | NEWLINE
        """
        if len(p) == 5:
            p[0] = ("else", p[4])
        else:
            p[0] = None

    # ------------------------------------------------------------------
    # while_statement
    # ------------------------------------------------------------------
    def p_while_statement(self, p):
        """
        while_statement : WHILE expression COLON block
        """
        p[0] = ("while_statement", p[2], p[4])

    # ------------------------------------------------------------------
    # Bloque
    # ------------------------------------------------------------------
    def p_block(self, p):
        """
        block : newlines LBRACE statement_list RBRACE
        """
        p[0] = ("block", p[3])

    # ------------------------------------------------------------------
    # Expresiones
    # ------------------------------------------------------------------
    def p_expression_binop(self, p):
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
        p[0] = ("binop", p[2], p[1], p[3])

    def p_expression_unary(self, p):
        """
        expression : NOT expression
                   | MINUS expression %prec MINUS
                   | PLUS expression %prec PLUS
        """
        p[0] = ("unary", p[1], p[2])

    def p_expression_paren(self, p):
        """
        expression : LPAREN expression RPAREN
        """
        p[0] = p[2]

    def p_expression_literal(self, p):
        """
        expression : DECIMAL
                   | BINARY
                   | OCTAL
                   | HEXADECIMAL
                   | FLOAT_CONST
                   | TRUE
                   | FALSE
                   | CHAR_CONST
        """
        p[0] = ("literal", p[1])



    def p_expression_funct_call(self, p):
        """
        expression : funct_call
        """
        # p[1] ya es ("funct_call", name, [args...])
        p[0] = p[1]

    def p_expression_reference(self, p):
        """
        expression : reference
        """
        p[0] = p[1]

    # ------------------------------------------------------------------
    # Manejo de errores sintácticos
    # ------------------------------------------------------------------
    def p_error(self, p):
        if p:
            # Obtener línea exacta usando la posición del token
            line_start = p.lexer.lexdata.rfind('\n', 0, p.lexpos) + 1
            line_end = p.lexer.lexdata.find('\n', p.lexpos)
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
        self.parser = yacc.yacc(
            module=self,
        )

    def parse(self):
        """
        Realiza el análisis sintáctico (parse) sobre el 'input_data'
        y retorna el árbol resultante (o None si hay error).
        """
        if not self.parser:
            self.build()

        with open(self.route, 'r') as file:
            input_data = file.read()

        if not input_data.endswith("\n"):
            input_data += "\n"

        return self.parser.parse(input_data, lexer=self.lexer.lexer)
