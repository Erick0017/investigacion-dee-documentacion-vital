"""Conventional participants. No evaluator targets, future events or DEE imports.

The replay buffer contains ONLY the most recently experienced observation for
each opaque form. Revision is another observed event, not a free correction.
Queries run the ordinary dictionary or MLP forward pass, respectively.
"""
from __future__ import annotations
import math
import random


class RelationshipDictionary:
    def __init__(self, count=65, seed=0, **unused):
        self.count=count; self.memory={}; self.experiences=0
    def experience(self, form, observation):
        assert 0 <= form < self.count and observation in (-1,1)
        self.memory[form]=observation; self.experiences+=1
    def query(self, form):
        value=self.memory.get(form)
        return {"value":value,"status":"OBSERVED_RELATION" if value is not None else "UNOBSERVED", "score":None}
    def state(self):
        return {"kind":"dictionary","count":self.count,"memory":self.memory,"experiences":self.experiences}
    @classmethod
    def restore(cls,state):
        x=cls(state["count"]);x.memory={int(k):v for k,v in state["memory"].items()};x.experiences=state["experiences"];return x


class ReplayMLP:
    """One-hot -> tanh hidden -> logistic scalar; finite latest-observation replay.

Sparse one-hot SGD trains the relevant input row and all shared output weights.
One quarter of updates revisit the new observation; other updates uniformly
sample the bounded replay buffer. No labels are consulted by query().
"""
    def __init__(self,count=65,seed=0,hidden=24,updates=256,learning_rate=0.08):
        self.count=count;self.seed=seed;self.hidden=hidden;self.updates=updates;self.learning_rate=learning_rate
        self.rng=random.Random(seed);self.buffer={};self.experiences=0;self.replay_presentations=0
        self.w=[[self.rng.uniform(-.15,.15) for _ in range(hidden)] for _ in range(count)]
        self.b=[0.]*hidden;self.v=[self.rng.uniform(-.15,.15) for _ in range(hidden)];self.c=0.
    def forward(self,form):
        h=[math.tanh(a+b) for a,b in zip(self.w[form],self.b)]
        z=max(-40.,min(40.,self.c+sum(a*b for a,b in zip(h,self.v))))
        return h,1./(1.+math.exp(-z))
    def experience(self,form,observation):
        assert 0 <= form < self.count and observation in (-1,1)
        self.buffer[form]=observation;self.experiences+=1
        keys=tuple(self.buffer)
        for step in range(self.updates):
            j=form if step%4==0 else self.rng.choice(keys)
            target=(self.buffer[j]+1)/2
            h,p=self.forward(j);g=p-target;lr=self.learning_rate
            old=self.v[:]
            self.c-=lr*g
            for k in range(self.hidden):
                self.v[k]-=lr*g*h[k]
                d=g*old[k]*(1.-h[k]*h[k])
                self.w[j][k]-=lr*d;self.b[k]-=lr*d
            self.replay_presentations+=1
    def query(self,form):
        _,score=self.forward(form)
        return {"value":1 if score>=.5 else -1,"score":score,"status":"MLP_FORWARD"}
    def state(self):
        return {"kind":"mlp","count":self.count,"seed":self.seed,"hidden":self.hidden,"updates":self.updates,
            "learning_rate":self.learning_rate,"w":self.w,"b":self.b,"v":self.v,"c":self.c,
            "buffer":self.buffer,"experiences":self.experiences,"replay_presentations":self.replay_presentations,
            "rng_state":self.rng.getstate()}
    @classmethod
    def restore(cls,state):
        x=cls(state["count"],state["seed"],state["hidden"],state["updates"],state["learning_rate"])
        for k in ("w","b","v","c","experiences","replay_presentations"):setattr(x,k,state[k])
        x.buffer={int(k):v for k,v in state["buffer"].items()}
        def tuplify(a):return tuple(tuplify(z) for z in a) if isinstance(a,(list,tuple)) else a
        x.rng.setstate(tuplify(state["rng_state"]));return x
