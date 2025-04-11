#!/bin/bash
RED="\033[31m"
GREEN="\033[32m"
RESET="\033[0m"
mkdir -p temp

echo ""
echo -e "\033[34m
BATERÍA DE PRUEBAS PROCESADORES DE LENGUAJE\033[0m"
echo -e "\033[31m
        PRÁCTICA FINAL 'VIPER'\033[0m"
echo ""
echo "Alberto Penas Díaz | Hector Álvarez Marcos"
echo ""

run_test() {
    local input_file="$1"
    local expected_file="$2"
    local output_file
    output_file="temp/$(basename "$input_file" .vip)_test"

    python3 main.py "$input_file" > "$output_file" 2> /dev/null
    if cmp "$expected_file" "$output_file"; then
        echo -e "Test $(basename "$input_file"): ${GREEN} SUCCESS ${RESET}"
    else
        echo -e "Test $(basename "$input_file"): ${RED} FAIL ${RESET}"
    fi
}

echo ""
echo "TEST VÁLIDOS"
echo ""

run_test ./test_files/valid/v0_empty.vip ./test_files/valid/v0_empty_expected                                           # Fichero vacío
run_test ./test_files/valid/v1_comment.vip ./test_files/valid/v1_comment_expected                                       # Fichero con comentarios
run_test ./test_files/valid/v2_declarations.vip ./test_files/valid/v2_declarations_expected                             # Fichero con declaraciones
run_test ./test_files/valid/v3_assignements.vip ./test_files/valid/v3_assignements_expected                             # Fichero con asignaciones
run_test ./test_files/valid/v4_op_and_assign.vip ./test_files/valid/v4_op_and_assign_expected                           # Fichero con operadores y asignaciones múltiples
run_test ./test_files/valid/v5_vec_assign.vip ./test_files/valid/v5_vec_assign_expected                                 # Fichero con asignaciones a vectores y operadores de registro
run_test ./test_files/valid/v6_flux_control.vip ./test_files/valid/v6_flux_control_expected                             # Fichero con ifs, bucles y registros
run_test ./test_files/valid/v7_functions.vip ./test_files/valid/v7_functions_expected                                   # Fichero con funciones y llamadas a funciones
run_test ./test_files/valid/v8_all.vip ./test_files/valid/v8_all_expected


echo ""
echo "TEST INVÁLIDOS"
echo ""

# Comprobaremos únicamente errores de sintaxis, no léxicos (puesto que son triviales) ni semánticos
run_test ./test_files/invalid/i0_multiple_assignment.vip ./test_files/invalid/i0_multiple_assignment_expected
run_test ./test_files/invalid/i1_decl_and_parenthesis.vip ./test_files/invalid/i1_decl_and_parenthesis_expected
run_test ./test_files/invalid/i2_flux_if.vip ./test_files/invalid/i2_flux_if_expected
run_test ./test_files/invalid/i3_reassign.vip ./test_files/invalid/i3_reassign_expected
run_test ./test_files/invalid/i4_blocks.vip ./test_files/invalid/i4_blocks_expected

#rm -rf temp