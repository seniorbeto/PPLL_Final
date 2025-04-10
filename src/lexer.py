import ply.lex as lex

class ViperLexer:
    def __init__(self, route: str):
        self.lexer = None
        self.input_file = route
        self.output_file = route.replace(".vip", ".token")

    # Palabras reservadas
    reserved = {
        'true': 'TRUE',
        'false': 'FALSE',
        'int': 'INT_TYPE',
        'float': 'FLOAT_TYPE',
        'char': 'CHAR_TYPE',
        'def': 'DEF',
        'return': 'RETURN',
        'type': 'TYPE',
        'if': 'IF',
        'else': 'ELSE',
        'and': 'AND',
        'or': 'OR',
        'not': 'NOT',
        'bool': 'BOOL_TYPE',
        'while': 'WHILE'
    }

    # Lista completa de tokens que maneja el lexer
    tokens = [
                 'ID',
                 'DECIMAL',
                 'BINARY',
                 'OCTAL',
                 'HEXADECIMAL',
                 'FLOAT_CONST', # Aquí se incluye la notación científica
                 'CHAR_CONST',
                 'PLUS', 'MINUS', 'TIMES', 'DIVIDE',
                 'GT', 'LT', 'GE', 'LE', 'EQ',
                 'EQUALS',
                 'LPAREN', 'RPAREN',
                 'LBRACKET', 'RBRACKET',
                 'LBRACE', 'RBRACE',
                 'COMMA', 'COLON', 'DOT', 'SEMICOLON',
                'COMMENT', 'MLCOMMENT',
                'NEWLINE'
             ] + list(reserved.values())

    # Expresiones regulares para tokens simples
    t_PLUS       = r'\+'
    t_MINUS      = r'-'
    t_TIMES      = r'\*'
    t_DIVIDE     = r'/'
    t_GE         = r'>='
    t_LE         = r'<='
    t_EQ         = r'=='
    t_GT         = r'>'
    t_LT         = r'<'
    t_EQUALS     = r'='
    t_LPAREN     = r'\('
    t_RPAREN     = r'\)'
    t_LBRACKET   = r'\['
    t_RBRACKET   = r'\]'
    t_LBRACE     = r'\{'
    t_RBRACE     = r'\}'
    t_COMMA      = r','
    t_COLON      = r':'
    t_SEMICOLON  = r';'
    t_DOT        = r'\.'

    # Ignorar espacios y tabulaciones (de momento)
    t_ignore = ' \t'

    # Definición para números en coma flotante (incluye notación científica)
    def t_FLOAT_CONST(self, t):
        r'\d+\.\d+([e][+-]?\d+)?|\d+[e][+-]?\d+'
        t.value = float(t.value)
        return t

    # Hexadecimal: 0x con letras mayúsculas
    def t_HEXADECIMAL(self, t):
        r'0x[0-9A-F]+'
        t.value = int(t.value, 16)
        return t

    # Binario: 0b
    def t_BINARY(self, t):
        r'0b[01]+'
        t.value = int(t.value, 2)
        return t

    # Octal: 0o
    def t_OCTAL(self, t):
        r'0o[0-7]+'
        t.value = int(t.value, 8)
        return t

    # Decimal
    def t_DECIMAL(self, t):
        r'\d+'
        t.value = int(t.value)
        return t

    # Comentarios de una línea
    def t_COMMENT(self, t):
        r'\#.*'
        pass

    def t_MULTICOMMENT(self, token):
        r'\'\'\'(.|\n)*\'\'\''
        token.lexer.lineno += token.value.count('\n')
        pass

    # Carácter: cualquier símbolo ASCII-extendido delimitado por comillas simples
    def t_CHAR_CONST(self, t):
        r'\'([^\\\n]|(\\.))?\''
        # Se descartan las comillas simples
        t.value = t.value[1:-1]
        return t

    # Identificadores y palabras reservadas
    def t_ID(self, t):
        r'[A-Za-z_][A-Za-z0-9_]*'
        t.type = self.reserved.get(t.value, 'ID')
        return t

    # Manejo de saltos de línea para llevar la cuenta
    def t_NEWLINE(self, token):
        r'\n+'
        token.lexer.lineno += token.value.count("\n")
        token.value = "nl" # Esto es para poder imprimirlo como "\n" en el archivo de salida .token
        return token

    # Manejo de errores léxicos
    def t_error(self, t):
        print(f"Caracter ilegal '{t.value[0]}' en la línea {t.lineno}")
        t.lexer.skip(1)

    # Método para construir el lexer
    def build(self, **kwargs):
        """
        Construye el lexer con la configuración de PLY.
        """
        self.lexer = lex.lex(module=self, **kwargs)

    def run(self) -> None:
        if self.lexer is None:
            print("ERROR: build the lexer first.")
            return None

        try:
            with open(self.input_file, "r") as file:
                self.lexer.input(file.read())

            # Exportamos los tokens a un archivo
            with open(self.output_file, "w") as file:
                for token in iter(self.lexer.token, None):
                    file.write(f"{token.type} {token.value}\n")

        except FileNotFoundError as e:
            print(f"ERROR: {e}")
            exit(-1)

    def token(self):
        """
        Retorna el siguiente token.
        """
        return self.lexer.token()
