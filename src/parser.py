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
    #
    # Aquí definimos la precedencia (de menor a mayor) para
    # evitar ambigüedades en expresiones como "a + b * c".
    #
    # El formato es:
    #   (asociatividad, 'TOKEN', 'TOKEN', ...)
    #
    # Ejemplo de menor precedencia a mayor:
    #  - 'OR', 'AND' (operadores lógicos)
    #  - comparaciones EQ, GT, etc.
    #  - aritméticos +, -
    #  - aritméticos *, /
    #  - NOT es unario (por eso right)
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
    # Reglas de la gramática
    #
    # La estructura principal que sugiere el enunciado es:
    # - El programa (program) está compuesto por sentencias (statements).
    # - Hay varios tipos de sentencias: declaración, asignación, control de flujo, etc.
    # - Las expresiones combinan operandos aritméticos, booleanos, etc.
    # - Los saltos de línea (NEWLINE) o ';' pueden servir de separadores (depende de tu diseño).
    # ------------------------------------------------------------

    # Regla de partida: el programa completo
    def p_program(self, p):
        """
        program : statement_list
                  |
        """
        # p[0] será la representación interna (AST, lista de sentencias, etc.)
        p[0] = (p[1] if len(p) > 1 else None)

    # Lista de sentencias
    #
    # Cada statement puede estar seguido opcionalmente de NEWLINE,
    # dependiendo de cómo quieras estructurarlo. Aquí lo hacemos
    # simple y asumimos que cada statement va seguido de NEWLINE.
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
    # Definimos statement como: declaración, asignación, if, while, etc.
    # Ajusta estas reglas según tu gramática final.
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
                  | NEWLINE
        """
        p[0] = (p[1] if len(p) == 2 else p[2])

    # Sentencia de declaración, ejemplo simple:
    #
    #  int a, b, c
    #  float x
    #
    # TODO: AQUÍ DEBERÍAN CONTEMPLARSE LAS "VARIABLES DE TIPO REGISTRO"
    def p_declaration(self, p):
        """
        declaration : INT_TYPE var_list
                    | FLOAT_TYPE var_list
                    | CHAR_TYPE var_list
                    | BOOL_TYPE var_list
                    | ID ID
        """
        # p[1] es el tipo (INT_TYPE, FLOAT_TYPE, etc.)
        # p[2] es la lista de variables devuelta por var_list
        p[0] = ("declaration", p[1], p[2])


    def p_register(self,p):
        """
        register : ID COLON block
        """
        p[0] = ("register", p[1], p[3])

    # Declaración de variables o de vectores
    def p_var_decl(self, p):
        """
        var_decl : ID
                 | LBRACKET expression RBRACKET ID
        """
        if len(p) == 2:
            p[0] = ("var", p[1])
        else:
            p[0] = ("vector", p[4], p[2])  # p[4] es el ID, p[2] es el tamaño

    # var_list: una lista de identificadores separada por comas
    #
    #  a, b, c
    #  foo
    #  x, y
    def p_var_list(self, p):
        """
        var_list : var_list COMMA var_decl
                 | var_decl
        """
        if len(p) == 4:
            p[0] = p[1] + [p[3]]  # p[1] es la lista previa, p[3] el nuevo ID
        else:
            p[0] = [p[1]]

    # Sentencia de asignación
    #
    #  a = expr
    # También se puede asignar a un vector y asignar a un valor
    # TODO CREO QUE NO PODEMOS HACER ASIGNACIONES A UN VECTOR TIENE QUE SER UN INT POR COJONES O UNA VAR de tipo INT
    # que se acaba de declarar
    def p_assignment(self, p):
        """
        assignment : ID EQUALS expression
                    | ID LBRACKET DECIMAL RBRACKET EQUALS expression
                    | ID LBRACKET ID RBRACKET EQUALS expression
                    | declaration EQUALS expression
                    | ID EQUALS assignment
                    | ID DOT unique_assignment
        """
        if len(p) == 7:
            # Asignación a un vector: ID [ expression ] = expression
            p[0] = ("assign_vector", p[1], p[3], p[6])
        elif len(p) == 4:
            # Si p[1] proviene de una declaración, usamos la alternativa declaration EQUALS expression
            if isinstance(p[1], tuple) and p[1][0] == "declaration":
                p[0] = ("assign_declaration", p[1], p[3])
            else:
                # Diferenciamos entre simple asignación (ID = expression)
                # y asignación recursiva (ID = assignment) comprobando el tipo de p[3].
                # Se asume que, en la alternativa recursiva, p[3] es una tupla
                # cuyo primer elemento indica que es resultado de una asignación.
                if isinstance(p[3], tuple) and p[3][0] in ("assign", "assign_vector", "assign_declaration", "assign_recursive"):
                    p[0] = ("assign_recursive", p[1], p[3])
                else:
                    p[0] = ("assign", p[1], p[3])


    # -------------------------------------------------------------------
    #Esto se usa para asignar a un valor de un registro. Puede ser o un id = Expr
    # o un id [id] = Expr o id[numero] = Expr
    def p_unique_assignment(self, p):
        """
        unique_assignment : ID EQUALS expression
                          | ID LBRACKET DECIMAL RBRACKET EQUALS expression
                            | ID LBRACKET ID RBRACKET EQUALS expression
        """
        if len(p) == 4:
            p[0] = ("unique_assign", p[1], p[3])
        else:
            p[0] = ("unique_assign_recursive", p[1], p[3])


    #-------------------------------------------------------------------
    # Estructura de declaración de funciones
    # def <Tipo de retorno> <Id_funcion> "(" <lista_argumentos> ")" ":" <BLOQUE_FUNC>
    #
    # BLOQUE_FUNC es del tipo:
    # "{" <BLOQUE_SENTENCIAS> return <SENTENCIA> "}"
    def p_funct_decl(self, p):
        """
        funct_decl : DEF type_funct ID LPAREN arg_funct RPAREN COLON block_funct
        """
    #TODO ESTO LO HE DESARROLLADO COMO LA QUE HICIMOS EN LA PIZARRA    L-> type id D OTRA
                                                                #TODO  D-> ,idD | lambda
                                                                #TODO  OTRA-> ;L | lambda

    def p_type_funct(self,p):
        """
        type_funct : INT_TYPE
                   | FLOAT_TYPE
                   | BOOL_TYPE
                   | ID
        """

    #TODO NO SE SI VA
    def p_arg_funct(self,p):
        """
        arg_funct : type_funct ID extra another
        """
    def p_extra(self,p):
        """
        extra : COMMA ID extra
                |
        """
    def p_another(self,p):
        """
        another : SEMICOLON arg_funct
                |
        """

    def p_block_funct(self, p):
        """
        block_funct : LBRACE statement_list funct_ret RBRACE
        """

    def p_funct_ret(self, p):
        """
        funct_ret : RETURN ID newlines
        """
    def p_newlines(self, p):
        """
        newlines : NEWLINE
                 |
        """
    
    # ------------------------------------------------------------------
    # Estructura if/else
    #
    # if <expresion> : (bloque)  [ else (bloque) ]
    #
    # Este es un ejemplo muy simplificado, asumiendo que el
    # parser reconoce : y un bloque luego (no implementado aquí).
    # ------------------------------------------------------------------
    # TODO: SI HAY UN NEWLINE ANTES DEL ELSE, NO DEBERÍA SER UN ERROR Y ESO TODAVÍA NO SE CONTEMPLA
    def p_if_statement(self, p):
        """
        if_statement : IF expression COLON block else
        """
        if len(p) == 5:
            # if sin else
            p[0] = ("if", p[2], p[4], None)
        else:
            # if con else (p[5] corresponde a newlines, y p[8] es el bloque después de ELSE)
            p[0] = ("if_else", p[2], p[4], p[5])

    def p_else(self, p):
        """
        else  : NEWLINE ELSE COLON block
                | NEWLINE
        """
        p[0] = ("else", p[4]) if len(p) == 5 else None
    # Bucle while
    #
    # while <expr> : (bloque)
    def p_while_statement(self, p):
        """
        while_statement : WHILE expression COLON block
        """
        p[0] = ("while", p[2], p[4])

    # Un ejemplo de bloque con llaves.
    # SI USÁRAMOS INDENTACIÓN, AQUÍ CAMBIARÍA TODA LA LÓGICA
    def p_block(self, p):
        """
        block : LBRACE statement_list RBRACE
        """
        p[0] = ("block", p[2])

    # ------------------------------------------------------------------
    # Expresiones
    #
    # Usamos la precedencia definida arriba para las expresiones
    # aritméticas y lógicas. Definimos las reglas de forma resumida.
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



    def p_expression_id(self, p):
        """
        expression : ID
        """
        p[0] = ("id", p[1])

    # ------------------------------------------------------------------
    # Manejo de errores sintácticos
    # ------------------------------------------------------------------
    def p_error(self, p):
        if p:
            print(f"Syntax error at token {p.type} (value: {p.value}) en la línea {getattr(p, 'lineno', 'UNKNOWN')}")
        else:
            print("Syntax error at EOF")

    def build(self, **kwargs):
        """
        Construye el parser con ply.yacc, usando las reglas definidas.
        """
        self.parser = yacc.yacc(module=self, **kwargs)

    def parse(self):
        """
        Realiza el análisis sintáctico (parse) sobre el 'input_data'
        y retorna el árbol resultante (o None si hay error).
        """
        if not self.parser:
            self.build()

        with open(self.route, 'r') as file:
            input_data = file.read()

        return self.parser.parse(input_data, lexer=self.lexer.lexer)
