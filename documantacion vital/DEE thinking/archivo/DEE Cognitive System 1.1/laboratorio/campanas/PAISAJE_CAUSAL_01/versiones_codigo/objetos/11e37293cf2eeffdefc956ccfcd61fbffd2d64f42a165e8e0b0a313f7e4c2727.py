"""Native use of the protected old-bank signal, without a new bridge body.

The alias is a view of the same material, NOT a transplant or new word.
"""
from pathlib import Path
import argparse,sys,json
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system));sys.path.insert(0,str(Path(__file__).parent))
from app.lives import Store
from app.native_tools import physical
from app.process_control import protect_current
from capacidades import espanol_funcional_01 as e,puente_lexico_10 as b,ensenanza_lexica_03 as f
from instrumentos_pc01 import receipts,sha
from dee_thinking.persistence import encode_metadata
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);s=Store(a.system);parent='PC01_APLICACION14_guard';life='PC01_SOCIAL18_'+a.case;s.fork(parent,life,kind='CANDIDATE');data={'case':a.case,'life':life,'parent':s.record(parent),'source_sha256':sha(__file__),'criteria_before':'Use the actual acquiredlexical05d5phase21carrier. Registeronlya metadata view for the already existing native communication preparer, no fieldcopy. Same Runtime and fixed two recipients, source conditioned by its learned history. Cut/sham aftersource, matching/mismatching explicit usertoken. Bmarkerread/action are not independent spatial understanding, role-relativeYO/TU or language grammar. A cut can consume the emitting memory carrier; report that collateral effect.'}
def trial(x):
    data['pre']=physical(x.world,occupation=True);g=e.prepare(x);entry=g['relational_words_v2']['lexical05'];bank=next(q for q in entry['banks']if q['id']=='d5')
    if 21 not in entry['lexical_v3']['learned_phases']:raise ValueError('Sourcephase21wasnotexperiencedbythislife')
    alias='PC01_existing_d5_view';g.setdefault('lexical_bridges_v10',{})[alias]={'schema':'PC01.existing_word_view.v1','hub':bank['hub'],'word_phase':21,'ports':{'query':bank['query']},'codebook':entry['lexical_v3']['codebook'],'taught':True,'after_comprehension':False,'view_of':{'frame':'lexical05','bank':'d5','phase':21,'no_new_matter_or_learned_fields':True},'scope':'Viewadapteronly: actualhistoricalwordstateorabsenceisreadnatively; metadataflagisnotanevidenceverdict'};x.world.runtime.set_snapshot_metadata(e.KEY,encode_metadata(g));data['view_only_physical_identity']=physical(x.world)=={k:data['pre'][k]for k in('N','tick','RAW_sha256','clocks_sha256')}
    requested='cerca'if a.case=='match'else'lejos'if a.case=='mismatch'else None
    data['communication']=b.communicate(x,bridge=alias,communication='PC01_new_receiver18',cut=a.case=='cut',sham=a.case=='sham',request_word=requested)
    if requested is not None:
        # The view shares old material. Do not leave the old API falsely
        # advertised as validated after a consumptive operation through alias.
        g=e.prepare(x);g['relational_words_v2']['lexical05']['lexical_v3']['after_comprehension']=True;x.world.runtime.set_snapshot_metadata(e.KEY,encode_metadata(g));data['shared_source_after_use']='Original lexical API is conservatively marked post-use unvalidated; no silent double-ownership.'
    else:
        data['later_source_use']=f.context(x,frame='lexical05',parameter=5,load=5,phase=21,emit_word_queries=False);data['other_old_forms']=f.query(x,frame='lexical05')
    data['contact']=e.contact_query(x,frame='contactoA');data['free']=e.contact_query(x,frame='freeRepair5');data['post']=physical(x.world,occupation=True);data['receipts']=receipts(x.world.runtime)
    return{'tick':x.tick,'B_words':data['communication']['B_WORDS_DECODED'],'B_actions':data['communication']['B_NATIVE_ACTION_BRANCHES'],'later_source_use':data.get('later_source_use',{}).get('SPANISH_DECODED'),'contact':data['contact']['SPANISH_DECODED'],'free':data['free']['SPANISH_DECODED'],'view_introduces_no_matter':data['view_only_physical_identity']}
data['commit']=s.mutate(life,'PC01_PROTECTED_ACQUIRED_SIGNAL_NATIVE_SOCIAL_USE18',trial);(a.out/'PRIMARIOS.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(data['commit']['result'],ensure_ascii=False))
