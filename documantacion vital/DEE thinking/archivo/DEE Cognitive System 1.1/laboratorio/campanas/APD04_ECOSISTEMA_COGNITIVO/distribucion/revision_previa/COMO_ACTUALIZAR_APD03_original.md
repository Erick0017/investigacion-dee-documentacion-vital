# Actualización de la copia de colaboración

El original es hermano de esta carpeta: `../DEE Cognitive System 1.1`. No hay una tarea programada ni conexión a servicios. No se cambió el flujo original ni se interrumpió MI02.

Después de cada campaña, Codex debe guardar y cerrar resultados y estados completos, y **ejecutar `ACTUALIZAR.bat` desde `cognitive sistem`**. No repetir auditorías científicas ni simulaciones para empaquetar.

Para registrar un nuevo cierre y seleccionar nuevos estados:

```bat
ACTUALIZAR.bat --cerrar NOMBRE_CAMPANA --verificacion entregas\VERIFICACION_FINAL_EXTERNA_NOMBRE.json --manual MANUAL_MAESTRO_VIGENTE.docx --vida VIDA_NUEVA
```

El comprobante debe existir realmente y ser posterior al código operativo que se distribuye. `--vida` se puede repetir. Para cortes históricos específicos o descripciones de dominio, editar `actualizaciones/SELECCION.json` con su ruta y hash exactos antes del cierre. No seleccionar un estado por ser el más reciente o tener un éxito aislado. El catálogo identifica cada vida; no fusiona memorias ni promociona automáticamente.

Sin argumentos se refresca el corte registrado. También reconoce un cierre posterior cuando coinciden un comprobante `VERIFICACION_FINAL_EXTERNA...json` y una `CONTINUIDAD_...json` que declaran explícitamente `campaign`, `manual` y `lives`. Si esos campos no están disponibles o el nombre no identifica inequívocamente la campaña, use el comando de registro anterior: no adivina un cierre por encontrar un snapshot nuevo. Copia sólo diferencias por SHA-256 y vuelve a sellar el ZIP. Código, contratos o estados posteriores al cierre bloquean la incorporación: la campaña puede continuar sin interrupción y la entrega anterior se conserva.

El programa utiliza los archivos originales vigentes, nunca los modifica ni los ejecuta. Adapta en la **copia** exclusivamente rutas relativas de motor, estado personal y dependencias. Si cambian esos fragmentos de código, detiene el empaquetado en vez de aplicar una sustitución aproximada. El catálogo completo de capacidades se copia del registro oficial; sus alcances no se elevan.

`entregas/cognitive_sistem_colaborador.zip` es el paquete completo. Una actualización que modifica archivos genera además `cognitive_sistem_actualizacion_FECHA.zip`, con miembros nuevos/cambiados y el manifiesto de la versión resultante. Los anteriores se conservan localmente; no se anidan en entregas nuevas. `entregas/ULTIMA_ENTREGA.json` contiene el hash externo del ZIP.

Para volver a crear el ZIP del corte ya copiado, sin consultar el origen ni incorporar una campaña abierta:

```bat
CREAR_ZIP.bat
```

Equivale a `ACTUALIZAR.bat --solo-zip`. Comprueba los hashes de los archivos gestionados antes de sellarlos. Excluye **todo `entregas/`**, estados personales, instalación desplegada del WHL, cachés, respaldos y conflictos. Mantiene recuperable el ZIP anterior. No ejecuta DEE ni es una nueva validación científica. El Manual Maestro vigente viaja tanto en la raíz como en `documentos/`, con bytes y hash idénticos.

## En el equipo del colaborador

Cierre sus procesos Cognitive antes de actualizar. Sin origen compartido no hay sincronización automática. Después de recibir el ZIP y comprobar el hash por un medio de confianza:

```bat
ACTUALIZAR.bat --aplicar cognitive_sistem_actualizacion_FECHA.zip
```

También acepta el ZIP completo. Verifica todos los miembros, bases del incremental y conflictos antes de sustituirlos. Si alguien modificó un archivo operativo, se detiene: conservar su variante en `trabajo_personal/`, reconciliar explícitamente y volver a aplicar. Los archivos sustituidos tienen respaldo en `actualizaciones/respaldos/`.

Un conflicto conserva el archivo local intacto y guarda la versión recibida más un recibo en `actualizaciones/conflictos/`. No se sobrescribe silenciosamente ninguna variante. La preparación de cambios se realiza en `actualizaciones/temporales/`; sólo se aplica una vez leído el corte completo. Los archivos retirados de una versión se apartan a respaldos únicamente si siguen intactos; una modificación local no se elimina. Esas carpetas de conservación no se envían al colaborador ni se usan como memoria del ente.

**Nunca se escribe ni borra `trabajo_personal/` durante una actualización receptora.** Tampoco se reabre un estado favorable ni se cambia el snapshot de una vida personal. Nuevos cortes aparecen en el catálogo y se importan explícitamente con otra identidad. La instalación generada del motor no viaja en el ZIP; se despliega desde el único WHL congelado.

Privacidad: sólo se copian categorías operativas explícitas. No copiar `.env`, credenciales, claves, directorios del usuario ni entornos completos. Los manuales y fuentes DEE siguen siendo privados, aunque no contengan contraseñas.
