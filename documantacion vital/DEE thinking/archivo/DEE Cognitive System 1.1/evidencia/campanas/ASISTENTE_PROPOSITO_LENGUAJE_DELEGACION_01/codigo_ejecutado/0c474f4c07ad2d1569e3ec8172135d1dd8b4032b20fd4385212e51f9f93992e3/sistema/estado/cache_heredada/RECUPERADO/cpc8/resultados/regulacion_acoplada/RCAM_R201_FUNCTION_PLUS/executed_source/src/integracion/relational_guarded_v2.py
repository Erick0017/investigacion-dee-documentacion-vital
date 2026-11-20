"""Second prepared guard geometry, keeping a Moore-26 margin from live contact.

V1 x20 support intercepted the live contact carrier before206. Here four
supports at ten-step cue candidates have X18/22, two sites away from that
carrier's X20 route. Earlier incoming contact phases are at least fourY away.
This is another preparation, never a modification of an old individual's RAW.
"""
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata
from integracion.relational_social import SocialEnsembleSession,prepare_social_ensemble
from integracion.relational_pair import move

def prepare_guarded_v2(*,guard_mode='onpath',**options):
 if guard_mode not in('onpath','offpath'):raise ValueError('Prepared guard contrast')
 r,g=prepare_social_ensemble(**options);placements=list(r.placements);sites=[]
 for q in g['joint_names'].values():
  site=move(q['delivery_site'],q['name_cue_direction'],10)
  if guard_mode=='offpath':site=move(site,(0,1,0),28)
  if site in sites:continue
  if any((p.site.x,p.site.y,p.site.z)==tuple(site)for p in placements):raise ValueError('Initial guard overlap')
  p=d.InitialPlacement();p.site=d.Coordinate(*site);p.raw=d.pack_record(1,0,0,0,0,4);p.clock=0;p.role='Fixed postconvergence cue-product interceptionV2 '+guard_mode;placements.append(p);sites.append(site)
 r.placements=placements;g['residual_guard']={'version':2,'mode':guard_mode,'sites':sites,'lead_from_cue':10,'prepared_before_T0':True,'clock':'0','semantic':4,'load':0,'hypothesized_contact_tick':224,'modality':'FIXED_PREPARED_REGULATION_NOT_LEARNED_POLICY','reason':'V1g8 sat on live contactX20 route. V2g10 keeps Moore margin from that route and targets postconvergence unused cue products.'}
 g['resources']['initial_material_sites']=len(placements);g['representation_version']='2+mode_social1+guard2';r.options={'CPC8R.relational_pair.geometry':encode_metadata(g)};return r,g

class GuardedV2Session(SocialEnsembleSession):
 @classmethod
 def create(cls,identifier='GUARDED_V2',guard_mode='onpath',**options):
  r,g=prepare_guarded_v2(guard_mode=guard_mode,**options);return cls(d.OrganizationalWorld.create(r),g,identifier=identifier)
