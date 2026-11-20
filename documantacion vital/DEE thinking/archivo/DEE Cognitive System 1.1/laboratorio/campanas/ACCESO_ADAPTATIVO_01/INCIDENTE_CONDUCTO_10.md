# Inversión de dirección no dependiente del comando

El primer compilador de conductos se detuvo antes de evolucionar E1: una transición −X→+X con dos aportes preparados produciría la misma dirección incluso sin el comando. La comprobación la rechazó; no se relaja el criterio para aceptar una ruta que actúe sola. El intento queda guardado en T39752 con su cola parcial y su error.

Se cambió el orden geométrico de ejes para evitar ese giro y se comprueba la admisibilidad de todas las transiciones antes de elegir un conducto. No se cambian firmas de respuesta ni el kernel. La réplica revisada usa otra vida y se contrastará con ausencia de consulta/enseñanza; la desigualdad geométrica por sí sola no demuestra que no existan efectos espurios posteriores.
