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

# JAREN PAZMIÑO

def treat_if_statement(statement):
    '''
    Procesa un statement if y retorna información sobre returns.

    Parámetros:
    - statement: una tupla que representa un statement if en el AST.
        Ejemplos:
        - ('if_statement', condicion, cuerpo_if, cuerpo_else)

    Retorna:
    - Lista de tuplas [(tipo_retorno, es_terminal)...] si hay retornos.
    '''
    condition = statement[1]
    cuerpo_if = statement[2]
    cuerpo_else = statement[3]

    condition_type = treat_expression(condition)
    if condition_type != 'TYPE_BOOLEAN':
        add_semantic_error(f"Error semántico: La condición del 'if' debe ser de tipo 'TYPE_BOOLEAN', no '{condition_type}'.")
    
    # Crear scope para el if
    if_scope_name = create_scope('if')

    returns_if = []
    if cuerpo_if:
        for stmt in cuerpo_if:
            ret = treat_statement(stmt)
            if ret:
                returns_if.extend(ret)
    else:
        add_semantic_error(f"Error semántico: El bloque 'if' debe contener al menos una sentencia.")

    # Limpiar scope del if
    delete_scope(if_scope_name)

    # Procesar else/else-if
    returns_elif = []
    returns_else = []
    if cuerpo_else: # ('else_part', cuerpo) o ('else_if', statement)
        if cuerpo_else[0] == 'else_if':
            # Es un else if anidado
            ret = treat_statement(cuerpo_else[1])
            if ret:
                returns_elif.extend(ret)
        elif cuerpo_else[0] == 'else_part':
            # Es un else normal
            # Un else es terminal cuando tiene returns terminales
            else_scope_name = create_scope('else')
                
            for stmt in cuerpo_else[1]:
                ret = treat_statement(stmt)
                if ret:
                    returns_else.extend(ret)
                
            delete_scope(else_scope_name)
    
    # Todos los retornos en if y elif no son terminales, ya que pueden no ejecutarse
    returns_if = [(ret_type, False) for ret_type, _ in returns_if]
    returns_elif = [(ret_type, False) for ret_type, _ in returns_elif]

    all_returns = []

    all_returns.extend(returns_if)
    all_returns.extend(returns_elif)
    all_returns.extend(returns_else)
    
    return all_returns if all_returns else None

def treat_statement(statement):
    '''
    Analiza una sentencia del AST y retorna su tipo o acción semántica.

    Parámetros:
    - statement: una tupla que representa una sentencia en el AST.
        Ejemplos:
        - ('return', valores)
        - ('if_statement', condition, cuerpo_if, cuerpo_else)

    Retorna:
    - Lista de tuplas [(tipo_retorno, es_terminal)...] si hay retorno.
    - None si no hay retornos.
    '''
    kind = statement[0]
    
    if kind == 'return':
        if not is_in_function():
            add_semantic_error(f"Error semántico: Statement 'return' fuera de una función.")
            return None
        
        ret_type = treat_return(statement)
        return [(ret_type, True)]
    
    elif kind == 'assign':
        treat_assignment(statement)
        return None
    
    elif kind == 'var_decl' or kind == 'val_decl':
        treat_variable_declaration(statement)
        return None
    
    elif kind == 'fun_decl':
        treat_function_declaration(statement)
        return None
    
    # FALTA: VALIDAR QUE LAS ENTRADAS DE FUNCIONES SEAN CORRECTAS
    elif kind == 'function_call':
        treat_function_call(statement)
        return None
    
    elif kind == 'print' or kind == 'println':
        treat_print_statement(statement)
        return None
    
    elif kind == 'readLine':
        treat_readline_statement(statement)
        return None
    
    elif kind == 'if_statement':
        return treat_if_statement(statement)
    
    elif kind == 'for_statement':
        return treat_for_statement(statement)
    
    elif kind == 'while_statement':
        return treat_while_statement(statement)

    return None

def process_block_returns(statements, func_name=None):
    '''
    Procesa una lista de statements y detecta returns y código inalcanzable.

    Parámetros:
    - statements: lista de sentencias en el bloque.
    - func_name: nombre de la función actual (opcional, para mensajes de error).
    
    Retorna:
    - Lista de tuplas [(tipo_retorno, es_terminal), ...]
    '''
    returns = []
    terminal_found_at = None

    for idx, statement in enumerate(statements):
        if terminal_found_at is not None:
            if func_name:
                add_semantic_error(f"Error semántico: Código inalcanzable después de return terminal en la función '{func_name}'.")
            break

        return_info = treat_statement(statement)
        if return_info:
            for ret_type, is_terminal in return_info:
                returns.append((ret_type, is_terminal))
                if is_terminal:
                    terminal_found_at = idx
    
    return returns

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

# JAREN PAZMIÑO

def check_explicit_cast(from_type, to_type):
    """Verifica si un casting explícito desde from_type a to_type es válido."""
    if from_type in primivites_types or to_type in primivites_types:
        add_semantic_error(f'Error semántico: El casting explícito solo es válido entre objetos')
        return False
    elif from_type == 'UNKNOWN' or to_type == 'UNKNOWN':
        return False
    elif from_type == to_type:
        return True
    elif from_type == 'TYPE_ANY' or to_type == 'TYPE_ANY':
        return True
    return False

# BRUNO ROMERO

def check_implicit_coerce(to_type, from_type):
    '''Verifica si una conversión implícita de from_type a to_type es válida.'''
    if to_type == from_type:
        return True
    elif to_type == 'TYPE_ANY' or from_type == 'TYPE_ANY':
        return True
    elif to_type in numeric_types and from_type in numeric_types:
        to_index = numeric_types.index(to_type)
        from_index = numeric_types.index(from_type)
        if to_index < from_index:
            add_semantic_error(f"Error semántico: Posible pérdida de datos al convertir de '{from_type}' a '{to_type}'")
            return False
        return True
    add_semantic_error(f"Error semántico: Tipos incompatibles '{from_type}' y '{to_type}' para conversión implícita.")
    return False

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

# BRUNO ROMERO

def treat_for_statement(statement):
    '''
    Procesa un statement for y retorna información sobre returns.
    
    Parámetros:
    - statement: una tupla que representa un statement for en el AST.
        Ejemplos:
        - ('for_statement', variable_iteracion, rango, cuerpo)
    '''
    variable = statement[1]
    iter_expr = statement[2]
    cuerpo_for = statement[3]

    iter_type = treat_expression(iter_expr)
    if iter_type != 'TYPE_RANGE' and iter_type not in collection_types:
        add_semantic_error(f"Error semántico: La expresión de rango en el 'for' debe ser un iterable, no '{iter_type}'.")

    # Crear scope para el for
    for_scope_name = create_scope('for')

    # Agregar variable de iteración
    symbol_table[for_scope_name]['variables'][variable] = 'TYPE_INT'

    all_returns = []
    for stmt in cuerpo_for:
        ret = treat_statement(stmt)
        if ret:
            # Returns en for nunca son terminales (pueden no ejecutarse)
            for ret_type, _ in ret:
                all_returns.append((ret_type, False))
    
    # Limpiar scope del for
    delete_scope(for_scope_name)
    
    return all_returns if all_returns else None

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

# BRUNO ROMERO

def treat_expression(expression):
    '''
    Analiza recursivamente una expresión del AST para determinar su tipo.
    Si hay un error en la expresión, se añade a la lista de errores semánticos.

    Parámetros:
    - expression: una tupla que representa una expresión en el AST.
        Ejemplos:
        - ('Int', 5)
        - ('id', 'x')
        - ('+', [('id', 'x'), ('Int', 10)])
    
    Retorna:
    - El tipo de la expresión (ej. 'TYPE_INT', 'TYPE_STRING', etc.')
    '''
    global current_line
    kind = expression[0]
    values = expression[1]
    
    # Extraer lineno si existe (último elemento de la tupla para literales e IDs)
    if len(expression) > 2 and isinstance(expression[-1], int):
        current_line = expression[-1]

    # Literales
    mapped_type = map_type(kind)
    if mapped_type:
        return mapped_type
    
    # Identificadores
    if kind == 'id':
        var_type, _ = lookup_variable(values)
        if var_type:
            return var_type
        add_semantic_error(f"Error semántico: Variable o constante '{values}' no declarada.")
        return 'TYPE_ANY'
    
    # Null literal
    if kind == 'Null':
        return 'TYPE_NULL'
    
    # Llamadas a funciones
    if kind == 'function_call':
        return treat_function_call(expression)
    
    # readLine como expresión (retorna TYPE_ANY)
    if kind == 'readLine':
        treat_readline_statement(expression)
        return 'TYPE_ANY'
    
    # print/println como expresión (retornan TYPE_UNIT)
    if kind in ['print', 'println']:
        treat_print_statement(expression)
        return 'TYPE_UNIT'
    
    # Operaciones aritméticas
    if kind in ['+', '-', '*', '/', '%']:
        return treat_arithmetic_operation(kind, values)
    
    # Operaciones booleanas
    if kind in ['&&', '||']:
        return treat_boolean_operation(kind, values)
        
    # Operaciones relacionales
    if kind in ['==', '!=', '>', '>=', '<', '<=']:
        return treat_relational_operation(kind, values)
    
    # Operador de rango
    if kind == '..':
        return treat_range_operation(values)
    
    # Operador NOT
    if kind == '!':
        return treat_not_operation(values)
        
    # Cast
    if kind == 'cast':
        return treat_cast_operation(values)
        
    # No reconocido
    add_semantic_error(f"Error semántico: Expresión no reconocida '{kind}'.")
    return 'TYPE_ANY'

def treat_arithmetic_operation(operator, operands):
    '''Procesa operaciones aritméticas (+, -, *, /, %).'''
    left_type = treat_expression(operands[0])
    right_type = treat_expression(operands[1])

    if left_type in numeric_types and right_type in numeric_types:
        return get_top_type_numeric(left_type, right_type)
    elif operator == '+' and (left_type == 'TYPE_STRING' or right_type == 'TYPE_STRING'):
        return 'TYPE_STRING'
    else:
        add_semantic_error(f"Error semántico: Tipos incompatibles '{left_type}' y '{right_type}' para la operación '{operator}'.")
        return 'TYPE_ANY'

def treat_boolean_operation(operator, operands):
    '''Procesa operaciones booleanas (&&, ||).'''
    left_type = treat_expression(operands[0])
    right_type = treat_expression(operands[1])

    if left_type == 'TYPE_BOOLEAN' and right_type == 'TYPE_BOOLEAN':
        return 'TYPE_BOOLEAN'
    else:
        add_semantic_error(f"Error semántico: Tipos incompatibles '{left_type}' y '{right_type}' para la operación lógica '{operator}'.")
        return 'TYPE_ANY'

def treat_relational_operation(operator, operands):
    '''Procesa operaciones relacionales (==, !=, >, >=, <, <=).'''
    left_type = treat_expression(operands[0])
    right_type = treat_expression(operands[1])

    if operator in ['==', '!=']:
        # ANY puede compararse con cualquier tipo
        if left_type == 'TYPE_ANY' or right_type == 'TYPE_ANY':
            return 'TYPE_BOOLEAN'
        
        # NULL puede compararse con cualquier tipo
        if left_type == 'TYPE_NULL' or right_type == 'TYPE_NULL':
            return 'TYPE_BOOLEAN'

        # Comparaciones válidas entre tipos específicos
        valid_pairs = [
            (left_type in numeric_types + ['TYPE_CHAR'] and right_type in numeric_types + ['TYPE_CHAR']),
            (left_type == 'TYPE_BOOLEAN' and right_type == 'TYPE_BOOLEAN'),
            (left_type == 'TYPE_STRING' and right_type == 'TYPE_STRING'),
            (left_type == right_type)
        ]
        if any(valid_pairs):
            return 'TYPE_BOOLEAN'
        else:
            add_semantic_error(f"Error semántico: Tipos incompatibles '{left_type}' y '{right_type}' para la operación de igualdad '{operator}'.")
            return 'TYPE_ANY'
    else:
        if left_type in numeric_types + ['TYPE_CHAR'] and right_type in numeric_types + ['TYPE_CHAR']:
            return 'TYPE_BOOLEAN'
        else:
            add_semantic_error(f"Error semántico: Tipos incompatibles '{left_type}' y '{right_type}' para la operación relacional '{operator}'.")
            return 'TYPE_ANY'

def treat_range_operation(operands):
    '''Procesa el operador de rango (..).'''
    left_type = treat_expression(operands[0])
    right_type = treat_expression(operands[1])

    if left_type in ['TYPE_INT', 'TYPE_LONG'] and right_type in ['TYPE_INT', 'TYPE_LONG']:
        return 'TYPE_RANGE'
    else:
        add_semantic_error(f"Error semántico: Tipos incompatibles '{left_type}' y '{right_type}' para el operador de rango '..'.")
        return 'TYPE_ANY'

def treat_not_operation(operands):
    '''Procesa el operador NOT (!).'''
    operand_type = treat_expression(operands[0])
    if operand_type == 'TYPE_BOOLEAN':
        return 'TYPE_BOOLEAN'
    else:
        add_semantic_error(f"Error semántico: Tipo incompatible '{operand_type}' para el operador lógico NOT.")
        return 'TYPE_ANY'

def treat_cast_operation(operands):
    '''Procesa operaciones de cast (as).'''
    expr_type = treat_expression(operands[0])
    to_type = treat_type(operands[1])

    if check_explicit_cast(expr_type, to_type):
        return to_type
    else:
        add_semantic_error(f"Error semántico: Cast inválido de '{expr_type}' a '{to_type}'.")
        return 'TYPE_ANY'

def treat_function_call(call_tuple):
    '''
    Procesa una llamada a función y valida que exista y tenga los argumentos correctos.
    
    Parámetros:
    - call_tuple: ('function_call', nombre_funcion, [argumentos])
                  ('function_call', ('member_call', objeto, nombre_funcion), [argumentos])
    
    Retorna:
    - El tipo de retorno de la función
    '''
    func_name = call_tuple[1]
    arguments = call_tuple[2]
    
    # Verificar si es una llamada a función miembro (obj.toInt())
    if isinstance(func_name, tuple) and func_name[0] == 'member_call':
        object_expr = func_name[1]
        member_func_name = func_name[2]
        
        # Obtener el tipo del objeto
        object_type = treat_expression(object_expr)
        
        # Verificar que la función miembro exista para ese tipo
        if object_type in type_member_functions:
            if member_func_name in type_member_functions[object_type]:
                func_info = type_member_functions[object_type][member_func_name]
                
                # Validar número de argumentos
                expected_params = func_info['params']
                if len(arguments) != len(expected_params):
                    add_semantic_error(f"Error semántico: La función miembro '{member_func_name}' de tipo '{object_type}' requiere {len(expected_params)} argumentos, pero se proporcionaron {len(arguments)}.")
                
                return func_info['return_type']
            else:
                add_semantic_error(f"Error semántico: El tipo '{object_type}' no tiene la función miembro '{member_func_name}'.")
                return 'TYPE_ANY'
        else:
            add_semantic_error(f"Error semántico: El tipo '{object_type}' no soporta funciones miembro.")
            return 'TYPE_ANY'
    
    # Buscar la función en la tabla de símbolos (funciones normales)
    func_info = None

    for i in range(len(scope_stack)-1, -1, -1):
        scope = '.'.join(scope_stack[:i+1])

        if func_name in symbol_table.get(scope, {}).get('functions', {}):
            func_info = symbol_table[scope]['functions'][func_name]
            break
    
    # Verificar que la función exista
    if not func_info and func_name not in collection_functions:
        add_semantic_error(f"Error semántico: Función '{func_name}' no declarada.")
        return 'TYPE_ANY'
    
    # Validar argumentos
    if func_info:
        # Es una función normal
        expected_params = func_info['params']
        
        # Validar número de argumentos
        if len(arguments) != len(expected_params):
            add_semantic_error(f"Error semántico: La función '{func_name}' requiere {len(expected_params)} argumentos, pero se proporcionaron {len(arguments)}.")
            return 'TYPE_ANY'
        
        # Validar tipos de argumentos
        for i, arg in enumerate(arguments):
            arg_type = treat_expression(arg)
            expected_type = treat_type(expected_params[i][1])
            check_implicit_coerce(expected_type, arg_type)
        return func_info['return_type']
    
    elif func_name in collection_functions:
        # Validar tipos de elementos en colecciones, deben ser consistentes
        arg_types = []

        for arg in arguments:
            arg_types.append(treat_expression(arg))
        
        for i in range(1, len(arg_types)):
            if not check_implicit_coerce(arg_types[0], arg_types[i]):
                add_semantic_error(f"Error semántico: Los elementos pasados a la función '{func_name}' deben ser del mismo tipo.")
                return 'TYPE_ANY'
        
        # Retornar el tipo de colección apropiado
        if 'list' in func_name.lower():
            return 'TYPE_LIST'
        elif 'set' in func_name.lower():
            return 'TYPE_SET'
        elif 'map' in func_name.lower():
            return 'TYPE_MAP'
    
    return 'TYPE_ANY'

def treat_print_statement(print_tuple):
    '''
    Procesa sentencias print/println y valida los argumentos.
    
    Parámetros:
    - print_tuple: ('print'|'println', [argumentos])
    '''
    kind = print_tuple[0]
    arguments = print_tuple[1]
    
    # Validar que haya al menos un argumento para print/println
    if len(arguments) == 0:
        add_semantic_error(f"Error semántico: '{kind}' requiere al menos un argumento.")
        return
    
    # Procesar cada argumento (Kotlin ya hace toString implícito)
    for arg in arguments:
        treat_expression(arg)

    return 'TYPE_UNIT'

# BRUNO ROMERO

def treat_readline_statement(readline_tuple):
    '''
    Procesa sentencias readLine y valida los argumentos.
    Retorna TYPE_STRING ya que readLine() lee una cadena de texto.
    
    Parámetros:
    - readline_tuple: ('readLine', [argumentos])
    '''
    arguments = readline_tuple[1]
    
    # readLine puede recibir argumentos opcionales (prompt)
    for arg in arguments:
        treat_expression(arg)
    
    return 'TYPE_STRING'

def analyze_program(ast):
    '''
    Analiza un programa completo desde el AST.
    
    Parámetros:
    - ast: ('program', ('package', nombre_paquete), [('import', nombre_import, alias_opcional)...], statements)
    
    Retorna:
    - True si no hay errores, False si hay errores
    '''
    global semantic_errors
    semantic_errors.clear()
    
    # Reiniciar tabla de símbolos y stack
    global symbol_table, scope_stack
    symbol_table = {
        '':{
            'variables': {},
            'constants': {},
            'functions': {},
        },
    }
    scope_stack = ['']
    
    if not ast:
        return False
    
    # Verificar si tiene la estructura de programa completa
    if isinstance(ast, tuple) and ast[0] == 'program':
        package_decl = ast[1]
        import_list = ast[2]
        statements = ast[3]
        
        # Procesar package (solo guardarlo, no requiere validación semántica adicional)
        if package_decl:
            # package_decl es ('package', nombre)
            pass  # El package ya fue validado sintácticamente
        
        # Procesar imports (solo guardarlos, no requiere validación semántica adicional)
        if import_list:
            # import_list es [('import', nombre, alias), ...]
            pass  # Los imports ya fueron validados sintácticamente
        
        # Procesar statements
        if statements:
            for statement in statements:
                treat_statement(statement)
    
    return len(semantic_errors) == 0
