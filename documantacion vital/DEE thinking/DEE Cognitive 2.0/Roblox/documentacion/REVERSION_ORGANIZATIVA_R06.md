# Reversión organizativa R06, sólo si se solicita

El archivo de control está fuera del conjunto transferible: `../../archivo/Roblox/otros_historicos/cierre_paquete_R06/`. Allí se conservan `MOVIMIENTOS_R06.jsonl`, `TRES_UNIONES_RETARGET_R06.json`, `CAMBIOS_ENTRADAS_R06.json`, hashes, entradas anteriores y objetos de unión originales. Los originales científicos no se modificaron.

1. Conciliar primero procesos y cambios posteriores legítimos. No sobrescribir ningún destino existente. Comparar todos los hashes del grupo que se pretende revertir con su manifiesto. Si no coinciden, detener sólo ese grupo.
2. Para un grupo físico, comprobar que el origen anterior está ausente, que el destino coincide exactamente en archivos/directorios/hashes y que no contiene estados posteriores únicos. Crear los padres necesarios; trasladar únicamente ese grupo de vuelta con `Move-Item -LiteralPath`, sin comodines y sin cruzar enlaces. Verificar los mismos hashes después. Nunca restaurar SQLite ni snapshots sobre una vida posterior.
3. Las tres uniones autorizadas de `entregas/DEE_ROBLOX_SDK_PILOTO` se revierten sólo coordinadamente con la ubicación física de sus destinos. Conservar la unión nueva como objeto separado; recolocar la unión original preservada sin recorrer ni borrar su destino. No modificar otros consumidores externos.
4. Las entradas documentales anteriores están preservadas en `archivo/Roblox/otros_historicos/entradas_sustituidas_R06`. Restaurarlas sólo si sus consumidores se han revertido también y si el documento actual no tiene cambios posteriores. No restaurar un localizador obsoleto encima de una organización nueva.
5. El payload privado y los destinos diagnósticos son archivos/instalaciones nuevos. No eliminarlos automáticamente como parte de una reversión. No abrir sus mundos ni adoptarlos. Una reversión documental no altera el principal Cognitive, su selección ni su historia.

No se ejecuta este procedimiento en el cierre. El mapa conserva procedencia histórica literal; los localizadores actuales describen la ubicación nueva.
