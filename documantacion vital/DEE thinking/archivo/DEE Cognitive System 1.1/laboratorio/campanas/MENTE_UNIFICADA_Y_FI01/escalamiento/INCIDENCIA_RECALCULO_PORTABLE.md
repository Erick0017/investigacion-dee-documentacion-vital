# Resolución del módulo local de recálculo

El primer staging reprodujo exactamente el recálculoB05, pero el intérprete empaquetado no resolvió el módulo vecino del recálculoB06/B07al ejecutar desde una carpeta externa. No se avanzó física ni cambiaron datos. Se conservaron el staging fallido y los bytes de su constructorR1.

La revisión añade un lanzador que resuelve únicamente los dos scripts congelados presentes en su misma carpeta y agrega explícitamente esa ruta local a sys.path. No instala dependencias ni lee fuentes históricas. Los calculadores científicos ejecutados y sus referencias permanecen intactos; la nueva prueba desde el staging debe verificar identidad de bytes de ambas salidas.
