# -*- coding: utf-8 -*-
import numpy as np
from screws.freeze.main import FrozenOnly
from screws.numerical._2d_space.Jacobian_21 import NumericalJacobian_xy_t_21


class TransfiniteMapping(FrozenOnly):
    def __init__(self, gamma, dgamma=None):
        """
         y          - 2 +
         ^     _______________
         |    |       R       |
         |    |               |
         |  + |               | +
         |  3 | U           D | 1
         |  - |               | -
         |    |       L       |
         |    |_______________|
         |          - 0 +
         |_______________________> x

        The indices of `gamma` and `dgamma` are as above. And the directs of the
        mappings are indicated as well.

        Parameters
        ----------
        gamma :
            A tuple of the four boundary functions
        dgamma : optional
            A tuple of first derivative of gamma.

        """
        t = np.linspace(0, 1, 12)[1:-1]
        _dict_ = {0: 'L', 1: 'D', 2: 'R', 3: 'U'}
        for i in range(4):
            XY = gamma[i]
            XtYt = dgamma[i]
            NJ21 = NumericalJacobian_xy_t_21(XY)
            assert all(NJ21.check_Jacobian(XtYt, t)), \
                " <TransfiniteMapping> :  '{}' edge mapping or Jacobian wrong.".format(_dict_[i])

        self.gamma = gamma
        self.dgamma = dgamma
        self.gamma1_x0, self.gamma1_y0 = self.gamma[0](0.0)
        self.gamma1_x1, self.gamma1_y1 = self.gamma[0](1.0)
        self.gamma3_x0, self.gamma3_y0 = self.gamma[2](0.0)
        self.gamma3_x1, self.gamma3_y1 = self.gamma[2](1.0)

    def mapping(self, r, s):
        """
        mapping (r, s) = (0, 1)^2 into (x, y) using the transfinite mapping.

        """
        gamma1_xs, gamma1_ys = self.gamma[0](r)
        gamma2_xt, gamma2_yt = self.gamma[1](s)
        gamma3_xs, gamma3_ys = self.gamma[2](r)
        gamma4_xt, gamma4_yt = self.gamma[3](s)
        x = (1 - r) * gamma4_xt + r * gamma2_xt + (1 - s) * gamma1_xs + s * gamma3_xs - \
            (1 - r) * ((1 - s) * self.gamma1_x0 + s * self.gamma3_x0) - r * (
                        (1 - s) * self.gamma1_x1 + s * self.gamma3_x1)
        y = (1 - r) * gamma4_yt + r * gamma2_yt + (1 - s) * gamma1_ys + s * gamma3_ys - \
            (1 - r) * ((1 - s) * self.gamma1_y0 + s * self.gamma3_y0) - r * (
                        (1 - s) * self.gamma1_y1 + s * self.gamma3_y1)
        return x, y

    def mapping_X(self, r, s):
        """
        mapping (r, s) = (0, 1)^2 into (x, y) using the transfinite mapping.

        """
        gamma1_xs, gamma1_ys = self.gamma[0](r)
        gamma2_xt, gamma2_yt = self.gamma[1](s)
        gamma3_xs, gamma3_ys = self.gamma[2](r)
        gamma4_xt, gamma4_yt = self.gamma[3](s)
        x = (1 - r) * gamma4_xt + r * gamma2_xt + (1 - s) * gamma1_xs + s * gamma3_xs - \
            (1 - r) * ((1 - s) * self.gamma1_x0 + s * self.gamma3_x0) - r * (
                        (1 - s) * self.gamma1_x1 + s * self.gamma3_x1)
        return x

    def mapping_Y(self, r, s):
        """
        mapping (r, s) = (0, 1)^2 into (x, y) using the transfinite mapping.

        """
        gamma1_xs, gamma1_ys = self.gamma[0](r)
        gamma2_xt, gamma2_yt = self.gamma[1](s)
        gamma3_xs, gamma3_ys = self.gamma[2](r)
        gamma4_xt, gamma4_yt = self.gamma[3](s)
        y = (1 - r) * gamma4_yt + r * gamma2_yt + (1 - s) * gamma1_ys + s * gamma3_ys - \
            (1 - r) * ((1 - s) * self.gamma1_y0 + s * self.gamma3_y0) - r * (
                        (1 - s) * self.gamma1_y1 + s * self.gamma3_y1)
        return y

    def dx_dr(self, r, s):
        """ """
        gamma2_xt, gamma2_yt = self.gamma[1](s)
        gamma4_xt, gamma_4yt = self.gamma[3](s)
        dgamma1_xds, dgamma1_yds = self.dgamma[0](r)
        dgamma3_xds, dgamma3_yds = self.dgamma[2](r)
        dx_dxi_result = (-gamma4_xt + gamma2_xt + (1 - s) * dgamma1_xds + s * dgamma3_xds +
                         ((1 - s) * self.gamma1_x0 + s * self.gamma3_x0) - (
                                     (1 - s) * self.gamma1_x1 + s * self.gamma3_x1))
        return dx_dxi_result

    def dx_ds(self, r, s):
        """ """
        gamma1_xs, gamma1_ys = self.gamma[0](r)
        gamma3_xs, gamma3_ys = self.gamma[2](r)
        dgamma2_xdt, dgamma2_ydt = self.dgamma[1](s)
        dgamma4_xdt, dgamma4_ydt = self.dgamma[3](s)
        dx_deta_result = ((1 - r) * dgamma4_xdt + r * dgamma2_xdt - gamma1_xs + gamma3_xs -
                          (1 - r) * (-self.gamma1_x0 + self.gamma3_x0) - r * (-self.gamma1_x1 + self.gamma3_x1))
        return dx_deta_result

    def dy_dr(self, r, s):
        """ """
        gamma2_xt, gamma2_yt = self.gamma[1](s)
        gamma4_xt, gamma4_yt = self.gamma[3](s)
        dgamma1_xds, dgamma1_yds = self.dgamma[0](r)
        dgamma3_xds, dgamma3_yds = self.dgamma[2](r)
        dy_dxi_result = (-gamma4_yt + gamma2_yt + (1 - s) * dgamma1_yds + s * dgamma3_yds +
                         ((1 - s) * self.gamma1_y0 + s * self.gamma3_y0) - (
                                     (1 - s) * self.gamma1_y1 + s * self.gamma3_y1))
        return dy_dxi_result

    def dy_ds(self, r, s):
        """ """
        gamma1_xs, gamma1_ys = self.gamma[0](r)
        gamma3_xs, gamma3_ys = self.gamma[2](r)
        dgamma2_xdt, dgamma2_ydt = self.dgamma[1](s)
        dgamma4_xdt, dgamma4_ydt = self.dgamma[3](s)
        dy_deta_result = ((1 - r) * dgamma4_ydt + r * dgamma2_ydt - gamma1_ys + gamma3_ys -
                          (1 - r) * (-self.gamma1_y0 + self.gamma3_y0) - r * (-self.gamma1_y1 + self.gamma3_y1))
        return dy_deta_result
