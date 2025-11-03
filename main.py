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
    #Booleanos
    'true': 'LITERAL_TRUE',
    'false': 'LITERAL_FALSE',
    #Estructuras de datos
    'List': 'TYPE_LIST',
    'Set': 'TYPE_SET',
    'Map': 'TYPE_MAP',
}

# --- 2. Lista de Tokens ---

tokens = [
    'ADD_ASSIGN',  # +=
    'SUB_ASSIGN',  # -=
    'MUL_ASSIGN',  # *=
    'DIV_ASSIGN',  # /=
    'MOD_EQUALS', # %=
    'EQ',  # == (Comparación)
    'NEQ',  # !=
    'GTE',  # >=
    'LTE',  # <=
    'SAFE_CALL',  # ?. (Operador de llamada segura)
    'ELVIS',  # ?: (Operador Elvis)
    'ID',  # Identificador
    'NUMBER_INT',  # Entero
    'NUMBER_FLOAT', # Decimal
    'STRING',  # String
    'PLUS',  # +
    'MINUS',  # -
    'TIMES',  # *
    'DIVIDE',  # /
    'MODULO',  # %
    'EQUALS',  # = (Asignación)
    'GT',  # >
    'LT',  # <
    'LPAREN',  # (
    'RPAREN',  # )
    'LBRACE',  # {
    'RBRACE',  # }
    'COLON',  # :
    'COMMA',  # ,
    'DOT',  # .
    'AND',  # &&
    'OR',  # ||
    'NOT',  # !
] + list(reserved.values())

# DAVID SANDOVAL

# --- 3. Definición de Reglas Léxicas ---

# Tokens para operadores con varios símbolos
t_ADD_ASSIGN = r'\+='
t_SUB_ASSIGN = r'-='
t_MUL_ASSIGN = r'\*='
t_DIV_ASSIGN = r'/='
t_MOD_EQUALS = r'%='
t_EQ = r'=='
t_NEQ = r'!='
t_GTE = r'>='
t_LTE = r'<='
t_SAFE_CALL = r'\?\.'
t_ELVIS = r'\?:'

# Tokens para operadores simples
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_EQUALS = r'='
t_MODULO = r'%'
t_GT = r'>'
t_LT = r'<'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_COLON = r':'
t_COMMA = r','
t_DOT = r'\.'

# Tokens para operadores lógicos
t_AND = r'&&'
t_OR = r'\|\|'
t_NOT = r'!'

# Tokens para identificadores y literales
# Esto captura "cualquier cosa entre comillas", manejando comillas escapadas.
def t_STRING(t):
    r'"([^"\\]|\\.)*"'
    t.value = t.value[1:-1]  # Remover las comillas
    return t

# Token para decimales
def t_NUMBER_FLOAT(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

# Token para enteros
def t_NUMBER_INT(t):
    r'\d+'
    t.value = int(t.value)
    return t

# BRUNO ROMERO

# Token para Identificadores (ID) y Palabras Reservadas
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    # Revisa si el ID es una palabra reservada
    t.type = reserved.get(t.value, 'ID')
    return t


# --- 4. Reglas de Ignorar y Errores ---

# Ignorar espacios en blanco, tabulaciones
t_ignore = ' \t'


# Ignorar comentarios de una línea
def t_ignore_COMMENT(t):
    r'//.*'
    pass  # No se retorna valor, se descarta el token


# Ignorar comentarios de múltiples líneas (no anidados)
def t_ignore_MULTILINE_COMMENT(t):
    r'/\*[\s\S]*?\*/'
    pass


# Manejo de números de línea
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# Manejo de errores léxicos
def t_error(t):
    print(f"Error léxico: Caracter ilegal '{t.value[0]}' en la línea {t.lineno}")
    t.lexer.skip(1)

# --- 5. Construcción del Lexer ---
lexer = lex()

# --- 6. Prueba del Lexer ---
if __name__ == "__main__":

    # Código de ejemplo de Kotlin para analizar
    kotlin_code = """
    package com.example

    // Esto es un comentario
    fun main() {
        val x: Int = 10
        var y = x + 5
        val s: String = "Hola Mundo"

        if (y > 10) {
            println(s) // Imprime saludo
        } else {
            val z = y ?: 0
        }
    }
    """

    # Dar el input al lexer
    lexer.input(kotlin_code)

    # Iterar sobre los tokens generados
    print("--- INICIO DE TOKENS ---")
    while True:
        tok = lexer.token()
        if not tok:
            break  # No hay más tokens
        #print(f"Tipo: {tok.type:<15} Valor: {tok.value!r:<20} Línea: {tok.lineno}")
        print(tok)
    print("--- FIN DE TOKENS ---")