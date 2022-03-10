

from screws.freeze.inheriting.frozen_only import FrozenOnly


class _2dCSCG_TraceMatrices(FrozenOnly):
    def __init__(self, tf):
        self._tf_ = tf
        self._N_ = None
        self._freeze_self_()

    @property
    def trace(self):
        return self._tf_.coboundary.trace_matrix