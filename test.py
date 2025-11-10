from datetime import datetime
import subprocess
import os
from sintactico import parser, lexer

LOG_DIRECTORY = "logs"

def get_git_user():
    result = subprocess.run(['git', 'config', 'user.name'], capture_output=True, text=True)
    return result.stdout.strip()

def get_log_filename(prefix):
    now = datetime.now()
    usuario = get_git_user()
    timestamp = now.strftime("%d-%m-%Y-%Hh%M")
    os.makedirs(LOG_DIRECTORY, exist_ok=True)
    file_name = f"{prefix}-{usuario}-{timestamp}.txt"
    return os.path.join(LOG_DIRECTORY, file_name)

def read_test_file():
    test_file_path = input("Nombre del archivo de prueba: ")
    try:
        with open(test_file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: El archivo de prueba '{test_file_path}' no se encontró.")
        print("Por favor, crea ese archivo con tu código de prueba de Kotlin.")
        exit()

def run_lexer(kotlin_code):
    lexer.log_entries = []
    lexer.input(kotlin_code)
    while True:
        tok = lexer.token()
        if not tok:
            break
        lexer.log_entries.append(str(tok))
    return lexer.log_entries

def run_parser(kotlin_code):
    parser.log_entries = []
    result = parser.parse(kotlin_code, lexer=lexer)
    parser.log_entries.append(str(result))
    return parser.log_entries

def save_log(log_filename, log_entries):
    """Guarda los tokens en el archivo de log."""
    try:
        with open(log_filename, 'w', encoding='utf-8') as log_f:
            for entry in log_entries:
                log_f.write(entry + "\n")
        print(f"Se han guardado {len(log_entries)} entradas en {log_filename}")
    except Exception as e:
        print(f"Error al escribir el archivo de log: {e}")

def main():
    kotlin_code = read_test_file()
    # Análisis léxico
    log_filename_lex = get_log_filename("lexico")
    log_entries_lex = run_lexer(kotlin_code)
    save_log(log_filename_lex, log_entries_lex)

    # Análisis sintáctico
    log_filename_syn = get_log_filename("sintactico")
    log_entries_syn = run_parser(kotlin_code)
    save_log(log_filename_syn, log_entries_syn)

if __name__ == "__main__":
    main()
