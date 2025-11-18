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
