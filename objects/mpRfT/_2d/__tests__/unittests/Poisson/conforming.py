# -*- coding: utf-8 -*-
"""
@author: Yi Zhang
@contact: zhangyi_aero@hotmail.com
@time: 2022/06/17 7:28 PM
"""
import sys

if './' not in sys.path: sys.path.append('./')
from screws.miscellaneous.miprint import miprint
from __init__ import rfT2, tools


def test_mpRfT2_conforming():
    """"""
    miprint(f"-sr- [test_mpRfT2_conforming] ... ", flush=True)

    pB = ['Upper', 'Down', 'Left', 'Right']

    K = 2
    N = 5
    c = 0.

    rfd = None
    # rfd = {'0-0':N, '0-1':N, '0-2':N, '0-3':N}

    MESH = rfT2.mesh('crazy', c=c)([K, K], N, rfd=rfd)
    FC = rfT2.form(MESH)
    ES = rfT2.exact_solution(MESH)('Poisson:sincos1')

    p = FC('2-f-o', name='potential')
    u = FC('1-f-o', name='velocity')
    f = FC('2-f-o', name='source')

    t = FC('nst', ndp=-1, name='trace')

    t.BC.valid_boundaries = pB

    f.analytic_expression = ES.status.source_term
    f.analytic_expression.current_time = 0
    f.discretization()

    M2 = p.matrices.mass
    M1 = u.matrices.mass
    E21 = u.matrices.incidence
    E12 = E21.T

    B = u.boundary_integrate(t)
    BT = B.T

    E12M2 = E12 @ M2

    A = tools.linalg.bmat(([M1, E12M2,  -B],
                           [E21, None, None],
                           [BT , None, None]))
    A.gathering_matrices = ([u, p, t], [u, p, t])

    B0 = tools.linalg.EWC_ColumnVector(u)
    B1 = - f.cochain.EWC
    B2 = tools.linalg.EWC_ColumnVector(t)
    B = tools.linalg.concatenate([B0, B1, B2])
    B.gathering_matrix = (u, p, t)

    LS = tools.linalg.LinearSystem(A, B)
    LS.customize.apply_strong_BC(2, 2, t.BC.partial_cochain)

    results = LS.solve('direct')()[0]
    results.do.distributed_to(u, p, t)

    u.analytic_expression = ES.status.velocity
    u.analytic_expression.current_time = 0
    u_error = u.error.L()

    p.analytic_expression = ES.status.potential
    p.analytic_expression.current_time = 0
    p_error = p.error.L()

    assert u_error < 0.0003
    assert p_error < 7e-5

    return 1













if __name__ == "__main__":
    # mpiexec -n 4 python objects/mpRfT/_2d/__tests__/unittests/Poisson/conforming.py
    test_mpRfT2_conforming()
