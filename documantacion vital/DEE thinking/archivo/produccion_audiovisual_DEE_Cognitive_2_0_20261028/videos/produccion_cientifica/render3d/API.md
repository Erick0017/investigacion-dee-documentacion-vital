# Render científico local

`dee_renderer.py` sólo dibuja datos que el editor proporciona. No importa DEE ni ejecuta su física.

```python
from dee_renderer import SceneRenderer
r = SceneRenderer(1920, 1080)
image = r.render(
    [{"position": [20, 23, 30], "radius": .8, "color": "#FFBE66"}],
    eye=[46, -12, 52], target=[23, 23, 26], bounds=(0, 66),
    paths=[{"points": [[17, 23, 30], [20, 23, 30]], "color": "#44D8C1"}],
    highlights=[{"position": [20, 23, 30], "radius": 1.2, "color": "#FFFFFF"}],
)
# image: PIL.Image RGB, 1920×1080
pixel = r.project([20, 23, 30])  # (x_px, y_px, depth_NDC); None si detrás
r.close()
```

`bounds` también admite `((xmin,ymin,zmin),(xmax,ymax,zmax))`. `grid=False` oculta retícula/caja.
`fov=42` controla la lente. El eje vertical de la cámara es Z. La proyección de etiquetas
es exactamente la del render, con origen de imagen arriba a la izquierda.

Colores, radios visibles y luces son decisiones del visualizador, no propiedades físicas.
Las líneas sólo se dibujan si el editor suministra `paths`; esta API no deduce recorridos.
`highlights` dibuja tres anillos como anotación geométrica, no un nuevo portador.

Motor de representación: ModernGL 5.13.0 + glcontext 3.1.0 instalados únicamente en
`../python_deps`, contexto WGL standalone, Intel HD Graphics 4600/OpenGL 3.3.
No se ha utilizado navegador, Blender, DEE Runtime, ni ventanas interactivas.
Mallas esféricas 32×20 con iluminación direccional/fill/specular, perspectiva y búfer de
profundidad, antialiasing MSAA4, framebuffer nativo1920×1080. Las geometrías de referencia
se dibujan tenues; no se añaden partículas aleatorias.

Pilotos: `piloto_1080.png`, `piloto_DEMO_1080.png`.
Benchmark local:4 partículas30frames1.734s (~17.3fps);276 posiciones reales de la observación
inicial de DEE20_DEMO_01,20frames1.234s (~16.2fps). Son tiempos del anfitrión para edición,
no medidas de capacidad o velocidad del ente DEE.
