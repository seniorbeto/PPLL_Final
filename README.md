# Entrega Final – Procesadores del Lenguaje

## Autores

| Nombre                    | NIA       | Correo                                                        | Titulación             |
| ------------------------- | --------- | ------------------------------------------------------------- | ---------------------- |
| **Alberto Penas Díaz**    | 100471939 | [100471939@alumnos.uc3m.es](mailto:100471939@alumnos.uc3m.es) | Ingeniería Informática |
| **Héctor Álvarez Marcos** | 100495794 | [100495794@alumnos.uc3m.es](mailto:100495794@alumnos.uc3m.es) | Ingeniería Informática |

---

## Índice

1. [Introducción](#introducción)
2. [Corrección de Errores](#corrección-de-errores)

   1. [Análisis Léxico](#análisis-léxico)
   2. [Análisis Sintáctico](#análisis-sintáctico)
3. [Gramática Final](#gramática-final)
4. [Decisiones de Diseño](#decisiones-de-diseño)
5. [Pruebas](#pruebas)
6. [Contenido Extra](#contenido-extra)

   1. [Scope de funciones (variables locales)](#scope-de-funciones-variables-locales)
   2. [Recuperación de errores](#recuperación-de-errores)
   3. [Preprocesado del fichero](#preprocesado-del-fichero)
7. [Conclusiones](#conclusiones)

---

## Introducción

Esta memoria describe el desarrollo completo del **ejercicio final** de la asignatura *Procesadores del Lenguaje*. Se exponen las fases de implementación y las mejoras realizadas sobre entregas anteriores. El objetivo principal ha sido construir un compilador funcional que integre correctamente el análisis léxico, sintáctico y semántico, cumpliendo con los requisitos del enunciado.

Además, se incorporan mejoras destinadas a aumentar la robustez y el mantenimiento del sistema, entre ellas:

* detección y recuperación de errores más exhaustiva,
* reducción sustancial de la complejidad gramatical,
* sistema de **preprocesado** previo al análisis léxico.

En los apartados siguientes se detallan las decisiones tomadas, la gramática final, el enfoque semántico y los mecanismos de gestión de ámbito y errores. También se recogen funcionalidades adicionales que, sin ser obligatorias, añaden valor al proyecto.

---

## Corrección de Errores

Hemos solucionado numerosos problemas detectados en la segunda entrega para evitar arrastrarlos a la versión final.

### Análisis Léxico

* La extensión original `.vip` ya **no se reemplaza** por `.token`; ahora se anexa al nombre del fichero.
* Se reconocen números en **notación científica**.
* Los ceros no significativos se tokenizan individualmente; por ejemplo, `00001,3` genera cuatro tokens `INT(0)` y un token `FLOAT(1,3)`.
* Se unifica la categoría de enteros (`INT`) para valores en base 2, 8, 10 y 16.
* Corrección del reconocimiento de **caracteres individuales**: sólo se permiten valores ASCII extendidos.

### Análisis Sintáctico

* Se ha simplificado la gramática (ver apartado [Gramática Final](#gramática-final)).
* Se impide la declaración de **funciones dentro de funciones** y de **tipos dentro de tipos**.

---

## Gramática Final

La gramática se basa en las directrices mostradas en las prácticas, con las correcciones y simplificaciones oportunas. A continuación se presenta la definición formal (BNF abreviada):

```bnf
<program> ::= <statement_list>
           		 | ε

<statement_list> ::= <statement_list> <statement>
                   | <statement>

<statement> ::= <sentence> NEWLINE
              | <type_definition> NEWLINE
              | <function_definition> NEWLINE
              | NEWLINE

<sentence_list> ::= <sentence_list> <sentence> NEWLINE
                 | <sentence> NEWLINE

<sentence> ::= <expression>
             | <assignment>
             | <declaration>
             | <if_statement>
             | <while_statement>

<expression> ::= <expression> PLUS <expression>
               | <expression> MINUS <expression>
               | <expression> TIMES <expression>
               | <expression> DIVIDE <expression>
               | <expression> EQ <expression>
               | <expression> GT <expression>
               | <expression> LT <expression>
               | <expression> GE <expression>
               | <expression> LE <expression>
               | <expression> AND <expression>
               | <expression> OR <expression>
               | NOT <expression>
               | MINUS <expression>
               | PLUS <expression>
               | INT
               | FLOAT
               | CHAR
               | TRUE
               | FALSE
               | ID LPAREN <function_call_argument_list> RPAREN
               | LPAREN <expression> RPAREN
               | ID <reference>

<function_call_argument_list> ::= <expression> COMMA <function_call_argument_list>
                               | <expression>
                               | ε

<reference> ::= LBRACKET <expression> RBRACKET <reference>
             | DOT ID <reference>
             | ε

<assignment> ::= ID <reference> EQUALS <expression>
               | ID <reference> EQUALS <assignment>

<declaration> ::= INT_TYPE <variable_list>
                | FLOAT_TYPE <variable_list>
                | BOOL_TYPE <variable_list>
                | CHAR_TYPE <variable_list>
                | ID <variable_list>

<declaration_list> ::= <declaration_list> <declaration> NEWLINE
                     | <declaration> NEWLINE

<variable_list> ::= <variable_list> COMMA <variable_declaration>
                  | <variable_declaration>

<variable_declaration> ::= ID <assignment_declaration>
                        | LBRACKET <expression> RBRACKET ID

<assignment_declaration> ::= EQUALS <expression>
                          | ε

<if_statement_header> ::= IF <expression> COLON

<if_statement> ::= <if_statement_header> LBRACE NEWLINE <sentence_list> RBRACE
                 | <if_statement_header> LBRACE NEWLINE <sentence_list> RBRACE ELSE COLON LBRACE NEWLINE <sentence_list> RBRACE

<while_header> ::= WHILE <expression> COLON

<while_statement> ::= <while_header> LBRACE NEWLINE <sentence_list> RBRACE

<type_definition> ::= <type_definition_header> <type_definition_body>

<type_definition_header> ::= TYPE ID COLON LBRACE NEWLINE

<type_definition_body> ::= <declaration_list> RBRACE

<function_header> ::= DEF <function_type> ID

<function_header_and_parameters> ::= <function_header> LPAREN <argument_list> RPAREN

<function_before_body> ::= <function_header_and_parameters> COLON LBRACE NEWLINE

<function_definition> ::= <function_before_body> <sentence_function> RETURN <expression> <newlines> RBRACE

<newlines> ::= NEWLINE
             | ε

<sentence_function> ::= <sentence_list>
                     | ε

<function_type> ::= INT_TYPE
                 | FLOAT_TYPE
                 | BOOL_TYPE
                 | CHAR_TYPE
                 | ID

<argument_list> ::= <declaration> SEMICOLON <argument_list>
                 | <declaration>
                 | ε

```

*Para evitar conflictos shift/reduce en la construcción `if/else`, el token `ELSE` debe aparecer en la **misma línea** que el corchete de cierre del bloque `if`.*

Con el fin de mantener la gramática limpia y reutilizable, empleamos reglas comunes —por ejemplo, `declaration`— tanto en atributos de registros como en listas de argumentos. Las restricciones que esto introduce (p.ej., prohibir asignaciones en dichos contextos) se delegan al **análisis semántico**.

---

## Decisiones de Diseño

* **Arquitectura orientada a objetos**: clases para Literales, Llamadas a función, Expresiones binarias/unarias, etc. Todas heredan de `Expression` y comparten el método clave `infer_type`.
* **Promoción implícita de tipos**: valores `char` se convierten a `int` o `float` cuando lo requiere el contexto. Por ejemplo:

  ```vip
  char a = 'A'
  int  b = a + 4   # a → 65
  ```
* Verificación del **tipo de retorno** en funciones. Solo se admite una sentencia `return` por función, cumpliendo la especificación.
* Prohibición de **asignaciones** en declaraciones dentro de registros y firmas de funciones; dichas infracciones se notifican pero no interrumpen el análisis.

---

## Pruebas

Se suministra un script *bash* (`run.sh`) que ejecuta todas las pruebas contenidas en `test_files/input/`. Para cada .vip se generan cuatro artefactos en `test_files/output/`:

| Extensión | Descripción                                          |
| --------- | ---------------------------------------------------- |
| `.token`  | Tokens producidos por el lexer                       |
| `.symbol` | Tabla de símbolos generada por el análisis semántico |
| `.record` | Registros definidos en el programa                   |
| `.error`  | Salida estándar (vacía si no hay errores)            |

El script compara cada salida con la referencia correspondiente en `test_files/expected/`. Se recomienda ejecutar las pruebas en un entorno **Linux** (son las VMs oficiales de la UC3M) para evitar discrepancias.

> **Nota:** la primera ejecución puede fallar si `parsetab.py` y `parser.out` aún no existen, pues su creación emite mensajes en stdout.

---

## Contenido Extra

### Scope de funciones (variables locales)

Se implementó un control de **ámbito** que permite declarar variables locales dentro de una función. Estas variables quedan inaccesibles tras el retorno:

```vip
def int foo(int a):{
    int i
    return 0
}

i = 10  # Error: 'i' fue declarada en un ámbito distinto
```

### Recuperación de errores

El compilador continúa el análisis tras detectar un error léxico, sintáctico o semántico, minimizando el número de abortos prematuros. Los errores léxicos suelen propagar más fallos derivados que los semánticos, al situarse en las primeras fases del pipeline.

### Preprocesado del fichero

Se añadió un **preprocesador** inspirado en C con dos directivas:

* `%append <path>`  – Inserta el contenido de *path*.
* `%supplant <old> <new>` – Reemplaza todas las ocurrencias de `<old>` por `<new>`.

Ejemplo:

```vip
%append foo.vip
%supplant PI 3.141592

Circle c
c.radius = 1
float perimeter = 2 * c.radius * PI
```

Activable con el argumento opcional `allow_preprocess` de `ViperLexer`, genera un archivo `.postprocessed` que se entrega al lexer.

---

## Conclusiones

La práctica ha consolidado los conceptos de compiladores: análisis léxico, sintáctico y semántico, así como el diseño modular y la gestión robusta de errores. Aunque el periodo de entrega coincidió con otras evaluaciones, el resultado es **funcional y coherente** con los objetivos.

Esta experiencia nos ha permitido reforzar tanto la habilidad técnica como la organización en proyectos de software.
