import itertools

# DAVID SANDOVAL

def make_type_pairings(types):
    return [pair for pair in itertools.combinations_with_replacement(types, 2)]

semantic_errors = []

symbol_table = {
    'types': {
        'TYPE_INT': [],
        'TYPE_DOUBLE': [],
        'TYPE_FLOAT': [],
        'TYPE_LONG': [],
        'TYPE_BOOLEAN': [],
        'TYPE_STRING': [],
        'TYPE_CHAR': [],
        'TYPE_LIST': ['listOf', 'mutableListOf'],
        'TYPE_SET': ['setOf', 'mutableSetOf'],
        'TYPE_MAP': ['mapOf', 'mutableMapOf'],
        'TYPE_UNIT': [],
        'TYPE_ANY': [],
        'RANGE': [],
    }
}

scopes = {
    'global': {
        'variables': {},
        'constants': {},
        'functions': {},
    },
}

scope_stack = ['global']

def get_current_scope():
    return '.'.join(scope_stack)

def enter_scope(scope_name):
    scope_stack.append(scope_name)
    full_scope = get_current_scope()

    if full_scope not in scopes:
        scopes[full_scope] = {
            'variables': {},
            'constants': {},
            'functions': {},
            'parent': '.'.join(scope_stack[:-1])
        }
    
def exit_scope():
    if len(scope_stack) > 1:
        scope_stack.pop()
    
def get_parent_scope(scope_name):
    if scope_name in scopes and 'parent' in scopes[scope_name]:
        return scopes[scope_name]['parent']
    return None

def find_symbol(symbol_name, symbol_type='variables'):
    """
    Busca un símbolo siguiendo la cadena de scopes.
    symbol_type puede ser: 'variables', 'constants', 'functions'
    """
    current_scope = get_current_scope()
    
    # Buscar desde el scope actual hacia arriba
    while current_scope:
        if current_scope in scopes:
            if symbol_name in scopes[current_scope][symbol_type]:
                return scopes[current_scope][symbol_type][symbol_name], current_scope
        # Subir al scope padre
        current_scope = get_parent_scope(current_scope)
    
    return None, None

def is_symbol_declared_in_current_scope(symbol_name, symbol_type='variables'):
    """Verifica si un símbolo está declarado en el scope actual solamente"""
    current_scope = get_current_scope()
    return (current_scope in scopes and symbol_name in scopes[current_scope][symbol_type])

def declare_variable(var_name, var_type, is_constant=False):
    """Declara una variable en el scope actual"""
    current_scope = get_current_scope()
    symbol_type = 'constants' if is_constant else 'variables'
    
    # Verificar si ya existe en el scope actual
    if is_symbol_declared_in_current_scope(var_name, 'variables') or is_symbol_declared_in_current_scope(var_name, 'constants'):
        return False, f"Símbolo '{var_name}' ya declarado en el ámbito actual"
    
    # Declarar la variable
    if current_scope not in scopes:
        scopes[current_scope] = {'variables': {}, 'constants': {}, 'functions': {}}
    
    scopes[current_scope][symbol_type][var_name] = var_type
    return True, None

def declare_function(func_name, return_type, params):
    """Declara una función en el scope actual"""
    current_scope = get_current_scope()
    
    # Verificar si ya existe en el scope actual
    if is_symbol_declared_in_current_scope(func_name, 'functions'):
        return False, f"Función '{func_name}' ya declarada en el ámbito actual"
    
    # Declarar la función
    scopes[current_scope]['functions'][func_name] = {
        'return_type': return_type,
        'params': params
    }
    return True, None

# --- Utilidades Semánticas ---

# Lista de tipos numéricos según precisión
numeric_types = [
    'TYPE_INT',
    'TYPE_LONG',
    'TYPE_FLOAT',
    'TYPE_DOUBLE',
]

# (TYPE_INT, TYPE_INT), (TYPE_INT, TYPE_LONG), ..., (TYPE_DOUBLE, TYPE_DOUBLE)
numeric_type_pairs = make_type_pairings(numeric_types)

def get_top_type_numeric(type_a, type_b):
    if type_a in numeric_types and type_b in numeric_types:
        return max(type_a, type_b, key=lambda t: numeric_types.index(t))
    return None

def type_match(p, type_a, type_b):
    return (p.slice[1].type == type_a and p.slice[3].type == type_b) or (p.slice[1].type == type_b and p.slice[3].type == type_a)

def totaly_match(p, types):
    return any(type_match(p, t1, t2) for t1, t2 in types)

def semantic_check_binary_numeric(p, op1, op2, operator):
    dict_ops = {
        '+': ('add', 'addition'),
        '-': ('sub', 'subtraction'),
        '*': ('mul', 'multiplication'),
        '/': ('div', 'division'),
        '%': ('mod', 'module'),
    }

    # Verificar si el operador es válido
    if operator not in dict_ops:
        return
    
    op_func, op_name = dict_ops[operator]
    # Verificar si los tipos son numericos
    if p.slice[1].type in numeric_types and p.slice[3].type in numeric_types:
        top_type = get_top_type_numeric(p.slice[1].type, p.slice[3].type)
        p.slice[0].type = top_type
        op_full_name = f'{top_type.split("_")[1].lower()}_{op_func}'
        p[0] = (op_full_name, op1, op2)
    
    # Verificar si son strings para concatenación
    elif operator == '+' and p.slice[1].type == 'TYPE_STRING' and p.slice[3].type == 'TYPE_STRING':
        p.slice[0].type = 'TYPE_STRING'
        p[0] = ('string_concat', op1, op2)
    
    # Si no son compatibles
    else:
        semantic_errors.append(f"Error semántico: Tipos incompatibles '{p.slice[1].type}' y '{p.slice[3].type}' para {op_name}")
        p.slice[0].type = 'TYPE_ANY'

# BRUNO ROMERO

def semantic_check_range_operator(p, op1, op2, operator):
    if operator == '..':
        if totaly_match(p, make_type_pairings(['TYPE_INT', 'TYPE_LONG'])):
            p.slice[0].type = f'RANGE'
            p[0] = ('range', op1, op2)
        else:
            semantic_errors.append(f"Error semántico: Tipos incompatibles '{p.slice[1].type}' y '{p.slice[3].type}' para el operador de rango '..'")
            p.slice[0].type = 'TYPE_ANY'

def semantic_check_binary_boolean(p, op1, op2, operator):
    dict_logical_ops = {
        '&&': ('and', 'logical AND'),
        '||': ('or', 'logical OR'),
    }

    dict_relacional_ops = {
        '==': ('eq', 'equality'),
        '!=': ('neq', 'inequality'),
        '>': ('gt', 'greater than'),
        '>=': ('gte', 'greater than or equal to'),
        '<': ('lt', 'less than'),
        '<=': ('lte', 'less than or equal to'),
    }

    if operator in dict_logical_ops:
        op_func, op_name = dict_logical_ops[operator]
        if p.slice[1].type == 'TYPE_BOOLEAN' and p.slice[3].type == 'TYPE_BOOLEAN':
            p.slice[0].type = 'TYPE_BOOLEAN'
            p[0] = (op_func, op1, op2)
        else:
            semantic_errors.append(f"Error semántico: Tipos incompatibles '{p.slice[1].type}' y '{p.slice[3].type}' para {op_name}")
            p.slice[0].type = 'TYPE_ANY'
    elif operator in dict_relacional_ops:
        op_func, op_name = dict_relacional_ops[operator]
        if op_func == 'eq' or op_func == 'neq':
            if totaly_match(p, make_type_pairings(numeric_types + ['TYPE_CHAR']) + [('TYPE_BOOLEAN', 'TYPE_BOOLEAN'), ('TYPE_STRING', 'TYPE_STRING')]):
                p.slice[0].type = 'TYPE_BOOLEAN'
                p[0] = (op_func, op1, op2)
            else:
                semantic_errors.append(f"Error semántico: Tipos incompatibles '{p.slice[1].type}' y '{p.slice[3].type}' para {op_name}")
                p.slice[0].type = 'TYPE_ANY'
        else:
            if totaly_match(p, make_type_pairings(numeric_types + ['TYPE_CHAR'])):
                p.slice[0].type = 'TYPE_BOOLEAN'
                p[0] = (op_func, op1, op2)
            else:
                semantic_errors.append(f"Error semántico: Tipos incompatibles '{p.slice[1].type}' y '{p.slice[3].type}' para {op_name}")
                p.slice[0].type = 'TYPE_ANY'

def semantic_check_unary_boolean(p, op, operator):
    if operator == '!':
        if p.slice[2].type == 'TYPE_BOOLEAN':
            p.slice[0].type = 'TYPE_BOOLEAN'
            p[0] = ('not', op)
        else:
            semantic_errors.append(f"Error semántico: Tipo incompatible '{p.slice[2].type}' para el operador lógico NOT")
            p.slice[0].type = 'TYPE_ANY'

# JAREN PAZMIÑO

def format_type(type_str):
    return "TYPE_" + type_str.upper()

def check_type_compatibility(to_type, from_type, error_msg):
    if to_type == from_type:
        return True
    elif to_type in numeric_types and from_type in numeric_types:
        if check_implicit_coerce(to_type, from_type):
            return True
        else:
            semantic_errors.append(f"Error semántico: Posible pérdida de datos al convertir de '{from_type}' a '{to_type}'")
            return False
    semantic_errors.append(error_msg)
    return False

def check_implicit_coerce(to_type, from_type):
    to_index = numeric_types.index(to_type)
    from_index = numeric_types.index(from_type)
    return to_index >= from_index

def check_type(p, type_index):
    return p.slice[type_index].type in symbol_table['types']


def check_explicit_cast(from_type, to_type):
    """Verifica si un casting explícito desde from_type a to_type es válido.

    Reglas simplificadas:
    - Igual tipo -> válido
    - Numéricos entre sí -> válido (Int <-> Float, etc.)
    - Cualquier numérico -> String -> válido
    - Boolean -> cualquier numérico -> inválido
    - String -> numérico -> inválido (simplificación)
    """
    if from_type == to_type:
        return True
    if from_type == 'TYPE_ANY' or to_type == 'TYPE_ANY':
        return True

    if from_type in numeric_types and to_type in numeric_types:
        return True

    if from_type in numeric_types and to_type == 'TYPE_STRING':
        return True

    if from_type == 'TYPE_BOOLEAN' and to_type in numeric_types:
        return False
    if from_type == 'TYPE_STRING' and to_type in numeric_types:
        return False

    return False


def check_all_paths_return(fun_name, return_type, ast_body):
    """Verifica que todos los caminos posibles dentro de `ast_body` retornen un valor
    cuando `return_type` no es `TYPE_UNIT`. Si no, añade un error semántico.
    `ast_body` puede ser la tupla devuelta por `p_function_body` (statements, return_stmt)
    o directamente una lista/tupla de sentencias.s
    """
    if return_type == 'TYPE_UNIT':
        return True

    def _check_paths_for_return(node):
        if node is None:
            return False

        if isinstance(node, tuple) and len(node) >= 1 and node[0] == 'return':
            return node[1] != 'TYPE_UNIT'

        if isinstance(node, tuple) and len(node) == 2 and isinstance(node[0], list):
            statements, return_stmt = node
            for stmt in statements:
                if isinstance(stmt, tuple) and stmt[0] == 'return':
                    return stmt[1] != 'TYPE_UNIT'
                if isinstance(stmt, tuple) and stmt[0] == 'if-else':
                    if_body = stmt[2] if len(stmt) > 2 else None
                    else_body = stmt[3] if len(stmt) > 3 else None
                    if _check_paths_for_return(if_body) and _check_paths_for_return(else_body):
                        return True
            
            if isinstance(return_stmt, tuple) and return_stmt[0] == 'return' and return_stmt[1] != 'TYPE_UNIT':
                return True
            return False

        if isinstance(node, list):
            for stmt in node:
                if isinstance(stmt, tuple) and stmt[0] == 'return':
                    return stmt[1] != 'TYPE_UNIT'
                if isinstance(stmt, tuple) and stmt[0] == 'if-else':
                    if_body = stmt[2] if len(stmt) > 2 else None
                    else_body = stmt[3] if len(stmt) > 3 else None
                    if _check_paths_for_return(if_body) and _check_paths_for_return(else_body):
                        return True
            return False

        return False

    ok = _check_paths_for_return(ast_body)
    if not ok:
        semantic_errors.append(f"Error semántico: La función '{fun_name}' puede terminar sin retornar un valor de tipo '{return_type}' en algunos caminos.")
    return ok