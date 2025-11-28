import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lexico import lexical_errors, lexer
from sintactico import parser, sintactic_errors
from semantico import analyze_program, semantic_errors

def analyze_code(code):
    result = {
        'tokens': [],
        'lex_errors': [],
        'sintactic_errors': [],
        'semantic_errors': [],
        'parse_tree': None,
        'semantic_ok': False
    }
    
    if not code or not code.strip():
        return result

    # Análisis Léxico
    lexical_errors.clear()
    lexer.lineno = 1  # Reiniciar contador de líneas
    lexer.input(code)
    
    while True:
        tok = lexer.token()
        if not tok:
            break
        result['tokens'].append(f"{tok.type}: {tok.value}")
    
    result['lex_errors'] = list(lexical_errors)

    # Análisis Sintáctico (solo si no hay errores léxicos)
    if not result['lex_errors']:
        sintactic_errors.clear()
        lexer.lineno = 1  # Reiniciar para el parser
        parse_tree = parser.parse(code, lexer=lexer)
        result['parse_tree'] = parse_tree
        result['sintactic_errors'] = list(sintactic_errors)
    
        # Análisis Semántico (solo si no hay errores sintácticos)
        if parse_tree and not result['sintactic_errors']:
            semantic_errors.clear()
            analyze_program(parse_tree)
            result['semantic_errors'] = list(semantic_errors)
            result['semantic_ok'] = len(semantic_errors) == 0
        else:
            result['semantic_ok'] = False
    else:
        result['semantic_ok'] = False

    return result

