"""One proposed geometry over a frozen exact snapshot; no DEE imports."""
from pathlib import Path
import datetime, hashlib, importlib.abc, json, runpy, struct, sys


class BlockDEE(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'dee_thinking', 'app', 'capacidades', '_native', 'numpy'}:
            raise RuntimeError('Forbidden executable/Native import in passive preflight: '+fullname)
        return None


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    p7 = Path(__file__).resolve().parents[1]
    atc = p7.parent
    source = atc/'PROGRESION_INTEGRADA_06/pares/BASE_MAIN_T824911/VIDA.deetsnap.gz'
    expected = 'af74c8f47e43ed3b2395a338a23a6cbd42f105ec2cff4daac15b7a4d45e90832'
    parser = atc/'PROGRESION_INTEGRADA_05/codigo/contrastar_prefijos_C2C_PI05_pasivo.py'
    geometry = atc/'PROGRESION_INTEGRADA_03/codigo/pi03_credito_generico_R01_BORRADOR.py'
    output = p7/'control/PREFLIGHT_TC_O33_25_35_PI07_R01.json'
    if output.exists():
        raise FileExistsError(output)
    before = {'bytes':source.stat().st_size,'sha256':sha(source.read_bytes())}
    sys.meta_path.insert(0, BlockDEE())
    m = runpy.run_path(str(parser), run_name='passive_parser_only')
    g = runpy.run_path(str(geometry), run_name='pure_geometry_only')
    view = m['parse'](source, expected)
    public, raw, clocks = view[:3]
    if public['physical']['tick'] != 824911:
        raise ValueError('Unexpected physical cut')
    origin = (33,25,35)
    at = g['at']
    footprint = {tuple(p) for p in g['geometry_footprint'](origin,67,1)}
    frame = {tuple(r['site']) for r in g['frame_rows'](origin)}
    stops = {at(origin,(3*x,3,3*z),67) for x in (-1,0,1) for z in (0,-1)}
    datum = {at(origin,(-1,0,1),67)}
    # A declared conservative Moore halo around the six added stopping sites.
    stops_halo = {at(p,(x,y,z),67) for p in stops
                  for x in (-1,0,1) for y in (-1,0,1) for z in (-1,0,1)}
    proposed_named = {
        'sink_falsecue':(55,48,47), 'sink_communication':(55,48,51),
        'sensor':(52,48,47), 'actor_and_communication':(52,48,51),
        'falsecue_X_source':(51,48,47), 'threat_Z_source':(52,48,46),
        'message_reader_Bplus1':(53,48,51),
        'alternative_message_reader_Bplus2':(54,48,51),
    }
    groups = {'old_PI03_footprint_halo1':footprint,
              'frame_installation':frame, 'six_stops':stops,
              'six_stops_halo1':stops_halo,'datum':datum,
              'external_named_sites':set(proposed_named.values())}
    all_sites = set().union(*groups.values())
    def observe(p):
        i=(p[0]*67+p[1])*67+p[2]
        return {'site':list(p),'clock':str(int(clocks[i])),**m['decode'](int(raw[i]))}
    def summary(points):
        rows=[observe(p) for p in sorted(points)]
        return {'sites':len(rows),'nonzero_RAW_count':sum(int(r['RAW'])!=0 for r in rows),
                'nonzero_RAW': [r for r in rows if int(r['RAW'])!=0],
                'coordinate_list_sha256':sha(json.dumps(sorted(points),separators=(',',':')).encode()),
                'selected_RAW_u64le_sha256':sha(b''.join(struct.pack('<Q',int(r['RAW']))for r in rows)),
                'selected_clocks_u64le_sha256':sha(b''.join(struct.pack('<Q',int(r['clock']))for r in rows))}
    grouped={name:summary(points)for name,points in groups.items()}
    total=summary(all_sites)
    refs=[observe(at(origin,p,67))for p in((-1,-1,0),(1,-1,0))]
    eligible=total['nonzero_RAW_count']==0 and refs[0]['clock']==refs[1]['clock']
    after={'bytes':source.stat().st_size,'sha256':sha(source.read_bytes())}
    if before!=after:
        raise RuntimeError('Frozen source changed')
    result={
        'schema':'DEE.PI07.one_geometry_passive_preflight.v1',
        'inspection_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'Native_ticks':0,'DEE_imports':0,'SQLite_opened':False,
        'candidate_geometry_only':True,'origin':list(origin),
        'source':{'path':str(source.resolve()),**before,'verified_expected_sha256':expected,
                  'after':after,'unchanged':True},
        'physical':public['physical'],'pending_count':public['pending_count'],
        'sources':[{'path':str(p.resolve()),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}
                   for p in (parser,geometry)],
        'grouped':grouped,'all_selected_sites':total,
        'refs':refs,'reference_exact_clocks_equal':refs[0]['clock']==refs[1]['clock'],
        'named_sites':{k:observe(v)for k,v in proposed_named.items()},
        'eligible_current_clearance_only':eligible,
        'scope':'One declared footprint, six fixed stops+Moorehalo1, datum and eight named sites. Not a global future influence proof; no clearing or source selection by response.',
        'script_sha256':sha(Path(__file__).read_bytes()),
    }
    data=(json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    if len(data)>10000:
        raise RuntimeError('Requested proof exceeds10000bytes; preserve code but do not write oversized proof')
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_bytes(data)
    print(json.dumps({'proof':str(output),'bytes':len(data),'sha256':sha(data),
                      'eligible':eligible,'sites':total['sites'],
                      'nonzero_RAW':total['nonzero_RAW'],'refs':refs,'Native_ticks':0},ensure_ascii=False))


if __name__=='__main__':
    main()
