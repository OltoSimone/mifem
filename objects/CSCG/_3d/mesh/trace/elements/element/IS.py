# -*- coding: utf-8 -*-

from screws.freeze.base import FrozenOnly



class _3dCSCG_TraceElement_IS(FrozenOnly):
    """"""
    def __init__(self, element):
        self._element_ = element
        self._sbc_ = None
        self._freeze_self_()


    @property
    def on_periodic_boundary(self):
        """As this property name says."""
        return self._element_._onpb_

    @property
    def shared_by_cores(self):
        """True or False, as this property name says."""
        if self._sbc_ is None:
            if self.on_mesh_boundary:
                self._sbc_ = False
            else:
                if int(self._element_._p1_[:-1]) in self._element_._elements_._mesh_.elements and \
                    int(self._element_._p2_[:-1]) in self._element_._elements_._mesh_.elements:
                    self._sbc_ = False
                else:
                    self._sbc_ = True
        return self._sbc_

    @property
    def on_mesh_boundary(self):
        """As this property name says."""
        return self._element_._ondb_