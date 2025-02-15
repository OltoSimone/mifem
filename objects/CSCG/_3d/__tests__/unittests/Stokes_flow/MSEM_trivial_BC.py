# -*- coding: utf-8 -*-
"""We test our library with a 3d Stokes flow in a fully periodic domain.

"""

import sys
if './' not in sys.path: sys.path.append('./')

from objects.CSCG._3d.master import MeshGenerator, SpaceInvoker, FormCaller, ExactSolutionSelector
from tools.linear_algebra.elementwise_cache.operators.concatenate.main import concatenate
from tools.linear_algebra.elementwise_cache.operators.bmat.main import bmat
from tools.linear_algebra.elementwise_cache.objects.column_vector.main import EWC_ColumnVector
from tools.linear_algebra.linear_system.main import LinearSystem
from root.config.main import rAnk, mAster_rank



def test_Stokes_MSEM_trivial_BC():
    if rAnk == mAster_rank:
        print(f"STK [test_Stokes_MSEM_trivial_BC] ...", flush=True)

    K = [6, 6, 6]
    N = [2, 2, 2]
    mesh = MeshGenerator('crazy', c=0.0)(K, show_info=True)
    space = SpaceInvoker('polynomials')(N, show_info=True)
    FC = FormCaller(mesh, space)
    es = ExactSolutionSelector(mesh)('Stokes:sincos1')

    w = FC('1-f', is_hybrid=False, name='vorticity')
    u = FC('2-f', is_hybrid=False, name='velocity')
    p = FC('3-f', is_hybrid=False, name='pressure')
    f = FC('2-f', is_hybrid=False, name='body_force')

    w.TW.func.do.set_func_body_as(es, 'vorticity')
    u.TW.func.do.set_func_body_as(es, 'velocity')
    p.TW.func.do.set_func_body_as(es, 'pressure')
    f.TW.func.do.set_func_body_as(es, 'body_force')

    w.TW.current_time = 0
    w.TW.do.push_func_to_instant()
    u.TW.current_time = 0
    u.TW.do.push_func_to_instant()
    p.TW.current_time = 0
    p.TW.do.push_func_to_instant()
    f.TW.current_time = 0
    f.TW.do.push_func_to_instant()
    f.discretize()

    M1 = w.matrices.mass
    M2 = u.matrices.mass
    M3 = p.matrices.mass
    E21 = w.matrices.incidence
    E32 = u.matrices.incidence
    E12 = E21.T
    E23 = E32.T

    A = ([      M1, - E12 @ M2,      None],
         [M2 @ E21,       None, -E23 @ M3],
         [    None,   M3 @ E32,      None],)
    A = bmat(A)

    b0 = EWC_ColumnVector(w)
    b1 = M2 @ f
    b2 = EWC_ColumnVector(p)
    b = concatenate([b0, b1, b2])

    A.gathering_matrices = ([w, u, p], [w, u, p])
    b.gathering_matrix = (w, u, p)
    LS = LinearSystem(A, b)

    results = LS.solve('direct')()[0]

    results.do.distributed_to(w, u, p)

    # w_L2 = w.error.L()
    # u_L2 = u.error.L()
    # p_L2 = p.error.L()
    #
    # if rAnk == mAster_rank:
    #     print(w_L2)
    #     print(u_L2)
    #     print(p_L2)

    assert w.error.L() < 0.4
    assert u.error.L() < 0.05
    assert p.error.L() < 0.03

    return 1



if __name__ == '__main__':
    # mpiexec -n 4 python objects/CSCG/_3d/__tests__/unittests/Stokes_flow/MSEM_trivial_BC.py
    test_Stokes_MSEM_trivial_BC()