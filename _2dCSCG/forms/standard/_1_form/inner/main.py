# -*- coding: utf-8 -*-
"""

@author: Yi Zhang.
         Department of Aerodynamics
         Faculty of Aerospace Engineering
         TU Delft, Delft, Netherlands

"""
import sys
if './' not in sys.path: sys.path.append('./')
from _2dCSCG.forms.standard._1_form.inner.special import _1Form_Inner_Special
import numpy as np
from scipy import sparse as spspa
from _2dCSCG.forms.standard._1_form.base import _1Form_BASE



class _2dCSCG_1Form_Inner(_1Form_BASE):
    """
    Standard 1-form.

    :param mesh:
    :param space:
    :param is_hybrid:
    :param numbering_parameters:
    :param name:
    """
    def __init__(self, mesh, space, is_hybrid=True,
        numbering_parameters='Naive',  name='inner-oriented-1-form'):
        super().__init__(mesh, space, is_hybrid, 'inner', numbering_parameters, name)
        self._k_ = 1
        self.standard_properties.___PRIVATE_add_tag___('2dCSCG_standard_1form_Inner')
        self.standard_properties.___PRIVATE_add_tag___('2dCSCG_standard_1form')
        self._special_ = _1Form_Inner_Special(self)
        self.___PRIVATE_reset_cache___()
        self._freeze_self_()

    @property
    def special(self):
        return self._special_

    def ___PRIVATE_discretize_standard_ftype___(self, update_cochain=True, target='func', quad_degree=None):
        """
        The return cochain is 'locally full local cochain', which means it is mesh-element-wise
        local cochain. So:

        cochainLocal is a dict, whose keys are mesh element numbers, and values (1-d arrays) are
        the local cochains.

        :param update_cochain:
        :param target:
        :param quad_degree:
        :return:
        """
        if self.___DISCRETIZE_STANDARD_CACHE___ is None or \
            quad_degree != self.___DISCRETIZE_STANDARD_CACHE___['quadDegree']:
            self.___DISCRETIZE_STANDARD_CACHE___ = dict()

            xi, eta, edge_size_d_xi, quad_weights = \
                self.___PRIVATE_discretize_preparation___(d_='x', quad_degree=quad_degree)
            self.___DISCRETIZE_STANDARD_CACHE___['X'] = (xi, eta)

            xi, eta, edge_size_d_eta, quad_weights = \
                self.___PRIVATE_discretize_preparation___(d_='y', quad_degree=quad_degree)
            self.___DISCRETIZE_STANDARD_CACHE___['Y'] = (xi, eta)

            edge_size = (edge_size_d_xi, edge_size_d_eta)
            self.___DISCRETIZE_STANDARD_CACHE___['edge'] = edge_size
            self.___DISCRETIZE_STANDARD_CACHE___['quad_weights'] = quad_weights
            self.___DISCRETIZE_STANDARD_CACHE___['quadDegree'] = quad_degree
        else:
            pass

        xi_x, eta_x = self.___DISCRETIZE_STANDARD_CACHE___['X']
        xi_y, eta_y = self.___DISCRETIZE_STANDARD_CACHE___['Y']
        quad_weights = self.___DISCRETIZE_STANDARD_CACHE___['quad_weights']
        edge_size = self.___DISCRETIZE_STANDARD_CACHE___['edge']

        local_dx = dict()
        local_dy = dict()

        # --- target --------------------------------------------------------
        if target == 'func':
            FUNC = self.func.body
        else:
            raise NotImplementedError(f"I cannot deal with target = {target}.")
        # =======================================================================

        JXC, JYC = dict(), dict()
        for i in self.mesh.elements.indices:
            element = self.mesh.elements[i]
            typeWr2Metric = element.type_wrt_metric.mark

            smctm = element.coordinate_transformation.mapping(xi_x, eta_x)
            if typeWr2Metric in JXC:
                J = JXC[typeWr2Metric]
            else:
                J = element.coordinate_transformation.Jacobian_matrix(xi_x, eta_x)
                if isinstance(typeWr2Metric, str):
                    JXC[typeWr2Metric] = J
            if isinstance(typeWr2Metric, str) and typeWr2Metric[:4] == 'Orth':
                u = FUNC[0](*smctm)
                local_dx[i] = np.einsum(
                    'jk, j, k -> k', J[0][0]*u, quad_weights[0], edge_size[0] * 0.5, optimize='greedy'
                )
            else:
                J = (J[0][0], J[1][0])
                u = FUNC[0](*smctm)
                v = FUNC[1](*smctm)
                local_dx[i] = np.einsum(
                    'jk, j, k -> k', J[0]*u + J[1]*v, quad_weights[0], edge_size[0] * 0.5, optimize='greedy'
                )

            smctm = element.coordinate_transformation.mapping(xi_y, eta_y)
            if typeWr2Metric in JYC:
                J = JYC[typeWr2Metric]
            else:
                J = element.coordinate_transformation.Jacobian_matrix(xi_y, eta_y)
                if isinstance(typeWr2Metric, str):
                    JYC[typeWr2Metric] = J
            if isinstance(typeWr2Metric, str) and typeWr2Metric[:4] == 'Orth':
                v = FUNC[1](*smctm)
                local_dy[i] = np.einsum(
                    'jk, j, k -> k', J[1][1]*v, quad_weights[1], edge_size[1]*0.5, optimize='greedy'
                )
            else:
                J = (J[0][1], J[1][1])
                u = FUNC[0](*smctm)
                v = FUNC[1](*smctm)
                local_dy[i] = np.einsum(
                    'jk, j, k -> k', J[0]*u + J[1]*v, quad_weights[1], edge_size[1]*0.5, optimize='greedy'
                )

        del JXC, JYC
        # isisKronecker? ...
        if not self.space.IS_Kronecker: raise NotImplementedError()
        # give it to cochain.local ...
        cochainLocal = dict()
        for i in self.mesh.elements.indices:
            cochainLocal[i] = np.hstack((local_dx[i], local_dy[i]))
        if update_cochain:
            self.cochain.local = cochainLocal
        # ...
        return 'locally full local cochain', cochainLocal


    def reconstruct(self, xi, eta, ravel=False, i=None):
        xietasigma, basis = self.do.evaluate_basis_at_meshgrid(xi, eta)
        xyz = dict()
        value = dict()
        shape = [len(xi), len(eta)]
        INDICES = self.mesh.elements.indices if i is None else [i,]
        iJ = self.mesh.elements.coordinate_transformation.inverse_Jacobian_matrix(*xietasigma)
        for i in INDICES:
            element = self.mesh.elements[i]
            xyz[i] = element.coordinate_transformation.mapping(*xietasigma)
            u = np.einsum('ij, i -> j', basis[0], self.cochain.___PRIVATE_local_on_axis___('x', i), optimize='optimal')
            v = np.einsum('ij, i -> j', basis[1], self.cochain.___PRIVATE_local_on_axis___('y', i), optimize='optimal')
            value[i] = [None, None]
            typeWr2Metric = element.type_wrt_metric.mark
            iJi = iJ[i]
            if isinstance(typeWr2Metric, str) and typeWr2Metric[:4] == 'Orth':
                value[i][0] = u*iJi[0][0]
                value[i][1] = v*iJi[1][1]
            else:
                for j in range(2):
                    value[i][j] = u*iJi[0][j] + v*iJi[1][j]
            if ravel:
                pass
            else:
                # noinspection PyUnresolvedReferences
                xyz[i] = [xyz[i][j].reshape(shape, order='F') for j in range(2)]
                # noinspection PyUnresolvedReferences
                value[i] = [value[i][j].reshape(shape, order='F') for j in range(2)]
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
        xietasigma, basis = self.do.evaluate_basis_at_meshgrid(xi, eta)

        INDICES = self.mesh.elements.indices
        iJ = self.mesh.elements.coordinate_transformation.inverse_Jacobian_matrix(*xietasigma)

        b0, b1 = basis[0].T, basis[1].T
        OO01 = 0 * b1
        OO10 = 0 * b0

        type_cache = dict()
        RM = dict()
        for i in INDICES:
            element = self.mesh.elements[i]
            typeWr2Metric = element.type_wrt_metric.mark
            if isinstance(typeWr2Metric, str):
                if typeWr2Metric in type_cache:
                    RM[i] = type_cache[typeWr2Metric]
                else:
                    iJi = iJ[i]
                    rm00 = np.einsum('ji, j -> ji', b0, iJi[0][0], optimize='greedy')
                    rm11 = np.einsum('ji, j -> ji', b1, iJi[1][1], optimize='greedy')
                    if typeWr2Metric[:4] == 'Orth':
                        RM_i_ = ( np.hstack((rm00, OO01)),
                                  np.hstack((OO10, rm11)) )
                    else:
                        rm01 = np.einsum('ji, j -> ji', b1, iJi[1][0], optimize='greedy')
                        rm10 = np.einsum('ji, j -> ji', b0, iJi[0][1], optimize='greedy')
                        RM_i_ = ( np.hstack((rm00, rm01)),
                                  np.hstack((rm10, rm11)) )

                    type_cache[typeWr2Metric] = RM_i_
                    RM[i] = RM_i_

            else:
                iJi = iJ[i]
                rm00 = np.einsum('ji, j -> ji', b0, iJi[0][0], optimize='optimal')
                rm01 = np.einsum('ji, j -> ji', b1, iJi[1][0], optimize='optimal')
                rm10 = np.einsum('ji, j -> ji', b0, iJi[0][1], optimize='optimal')
                rm11 = np.einsum('ji, j -> ji', b1, iJi[1][1], optimize='optimal')
                RM[i] = (np.hstack((rm00, rm01)),
                         np.hstack((rm10, rm11)))

        return RM



    def ___PRIVATE_operator_inner___(self, other, i, xietasigma, quad_weights, bfSelf, bfOther):
        """Note that here we only return a local matrix."""
        element = self.mesh.elements[i]
        mark = element.type_wrt_metric.mark
        J = element.coordinate_transformation.Jacobian_matrix(*xietasigma)
        sqrtg = element.coordinate_transformation.Jacobian(*xietasigma, J=J)
        iJ = element.coordinate_transformation.inverse_Jacobian_matrix(*xietasigma, J=J)
        g = element.coordinate_transformation.inverse_metric_matrix(*xietasigma, iJ=iJ)

        del J, iJ
        M00 = self.___PRIVATE_inner_Helper1___(quad_weights, sqrtg*g[0][0], bfOther[0], bfSelf[0])
        M11 = self.___PRIVATE_inner_Helper1___(quad_weights, sqrtg*g[1][1], bfOther[1], bfSelf[1])
        if isinstance(mark, str) and mark[:4] == 'Orth':
            M01 = None
            M10 = None
        else:
            M01 = self.___PRIVATE_inner_Helper1___(quad_weights, sqrtg*g[0][1], bfOther[0], bfSelf[1])
            if other is self:
                M10 = M01.T
            else:
                M10 = self.___PRIVATE_inner_Helper1___(quad_weights, sqrtg*g[1][0], bfOther[1], bfSelf[0])
        Mi = spspa.bmat([(M00, M01),
                         (M10, M11)], format='csc')
        return Mi

    @staticmethod
    def ___PRIVATE_inner_Helper1___(quad_weights, sqrt_g_g, bfO, bfS):
        M = np.einsum('m, im, jm -> ij', quad_weights*sqrt_g_g, bfO, bfS, optimize='optimal')
        return spspa.csc_matrix(M)

    def ___PRIVATE_operator_wedge___(self, other, quad_degree=None):
        """ """
        assert other.k == 1, "Need a _2dCSCG_1Form"
        assert self.mesh == other.mesh, "Meshes do not match."
        if quad_degree is None:
            quad_degree = [int(np.max([self.dqp[i], other.dqp[i]])) for i in range(2)]
        quad_nodes, _, quad_weights = self.space.___PRIVATE_do_evaluate_quadrature___(quad_degree)
        xietasigma, bS = self.do.evaluate_basis_at_meshgrid(*quad_nodes)
        _, bO = other.do.evaluate_basis_at_meshgrid(*quad_nodes)
        W00 = np.einsum('im, jm -> ij', bO[0], bS[0]*quad_weights[np.newaxis, :], optimize='optimal')
        W11 = np.einsum('im, jm -> ij', bO[1], bS[1]*quad_weights[np.newaxis, :], optimize='optimal')
        i, j = other.num.basis_components
        m, n = self.num.basis_components
        #      m   n
        # i  |W00 W01 |
        # j  |W10 W11 |
        W = np.vstack((np.hstack((W00, np.zeros((i,n)))),
                       np.hstack((np.zeros((j,m)), W11))))
        return spspa.csc_matrix(W)




if __name__ == '__main__':
    # mpiexec python _2dCSCG\form\standard\_1_form_inner.py
    from _2dCSCG.main import MeshGenerator, SpaceInvoker, FormCaller, ExactSolutionSelector

    mesh = MeshGenerator('crazy', c=0.0,bounds=([0,1],[0,1]))([1,1])
    # mesh = MeshGenerator('chp1',)([2,2])
    space = SpaceInvoker('polynomials')([('Lobatto',1), ('Lobatto',1)])
    FC = FormCaller(mesh, space)

    ES = ExactSolutionSelector(mesh)('sL:sincos1')

    f1 = FC('1-f-i', is_hybrid=True)

    M0 = f1.matrices.mass[0]
    print(M0.toarray())

    # f1.TW.func.do.set_func_body_as(ES, 'velocity')
    # f1.TW.current_time = 0
    # f1.TW.do.push_all_to_instant()
    # f1.discretize()
    # print(f1.error.L())
    #
    # from root.mifem import save
    #
    # save(f1, 'test_2d_f1_i')