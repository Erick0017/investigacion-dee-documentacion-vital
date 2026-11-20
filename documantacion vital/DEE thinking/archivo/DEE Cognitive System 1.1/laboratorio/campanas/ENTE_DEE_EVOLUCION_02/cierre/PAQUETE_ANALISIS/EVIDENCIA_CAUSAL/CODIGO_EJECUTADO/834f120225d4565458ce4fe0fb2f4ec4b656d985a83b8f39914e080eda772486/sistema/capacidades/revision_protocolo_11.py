"""Explicit experimental continuation of prepared native revision ports.

Official4.5revise_form is deliberately limited to its published absolute tick.
This private1.1protocol uses Runtime inputs, not a patched descriptor or engine.
Only the initially configured repertoire revisionform and N131are attempted.
"""
from dee_thinking import _native as d
def revise(session,form,consequence,tick,*,control='treatment',cue=5,teacher=11):
    p=session.preparation
    if session.session_kind!='repertoire'or session.dimension!=131:raise ValueError('OUT_OF_DOMAIN: experimental continued revision requires officialN131repertoire')
    if control not in('treatment','offpath_sham')or type(consequence)is not int or consequence not in(-1,1):raise ValueError('Explicit current consequence and causalcontrol required')
    index=session._index(form)
    if int(p.parameters['revision_interfaces'])!=1 or index!=int(p.parameters['revision_form']):raise ValueError('OUT_OF_DOMAIN: only the initially prepared revisionform')
    if type(tick)is not int or tick<session.tick:raise ValueError('No retrospectivephysicalexperience')
    if any(type(x)is not int or not 0<=x<=65535 for x in(cue,teacher)):raise ValueError('Exact materialloads required')
    label='plus'if consequence==1 else'minus';name=p.forms[index].name;ports=[(name+'.signal',cue),(name+'.event.'+label,teacher),(p.ports['revision.teacher2.'+control+'.'+label],teacher)]
    # Structural preflight only; no global target or current material is read.
    by_name={x.name:x for x in session.world.interfaces}
    for port,payload in ports:
        if port not in by_name:raise ValueError('Preparedrevisionportabsent')
        by_name[port].codec.encode_integer(payload)
    receipts=[session.submit(port,payload,tick)for port,payload in ports]
    return{'INSTRUMENTO':{'modality':'EXPERIMENTAL_1_1_PREPARED_PORT_PROTOCOL_NOT_OFFICIAL_EXTENDED_API','method':'double_teacher','control':control,'requested_tick':tick,'official_published_revision_tick':int(p.ticks['revision_input']),'receipts':receipts,'current_actual_consequence':consequence},'INTERPRETACION':'NoRAW/clocks/manifestedit; allqueuedcarriers evolve through officialv27. Success outside the publishedtick must be demonstrated, not inherited.'}
