# Componente experimental de solicitud y retorno

Se reutiliza la física de DEE thinking4.5.0, sin importar implementaciones de CPC3/4/7 ni respuestas guardadas. La selección de la ruta depende de una salida nativa. Los recursos, el sensor y la política geométrica finita son preparados; referencia y contenido del proveedor se forman por experiencias.

`prepare_gradient_tap()` devuelve interfaces y geometría inertes. Antes de crear el mundo, añádelas a una recetaN67. Crea **un único** `OrganizationalWorld`; `InitiativeSession(world, geometry)` sólo asocia la fachada. `acquire_source(signo)` presenta observaciones por puertos declarados. `opportunities()` fija los recursos antes de evolucionar; no consulta la salida de comparación para decidir si introducirlos. No ofrece selección general de qué información hace falta.

El recorrido F2 validado tiene comparación en(50,35,35)70 y tap+X en(52,35,35)72. Una entrada de carga cero gira la emisión hacia(0,+Y,+Z); la fuente adquirida se encuentra77 en(52,40,40). El efecto ocurre81 y el retorno86. `prepare_return_use(g)` en `return_use.py` ofrece, opcionalmente, dos recursos fijos adicionales13 para utilizar el retorno en89. Toda incorporación a otro contexto requiere volver a comprobar rutas, retornos toroidales y función previa.

Las fachadas no limpian puertos ni reinician clocks. Las entradas rechazadas se conservan. `save`/`load` incluyen el mundo y la metadata operativa; cargar no prepara de nuevo. Los cortes sólo se ejecutan en forks explícitos de auditoría, que no regresan al MAIN.

Reproducción desde la raíz extraída y un CPython3.13x64 con el WHL incluido instalado:

```powershell
python src/iniciativa_accion/gradient_pilot.py --config configuraciones/iniciativa/GRADIENT_TAP_F2_CONFIRMACION_Y_RESERVAS.json --case GRAD_R101_NEW_VALUES_OPPOSED_SOURCE --out resultados/reproduccion_F2_NUEVA
python src/iniciativa_accion/return_use.py --config configuraciones/iniciativa/RETURN_USE_F2_EXT01.json --case USE_D01_POSITIVE --out resultados/reproduccion_USE_NUEVA
python tools/resumir_iniciativa.py
```

Cada salida debe ser nueva. Los runners conservan una copia byte-exacta del código que ejecutaron. El recálculo final pertenece al auditor y no alimenta al participante. Véanse `revision/INICIATIVA_ADQUIRIDA_Y_RETORNO.{json,md}` y `configuraciones/iniciativa/INTERFAZ_F2_PARA_INTEGRACION.json`.
