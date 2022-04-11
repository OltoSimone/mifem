
from screws.freeze.base import FrozenOnly


class _3dCSCG_Tr_form_DO(FrozenOnly):
    """"""
    def __init__(self, Tr):
        self._Tr_ = Tr
        self._freeze_self_()

    def evaluate_basis_at_meshgrid(self, xi, eta, sigma, compute_xietasigma=True):
        """
        Evaluate the basis functions on ``meshgrid(xi, eta, sigma)``.

        :param xi: A 1d iterable object of floats between -1 and 1.
        :param eta: A 1d iterable object of floats between -1 and 1.
        :param sigma: A 1d iterable object of floats between -1 and 1.
        :type xi: list, tuple, numpy.ndarray
        :type eta: list, tuple, numpy.ndarray
        :type sigma: list, tuple, numpy.ndarray
        :param bool compute_xietasigma: (`default`:``True``) If we compute the
            ``meshgrid(xi, eta, sigma, indexing='ij')``.
        :returns: A tuple of outputs:

            1. (None, tuple) -- ``(xi, eta, sigma)`` after ``meshgrid`` and ``ravel('F')``.
            2. tuple -- The evaluated basis functions.
        """
        return self._Tr_.space.do.evaluate_trace_basis_at_meshgrid(
            self._Tr_.k, xi, eta, sigma, compute_xietasigma=compute_xietasigma)