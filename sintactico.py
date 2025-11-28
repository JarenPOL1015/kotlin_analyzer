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

# JAREN PAZMIÑO

# --- Regla para declaraciones de variables ---

def p_variable_declaration(p):
    '''
    variable_declaration    : VAR ID COLON type EQUALS expression
                            | VAR BACKTICK_ID COLON type EQUALS expression
                            | VAL ID COLON type EQUALS expression
                            | VAL BACKTICK_ID COLON type EQUALS expression
                            | VAR ID COLON type
                            | VAR BACKTICK_ID COLON type
                            | VAL ID COLON type
                            | VAL BACKTICK_ID COLON type
                            | VAR ID EQUALS expression
                            | VAR BACKTICK_ID EQUALS expression
                            | VAL ID EQUALS expression
                            | VAL BACKTICK_ID EQUALS expression
    '''
    # RETORNA: (tipo_declaracion, tipo_variable, nombre_variable, expresion)
    decl_type = 'var_decl' if p[1] == 'var' else 'val_decl'
    var_name = p[2]
    var_type = None
    expr = None
    lineno = p.lineno(1)

    if len(p) == 7:
        var_type = p[4]
        expr = p[6]
    elif len(p) == 5:
        if p[3] == ':':
            var_type = p[4]
        else:
            expr = p[4]
    
    p[0] = (decl_type, var_type, var_name, expr, lineno)

# --- Regla para tipos de datos ---
def p_type(p):
    '''
    type    : TYPE_INT
            | TYPE_LONG
            | TYPE_FLOAT
            | TYPE_DOUBLE
            | TYPE_STRING
            | TYPE_BOOLEAN
            | TYPE_ANY
            | TYPE_UNIT
            | TYPE_LIST
            | TYPE_SET
            | TYPE_MAP
            | dynamic_type
    '''
    # RETORNA: tipo (Ej: 'Int', 'Boolean', 'Hola')
    p[0] = p[1]

def p_dynamic_type(p):
    '''
    dynamic_type    : ID
    '''
    # RETORNA: tipo dinámico como ID
    p[0] = p[1]

# --- Regla para declaraciones de funciones ---

def p_function_declaration(p):
    '''
    function_declaration    : FUN ID LPAREN params RPAREN block
                            | FUN BACKTICK_ID LPAREN params RPAREN block
                            | FUN ID LPAREN params RPAREN EQUALS expression
                            | FUN BACKTICK_ID LPAREN params RPAREN EQUALS expression
                            | FUN ID LPAREN params RPAREN COLON type block
                            | FUN BACKTICK_ID LPAREN params RPAREN COLON type block
                            | FUN ID LPAREN params RPAREN COLON type EQUALS expression
                            | FUN BACKTICK_ID LPAREN params RPAREN COLON type EQUALS expression
    '''
    # RETORNA: ('fun_decl', nombre_funcion, parametros, tipo_retorno, cuerpo)
    func_name = p[2]
    params = p[4]
    return_type = None
    body = p[len(p)-1]
    lineno = p.lineno(1)

    if len(p) >= 9:
        return_type = p[7]

    p[0] = ('fun_decl', func_name, params, return_type, body, lineno)

def p_return_statement(p):
    '''
    return_statement    : RETURN expression
                        | RETURN
    '''
    # RETORNA: ('return', valores, lineno)
    if len(p) == 3:
        return_type = p[2]
        p[0] = ('return', return_type, p.lineno(1))
    elif len(p) == 2:
        p[0] = ('return', None, p.lineno(1))

def p_params(p):
    '''
    params  : params COMMA param
            | param
            | empty
    '''
    # RETORNA: lista de parámetros
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    elif len(p) == 2:
        if p[1] is None:
            p[0] = []
        else:
            p[0] = [p[1]]

def p_param(p):
    '''
    param   : ID COLON type
            | ID COLON type EQUALS expression
            | BACKTICK_ID COLON type
            | BACKTICK_ID COLON type EQUALS expression
    '''
    # RETORNA: (nombre_parametro, tipo_parametro, valor_por_defecto)
    param_name = p[1]
    param_type = p[3]
    if len(p) == 6:
        default_value = p[5]
        p[0] = (param_name, param_type, default_value)
    else:
        p[0] = (param_name, param_type, None)

# JAREN PAZMIÑO

# --- Regla para sentencias if ---

def p_if_statement(p):
    '''
    if_statement : IF LPAREN expression RPAREN block else_part
    '''
    # RETORNA: ('if_statement', condicion, cuerpo_if, cuerpo_else)
    condition = p[3]
    if_body = p[5]
    else_body = p[6]
    p[0] = ('if_statement', condition, if_body, else_body)

def p_else_part(p):
    '''
    else_part : ELSE if_statement
              | ELSE block
              | empty
    '''
    # RETORNA: ('else_part', cuerpo) o None si no hay else
    if len(p) == 3:
        if isinstance(p[2], tuple) and p[2][0] == 'if_statement':
            p[0] = ('else_if', p[2])
        else:
            p[0] = ('else_part', p[2])
    else:
        p[0] = None

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

# JAREN PAZMIÑO

# --- Regla para funciones de impresión y lectura ---
def p_print_statement(p):
    '''
    print_statement : PRINT LPAREN arguments RPAREN
                    | PRINTLN LPAREN arguments RPAREN
                    | READLINE LPAREN arguments RPAREN
    '''
    # RETORNA: ('print', argumentos) o ('println', argumentos) o ('readLine', argumentos)
    if p[1] == 'print':
        p[0] = ('print', p[3])
    elif p[1] == 'println':
        p[0] = ('println', p[3])
    elif p[1] == 'readLine':
        p[0] = ('readLine', p[3])