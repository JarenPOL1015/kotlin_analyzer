import ply.yacc as yacc
from lexico import tokens, lexer
import semantico as smt

# DAVID SANDOVAL

sintactic_errors = []

# --- PRECEDENCIA DE OPERADORES ---

# Se define de MENOR a MAYOR precedencia.

precedence = (
    ('right', 'EQUALS', 'ADD_ASSIGN', 'SUB_ASSIGN', 'MUL_ASSIGN', 'DIV_ASSIGN', 'MOD_ASSIGN'),
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'EQ', 'NEQ'),
    ('left', 'GT', 'GTE', 'LT', 'LTE'),
    ('left', 'RANGE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MODULO'),
    ('right', 'NOT'),
    ('left', 'DOT', 'AS'),
)

# --- DEFINICIÓN DE LA GRAMÁTICA ---

# ----- Regla Inicial -----

def p_program(p):
    '''
    program : package_declaration import_list statements
            | package_declaration statements
            | import_list statements
            | statements
    '''
    # RETORNA: ('program', package_opt, imports_list, statements_list)
    if len(p) == 4:
        # package + imports + statements
        p[0] = ('program', p[1], p[2], p[3])
    elif len(p) == 3:
        if p[1] and isinstance(p[1], tuple) and p[1][0] == 'package':
            # package + statements (sin imports)
            p[0] = ('program', p[1], [], p[2])
        else:
            # imports + statements (sin package)
            p[0] = ('program', None, p[1], p[2])
    else:
        # solo statements (sin package ni imports)
        p[0] = ('program', None, [], p[1])

def p_package_declaration(p):
    '''
    package_declaration : PACKAGE qualified_name
    '''
    # RETORNA: ('package', nombre_paquete)
    p[0] = ('package', p[2])

def p_qualified_name(p):
    '''
    qualified_name  : qualified_name DOT ID
                    | ID
    '''
    # RETORNA: string con el nombre calificado (ej: 'com.example.app')
    if len(p) == 4:
        p[0] = p[1] + '.' + p[3]
    else:
        p[0] = p[1]

def p_import_list(p):
    '''
    import_list : import_list import_declaration
                | import_declaration
    '''
    # RETORNA: lista de imports
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]

def p_import_declaration(p):
    '''
    import_declaration : IMPORT qualified_name
                       | IMPORT qualified_name DOT TIMES
                       | IMPORT qualified_name AS ID
    '''
    # RETORNA: ('import', nombre_import, alias_opcional)
    if len(p) == 3:
        # import simple: import com.example.Clase
        p[0] = ('import', p[2], None)
    elif len(p) == 5:
        if p[3] == '.':
            # import wildcard: import com.example.*
            p[0] = ('import', p[2] + '.*', None)
        else:
            # import con alias: import com.example.Clase as Alias
            p[0] = ('import', p[2], p[4])

def p_block(p):
    '''
    block   : LBRACE statements RBRACE
    '''
    # RETORNA: lista de sentencias
    p[0] = p[2]

# ----- Regla para Sentencias -----

def p_statements(p):
    '''
    statements  : statements statement
                | empty
    '''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []

def p_statement(p):
    '''
    statement   : assignment_expression
                | variable_declaration
                | function_declaration
                | function_call
                | return_statement
                | if_statement
                | for_statement
                | while_statement
                | print_statement
    '''
    # RETORNA: (tipo_de_sentencia, valores, ...)
    p[0] = p[1]

# --- Regla para la asignación ---

def p_assignment_expression(p):
    '''
    assignment_expression   : ID EQUALS expression
                            | BACKTICK_ID EQUALS expression
                            | ID ADD_ASSIGN expression
                            | BACKTICK_ID ADD_ASSIGN expression
                            | ID SUB_ASSIGN expression
                            | BACKTICK_ID SUB_ASSIGN expression
                            | ID MUL_ASSIGN expression
                            | BACKTICK_ID MUL_ASSIGN expression
                            | ID DIV_ASSIGN expression
                            | BACKTICK_ID DIV_ASSIGN expression
                            | ID MOD_ASSIGN expression
                            | BACKTICK_ID MOD_ASSIGN expression
    '''
    # RETORNA: ('assign', nombre_variable, operador, expresion, lineno)
    p[0] = ('assign', p[1], p[2], p[3], p.lineno(1))

# DAVID SANDOVAL

# --- Regla para sentencias while ---
def p_while_statement(p):
    '''
    while_statement : WHILE LPAREN expression RPAREN block
    '''
    # RETORNA: ('while_statement', condicion, cuerpo)
    condition = p[3]
    body = p[5]
    p[0] = ('while_statement', condition, body)

# --- Manejo de errores ---
def p_error(p):
    if p:
        sintactic_errors.append(f"Error sintáctico: Token '{p.value}' en la línea {p.lineno}")
        parser.errok()
    else:
        sintactic_errors.append(f"Error sintáctico: Fin de archivo inesperado")

# --- Vacío ---
def p_empty(p):
    '''
    empty :
    '''
    p[0] = None

# --- CONSTRUCCIÓN DEL PARSER ---
parser = yacc.yacc(debug=True)

def build_parse_tree(code, lexer):
    global sintactic_errors
    sintactic_errors = []
    lexer.lineno = 1
    lexer.input(code)

    try:
        result = parser.parse(lexer=lexer)
    except Exception as e:
        sintactic_errors.append(f"Error crítico durante el parsing: {str(e)}")
        result = None
    
    if result is None and not sintactic_errors:
        sintactic_errors.append("Error sintáctico: El código no pudo ser parseado correctamente")
    
    return result


if __name__ == "__main__":
    last_length = len(smt.semantic_errors)
    while True:
        try:
            s = input('kt-parser > ')
        except EOFError:
            print("\nSaliendo...")
            break

        if not s: continue
        lexer.input(s)
        result = parser.parse(lexer=lexer)

        if result:
            print(result)
        
        # Imprimir nuevos errores semánticos
        if len(smt.semantic_errors) > last_length:
            print("\n".join(smt.semantic_errors[last_length:]))
            last_length = len(smt.semantic_errors)