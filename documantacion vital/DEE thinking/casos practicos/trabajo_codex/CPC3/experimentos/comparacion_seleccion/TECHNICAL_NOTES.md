# Notas técnicas del frente de comparación y selección

- Primer test de backends: se intentó la sintaxis C++
  `Runtime.set_execution_options`. El binding Python publica la propiedad
  `execution_options`. Se corrigió únicamente el runner técnico; el error y
  su salida se conservaron en `experimentos/supervision`. No se modificó el
  producto, la dinámica ni los resultados científicos.
- El comparador publicado opera sobre un dominio binario de valores
  codificados por dirección. Las cargas 30/100 y 65/65 son cargas de transporte,
  no valores que el comparador numérico esté restando. Los contrastes con
  cargas idénticas y códigos distintos separan dirección de suma. No se afirma
  una comparación aritmética universal.
- El lector lateral emite más de un frente. La primera cadena se identifica
  por traza temporal-espacial, el contexto completo alrededor del encuentro y
  cortes tardíos sobre el producto concreto. No se atribuye parentesco sólo por
  igualdad de carga.
- La comparación no trata la ausencia como un número cero. Si falta un
  participante, el producto queda fuera del código físico completo publicado.
  El resultado externo es un informe explícito de una de dos clases presentes;
  no procede de un timeout Python que escriba ausencia.
- La ruta de selección es fija y físicamente condicionada por la experiencia.
  Al intercambiar qué fuente informa, el aparato mantiene su ruta y puede
  recibir el dato constante no informativo. No se atribuye una política óptima
  aprendida ni reescritura posterior de la memoria basal A/B.
