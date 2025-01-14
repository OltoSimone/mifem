
from abc import ABC
import numpy as np

class CFGt(ABC):
    """
    Constant function generator: ``CF = CFG(5)()``.

    .. doctest::

        >>> cf = CFGt(10.5)()
        >>> cf(1, 1,1)
        10.5
    """

    def __init__(self, C):
        """ """
        self._C_ = C

    def _constant_func_(self, t, x, y):
        assert np.shape(x) == np.shape(y)
        return self._C_ + np.zeros(np.shape(x)) + 0 * t

    def __call__(self):
        return self._constant_func_






if __name__ == "__main__":
    import doctest
    doctest.testmod()