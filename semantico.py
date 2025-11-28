# DAVID SANDOVAL

semantic_errors = []
current_line = None  # Variable global para rastrear la línea actual

# Lista de tipos numéricos según precisión
numeric_types = [
    'TYPE_INT',
    'TYPE_LONG',
    'TYPE_FLOAT',
    'TYPE_DOUBLE',
]

# Lista de tipos en general
primivites_types = numeric_types + [
    'TYPE_BOOLEAN',
    'TYPE_CHAR',
    'TYPE_UNIT',
    'TYPE_ANY',
]

collection_types = [
    'TYPE_LIST',
    'TYPE_SET',
    'TYPE_MAP',
]

all_types = primivites_types + collection_types + ['TYPE_STRING']

symbol_table = {
    '':{
        'variables': {},
        'constants': {},
        'functions': {},
    },
}

type_mapping = {
    'Int': 'TYPE_INT',
    'Long': 'TYPE_LONG',
    'Float': 'TYPE_FLOAT',
    'Double': 'TYPE_DOUBLE',
    'Boolean': 'TYPE_BOOLEAN',
    'String': 'TYPE_STRING',
    'Char': 'TYPE_CHAR',
    'Unit': 'TYPE_UNIT',
    'Any': 'TYPE_ANY',
    'Null': 'TYPE_NULL',
    'List': 'TYPE_LIST',
    'Set': 'TYPE_SET',
    'Map': 'TYPE_MAP',
}

# Funciones miembro de conversión para cada tipo
type_member_functions = {
    'TYPE_INT': {
        'toInt': {'params': [], 'return_type': 'TYPE_INT'},
        'toLong': {'params': [], 'return_type': 'TYPE_LONG'},
        'toFloat': {'params': [], 'return_type': 'TYPE_FLOAT'},
        'toDouble': {'params': [], 'return_type': 'TYPE_DOUBLE'},
        'toChar': {'params': [], 'return_type': 'TYPE_CHAR'},
        'toString': {'params': [], 'return_type': 'TYPE_STRING'},
    },
    'TYPE_LONG': {
        'toInt': {'params': [], 'return_type': 'TYPE_INT'},
        'toLong': {'params': [], 'return_type': 'TYPE_LONG'},
        'toFloat': {'params': [], 'return_type': 'TYPE_FLOAT'},
        'toDouble': {'params': [], 'return_type': 'TYPE_DOUBLE'},
        'toChar': {'params': [], 'return_type': 'TYPE_CHAR'},
        'toString': {'params': [], 'return_type': 'TYPE_STRING'},
    },
    'TYPE_FLOAT': {
        'toInt': {'params': [], 'return_type': 'TYPE_INT'},
        'toLong': {'params': [], 'return_type': 'TYPE_LONG'},
        'toFloat': {'params': [], 'return_type': 'TYPE_FLOAT'},
        'toDouble': {'params': [], 'return_type': 'TYPE_DOUBLE'},
        'toString': {'params': [], 'return_type': 'TYPE_STRING'},
    },
    'TYPE_DOUBLE': {
        'toInt': {'params': [], 'return_type': 'TYPE_INT'},
        'toLong': {'params': [], 'return_type': 'TYPE_LONG'},
        'toFloat': {'params': [], 'return_type': 'TYPE_FLOAT'},
        'toDouble': {'params': [], 'return_type': 'TYPE_DOUBLE'},
        'toString': {'params': [], 'return_type': 'TYPE_STRING'},
    },
    'TYPE_BOOLEAN': {
        'toString': {'params': [], 'return_type': 'TYPE_STRING'},
    },
    'TYPE_STRING': {
        'toInt': {'params': [], 'return_type': 'TYPE_INT'},
        'toLong': {'params': [], 'return_type': 'TYPE_LONG'},
        'toFloat': {'params': [], 'return_type': 'TYPE_FLOAT'},
        'toDouble': {'params': [], 'return_type': 'TYPE_DOUBLE'},
        'toBoolean': {'params': [], 'return_type': 'TYPE_BOOLEAN'},
        'toString': {'params': [], 'return_type': 'TYPE_STRING'},
    },
    'TYPE_CHAR': {
        'toInt': {'params': [], 'return_type': 'TYPE_INT'},
        'toString': {'params': [], 'return_type': 'TYPE_STRING'},
    },
}

collection_functions = ['listOf', 'mutableListOf', 'setOf', 'mutableSetOf', 'mapOf', 'mutableMapOf']

scope_stack = ['']

# --- Utilidades Semánticas ---

def add_semantic_error(message, lineno=None):
    '''Agrega un error semántico con información de línea.'''
    if lineno is None:
        lineno = current_line
    if lineno:
        semantic_errors.append(f"{message} (Línea {lineno})")
    else:
        semantic_errors.append(message)

def format_type(type_str):
    '''Retorna el tipo formateado como 'TYPE_<TYPE_STR>'.'''
    return "TYPE_" + type_str.upper()

def map_type(type_str):
    '''Mapea un string de tipo a su representación en el analizador.'''
    return type_mapping.get(type_str, None)

def get_top_type_numeric(type_a, type_b):
    '''Retorna el tipo numérico de mayor precisión entre type_a y type_b.'''
    types = ['TYPE_ANY'] + numeric_types
    if type_a in types and type_b in types:
        return max(type_a, type_b, key=lambda t: types.index(t))
    return None

def get_current_scope():
    '''Retorna el scope actual como string.'''
    return '.'.join(scope_stack)

def lookup_variable(var_name):
    '''
    Busca una variable o constante en la tabla de símbolos, desde el scope actual hacia arriba.

    Parámetros:
    - var_name: el nombre de la variable o constante a buscar.
    
    Retorna:
    - (tipo, True) si se encuentra la constante.
    - (tipo, False) si se encuentra la variable.
    - (None, None) si no se encuentra.
    '''
    for i in range(len(scope_stack)-1, -1, -1): # Rango: len a 0
        scope_name = '.'.join(scope_stack[:i+1])
        
        if scope_name in symbol_table:
            if var_name in symbol_table[scope_name]['variables']:
                return (symbol_table[scope_name]['variables'][var_name], False)
            if var_name in symbol_table[scope_name]['constants']:
                return (symbol_table[scope_name]['constants'][var_name], True)
    
    return (None, None)

def lookup_function(func_name):
    '''
    Busca una función en la tabla de símbolos, desde el scope actual hacia arriba.

    Parámetros:
    - func_name: el nombre de la función a buscar.
    
    Retorna:
    - La información de la función si se encuentra.
    - None si no se encuentra.
    '''
    for i in range(len(scope_stack)-1, -1, -1):
        scope_name = '.'.join(scope_stack[:i+1])
        
        if scope_name in symbol_table:
            if func_name in symbol_table[scope_name]['functions']:
                return symbol_table[scope_name]['functions'][func_name]
    
    return None

def create_scope(scope_name):
    '''Crea y registra un nuevo scope en la tabla de símbolos.'''
    scope_stack.append(scope_name)
    full_scope_name = get_current_scope()
    symbol_table[full_scope_name] = {
        'variables': {},
        'constants': {},
        'functions': {},
    }
    return full_scope_name

def delete_scope(scope_name):
    '''Elimina un scope de la tabla de símbolos y del stack. Recibe el scope_name completo.'''
    if scope_name in symbol_table:
        del symbol_table[scope_name]
        scope_stack.pop() # Asume que es el último agregado

def is_in_function():
    '''Verifica si estamos dentro de una función (no solo if/for/while).'''
    return any(scope for scope in scope_stack if scope and scope not in ['if', 'else', 'for', 'while'])

# FUNCIONES PRINCIPALES
def treat_type(type_str):
    '''
    Procesa un tipo del AST y retorna su representación interna.

    Parámetros:
    - type_str: un string que representa un tipo en el AST.
        Ejemplos:
        - 'Int'
        - 'String'
    
    Retorna:
    - El tipo mapeado (ej. 'TYPE_INT', 'TYPE_STRING', etc.). Si el tipo es desconocido, retorna 'UNKNOWN' y añade un error semántico.
    '''
    mapped_type = map_type(type_str)
    
    if mapped_type:
        return mapped_type
    else:
        add_semantic_error(f"Error semántico: Tipo desconocido '{type_str}'.")
        return 'UNKNOWN'

# DAVID SANDOVAL

def treat_function_declaration(func_tuple):
    '''
    Procesa una tupla de declaración de función del AST. Crea las variables internas y sus parámetros en la tabla de símbolos. Agrega la función a la tabla de símbolos. Verifica que todos los caminos posibles retornen un valor correcto. 

    Parámetros:
    - func_tuple: una tupla que representa una declaración de función en el AST.
        Ejemplos:
        - ('fun_decl', nombre, [(ID, tipo)], 'TYPE_BOOLEAN', function_body, lineno)
    '''
    global current_line
    func_name = func_tuple[1]
    func_params = func_tuple[2]
    func_return_type = treat_type(func_tuple[3]) if func_tuple[3] else None
    func_body = func_tuple[4]
    current_line = func_tuple[5]

    # Verificar que no exista función con el mismo nombre en ningún scope del stack
    if lookup_function(func_name):
        add_semantic_error(f"Error semántico: Función '{func_name}' ya declarada.")
        return
    
    # Si el cuerpo es una expresión simple (fun foo() = expr), el tipo de retorno puede ser ANY si no se especifica
    if not isinstance(func_body, list):
        func_return_type = func_return_type if func_return_type else 'TYPE_ANY'
    else:
        func_return_type = func_return_type if func_return_type else 'TYPE_UNIT'
    
    # Agregar función a las funciones del padre, ya que no existe en el scope actual
    parent_scope = get_current_scope()
    symbol_table[parent_scope]['functions'][func_name] = {
        'params': func_params,
        'return_type': func_return_type,
    }

    # Crear scope de la función
    func_scope_name = create_scope(func_name)
    symbol_table[func_scope_name]['return_type'] = func_return_type

    # Agregar parámetros a la tabla de símbolos
    for param in func_params:
        param_name = param[0]
        param_type = treat_type(param[1])
        
        if param_name in symbol_table[func_scope_name]['variables']:
            add_semantic_error(f"Error semántico: Parámetro '{param_name}' ya declarado en la función '{func_name}'.")
        else:
            symbol_table[func_scope_name]['variables'][param_name] = param_type
    
    # Si el cuerpo es una expresión simple (fun foo() = expr)
    if not isinstance(func_body, list):
        expr_return_type = treat_expression(func_body)
        if not check_implicit_coerce(func_return_type, expr_return_type):
            add_semantic_error(f"Error semántico: La función '{func_name}' debe retornar un valor de tipo '{func_return_type}', pero se encontró un retorno de tipo '{expr_return_type}'.")
        scope_stack.pop()
        return

    # Procesar bloque de sentencias
    returns = process_block_returns(func_body, func_name)

    # Validar tipos de retorno
    expected_return = symbol_table[func_scope_name]['return_type']
    validate_function_returns(func_name, expected_return, returns)

    # Limpiar scope de la función
    scope_stack.pop()

# DAVID SANDOVAL

def validate_function_returns(func_name, expected_return, retornos):
    '''Valida que los tipos de retorno de una función sean correctos.'''
    if expected_return and expected_return != 'TYPE_UNIT':
        # La función DEBE retornar algo
        has_terminal_return = any(is_terminal for _, is_terminal in retornos)
        if not has_terminal_return:
            add_semantic_error(f"Error semántico: La función '{func_name}' debe retornar un valor de tipo '{expected_return}'.")
        
        for ret_type, _ in retornos:
            if not check_implicit_coerce(expected_return, ret_type):
                add_semantic_error(f"Error semántico: La función '{func_name}' debe retornar un valor de tipo '{expected_return}', pero se encontró un retorno de tipo '{ret_type}'.")
                break
    else:
        # La función NO debe retornar nada o solo TYPE_UNIT
        for ret_type, _ in retornos:
            if ret_type != 'TYPE_UNIT':
                add_semantic_error(f"Error semántico: La función '{func_name}' no debe retornar ningún valor, pero se encontró un retorno de tipo '{ret_type}'.")
                break

# DAVID SANDOVAL

def treat_while_statement(statement):
    '''Procesa un statement while y retorna información sobre returns.'''
    condition = statement[1]
    cuerpo_while = statement[2]

    condition_type = treat_expression(condition)
    if condition_type != 'TYPE_BOOLEAN':
        add_semantic_error(f"Error semántico: La condición del 'while' debe ser de tipo 'TYPE_BOOLEAN', no '{condition_type}'.")

    # Crear scope para el while
    while_scope_name = create_scope('while')

    all_returns = []
    for stmt in cuerpo_while:
        ret = treat_statement(stmt)
        if ret:
            # Returns en while nunca son terminales (pueden no ejecutarse)
            for ret_type, _ in ret:
                all_returns.append((ret_type, False))

    # Limpiar scope del while
    delete_scope(while_scope_name)
    
    return all_returns if all_returns else None

# DAVID SANDOVAL

def treat_return(return_tuple):
    '''
    Procesa una tupla de retorno del AST. Analiza la expresión de retorno y retorna su tipo.

    Parámetros:
    - return_tuple: una tupla que representa una sentencia de retorno en el AST.
        Ejemplos:
        - ('return', valores, lineno)
        - ('return', None, lineno)
    
    Retorna:
    - El tipo de la expresión retornada.
    '''
    global current_line
    return_type = return_tuple[1]
    current_line = return_tuple[2]
    return treat_expression(return_type) if return_type else 'TYPE_UNIT'

def treat_variable_declaration(decl_tuple):
    '''
    Procesa una tupla de declaración de variable o constante del AST. Crea la variable o constante en la tabla de símbolos y verifica la compatibilidad de tipos.

    Parámetros:
    - decl_tuple: una tupla que representa una declaración de variable o constante en el AST.
        Ejemplos:
        - ('var_decl', tipo_variable, nombre_variable, expresion, lineno)
        - ('val_decl', tipo_variable, nombre_variable, expresion, lineno)
    '''
    global current_line

    kind = decl_tuple[0]
    var_type_str = decl_tuple[1]
    var_name = decl_tuple[2]
    expr = decl_tuple[3]
    current_line = decl_tuple[4]

    var_type = treat_type(var_type_str) if var_type_str else None
    expr_type = treat_expression(expr) if expr else None

    # Obtener scope actual
    current_scope = get_current_scope()
    
    # Verificar si la variable ya está declarada en el ámbito actual
    if var_name in symbol_table.get(current_scope, {}).get('variables', {}) or var_name in symbol_table.get(current_scope, {}).get('constants', {}):
        add_semantic_error(f"Error semántico: Variable o constante '{var_name}' ya declarada en el ámbito actual.")
        return
    
    # Declarar la variable o constante
    is_var = (kind == 'var_decl')
    target_dict = symbol_table[current_scope]['variables' if is_var else 'constants']
    
    if var_type and expr_type:
        if check_implicit_coerce(var_type, expr_type):
            target_dict[var_name] = var_type
    elif var_type and not expr_type:
        if is_var:
            target_dict[var_name] = var_type
        else:
            add_semantic_error(f"Error semántico: La constante '{var_name}' debe ser inicializada.")
    elif not var_type and expr_type:
        target_dict[var_name] = expr_type
    else:
        add_semantic_error(f"Error semántico: No se puede inferir el tipo de la variable o constante '{var_name}'.")

def treat_assignment(assignment_tuple):
    '''
    Procesa una tupla de asignación del AST. Verifica que la variable exista y que el tipo de la expresión sea compatible con el tipo de la variable.

    Parámetros:
    - assignment_tuple: una tupla que representa una asignación en el AST.
        Ejemplos:
        - ('assign', nombre_variable, '=', expresion, lineno)
        - ('assign', nombre_variable, '+=', expresion, lineno)
    '''
    global current_line
    var_name = assignment_tuple[1]
    operator = assignment_tuple[2]
    expr = assignment_tuple[3]
    current_line = assignment_tuple[4]

    expr_type = treat_expression(expr)

    # Buscar variable en la tabla de símbolos
    var_type, is_constant = lookup_variable(var_name)
    
    if var_type:
        if is_constant:
            add_semantic_error(f"Error semántico: No se puede asignar a la constante '{var_name}'.")
        else:
            # Para asignaciones compuestas, validar la operación
            if operator == '=':
                check_implicit_coerce(var_type, expr_type)
            elif operator in ['+=', '-=', '*=', '/=', '%=']:
                # La operación compuesta debe ser válida entre el tipo de la variable y la expresión
                op_symbol = operator[0]  # Extraer +, -, *, /, %
                
                # Crear una expresión temporal para validar la operación
                temp_expr_type = treat_arithmetic_operation(op_symbol, [
                    ('id', var_name),  # Variable actual
                    expr  # Expresión
                ])
                
                # El resultado debe ser compatible con el tipo de la variable
                if temp_expr_type != 'TYPE_ANY':
                    check_implicit_coerce(var_type, temp_expr_type)
    else:
        add_semantic_error(f"Error semántico: Variable '{var_name}' no declarada.")