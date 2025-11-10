// David Sandoval

// Clase que representa un contador de números pares
class Contador {
    var totalPares = 0

    fun contarHasta(n: Int) {
        // Iteramos del 1 al número dado usando un for con rango
        for (i in 1..n) {
            // Si el número es par
            if (i % 2 == 0) {
                totalPares = totalPares + 1
                println(i)  // Imprime el número par
            }
        }
    }
}

// Programa principal
fun main() {
    // Creamos una instancia de la clase
    val c = Contador()

    // Leemos un número desde input
    var limite = readLine()

    // Convertimos el input a entero si no es nulo
    if (limite != null) {
        // Simple casting simulado con expression
        var n = limite.toInt()  // Consideramos que `toInt()` se ignora en el parser
        c.contarHasta(n)
    }

    // Bucle while para mostrar mensaje repetido
    var x = 0
    while (x < 3) {
        println("Repetición: " + x)
        x = x + 1
    }
}
