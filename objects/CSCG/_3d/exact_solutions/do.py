# -*- coding: utf-8 -*-
""""""

import numpy as np
from root.config.main import cOmm, MPI
from screws.quadrature import Quadrature
from screws.freeze.base import FrozenOnly


class _3dCSCG_ES_DO(FrozenOnly):
    """"""
    def __init__(self, es):
        self._es_ = es
        self._freeze_self_()


    def compute_Ln_norm_of(self, what, time=0, n=2, quad_degree=None):
        """We compute the :math:`L^n`-norm of the attribute name ``what`` at `time`.

        :param str what:
        :param float time:
        :param int n: We compute :math:`L^n`-norm.
        :param quad_degree:
        :return:
        """
        what = getattr(self._es_.status, what)

        assert self._es_._mesh_ is not None, " <MS> : to compute L2_norm, I need a mesh."
        if quad_degree is None:
            quad_degree = int(np.ceil((500000/self._es_._mesh_.elements.GLOBAL_num)**(1/3)))
            if quad_degree > 20: quad_degree = 20
            quad_degree = (quad_degree, quad_degree, quad_degree)

        if what.ftype == 'standard':

            _Quadrature_ = Quadrature(quad_degree, category='Gauss')
            quad_nodes, quad_weights = _Quadrature_.quad
            quad_nodes = np.meshgrid(*quad_nodes, indexing='ij')

            _, v = what.reconstruct(*quad_nodes, time=time)
            detJ = self._es_.mesh.elements.coordinate_transformation.Jacobian(*quad_nodes)
            LOCAL = 0
            for i in v:
                local = np.sum([vij**n for vij in v[i]], axis=0)
                LOCAL += np.einsum('ijk, ijk, i, j, k -> ', local, detJ[i], *quad_weights, optimize='optimal')
            GLOBAL = cOmm.allreduce(LOCAL, op=MPI.SUM) ** (1/n)
            return GLOBAL

        else:
            raise Exception()

    def generate_random_valid_time_instances(self, amount=None):
        """

        Parameters
        ----------
        amount : None

        Returns
        -------

        """
        return self._es_.status.___PRIVATE_generate_random_valid_time_instances___(
            amount=amount)