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
        self.symbol_table._scope = "statement" if not self.symbol_table._scope.__contains__(
            "FUNCTION") else self.symbol_table._scope
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
        p[0] = UnaryExpr(p[1], p[2])

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
        func_name = p[1]
        func_params = p[3]
        func_call = FunctionCall(func_name, func_params)


        if self.symbol_table._scope.startswith("FUNCTIONBODY"):
            func_scope_name = self.symbol_table._scope.split("-")[1]
            function_scope = self.symbol_table.lookup_function(func_scope_name)
            list_variables = SymbolTable()
            for var2 in function_scope.body + function_scope.parameters:
                list_variables.add_variable(var2)

            if func_name not in self.symbol_table._functions.keys():
                SemanticError.print_sem_error("Function not found FUNC", [func_name, func_scope_name])
                func_call.datatype = None
                p[0] = func_call
                return None

            function = self.symbol_table._functions[func_name]
            if len(func_params) != len(function.parameters):
                SemanticError.print_sem_error("Function parameters mismatch FUNC", [func_name, func_params, function.parameters, func_scope_name])
                func_call.datatype = None
                p[0] = func_call
                return None

            for parameter_to_pass, original_parameters in zip(func_params, function.parameters):
                if not list_variables.exists_variable(parameter_to_pass.name):
                    SemanticError.print_sem_error("Variable not found Function", [parameter_to_pass.name, func_scope_name])
                    func_call.datatype = None
                    p[0] = func_call
                    return None
                if parameter_to_pass.datatype != original_parameters.datatype:
                    SemanticError.print_sem_error("Function error parameter FUNC",
                                                  [parameter_to_pass, original_parameters, func_name, func_scope_name])
            print(f"POR QUE FALLAS")
            func_call.datatype = function.return_type
            func_call.value = function.return_type
            p[0] = func_call
            return None

        else:
            if func_name not in self.symbol_table._functions.keys():
                SemanticError.print_sem_error("Function not found", [func_name])
                func_call.datatype = None
                p[0] = func_call
                return None

            function = self.symbol_table._functions[func_name]
            if len(func_params) != len(function.parameters):
                SemanticError.print_sem_error("Function parameters mismatch", [func_name, func_params, function.parameters])
                func_call.datatype = None
                p[0] = func_call
                return None

            for parameter_to_pass, original_parameters in zip(func_params, function.parameters):
                if not self.symbol_table.exists_variable(parameter_to_pass.name):
                    SemanticError.print_sem_error("Variable not found", parameter_to_pass.name)
                    func_call.datatype = None
                    p[0] = func_call
                    return None
                if parameter_to_pass.datatype != original_parameters.datatype:
                    SemanticError.print_sem_error("Function error parameter",
                                                  [parameter_to_pass, original_parameters, func_name])

            func_call.datatype = function.return_type
            p[0] = func_call
            return None

    def p_function_call_argument_list(self, p):
        """
        function_call_argument_list : expression COMMA function_call_argument_list
                                    | expression
                                    |
        """
        if len(p) == 4:
            p[0] = [p[1]] + [p[3]]
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
        identifier, ref_chain = p[1], p[2]

        if self.symbol_table._scope.startswith("FUNCTIONBODY"):
            func_name = self.symbol_table._scope.split("-")[1]
            func = self.symbol_table.lookup_function(func_name)

            local_tbl = SymbolTable()
            for v in func.parameters + func.body:
                local_tbl.add_variable(v)

            var = local_tbl.lookup_variable(identifier)
            if var is None:
                SemanticError.print_sem_error(
                    "Variable not found Function", [identifier, func_name]
                )
                var = Variable(identifier, None, None)
        else:
            var = self.symbol_table.lookup_variable(identifier)
            if var is None:
                SemanticError.print_sem_error("Variable not found", identifier)
                var = Variable(identifier, None, None)

        counter = 0
        for kind, payload in ref_chain:

            if kind == "field":
                if isinstance(var, Vector) and counter == len(ref_chain) - 1:
                    SemanticError.print_sem_error(
                        "No Vector DEC Error", [var.value, var.name]
                    )
                    var.datatype = None
                    break

                if (var.datatype not in self.record_table._basic_symbols and
                        not self.record_table.exists(var.datatype)):
                    SemanticError.print_sem_error(
                        "Type Error Not defined", [identifier, var.datatype]
                    )

                if (var.datatype in self.record_table._basic_symbols or
                        payload not in [f.name for f in self.record_table._table[var.datatype]]):
                    SemanticError.print_sem_error(
                        "Attribute of type", [var.datatype, payload]
                    )
                    var = Variable(identifier, None, payload)
                else:
                    field_obj = next(
                        f for f in self.record_table._table[var.datatype]
                        if f.name == payload
                    )
                    if isinstance(field_obj, Vector):
                        var = Vector(identifier, field_obj.datatype,
                                     field_obj.length, payload)
                    else:
                        var = Variable(identifier, field_obj.datatype, payload)
                counter += 1

            else:
                if (var.datatype not in self.record_table._basic_symbols and
                        not self.record_table.exists(var.datatype)):
                    SemanticError.print_sem_error(
                        "Type Error Not defined", [identifier, var.datatype]
                    )

                if not isinstance(var, Vector):
                    SemanticError.print_sem_error(
                        "No Vector Error", [var.value, var.name]
                    )

                idx_type = payload.infer_type(
                    self.symbol_table if not self.symbol_table._scope.startswith("FUNCTIONBODY")
                    else local_tbl,
                    self.record_table
                )
                if idx_type not in ("int", "char"):
                    SemanticError.print_sem_error(
                        "Vector length error", [identifier, idx_type]
                    )
                    var.datatype = None
                    break

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
        reference_value = p[2]
        value = p[4]
        if not self.symbol_table._scope.__contains__("FUNCTIONBODY"):
            if reference_value == []:
                var = self.symbol_table.lookup_variable(identifier)
                if var is None:
                    SemanticError.print_sem_error("Variable not found", identifier)

                else:
                    if isinstance(value, VariableRef) and self.record_table.exists(value.datatype) == False:
                        # SI ES UNA REFERENCIA QUE NO ESTA EN LA TABLA DE REGISTROS NO ES NADA, ERROR SEMANTICO
                        SemanticError.print_sem_error("Type Error Not defined", [identifier, value])
                    else:
                        #COMPROBACION DE DATATYPE == VALOR ASIGNADO
                        actual_type = value.infer_type(self.symbol_table, self.record_table) if not isinstance(value, Variable) else value.datatype
                        if var.datatype != actual_type:
                            SemanticError.print_sem_error(
                                "Incompatible Types Assignment",
                                [var.datatype, actual_type, identifier, self.symbol_table, self.record_table]
                            )
                            var.datatype = None
                            p[0] = var
                            return None
            else:
                var = self.symbol_table.lookup_variable(identifier)
                counter = 0
                for key, attr in reference_value:
                    if key == 'field':
                        if isinstance(var, Vector) and counter == len(reference_value) -1:
                            SemanticError.print_sem_error("No Vector DEC Error", [var.value, var.name])
                            var.datatype = None
                            p[0] = var
                            return None

                        if var is None:
                            SemanticError.print_sem_error("Variable not found", identifier)
                        if (var.datatype not in self.record_table._basic_symbols
                            and self.record_table.exists(var.datatype) == False):
                            SemanticError.print_sem_error("Type Error Not defined", [identifier, var.datatype])
                        else:
                            if var.datatype in self.record_table._basic_symbols or attr not in [atribute.name for atribute in  self.record_table._table[var.datatype]]:
                                SemanticError.print_sem_error("Attribute of type", [var.datatype, attr])
                                var = Variable(identifier, None, attr)
                            else:
                                x = [atribute.datatype for atribute in self.record_table._table[var.datatype] if atribute.name == attr]
                                check_if_vector = [atribute for atribute in self.record_table._table[var.datatype] if atribute.name == attr]
                                if isinstance(check_if_vector[0], Vector):
                                    var = Vector(identifier, x[0], check_if_vector[0].length, attr)
                                    counter += 1
                                    if counter == len(reference_value) -1:
                                        SemanticError.print_sem_error("No Vector DEC Error", [attr, var.name])
                                        var.datatype = None
                                        p[0] = var
                                        return None
                                else:
                                    var = Variable(identifier, x[0] , attr)
                                    counter += 1
                    else:
                        #INDICE DE VECTOR
                        if var is None:
                            SemanticError.print_sem_error("Variable not found", identifier)
                        if (var.datatype not in self.record_table._basic_symbols
                            and self.record_table.exists(var.datatype) == False):
                            SemanticError.print_sem_error("Type Error Not defined", [identifier, var.datatype])

                        #SI intentas indicar un indice de una variable que no es vector te devuelve fallo
                        if not isinstance(var, Vector):
                            SemanticError.print_sem_error("No Vector Error", [var.value, var.name])
                        if attr.infer_type(self.symbol_table, self.record_table) not in  ("int", "char"):
                            SemanticError.print_sem_error("Vector length error",
                                                          [identifier, attr.infer_type(self.symbol_table, self.record_table)])
                            var.datatype = None
                            p[0] = var
                            return None
                        else:
                            pass

                actual_type = value.infer_type(self.symbol_table, self.record_table) if not isinstance(value, Variable) else value.datatype
                if var.datatype != actual_type and var.datatype not in ("int", "float") and actual_type not in ("char"):
                    SemanticError.print_sem_error("Incompatible Types Assignment",
                                      [var.datatype, actual_type, identifier, self.symbol_table, self.record_table])
                    var.datatype = None
                p[0] = var
                return None
        else:
            func_name = self.symbol_table._scope.split("-")[1]
            function = self.symbol_table.lookup_function(func_name)
            list_variables = SymbolTable()
            for var2 in function.body + function.parameters:
                list_variables.add_variable(var2)
            var = list_variables.lookup_variable(identifier)

            if reference_value == []:

                if var is None:
                    SemanticError.print_sem_error("Variable not found", identifier)

                else:
                    if isinstance(value, VariableRef) and self.record_table.exists(value.datatype) == False:
                        # SI ES UNA REFERENCIA QUE NO ESTA EN LA TABLA DE REGISTROS NO ES NADA, ERROR SEMANTICO
                        SemanticError.print_sem_error("Type Error Not defined", [identifier, value])
                    else:
                        #COMPROBACION DE DATATYPE == VALOR ASIGNADO
                        actual_type = value.infer_type(list_variables, self.record_table) if not isinstance(value, Variable) else value.datatype
                        if var.datatype != actual_type:
                            SemanticError.print_sem_error(
                                "Incompatible Types Assignment",
                                [var.datatype, actual_type, identifier, list_variables, self.record_table]
                            )
                            var.datatype = None
                            p[0] = var
                            return None
            else:
                counter = 0
                for key, attr in reference_value:
                    if key == 'field':
                        if isinstance(var, Vector) and counter == len(reference_value) -1:
                            SemanticError.print_sem_error("No Vector DEC Error", [var.value, var.name])
                            var.datatype = None
                            p[0] = var
                            return None

                        if var is None:
                            SemanticError.print_sem_error("Variable not found", identifier)
                        if (var.datatype not in self.record_table._basic_symbols
                            and self.record_table.exists(var.datatype) == False):
                            SemanticError.print_sem_error("Type Error Not defined", [identifier, var.datatype])
                        else:
                            if var.datatype in self.record_table._basic_symbols or attr not in [atribute.name for atribute in  self.record_table._table[var.datatype]]:
                                SemanticError.print_sem_error("Attribute of type", [var.datatype, attr])
                                var = Variable(identifier, None, attr)
                            else:
                                x = [atribute.datatype for atribute in self.record_table._table[var.datatype] if atribute.name == attr]
                                check_if_vector = [atribute for atribute in self.record_table._table[var.datatype] if atribute.name == attr]
                                if isinstance(check_if_vector[0], Vector):
                                    var = Vector(identifier, x[0], check_if_vector[0].length, attr)
                                    counter += 1
                                    if counter == len(reference_value) -1:
                                        SemanticError.print_sem_error("No Vector DEC Error", [attr, var.name])
                                        var.datatype = None
                                        p[0] = var
                                        return None
                                else:
                                    var = Variable(identifier, x[0] , attr)
                                    counter += 1
                    else:
                        #INDICE DE VECTOR
                        if var is None:
                            SemanticError.print_sem_error("Variable not found", identifier)
                        if (var.datatype not in self.record_table._basic_symbols
                            and self.record_table.exists(var.datatype) == False):
                            SemanticError.print_sem_error("Type Error Not defined", [identifier, var.datatype])

                        #SI intentas indicar un indice de una variable que no es vector te devuelve fallo
                        if not isinstance(var, Vector):
                            SemanticError.print_sem_error("No Vector Error", [var.value, var.name])
                        if attr.infer_type(list_variables, self.record_table) not in  ("int", "char"):
                            SemanticError.print_sem_error("Vector length error",
                                                          [identifier, attr.infer_type(list_variables, self.record_table)])
                            var.datatype = None
                            p[0] = var
                            return None
                        else:
                            pass

                actual_type = value.infer_type(list_variables, self.record_table) if not isinstance(value, Variable) else value.datatype
                if var.datatype != actual_type and var.datatype not in ("int", "float") and actual_type not in ("char"):
                    SemanticError.print_sem_error("Incompatible Types Assignment",
                                      [var.datatype, actual_type, identifier,list_variables, self.record_table])
                    var.datatype = None
                p[0] = var
                return None
        p[0] = var


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

            if self.symbol_table._scope == "Type Definition":
                #SI ESTAS EN UNA DECLARACION DE TIPO
                SemanticError.print_sem_error("Type Declaration Error", variables)

            if self.symbol_table._scope.__contains__("FUNCTIONDECL"):
                SemanticError.print_sem_error("Function Declaration Error",
                                              [self.symbol_table._scope.split("-")[1], variables])

            if self.symbol_table._scope.__contains__("FUNCTIONBODY"):
                #DENTRO DEL CUERPO DE UNA FUNCION
                func_name = self.symbol_table._scope.split("-")[1]
                function = self.symbol_table.lookup_function(func_name)
                # MIRO TODAS LAS VARIABLES
                for var in variables:
                    if var.name in [f.name for f in function.parameters] or var.name in [f.name for f in function.body]:
                        SemanticError.print_sem_error("Redefinition of Variable",
                                                      [var.name, func_name])
                    else:
                        # COMO ES SIN ASIGNACION, SIMPLEMENTE SE AÑADE A LA LISTA DEL BODY SI COINCIDEN EN TIPO
                        local_var_table = SymbolTable()
                        for var2 in function.parameters + function.body:
                            local_var_table.add_variable(var2)
                        type = variables[-1].value.infer_type(local_var_table, self.record_table)

                        if datatype != type:
                            SemanticError.print_sem_error("Incompatible Types Func",
                                                          [datatype, type, variables, func_name])
                        else:
                            var.datatype = datatype
                            var.value = type
                            function.body.append(var)

                self.symbol_table._functions[func_name].body = function.body
                p[0] = variables
                return None

            type = variables[-1].value.infer_type(self.symbol_table, self.record_table)

            if type != datatype and type != SemanticError:
                SemanticError.print_sem_error("Incompatible Types",
                                              [datatype, type, variables])
                p[0] = variables
                return None
            else:
                for var in variables:
                    var.datatype = datatype
                    var.value = type
                    self.symbol_table.add_variable(var) if (self.symbol_table._scope == "statement" and
                                                            not self.symbol_table.exists_variable(var.name)) else None
        else:
            if self.symbol_table._scope.__contains__("FUNCTIONBODY"):
                #DECLARACION SIN ASIGNACION DENTRO DEL CUERPO DE UNA FUNCION
                func_name = self.symbol_table._scope.split("-")[1]
                function = self.symbol_table.lookup_function(func_name)
                #MIRO TODAS LAS VARIABLES
                for var in variables:
                    if var.name in [f.name for f in function.parameters] or var.name in [f.name for f in function.body]:
                        SemanticError.print_sem_error("Redefinition of Variable",
                                                      [var.name, func_name])
                    else:
                        #COMO ES SIN ASIGNACION, SIMPLEMENTE SE AÑADE A LA LISTA DEL BODY SI EL TIPO ES CORRECTO
                        var.datatype = datatype if (datatype in self.record_table._basic_symbols
                                                    or self.record_table.exists(datatype) != False) else None
                        if var.datatype == None:
                            SemanticError.print_sem_error("Type Variable Declaration Error Function",
                                                          [datatype, var.name, func_name])
                        self.symbol_table._functions[func_name].body.append(var)

                p[0] = variables
                return None
            #Hay que verificar que el tipo declarado sea correcto, pese a que el valor sea nulo
            if datatype not in self.record_table._basic_symbols and self.record_table.exists(datatype) == False:

                if self.symbol_table._scope.__contains__("FUNCTIONDECL"):
                    SemanticError.print_sem_error("Function Declaration Type Atribute Error",
                                                  [self.symbol_table._scope.split("-")[1], datatype, variables])
                    p[0] = variables
                    return None
                else:
                    SemanticError.print_sem_error("Declaration Error", [datatype, variables])
                    p[0] = variables
                    return None
            else:
                for var in variables:
                    var.datatype = datatype
                    self.symbol_table.add_variable(var) if (self.symbol_table._scope == "statement" and
                                                            not self.symbol_table.exists_variable(var.name)) else None
        p[0] = variables


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
            prev, new = p[1], p[3]

            vec_len = next(
                (v.length for v in prev if isinstance(v, Vector)),
                None
            )
            if vec_len and isinstance(new, Variable):
                new = Vector(new.name, None, vec_len, new.value)

            p[0] = prev + [new]
        else:
            # p[0] = [p[1]]
            p[0] = [p[1]]

    def p_variable_declaration(self, p):
        """
        variable_declaration : ID assignment_declaration
                             | LBRACKET expression RBRACKET ID
        """
        if len(p) == 3:
            name = p[1]
            init = p[2]
            #p[0] = (name, init)
            p[0] = Variable(name, None, init)
        else:
            size = p[2]
            name = p[4]
            p[0] = Vector(name, None, size, None)
            if p[0].length == None:
                SemanticError.print_sem_error("Vector length error", [name, size])
            p[0].datatype = None
            return p[0]

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
        # Tenemos que comprobar que la expresión del if sea de tipo booleano
        p[2].infer_type()
        if len(p) == 8:
            p[0] = ("if", p[2], p[6])
        else:
            p[0] = ("if_else", p[2], p[6], p[12])

    def p_while_statement(self, p):
        """
        while_statement : WHILE expression COLON LBRACE NEWLINE sentence_list RBRACE
        """
        p[0] = ("while", p[2], p[6])

    def p_type_definition(self, p):
        """
        type_definition : type_definition_header type_definition_body
        """

        type_name = p[1]

        fields_declared = p[2]

        #Lista contenedora de los atributos del tipo declarado. Solo se guardaran si cada atributo tiene un tipo correcto
        fields = []

        #Contador para luego comprobar que todos los atributos que se han pasado se hayan guardado.
        #En caso de no coincidir con la longitud de FIELDS no se guardará el tipo en la tabla de registros
        number_of_attr = 0
        for field in fields_declared:
            #DE MOMENTO EL ELEMENTO VARIABLE O LO QUE COÑO SEA ESTÄ EN FIELD[2][0] TODO BORRAR COMENTAARIO
            for elems in field:
                number_of_attr += 1
                if elems.datatype != None and elems.name not in [field.name for field in fields]:
                    fields.append(elems)
                else:
                    if not elems.datatype == None:
                        SemanticError.print_sem_error("Redeclaration of Type Attr", [elems.name, type_name])
        #Solo se guarda si todos los elementos de fields declared se han guardado en fields, esto quiere decir
        # QUE TODOS LOS ATRIBUTOS DECLARADOS SON CORRECTOS
        self.record_table.add_record(type_name, fields) if len(fields) == number_of_attr else None
        p[0] = ("type_definition", p[2])

    #FUNCION QUE PERMITE CAMBIAR EL SCOPE A TYPE_DEFINITION
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

    def p_function_header(self, p):
        """
        function_header : DEF function_type ID
        """
        self.symbol_table._scope = f"FUNCTIONDECL-{p[3]}"
        p[0] = ("function_header", p[2], p[3])

    def p_function_header_and_parameters(self, p):
        """
        function_header_and_parameters : function_header LPAREN argument_list RPAREN
        """
        p[0] = ("header_and_p", p[1], p[3])

    def p_function_before_body(self, p):
        """
        function_before_body : function_header_and_parameters COLON LBRACE NEWLINE
        """
        type_funct = p[1][1][1]
        name_funct = p[1][1][2]
        arg_list = p[1][2]
        if type_funct not in self.record_table._basic_symbols and self.record_table.exists(type_funct) == False:
            SemanticError.print_sem_error("Function Type Declaration Error", [name_funct, type_funct])
            new_function = Function(name_funct, None, arg_list, "NoneType")
        else:
            new_function = Function(name_funct, type_funct, arg_list, type_funct)
        self.symbol_table.add_function(new_function)
        self.symbol_table._scope = f"FUNCTIONBODY-{name_funct}"

    def p_function_definition(self, p):
        """
        function_definition : function_before_body sentence_function RETURN expression newlines RBRACE
        """
        return_statement = p[4]

        funct_name = self.symbol_table._scope.split("-")[1]
        function = self.symbol_table.lookup_function(funct_name)
        local_var_table = SymbolTable()
        for var in function.body + function.parameters:
            local_var_table.add_variable(var)

        result = return_statement.infer_type(local_var_table, self.record_table) if return_statement != None else None
        if result == None:
            result = "NoneType"
        if result.upper() != function.return_type.upper():
            SemanticError.print_sem_error("Incompatible Types Func Ret",
                                          [function.return_type, result, funct_name])

        self.symbol_table._scope = ""
        #p[0] = ("function_definition", function_type, function_name,argument_list, p[5], p[7])"""

    def p_newlines(self, p):
        """
        newlines : NEWLINE
                |
        """

    def p_sentence_function(self, p):
        """
        sentence_function : sentence_list
                          |
        """
        p[0] = p[1] if len(p) > 1 else []

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
            p[0] = [var for var in p[1]] + p[3]
        elif len(p) == 2:
            p[0] = p[1]
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

        if not input_data.startswith("\n"):
            input_data = "\n" + input_data

        result = self.parser.parse(input_data, lexer=self.lexer.lexer)

        # Exportamos las tablas
        with open(f"{self.route.replace(".postprocessed", "").replace(".vip", "")}.symbol", "w") as file:
            for symbol in self.symbol_table._variables:
                file.write(f"{symbol}:{self.symbol_table._variables[symbol]}\n")

        with open(f"{self.route.replace(".postprocessed", "").replace(".vip", "")}.record", "w") as file:
            for symbol in self.record_table._table:
                file.write(f"{symbol} => {self.record_table._table[symbol]}\n")

        return result
