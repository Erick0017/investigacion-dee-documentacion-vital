"""Fresh prepared regulation of unused posterior cue products, not attention learned."""
from dee_thinking import _native as d
from dee_thinking.persistence import encode_metadata
from integracion.relational_social import SocialEnsembleSession,prepare_social_ensemble

def prepare_guarded(*,guard_mode='onpath',**options):
 if guard_mode not in('onpath','offpath'):raise ValueError('Explicit prepared guard contrast')
 r,g=prepare_social_ensemble(**options);q=[20,20,14]if guard_mode=='onpath'else[20,48,14]
 placements=list(r.placements)
 if any((p.site.x,p.site.y,p.site.z)==tuple(q)for p in placements):raise ValueError('Guard collides with prepared initial material')
 p=d.InitialPlacement();p.site=d.Coordinate(*q);p.raw=d.pack_record(1,0,0,0,0,4);p.clock=0;p.role='Fixed unused posterior cue convergence interception '+guard_mode;placements.append(p);r.placements=placements
 g['residual_guard']={'mode':guard_mode,'site':q,'clock':'0','raw':str(p.raw),'prepared_before_T0':True,'hypothesized_contact_tick':222,'provenance':'FIXED_DESIGN_NOT_EXPERIENCE_DEPENDENT_POLICY'}
 g['resources']['initial_material_sites']=len(placements);g['representation_version']='2+mode_social1+guard1';r.options={'CPC8R.relational_pair.geometry':encode_metadata(g)}
 return r,g

class GuardedEnsembleSession(SocialEnsembleSession):
 @classmethod
 def create(cls,identifier='GUARDED_ENSEMBLE',guard_mode='onpath',**options):
  r,g=prepare_guarded(guard_mode=guard_mode,**options);return cls(d.OrganizationalWorld.create(r),g,identifier=identifier)
