# -*- coding: utf-8 -*-
"""

@author: Yi Zhang.
         Department of Aerodynamics
         Faculty of Aerospace Engineering
         TU Delft, Delft, Netherlands

"""
import sys
if './' not in sys.path: sys.path.append('./')
from _2dCSCG.forms.standard._0_form.outer.special.main import _0Form_Outer_Special
from _2dCSCG.forms.standard._0_form.base import _0Form_BASE

class _2dCSCG_0Form_Outer(_0Form_BASE):
    """
    Standard outer 0-form.

    :param mesh:
    :param space:
    :param is_hybrid:
    :param numbering_parameters:
    :param name:
    """
    def __init__(self, mesh, space, is_hybrid=True,
        numbering_parameters='Naive',  name='outer-oriented-0-form'):
        super().__init__(mesh, space, is_hybrid, 'outer', numbering_parameters, name)
        self._k_ = 0
        self.standard_properties.___PRIVATE_add_tag___('2dCSCG_standard_outer_0form')
        self.standard_properties.___PRIVATE_add_tag___('2dCSCG_standard_0form')
        self._special_ = _0Form_Outer_Special(self)
        self.___PRIVATE_reset_cache___()
        self._freeze_self_()

    @property
    def special(self):
        return self._special_


    def ___PRIVATE_reset_cache___(self):
        super().___PRIVATE_reset_cache___()









if __name__ == '__main__':
    # mpiexec -n 4 python _2dCSCG\forms\standard\_0_form\outer\main.py

    from _2dCSCG.main import MeshGenerator, SpaceInvoker, FormCaller, ExactSolutionSelector

    mesh = MeshGenerator('crazy', c=0.3)([10,10])
    # mesh = MeshGenerator('chp1',)([2,2])
    space = SpaceInvoker('polynomials')([('Lobatto',3), ('Lobatto',4)])
    FC = FormCaller(mesh, space)
    ES = ExactSolutionSelector(mesh)('sL:sincos1')
    f0 = FC('0-f-o', is_hybrid=True)
    f0.TW.func.do.set_func_body_as(ES, 'potential')

    f0.TW.current_time = 0
    f0.TW.do.push_all_to_instant()
    f0.discretize()
    print(f0.error.L())
