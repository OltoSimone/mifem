


from screws.freeze.main import FrozenOnly
from scipy import sparse as spspa
from root.config.main import rAnk, mAster_rank, cOmm, np, sEcretary_rank, MPI
from tools.linear_algebra.data_structures.vectors.GLOBAL.adjust import ___GV_ADJUST___
from tools.linear_algebra.data_structures.vectors.GLOBAL.do import GlobalVectorDo
from tools.linear_algebra.data_structures.vectors.GLOBAL.IS import GlobalVectorIS

class GlobalVector(FrozenOnly):
    """
    An entry can be split into parts and stored in multiple cores.

    This is convenient for, for example, the rhs of a linear system. To see the exact value of one entry,
    we must sum up that entry in all cores.

    GlobalVector may have to be adjusted, so we do not ask it to be csc_matrix.
    """
    def __init__(self, V):
        """

        :param V: it can be:
            - csc_matrix of shape (x, 1).
            - 1d array
            - 2d array of shape (x, 1)
            - int: we will make an empty sparse matrix.
            - None: (Cannot be in the master core) we will make an empty sparse matrix.

        """
        #------ parse input V ------------------------------------------------------------
        if V.__class__.__name__ == 'ndarray':
            if np.ndim(V) == 1:
                V = spspa.csr_matrix(V).T
            elif np.ndim(V) == 2:
                assert V.shape[1] == 1, f"Need a shape = (n,1) ndarray, now it is {V.shape}."
                V = spspa.csc_matrix(V)
            else:
                raise Exception(f"Only accept 1- or 2-d array, now it is {np.ndim(V)}.")
        elif V is None:
            assert rAnk != mAster_rank, "in master core, can not give None."
        elif V.__class__.__name__ in ('int', 'int32', 'int64'):
            V = spspa.csc_matrix((V, 1))
        else:
            pass
        #----------------- check V ---------------------------------------
        if V.__class__.__name__ == 'csr_matrix':
            V = V.tocsc()

        if rAnk == mAster_rank:
            assert spspa.issparse(V), "I need a scipy sparse matrix"
            shape = V.shape
        else:
            shape = None

        shape = cOmm.bcast(shape, root=mAster_rank)
        if rAnk != mAster_rank:
            if V is None:
                V = spspa.csc_matrix(shape)
            else:
                pass

        assert spspa.isspmatrix_csc(V) and V.shape[1] == 1, "V must be a csc_matrix of shape (x, 1)."
        #--------------------------------------------------------------------------------------

        self._V_ = V
        SHAPE = cOmm.gather(self.shape, root=sEcretary_rank)
        if rAnk == sEcretary_rank:
            for i, sp in enumerate(SHAPE):
                assert sp == SHAPE[0], f"shape in core {i} is different from shape in core 0."
        self._adjust_ = ___GV_ADJUST___(self)
        self._do_ = None
        self._IS_ = None
        self._freeze_self_()

    @property
    def V(self):
        return self._V_

    @property
    def shape(self):
        return self.V.shape

    def __len__(self):
        return self.shape[0]

    @property
    def nnz(self):
        return self.V.nnz

    def __neg__(self):
        return GlobalVector(-self.V)

    def __sub__(self, other):
        """

        :param other:
        :return:
        """
        return GlobalVector(self.V - other.V)

    def __add__(self, other):
        """

        :param other:
        :return:
        """
        return GlobalVector(self.V + other.V)

    def __mul__(self, other):
        return GlobalVector(other*self.V)

    def __rmul__(self, other):
        return GlobalVector(other*self.V)

    def ___PRIVATE_gather_V_to_core___(self, core=None, clean_local=False):
        """
        Gather all vector to one core such that in all other core we have zero vector.

        :param core:
        :param bool clean_local: If True, we clear the local V while gathering.
        :return: A 1d ndarray that contains the vector in only one core.
        """
        if core is None: core = mAster_rank
        v = self.V
        v = cOmm.gather(v, root=core)
        if clean_local: self._V_ = None
        if rAnk == core:
            # noinspection PyUnresolvedReferences
            v = np.sum(v).toarray()[:, 0]
        return v

    def ___PRIVATE_resemble_row_distribution_of___(self, GM):
        """
        We let self's distribution resemble that of a GM.

        :param GM:
        :return:
        """
        assert GM.shape[0] == self.shape[0], f"shape[0] does not match."
        already_match = set(self.V.indices) <= set(GM.nonempty_rows)
        already_match = cOmm.allreduce(already_match, op=MPI.LAND)
        if already_match: # already match, just stop here.
            return
        else:
            raise NotImplementedError(f"Not coded yet!")

    @property
    def adjust(self):
        return self._adjust_

    @property
    def do(self):
        if self._do_ is None:
            self._do_ = GlobalVectorDo(self)
        return self._do_

    @property
    def IS(self):
        if self._IS_ is None:
            self._IS_ = GlobalVectorIS(self)
        return self._IS_