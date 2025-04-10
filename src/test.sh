#!/bin/bash

RED="\033[31m"
GREEN="\033[32m"
RESET="\033[0m"

mkdir -p temp

echo ""
echo -e "\033[34m
BATERÍA DE PRUEBAS PROCESADORES DE LENGUAJE\033[0m"
echo "Alberto Penas Díaz | Hector Álvarez Marcos"
echo ""


run_test() {
    local input_file="$1"
    local expected_file="$2"
    local output_file
    output_file="temp/$(basename "$input_file")"

    python3 main.py "$input_file" > "$output_file"
    if cmp -s "$expected_file" "$output_file"; then
        echo -e "Test $(basename "$input_file"): ${GREEN} SUCCESS ${RESET}"
    else
        echo -e "Test $(basename "$input_file"): ${RED} FAIL ${RESET}"
    fi
}

echo ""
echo "TEST VÁLIDOS"
echo ""

run_test input/valid_declarations input/expected_01
run_test input/valid_assignments input/expected_01
run_test input/valid_assignments input/expected_01
run_test input/valid_all.vip input/expected_all

echo ""
echo "TEST INVÁLIDOS"
echo ""

run_test test_files/invalid_01 test_files/expected_inv_01
run_test test_files/invalid_02 test_files/expected_inv_02
run_test test_files/invalid_03 test_files/expected_inv_03

rm -rf temp