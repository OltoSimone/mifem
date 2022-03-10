
from screws.numerical.time_plus_3d_space.partial_derivative_as_functions import NumericalPartialDerivative_txyz_Functions
from screws.freeze.main import FrozenOnly
from importlib import import_module





class _3dCSCG_VectorField_Numerical(FrozenOnly):
    def __init__(self, vf):
        self._vf_ = vf
        self._freeze_self_()

    @property
    def time_derivative(self):
        """Return a _3dCSCG_VectorField instances which is the numerical time derivative of self."""
        if self._vf_.ftype == 'standard':
            func_x, func_y, func_z = self._vf_.func
            NPD4F_x = NumericalPartialDerivative_txyz_Functions(func_x)
            NPD4F_y = NumericalPartialDerivative_txyz_Functions(func_y)
            NPD4F_z = NumericalPartialDerivative_txyz_Functions(func_z)
            vector_class = getattr(import_module('_3dCSCG.fields.vector.main'), '_3dCSCG_VectorField')
            TDV = vector_class(self._vf_.mesh,
                                      (NPD4F_x('t'), NPD4F_y('t'), NPD4F_z('t')),
                                      ftype='standard',
                                      valid_time=self._vf_.valid_time,
                                      name='time-derivative-of-' + self._vf_.standard_properties.name
                                      )
            return TDV
        else:
            raise NotImplementedError(
                f"Numerical time derivative not implemented for vector type = {self._vf_.ftype}.")

    @property
    def gradient(self):
        """Return a _3dCSCG_TensorField instances which is the numerical gradient of self."""
        if self._vf_.ftype == 'standard':
            func_x, func_y, func_z = self._vf_.func
            NPD4F_x = NumericalPartialDerivative_txyz_Functions(func_x)
            NPD4F_y = NumericalPartialDerivative_txyz_Functions(func_y)
            NPD4F_z = NumericalPartialDerivative_txyz_Functions(func_z)
            T00, T01, T02 = NPD4F_x('x'), NPD4F_x('y'), NPD4F_x('z')
            T10, T11, T12 = NPD4F_y('x'), NPD4F_y('y'), NPD4F_y('z')
            T20, T21, T22 = NPD4F_z('x'), NPD4F_z('y'), NPD4F_z('z')

            tensor_class = getattr(import_module('_3dCSCG.fields.tensor.main'), '_3dCSCG_TensorField')
            gradient_tensor = tensor_class(self._vf_.mesh,
                                     [(T00, T01, T02),
                                      (T10, T11, T12),
                                      (T20, T21, T22),],
                                     ftype='standard',
                                     valid_time=self._vf_.valid_time,
                                     name = 'gradient-of-' + self._vf_.standard_properties.name
                                     )
            return gradient_tensor
        else:
            raise NotImplementedError(f"Numerical gradient not implemented for vector type = {self._vf_.ftype}.")

    @property
    def curl(self):
        """Return a _3dCSCG_TensorField instances which is the numerical curl of self."""
        if self._vf_.ftype == 'standard':
            func_x, func_y, func_z = self._vf_.func
            NPD4F_u = NumericalPartialDerivative_txyz_Functions(func_x)
            NPD4F_v = NumericalPartialDerivative_txyz_Functions(func_y)
            NPD4F_w = NumericalPartialDerivative_txyz_Functions(func_z)
            u_y, u_z = NPD4F_u('y'), NPD4F_u('z')
            v_x, v_z = NPD4F_v('x'), NPD4F_v('z')
            w_x, w_y = NPD4F_w('x'), NPD4F_w('y')

            curl_vector_0 = ___VECTOR_CURL_HELPER___(w_y, v_z)
            curl_vector_1 = ___VECTOR_CURL_HELPER___(u_z, w_x)
            curl_vector_2 = ___VECTOR_CURL_HELPER___(v_x, u_y)

            vector_class = getattr(import_module('_3dCSCG.fields.vector.main'), '_3dCSCG_VectorField')

            curl_vector = vector_class(self._vf_.mesh,
                                     [curl_vector_0, curl_vector_1, curl_vector_2],
                                     ftype='standard',
                                     valid_time=self._vf_.valid_time,
                                     name = 'curl-of-' + self._vf_.standard_properties.name
                                     )
            return curl_vector
        else:
            raise NotImplementedError(f"Numerical curl not implemented for vector type = {self._vf_.ftype}.")

    @property
    def divergence(self):
        """Return a _3dCSCG_ScalarField instances which is the numerical divergence of self."""
        if self._vf_.ftype == 'standard':
            func_x, func_y, func_z = self._vf_.func
            NPD4F_x = NumericalPartialDerivative_txyz_Functions(func_x)
            NPD4F_y = NumericalPartialDerivative_txyz_Functions(func_y)
            NPD4F_z = NumericalPartialDerivative_txyz_Functions(func_z)
            u_x = NPD4F_x('x')
            v_y = NPD4F_y('y')
            w_z = NPD4F_z('z')
            div_func = ___VECTOR_DIVERGENCE_HELPER___(u_x, v_y, w_z)
            scalar_class = getattr(import_module('_3dCSCG.fields.scalar.main'), '_3dCSCG_ScalarField')
            divergence_scalar = scalar_class(self._vf_.mesh,
                                             div_func,
                                             ftype='standard',
                                             valid_time=self._vf_.valid_time,
                                             name = 'divergence-of-' + self._vf_.standard_properties.name
                                             )
            return divergence_scalar
        else:
            raise NotImplementedError(f"Numerical divergence not implemented for vector type = {self._vf_.ftype}.")




class ___VECTOR_CURL_HELPER___(object):
    def __init__(self, f0, f1):
        self._f0_ = f0
        self._f1_ = f1

    def __call__(self, t, x, y, z):
        return self._f0_(t, x, y, z) - self._f1_(t, x, y, z)


class ___VECTOR_DIVERGENCE_HELPER___(object):
    def __init__(self, f0, f1, f2):
        self._f0_ = f0
        self._f1_ = f1
        self._f2_ = f2

    def __call__(self, t, x, y, z):
        return self._f0_(t, x, y, z) + self._f1_(t, x, y, z) + self._f2_(t, x, y, z)