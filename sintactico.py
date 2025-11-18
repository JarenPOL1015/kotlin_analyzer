import ply.yacc as yacc
from lexico import tokens, lexer
import semantico as smt

# DAVID SANDOVAL

_temp_function_params_stack = []
_temp_function_params = {}
_function_context_stack = []
_function_depth = 0
_temp_variables = {}

# --- POST-PROCESAMIENTO DEL AST PARA FUNCIONES ANIDADAS ---
# REVISAR ESTA SECCIÓN CON CUIDADO (CASI MUERO AQUÍ)
def post_process_nested_functions(ast_node):
    """
    Post-procesa el AST para corregir declaraciones de funciones anidadas.
    Mueve las funciones anidadas de 'global' a sus scopes correctos.
    """
    if not ast_node:
        return
        
    if isinstance(ast_node, (list, tuple)):
        for item in ast_node:
            if isinstance(item, tuple) and len(item) >= 2 and item[0] == 'fun_decl':
                # Encontramos una declaración de función de nivel superior
                process_function_declaration(item, "global")
            else:
                post_process_nested_functions(item)

def process_function_declaration(fun_decl, parent_scope="global"):
    """Procesa una declaración de función para detectar funciones anidadas"""
    if len(fun_decl) < 5:
        return
        
    _, return_type, func_name, params, body = fun_decl[:5]
    
    # El scope de esta función
    current_function_scope = f"{parent_scope}.{func_name}" if parent_scope != "global" else f"global.{func_name}"
    
    # Buscar declaraciones de función anidadas directamente en el cuerpo
    nested_function_decls = find_nested_function_declarations(body)
    
    # Procesar cada función anidada recursivamente
    for nested_decl in nested_function_decls:
        nested_func_name = nested_decl[2]
        
        # Mover la función anidada del scope global al scope de esta función
        move_function_to_scope(nested_func_name, current_function_scope)
        
        # Procesar recursivamente las funciones anidadas dentro de esta función anidada
        process_function_declaration(nested_decl, current_function_scope)

def find_nested_function_declarations(body):
    """Encuentra declaraciones de función anidadas directamente en un cuerpo de función"""
    nested_declarations = []
    
    if isinstance(body, (list, tuple)):
        # Si body es una tupla de (statements, return_statement) del function_body
        if len(body) == 2 and isinstance(body[0], list):
            statements = body[0]
            # Buscar declaraciones de función en las statements
            for stmt in statements:
                if isinstance(stmt, tuple) and len(stmt) >= 3 and stmt[0] == 'fun_decl':
                    nested_declarations.append(stmt)
                elif isinstance(stmt, (list, tuple)):
                    # Buscar recursivamente en estructuras anidadas
                    nested_declarations.extend(find_nested_function_declarations(stmt))
            
            # También buscar en el return statement si es necesario
            return_stmt = body[1]
            if isinstance(return_stmt, (list, tuple)):
                nested_declarations.extend(find_nested_function_declarations(return_stmt))
        else:
            # Procesamiento normal para listas o tuplas simples
            for item in body:
                if isinstance(item, tuple) and len(item) >= 3 and item[0] == 'fun_decl':
                    # Esta es una declaración de función anidada
                    nested_declarations.append(item)
                elif isinstance(item, (list, tuple)):
                    # Buscar recursivamente en estructuras de control, etc.
                    nested_declarations.extend(find_nested_function_declarations(item))
    
    return nested_declarations

def find_nested_functions(body):
    """Encuentra todas las funciones anidadas en un cuerpo de función (solo nombres)"""
    nested_functions = []
    
    if isinstance(body, (list, tuple)):
        for item in body:
            if isinstance(item, tuple) and len(item) >= 2 and item[0] == 'fun_decl':
                # Esta es una función anidada
                func_name = item[2]
                nested_functions.append(func_name)
            elif isinstance(item, (list, tuple)):
                # Buscar recursivamente
                nested_functions.extend(find_nested_functions(item))
    
    return nested_functions

def move_function_to_scope(func_name, target_scope):
    """Mueve una función del scope global al scope objetivo"""
    # Verificar que la función existe en global
    if 'global' in smt.scopes and func_name in smt.scopes['global']['functions']:
        func_info = smt.scopes['global']['functions'][func_name]
        
        # Crear el scope objetivo si no existe
        if target_scope not in smt.scopes:
            # Determinar el scope padre
            scope_parts = target_scope.split('.')
            if len(scope_parts) > 1:
                parent_scope = '.'.join(scope_parts[:-1])
            else:
                parent_scope = 'global'
                
            smt.scopes[target_scope] = {
                'variables': {},
                'constants': {},  
                'functions': {},
                'parent': parent_scope
            }
        
        # Mover la función
        smt.scopes[target_scope]['functions'][func_name] = func_info
        
        # Eliminar del scope global
        del smt.scopes['global']['functions'][func_name]
        
        # Mover también el scope propio de la función si existe
        old_function_scope = f'global.{func_name}'
        new_function_scope = f'{target_scope}.{func_name}'
        
        if old_function_scope in smt.scopes:
            # Mover el contenido del scope de la función
            smt.scopes[new_function_scope] = smt.scopes[old_function_scope].copy()
            # Actualizar el parent del scope movido
            smt.scopes[new_function_scope]['parent'] = target_scope
            # Eliminar el scope antiguo
            del smt.scopes[old_function_scope]
            
            # También mover cualquier scope anidado de esta función
            move_nested_scopes(old_function_scope, new_function_scope)

def move_nested_scopes(old_base_scope, new_base_scope):
    """Mueve recursivamente todos los scopes que empiecen con old_base_scope"""
    scopes_to_move = []
    
    # Encontrar todos los scopes que empiecen con old_base_scope
    for scope_name in smt.scopes.keys():
        if scope_name.startswith(old_base_scope + '.'):
            scopes_to_move.append(scope_name)
    
    # Mover cada scope encontrado
    for old_scope in scopes_to_move:
        # Calcular el nuevo nombre del scope
        relative_path = old_scope[len(old_base_scope):]  # obtener la parte después de old_base_scope
        new_scope = new_base_scope + relative_path
        
        # Mover el scope
        smt.scopes[new_scope] = smt.scopes[old_scope].copy()
        
        # Actualizar el parent si es necesario
        old_parent = smt.scopes[new_scope]['parent']
        if old_parent.startswith(old_base_scope):
            # Actualizar el parent al nuevo esquema de nombres
            new_parent = new_base_scope + old_parent[len(old_base_scope):]
            smt.scopes[new_scope]['parent'] = new_parent
        
        # Eliminar el scope antiguo
        del smt.scopes[old_scope]

# --- PRECEDENCIA DE OPERADORES ---

# Lista de operadores binarios.

arithmetic_bin_ops = ['+', '-', '*', '/', '%']
logical_bin_ops = ['&&', '||']
relational_bin_ops = ['==', '!=', '>', '>=', '<', '<=']
range_bin_ops = ['..']

# Se define de MENOR a MAYOR precedencia.

precedence = (
    ('right', 'ELSE'),
    ('right', 'EQUALS', 'ADD_ASSIGN', 'SUB_ASSIGN', 'MUL_ASSIGN', 'DIV_ASSIGN', 'MOD_ASSIGN'),
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'EQ', 'NEQ'),
    ('left', 'GT', 'GTE', 'LT', 'LTE'),
    ('left', 'RANGE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MODULO'),
    ('right', 'NOT'),
    ('left', 'INC', 'DEC'),
    ('left', 'DOT', 'SAFE_CALL', 'AS'),
)

# --- DEFINICIÓN DE LA GRAMÁTICA ---

# ----- Regla Inicial -----

def p_program(p):
    '''
    program : top_level_list
    '''
    p[0] = p[1]
    
    # Post-procesar el AST para corregir las declaraciones de funciones anidadas
    post_process_nested_functions(p[0])
    
    import pprint
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(smt.scopes)

    print(smt.scopes)


def p_top_level_list(p):
    '''
    top_level_list  : top_level_list top_level
                    | top_level
    '''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]

def p_top_level(p):
    '''
    top_level   : variable_declaration
                | function_declaration
                | assignment_expression
    '''
                # | package_declaration
                # | import_declaration
    p[0] = p[1]

def p_block(p):
    '''
    block   : LBRACE statements RBRACE
    '''
    p.slice[0].type = p.slice[2].type
    p[0] = p[2]

# ----- Regla para Sentencias -----
def p_statements(p):
    '''
    statements   : statements statement
                 | statement
    '''
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = [p[1]]

def p_statement(p):
    '''
    statement   : variable_declaration
                | assignment_expression
                | function_declaration
    '''
                # | if_statement
                # | while_statement
                # | for_statement
    p[0] = p[1]

# --- Regla para declaraciones de variables ---
def p_variable_declaration(p):
    '''
    variable_declaration    : VAR ID COLON type EQUALS expression
                            | VAL ID COLON type EQUALS expression
                            | VAR ID COLON type
                            | VAL ID COLON type
                            | VAR ID EQUALS expression
                            | VAL ID EQUALS expression
    '''
    is_constant = (p[1] == 'val')
    var_name = p[2]

    # Determinar tipo
    var_type = None
    
    if len(p) == 7: # var/val id: type = expr
        if smt.check_type(p, 4):
            declared_type = p.slice[4].type
        else:
            smt.semantic_errors.append(f"Error semántico: Tipo inválido '{p.slice[4].type}' en la declaración de la variable '{var_name}'.")
            # Si no es válido, asignar TYPE_ANY para continuar con el análisis
            declared_type = 'TYPE_ANY'
        
        expr_type = p.slice[6].type

        error_msg = f"Error semántico: Incompatibilidad de tipos en la declaración de la variable '{var_name}'. Se esperaba '{declared_type}', se obtuvo '{expr_type}'."

        if not smt.check_type_compatibility(declared_type, expr_type, error_msg):
            smt.semantic_errors.append(error_msg)
            var_type = 'TYPE_ANY'
        else:
            var_type = declared_type

    elif len(p) == 5:
        if p[3] == ':': # var/val id: type
            if is_constant:
                smt.semantic_errors.append(f"Error semántico: La variable constante '{var_name}' debe ser inicializada.")
                return
            if smt.check_type(p, 4):
                var_type = p.slice[4].type
            else:
                smt.semantic_errors.append(f"Error semántico: Tipo inválido '{p.slice[4].type}' en la declaración de la variable '{var_name}'.")
                var_type = 'TYPE_ANY'
        else: # var/val id = expr
            if smt.check_type(p, 4):
                var_type = p.slice[4].type
            else:
                smt.semantic_errors.append(f"Error semántico: Tipo inválido '{p.slice[4].type}' en la declaración de la variable '{var_name}'.")
                var_type = 'TYPE_ANY'
    
    # Verificar que var_type fue asignado correctamente
    if var_type is None:
        smt.semantic_errors.append(f"Error semántico: No se pudo determinar el tipo para la variable '{var_name}'.")
        return
    
    # Declarar la variable (usar approach temporal si estamos dentro de una función)
    global _function_depth, _temp_variables
    
    if _function_depth > 0:
        # Estamos dentro de una función, almacenar temporalmente
        if _function_depth not in _temp_variables:
            _temp_variables[_function_depth] = {}
        _temp_variables[_function_depth][var_name] = var_type
    else:
        # Estamos en scope global, declarar directamente
        success, error_msg = smt.declare_variable(var_name, var_type, is_constant)
        if not success:
            smt.semantic_errors.append(f"Error semántico: {error_msg}")
            return
    
    p.slice[0].type = var_type
    decl_type = 'val_decl' if is_constant else 'var_decl'
    p[0] = (decl_type, var_type, var_name)

# --- Regla para tipos de datos ---
def p_type(p):
    '''
    type    : TYPE_INT
            | TYPE_STRING
            | TYPE_BOOLEAN
            | TYPE_FLOAT
            | TYPE_ANY
            | TYPE_UNIT
            | TYPE_LIST
            | TYPE_SET
            | TYPE_MAP
            | dynamic_type
    '''
    p.slice[0].type = p.slice[1].type
    p[0] = p[1]

def p_dynamic_type(p):
    '''
    dynamic_type    : ID
    '''
    format = smt.format_type(str(p[1]))
    if format in smt.symbol_table['types']:
        p.slice[0].type = format
    else:
        smt.semantic_errors.append(f"Error semántico: Tipo '{p[1]}' no declarado.")
        p.slice[0].type = 'TYPE_ANY'
    p[0] = p[1]

# FALTA T_T
# --- Regla para ciclo 'for' ---
def p_for_statement(p):
    '''
    for_statement   : FOR LPAREN ID IN expression RPAREN LBRACE program RBRACE
    '''
    p[0] = ('for', p[3], p[5], p[8])

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
                         | FUN ID LPAREN params RPAREN COLON type LBRACE program RBRACE
    '''
    if len(p) == 9:
        p[0] = ('function_decl', p[2], p[4], None, p[7])
    else:
        p[0] = ('function_decl', p[2], p[4], p[7], p[9])
    

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