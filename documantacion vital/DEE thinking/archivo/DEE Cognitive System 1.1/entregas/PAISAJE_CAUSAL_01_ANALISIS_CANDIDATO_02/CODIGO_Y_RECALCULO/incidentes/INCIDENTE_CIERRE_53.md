# Comprobación de cierre 53

La primera comprobación del candidato se detuvo al comparar el recálculo profundo con el ordinario: la versión ordinaria no incluía la clave opcional `deep_field_hash_checks`. No hubo diferencias en casos, cabeceras, campos, decodificación ni métricas. La comparación inicial introducía una lista vacía donde antes no existía esa clave.

Se corrigió sólo la exclusión de ese campo adicional en la comparación, conservando los bytes de la primera revisión en el almacén de objetos. No cambian datos primarios, criterios ni física; no se repite simulación.
