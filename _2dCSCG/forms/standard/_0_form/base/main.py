
from root.config.main import *
from scipy import sparse as spspa
from _2dCSCG.forms.standard.base.main import _2dCSCG_Standard_Form
from _2dCSCG.forms.standard._0_form.base.discretize.main import _2dCSCG_S0F_Discretize
from _2dCSCG.forms.standard._0_form.base.visualize.main import _2dCSCG_S0F_VIS


class _0Form_BASE(_2dCSCG_Standard_Form):
    """"""
    def __init_0form_base__(self):
        self._discretize_ = _2dCSCG_S0F_Discretize(self)
        self._visualize_ = _2dCSCG_S0F_VIS(self)

    @property
    def visualize(self):
        return self._visualize_

    def ___PRIVATE_TW_FUNC_body_checker___(self, func_body):
        assert func_body.mesh.domain == self.mesh.domain
        assert func_body.ndim == self.ndim == 2

        if func_body.__class__.__name__ == '_2dCSCG_ScalarField':
            assert func_body.ftype in ('standard',), \
                f"2dCSCG 0form FUNC do not accept func _2dCSCG_ScalarField of ftype {func_body.ftype}."
        else:
            raise Exception(f"3dCSCG 0form FUNC do not accept func {func_body.__class__}")


    def ___PRIVATE_TW_BC_body_checker___(self, func_body):
        assert func_body.mesh.domain == self.mesh.domain
        assert func_body.ndim == self.ndim == 3
        raise Exception(f"3dCSCG 0form BC do not accept func {func_body.__class__}")


    def ___PRIVATE_reset_cache___(self):
        super().___PRIVATE_reset_cache___()

    @property
    def discretize(self):
        return self._discretize_

    def reconstruct(self, xi, eta, ravel=False, i=None):
        xietasigma, basis = self.do.evaluate_basis_at_meshgrid(xi, eta)
        xyz = dict()
        value = dict()
        shape = [len(xi), len(eta)]
        INDICES = self.mesh.elements.indices if i is None else [i, ]
        for i in INDICES:
            element = self.mesh.elements[i]
            xyz[i] = element.coordinate_transformation.mapping(*xietasigma)
            v = np.einsum('ij, i -> j', basis[0], self.cochain.local[i], optimize='optimal')
            if ravel:
                value[i] = [v,]
            else:
                # noinspection PyUnresolvedReferences
                xyz[i] = [xyz[i][j].reshape(shape, order='F') for j in range(2)]
                value[i] = [v.reshape(shape, order='F'),]
        return xyz, value

    def ___PRIVATE_make_reconstruction_matrix_on_grid___(self, xi, eta):
        """
        Make a dict (keys are #mesh-elements) of matrices whose columns refer to
        nodes of meshgrid(xi, eta, indexing='ij') and rows refer to
        local dofs.

        If we apply these matrices to the local dofs, we will get the
        reconstructions on the nodes in the mesh-elements.

        :param xi: 1d array in [-1, 1]
        :param eta: 1d array in [-1, 1]
        :return:
        """
        _, basis = self.do.evaluate_basis_at_meshgrid(xi, eta)
        RM = dict()
        INDICES = self.mesh.elements.indices
        rmi = basis[0].T
        for i in INDICES:
            RM[i] = rmi
        return RM





    def ___PRIVATE_operator_inner___(self, _, i, xietasigma, quad_weights, bfSelf, bfOther):
        """Note that here we only return a local matrix."""
        element = self.mesh.elements[i]
        detJ = element.coordinate_transformation.Jacobian(*xietasigma)
        Mi = np.einsum('im, jm, m -> ij', bfOther[0], bfSelf[0], detJ*quad_weights, optimize='greedy')
        Mi = spspa.csc_matrix(Mi)
        return Mi


    def ___PRIVATE_operator_wedge___(self, other, quad_degree=None):
        """ """
        assert self.ndim == other.ndim and self.k + other.k == other.ndim, " <_0Form> "
        try:
            assert self.mesh == other.mesh
        except AssertionError:
            raise Exception(' <_0Form_int_wedge> : meshes do not fit.')
        if quad_degree is None:
            quad_degree = [int(np.max([self.dqp[i], other.dqp[i]])) + 1 for i in range(2)]
        quad_nodes , _, quad_weights = self.space.___PRIVATE_do_evaluate_quadrature___(quad_degree)
        xietasigma, basisS = self.do.evaluate_basis_at_meshgrid(*quad_nodes)
        _, basisO = other.do.evaluate_basis_at_meshgrid(*quad_nodes)
        W = np.einsum('im, jm, m -> ij', basisO[0], basisS[0], quad_weights, optimize='greedy')
        return spspa.csc_matrix(W)