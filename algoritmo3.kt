// Bruno Romero

package com.example.test

import java.util.List /* Test de 'import' y 'List' */

fun calcularTotal(precio: Double, cantidad: Int): Double {
    if (cantidad <= 0 || precio < 0.0) {
        return 0.0
    }
    
    var total = precio * cantidad
    total += (total * 0.12) // IVA
    total /= 2
    
    val mapa: Map<String, Any> = mapOf("total" to total)
    
    /* * Bucle while para probar
     * operadores de asignación.
     */
    while (total > 100) {
        total -= 5
        if (total % 2 == 0) {
            total *= 1 // Sin efecto
            total %= 3
        }
    }
    
    val setDeValores = setOf(true, false)
    val s: String = "El total es ${total}" // El lexer verá 'STRING'
    
    // Prueba de errores léxicos
    val error1 = 10 $ 5 // El $ causará un error léxico
    val error2 = 25 # 3 // El # causará un error léxico
}