# -*- coding: utf-8 -*-
from screws.decorators.accepts import accepts
from screws.freeze.main import FrozenOnly


class SpaVec_Adjust(FrozenOnly):
    def __init__(self, spa_vec):
        self._spa_vec_ = spa_vec
        self._freeze_self_()


    @accepts('self', ('PartialDofs', 'PartialCochain'))
    def set_entries_according_to_CSCG_partial_cochains(
        self, pd, pc=None, interpreted_as='local_dofs'):
        """We do:
        V[row_pds.dofs, 0] = col_pds.cochain
        locally. Note it is "locally", that means, after assembly, we
        may have values which are multiple times of the value. This is okay because same thing
        will happen in the left-hand-side EWC matrix.

        Parameters
        ----------
        pd :
        pc :
        interpreted_as :

        Returns
        -------

        """
        if pc is None:
            assert pd.__class__.__name__ == 'PartialCochain', \
                "I need a PartialCochain when pc is None."
            pc = pd

        if pd.__class__.__name__ == 'PartialCochain': pd = pd.dofs

        assert pd.__class__.__name__ == 'PartialDofs', f"pd must be a PartialDofs."
        assert pc.__class__.__name__ == 'PartialCochain', f"pc must be a PartialCochain."

        SPA_VEC = dict()  # the data of the new EWC_ColumnVector.

        if interpreted_as == 'local_dofs':

            LDF_row = pd.interpreted_as.local_dofs
            cochain = pc.cochain

            assert len(LDF_row) == len(cochain), "pc, pd must cover same amount of mesh elements."
            for e in LDF_row:
                assert e in self._spa_vec_ and e in cochain
                ROW = LDF_row[e]
                local_cochain = cochain[e]

                SVe = self._spa_vec_[e].copy().tolil()
                SVe[ROW, 0] = local_cochain

                SPA_VEC[e] = SVe.tocsc()

        else:
            raise NotImplementedError(f"interpreted_as={interpreted_as} not implemented.")

        for e in self._spa_vec_:
            if e not in SPA_VEC:
                SPA_VEC[e] = self._spa_vec_[e]

        SPA_VEC = self._spa_vec_.__class__(
            self._spa_vec_._elements_, SPA_VEC, cache_key_generator = 'no_cache')

        if self._spa_vec_.gathering_matrix is not None:
            SPA_VEC.gathering_matrix = self._spa_vec_.gathering_matrix

        return SPA_VEC