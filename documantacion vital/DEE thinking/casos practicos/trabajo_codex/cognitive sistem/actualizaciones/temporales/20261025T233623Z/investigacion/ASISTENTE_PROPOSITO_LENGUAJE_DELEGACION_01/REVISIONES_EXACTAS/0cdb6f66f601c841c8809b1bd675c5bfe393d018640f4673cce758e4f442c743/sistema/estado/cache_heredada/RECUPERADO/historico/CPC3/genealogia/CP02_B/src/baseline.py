"""Conventional persistence predictor with exactly the supplied sensor stream."""
class PersistencePredictor:
    def __init__(self):self.last=None
    def observe(self,sensor,reference_branch=False):
        if sensor not in ('A','B'):raise ValueError('sensor A|B')
        if not reference_branch:self.last=sensor=='A'
    def predict(self):return [False,True] if self.last is None else [self.last]
