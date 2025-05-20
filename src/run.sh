#!/bin/bash
RED="\033[31m"
GREEN="\033[32m"
RESET="\033[0m"
BLUE="\033[34m"

mkdir -p output

echo ""
echo -e "${BLUE}BATERÍA DE PRUEBAS PROCESADORES DE LENGUAJE${RESET}"
echo -e "${RED}        PRÁCTICA FINAL 'VIPER'${RESET}"
echo ""
echo "Alberto Penas Díaz | Hector Álvarez Marcos"
echo ""

run_test() {
    local input_file="$1"
    local base_name
    base_name=$(basename "$input_file" .vip)

    # Ficheros de salida
    local output_token="test_files/output/${base_name}.token"
    local output_symbol="test_files/output/${base_name}.symbol"
    local output_record="test_files/output/${base_name}.record"
    local output_error="test_files/output/${base_name}.error"

    # Ficheros esperados
    local expected_token="test_files/expected/${base_name}.token"
    local expected_symbol="test_files/expected/${base_name}.symbol"
    local expected_record="test_files/expected/${base_name}.record"

    # Ejecutar el compilador y redirigir la salida estándar de error
    python3 main.py "$input_file" > "$output_error" 2>&1

    for ext in token symbol record; do
        src="test_files/input/${base_name}.${ext}"
        dst="test_files/output/${base_name}.${ext}"
        [ -f "$src" ] && mv "$src" "$dst"
    done

    # Comparar los ficheros generados con los esperados
    for ext in token symbol record; do
        local expected_file="test_files/expected/${base_name}.${ext}"
        local output_file="test_files/output/${base_name}.${ext}"
        if cmp -s "$expected_file" "$output_file"; then
            echo -e "Test $base_name ($ext): ${GREEN}SUCCESS${RESET}"
        else
            echo -e "Test $base_name ($ext): ${RED}FAIL${RESET}"
        fi
    done

    # Comprobar que el .error está vacío si no ha habido errores
    if [ -s "$output_error" ]; then
        echo -e "Test $base_name (error): ${RED}FAIL${RESET}"
    else
        echo -e "Test $base_name (error): ${GREEN}SUCCESS${RESET}"
    fi

    echo ""
}

echo ""
echo "EJECUTANDO TESTS"
echo ""

for input_file in test_files/input/*.vip; do
    run_test "$input_file"
done
