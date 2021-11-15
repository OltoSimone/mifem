
import sys
if './' not in sys.path: sys.path.append('./')

from _3dCSCG.ADF.trace.main import _3dCSCG_Algebra_DUAL_Trace_Form


class _1_Algebra_DUAL_Trace(_3dCSCG_Algebra_DUAL_Trace_Form):
    """
    Dual trace 1-form.

    :param mesh:
    :param space:
    :param orientation:
    :param name:
    """
    def __init__(self, prime, mesh, space, orientation='outer', name=None):
        """"""
        if name is None: name = orientation + '-oriented-1-AD-Trace'
        super().__init__(3, mesh, space, orientation, name)
        self._prime_ = prime
        self._k_ = 1
        self.standard_properties.___PRIVATE_add_tag___('3dCSCG_standard_algebra_dual_1trace')
        self.RESET_cache()
        self._freeze_self_()




    def RESET_cache(self):
        """"""
        super().RESET_cache()






if __name__ == "__main__":
    # mpiexec -n 6 python _3dCSCG\ADF\trace\_1_AD_trace.py
    from _3dCSCG.main import MeshGenerator, SpaceInvoker, FormCaller, ExactSolutionSelector

    # mesh = MeshGenerator('bridge_arch_cracked')([8,9,7], EDM='SWV0', show_info=True)
    mesh = MeshGenerator('crazy')([3, 3, 3], EDM=None, show_info=True)
    space = SpaceInvoker('polynomials')([('Lobatto',2), ('Lobatto',1), ('Lobatto',2)], show_info=True)
    # es = ExactSolutionSelector(mesh)('icpsNS:still', show_info=True)
    # ke0 = es.status.kinetic_energy(0)
    # he0 = es.status.helicity(0)


    FC = FormCaller(mesh, space)
    df3 = FC('1-adt', numbering_parameters={'scheme_name': 'Naive', })

    es = ExactSolutionSelector(mesh)('icpsNS:sincosRD')

    # df3.prime.TW.func.DO.set_func_body_as(es, 'pressure')
    # df3.prime.TW.current_time = 0
    # df3.prime.TW.DO.push_all_to_instant()
    # df3.prime.DO.discretize()