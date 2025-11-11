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
                | assignment_statement
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
                | NOT expression
                | LPAREN expression RPAREN
                | NUMBER_INT
                | NUMBER_FLOAT
                | STRING
                | LITERAL_TRUE
                | LITERAL_FALSE
                | ID
    '''
    if len(p) == 4 and p[2] != '(':
        p[0] = ('binop', p[2], p[1], p[3])
    elif len(p) == 3:
        p[0] = ('unop', p[1], p[2])
    elif len(p) == 4:
        p[0] = p[2]
    else:
        p[0] = ('literal', p[1])

# --- Regla para ciclo 'for' ---
def p_for_statement(p):
    '''
    for_statement   : FOR LPAREN ID IN expression RPAREN LBRACE program RBRACE
    '''
    p[0] = ('for', p[3], p[5], p[8])

# --- Regla para declaraciones de variables ---
def p_variable_declaration(p):
    '''
    variable_declaration : VAR ID EQUALS expression
                         | VAL ID EQUALS expression
                         | VAL ID COLON type EQUALS expression
                         | VAR ID COLON type EQUALS expression
    '''
    if p[1] == 'var':
        p[0] = ('var_decl', p[2], p[4])
    else:
        p[0] = ('val_decl', p[2], p[4])

# BRUNO ROMERO

# --- Regla para 'input' ---
def p_input_statement(p):
    '''
    input_statement : ID EQUALS READLINE LPAREN RPAREN
                    | ID EQUALS READLN LPAREN RPAREN
                    | ID EQUALS READLN_OR_NULL LPAREN RPAREN
    '''
    if p[3] == 'readLine':
        p[0] = ('input_readline', p[1])
    elif p[3] == 'readln':
        p[0] = ('input_readln', p[1])
    else:
        p[0] = ('input_readln_or_null', p[1])

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

# --- Regla para 'print' ---
def p_print_statement(p):
    '''
    print_statement : PRINT LPAREN expression RPAREN
                    | PRINTLN LPAREN expression RPAREN
    '''
    if p[1] == 'print':
        p[0] = ('print', p[3])
    else:
        p[0] = ('println', p[3])

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
    function_declaration : FUN ID LPAREN RPAREN LBRACE program RBRACE
    '''
    p[0] = ('function', p[2], p[6])

# --- Regla para asignaciones ---
def p_assignment(p):
    '''
    assignment  : ID EQUALS expression
    '''
    p[0] = ('assign', p[1], p[3])

# --- Manejo de errores ---
def p_error(p):
    if p:
        print(f"Error sintáctico: Token '{p.value}' en la línea {p.lineno}")

# --- CONSTRUCCIÓN DEL PARSER ---
parser = yacc.yacc()