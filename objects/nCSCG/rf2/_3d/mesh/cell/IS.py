# -*- coding: utf-8 -*-
"""
@author: Yi Zhang
@contact: zhangyi_aero@hotmail.com
@time: 
"""
import sys

if './' not in sys.path: sys.path.append('./')

from screws.freeze.base import FrozenOnly

class _3nCSCG_CellIS(FrozenOnly):
    """"""
    def __init__(self, cell):
        """"""
        self._cell_ = cell
        self._freeze_self_()

    @property
    def refined(self):
        return False if self._cell_.sub_cells is None else True


if __name__ == '__main__':
    # mpiexec -n 4 python 
    pass
