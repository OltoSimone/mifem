# -*- coding: utf-8 -*-
"""
@author: Yi Zhang
@contact: zhangyi_aero@hotmail.com
@time: 
"""
import sys

if './' not in sys.path: sys.path.append('./')

from screws.freeze.base import FrozenOnly

class _3nCSCG_SubCells(FrozenOnly):
    """"""
    def __init__(self, cell):
        """"""
        self._cell_ = cell
        self._individual_sub_cells_ = dict()
        self._freeze_self_()


    def __getitem__(self, i):
        """"""
        if i in self._individual_sub_cells_:
            pass
        elif isinstance(i, int) and 0 <= i < 8:
            self._individual_sub_cells_[i] = self._cell_.__class__(self._cell_.mesh,
                                                                   self._cell_.level+1,
                                                                   self._cell_.indices + (i,))
        else:
            raise Exception(f"3d nCSCG_RF2 mesh only have 8 sub-cells in each cell, "
                            f"index={i} for level: >{self._cell_.level+1}< wrong.")

        return self._individual_sub_cells_[i]


if __name__ == '__main__':
    # mpiexec -n 4 python 
    pass
