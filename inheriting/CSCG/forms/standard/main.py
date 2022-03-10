# -*- coding: utf-8 -*-
"""
"""
from inheriting.CSCG.forms.standard.IS import CSCG_standard_form_IS
from inheriting.CSCG.forms.standard.num import CSCG_standard_form_NUM

# noinspection PyUnresolvedReferences
class CSCG_Standard_Form:
    """"""
    def ___init___(self):
        self._IS_ = CSCG_standard_form_IS(self)
        self._num_ = CSCG_standard_form_NUM(self)

    @property
    def GLOBAL_num_dofs(self):
        """(int) Return number of total dofs."""
        return self.numbering.gathering.GLOBAL_num_dofs

    @property
    def orientation(self):
        return self._orientation_

    @property
    def IS(self):
        return self._IS_

    @property
    def num(self):
        return self._num_