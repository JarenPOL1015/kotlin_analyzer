// Jaren Pazmiño

fun main() {
    // Prueba de Listas y Sets
    val numeros = listOf(1, 2, 3, 4, 5)
    val unicos = setOf(1, 1, 2, 3)
    
    println(numeros)
    println(unicos)

    // Prueba de Tipos Genéricos (Declaración)
    val nombres: List = listOf("Ana", "Luis")
    
    // Prueba de Mapas
    val edades = mapOf("Ana", "Luis")
    
    // Prueba de 'if' con operadores
    if (1 + 1 == 2) {
        println(edades)
    }

    // Prueba de colecciones vacías
    val listaVacia = mutableListOf()
    val mapaVacio = mapOf()

    val a: Float = 1.toFloat()
    val b: Int = 1.5.toInt()
    val c: String = 5.toString()
    val e: Int = "123".toInt()

    // Return path tests
    fun good(): Int { return 42 }
    fun bad(): Int { val x: Int = 1 return x}
}
