"""Portable arithmetic audit of recorded R03 local fields; never runs DEE."""
from pathlib import Path
import argparse,hashlib,json

KERNEL_SHA='fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31'


def require(value,message):
    if not value:raise ValueError(message)


def decode(row):
    raw=int(row['RAW']);ds=[(raw>>shift)&15 for shift in(48,52,56)]
    result={'state':raw&0xffffffff,'s_reg':(raw>>32)&65535,
            'semantic':raw>>60,'direction':[v-16 if v&8 else v for v in ds]}
    require(all(row[k]==v for k,v in result.items()),'Recorded field disagrees with RAW:'+str(row['site']))
    return result


def recalculate(evidence_bytes,source_bytes):
    require(hashlib.sha256(source_bytes).hexdigest()==KERNEL_SHA,'Frozen kernel source changed')
    e=json.loads(evidence_bytes);q=e['q'];frames={f['relative_q']:f for f in e['selected_frames']}
    require(set(frames)=={6,7,8,9,10},'Five predetermined frames required')
    for offset,f in frames.items():
        require(f['tick']==q+offset,'Recorded tick mismatch')
        for rows in(f['fixed_sites'],f['Moore27_contact56']):
            for row in rows:decode(row)
    def pick(offset,site):
        rows=[r for r in frames[offset]['fixed_sites']if r['site']==list(site)]
        require(len(rows)==1,'Predetermined observed site missing');return rows[0]
    before=frames[7];region={tuple(r['site']):dict(r)for r in before['Moore27_contact56']}
    require(len(region)==27,'Complete Moore27 required')
    require(int(pick(7,(52,48,56))['RAW'])==0,'Contact destination was not vacant')
    request=e['actuator_request'];receipt=request['receipt']
    require(request['site']==[53,48,56]and request['direction']==[-1,0,0]and request['payload']==0,'Fixed actuator contract differs')
    require(receipt['status']=='applied'and receipt['requested_tick']==receipt['effective_tick']==q+7,'Actual applied actuator receipt required')
    require(int(pick(7,(53,48,56))['RAW'])==0,'Actuator site occupied before boundary')
    # This application field is inferred from its admitted event, not an extra measured frame.
    region[(53,48,56)]={'site':[53,48,56],'state':1,'s_reg':0,'semantic':1,'direction':[-1,0,0]}
    incoming=[]
    for site,row in region.items():
        if site==(52,48,56)or row['direction']==[0,0,0]:continue
        if tuple((site[i]+row['direction'][i])%67 for i in range(3))==(52,48,56):incoming.append(row)
    require({tuple(r['site'])for r in incoming}=={(52,48,55),(53,48,56)},'Exact incoming set differs')
    summed=[sum(r['direction'][i]for r in incoming)for i in range(3)]
    direction=[(v>0)-(v<0)for v in summed]
    charge=sum(r['s_reg']for r in incoming)
    require(charge==0 and direction==[-1,0,1],'Frozen reducer arithmetic differs')
    active=[r for site,r in region.items()if site!=(52,48,56)and r['state']>0 and r['semantic']!=5]
    require(len(active)==3,'Unexpected local active count')
    # An odd active count cannot satisfy all opposite pairs of verificar_genesis_xnor.
    require(len(active)%2==1,'XNOR parity statement unavailable')
    observed=[]
    for offset,site in((8,(52,48,56)),(9,(51,48,57)),(10,(50,48,58))):
        row=pick(offset,site)
        require(row['state']==1 and row['semantic']==1 and row['s_reg']==0 and row['direction']==direction,'Observed deflection differs')
        observed.append({'tick':row['clock'],'site':list(site),'RAW':row['RAW']})
    require(pick(8,(52,48,58))['direction']==[0,0,1],'Ahead configuration is not retained as observed')
    require(e['FI_q4']==e['FI_q6']==1,'Original calibrated FI result differs')
    return {'schema':'DEE.PI07.F1.lateral_deflection.portable_recalculation.v1',
      'Native_executed':False,'DEE_imports':False,'new_Native_ticks':0,
      'evidence_sha256':hashlib.sha256(evidence_bytes).hexdigest(),'kernel_source_sha256':KERNEL_SHA,
      'fixed_recorded_frames':5,'RAW_fields_decoded':True,'complete_local_Moore27':True,
      'post_application_field_reconstructed_from_actual_receipt':True,'extra_observed_application_frame':False,
      'exact_incoming_sites':[r['site']for r in incoming],'incoming_vector_sum':summed,
      'incoming_charge_sum':charge,'recorded_product_direction':direction,
      'local_active_count_after_application':len(active),'XNOR_all_opposite_pairs_false_by_odd_count':True,
      'observed_three_frame_local_continuity':observed,'ahead_plusZ_configuration_still_observed':True,
      'calibrated_FI_q4_q6':[e['FI_q4'],e['FI_q6']],
      'operator_forced_action':e['operator_forced_action'],
      'scope':'Audit of included local observations and an admitted event, not a Native replay or universal causal simulation. Deflection is observed; annihilation, unique particle lineage, discovery and learned selection are not claimed. Comparison to NoPulse is a separate primary experiment.'}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--evidence',type=Path,required=True)
    ap.add_argument('--source',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();require(not a.out.exists(),'Output exists')
    result=recalculate(a.evidence.read_bytes(),a.source.read_bytes())
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'out':str(a.out),'recorded_deflection_check':True,'Native_ticks':0},ensure_ascii=False))


if __name__=='__main__':main()
