from pathlib import Path
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[4]
SELECTED={'E1_SOCIAL_11','E1_11_ESTABLE','E1_CPC9_1907','E1_CPC9_884','E1_RECONSTRUIDO_11','R65_45_VIVIDO','R65_REVISION_11','R65_N67_VIVIDO','U0_14_VIVIDO'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    s=ROOT/'sistema';base=ROOT/'laboratorio/candidatos/ESTADOS_AUXILIARES';base.mkdir(parents=True,exist_ok=False);files={};lives={}
    for p in(s/'estado/vidas').glob('*/VIDA.json'):
        life=p.parent.name
        if life in SELECTED:continue
        d=json.loads(p.read_bytes());paths=[x for x in p.parent.iterdir()if x.is_file()];paths.append(s/d['snapshot']);paths+=list((s/'estado/checkpoints').glob(life+'.*.gz'));paths+=list((s/'estado/checkpoints').glob('import.'+life+'.*.gz'))
        lives[life]={'branch':d['branch'],'profile':d['profile'],'tick':d['physical']['tick'],'parent':d.get('parent'),'admitted_as_preferred':False,'not_new_learning':True}
        for src in paths:
            rel=src.relative_to(s).as_posix();dst=base/'sistema'/rel
            if rel not in files:dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst);files[rel]={'path':rel,'sha256':sha(src),'bytes':src.stat().st_size,'lives':[]}
            files[rel]['lives'].append(life)
    (base/'INDICE.json').write_text(json.dumps({'schema':'DCS1.1.auxiliary.complete_states.v1','lives':lives,'files':list(files.values()),'requires_explicit_restoration':True,'no_motor_included':True},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'auxiliary_lives':len(lives),'files':len(files),'bytes':sum(x['bytes']for x in files.values())}))
if __name__=='__main__':main()
