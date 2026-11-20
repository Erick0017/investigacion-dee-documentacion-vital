"""Declared P0 interception of uncommanded relay products, not online repair.

The selection is geometric and fixed before any response; it does not inspect
a world or infer what content should be returned. Uncovered products remain
explicit. Native causal controls, not this plan, establish any benefit.
"""
def ghost_guards(plans,protected_sites,n=67):
    protected={tuple(p)for p in protected_sites};result={};uncovered=[]
    def move(q,d,k):return tuple((q[i]+d[i]*k)%n for i in range(3))
    def near(q):
        return any(move(q,(x,y,z),1)in protected for x in(-1,0,1)for y in(-1,0,1)for z in(-1,0,1))
    for key,plan in plans.items():
        for index,turn in enumerate(plan['turns']):
            g=turn['without_command_direction']
            if not any(g):uncovered.append({'route':key,'turn':index,'reason':'Stationary product; no moving-line interception claimed'});continue
            options=[]
            for steps in range(4,19):
                site=move(turn['site'],g,steps)
                if near(site):continue
                options.append((steps,site))
            if not options:uncovered.append({'route':key,'turn':index,'reason':'No bounded site clear of all declared protected paths'});continue
            steps,site=options[0];tick=turn['tick']+steps-1;reason={'route':key,'turn':index,'uncommanded_direction':g,'steps':steps,'not_a_unique_lineage_claim':True}
            if site not in result:result[site]={'site':list(site),'tick':tick,'roles':[reason]}
            else:result[site]['tick']=min(result[site]['tick'],tick);result[site]['roles'].append(reason)
    return {'guards':list(result.values()),'uncovered':uncovered,'not_a_global_closed_causal_map':True,'P0_not_acquired_or_adaptive':True}
