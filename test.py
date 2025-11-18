from datetime import datetime
import subprocess
import os
from sintactico import parser, lexer

LOG_LEXICO_DIRECTORY = os.path.join("logs", "lexico")
LOG_SINTACTICO_DIRECTORY = os.path.join("logs", "sintactico")
LOG_SEMANTICO_DIRECTORY = os.path.join("logs", "semantico")

def get_git_user():
    result = subprocess.run(['git', 'config', 'user.name'], capture_output=True, text=True)
    return result.stdout.strip()

def get_log_filename(prefix, directory):
    now = datetime.now()
    usuario = get_git_user()
    timestamp = now.strftime("%d-%m-%Y-%Hh%M")
    os.makedirs(directory, exist_ok=True)
    file_name = f"{prefix}-{usuario}-{timestamp}.txt"
    return os.path.join(directory, file_name)

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
    syntax_errors = []

    def custom_error(p):
        msg = f"Error sintáctico: Token '{p.value}' en la línea {p.lineno}" if p else f"Error sintáctico: Fin de archivo inesperado"
        syntax_errors.append(msg)
    
    original_error = getattr(parser, 'errorfunc', None)
    parser.errorfunc = custom_error
    parser.parse(kotlin_code, lexer=lexer)
    parser.errorfunc = original_error

    return syntax_errors

def run_semantic_analysis(kotlin_code):
    from semantico import semantic_errors
    semantic_errors.clear()

    parser.parse(kotlin_code, lexer=lexer)

    return semantic_errors

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
    choice = int(input("Ingrese análisis:\n1. Analizador Léxico\n2. Analizador Sintáctico\n3. Analizador Semántico\n4. Todos\n>> "))
    if choice == 1 or choice == 4:
        # Análisis léxico
        log_filename_lex = get_log_filename("lexico", LOG_LEXICO_DIRECTORY)
        log_entries_lex = run_lexer(kotlin_code)
        save_log(log_filename_lex, log_entries_lex)
    if choice == 2 or choice == 4:
        # Análisis sintáctico
        log_filename_syn = get_log_filename("sintactico", LOG_SINTACTICO_DIRECTORY)
        log_entries_syn = run_parser(kotlin_code)
        save_log(log_filename_syn, log_entries_syn)
    if choice == 3 or choice == 4:
        # Analisis semántico
        log_filename_sem = get_log_filename("semantico", LOG_SEMANTICO_DIRECTORY)
        log_entries_sem = run_semantic_analysis(kotlin_code)
        save_log(log_filename_sem, log_entries_sem)

if __name__ == "__main__":
    main()
