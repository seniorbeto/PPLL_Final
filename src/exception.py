class SemanticError(Exception):

    @staticmethod
    def print_sem_error( type_error, args):
        if type_error == "Function Declaration Error":
            print("SEMANTIC ERROR DETECTED IN FUNCTION ATRIBUTES DEFINITION:")
            print(f"\tYou cannot assign a value to a function atribute type.")
            print(f"\tVariables Affected: {', '.join(var.name for var in args[1])}")
            print(f"\tFunction declaration affected: {args[0]}")
            print("")

        if type_error == "Function Declaration Type Atribute Error":
            print("SEMANTIC ERROR DETECTED IN FUNCTION ATRIBUTES TYPE DEFINITION:")
            print(f"\t DATATYPE {args[1]} is not defined for variables:")
            print(f"\t\t-{"\n\t\t-".join(var.name for var in args[2])}")
            print(f"\t Function affected: {args[0]}")
            print("")
        if type_error == "Function Type Declaration Error":
            print("SEMANTIC ERROR DETECTED IN FUNCTION TYPE DEFINITION:")
            print(f"\t DATATYPE {args[1]} is not defined")
            print(f"\t Function affected: {args[0]}")
            print("")

        if type_error == "Type Variable Declaration Error Function":
            print("SEMANTIC ERROR DETECTED IN FUNCTION VARIABLE DEFINITION:")
            print(f"\tDATATYPE {args[0]} is not defined for variable: {args[1]}")
            print(f"\tFunction affected: {args[2]}")
            print("")

        if type_error == "Type Declaration Error":
            print("SEMANTIC ERROR DETECTED IN TYPE DECLARATION:")
            print(f"\tYou cannot assign a value to a record type.")
            print(f"\tRecords Affected: {', '.join(var.name for var in args)}")
            print("")

        if type_error == "Incompatible Types":
            print("SEMANTIC ERROR DETECTED IN DECLARATION AND ASSIGNEMENT:")
            print(f"\tIncompatible types: {args[0].upper() if args[0] != None else "NONETYPE"} and {args[1].upper() if args[1] != None else "NONETYPE"}")
            print(f"\tVariables Affected: {', '.join(var.name for var in args[2])}")
            print("")

        if type_error == "Incompatible Types Func":
            print("SEMANTIC ERROR DETECTED IN DECLARATION AND ASSIGNEMENT INSIDE FUNCTION:")
            print(f"\tIncompatible types: {args[0].upper() if args[0] != None else "NONETYPE"} and {args[1].upper() if args[1] != None else "NONETYPE"}")
            print(f"\tVariables Affected: {', '.join(var.name for var in args[2])}")
            print(f"\tFunction Affected: {args[3]}")
            print("")

        if type_error == "Incompatible Types Func Ret":
            print("SEMANTIC ERROR DETECTED IN RETURN STATEMENT:")
            print(f"\tIncompatible types: {args[0].upper()} and {args[1].upper()}")
            print(f"\tFunction Affected: {args[2]}")
            print("")

        if type_error == "Incompatible Types Assignment":
            if args[1] is None:
                print("\tDETECTED IN ASSIGNMENT")
                print(f"\tVariable affected: {args[2]}")
                print("")
            else:
                print("SEMANTIC ERROR DETECTED IN ASSIGNMENT:")
                print(f"\tIncompatible types: {args[0].upper() if args[0] != None else "NONETYPE"} and {args[1].upper() if args[1] != None else "NONETYPE"}")
                print(f"\tVariable affected: {args[2]}")
                print("")
        if type_error == "Incompatible Types Assignment Function":
            print("SEMANTIC ERROR DETECTED IN ASSIGNMENT INSIDE FUNCTION:")
            print(f"\tIncompatible types: {args[0].upper() if args[0] != None else "NONETYPE"} and {args[1].upper() if args[1] != None else "NONETYPE"}")
            print(f"\tVariable affected: {args[2]}")
            print(f"\tFunction Affected: {args[3]}")
            print("")

        if type_error == "Declaration Error":
            print("SEMANTIC ERROR DETECTED IN DECLARATION:")
            print(f"\tRecord {args[0]} not found.")
            print(f"\tVariables Affected: {', '.join(var.name for var in args[1])}")
            print("")
        if type_error == "Variable not found":
            print("SEMANTIC ERROR DETECTED IN ASSIGNMENT:")
            print(f"\tVariable '{args}' not found or out of scope")
            print("")

        if type_error == "Variable not found Function":
            print("SEMANTIC ERROR DETECTED IN ASSIGNMENT:")
            print(f"\tVariable '{args[0]}' not found or out of scope")
            print(f"\tFunction Affected: {args[1]}")
            print("")

        if type_error == "Type Error Not defined":
            print("SEMANTIC ERROR DETECTED IN ASSIGNMENT:")
            print(f"\tInvalid assignment to variable '{args[0]}'. Attribute: {args[1]} is not defined")
            print("")
        if type_error =="Incompatible Operands":
            print("SEMANTIC ERROR DETECTED IN OPERATOR EXPRESSION:")
            print(f"\tIncompatible operands: {args[1].value} and {args[2].value} for operator {args[0]}")
            print("")
        if type_error == "Redefinition of Variable":
            print("SEMANTIC ERROR DETECTED IN FUNCTION BODY->REDECLARATION OF VARIABLE:")
            print(f"\tVariable {args[0]} is already declared in this scope")
            print(f"\tFunction Affected: {args[1]}")
            print("")

        if type_error == "Type Redefinition Error":
            print("SEMANTIC ERROR DETECTED IN TYPE DECLARATION:")
            print(f"\ttype '{args[0]}' is already defined")
            print("")
        if type_error == "Redeclaration of Type Attr":
            print("SEMANTIC ERROR DETECTED IN TYPE DECLARATION:")
            print(f"\ttype '{args[1]}' already has an attribute '{args[0]}'")
            print("")

        if type_error == "Attribute of type":
            print("SEMANTIC ERROR DETECTED IN TYPE REFERENCE:")
            print(f"\ttype '{args[0]}' OBJECT has no attribute '{args[1]}'")
            print("")

        if type_error == "No Vector Error":
            print("SEMANTIC ERROR DETECTED IN VECTOR REFERENCE:")
            print(f"\tAttribute '{args[0]}' is not a vector")
            print(f"\tVariable affected: {args[1]}")
            print("")

        if type_error == "Vector length error":
            print("SEMANTIC ERROR DETECTED IN VECTOR LENGTH:")
            print(f"\tCannot assign type {args[1]} to vector length")
            print(f"\tVariable affected: {args[0]}")
            print("")

        if type_error == "No Vector DEC Error":
            print("SEMANTIC ERROR DETECTED IN VECTOR DEC:")
            print(f"\tMissing index for vector {args[0]}")
            print(f"\tVariable affected: {args[1]}")
            print("")