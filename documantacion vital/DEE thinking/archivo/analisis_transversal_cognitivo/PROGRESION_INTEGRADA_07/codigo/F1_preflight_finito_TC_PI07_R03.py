"""Four predeclared additional physical-clearance candidates, first clear only.

Read-only frozen snapshot and pure geometry. No Native/imports/response search.
"""
from pathlib import Path
import datetime, hashlib, importlib.abc, json, runpy, struct, sys

CANDIDATES = ((45,25,42),(45,40,42),(45,8,52),(8,40,50))
EXPECTED = 'af74c8f47e43ed3b2395a338a23a6cbd42f105ec2cff4daac15b7a4d45e90832'


class BlockDEE(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'dee_thinking','app','capacidades','_native','numpy'}:
            raise RuntimeError('Forbidden import: '+fullname)
        return None


def sha(b):
    return hashlib.sha256(b).hexdigest()


def main():
    p7=Path(__file__).resolve().parents[1];atc=p7.parent
    output=p7/'control/PREFLIGHT_FINITO_TC_PI07_R03.json'
    if output.exists():raise FileExistsError(output)
    source=atc/'PROGRESION_INTEGRADA_06/pares/BASE_MAIN_T824911/VIDA.deetsnap.gz'
    parser=atc/'PROGRESION_INTEGRADA_05/codigo/contrastar_prefijos_C2C_PI05_pasivo.py'
    geometry=atc/'PROGRESION_INTEGRADA_03/codigo/pi03_credito_generico_R01_BORRADOR.py'
    before=sha(source.read_bytes());sys.meta_path.insert(0,BlockDEE())
    m=runpy.run_path(str(parser),run_name='passive_only')
    g=runpy.run_path(str(geometry),run_name='pure_geometry_only')
    view=m['parse'](source,EXPECTED);public,raw,clocks=view[:3]
    assert public['physical']['tick']==824911 and before==EXPECTED
    at=g['at'];tested=[];selected=None
    external={(55,48,47),(55,48,51),(52,48,47),(52,48,51),
              (51,48,47),(52,48,46),(53,48,51),(54,48,51)}
    def observe(p):
        i=(p[0]*67+p[1])*67+p[2]
        return {'site':list(p),'clock':str(int(clocks[i])),**m['decode'](int(raw[i]))}
    def group(points,detail=True):
        rows=[observe(p)for p in sorted(points)]
        bad=[r for r in rows if int(r['RAW'])!=0]
        return {'sites':len(rows),
                **({'nonzero_RAW':bad}if detail else{'nonzero_RAW_sites':[r['site']for r in bad]}),
                'coordinates_sha256':sha(json.dumps(sorted(points),separators=(',',':')).encode()),
                'RAW_u64le_sha256':sha(b''.join(struct.pack('<Q',int(r['RAW']))for r in rows)),
                'clocks_u64le_sha256':sha(b''.join(struct.pack('<Q',int(r['clock']))for r in rows))}
    for ordinal,origin in enumerate(CANDIDATES,3):
        footprint={tuple(p)for p in g['geometry_footprint'](origin,67,1)}
        stops={at(origin,(3*x,3,3*z),67)for x in(-1,0,1)for z in(0,-1)}
        stophalo={at(p,(x,y,z),67)for p in stops for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1)}
        datum={at(origin,(-1,0,1),67)};all_sites=footprint|stophalo|datum|external
        total=group(all_sites);refs=[observe(at(origin,p,67))for p in((-1,-1,0),(1,-1,0))]
        clear=not total['nonzero_RAW'] and refs[0]['clock']==refs[1]['clock']
        tested.append({'total_candidate_ordinal':ordinal,'origin':list(origin),
                       'footprint':group(footprint,False),'stops_and_halo':group(stophalo,False),
                       'all_sites':total,'reference_exact_clocks_equal':refs[0]['clock']==refs[1]['clock'],
                       'refs':refs,'eligible_current_clearance_only':clear})
        if clear:selected=list(origin);break
    after=sha(source.read_bytes())
    if before!=after:raise RuntimeError('Frozen snapshot changed')
    result={'schema':'DEE.PI07.finite_external_clearance_preflight.v1',
            'inspection_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'Native_ticks':0,'DEE_imports':0,'SQLite_opened':False,
            'source':{'path':str(source.resolve()),'bytes':source.stat().st_size,
                      'sha256_before':before,'sha256_after':after,'unchanged':True},
            'physical':public['physical'],'pending_count':public['pending_count'],
            'prior_negative_proofs':['PREFLIGHT_TC_O33_25_35_PI07_R01.json','PREFLIGHT_TC_O42_8_42_PI07_R02.json'],
            'predeclared_additional_candidates':CANDIDATES,'stopping_rule':'Stop at first all-RAW0+equal-reference-clock candidate, maximum6total including2prior. No responses or Native runtime are inspected.',
            'tested':tested,'selected_first_clear':selected,
            'not_inspected_after_first_clear':[list(p)for p in CANDIDATES[len(tested):]],
            'selected_external_named_sites':{','.join(map(str,p)):observe(p)for p in sorted(external)},
            'sources':[{'path':str(p.resolve()),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}for p in(parser,geometry)],
            'scope':'External P0 engineering of one new anatomy; no discovery/learning/function claim, no global future influence proof, no original altered, no field cleared.',
            'script_sha256':sha(Path(__file__).read_bytes())}
    data=(json.dumps(result,ensure_ascii=False,separators=(',',':'))+'\n').encode()
    if len(data)>10000:
        print(json.dumps({'proof_bytes_before_compaction':len(data),'selected':selected,
                          'tested':[{ 'origin':r['origin'],'sites':r['all_sites']['sites'],
                                    'nonzero_RAW':r['all_sites']['nonzero_RAW']}
                                   for r in tested]},ensure_ascii=False))
        raise RuntimeError('Proof exceeds10000bytes')
    output.write_bytes(data)
    print(json.dumps({'proof':str(output),'bytes':len(data),'sha256':sha(data),
                      'tested':len(tested),'selected':selected,
                      'conflicts':[r['all_sites']['nonzero_RAW']for r in tested],
                      'Native_ticks':0},ensure_ascii=False))


if __name__=='__main__':main()
