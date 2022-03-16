import sys


if './' not in sys.path: sys.path.append('./')

from _2dCSCG.APP.exact_solution.status.incompressible_Navier_Stokes.base import incompressibleNavierStokesBase
from numpy import sin, cos, exp, pi


class TaylorGreenVortex(incompressibleNavierStokesBase):
    """
    See Section 5.1 of MEEVC paper.

    """
    def __init__(self, es, nu=0.01):
        """

        :param es:
        :param nu:
        """
        super(TaylorGreenVortex, self).__init__(es, nu)
        #-------- check the domain ---------------------------------------------------------------
        assert self.mesh.domain.name == 'CrazyPeriodic', \
            f"Shear-Layer-Rollup exact solution only works in crazy_periodic domain, " \
            f"now it is {self.mesh.domain.name}."
        bx, by = self.mesh.domain.domain_input.bounds
        assert tuple(bx) == (0, 2) and tuple(by) == (0, 2), \
            f"ShearLayerRollup can only work in [0, 2]^2 periodic domain"
        #-----------------------------------------------------------------------------------------


    def u(self, t, x, y):
        return - sin(pi * x) * cos(pi * y) * exp(-2 * pi**2 * self.nu * t)


    def v(self, t, x, y):
        return cos(pi * x) * sin(pi * y) * exp(-2 * pi**2 * self.nu * t)


    def p(self, t, x, y):
        """In the MEEVC paper, it is wrong, the minus in the exp() is missed there."""
        return 0.25 * (cos(2*pi*x) + cos(2*pi*y)) * exp(- 4 * pi**2 * self.nu * t)


    def fx(self, t, x, y):
        return 0 * x

    def fy(self, t, x, y):
        return 0 * y



if __name__ == '__main__':
    # mpiexec -n 4 python _2dCSCG\APP\exact_solution\status\incompressible_Navier_Stokes\Taylor_Green_vortex.py
    from _2dCSCG.main import MeshGenerator, ExactSolutionSelector
    mesh = MeshGenerator('crazy_periodic', bounds=[[0, 2], [0, 2]], c=0.)([2, 2])
    es = ExactSolutionSelector(mesh)("icpsNS:TGV", show_info=True)

    es.status.body_force.visualize(time=10)