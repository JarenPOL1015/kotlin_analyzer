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
    # QUE VAL ID COLON type NO FUNCIONA
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

# BRUNO ROMERO

# --- Regla para declaraciones de funciones ---
def p_function_declaration(p):
    '''
    function_declaration    : FUN ID LPAREN params RPAREN function_body
                            | FUN ID LPAREN params RPAREN EQUALS expression
                            | FUN ID LPAREN params RPAREN COLON type function_body
                            | FUN ID LPAREN params RPAREN COLON type EQUALS expression
    '''
    global _temp_function_params, _temp_function_params_stack, _function_context_stack
    global _function_depth, _temp_variables  # Añadir las nuevas variables
    
    function_name = p[2]
    params = p[4] if p[4] else []

    _temp_function_params_stack.append(_temp_function_params.copy())
    
    if params:
        for param in params:
            param_name = param[1]
            param_type = param[0]
            _temp_function_params[param_name] = param_type

    # Determinar el tipo de retorno
    if len(p) >= 8 and p[6] == ':':
        return_type = p.slice[7].type
    else:
        return_type = 'TYPE_UNIT'
    
    current_scope = smt.get_current_scope()
    
    function_context = {
        'name': function_name,
        'params': params, 
        'return_type': return_type
    }
    _function_context_stack.append(function_context)
    
    # El depth ya se incrementó en p_param
    current_depth = _function_depth
    
    # Entrar al scope de la función para procesar su cuerpo
    smt.enter_scope(function_name)

    # Declarar parámetros en el scope de la función
    param_names = set()
    for param in params:
        param_name = param[1]
        param_type = param[0]
        
        # Verificar parámetros duplicados
        if param_name in param_names:
            smt.semantic_errors.append(f"Error semántico: Parámetro '{param_name}' ya declarado en la función '{function_name}'.")
            continue
        param_names.add(param_name)
        
        # Declarar el parámetro como variable
        success, error_msg = smt.declare_variable(param_name, param_type, is_constant=False)
        if not success:
            smt.semantic_errors.append(f"Error semántico: {error_msg}")

    if len(p) == 7:
        body = p[6]
        p.slice[0].type = p.slice[6].type
        p[0] = ('fun_decl', return_type, function_name, params, body)
    
    elif len(p) == 8 and p[6] == '=': # FUN ID (params) = expression
        expr = p[7]
        if return_type == 'TYPE_UNIT':
            return_type = p.slice[7].type # Inferir el tipo de retorno
        
        if return_type == p.slice[7].type:
            p.slice[0].type = return_type
            p[0] = ('fun_decl', return_type, function_name, params, expr)
        else:
            smt.semantic_errors.append(f"Error semántico: Incompatibilidad de tipo de retorno. Se esperaba '{return_type}', se obtuvo '{p.slice[7].type}'")
            p.slice[0].type = return_type
            p[0] = ('fun_decl', return_type, function_name, params, expr)
    
    elif len(p) == 9: # FUN ID (params) : type function_body
        error_msg = f'Error semántico: Incompatibilidad de tipo de retorno en el cuerpo de la función \'{function_name}\'. Se esperaba \'{return_type}\', se obtuvo \'{p.slice[8].type}\'.'

        body = p[8]
        if smt.check_type_compatibility(return_type, p.slice[8].type, error_msg):
            p.slice[0].type = return_type
            p[0] = ('fun_decl', return_type, function_name, params, body)
        else:
            p.slice[0].type = return_type
            p[0] = ('fun_decl', return_type, function_name, params, body)
    
    elif len(p) == 10: # FUN ID (params) : type = expression
        error_msg = f"Error semántico: Incompatibilidad de tipo de retorno en la función '{function_name}'. Se esperaba '{return_type}', se obtuvo '{p.slice[9].type}'."
        expr = p[9]

        if smt.check_type_compatibility(return_type, p.slice[9].type, error_msg):
            p.slice[0].type = p.slice[7].type
            p[0] = ('fun_decl', p.slice[7].type, function_name, params, expr)
        else:
            p.slice[0].type = return_type
            p[0] = ('fun_decl', return_type, function_name, params, expr)

    if _temp_function_params_stack:
        _temp_function_params = _temp_function_params_stack.pop()
    else:
        _temp_function_params.clear()

    # Mover variables temporales al scope correcto antes de salir
    if current_depth in _temp_variables:
        function_scope = smt.get_current_scope()
        for var_name, var_type in _temp_variables[current_depth].items():
            if function_scope in smt.scopes:
                smt.scopes[function_scope]['variables'][var_name] = var_type
        # Limpiar variables temporales de este depth
        del _temp_variables[current_depth]

    # Salir del scope de la función
    smt.exit_scope()
    
    if return_type != 'TYPE_UNIT' and 'body' in locals() and body is not None:
        smt.check_all_paths_return(function_name, return_type, body)

    # Decrementar depth al salir de la función
    _function_depth -= 1
    
    # Declarar la función en el scope actual (después de salir del scope de la función)
    if _function_context_stack:
        func_ctx = _function_context_stack.pop()
        current_scope = smt.get_current_scope()  # Este es el scope donde debe declararse
        
        if current_scope in smt.scopes:
            if func_ctx['name'] in smt.scopes[current_scope]['functions']:
                smt.semantic_errors.append(f"Error semántico: Función '{func_ctx['name']}' ya declarada en el ámbito actual")
            else:
                smt.scopes[current_scope]['functions'][func_ctx['name']] = {
                    'return_type': func_ctx['return_type'],
                    'params': func_ctx['params']
                }

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

# --- Regla para el cuerpo de funciones ---
def p_function_body(p):
    '''
    function_body   : LBRACE statements return_statement RBRACE
                    | LBRACE empty return_statement RBRACE
    '''
    # Extraer información de la función desde el contexto del parser
    # Necesitamos acceder a la información de la función padre
    
    p.slice[0].type = p.slice[3].type
    p[0] = (p[2], p[3])

# NO TOCAR
def p_params(p):
    '''
    params  : params COMMA param
            | param
            | empty
    '''
    if len(p) == 4:
        p[0] = p[1] + [p[3]]
    elif len(p) == 2:
        if p[1] == []:
            p[0] = None
        else:
            p[0] = [p[1]]

def p_param(p):
    '''
    param   : ID COLON type
            | ID COLON type EQUALS expression
    '''
    global _temp_function_params, _function_depth
    
    # Incrementar depth cuando procesamos el primer parámetro de una función
    # Esto indica que estamos entrando al contexto de una función
    _function_depth += 1
    
    param_name = p[1]
    param_type = p.slice[3].type

    # WORKAROUND: Registrar inmediatamente el parámetro cuando se procesa
    _temp_function_params[param_name] = param_type

    # Verificar que el tipo sea válido
    if not smt.check_type(p, 3):
        smt.semantic_errors.append(f"Error semántico: Tipo inválido '{p.slice[3].type}' para el parámetro '{param_name}'.")
        # Usamos TYPE_ANY pero seguimos procesando el parámetro
        param_type = 'TYPE_ANY'
        p.slice[3].type = 'TYPE_ANY'
        _temp_function_params[param_name] = 'TYPE_ANY'

    if len(p) == 6:  # Parámetro con valor por defecto
        default_value = p[5]
        error_msg = f"Error semántico: Incompatibilidad de tipos en el valor por defecto del parámetro '{param_name}'. Se esperaba '{param_type}', se obtuvo '{p.slice[5].type}'."
        
        if smt.check_type_compatibility(param_type, p.slice[5].type, error_msg):
            p.slice[0].type = param_type
            p[0] = (param_type, param_name, default_value)
        else:
            p.slice[0].type = param_type
            p[0] = (param_type, param_name, None)
    else:  # Parámetro sin valor por defecto
        p.slice[0].type = param_type
        p[0] = (param_type, param_name, None)

            
def p_return_statement(p):
    '''
    return_statement    : RETURN expression
                        | RETURN
                        | empty
    '''
    if len(p) == 3:
        p.slice[0].type = p.slice[2].type
        p[0] = ('return', p.slice[2].type, p[2])
    else:
        p.slice[0].type = 'TYPE_UNIT'
        p[0] = ('return', 'TYPE_UNIT', None)


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
                | assignment_expression
    '''
                # | function_call
    if len(p) == 4:
        if p[2] in arithmetic_bin_ops:
            smt.semantic_check_binary_numeric(p, p[1], p[3], p[2])
        elif p[2] in relational_bin_ops + logical_bin_ops:
            smt.semantic_check_binary_boolean(p, p[1], p[3], p[2])
        elif p[2] == '..':
            smt.semantic_check_range_operator(p, p[1], p[3], p[2])
        elif p[1] == '(' and p[3] == ')':
            p.slice[0].type = p.slice[2].type
            p[0] = p[2]
    elif len(p) == 3:
        if p[1] == '!':
            smt.semantic_check_unary_boolean(p, p[2], p[1])
    elif len(p) == 2:
        # Para assignment_expression, simplemente pasar el resultado
        p.slice[0].type = p.slice[1].type
        p[0] = p[1]

def p_expression_number_int(p):
    'expression : NUMBER_INT'
    p[0] = p[1]
    p.slice[0].type = 'TYPE_INT'

def p_expression_number_long(p):
    'expression : NUMBER_LONG'
    p[0] = p[1]
    p.slice[0].type = 'TYPE_LONG'

def p_expression_number_float(p):
    'expression : NUMBER_FLOAT'
    p[0] = p[1]
    p.slice[0].type = 'TYPE_FLOAT'

def p_expression_number_double(p):
    'expression : NUMBER_DOUBLE'
    p[0] = p[1]
    p.slice[0].type = 'TYPE_DOUBLE'

def p_expression_string(p):
    'expression : STRING'
    p[0] = p[1]
    p.slice[0].type = 'TYPE_STRING'

def p_expression_char(p):
    'expression : CHAR'
    p[0] = p[1]
    p.slice[0].type = 'TYPE_CHAR'

def p_expression_literal_boolean(p):
    '''
    expression : LITERAL_TRUE
               | LITERAL_FALSE
    '''
    if p[1] == 'true':
        p[0] = True
    else:
        p[0] = False
    p.slice[0].type = 'TYPE_BOOLEAN'

def p_expression_id(p):
    '''
    expression : ID
    '''
    global _temp_function_params
    
    var_name = p[1]
    
    # WORKAROUND: Primero verificar si es un parámetro temporal
    if var_name in _temp_function_params:
        temp_type = _temp_function_params[var_name]
        p.slice[0].type = temp_type
        p[0] = var_name
        return
    
    # Buscar en variables
    var_type, found_scope = smt.find_symbol(var_name, 'variables')
    if var_type:
        p.slice[0].type = var_type
        p[0] = var_name
        return

    # Buscar en constantes
    const_type, found_scope = smt.find_symbol(var_name, 'constants')
    if const_type:
        p.slice[0].type = const_type
        p[0] = var_name
        return
    smt.semantic_errors.append(f"Error semántico: Variable '{var_name}' no declarada.")
    p.slice[0].type = 'TYPE_ANY'
    p[0] = var_name


def p_expression_cast(p):
    '''
    expression : expression AS type
    '''
    from_type = p.slice[1].type
    to_type = p.slice[3].type
    p.slice[0].type = to_type
    p[0] = ('cast', p[1], to_type)
    if not smt.check_explicit_cast(from_type, to_type):
        smt.semantic_errors.append(f"Error semántico: Casting explícito inválido de '{from_type}' a '{to_type}'")

def p_expression_assignment(p):
    '''
    assignment_expression   : ID EQUALS expression
    '''
    global _temp_function_params
    
    var_name = p[1]
    
    if var_name in _temp_function_params:
        temp_type = _temp_function_params[var_name]
        error_msg = f"Error semántico: Incompatibilidad de tipos en la asignación a la variable '{var_name}'. Se esperaba '{temp_type}', se obtuvo '{p.slice[3].type}'."
        if smt.check_type_compatibility(temp_type, p.slice[3].type, error_msg):
            p.slice[0].type = temp_type
            p[0] = ('assign', var_name, p[3])
        else:
            p.slice[0].type = 'TYPE_ANY'
            p[0] = ('assign', var_name, p[3])
        return
    
    # Buscar la variable en el scope chain
    var_type, found_scope = smt.find_symbol(var_name, 'variables')
    const_type, const_scope = smt.find_symbol(var_name, 'constants')
    
    # Verificar si la variable existe
    if not var_type and not const_type:
        smt.semantic_errors.append(f"Error semántico: Variable '{var_name}' no declarada.")
        p.slice[0].type = 'TYPE_ANY'
        p[0] = ('assign', var_name, p[3])
        return
    
    # Verificar si es una constante
    if const_type:
        smt.semantic_errors.append(f"Error semántico: No se puede asignar a la variable constante '{var_name}'.")
        p.slice[0].type = 'TYPE_ANY'
        p[0] = ('assign', var_name, p[3])
        return
    
    # Verificar compatibilidad de tipos
    error_msg = f"Error semántico: Incompatibilidad de tipos en la asignación a la variable '{var_name}'. Se esperaba '{var_type}', se obtuvo '{p.slice[3].type}'."
    if smt.check_type_compatibility(var_type, p.slice[3].type, error_msg):
        p.slice[0].type = var_type
        p[0] = ('assign', var_name, p[3])
    else:
        p.slice[0].type = 'TYPE_ANY'
        p[0] = ('assign', var_name, p[3])

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