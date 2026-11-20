# Sesión MENTE_ACUMULATIVA

Este procedimiento pertenece al gestor existente y al Manual Maestro vigente.
No es un chatbot ni un selector externo de la respuesta correcta.

En la distribución, cree una copia con INICIAR.bat mente MI_COPIA
--situaciones JSON. Para continuarla añada --continuar. JSON es una lista:

    [{"contexto":"c1","valores":[24,32],"regimen":"revisado"}]

Para una herramienta real:

    [{"contexto":"c1","valores":[26,34],"regimen":"revisado","herramienta":"trabajadores"}]

El lanzador utiliza el alias de la continuación seleccionada; no reúne recuerdos
de varias vidas. En Python compatible, las operaciones reales son:

    python sistema/gestionar.py mente-estado
    python sistema/gestionar.py bifurcar MA_MAIN_R9 MI_COPIA
    python sistema/gestionar.py mente-sesion --vida MI_COPIA --situaciones JSON
    python sistema/gestionar.py guardar --vida MI_COPIA

JSON admite una a64 situaciones. Cada una requiere contexto (c1,c2,c3,c4)
y dos valores enteros0..64. Herramienta puede ser puertas, trabajadores o
transaccion. Regimen es original o, sólo para c1, revisado.
No cambie lectores ni entregue un crédito como respuesta.

El contexto produce dos entradas crudas iguales por canales comunes.
La organización sólo conserva un criterio mutable: no presuponga que puede
guardar cuatro políticas contextuales. Cada consulta puede aprender por su
consecuencia. Los rechazos, errores, silencios y primeras respuestas se conservan.
El algoritmo de compresión/verificación pertenece a la herramienta.

Las transacciones guardan el archivo preparado y el progreso externo en el
estado operativo. Guardar/cargar no reinicia la organización ni ese progreso.
Una operación interrumpida no autoriza restaurar silenciosamente un pasado.

U0 es un perfil complementario, otra vida nueva: asociaciones reutilizables
con acceso asistido. Su cadena nativa inicial de orden/consulta/acción no tiene
todavía un protocolo de repetición completo demostrado después deT472.
No use el comando R9 anterior para ese perfil.
