// Jaren Pazmiño

fun sumar(a: Int, b: Int): Int {
    return a + b
}

fun multiplicar(a: Int, b: Int) = a * b

/* ERROR SEMÁNTICO (si se llama): Tipo de retorno incorrecto. */
fun getNombre(id: Int): String {
    if (id == 1) {
        return "Admin"
    } else {
        // ERROR: La función debe retornar 'String', pero se encontró 'Int'.
        return 99
    }
}

/* ERROR SEMÁNTICO (si se llama): Ausencia de retorno. */
fun calcularArea(radio: Double): Double {
    val area = 3.1415 * radio * radio
    // ERROR: La función 'calcularArea' debe retornar un valor.
}


// --- Programa Principal ---

fun main() {
    
    println("Iniciando prueba mixta...")

    // Declaraciones válidas
    val pi: Double = 3.1415
    var contador = 10
    var nombre: String
    nombre = "Juan"
    
    // Expresiones aritméticas y booleanas válidas
    val resultado = 5 + 10 * 2 // 25
    val promedio = (resultado + 5.0) / 2.0 // 15.0
    val esMayor = contador >= 10 // true
    
    // Estructuras de control válidas
    if (esMayor && nombre == "Juan") {
        println("Bloque 'if' válido.")
        contador = contador + 1
    } else {
        println("Bloque 'else' válido.")
    }

    // Bucle válido
    var i = 0
    while (i < 2) {
        println("Bucle 'while' válido, i=$i")
        i = i + 1
    }
    
    // Estructuras de datos válidas
    val numeros = listOf(1, 2, 3)
    val edades = mapOf("Ana" to 20)
    
    // Llamada a función válida
    val suma = sumar(contador, 5)
    println("Suma válida: $suma")
    
    
    // --- 2. SECCIÓN INVÁLIDA (Debe fallar el análisis semántico) ---
    
    println("... Probando errores semánticos ...")

    /* ERROR SEMÁNTICO: Modificación de constante. */
    pi = 3.14     
    
    /* ERROR SEMÁNTICO: Asignación de tipo incompatible. */
    val miNumero: Int = "Esto es un string"
    

    /* ERROR SEMÁNTICO: Uso antes de la declaración. */
    val y = total + 5
    
    
    /* ERROR SEMÁNTICO: Declaración duplicada. */
    val nombre = "Pedro" 
    

    /* ERROR SEMÁNTICO: Condición no booleana. */
    if (contador) { 
        println("Esto no debería compilar")
    }

    /* ERROR SEMÁNTICO: Operador '+' no se puede aplicar a 'Boolean' y 'Int'. */
     val opInvalida = true + 5

}