from datetime import datetime
import subprocess
import os
from lexico import lexer, lexical_errors
from sintactico import parser, sintactic_errors
from semantico import analyze_program, semantic_errors

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
    lexical_errors.clear()
    lexer.lineno = 1
    lexer.input(kotlin_code)
    
    tokens = []
    while True:
        tok = lexer.token()
        if not tok:
            break
        tokens.append(str(tok))
    
    return tokens + list(lexical_errors)

def run_parser(kotlin_code):
    sintactic_errors.clear()
    lexer.lineno = 1
    parse_tree = parser.parse(kotlin_code, lexer=lexer)
    
    return list(sintactic_errors)

def run_semantic_analysis(kotlin_code):
    semantic_errors.clear()
    lexer.lineno = 1
    ast = parser.parse(kotlin_code, lexer=lexer)
    
    if ast:
        analyze_program(ast)
    
    return list(semantic_errors)

def save_log(log_filename, log_entries):
    """Guarda las entradas en el archivo de log."""
    try:
        with open(log_filename, 'w', encoding='utf-8') as log_f:
            for entry in log_entries:
                log_f.write(entry + "\n")
        print(f"✅ {len(log_entries)} entradas guardadas en {log_filename}")
    except Exception as e:
        print(f"❌ Error al escribir el archivo de log: {e}")

def main():
    kotlin_code = read_test_file()
    choice = int(input("Ingrese análisis:\n1. Analizador Léxico\n2. Analizador Sintáctico\n3. Analizador Semántico\n4. Todos\n>> "))
    
    if choice == 1 or choice == 4:
        log_filename = get_log_filename("lexico", LOG_LEXICO_DIRECTORY)
        log_entries = run_lexer(kotlin_code)
        save_log(log_filename, log_entries)
    
    if choice == 2 or choice == 4:
        # Solo ejecutar si no hay errores léxicos
        lexical_errors.clear()
        lexer.lineno = 1
        lexer.input(kotlin_code)
        while lexer.token():
            pass
        
        if not lexical_errors:
            log_filename = get_log_filename("sintactico", LOG_SINTACTICO_DIRECTORY)
            log_entries = run_parser(kotlin_code)
            save_log(log_filename, log_entries)
        else:
            print("⚠️  Análisis sintáctico omitido (hay errores léxicos)")
    
    if choice == 3 or choice == 4:
        # Solo ejecutar si no hay errores léxicos ni sintácticos
        lexical_errors.clear()
        lexer.lineno = 1
        lexer.input(kotlin_code)
        while lexer.token():
            pass
        
        if not lexical_errors:
            sintactic_errors.clear()
            lexer.lineno = 1
            parser.parse(kotlin_code, lexer=lexer)
            
            if not sintactic_errors:
                log_filename = get_log_filename("semantico", LOG_SEMANTICO_DIRECTORY)
                log_entries = run_semantic_analysis(kotlin_code)
                save_log(log_filename, log_entries)
            else:
                print("⚠️  Análisis semántico omitido (hay errores sintácticos)")
        else:
            print("⚠️  Análisis semántico omitido (hay errores léxicos)")

if __name__ == "__main__":
    main()
