# Base CAS de evidencia APD04, no sistema operativo

Cada ruta fuente seleccionada está en RUTAS_Y_HASHES.json y remite a un objeto SHA-256 exacto. Los duplicados usan un solo objeto; no se cambió ni omitió ningún byte seleccionado. Esta es una extracción N0 de la base medida, no el informe final, no un ZIP, ni un respaldo de vidas.

Para restaurar en una ruta nueva: python -I -B RESTAURAR_Y_RECALCULAR_CAS.py --out RUTA_NUEVA --proof PRUEBA_NUEVA.json --recalculate

El comando escribe sólo evidencia extraída y recálculos. No lee los históricos, no importa el motor ni continúa una vida. Tres CLIs stdlib verifican R04 adverso, reserva parcial de dos oportunidades y panel ancestral. Sus resultados deben ser byte-idénticos a los archivados. Los demás primarios, negativos y código de la selección también se restauran íntegros; no afirmar que esos tres CLIs cubren todos los contratos científicos.
