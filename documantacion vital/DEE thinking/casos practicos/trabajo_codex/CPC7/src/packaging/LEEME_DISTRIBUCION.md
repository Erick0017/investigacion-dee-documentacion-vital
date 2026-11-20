# Instrumentos de entrega CPC7

Estos módulos son instrumentos de ingeniería y auditoría. No producen respuestas
del participante, no modifican el kernel y no escriben estados físicos en MAIN.

`bundle.py inventory` registra selección positiva y exclusiones. `stage` guarda
gzip deterministas bajo `_delivery`, conservando y comparando los originales.
`build` vuelve a verificar la representación y crea un candidato nuevo, sin
modificar documentos/manifiestos científicos de la raíz. Los manifiestos del ZIP
se calculan virtualmente: `MANIFEST.json` no se incluye a sí mismo ni incluye
`HASHES.sha256`; este último cubre payload y MANIFEST, no a sí mismo. El SHA-256
del ZIP es siempre externo.

Los reportes pequeños que deban conservarse en la entrega pueden colocarse en
`_delivery/proofs/`; se incorporan como `validation/packaging/`. Los demás
temporales, pruebas sintéticas, extracciones y entornos de `_delivery` se excluyen.
Los jobs y sus errores científicos/técnicos permanecen seleccionados.

`clean.py` lee un plan **desde el candidato exacto** y lo extrae fuera del source
en una ruta corta nueva. Crea venv, instala el WHL local no editable sin red,
verifica identidad y ejecuta procesos supervisados secuencialmente. Cada comando
debe empezar por `{python}`. Los placeholders son `{python}`, `{root}` (CPC7 del
ZIP), `{out}` (salidas nuevas) y `{work}` (directorio corto del verificador).

Ejemplo de estructura de plan, que debe adaptarse a las funciones publicadas:

```json
{
  "schema": "CPC7.clean-plan.v1",
  "commands": [
    {
      "id": "referencia_y_main",
      "argv": ["{python}", "-I", "-B", "{root}/ruta/runner_publicado.py", "--output", "{out}/main"],
      "timeout_seconds": 300
    },
    {
      "id": "auditor_posterior",
      "argv": ["{python}", "-I", "-B", "{root}/ruta/comparador_publicado.py", "--actual", "{out}/main", "--output", "{out}/CHECKS.json"]
    }
  ],
  "required_outputs": ["CHECKS.json"],
  "assertions": [{"path": "CHECKS.json", "equals": {"/verified": true}}]
}
```

El ejemplo no anuncia que esos archivos existan: es el contrato de configuración.
Los asserts usan JSON Pointer y sólo se calculan después de acabar las trayectorias.
El plan definitivo debe ejecutar referencia breve, resultado principal/control,
restauración y consulta posterior, más aislamiento y comparadores pertinentes.
La integridad del ZIP y la validación funcional se informan por separado.

Antes del candidato final, probar los comandos con `-I --help` o imports sin MAIN
evita restricciones accidentales de arranque o rutas. La prueba funcional final
no puede sustituirse por ese preflight ni por una prueba de un candidato anterior.

`publish` exige un reporte VERIFIED ligado al SHA exacto del candidato y al plan
incluido. Rehúsa sobrescribir CPC7 existente. Las dos partes binarias se generan
sólo si el ZIP comprimido supera 20 MiB; reconstrucción real comprobada. Se dejan
adyacentes al canónico y los auxiliares en `transporte_CPC7`, sin alterar los de
CPC4/5/6. La publicación se ejecuta sólo con autorización de cierre del responsable.
