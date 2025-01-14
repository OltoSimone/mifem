# -*- coding: utf-8 -*-


from screws.freeze.base import FrozenOnly
from objects.CSCG._3d.forms.edge._0eg.discretize.standard_scalar import _3dCSCG_Edge0Form_Discretize_StandardScalar




class _3dCSCG_Edge0Form_Discretize(FrozenOnly):
    """"""
    def __init__(self, ef):
        """"""
        self._ef_ = ef
        self._standard_scalar_ = _3dCSCG_Edge0Form_Discretize_StandardScalar(ef)
        self._freeze_self_()


    def __call__(self, update_cochain=True, target='func'):
        """
        Discretize the current function (a scalar field) to cochain.

        It is actually a wrapper of multiple methods that discretize functions of different types (a scalar
        field can be defined and represented in different ways in `python`, right?).

        :param bool update_cochain: (`default`: ``True``) If we update cochain with the output? Sometimes we
            may do not want to do so since we just want to use this method do some external jobs.
        :param target:
        :return: The cochain.
        :rtype: Its type can be different according to the particular discretize method.
        """
        if target == 'func':
            if self._ef_.TW.func.body.__class__.__name__ == '_3dCSCG_ScalarField':
                if self._ef_.func.ftype == 'standard':
                    return self._standard_scalar_(update_cochain=update_cochain, target = 'func')
                else:
                    raise NotImplementedError(f"3dCSCG 0-edge cannot (target func) discretize "
                                              f"_3dCSCG_ScalarField of ftype={self._ef_.func.ftype}")

            else:
                raise NotImplementedError(f'3dCSCG 0-edge can not (target func) '
                                          f'discretize {self._ef_.TW.func.body.__class__}.')

        else:
            raise NotImplementedError(f"3dCSCG 0-edge cannot discretize while targeting at {target}.")