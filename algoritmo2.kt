// David Sandoval

fun contadorDePares(): Unit {
    var totalPares = 0

    fun contarHasta(n: Int) {
        for (i in 1..n) {
            if (i % 2 == 0) {
                totalPares = totalPares + 1
                println(i)
            }
        }
    }
}

val d = 0

fun main() {
    contadorDePares()

    fun hola(c: Int, d: Int, e: Int): Int {
        if (c > d) {
            return c
        } else {
            if (d > e) {
                return d
            } else {
                return e
            }
        }
    }

    var limite = readLine()

    if (limite != null) {
        var n = limite
    }
    
    var x = 0
    while (x < 3) {
        println("Repetición: " + x)
        x = x + 1
    
        var mapa = mapOf(1, 2, 3, 4)

        for (i in mapa){
            println(i)
        }
    }
}
