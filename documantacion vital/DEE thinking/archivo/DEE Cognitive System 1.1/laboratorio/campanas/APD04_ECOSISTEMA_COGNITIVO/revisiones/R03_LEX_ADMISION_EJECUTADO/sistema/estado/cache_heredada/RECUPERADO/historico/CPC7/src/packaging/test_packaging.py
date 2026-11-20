"""Finite synthetic engineering tests. No native worlds or scientific claims."""
import argparse
import gzip
import json
from pathlib import Path
import shutil
import sys
import zipfile

HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from bundle import ROOT,NAME,WHL,build,encode_snapshot,put,safe_name,select,sha,split,verify
from reunir import join
from clean import pointer,validate_plan

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--directory',type=Path,required=True)
    p.add_argument('--kernel-source',type=Path,default=ROOT/'genealogia/kernel_v27.cpp');a=p.parse_args()
    directory=a.directory.resolve();assert directory.is_relative_to(ROOT/'_delivery')
    directory.mkdir(parents=True,exist_ok=False);checks=[]
    source_cut={path.name:sha(path) for path in sorted(HERE.glob('*.py'))}
    archive=ROOT/'_delivery/proofs/executed_sources'/directory.name;archive.mkdir(parents=True,exist_ok=False)
    for path in sorted(HERE.glob('*.py')):shutil.copyfile(path,archive/(path.name+'.txt'))
    def check(name,value):
        assert value,name;checks.append({'check':name,'correct':True})
    fixture=directory/'CPC7';fixture.mkdir()
    for name in ('src','resultados/adverse','runtime','genealogia','.venv','documantacion vital','_delivery'):(fixture/name).mkdir(parents=True,exist_ok=True)
    (fixture/'src/example.py').write_text('# SYNTHETIC_SCHEMA_TEST_ONLY\n',encoding='utf-8')
    (fixture/'resultados/adverse/ERROR.json').write_text('{"kind":"SYNTHETIC"}',encoding='utf-8')
    (fixture/'.venv/private.py').write_text('DO_NOT_PACKAGE',encoding='utf-8')
    (fixture/'documantacion vital/accidental.py').write_text('DO_NOT_PACKAGE',encoding='utf-8')
    (fixture/'_delivery/duplicate.py').write_text('DO_NOT_PACKAGE',encoding='utf-8')
    selected,excluded=select(fixture);names={rel for _,rel in selected}
    check('positive_selection_preserves_adverse_result','resultados/adverse/ERROR.json' in names)
    check('positive_selection_excludes_venv_accidental_nested_root_and_delivery',not any('private.py' in x or 'accidental.py' in x or 'duplicate.py' in x for x in names))
    check('selection_exclusions_are_recorded',len(excluded)==3)
    for name in ('../outside','C:/outside','/outside','a\\b','a/./b','a//b','a\nb'):
        try:safe_name(name)
        except AssertionError:pass
        else:raise AssertionError('Accepted unsafe archive path '+repr(name))
    check('unsafe_noncanonical_archive_paths_rejected',True)
    raw=fixture/'resultados/adverse/STATE.deetsnap';raw.write_bytes(b'SYNTHETIC_STATE_NOT_NATIVE\x00'+bytes(range(256))*1024)
    first=directory/'one.gz';second=directory/'two.gz';before=sha(raw)
    encode_snapshot(raw,first,'resultados/adverse/STATE.deetsnap');encode_snapshot(raw,second,'resultados/adverse/STATE.deetsnap')
    check('gzip_deterministic_filename_and_mtime',first.read_bytes()==second.read_bytes())
    check('gzip_decodes_byte_exact_and_preserves_original',gzip.decompress(first.read_bytes())==raw.read_bytes() and sha(raw)==before)
    corrupt=directory/'corrupt.gz';data=bytearray(first.read_bytes());data[-1]^=1;corrupt.write_bytes(data)
    try:gzip.decompress(corrupt.read_bytes())
    except (gzip.BadGzipFile,EOFError):pass
    else:raise AssertionError('Corrupt gzip accepted')
    check('gzip_CRC_corruption_rejected',True)
    shutil.copyfile(ROOT/'runtime'/WHL,fixture/'runtime'/WHL)
    shutil.copyfile(a.kernel_source,fixture/'genealogia/kernel_v27.cpp')
    candidate=directory/'synthetic.candidate.zip'
    result=build(fixture,candidate,fixture/'_delivery/encoded',[],check_protected=False)
    check('synthetic_container_CRC_manifest_and_decoded_state_verified',result['status']=='VERIFIED' and result['encoded_snapshots']==1)
    with zipfile.ZipFile(candidate) as z:
        check('no_raw_duplicate_when_encoded','CPC7/resultados/adverse/STATE.deetsnap' not in z.namelist())
        check('source_cut_retains_original_identity',json.loads(z.read('CPC7/SOURCE_CUT.json'))['files'][-1]['path']!='_delivery/duplicate.py')
        bad=directory/'bad.candidate.zip'
        with zipfile.ZipFile(bad,'x',compression=zipfile.ZIP_DEFLATED) as out:
            for name in z.namelist():out.writestr(name,b'altered' if name=='CPC7/src/example.py' else z.read(name))
    try:verify(bad)
    except AssertionError:pass
    else:raise AssertionError('Changed member accepted')
    check('member_tamper_rejected_by_manifest',True)
    transport=directory/'transport';transport.mkdir()
    (transport/'PARTES.json').write_text('CPC5_SENTINEL',encoding='utf-8')
    large=directory/'transport_source.zip'
    with zipfile.ZipFile(large,'x',compression=zipfile.ZIP_STORED) as z:z.writestr('synthetic.bin',b'x'*(21*1024*1024))
    parts=split(large,transport);metadata=transport/'transporte_CPC7/PARTES.json'
    check('exact_two_parts_threshold_uses_compressed_container_bytes',len(parts['parts'])==2 and parts['reconstruction_tested'])
    check('existing_historical_transport_metadata_untouched',(transport/'PARTES.json').read_text(encoding='utf-8')=='CPC5_SENTINEL')
    reunited=join(metadata,transport/'reunited.zip')
    check('actual_helper_reconstruction_exact',reunited['verified'] and sha(transport/'reunited.zip')==sha(large))
    try:join(metadata,transport/'reunited.zip')
    except FileExistsError:pass
    else:raise AssertionError('Existing joined file overwritten')
    check('reunifier_protects_existing_output',True)
    part=transport/parts['parts'][0]['name']
    with part.open('r+b') as stream:stream.write(b'!')
    try:join(metadata,transport/'invalid.zip')
    except AssertionError:pass
    else:raise AssertionError('Corrupt transport part accepted')
    check('reunifier_rejects_corrupt_part',True)
    small=split(candidate,directory/'small_transport')
    check('under_threshold_no_unnecessary_parts',small['split_required'] is False)
    plan={'schema':'CPC7.clean-plan.v1','commands':[{'id':'only_help','argv':['{python}','-I','--help']}],
          'assertions':[{'path':'test.json','equals':{'/deep/value':True}}]}
    validate_plan(plan);check('clean_plan_JSON_pointer_assertions',pointer({'deep':{'value':True}},'/deep/value') is True)
    assert source_cut=={path.name:sha(path) for path in sorted(HERE.glob('*.py'))},'Packaging source changed while tests ran'
    result={'schema':'CPC7.packaging-technical.v1','status':'VERIFIED',
      'checks':checks,'native_worlds_executed':0,'classification':'SYNTHETIC_ENGINEERING_ONLY',
      'source_sha256':sha(Path(__file__)),'kernel_fixture_source_sha256':sha(a.kernel_source),
      'executed_sources':source_cut,'executed_source_copies':'validation/packaging/executed_sources/'+directory.name}
    put(directory/'TECHNICAL_REPORT.json',result)
    put(ROOT/'_delivery/proofs'/('PACKAGING_'+directory.name.upper()+'.json'),result)
    print(json.dumps({'status':'VERIFIED','checks':len(checks),'native_worlds_executed':0},indent=2))

if __name__=='__main__':main()
