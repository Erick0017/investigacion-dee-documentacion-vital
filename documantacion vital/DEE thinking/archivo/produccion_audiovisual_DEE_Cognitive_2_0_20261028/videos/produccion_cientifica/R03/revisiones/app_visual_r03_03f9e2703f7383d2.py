"""R03: encuadres editoriales de capturas auténticas, sin ejecutar DEE.

API: draw(phase, p) -> PIL.Image RGB 1920x1080. Sólo utiliza el área
x=90..1830, y=205..790; el montaje añade títulos, procedencia y subtítulos.
No genera una interfaz: muestra fotografías/recortes de la grabación.
Los datos ampliados a22/b02 están separados y rotulados como registros.
"""
from functools import lru_cache
from pathlib import Path
from PIL import Image, ImageDraw
import math

from estilo_r03 import BG, DARK, WHITE, GRAY, CYAN, AMBER, MUTED
from estilo_r03 import plain, text, bi, panel, lerp

PROJECT = Path(__file__).resolve().parent.parent
FULL_BEFORE = PROJECT / 'fuentes_g07/demo_t170.png'
FULL_RETAINED = PROJECT / 'fuentes_g07/demo_t1418.png'
CLIPS = PROJECT / 'clips'
EVIDENCE_CONTROL = PROJECT / 'R02_memoria_plasticidad/CONTROL_R02.json'
BOUNDS = (90, 205, 1830, 790)
PHASES = ('overview', 'before', 'teach', 'after', 'compare', 'save', 'reopen', 'retained')
REVISION_HISTORY = [{
    'previous_source_sha256': '2b27022a0e384215637e2671b017e179f6e05b4fedbd757479af1babbfc11ea1',
    'change': 'Public-facing reopen wording only; full N/tick/RAW/clocks remain in SOURCES.',
}, {
    'previous_source_sha256': '06aaa90e39c69a3655c60bd06dc90a443e1b815ee7fd0b3a0cb9bb75958d22c2',
    'change': 'Large query/receipt cut, explicit archival teaching denominator, editorial before/after comparison, public-facing English labels.',
}]

# Procedencia del montaje: no son sensores ni memoria accesible a DEE.
SOURCES = {
    'source_recording': {
        'file': 'DEE_Cognitive_2_0_Demostracion_Completa_Original.mp4',
        'sha256': 'cd4c137f3529b86583cea0934a2f1bf364998c8dcaba6c4bca06fbcb40f36c87',
        'native_size': [1284, 932], 'native_fps': 15,
        'seconds': 1600.6,
    },
    'before': {
        'file': str(FULL_BEFORE),
        'sha256': '7868e23ca2ed7fd9c3895cb280c7883b5167a4f7dd86b7e9a9cb6bc1462cc869',
        'source_size': [1284, 932], 'source_seconds': 170,
        'record': 'a13_clasifica', 'transport': 'dee20_demo_clasifica_01',
        'input_tick': 684673, 'read_tick': 684677, 'end_tick': 684680,
        'sign': 1, 'applied': 7, 'requested': 7,
        'initial_content': 'Inherited from complete APD05 import at T684418; not newly taught in the recording.',
        'passive_view_tick': 684613,
    },
    'teach': {
        'directory': str(CLIPS / 'teach'), 'frames': 75, 'fps': 15,
        'source_seconds': [416.4, 421.4], 'clip_size': [496, 310],
        'roi_in_clip': [0, 153, 496, 265],
        'roi_in_recording': [18, 513, 514, 625],
        'first_frame_sha256': '668ad960937cb81454cfbe80df8b9fd9fa6db300977fd7aa4bfb08a4db2949eb',
        'record': 'a21_revision', 'teacher_tick': 688961,
        'teacher_sign': -1, 'applied': 3, 'requested': 3,
        'limit': 'Teaching is explicit operator input; unrelated previous command field is excluded.',
    },
    'after': {
        'directory': str(CLIPS / 'after'), 'frames': 75, 'fps': 15,
        'source_seconds': [440, 445], 'clip_size': [494, 62],
        'record': 'a22_revision_use', 'transport': 'dee20_demo_clasifica_post_01',
        'input_tick': 689028, 'read_tick': 689032, 'end_tick': 689035,
        'sign': -1, 'applied': 7, 'requested': 7,
        'limit': 'The authentic crop shows the query field, not its result receipt. The -1 is separately labelled archival data.',
    },
    'compare': {
        'query_image_directory': str(CLIPS / 'after'),
        'records': ['a13_clasifica', 'a22_revision_use'],
        'before_sign': 1, 'after_sign': -1,
        'same_query_payload_sha256': 'd28b44882f785faaf2ad030468ab0c3d52577e419f561760937bef4edae69a02',
        'limit': 'Two explicitly editorial readouts of already-recorded results; not a reconstructed GUI or a new DEE response.',
    },
    'save': {
        'directory': str(CLIPS / 'save'), 'frames': 47, 'fps': 15,
        'source_seconds': [1278.9, 1282.1], 'clip_size': [494, 216],
        'record': 'a44_save', 'tick': 697650,
        'content': 'Authentic guardar completed receipt and operator entry.',
        'display_roi_in_clip': [0, 0, 494, 192],
    },
    'reopen': {
        'directory': str(CLIPS / 'reopen'), 'frames': 56, 'fps': 15,
        'source_seconds': [1376.8, 1380.5], 'clip_size': [496, 144],
        'record': 'b02_reopen', 'tick': 697650, 'N': 67,
        'RAW_sha256': '379fb3a656b4d415351adff972f21df335cc3aa2f8049d95e73b23899d6ad9b4',
        'clocks_sha256': 'c772e99799848c10af197c434b62b80cb463dfb72fda5d3b032ca0ec82393010',
        'limit': 'The crop shows actual controls, not a reopen receipt. Equality N/tick/RAW/clocks comes from b02 and save/stop records; host metadata bytes can differ.',
    },
    'retained': {
        'file': str(FULL_RETAINED),
        'sha256': '649189139b383708e1f5d38b0e11749965b114acc52a58a1e9cc159543efc718',
        'source_size': [1284, 932], 'source_seconds': 1418,
        'record': 'b09_revision', 'transport': 'dee20_demo_clasifica_reabierta_01',
        'input_tick': 697738, 'read_tick': 697742, 'end_tick': 697745,
        'sign': -1, 'applied': 7, 'requested': 7,
        'passive_view_tick': 697678,
    },
}
LIMITS = [
    'GUI content is an enlarged native 1284x932 / 15fps recording crop, not native 1080p interface capture.',
    'The same life is used; this presentation does not execute or teach DEE.',
    'Passive 3D captures precede query receipts and do not trace the query microscopically.',
    'No dense microscopic frames for a13/a22/b09 are available.',
    'Signs +1/-1 are opaque code responses, not correctness or human word comprehension.',
]


def _clamp(p):
    return min(1., max(0., float(p)))


@lru_cache(32)
def _image(path):
    with Image.open(path) as im:
        return im.convert('RGB')


def _frame(phase, p):
    meta = SOURCES[phase]
    index = 1 + min(meta['frames'] - 1, int(_clamp(p) * meta['frames']))
    return _image(str(Path(meta['directory']) / f'{index:05d}.jpg'))


def _fit(im, photo, box, border=False):
    """Uniform scaling only; never stretches or invents image detail."""
    x0, y0, x1, y1 = map(int, box)
    scale = min((x1 - x0) / photo.width, (y1 - y0) / photo.height)
    size = (max(1, round(photo.width * scale)), max(1, round(photo.height * scale)))
    pic = photo.resize(size, Image.Resampling.LANCZOS)
    at = (x0 + (x1 - x0 - size[0]) // 2, y0 + (y1 - y0 - size[1]) // 2)
    im.paste(pic, at)
    if border:
        ImageDraw.Draw(im).rectangle((at[0], at[1], at[0] + size[0] - 1, at[1] + size[1] - 1), outline=MUTED, width=2)


def _crop(path, rectangle):
    return _image(str(path)).crop(tuple(round(v) for v in rectangle))


def _readout(im, box, label, english, value, detail, subdetail):
    """Editorial readout, explicitly distinguished from the captured GUI."""
    panel(im, box, color=CYAN, fill=DARK)
    x0, y0, x1, y1 = box
    center = (x0 + x1) / 2
    bi(im, (center, y0 + 45), label, english, 32, AMBER, 'mm', x1-x0-60)
    text(im, (center, y0 + 187), value, 104, CYAN, True, 'mm', x1-x0-60)
    bi(im, (center, y1 - 95), detail, subdetail, 33, WHITE, 'mm', x1-x0-60)


def draw(phase, p):
    """Return one editorial content frame; titles/subtitles belong to root."""
    if phase not in PHASES:
        raise ValueError(f'Unknown application phase: {phase!r}')
    p = _clamp(p)
    im = plain()
    if phase == 'overview':
        # One app view, never an application view nested in a second fake UI.
        rectangle = lerp((0, 87, 1262, 510), (6, 91, 1256, 510), p)
        _fit(im, _crop(FULL_BEFORE, rectangle), (100, 205, 1820, 790))
    elif phase == 'before':
        if p < .40:
            # Large, shallow authentic query crop. The nominal bottom 190
            # includes a cut-off helper line; 180 ends cleanly after the field.
            rect = (12, 106, 512, 180)
        else:
            rect = (20, 397, 512, 470)
        _fit(im, _crop(FULL_BEFORE, rect), (100, 238, 1820, 745))
    elif phase == 'teach':
        photo = _frame('teach', p).crop((0, 153, 496, 265))
        bi(im, (960, 226), 'DATO AMPLIADO · Registro a21', 'Primary teaching record a21',
           30, AMBER, 'mm', 1740)
        _fit(im, photo, (130, 285, 1790, 645))
        bi(im, (960, 697), 'Enseñanza admitida: 3/3', 'Teaching admitted: 3/3',
           60, CYAN, 'mm', 1740)
    elif phase == 'after':
        bi(im, (110, 260), 'Petición auténtica', 'Recorded request', 40, WHITE, width=980)
        _fit(im, _frame('after', p), (110, 370, 1110, 610))
        _readout(im, (1160, 235, 1810, 755), 'REGISTRO a22 · DATO AMPLIADO',
                 'Primary recorded result', '−1',
                 '7/7 entradas aplicadas', '7/7 material inputs admitted')
    elif phase == 'compare':
        _fit(im, _frame('after', p), (300, 210, 1620, 385))
        # These are editorial data columns, not buttons or a simulated GUI.
        for box, es, en, value, source in [
            ((150, 405, 900, 785), 'Antes', 'Before', '+1', 'a13'),
            ((1020, 405, 1770, 785), 'Tras nueva enseñanza', 'After teaching', '−1', 'a22'),
        ]:
            panel(im, box, color=MUTED, fill=DARK)
            cx = (box[0] + box[2]) / 2
            bi(im, (cx, 450), es, en, 60, WHITE, 'mm', 700)
            text(im, (cx, 620), value, 128, CYAN, True, 'mm', 700)
            bi(im, (cx, 735), 'DATO AMPLIADO · Registro ' + source,
               'Primary recorded result · ' + source, 29, AMBER, 'mm', 700)
    elif phase == 'save':
        _fit(im, _frame('save', p).crop((0, 0, 494, 192)), (270, 220, 1650, 775))
    elif phase == 'reopen':
        _fit(im, _frame('reopen', p), (340, 215, 1580, 545))
        bi(im, (960, 575), 'LECTURA DEL REGISTRO b02', 'Archived reopening record',
           32, AMBER, 'mm', 1650)
        bi(im, (960, 660), 'Misma vida · misma historia', 'Same life · same saved history',
           52, CYAN, 'mm', 1650)
    elif phase == 'retained':
        # The actual receipt states -1 and the 7/7 admitted-input denominator.
        _fit(im, _crop(FULL_RETAINED, (20, 397, 512, 470)), (100, 238, 1820, 745))
    assert im.mode == 'RGB' and im.size == (1920, 1080)
    return im


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--samples', type=Path, required=True)
    args = parser.parse_args()
    args.samples.mkdir(parents=True, exist_ok=True)
    for name in PHASES:
        draw(name, .5).save(args.samples / (name + '.png'))
    print('PIL-only editorial samples:', len(PHASES))
