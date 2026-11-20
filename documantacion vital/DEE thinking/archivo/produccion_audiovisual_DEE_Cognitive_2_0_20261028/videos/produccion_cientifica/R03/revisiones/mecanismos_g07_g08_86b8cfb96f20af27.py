"""Planos editoriales G07/G08 para R03. No importa ni ejecuta DEE.

Las posiciones intermedias son reconstrucción de la receta congelada, no
telemetría microscópica densa. El propietario de película añade cabecera,
procedencia y subtítulos. Coordenadas de texto dentro de y=210..780.
"""
from pathlib import Path
import math
from PIL import ImageDraw
from estilo_r03 import (BG, WHITE, GRAY, CYAN, AMBER, VIOLET, MUTED,
                        text, bi, panel, plain)

HERE = Path(__file__).resolve().parent
SOURCES = {
    "g07_geometry": {
        "path": str(HERE.parent / "fuentes_g07/G07_EVIDENCIA_Y_GEOMETRIA.json"),
        "sha256": "940ff5ff728ed971e97a63b4ab2d822873f7c425a4ab6e415c8a7b34e6019af7",
        "pointer": "/causal_events",
    },
    "recipe": {
        "path": str(HERE.parent / "fuentes_g07/verificar_dee_original.py"),
        "sha256": "335fecb46c45612a3eece53b907850751b499204d6324f8a88d463d5b0ac5b89",
        "g07_lines": [134, 146], "g08_lines": [148, 157],
    },
    "report": {
        "path": str(HERE.parent / "fuentes_g07/VERIFICACION_EDITORIAL_LINUX_original.json"),
        "sha256": "a958693e02a9557a465f6a2154817537d65fc1937227ecad4071720851f76ad5",
        "g07_pointer": "/groups/07", "g08_pointer": "/groups/08",
        "runtime": "Historical same-source Linux build; not a new Windows thinking4.5 run",
    },
    "control": {
        "path": str(HERE.parent / "fuentes_g07/C6H04_compositional_translation_holdout_original.json"),
        "sha256": "3f61ead2415dcf75a45e18c8089ecec45f8956d36aee1e16cbe53afea879fb98",
        "positive_pointer": "/cases/0", "omitted_pointer": "/cases/1",
        "runner_member": "RUNNERS/run_c6h04_compositional_translation_holdout.py",
        "runner_sha256": "8781a6e51d765b916d0649c40d459a60f10fc2a92f7f76fd53194bd0670dff95",
    },
    "g08_original": {
        "member": "RESULTS/C7H01_functional_learning_transfer.json",
        "sha256": "18d4c42462f4a44b8bf9935d80563c19dd5f3378950c361aa61646865f7945ca",
        "scope": "16 transferred treatments and160 controls, distinct from compact G08",
    },
    "book": {
        "path": str(HERE.parents[5] / "FISICA DEE Y PROCESAMIENTO NATIVO/Procesamiento_Nativo_DEE_Libro_Manual_v1.docx"),
        "sha256": "d619b530658d2d352a24051508f3d49df555846afc475e3532e47a368a458ddb",
        "chapters": [11, 12],
    },
}
ATTRIBUTION = {
    "image_category": "Reconstrucción del mecanismo / Mechanism reconstruction",
    "new_native_ticks": 0,
    "g07": {
        "N": 67, "same_tick_acquisitions": 5, "query_insertion": 10,
        "teaching_timing": "Both relationships form simultaneously at T5; alternating editorial focus does not imply sequential physical acquisition.",
        "prior_editorial_revision_sha256": "499b9e0e17667cc6d37364e0d1a2c308f07b92e36e7a9f50f5f0b127a19992f4",
        "time_display": "Fractional reconstruction counter removed; exact source times remain in this metadata.",
        "prior_teaching_hold_revision_sha256": "c811865d02485da40f872944b4dfbda1bf7527353c8b40cd2f395945dc6ed98a",
        "editorial_teaching_hold": "Formation reaches T5 halfway through the teaching phase; both acquired-relation labels remain visible during its final half. Physical acquisitions remain simultaneous at T5.",
        "first_encounter": 13, "second_encounter": 20,
        "intermediate_23": "Derived functional reading4119-4096; no retained middle RAW",
        "final_30": "Retained final8222-8192",
        "no_compact_omission_control": True, "no_boundary_crossing_0_20": True,
    },
    "control": {
        "identity": "C6H04 cell0 N64, not G07",
        "both": {"query": 0, "relations": [-5, 2], "final_sreg": 8189, "decoded": -3},
        "second_omitted": {"final_sreg": 4091, "decoded": -4101, "signal_present": True},
        "warning": "Omission yields a different output, not silence or zero.",
    },
    "g08": {
        "N": 53, "train": 5, "relay": 12, "query_insert": 18, "query_use": 23,
        "delta": -5, "query": 4, "result": -1,
        "geometry": "Exact recipe reconstruction; report retains final functional output only",
    },
}
G07_J = (20, 15, 30)
G07_R = (20, 23, 30)
G07_R2 = (27, 30, 30)
G07_J2 = (27, 30, 15)
# One orientation throughout the causal chain; this camera is editorial.
G07_EYE = (52, -16, 56)
G07_TARGET = (22, 24, 22)
G07_BOUNDS = ((12, 8, 8), (36, 38, 37))
G08_J = (20, 15, 20)
G08_RELAY = (20, 22, 20)
G08_RECEIVER = (31, 22, 20)
G08_EYE = (50, -15, 46)
G08_TARGET = (23, 21, 20)


def clamp(p):
    return max(0.0, min(1.0, float(p)))


def position(a, direction, ticks):
    return [float(x + ticks * y) for x, y in zip(a, direction)]


def particle(pos, color, radius=.8):
    return {"position": list(pos), "color": color, "radius": radius}


def trail(points, color, width=2, alpha=.65):
    return {"points": [list(p) for p in points], "color": color,
            "width": width, "alpha": alpha}


def _world(renderer, particles, eye=G07_EYE, target=G07_TARGET,
           bounds=G07_BOUNDS, paths=(), highlights=()):
    return renderer.render(particles, eye=eye, target=target, bounds=bounds,
                           paths=list(paths), highlights=list(highlights),
                           fov=43).convert("RGB")


def _dot(im, x, y, color, radius=10):
    ImageDraw.Draw(im).ellipse((x-radius, y-radius, x+radius, y+radius), fill=color)


def _guide(im, renderer, pos, es, en, color, xy, size=38, width=460):
    """Editorial leader line, never a physical channel or added carrier."""
    pt = renderer.project(pos)
    x, y = xy
    if pt and 80 <= pt[0] <= 1840 and 202 <= pt[1] <= 782:
        endpoint = x+width+14 if x < 960 else x-14
        ImageDraw.Draw(im).line((pt[0], pt[1], endpoint, y+size*.5), fill=color, width=2)
    bi(im, (x, y), es, en, size, color, width=width)


def _clock(im, tick, same=False):
    # No tick counters in the public picture: interpolation is editorial,
    # not a measured fractional clock or a new trajectory of the engine.
    if same:
        text(im, (112, 706), "Mismo instante de enseñanza", 35, GRAY, width=700)
        text(im, (112, 750), "Same teaching instant", 26, GRAY, width=700)


def _chain(im, active=0):
    # This is a functional interpretation guide, not RAW or a second system.
    vals = [("20", CYAN), ("23", AMBER), ("30", VIOLET)]
    for i, (v, c) in enumerate(vals):
        text(im, (995+i*270, 736), v, 62, c if active>=i else MUTED, True,
             anchor="mm")
        if i < 2:
            text(im, (1130+i*270, 736), "→", 48, GRAY, anchor="mm")


def g07_particles(t):
    """Only the exact carrier paths of the frozen G07 recipe."""
    pp = []
    if t < 5:
        pp.extend([
            particle(position((15,15,30),(1,0,0),t), CYAN, .68),
            particle(position((25,10,30),(-1,1,0),t), AMBER, .68),
            particle(position((22,30,15),(1,0,0),t), CYAN, .68),
            particle(position((32,30,10),(-1,0,1),t), VIOLET, .68),
        ])
    else:
        if t < 13:
            pp.append(particle(position(G07_J,(0,1,0),t-5), AMBER, .95))
        if t < 20:
            pp.append(particle(position(G07_J2,(0,0,1),t-5), VIOLET, .95))
        if 10 <= t < 13:
            pp.append(particle(position((17,23,30),(1,0,0),t-10), CYAN, .80))
        if 13 <= t < 20:
            pp.append(particle(position(G07_R,(1,1,0),t-13), CYAN, 1.02))
        if t >= 20:
            pp.append(particle(G07_R2, CYAN, 1.15))
    return pp


def _g07_control(p):
    """Actual C6H04 record comparison; no invented compact-G07 omission."""
    im = plain()
    panel(im, (100, 225, 925, 752), AMBER)
    panel(im, (995, 225, 1820, 752), VIOLET)
    bi(im, (140, 248), "Dos relaciones adquiridas", "Both relationships learned",
       40, AMBER, width=740)
    bi(im, (1035, 248), "Segunda relación omitida", "Second relationship omitted",
       40, VIOLET, width=740)
    text(im, (140, 359), "Consulta 0 · relaciones −5 y +2", 36, WHITE, width=740)
    text(im, (1035, 359), "Misma consulta 0", 36, WHITE, width=740)
    for x, value, color in [(512, "−3", AMBER), (1407, "−4101", VIOLET)]:
        text(im, (x, 421), "Valor final / Final reading", 31, GRAY, anchor="mm")
        text(im, (x, 493), value, 86, color, True, anchor="mm")
    bi(im, (140, 580), "Se completa la composición", "Composition is completed",
       35, AMBER, width=740)
    bi(im, (1035, 580), "Una salida distinta", "A different output",
       35, VIOLET, width=740)
    text(im, (140, 686), "C6H04 · N64 · dos mundos comparados", 29, GRAY, width=745)
    text(im, (1035, 686), "Señal presente · sin segunda transformación",
         27, GRAY, width=745)
    # -4101 is the actual second-point reading with the same two-memory decoder.
    return im


def g07(renderer, phase, p):
    p = clamp(p)
    phase = str(phase).lower().replace("ó","o")
    if phase == "control":
        return _g07_control(p)
    if phase in ("enseñanza", "ensenanza"):
        t = min(5.0, 10.0*p)
        im = _world(renderer, g07_particles(t))
        if t < 5:
            bi(im, (112,245), "Dos experiencias", "Two experiences",
               42, WHITE, width=550)
            text(im, (112, 357), "Las señales se encuentran", 35, GRAY, width=570)
            text(im, (112, 404), "Signals meet", 27, GRAY, width=570)
            _guide(im,renderer,position((25,10,30),(-1,1,0),t),
                   "Primera experiencia","First experience",AMBER,(1170,322),35,560)
            _guide(im,renderer,position((32,30,10),(-1,0,1),t),
                   "Segunda experiencia","Second experience",VIOLET,(1170,593),35,560)
            _clock(im,t)
        else:
            bi(im, (112,245), "Relaciones adquiridas", "Learned relationships",
               42, WHITE, width=560)
            _guide(im,renderer,G07_J,"Relación +3","Relationship +3",
                   AMBER,(112,389),42,510)
            _guide(im,renderer,G07_J2,"Relación +7","Relationship +7",
                   VIOLET,(1225,592),42,510)
            _clock(im,5,same=True)
        return im
    if phase == "orientacion":
        t=10+2.75*p
        im=_world(renderer,g07_particles(t))
        bi(im,(112,235),"Elementos del modelo","Elements of the model",
           41,WHITE,width=560)
        for y,col,es,en in [(380,CYAN,"Señal de consulta","Query signal"),
                            (504,AMBER,"Relación adquirida +3","Learned relationship +3"),
                            (628,VIOLET,"Relación adquirida +7","Learned relationship +7")]:
            _dot(im,124,y+13,col)
            bi(im,(155,y),es,en,35,col,width=505)
        _clock(im,t)
        return im
    if phase == "consulta":
        t=10+2.9*p
        im=_world(renderer,g07_particles(t),
                  paths=[trail([(17,23,30),G07_R],CYAN,2,.6)])
        bi(im,(112,245),"Consulta nueva","New query",46,CYAN,width=540)
        text(im,(275,400),"20",112,CYAN,True,anchor="mm")
        text(im,(112,505),"Lo aprendido ya está presente",34,GRAY,width=570)
        text(im,(112,551),"Prior learning is already present",27,GRAY,width=570)
        _clock(im,t)
        _chain(im,0)
        return im
    if phase == "primer_encuentro":
        t=13
        im=_world(renderer,g07_particles(t),
                  paths=[trail([(17,23,30),G07_R],CYAN)],
                  highlights=[{"position":G07_R,"color":AMBER,"radius":1.5}])
        bi(im,(112,245),"Primer encuentro","First encounter",44,AMBER,width=570)
        bi(im,(112,375),"Valor interpretado","Interpreted value",36,GRAY,width=540)
        text(im,(290,543),"23",125,AMBER,True,anchor="mm")
        _guide(im,renderer,G07_R,"20 se transforma en 23","20 is transformed into 23",
               CYAN,(1170,330),36,600)
        _clock(im,t)
        _chain(im,1)
        return im
    if phase == "viaje":
        t=13.03+6.84*p
        current=position(G07_R,(1,1,0),t-13)
        second=position(G07_J2,(0,0,1),t-5)
        im=_world(renderer,g07_particles(t),
                  paths=[trail([G07_R,current],CYAN,3,.88),
                         trail([G07_J2,second],VIOLET,2,.65)],
                  highlights=[{"position":G07_R2,"color":VIOLET,"radius":1.2}])
        bi(im,(112,245),"La salida continúa","The output continues",42,CYAN,width=555)
        text(im,(112,375),"Viaja hacia otra relación",36,GRAY,width=560)
        text(im,(112,423),"It travels toward another relationship",27,GRAY,width=560)
        _guide(im,renderer,current,"Salida del primer encuentro","First-encounter output",
               CYAN,(1160,335),33,620)
        _clock(im,t)
        _chain(im,1)
        return im
    if phase in ("segundo_encuentro","resultado","recap"):
        t=20
        im=_world(renderer,g07_particles(t),
                  paths=[trail([G07_R,G07_R2],CYAN,3,.9),
                         trail([G07_J2,G07_R2],VIOLET,2,.6)],
                  highlights=[{"position":G07_R2,"color":VIOLET,"radius":1.65}])
        bi(im,(112,245),"Segundo encuentro"if phase=="segundo_encuentro"else"Resultado de la composición",
           "Second encounter"if phase=="segundo_encuentro"else"Composition result",
           42,VIOLET,width=600)
        text(im,(300,450),"30",140,VIOLET,True,anchor="mm")
        bi(im,(112,577),"Dos relaciones utilizadas","Two relationships used",
           34,GRAY,width=560)
        _clock(im,t)
        _chain(im,2)
        return im
    raise ValueError("Fase G07 desconocida: "+phase)


def _g08_particles(t):
    pp=[]
    if t<5:
        pp=[particle(position((15,15,20),(1,0,0),t),CYAN,.75),
            particle(position((25,10,20),(-1,1,0),t),AMBER,.75)]
    elif t<12:
        pp=[particle(position(G08_J,(0,1,0),t-5),AMBER,1)]
    else:
        pp=[particle(position(G08_RELAY,(1,0,0),min(t,23)-12),AMBER,1)]
    # Relay is present from T0; its zero load is not an empty physical site.
    if t<12:
        pp.append(particle(position((8,34,20),(1,-1,0),t),VIOLET,.68))
    if 18<=t<23:
        pp.append(particle(position((31,17,20),(0,1,0),t-18),CYAN,.8))
    if t>=23:
        pp=[particle(G08_RECEIVER,CYAN,1.2)]
    return pp


def g08(renderer,p):
    p=clamp(p)
    # Four editorial views, one physically consistent compact G08 recipe.
    if p<.23:
        t=min(5,6*p/.23);stage="teach"
    elif p<.49:
        t=5+7*(p-.23)/.26;stage="relay"
    elif p<.80:
        t=12+10.9*(p-.49)/.31;stage="travel"
    else:
        t=23;stage="use"
    current=position(G08_RELAY,(1,0,0),max(0,min(11,t-12)))
    pp=_g08_particles(t)
    paths=[trail([G08_J,G08_RELAY],AMBER,2,.6)]
    if t>=12:
        paths.append(trail([G08_RELAY,current],AMBER,3,.85))
    im=_world(renderer,pp,G08_EYE,G08_TARGET,((7,9,15),(36,36,25)),
              paths=paths,highlights=[{"position":G08_RELAY,"color":VIOLET},
                                      {"position":G08_RECEIVER,"color":CYAN}])
    if stage=="teach":
        bi(im,(112,240),"Una experiencia","An experience",44,AMBER,width=570)
        if t>=5:
            bi(im,(112,388),"Relación −5","Relationship −5",46,AMBER,width=560)
        else:
            bi(im,(112,388),"La relación se adquiere","The relationship is learned",
               36,GRAY,width=560)
    elif stage=="relay":
        bi(im,(112,240),"Transportar lo aprendido","Transport prior learning",
           39,AMBER,width=590)
        bi(im,(112,383),"Relación −5","Relationship −5",46,AMBER,width=560)
        bi(im,(112,531),"Un encuentro cambia su ruta","An encounter changes its route",
           34,VIOLET,width=590)
    elif stage=="travel":
        bi(im,(112,240),"La relación llega a otro lugar","The relationship reaches another place",
           37,AMBER,width=610)
        if t<18:
            bi(im,(112,405),"Su función se conserva","Its function is retained",
               39,AMBER,width=570)
        else:
            bi(im,(112,389),"Nueva consulta: 4","New query: 4",
               46,CYAN,width=570)
        _guide(im,renderer,current,"Relación transportada","Transferred relationship",
               AMBER,(1160,337),34,620)
    else:
        bi(im,(112,240),"Utilización en el destino","Use at the destination",
           42,CYAN,width=600)
        text(im,(112,393),"4 + (−5) = −1",68,CYAN,True,width=650)
        bi(im,(112,542),"La relación no se enseñó aquí","The relationship was not retaught here",
           32,GRAY,width=640)
    _clock(im,t)
    if t>=12:
        text(im,(1110,718),"RELACIÓN −5",39,AMBER,True,width=560)
        text(im,(1110,765),"RELATIONSHIP −5",26,GRAY,width=560)
    return im

