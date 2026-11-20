// ==============================================================================
// dee_kernel_v24.cpp - DEE Universe Kernel v25.0 (FISICA PURA SIN ALIAS)
// ==============================================================================
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include <cstdint>
#include <cstring>
#include <cmath>
#include <cstdlib>
#include <vector>
#include <thread>
#include <atomic>
#include <mutex>
#include <climits>
#include <random>
#include <algorithm>
#include <string>

namespace py = pybind11;

// =========================================================================
// SECCION 1: CONSTANTES AUTO-DERIVADAS
// =========================================================================
static constexpr double K_LIMIT = 9.887;
static constexpr double V_NODES = 8.0;
static constexpr double E_EDGES = 12.0;
static constexpr double F_FACES = 6.0;
static constexpr double D_MOORE = 26.0;
static constexpr double V_TETRA = 4.0;

static constexpr double TENSION_ELECTROWEAK = (D_MOORE - F_FACES) / V_NODES;
static constexpr double TENSION_STRONG = (E_EDGES * V_TETRA) / (V_TETRA - 1.0);
static constexpr int UMBRAL_CRISTALIZACION = (int)(K_LIMIT * K_LIMIT * K_LIMIT);
static constexpr uint64_t P_KERNEL = 19665ULL;
static constexpr int UMBRAL_FUSION = 19665;
static constexpr int TTL_ORFAN = 194422;

static constexpr int ORPHAN_TTL = 9;
static constexpr int COMPLETE_CUBE_VECINOS = 7;
static constexpr int XNOR_MIN_ACTIVE = 8;
static constexpr int XNOR_PAIRS_TOTAL = 13;

static constexpr uint8_t SEM_VOID = 0;
static constexpr uint8_t SEM_NORMAL = 1;
static constexpr uint8_t SEM_ELECTRON_SEED = 2;
static constexpr uint8_t SEM_PROTON_SEED = 3;
static constexpr uint8_t SEM_OBSERVER = 4;
static constexpr uint8_t SEM_ORPHAN_BIT = 5;
static constexpr uint8_t SEM_HORIZON = 6;
static constexpr uint8_t SEM_NACIDO_XNOR = 7;

static constexpr int SHIFT_SREG = 32;
static constexpr int SHIFT_DIRX = 48;
static constexpr int SHIFT_DIRY = 52;
static constexpr int SHIFT_DIRZ = 56;
static constexpr int SHIFT_SEM = 60;
static constexpr uint64_t MASK_ESTADO = 0xFFFFFFFFULL;

// =========================================================================
// SECCION 2: TABLAS DE VECINDADES
// =========================================================================
static const int MOORE_DXYZ[26][3] = {
    {-1,-1,-1}, {-1,-1,0}, {-1,-1,1}, {-1,0,-1}, {-1,0,0}, {-1,0,1},
    {-1,1,-1},  {-1,1,0},  {-1,1,1},  {0,-1,-1}, {0,-1,0}, {0,-1,1},
    {0,0,-1},              {0,0,1},   {0,1,-1},  {0,1,0},  {0,1,1},
    {1,-1,-1},  {1,-1,0},  {1,-1,1},  {1,0,-1},  {1,0,0},  {1,0,1},
    {1,1,-1},   {1,1,0},   {1,1,1}
};

static const int EDGE_DXYZ[12][3] = {
    {1,1,0}, {1,-1,0}, {-1,1,0}, {-1,-1,0},
    {1,0,1}, {1,0,-1}, {-1,0,1}, {-1,0,-1},
    {0,1,1}, {0,1,-1}, {0,-1,1}, {0,-1,-1}
};

static const int XNOR_PAIRS[13][3] = {
    {1,0,0}, {0,1,0}, {0,0,1},
    {1,1,0}, {1,-1,0}, {1,0,1}, {1,0,-1},
    {0,1,1}, {0,1,-1},
    {1,1,1}, {1,1,-1}, {1,-1,1}, {1,-1,-1}
};

static const int TET_PATTERNS[8][4][3] = {
    {{1,0,0}, {0,1,0}, {0,0,1}, {1,1,1}},
    {{-1,0,0}, {0,1,0}, {0,0,1}, {-1,1,1}},
    {{1,0,0}, {0,-1,0}, {0,0,1}, {1,-1,1}},
    {{1,0,0}, {0,1,0}, {0,0,-1}, {1,1,-1}},
    {{-1,0,0}, {0,-1,0}, {0,0,1}, {-1,-1,1}},
    {{-1,0,0}, {0,1,0}, {0,0,-1}, {-1,1,-1}},
    {{1,0,0}, {0,-1,0}, {0,0,-1}, {1,-1,-1}},
    {{-1,0,0}, {0,-1,0}, {0,0,-1}, {-1,-1,-1}}
};

// =========================================================================
// SECCION 3: BIT-PACKING
// =========================================================================
static inline uint32_t get_estado(uint64_t v) { return (uint32_t)(v & MASK_ESTADO); }
static inline uint16_t get_s_reg(uint64_t v) { return (uint16_t)((v >> SHIFT_SREG) & 0xFFFFULL); }
static inline int get_dir_x(uint64_t v) {
    int8_t r = (int8_t)((v >> SHIFT_DIRX) & 0xFULL);
    if (r & 0x8) r |= (int8_t)0xF0;
    return (int)r;
}
static inline int get_dir_y(uint64_t v) {
    int8_t r = (int8_t)((v >> SHIFT_DIRY) & 0xFULL);
    if (r & 0x8) r |= (int8_t)0xF0;
    return (int)r;
}
static inline int get_dir_z(uint64_t v) {
    int8_t r = (int8_t)((v >> SHIFT_DIRZ) & 0xFULL);
    if (r & 0x8) r |= (int8_t)0xF0;
    return (int)r;
}
static inline uint8_t get_sem(uint64_t v) { return (uint8_t)((v >> SHIFT_SEM) & 0xFULL); }

static inline uint64_t pack_voxel(uint32_t e, uint16_t s, int dx, int dy, int dz, uint8_t sem) {
    return (uint64_t)e
         | ((uint64_t)s << SHIFT_SREG)
         | (((uint64_t)(dx & 0xF)) << SHIFT_DIRX)
         | (((uint64_t)(dy & 0xF)) << SHIFT_DIRY)
         | (((uint64_t)(dz & 0xF)) << SHIFT_DIRZ)
         | (((uint64_t)(sem & 0xF)) << SHIFT_SEM);
}

static inline bool exists(uint64_t v) { return get_estado(v) > 0; }
static inline bool is_alive_for_rule(uint64_t v) {
    return (get_estado(v) > 0) && (get_sem(v) != SEM_ORPHAN_BIT);
}

// =========================================================================
// SECCION 4: INDEXADO TOROIDAL
// =========================================================================
static inline int wrap(int v, int N) {
    int r = v % N;
    return (r < 0) ? r + N : r;
}
static inline size_t idx3d(int x, int y, int z, int N) {
    return ((size_t)x * N + (size_t)y) * N + (size_t)z;
}

// =========================================================================
// SECCION 5: HELPERS FISICOS
// =========================================================================
static bool tiene_firma_tetraedrica(const uint64_t* gA, int x, int y, int z, int N) {
    for (int p = 0; p < 8; ++p) {
        bool all_alive = true;
        for (int v = 0; v < 4; ++v) {
            int nx = wrap(x + TET_PATTERNS[p][v][0], N);
            int ny = wrap(y + TET_PATTERNS[p][v][1], N);
            int nz = wrap(z + TET_PATTERNS[p][v][2], N);
            size_t nidx = idx3d(nx, ny, nz, N);
            if (!is_alive_for_rule(gA[nidx])) { all_alive = false; break; }
        }
        if (all_alive) return true;
    }
    return false;
}

static bool verificar_genesis_xnor(const uint64_t* gA, int x, int y, int z, int N) {
    int symmetric = 0, active = 0;
    for (int i = 0; i < XNOR_PAIRS_TOTAL; ++i) {
        int dx = XNOR_PAIRS[i][0], dy = XNOR_PAIRS[i][1], dz = XNOR_PAIRS[i][2];
        bool p_active = is_alive_for_rule(gA[idx3d(wrap(x+dx,N), wrap(y+dy,N), wrap(z+dz,N), N)]);
        bool n_active = is_alive_for_rule(gA[idx3d(wrap(x-dx,N), wrap(y-dy,N), wrap(z-dz,N), N)]);
        if (p_active == n_active) ++symmetric;
        if (p_active) ++active;
        if (n_active) ++active;
    }
    return (symmetric == XNOR_PAIRS_TOTAL) && (active >= XNOR_MIN_ACTIVE);
}

static int demux_edge_min(const uint64_t* gA, int x, int y, int z, int N) {
    int best = -1;
    uint32_t min_state = UINT32_MAX;
    for (int k = 0; k < 12; ++k) {
        int nx = wrap(x + EDGE_DXYZ[k][0], N);
        int ny = wrap(y + EDGE_DXYZ[k][1], N);
        int nz = wrap(z + EDGE_DXYZ[k][2], N);
        size_t nidx = idx3d(nx, ny, nz, N);
        uint32_t e = get_estado(gA[nidx]);
        if (e < min_state) { min_state = e; best = k; }
    }
    return best;
}

static uint64_t buscar_fuente_demux(const uint64_t* gA, int x, int y, int z, int N) {
    // v26-SYM1: reducer simetrico para TODAS las fuentes direccionales que apuntan al destino.
    // - 0 fuentes: conserva el comportamiento nulo.
    // - 1 fuente: conserva EXACTAMENTE el raw de v25.
    // - >1 fuentes: suma s_reg con la misma cota P_KERNEL-1 ya usada por DEMUX,
    //   y compone la direccion mediante signo de la suma vectorial.
    // La reduccion es conmutativa y no depende del indice de MOORE_DXYZ.
    int count = 0;
    uint64_t only_source = 0;
    uint32_t sum_sreg = 0;
    int sum_dx = 0, sum_dy = 0, sum_dz = 0;

    for (int k = 0; k < 26; ++k) {
        int nx = wrap(x + MOORE_DXYZ[k][0], N);
        int ny = wrap(y + MOORE_DXYZ[k][1], N);
        int nz = wrap(z + MOORE_DXYZ[k][2], N);
        size_t nidx = idx3d(nx, ny, nz, N);
        uint64_t nv = gA[nidx];
        int ndx = get_dir_x(nv), ndy = get_dir_y(nv), ndz = get_dir_z(nv);
        if (ndx == 0 && ndy == 0 && ndz == 0) continue;
        if (wrap(nx + ndx, N) == x && wrap(ny + ndy, N) == y && wrap(nz + ndz, N) == z) {
            ++count;
            only_source = nv;
            sum_sreg += static_cast<uint32_t>(get_s_reg(nv));
            sum_dx += ndx;
            sum_dy += ndy;
            sum_dz += ndz;
        }
    }

    if (count == 0) return 0;
    if (count == 1) return only_source;

    const uint32_t cap = static_cast<uint32_t>(P_KERNEL - 1);
    if (sum_sreg > cap) sum_sreg = cap;
    const int out_dx = (sum_dx > 0) ? 1 : ((sum_dx < 0) ? -1 : 0);
    const int out_dy = (sum_dy > 0) ? 1 : ((sum_dy < 0) ? -1 : 0);
    const int out_dz = (sum_dz > 0) ? 1 : ((sum_dz < 0) ? -1 : 0);
    return pack_voxel(1, static_cast<uint16_t>(sum_sreg), out_dx, out_dy, out_dz, SEM_NORMAL);
}

// =========================================================================
// SECCION 6: actualizar_voxel (FISICA PURA SIN ALIAS)
// =========================================================================
static void actualizar_voxel(
    const uint64_t* gA, const uint64_t* clkA,
    uint64_t* gB, uint64_t* clkB,
    std::atomic<uint32_t>* delta_demux,
    std::atomic<uint64_t>* overflow_count,
    std::atomic<uint64_t>* genesis_count,
    int x, int y, int z, int N)
{
    const size_t i = idx3d(x, y, z, N);
    const uint64_t v = gA[i];

    const uint32_t estado = get_estado(v);
    const uint16_t s_reg = get_s_reg(v);
    const uint8_t sem = get_sem(v);
    const uint64_t tick = clkA[i];

    if (sem == SEM_OBSERVER) { gB[i] = v; clkB[i] = tick + 1; return; }

    int n_active = 0;
    int sum_x = 0, sum_y = 0, sum_z = 0;
    int grad_x = 0, grad_y = 0, grad_z = 0;
    int suma_s_reg_vecinos = 0;
    uint8_t sem_heredada = SEM_NORMAL;
    bool tiene_vecino_vivo = false;
    bool hay_vecino_orphan = false;
    int max_sreg = 0;
    int max_off_x = 0, max_off_y = 0, max_off_z = 0;

    for (int k_v = 0; k_v < 26; ++k_v) {
        int nx = wrap(x + MOORE_DXYZ[k_v][0], N);
        int ny = wrap(y + MOORE_DXYZ[k_v][1], N);
        int nz = wrap(z + MOORE_DXYZ[k_v][2], N);
        size_t nidx = idx3d(nx, ny, nz, N);
        uint64_t nv = gA[nidx];

        if (get_sem(nv) == SEM_ORPHAN_BIT) hay_vecino_orphan = true;

        if (is_alive_for_rule(nv)) {
            n_active++;
            sum_x += get_dir_x(nv);
            sum_y += get_dir_y(nv);
            sum_z += get_dir_z(nv);
            if (!tiene_vecino_vivo) {
                sem_heredada = get_sem(nv);
                tiene_vecino_vivo = true;
            }
        }
        if (exists(nv)) {
            int s_v = (int)get_s_reg(nv);
            suma_s_reg_vecinos += s_v;
            grad_x -= MOORE_DXYZ[k_v][0] * s_v;
            grad_y -= MOORE_DXYZ[k_v][1] * s_v;
            grad_z -= MOORE_DXYZ[k_v][2] * s_v;
        }
        int s_v_total = (int)get_s_reg(nv);
        if (s_v_total > max_sreg) {
            max_sreg = s_v_total;
            max_off_x = MOORE_DXYZ[k_v][0];
            max_off_y = MOORE_DXYZ[k_v][1];
            max_off_z = MOORE_DXYZ[k_v][2];
        }
    }

    int grad_mag = std::abs(grad_x) + std::abs(grad_y) + std::abs(grad_z);

    // =========================================================
    // REGLA DEL VACIO
    // =========================================================
    if (estado == 0) {
        if (tiene_vecino_vivo && (grad_mag / P_KERNEL) >= UMBRAL_CRISTALIZACION && !hay_vecino_orphan) {
            int ndx = (grad_x > 0) ? 1 : ((grad_x < 0) ? -1 : 0);
            int ndy = (grad_y > 0) ? 1 : ((grad_y < 0) ? -1 : 0);
            int ndz = (grad_z > 0) ? 1 : ((grad_z < 0) ? -1 : 0);
            gB[i] = pack_voxel(1, 0, ndx, ndy, ndz, sem_heredada);
            clkB[i] = tick + 1;
            genesis_count->fetch_add(1, std::memory_order_relaxed);
            return;
        }

        if (verificar_genesis_xnor(gA, x, y, z, N)) {
            gB[i] = pack_voxel(1, 1, 0, 0, 0, SEM_NACIDO_XNOR);
            clkB[i] = tick + 1;
            genesis_count->fetch_add(1, std::memory_order_relaxed);
            return;
        }

        uint64_t fuente = buscar_fuente_demux(gA, x, y, z, N);
        if (fuente != 0) {
            gB[i] = pack_voxel(1, get_s_reg(fuente), get_dir_x(fuente), get_dir_y(fuente), get_dir_z(fuente), SEM_NORMAL);
            clkB[i] = tick + 1;
            return;
        }

        if (max_sreg > 0) {
            gB[i] = pack_voxel(0, 0, 0, 0, 0, SEM_VOID);
            clkB[i] = tick + 1;
            return;
        }

        gB[i] = pack_voxel(0, 0, 0, 0, 0, SEM_VOID);
        clkB[i] = tick + 1;
        return;
    }

    // =========================================================
    // REGLA DE LA MATERIA (Friccion Geometrica)
    // =========================================================
    bool hadron = tiene_firma_tetraedrica(gA, x, y, z, N);
    bool incomplete = (n_active < COMPLETE_CUBE_VECINOS);
    double T_local = (hadron && incomplete) ? TENSION_STRONG : TENSION_ELECTROWEAK;
    double rho_eff = ((double)n_active * T_local) / D_MOORE;
    int rule_value = (int)std::floor(rho_eff + 0.5);

    if (rule_value == 0) {
        gB[i] = pack_voxel(0, 0, 0, 0, 0, SEM_VOID);
        clkB[i] = tick + 1;
        return;
    }

    bool simetria_vectorial = (sum_x == 0 && sum_y == 0 && sum_z == 0);
    bool write_protected = (n_active >= 7) && simetria_vectorial; 

    int prov_total = (int)s_reg;

    if (!write_protected) {
        int anclajes_faltantes = 8 - n_active;
        if (anclajes_faltantes > 0 && anclajes_faltantes <= 8) {
            int periodo_ticks = 782 / anclajes_faltantes;
            if (periodo_ticks < 1) periodo_ticks = 1;
            if ((tick % (uint64_t)periodo_ticks) == 0) {
                prov_total += 1;
            }
        }
    }

    if (prov_total >= UMBRAL_FUSION) {
        int s_min_vecino = INT_MAX;
        int best_offset_x = 0, best_offset_y = 0, best_offset_z = 0;
        bool encontro_vecino_abierto = false;

        for (int k_imp = 0; k_imp < 26; ++k_imp) {
            int nx_i = wrap(x + MOORE_DXYZ[k_imp][0], N);
            int ny_i = wrap(y + MOORE_DXYZ[k_imp][1], N);
            int nz_i = wrap(z + MOORE_DXYZ[k_imp][2], N);
            size_t nidx_i = idx3d(nx_i, ny_i, nz_i, N);
            uint64_t nv_i = gA[nidx_i];

            uint8_t nsem = get_sem(nv_i);
            if (nsem == SEM_ORPHAN_BIT) continue; 

            int n_vecino_act = 0;
            for (int kk = 0; kk < 26; ++kk) {
                int nnx = wrap(nx_i + MOORE_DXYZ[kk][0], N);
                int nny = wrap(ny_i + MOORE_DXYZ[kk][1], N);
                int nnz = wrap(nz_i + MOORE_DXYZ[kk][2], N);
                size_t nnidx = idx3d(nnx, nny, nnz, N);
                if (is_alive_for_rule(gA[nnidx])) n_vecino_act++;
            }
            
            if (n_vecino_act < 8) {
                int s_v = (int)get_s_reg(nv_i);
                if (s_v < s_min_vecino) {
                    s_min_vecino = s_v;
                    best_offset_x = MOORE_DXYZ[k_imp][0];
                    best_offset_y = MOORE_DXYZ[k_imp][1];
                    best_offset_z = MOORE_DXYZ[k_imp][2];
                    encontro_vecino_abierto = true;
                }
            }
        }

        if (encontro_vecino_abierto) {
            int tx = wrap(x + best_offset_x, N);
            int ty = wrap(y + best_offset_y, N);
            int tz = wrap(z + best_offset_z, N);
            delta_demux[idx3d(tx, ty, tz, N)].fetch_add(1, std::memory_order_relaxed);
            overflow_count->fetch_add(1, std::memory_order_relaxed);
            prov_total = 0; // Reset
        }
    }

    // Anclaje de Momento. Solo bosones o materia en movimiento empujan.
    int ndx = 0, ndy = 0, ndz = 0;
    if (get_dir_x(v) != 0 || get_dir_y(v) != 0 || get_dir_z(v) != 0 || sem == SEM_ORPHAN_BIT) {
        ndx = (grad_x > 0) ? 1 : ((grad_x < 0) ? -1 : 0);
        ndy = (grad_y > 0) ? 1 : ((grad_y < 0) ? -1 : 0);
        ndz = (grad_z > 0) ? 1 : ((grad_z < 0) ? -1 : 0);
    }

    gB[i] = pack_voxel((uint32_t)rule_value, (uint16_t)prov_total, ndx, ndy, ndz, (sem == SEM_VOID) ? SEM_NORMAL : sem);
    clkB[i] = tick + 1;
}

// =========================================================================
// SECCION 7: APLICAR DEMUX
// =========================================================================
static void aplicar_demux(uint64_t* gB, std::atomic<uint32_t>* delta_demux, size_t total) {
    for (size_t i = 0; i < total; ++i) {
        uint32_t d = delta_demux[i].exchange(0, std::memory_order_relaxed);
        if (d == 0) continue;
        uint64_t cur = gB[i];
        uint8_t cur_sem = get_sem(cur);
        if (cur_sem == SEM_OBSERVER) continue;
        if (cur_sem == SEM_ORPHAN_BIT) {
            gB[i] = pack_voxel((uint32_t)TTL_ORFAN, 0, 0, 0, 0, SEM_ORPHAN_BIT);
        } else if (get_estado(cur) == 0) {
            gB[i] = pack_voxel(1, 0, 0, 0, 0, SEM_NORMAL);
        } else {
            uint16_t s = get_s_reg(cur);
            uint16_t new_s = (s + d < (uint16_t)P_KERNEL) ? (uint16_t)(s + d) : (uint16_t)(P_KERNEL - 1);
            gB[i] = pack_voxel(get_estado(cur), new_s,
                               get_dir_x(cur), get_dir_y(cur), get_dir_z(cur),
                               cur_sem);
        }
    }
}

// =========================================================================
// SECCION 8: tick_universo
// =========================================================================
static py::dict tick_universo(
    py::array_t<uint64_t> grid_A,
    py::array_t<uint64_t> grid_B,
    py::array_t<uint64_t> clock_A,
    py::array_t<uint64_t> clock_B,
    int N, int n_hilos)
{
    auto bufA = grid_A.request();
    auto bufB = grid_B.request();
    auto bufCA = clock_A.request();
    auto bufCB = clock_B.request();

    uint64_t* gA = (uint64_t*)bufA.ptr;
    uint64_t* gB = (uint64_t*)bufB.ptr;
    uint64_t* clkA = (uint64_t*)bufCA.ptr;
    uint64_t* clkB = (uint64_t*)bufCB.ptr;

    size_t total = (size_t)N * N * N;

    std::vector<std::atomic<uint32_t>> delta_demux(total);
    for (size_t i = 0; i < total; ++i) delta_demux[i].store(0);
    std::atomic<uint64_t> overflow_count(0);
    std::atomic<uint64_t> genesis_count(0);

    std::vector<std::thread> hilos;
    hilos.reserve(n_hilos);
    int slabs_per_thread = (N + n_hilos - 1) / n_hilos;

    for (int t = 0; t < n_hilos; ++t) {
        int x_ini = t * slabs_per_thread;
        int x_fin = std::min(x_ini + slabs_per_thread, N);
        if (x_ini >= N) break;
        hilos.emplace_back([=, &delta_demux, &overflow_count, &genesis_count]() {
            for (int x = x_ini; x < x_fin; ++x) {
                for (int y = 0; y < N; ++y) {
                    for (int z = 0; z < N; ++z) {
                        actualizar_voxel(gA, clkA, gB, clkB,
                                         delta_demux.data(),
                                         &overflow_count, &genesis_count,
                                         x, y, z, N);
                    }
                }
            }
        });
    }
    for (auto& th : hilos) th.join();

    aplicar_demux(gB, delta_demux.data(), total);
    std::memcpy(gA, gB, total * sizeof(uint64_t));
    std::memcpy(clkA, clkB, total * sizeof(uint64_t));

    py::dict info;
    info["overflows"] = overflow_count.load();
    info["genesis"] = genesis_count.load();
    return info;
}

// =========================================================================
// SECCION 9: FUNCIONES DE INYECCION
// =========================================================================
static int inyectar_electron(py::array_t<uint64_t> grid, int x, int y, int z, int N,
                              int valor_inicial, int dx_m, int dy_m, int dz_m) {
    auto buf = grid.request();
    uint64_t* g = (uint64_t*)buf.ptr;
    int count = 0;
    for (int px = 0; px < 2; ++px) {
        for (int py_ = 0; py_ < 2; ++py_) {
            for (int pz = 0; pz < 2; ++pz) {
                int ax = wrap(x + px, N), ay = wrap(y + py_, N), az = wrap(z + pz, N);
                g[idx3d(ax, ay, az, N)] = pack_voxel((uint32_t)valor_inicial, 0,
                                                     dx_m, dy_m, dz_m, SEM_ELECTRON_SEED);
                count++;
            }
        }
    }
    return count;
}

static int inyectar_proton(py::array_t<uint64_t> grid, int x, int y, int z, int N) {
    auto buf = grid.request();
    uint64_t* g = (uint64_t*)buf.ptr;
    int count = 0;
    for (int px = -1; px <= 1; ++px) {
        for (int py_ = -1; py_ <= 1; ++py_) {
            for (int pz = -1; pz <= 1; ++pz) {
                int ax = wrap(x + px, N), ay = wrap(y + py_, N), az = wrap(z + pz, N);
                g[idx3d(ax, ay, az, N)] = pack_voxel(1, 0, 0, 0, 0, SEM_PROTON_SEED);
                count++;
            }
        }
    }
    return count;
}

static int sembrar_ruido(py::array_t<uint64_t> grid, int N, double densidad, int semilla) {
    auto buf = grid.request();
    uint64_t* g = (uint64_t*)buf.ptr;
    std::mt19937_64 rng((uint64_t)semilla);
    std::uniform_real_distribution<double> dist(0.0, 1.0);
    size_t total = (size_t)N * N * N;
    int count = 0;
    for (size_t i = 0; i < total; ++i) {
        if (dist(rng) < densidad) {
            g[i] = pack_voxel((uint32_t)ORPHAN_TTL, 0, 0, 0, 0, SEM_ORPHAN_BIT);
            count++;
        }
    }
    return count;
}


// =========================================================================
// DEE v25-LAZY SAFE SCAN
// MISMA FISICA que tick_universo denso.
// Solo cambia QUE voxeles llaman a actualizar_voxel.
// =========================================================================
static py::dict tick_universo_lazy(
    py::array_t<uint64_t> grid_A,
    py::array_t<uint64_t> grid_B,
    py::array_t<uint64_t> clock_A,
    py::array_t<uint64_t> clock_B,
    int N, int n_hilos)
{
    auto bufA = grid_A.request();
    auto bufB = grid_B.request();
    auto bufCA = clock_A.request();
    auto bufCB = clock_B.request();

    uint64_t* gA = (uint64_t*)bufA.ptr;
    uint64_t* gB = (uint64_t*)bufB.ptr;
    uint64_t* clkA = (uint64_t*)bufCA.ptr;
    uint64_t* clkB = (uint64_t*)bufCB.ptr;

    const size_t total = (size_t)N * (size_t)N * (size_t)N;

    // Estado por defecto de toda coordenada: conservar grid y avanzar clock.
    // Toda celda raw!=0 sera candidata y se recalculara con actualizar_voxel.
    std::memcpy(gB, gA, total * sizeof(uint64_t));
    for (size_t i = 0; i < total; ++i) {
        clkB[i] = clkA[i] + 1ULL;
    }

    // Candidatos = toda celda raw!=0 + halo Moore de radio 1.
    std::vector<uint8_t> candidate(total, 0);
    std::vector<size_t> active_raw;
    active_raw.reserve(1024);

    for (size_t i = 0; i < total; ++i) {
        if (gA[i] != 0ULL) active_raw.push_back(i);
    }

    const size_t NN = (size_t)N * (size_t)N;
    for (size_t idx : active_raw) {
        candidate[idx] = 1;
        int x = (int)(idx / NN);
        size_t rem = idx % NN;
        int y = (int)(rem / (size_t)N);
        int z = (int)(rem % (size_t)N);

        for (int k = 0; k < 26; ++k) {
            int nx = wrap(x + MOORE_DXYZ[k][0], N);
            int ny = wrap(y + MOORE_DXYZ[k][1], N);
            int nz = wrap(z + MOORE_DXYZ[k][2], N);
            candidate[idx3d(nx, ny, nz, N)] = 1;
        }
    }

    std::vector<size_t> work;
    work.reserve(active_raw.size() * 8 + 64);
    for (size_t i = 0; i < total; ++i) {
        if (candidate[i]) work.push_back(i);
    }

    // Conservamos DEMUX exactamente; solo reducimos las llamadas a actualizar_voxel.
    std::vector<std::atomic<uint32_t>> delta_demux(total);
    for (size_t i = 0; i < total; ++i) {
        delta_demux[i].store(0, std::memory_order_relaxed);
    }
    std::atomic<uint64_t> overflow_count(0);
    std::atomic<uint64_t> genesis_count(0);

    int threads = std::max(1, n_hilos);
    size_t nwork = work.size();
    size_t chunk = (nwork + (size_t)threads - 1) / (size_t)threads;

    std::vector<std::thread> hilos;
    hilos.reserve((size_t)threads);

    for (int t = 0; t < threads; ++t) {
        size_t begin = (size_t)t * chunk;
        size_t end = std::min(begin + chunk, nwork);
        if (begin >= end) break;

        hilos.emplace_back([=, &work, &delta_demux,
                            &overflow_count, &genesis_count]() {
            for (size_t p = begin; p < end; ++p) {
                size_t idx = work[p];
                int x = (int)(idx / NN);
                size_t rem = idx % NN;
                int y = (int)(rem / (size_t)N);
                int z = (int)(rem % (size_t)N);

                actualizar_voxel(
                    gA, clkA, gB, clkB,
                    delta_demux.data(),
                    &overflow_count, &genesis_count,
                    x, y, z, N
                );
            }
        });
    }
    for (auto& th : hilos) th.join();

    aplicar_demux(gB, delta_demux.data(), total);

    std::memcpy(gA, gB, total * sizeof(uint64_t));
    std::memcpy(clkA, clkB, total * sizeof(uint64_t));

    py::dict info;
    info["overflows"] = overflow_count.load();
    info["genesis"] = genesis_count.load();
    info["lazy_evaluated"] = (uint64_t)nwork;
    info["lazy_active_raw"] = (uint64_t)active_raw.size();
    info["lazy_total"] = (uint64_t)total;
    info["lazy_fraction"] = total ? ((double)nwork / (double)total) : 0.0;
    return info;
}

// =========================================================================
// SECCION 10: CENSO SEMANTICO
// =========================================================================
static py::dict censo_semantico(py::array_t<uint64_t> grid, int N) {
    auto buf = grid.request();
    const uint64_t* g = (const uint64_t*)buf.ptr;

    int por_sem[16] = {0};
    int totales = 0, vivos = 0, orphans = 0, xnor_born = 0;
    int observers = 0, con_momento = 0;
    uint64_t suma_s_reg = 0;

    size_t total = (size_t)N * N * N;
    for (size_t i = 0; i < total; ++i) {
        uint64_t v = g[i];
        uint32_t e = get_estado(v);
        if (e == 0) continue;
        uint8_t s = get_sem(v);
        por_sem[s]++;
        totales++;
        suma_s_reg += get_s_reg(v);
        if (s == SEM_ORPHAN_BIT) orphans++;
        else vivos++;
        if (s == SEM_NACIDO_XNOR) xnor_born++;
        if (s == SEM_OBSERVER) observers++;
        if (get_dir_x(v) != 0 || get_dir_y(v) != 0 || get_dir_z(v) != 0) con_momento++;
    }

    py::dict result;
    result["totales"] = totales;
    result["vivos"] = vivos;
    result["orphans"] = orphans;
    result["xnor"] = xnor_born;
    result["observers"] = observers;
    result["con_momento"] = con_momento;
    result["suma_s_reg"] = (uint64_t)suma_s_reg;

    py::dict por_sem_dict;
    por_sem_dict["void"] = por_sem[SEM_VOID];
    por_sem_dict["normal"] = por_sem[SEM_NORMAL];
    por_sem_dict["electron_seed"] = por_sem[SEM_ELECTRON_SEED];
    por_sem_dict["proton_seed"] = por_sem[SEM_PROTON_SEED];
    por_sem_dict["observer"] = por_sem[SEM_OBSERVER];
    por_sem_dict["orphan_bit"] = por_sem[SEM_ORPHAN_BIT];
    por_sem_dict["horizon"] = por_sem[SEM_HORIZON];
    por_sem_dict["nacido_xnor"] = por_sem[SEM_NACIDO_XNOR];
    result["por_semantica"] = por_sem_dict;

    return result;
}

// =========================================================================
// SECCION 11: PYBIND11 MODULE
// =========================================================================
PYBIND11_MODULE(dee_kernel_v27, m) {
    m.doc() = "DEE Universe Kernel v26.0-PHASE0 (SAFE SCAN, v25 physics)";

    m.def("tick_universo", &tick_universo,
          py::arg("grid_A"), py::arg("grid_B"),
          py::arg("clock_A"), py::arg("clock_B"),
          py::arg("N"), py::arg("n_hilos"));

    m.def("tick_universo_lazy", &tick_universo_lazy,
          py::arg("grid_A"), py::arg("grid_B"),
          py::arg("clock_A"), py::arg("clock_B"),
          py::arg("N"), py::arg("n_hilos"));


    m.def("inyectar_electron", &inyectar_electron,
          py::arg("grid"), py::arg("x"), py::arg("y"), py::arg("z"),
          py::arg("N"), py::arg("valor_inicial"),
          py::arg("dir_x"), py::arg("dir_y"), py::arg("dir_z"));

    m.def("inyectar_proton", &inyectar_proton,
          py::arg("grid"), py::arg("x"), py::arg("y"), py::arg("z"), py::arg("N"));

    m.def("sembrar_ruido", &sembrar_ruido,
          py::arg("grid"), py::arg("N"), py::arg("densidad"), py::arg("semilla"));

    m.def("censo_semantico", &censo_semantico, py::arg("grid"), py::arg("N"));

    m.attr("VERSION") = py::str("DEE Universe Kernel v27.0-PKCANON (v26-SYM1 fork; canonical P_KERNEL=19665)");
}