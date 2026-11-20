"""Read the supplied production contract and prepare the single R05 register.
No DEE imports, Native calls, life writes, or old-media modifications.
"""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os
from docx import Document

HERE=Path(__file__).resolve().parent
PROMPT=Path(r'C:\Users\Erik\.codex\codex-remote-attachments\01a0921e-4727-7f93-8ad0-0b605c9afe96\C362B742-5108-465C-AEE3-EF62F1A50C55\1-PROMPT_CODEX_DEE_VIDEO_R05_MUNDO_3D_Y_CAPACIDADES.docx')
REG=HERE/'REGISTRO_PRODUCCION_R05.json'
def main():
    if REG.exists():
        raise SystemExit('Continue the existing register; do not restart the production clock.')
    doc=Document(PROMPT)
    texts=[p.text for p in doc.paragraphs]
    starts=[60,75,90,105,120,135,150,165,179,193,207,221,235,249,263]
    boundaries=[0,20,44,76,108,130,158,180,202,230,250,274,300,322,342,360]
    scenes=[]
    for n,start in enumerate(starts):
        end=starts[n+1] if n+1<len(starts) else 277
        chunk=texts[start:end]
        es=chunk[chunk.index('Locución literal en español')+1]
        en=chunk[chunk.index('Traducción inglesa para subtitular')+1]
        scenes.append({'id':f'S{n+1:02d}','start_s':boundaries[n],'end_s':boundaries[n+1],
                       'start_frame':boundaries[n]*30,'frames':(boundaries[n+1]-boundaries[n])*30,
                       'title':texts[start+1],'es':es,'en':en,'contract_paragraphs':chunk,
                       'representation':None,'scientific_sources':[],'status':'preparing'})
    assert len(scenes)==15 and sum(s['frames'] for s in scenes)==10800
    r={'schema':'DEE.Cognitive2.R05.production.v1','stage':'assets_and_evidence',
       'started_utc':'2026-10-31T05:42:51+00:00','deadline_utc':'2026-10-31T11:42:51+00:00',
       'wall_time_budget_hours':6,'budget_not_automatically_extended':True,
       'resource_limits':{'render_workers_max':2,'encoder_threads_max':4,'temporary_storage_budget_bytes':17179869184,
                          'C_drive_free_at_start':5076402176,'D_drive_free_at_start':600329728000},
       'source_prompt':{'path':str(PROMPT),'sha256':hashlib.sha256(PROMPT.read_bytes()).hexdigest(),
                        'paragraphs':len(texts),'tables':len(doc.tables),'read_coverage':'All325paragraphs and3tables; long output read in bounded blocks.'},
       'contract':{'duration_seconds':360,'width':1920,'height':1080,'fps':30,'frames':10800,
                   'codec':'H264','pixel_format':'yuv420p','audio_sample_rate':48000,'audio_codec':'AAC',
                   'primary_subtitles':'English burned in','clean_subtitles':'Selectable English and Spanish',
                   'no_old_video_recut':True,'no_Native_ticks':True,'no_manual_or_system_change':True},
       'scenes':scenes,'families':[row.cells[1].text for row in doc.tables[0].rows[1:]],
       'catalogue_mapping':[dict(zip([c.text for c in doc.tables[2].rows[0].cells],[c.text for c in row.cells])) for row in doc.tables[2].rows[1:]],
       'scientific_cut':'CompendioR01 and ECI01/ECI02R01. Operational adoption1.26 exists but is not silently added to the prescribed examples.',
       'external_concept_source':{'scene':'S02','url':'https://www.nature.com/articles/323533a0','DOI':'10.1038/323533a0',
                                  'access':'Publisher abstract read2026-10-31; connection-weight adaptation supports conceptual illustration; no private input uploaded.'},
       'outputs':{},'QA':{},'incidents':[],'resume':'Complete15scene3Ddata and literal voice; internal S04/S06/S09proof before final render.'}
    assert len(r['catalogue_mapping'])==101 and len(r['families'])==12
    tmp=REG.with_suffix('.json.pending');tmp.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n',encoding='utf8');os.replace(tmp,REG)
    print(json.dumps({'register':str(REG),'scenes':len(scenes),'catalogue_records':101,'narration_words':sum(len(s['es'].split()) for s in scenes),'new_Native_ticks':0},ensure_ascii=True))
if __name__=='__main__':main()
