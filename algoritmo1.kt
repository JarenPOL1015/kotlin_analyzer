// Jaren Pazmiño

fun main() {
    // Prueba de Listas y Sets
    val numeros = listOf(1, 2, 3, 4, 5)
    val unicos = setOf(1, 1, 2, 3)
    
    println(numeros)
    println(unicos)

    // Prueba de Tipos Genéricos (Declaración)
    val nombres: List<String> = listOf("Ana", "Luis")
    
    // Prueba de Mapas
    val edades = mapOf("Ana" to 20, "Luis" to 22)
    
    // Prueba de 'if' con operadores
    if (1 + 1 == 2) {
        println(edades)
    }

    // Prueba de colecciones vacías
    val listaVacia = mutableListOf()
    val mapaVacio = mapOf()
}
