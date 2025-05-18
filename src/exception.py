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

        if type_error == "Type Declaration Error":
            print("SEMANTIC ERROR DETECTED IN TYPE DECLARATION:")
            print(f"\tYou cannot assign a value to a record type.")
            print(f"\tRecords Affected: {', '.join(var.name for var in args)}")
            print("")

        if type_error == "Incompatible Types":
            print("SEMANTIC ERROR DETECTED IN DECLARATION AND ASSIGNEMENT:")
            print(f"\tIncompatible types: {args[0].upper()} and {args[1][-1].value.infer_type(args[0], args[1][-1].value).upper()}")
            print(f"\tVariables Affected: {', '.join(var.name for var in args[1])}")
            print("")

        if type_error == "Incompatible Types Assignment":
            if args[1] is None:
                print("\tDETECTED IN ASSIGNMENT:")
                print(f"\tVariable affected: {args[2]}")
                print("")
            else:
                print("SEMANTIC ERROR DETECTED IN ASSIGNMENT:")
                print(f"\tIncompatible types: {args[0].upper()} and {args[1].infer_type(args[1], args[1].value).upper()}")
                print(f"\tVariable affected: {args[2]}")
                print("")

        if type_error == "Declaration Error":
            print("SEMANTIC ERROR DETECTED IN DECLARATION:")
            print(f"\tRecord {args[0]} not found.")
            print(f"\tVariables Affected: {', '.join(var.name for var in args[1])}")
            print("")
        if type_error == "Variable not found":
            print("SEMANTIC ERROR DETECTED IN ASSIGNMENT:")
            print(f"\tVariable {args} not found.")

        if type_error == "Type Error Not defined":
            print("SEMANTIC ERROR DETECTED IN ASSIGNMENT:")
            print(f"\tInvalid assignment to variable '{args[0]}'. Attribute: {args[1]} is not defined")

        if type_error =="Incompatible Operands":
            print("SEMANTIC ERROR DETECTED IN OPERATOR EXPRESSION:")
            print(f"\tIncompatible operands: {args[1].value} and {args[2].value} for operator {args[0]}")