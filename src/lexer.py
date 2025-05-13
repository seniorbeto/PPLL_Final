import os
import shlex
import ply.lex as lex


class ViperLexer:
    def __init__(self, route: str, allow_preprocess: bool = False):
        self.allow_preprocess = allow_preprocess
        self.lexer = None
        self.input_file = route

        # Este será el path al que accederá el parser para analizar el
        # el código. Si el preprocesador está activado, esta ruta se cambiará
        # por la del fichero preprocesado para que el parser pueda analizarlo correctamente.
        self.parser_input_file = route

        if route.endswith(".vip"):
            self.output_file = route.replace(".vip", ".token")
        else:
            self.output_file = route + ".token"
        # PEQUEÑA DISTINCION PARA REDIRIGIR LOS .token DE LOS CASOS DE PRUEBA
        if (
            "test_files/valid" in self.output_file
            or "test_files/invalid" in self.output_file
        ):
            if "test_files/valid" in self.output_file:
                self.output_file = self.output_file.replace(
                    "test_files/valid", "test_files/outputs"
                )
            else:
                self.output_file = self.output_file.replace(
                    "test_files/invalid", "test_files/outputs"
                )

    # Palabras reservadas
    reserved = {
        "true": "TRUE",
        "false": "FALSE",
        "int": "INT_TYPE",
        "float": "FLOAT_TYPE",
        "char": "CHAR_TYPE",
        "def": "DEF",
        "return": "RETURN",
        "type": "TYPE",
        "if": "IF",
        "else": "ELSE",
        "and": "AND",
        "or": "OR",
        "not": "NOT",
        "bool": "BOOL_TYPE",
        "while": "WHILE",
    }

    # Lista completa de tokens que maneja el lexer
    tokens = [
        "ID",
        "INT",
        "FLOAT",  # Aquí se incluye la notación científica
        "CHAR",
        "PLUS",
        "MINUS",
        "TIMES",
        "DIVIDE",
        "GT",
        "LT",
        "GE",
        "LE",
        "EQ",
        "EQUALS",
        "LPAREN",
        "RPAREN",
        "LBRACKET",
        "RBRACKET",
        "LBRACE",
        "RBRACE",
        "COMMA",
        "COLON",
        "DOT",
        "SEMICOLON",
        "NEWLINE",
    ] + list(reserved.values())

    # Expresiones regulares para tokens simples
    t_PLUS = r"\+"
    t_MINUS = r"-"
    t_TIMES = r"\*"
    t_DIVIDE = r"/"
    t_GE = r">="
    t_LE = r"<="
    t_EQ = r"=="
    t_GT = r">"
    t_LT = r"<"
    t_EQUALS = r"="
    t_LPAREN = r"\("
    t_RPAREN = r"\)"
    t_LBRACKET = r"\["
    t_RBRACKET = r"\]"
    t_LBRACE = r"\{"
    t_RBRACE = r"\}"
    t_COMMA = r","
    t_COLON = r":"
    t_SEMICOLON = r";"
    t_DOT = r"\."

    # Ignorar espacios y tabulaciones (de momento)
    t_ignore = " \t"

    # Definición para números en coma flotante (incluye notación científica)
    def t_FLOAT(self, t):
        r'(?:[1-9]\d*|0)\.\d+(?:[eE][+-]?\d+)?|\d+[eE][+-]?\d+'
        t.value = float(t.value)
        return t

    def t_INT(self, t):
        r"""
        0x[0-9A-F]+ |
        0b[01]+ |
        0o[0-7]+ |
        [1-9]\d* |
        0
        """
        value = t.value
        if value.startswith("0x"):
            t.value = int(value, 16)
        elif value.startswith("0b"):
            t.value = int(value, 2)
        elif value.startswith("0o"):
            t.value = int(value, 8)
        else:
            t.value = int(value)
        return t

    # Comentarios de una línea
    def t_COMMENT(self, t):
        r"\#.*"
        pass

    def t_MULTICOMMENT(self, token):
        r"\'\'\'(.|\n)*\'\'\'"
        token.lexer.lineno += token.value.count("\n")
        pass

    # Carácter: cualquier símbolo ASCII-extendido delimitado por comillas simples
    def t_CHAR(self, t):
        r"'(?:[\x00-\xff]|\\.)'"
        # ASÍ ES COMO LO TIENE EL PROFE
        # '[\x00-\xff]'
        # Se descartan las comillas simples
        t.value = t.value[1:-1]
        return t

    # Identificadores y palabras reservadas
    def t_ID(self, t):
        r"[A-Za-z_][A-Za-z0-9_]*"
        t.type = self.reserved.get(t.value, "ID")
        return t

    # Manejo de saltos de línea para llevar la cuenta
    def t_NEWLINE(self, token):
        r"\n+"
        token.lexer.lineno += token.value.count("\n")
        token.value = "nl"  # Esto es para poder imprimirlo como "\n" en el archivo de salida .token
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
                content = file.read()

            if self.allow_preprocess:
                # Preprocesamos el contenido
                content = self.preprocess(self.input_file)

                # Actualizamos la ruta del fichero de entrada para el parser
                self.parser_input_file = self.output_file.replace(".token", ".postprocessed")

                # Exportamos un fichero con el contenido preprocesado
                with open(self.output_file.replace(".token", ".postprocessed"), "w") as pre_file:
                    pre_file.write(content)

            self.lexer.input(content)

            # Exportamos los tokens a un archivo
            with open(self.output_file, "w") as file:
                for token in iter(self.lexer.token, None):
                    file.write(f"{token.type} {token.value}\n")

        except FileNotFoundError as e:
            print(f"ERROR: {e}")
            exit(-1)

    def preprocess(self, file_path, visited=None):
        """
        Lee el fichero en file_path, expande %append y aplica %supplant,
        devolviendo el contenido resultante como cadena.
        Evita inclusiones cíclicas usando el conjunto `visited`.
        """
        if visited is None:
            visited = set()

        # Normaliza y detecta ciclos
        file_path = os.path.abspath(file_path)
        if file_path in visited:
            raise ValueError(f"Circular include detectado: {file_path}")
        visited.add(file_path)

        # Lectura de líneas originales
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        replacements = []
        output_lines = []

        for line in lines:
            stripped = line.strip()
            if stripped.startswith('%'):
                parts = shlex.split(stripped)
                cmd = parts[0]

                # %append <ruta>
                if cmd == '%append' and len(parts) == 2:
                    include_path = parts[1]
                    # ruta relativa → absoluta (respecto al directorio del fichero padre)
                    if not os.path.isabs(include_path):
                        include_path = os.path.join(os.path.dirname(file_path), include_path)
                    # recursividad para el fichero incluido, por si hay %appends dentro de %appends
                    included = self.preprocess(include_path, visited)
                    output_lines.append(included)
                    continue

                # %supplant A B
                elif cmd == '%supplant' and len(parts) == 3:
                    old, new = parts[1], parts[2]
                    replacements.append((old, new))
                    continue

            # Si no era directiva, la conservamos
            output_lines.append(line)

        # Ensamblamos el fichero resultante
        content = ''.join(output_lines)
        for old, new in replacements:
            content = content.replace(old, new)

        return content

    def token(self):
        """
        Retorna el siguiente token.
        """
        return self.lexer.token()
