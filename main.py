from ply.lex import lex

# --- 1. Definición de Palabras Reservadas ---

# JAREN PAZMIÑO

reserved = {
    'fun': 'FUN',
    'val': 'VAL',
    'var': 'VAR',
    'if': 'IF',
    'else': 'ELSE',
    'return': 'RETURN',
    'while': 'WHILE',
    'for': 'FOR',
    'class': 'CLASS',
    'interface': 'INTERFACE',
    'package': 'PACKAGE',
    'import': 'IMPORT',
    # Tipos de datos comunes (aunque en Kotlin son clases,
    # a nivel léxico se pueden tratar como palabras clave)
    'Int': 'TYPE_INT',
    'String': 'TYPE_STRING',
    'Boolean': 'TYPE_BOOLEAN',
    'Double': 'TYPE_DOUBLE',
    'Any': 'TYPE_ANY',
    'Unit': 'TYPE_UNIT',
}

# --- 2. Lista de Tokens ---

tokens = [
             'ID',  # Identificador
             'NUMBER_INT',  # Entero
             'STRING',  # String
             'PLUS',  # +
             'MINUS',  # -
             'TIMES',  # *
             'DIVIDE',  # /
             'EQUALS',  # = (Asignación)
             'EQ',  # == (Comparación)
             'NEQ',  # !=
             'GT',  # >
             'LT',  # <
             'GTE',  # >=
             'LTE',  # <=
             'LPAREN',  # (
             'RPAREN',  # )
             'LBRACE',  # {
             'RBRACE',  # }
             'COLON',  # :
             'COMMA',  # ,
             'DOT',  # .
             'SAFE_CALL',  # ?. (Operador de llamada segura)
             'ELVIS',  # ?: (Operador Elvis)
         ] + list(reserved.values())
