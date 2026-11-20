# Revisiones sintácticas antes de las pruebas de API

Dos revisiones intermedias de autoría contenían un `else` pegado a un literal numérico. Se conservaron sus bytes por SHA y se corrigieron antes de iniciar las nuevas pruebas de integración de esas funciones. El AST detectó el defecto del ejecutor 43; no hubo evolución nativa ni resultado científico derivado de él. Los lotes 40 y 42 ya habían concluido cuando se añadió la nueva interfaz al módulo compartido.

Se añadió un preflight sintáctico al supervisor para el worker y la capa de sistema pertinente, después de capturar sus fuentes. No se identifica esa comprobación con validación física ni se eliminan los ensayos fallidos anteriores.
