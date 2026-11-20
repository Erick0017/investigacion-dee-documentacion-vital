"""DEE v15.0 - Constantes inmutables."""

# Topología
P_KERNEL          = 19658
D_MOORE           = 26
D_EDGES           = 12          # solo aristas de Moore (Manhattan=2, Eucl²=2)
EPSILON_ALIASING  = 1.0 / 1248

# Cinemática
C_DEE             = 1
M_E_DEE           = 1

# Tensiones topológicas
TENSION_ELECTROWEAK = 2.5    # (E+V)/V del cubo unitario
TENSION_STRONG      = 16.0   # (E*V_t)/(V_t-1) del tetraedro (futuro)

# Empaquetado del voxel (64 bits)
MASK_ESTADO = 0x00000000FFFFFFFF      # bits 0-31
MASK_SREG   = 0x0000FFFF00000000      # bits 32-47
MASK_DIRX   = 0x000F000000000000      # bits 48-51
MASK_DIRY   = 0x00F0000000000000      # bits 52-55
MASK_DIRZ   = 0x0F00000000000000      # bits 56-59
MASK_SEM    = 0xF000000000000000      # bits 60-63

# Ontología semántica
SEM_VOID          = 0
SEM_NORMAL        = 1
SEM_ELECTRON_SEED = 2
SEM_PROTON_SEED   = 3
SEM_OBSERVER      = 4
SEM_ORPHAN_BIT    = 5
SEM_HORIZON       = 6