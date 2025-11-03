// David Sandoval

// Programa que calcula el factorial de un número
fun main() {
    val n: Int = 5  // Número del que se quiere el factorial
    var resultado = 1

    // Bucle para calcular el factorial
    for (i in 1..n) {
        resultado *= i
    }

    println("El factorial de $n es $resultado") // Muestra el resultado
}