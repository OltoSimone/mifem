# -*- coding: utf-8 -*-
"""
@author: Yi Zhang
@contact: zhangyi_aero@hotmail.com
@time: 
"""
import sys

if './' not in sys.path: sys.path.append('./')

from screws.freeze.base import FrozenOnly
from objects.mpRfT._2d.mesh.do.find import mpRfT2_Mesh_Do_Find


class mpRfT2_Mesh_Do(FrozenOnly):
    """"""
    def __init__(self, mesh):
        """"""
        self._mesh_ = mesh
        self._find_ = None
        self._freeze_self_()

    @property
    def find(self):
        """"""
        if self._find_ is None:
            self._find_ = mpRfT2_Mesh_Do_Find(self._mesh_)
        return self._find_

    def evolve(self):
        """Applying all the refinements to the cscg mesh to make a new mpRfT2 mesh."""
        rfd = self._mesh_.refinements.future.rfd
        return self._mesh_.__class__(self._mesh_.cscg, self._mesh_.dN, rfd)




if __name__ == '__main__':
    # mpiexec -n 4 python objects/mpRfT/_2d/mesh/do/main.py
    pass