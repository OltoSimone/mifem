
from screws.decorators.accepts import accepts
import numpy as np



class StraightLine(object):
    @accepts('self', (tuple, list), (tuple, list))
    def __init__(self, start_point, end_point):
        assert np.shape(start_point) == np.shape(end_point) == (2,)
        self.x1, self.y1 = start_point
        self.x2, self.y2 = end_point

    # o in [0, 1]
    def _gamma(self, o):
        return self.x1 + o* (self.x2 - self.x1), self.y1 + o * (self.y2 - self.y1)

    def _dgamma(self, o):
        return (self.x2 - self.x1) * np.ones(np.shape(o)), (self.y2 - self.y1) * np.ones(
            np.shape(o))

    def __call__(self):
        return self._gamma, self._dgamma