"""B1 exact observed-key memory and B2 small continual replay learner.

Neither learner reads files, seeds of environments, targets, or teaching logs.
Only the local random generator for model initialization/replay is accessible.
Both learn from a public paired consequence passed to observe().
"""
from __future__ import annotations
import math, random


def canonical(stimulus):
    allowed={'form_id','context_id','events'}
    if not isinstance(stimulus,dict) or set(stimulus)-allowed:raise ValueError('Undeclared stimulus field')
    if type(stimulus.get('form_id')) is not str or type(stimulus.get('context_id')) is not int:raise ValueError('Malformed observable key')
    events=stimulus.get('events',[])
    if not isinstance(events,list) or len(events) not in (0,2):raise ValueError('Zero or two ordered slots required')
    for event in events:
        if set(event)!= {'token_id','t_rel'} or type(event['token_id']) is not str or type(event['t_rel']) is not int or not 0<=event['t_rel']<=1000:raise ValueError('Malformed ordered event')
    return stimulus['form_id'],stimulus['context_id'],tuple(e['token_id'] for e in events)


class B1:
    """Last paired consequence per explicitly engineered observable key."""
    kind='B1_OBSERVED_RELATION_MEMORY'
    def __init__(self,interface,config=None):
        self.interface=dict(interface);self.table={};self.counters={'training_examples':0,'gradient_steps':0,'gradient_examples':0,'replay_examples':0}
    def observe(self,stimulus,consequence):
        if type(consequence) is not int or consequence not in (-1,1):raise ValueError('Observable consequence must be a declared class')
        key=canonical(stimulus);self.table[key]=consequence;self.counters['training_examples']+=1
    def predict(self,stimulus):
        key=canonical(stimulus);value=self.table.get(key)
        return {'state':'RESPONSE' if value is not None else 'UNSEEN_KEY','response':value,'probability_positive':None}
    def state(self):
        return {'schema':'CPC7.B1.state.v1','kind':self.kind,'interface':self.interface,
                'table':[[k[0],k[1],list(k[2]),v] for k,v in sorted(self.table.items())], 'counters':self.counters.copy()}
    @classmethod
    def restore(cls,state):
        if state.get('schema')!='CPC7.B1.state.v1':raise ValueError('Foreign memory state')
        obj=cls(state['interface']);obj.table={(f,c,tuple(e)):y for f,c,e,y in state['table']};obj.counters=dict(state['counters']);return obj


class Encoder:
    """Prepared one-hot identities, positional slots and fixed time scaling."""
    def __init__(self,interface):
        self.forms=list(interface['forms']);self.contexts=list(interface['contexts']);self.tokens=list(interface.get('tokens',[]))
        self.dim=len(self.forms)+len(self.contexts)+(2*len(self.tokens)+2 if self.tokens else 0)
    def __call__(self,stimulus):
        form,context,tokens=canonical(stimulus)
        if form not in self.forms or context not in self.contexts:raise ValueError('Stimulus outside frozen interface')
        x=[0.0]*self.dim;x[self.forms.index(form)]=1.0;x[len(self.forms)+self.contexts.index(context)]=1.0
        if self.tokens:
            if len(tokens)!=2 or any(t not in self.tokens for t in tokens):raise ValueError('Unknown token or missing ordered slots')
            offset=len(self.forms)+len(self.contexts)
            for slot,event in enumerate(stimulus['events']):
                x[offset+slot*len(self.tokens)+self.tokens.index(event['token_id'])]=1.0
                x[offset+2*len(self.tokens)+slot]=event['t_rel']/16.0
        return x


class B2:
    """Two-layer tanh/sigmoid MLP with supervised uniform FIFO replay.

    No continual-backpropagation replacement or pretrained representation is
    claimed. Each gradient step has the same configured sample budget; the
    no-replay arm uses only repetitions of its current actual example.
    """
    kind='B2_SMALL_CONTINUAL_MLP'
    def __init__(self,interface,config):
        self.interface=dict(interface);self.config=dict(config);self.encoder=Encoder(interface)
        self.rng=random.Random(config['model_seed']);d=self.encoder.dim;h=int(config['hidden'])
        if not 1<=h<=64 or not 1<=d<=128:raise ValueError('Finite MLP size exceeded')
        self.w1=[[self.rng.uniform(-math.sqrt(6/(d+h)),math.sqrt(6/(d+h))) for _ in range(d)] for _ in range(h)]
        self.b1=[0.0]*h;self.w2=[self.rng.uniform(-math.sqrt(6/(h+1)),math.sqrt(6/(h+1))) for _ in range(h)];self.b2=0.0
        self.buffer=[];self.counters={'training_examples':0,'gradient_steps':0,'gradient_examples':0,'replay_examples':0}
    def forward(self,x):
        h=[math.tanh(sum(w*v for w,v in zip(row,x))+b) for row,b in zip(self.w1,self.b1)]
        z=sum(w*v for w,v in zip(self.w2,h))+self.b2
        p=1/(1+math.exp(-z)) if z>=0 else math.exp(z)/(1+math.exp(z))
        return h,p
    def loss(self,x,y):
        p=self.forward(x)[1];target=(y+1)/2
        return -target*math.log(max(p,1e-300))-(1-target)*math.log(max(1-p,1e-300))
    def gradient(self,x,y):
        h,p=self.forward(x);err=p-(y+1)/2;g2=[err*v for v in h]
        gh=[err*w*(1-v*v) for w,v in zip(self.w2,h)]
        return [[v*g for v in x] for g in gh],gh,g2,err
    def step(self,batch):
        h=len(self.w1);d=len(self.w1[0]);g1=[[0.0]*d for _ in range(h)];gb=[0.0]*h;g2=[0.0]*h;gout=0.0
        for x,y in batch:
            a,b,c,e=self.gradient(x,y);gout+=e
            for j in range(h):
                gb[j]+=b[j];g2[j]+=c[j]
                for i in range(d):g1[j][i]+=a[j][i]
        rate=self.config['learning_rate']/len(batch);decay=self.config.get('l2',0.0)
        for j in range(h):
            self.b1[j]-=rate*gb[j];self.w2[j]-=rate*g2[j]+self.config['learning_rate']*decay*self.w2[j]
            for i in range(d):self.w1[j][i]-=rate*g1[j][i]+self.config['learning_rate']*decay*self.w1[j][i]
        self.b2-=rate*gout;self.counters['gradient_steps']+=1;self.counters['gradient_examples']+=len(batch)
    def observe(self,stimulus,consequence):
        if type(consequence) is not int or consequence not in(-1,1):raise ValueError('Declared consequence required')
        x=self.encoder(stimulus);current=(x,consequence);batch_size=self.config['batch_size'];capacity=self.config['replay_capacity']
        for _ in range(self.config['steps_per_experience']):
            if capacity and self.buffer:
                batch=[current]+[self.rng.choice(self.buffer) for _ in range(batch_size-1)]
                self.counters['replay_examples']+=batch_size-1
            else:batch=[current]*batch_size
            self.step(batch)
        self.counters['training_examples']+=1
        if capacity:
            self.buffer.append(current)
            if len(self.buffer)>capacity:self.buffer.pop(0)
    def predict(self,stimulus):
        p=self.forward(self.encoder(stimulus))[1]
        if not math.isfinite(p):return {'state':'NUMERICAL_FAILURE','response':None,'probability_positive':None}
        return {'state':'RESPONSE','response':1 if p>=0.5 else -1,'probability_positive':p}
    def state(self):
        return {'schema':'CPC7.B2.state.v1','kind':self.kind,'interface':self.interface,'config':self.config,
                'w1':self.w1,'b1':self.b1,'w2':self.w2,'b2':self.b2,'buffer':self.buffer,
                'rng':self.rng.getstate(),'counters':self.counters.copy()}
    @classmethod
    def restore(cls,state):
        if state.get('schema')!='CPC7.B2.state.v1':raise ValueError('Foreign MLP state')
        obj=cls(state['interface'],state['config'])
        for key in ('w1','b1','w2','b2','buffer'):setattr(obj,key,state[key])
        def tuplify(x):return tuple(tuplify(v) for v in x) if isinstance(x,list) else x
        obj.rng.setstate(tuplify(state['rng']));obj.counters=dict(state['counters']);return obj


def selftest():
    interface={'forms':['L01','L02'],'contexts':[0]};cfg={'hidden':4,'model_seed':7,'learning_rate':0.1,
        'steps_per_experience':64,'batch_size':4,'replay_capacity':16,'l2':0.0}
    m=B2(interface,cfg);x=m.encoder({'form_id':'L01','context_id':0});g=m.gradient(x,1);eps=1e-6;checks=[]
    for name,j,i,expected in [('w1',0,0,g[0][0][0]),('b1',0,None,g[1][0]),('w2',0,None,g[2][0]),('b2',None,None,g[3])]:
        if name=='w1':old=m.w1[j][i];m.w1[j][i]=old+eps
        elif name=='b2':old=m.b2;m.b2=old+eps
        else:old=getattr(m,name)[j];getattr(m,name)[j]=old+eps
        hi=m.loss(x,1)
        if name=='w1':m.w1[j][i]=old-eps
        elif name=='b2':m.b2=old-eps
        else:getattr(m,name)[j]=old-eps
        lo=m.loss(x,1)
        if name=='w1':m.w1[j][i]=old
        elif name=='b2':m.b2=old
        else:getattr(m,name)[j]=old
        error=abs((hi-lo)/(2*eps)-expected);checks.append(error);assert error<1e-7
    before=m.loss(x,1);m.observe({'form_id':'L01','context_id':0},1);after=m.loss(x,1);assert after<before and after<0.1
    b=B1(interface);assert b.predict({'form_id':'L01','context_id':0})['response'] is None
    b.observe({'form_id':'L01','context_id':0},-1);b.observe({'form_id':'L02','context_id':0},1);b.observe({'form_id':'L01','context_id':0},1)
    assert b.predict({'form_id':'L01','context_id':0})['response']==1 and b.predict({'form_id':'L02','context_id':0})['response']==1
    for model in (b,m):
        restored=type(model).restore(model.state());assert model.predict({'form_id':'L01','context_id':0})==restored.predict({'form_id':'L01','context_id':0})
    return {'gradient_max_abs_error':max(checks),'single_example_loss_before':before,'single_example_loss_after':after,
            'mutable_memory_retains_other_key':True,'restore_exact_prediction':True,'passed':True}
