"""DEE v16.0 - Orquestador Python."""
import numpy as np
from typing import Dict, Tuple, Any

from . import dee_kernel_v27 as kernel
from . import dee_constants_v27 as K


class UniversoDEE_v27:
    """
    Universo toroidal DEE v16.0 con doble buffer Grid_A/Grid_B.
    
    Diferencias clave con v14.0.2:
      - Sin bordes: el espacio se envuelve sobre sÃ­ mismo (toroide).
      - Cada voxel guarda: estado, s_reg, dir_x/y/z, semÃ¡ntica, tick_local.
      - S_reg solo crece cuando estado > 0 (no mÃ¡s colapso del vacÃ­o).
      - DEMUX restringido a 12 aristas de Moore (no 26 caras+aristas+vÃ©rtices).
      - Bit huÃ©rfano = LSB del estado (no '1' hardcoded).
    """

    def __init__(self, N: int = 48, n_hilos: int = 8):
        if N < 4:
            raise ValueError("N >= 4")
        self.N       = int(N)
        self.n_hilos = int(n_hilos)
        self.total   = self.N ** 3

        # Doble buffer
        self.grid_A  = np.zeros(self.total, dtype=np.uint64)
        self.grid_B  = np.zeros(self.total, dtype=np.uint64)
        self.clock_A = np.zeros(self.total, dtype=np.uint64)
        self.clock_B = np.zeros(self.total, dtype=np.uint64)

        self.tick_global = 0

        print(f"[DEE-v27] Universo toroidal {self.N}^3 = {self.total:,} voxeles "
              f"({self.total * 32 / 1024 / 1024:.2f} MB en doble buffer)")

    # ------------- INYECCIONES -------------
    def sembrar_electron(self, x: int, y: int, z: int,
                          valor_inicial: int = 1,
                          dir_x: int = 0, dir_y: int = 0, dir_z: int = 0) -> int:
        """Bloque 2x2x2. Soporta momento opcional (dir_x/y/z âˆˆ {-1,0,1})."""
        for d in (dir_x, dir_y, dir_z):
            if d < -1 or d > 1:
                raise ValueError(f"dir debe estar en {{-1, 0, 1}}, recibido {d}")
        n = kernel.inyectar_electron(self.grid_A, x, y, z, self.N,
                                       int(valor_inicial),
                                       int(dir_x), int(dir_y), int(dir_z))
        print(f"[v15] Electron sembrado en ({x},{y},{z}) "
              f"momento=({dir_x},{dir_y},{dir_z}): {n} voxeles")
        return n

    def sembrar_proton(self, x: int, y: int, z: int,
                        valor_inicial: int = 1) -> int:
        n = kernel.inyectar_proton(self.grid_A, x, y, z, self.N, int(valor_inicial))
        print(f"[v15] Proton sembrado en ({x},{y},{z}): {n} voxeles")
        return n

    # ------------- EVOLUCIÃ“N -------------
    def tick(self, n_ticks: int = 1, verbose: bool = False) -> Dict[str, Any]:
        ms_total = 0.0
        overflows_total = 0
        for k in range(n_ticks):
            info = kernel.tick_universo_lazy(
                self.grid_A, self.grid_B,
                self.clock_A, self.clock_B,
                self.N, self.n_hilos)
            ms_total        += info.get("elapsed_ms", 0.0)
            overflows_total += info.get("overflows_demux", info.get("overflows", 0))
            # Swap A<->B
            self.grid_A,  self.grid_B  = self.grid_B,  self.grid_A
            self.clock_A, self.clock_B = self.clock_B, self.clock_A
            self.tick_global += 1
            if verbose:
                print(f"  [tick {self.tick_global}] {info.get("elapsed_ms", 0.0):.2f} ms "
                      f"overflows={info.get("overflows_demux", info.get("overflows", 0))}")
        return {
            "ticks_ejecutados":    n_ticks,
            "elapsed_ms_total":    ms_total,
            "elapsed_ms_promedio": ms_total / max(1, n_ticks),
            "overflows_total":     overflows_total,
        }

    # ------------- MEDICIÃ“N -------------
    def censo(self) -> Dict[str, Any]:
        return kernel.censo_semantico(self.grid_A, self.N)

    def medir_energia_total(self) -> int:
        return int(self.censo()["energia_total"])

    def detectar_estructuras(self) -> Dict[str, int]:
        c = self.censo()
        return {
            "electrones":      c.get("sem_2", 0),
            "protones":        c.get("sem_3", 0),
            "normales":        c.get("sem_1", 0),
            "huerfanos":       c.get("sem_5", 0),
            "voxeles_activos": c["voxeles_activos"],
            "energia_total":   c["energia_total"],
        }

    def exportar_slice(self, eje: str = "z", indice: int = -1) -> np.ndarray:
        """Rebanada 2D del estado (solo los bits 0-31 del estado)."""
        if indice < 0:
            indice = self.N // 2
        grid_3d = self.grid_A.reshape(self.N, self.N, self.N)
        # Extraer solo estado (bits 0-31)
        estados_3d = (grid_3d & K.MASK_ESTADO).astype(np.uint32)
        if eje == "z": return estados_3d[:, :, indice]
        if eje == "y": return estados_3d[:, indice, :]
        if eje == "x": return estados_3d[indice, :, :]
        raise ValueError(f"Eje desconocido: {eje}")


    def inyectar_orphan(self, coord, calor=1000):
        """Inyecta voxel huerfano transfiriendo la magnitud al s_reg termico."""
        import numpy as np
        N = self.N
        # Estado = 1. Calor se inyecta en el s_reg (bits 32 a 47). Semantica = 5.
        val = np.uint64(1) | (np.uint64(calor) << 32) | (np.uint64(5) << 60)
        g3d = self.grid_A.reshape(N, N, N)
        g3d[coord[0]%N, coord[1]%N, coord[2]%N] = val
        self.grid_A = g3d.reshape(-1)

    # === v19.0 API de Pointer Aliasing ===

    def coord_to_idx(self, coord):
        x, y, z = coord
        return (x % self.N) * self.N * self.N + (y % self.N) * self.N + (z % self.N)

    
    
    
    