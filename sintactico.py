import ply.yacc as yacc
from lexico import tokens, lexer

# DAVID SANDOVAL

# --- PRECEDENCIA DE OPERADORES ---

# Se define de MENOR a MAYOR precedencia.

precedence = (
    ('right', 'ELSE'),
    ('right', 'EQUALS', 'ADD_ASSIGN', 'SUB_ASSIGN', 'MUL_ASSIGN', 'DIV_ASSIGN', 'MOD_ASSIGN'),
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'TO'),
    ('left', 'EQ', 'NEQ'),
    ('left', 'GT', 'GTE', 'LT', 'LTE'),
    ('left', 'RANGE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MODULO'),
    ('right', 'NOT'),
    ('left', 'INC', 'DEC'),
    ('left', 'DOT', 'SAFE_CALL'),
)

# --- DEFINICIÓN DE LA GRAMÁTICA ---

# ----- Regla Inicial -----

def p_program(p):
    '''
    program : program statement
            | statement
    '''
    if len(p) == 2:
        p[0] = ('program', [p[1]])
    else:
        p[0] = ('program', p[1][1] + [p[2]])

# ----- Regla para Sentencias -----

def p_statement(p):
    '''
    statement   : expression
                | for_statement
                | variable_declaration
                | if_statement
                | function_declaration
                | return_statement
                | while_statement
                | class_declaration
    '''
    p[0] = p[1]

# --- Regla para expresiones ---
def p_expression(p):
    '''
    expression  : expression PLUS expression
                | expression MINUS expression
                | expression TIMES expression
                | expression DIVIDE expression
                | expression MODULO expression
                | expression RANGE expression
                | expression EQ expression
                | expression NEQ expression
                | expression GT expression
                | expression GTE expression
                | expression LT expression
                | expression LTE expression
                | expression AND expression
                | expression OR expression
                | expression TO expression
                | NOT expression
                | LPAREN expression RPAREN
                | NUMBER_INT
                | NUMBER_FLOAT
                | STRING
                | LITERAL_TRUE
                | LITERAL_FALSE
                | ID
                | function_call
                | assignment_expression
    '''
    if len(p) == 4 and p[2] != '(':
        p[0] = ('binop', p[2], p[1], p[3])
    elif len(p) == 3:
        p[0] = ('unop', p[1], p[2])
    elif len(p) == 4 and p[1] == '(':
        p[0] = p[2]  # LPAREN expression RPAREN -> devuelve solo la expresión
    elif len(p) == 2:
        if isinstance(p[1], tuple):
            p[0] = p[1] 
        else:
            p[0] = ('literal', p[1])

# --- Regla para ciclo 'for' ---
def p_for_statement(p):
    '''
    for_statement   : FOR LPAREN ID IN expression RPAREN LBRACE program RBRACE
    '''
    p[0] = ('for', p[3], p[5], p[8])

def p_return_statement(p):
    '''
    return_statement : RETURN expression
                     | RETURN
    '''
    if len(p) == 3:
        p[0] = ('return', p[2])
    else:
        p[0] = ('return', None)

# --- Regla para declaraciones de variables ---
def p_variable_declaration(p):
    '''
    variable_declaration : VAR ID EQUALS expression
                         | VAL ID EQUALS expression
                         | VAR ID COLON type EQUALS expression
                         | VAL ID COLON type EQUALS expression
                         | VAR ID COLON type
                         | VAL ID COLON type
    '''
    if len(p) == 5 and p[3] == ':':
        # Declaración sin inicialización
        if p[1] == 'var':
            p[0] = ('var_decl_no_init', p[2], p[4])
        else:
            p[0] = ('val_decl_no_init', p[2], p[4])
    else:
        # Declaración con inicialización
        if p[1] == 'var':
            p[0] = ('var_decl', p[2], p[4] if len(p) == 5 else p[6])
        else:
            p[0] = ('val_decl', p[2], p[4] if len(p) == 5 else p[6])

# BRUNO ROMERO

# --- Regla para ciclo 'while' ---
def p_while_statement(p):
    '''
    while_statement : WHILE LPAREN expression RPAREN LBRACE program RBRACE
    '''
    p[0] = ('while', p[3], p[6])

# --- Regla para clases ---
def p_class_declaration(p):
    '''
    class_declaration : CLASS ID LBRACE program RBRACE
    '''
    p[0] = ('class', p[2], p[4])

# JAREN PAZMIÑO

# --- Regla para 'if' ---
def p_if_statement(p):
    '''
    if_statement    : IF LPAREN expression RPAREN LBRACE program RBRACE ELSE LBRACE program RBRACE
                    | IF LPAREN expression RPAREN LBRACE program RBRACE
    '''
    if len(p) == 12:
        p[0] = ('if_else', p[3], p[6], p[10])
    else:
        p[0] = ('if', p[3], p[6])


# --- Regla para funciones ---
def p_function_declaration(p):
    '''
    function_declaration : FUN ID LPAREN params RPAREN LBRACE program RBRACE
                         | FUN ID LPAREN RPAREN LBRACE program RBRACE
                         | FUN ID LPAREN params RPAREN COLON type LBRACE program RBRACE
                         | FUN ID LPAREN RPAREN LBRACE COLON type program RBRACE
    '''
    if len(p) == 9:
        p[0] = ('function_decl', p[2], p[4], None, p[7])
    elif len(p) == 10:
        p[0] = ('function_decl', p[2], [], None, p[7])
    elif len(p) == 11:
        p[0] = ('function_decl', p[2], p[4], p[8], p[10])
    else:
        p[0] = ('function_decl', p[2], [], p[8], p[10])

def p_params(p):
    '''
    params : param COMMA params
           | param
           | empty
    '''
    if len(p) == 4:
        p[0] = [p[1]] + p[3]
    elif len(p) == 2 and p[1] != []:
        p[0] = [p[1]]
    else:
        p[0] = []

def p_param(p):
    '''
    param : ID COLON type
    '''
    p[0] = ('param', p[1], p[3])

def p_function_call(p):
    '''
    function_call : ID LPAREN args RPAREN
                  | READLINE LPAREN args RPAREN
                  | READLN LPAREN args RPAREN
                  | READLN_OR_NULL LPAREN args RPAREN
                  | PRINT LPAREN args RPAREN
                  | PRINTLN LPAREN args RPAREN
    '''
    p[0] = ('function_call', p[1], p[3])

def p_args(p):
    '''
    args : args COMMA arg
         | arg
    '''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    elif len(p) == 2 and p[1] is not None:
        p[0] = [p[1]]
    else:
        p[0] = []

def p_arg(p):
    '''
    arg : expression
        | empty
    '''
    p[0] = p[1]

# --- Regla para asignaciones ---
def p_assignment_expression(p):
    '''
    assignment_expression : ID EQUALS expression
    '''
    p[0] = ('assign', p[1], p[3])

# --- Regla para tipos de datos ---
def p_type(p):
    '''
    type : TYPE_INT
         | TYPE_STRING
         | TYPE_BOOLEAN
         | TYPE_FLOAT
         | TYPE_ANY
         | TYPE_UNIT
         | TYPE_LIST
         | TYPE_SET
         | TYPE_MAP
         | generic_type
    '''
    if p[1] in ('Int', 'String', 'Boolean', 'Float', 'Any', 'Unit'):
        p[0] = ('basic_type', p[1])
    else:
        p[0] = p[1]

def p_generic_type(p):
    '''
    generic_type : TYPE_LIST LT type GT
                 | TYPE_SET LT type GT
                 | TYPE_MAP LT type COMMA type GT
    '''
    if p[1] == 'List':
        p[0] = ('list_type', p[3])
    elif p[1] == 'Set':
        p[0] = ('set_type', p[3])
    else:
        p[0] = ('map_type', p[3], p[5])

# --- Manejo de errores ---
def p_error(p):
    if p:
        print(f"Error sintáctico: Token '{p.value}' en la línea {p.lineno}")

# --- Vacío ---
def p_empty(p):
    '''
    empty :
    '''
    p[0] = []

# --- CONSTRUCCIÓN DEL PARSER ---
parser = yacc.yacc()

if __name__ == "__main__":
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