# -*- coding: utf-8 -*-
"""
Here we define a class serves as a base for all interpolations. The mapping 
maps [0, 1]^3 into the regions.

Yi Zhang (C)
Created on Wed Nov 21 23:32:57 2018
Aerodynamics, AE
TU Delft
"""
import numpy as np
from screws.freeze.main import FrozenOnly
from screws.decorators.accepts import accepts
from screws.numerical._3d_space.Jacobian_33 import NumericalJacobian_xyz_33, NumericalPartialDerivative_xyz


class InterpolationBase(FrozenOnly):
    @accepts('self', 'Region')
    def __init__(self, region):
        """
        To initialize an interpolation, we take a regions as input.
        
        Parameters
        ----------
        region : Region
        
        """
        self._region_ = region
        self._ndim_ = region.ndim
        
    @property
    def ndim(self):
        return self._ndim_

    @staticmethod
    def ___check_rst___(r, s, t):
        """ r, s, t be in [0, 1]. """
        if r.__class__.__name__ == 'ndarray':
            pass
        elif isinstance(r, (int, float)):
            r = np.array([r])
        elif isinstance(r, list):
            r = np.array(r)
        else:
            raise Exception()

        if s.__class__.__name__ == 'ndarray':
            pass
        elif isinstance(s, (int, float)):
            s = np.array([s])
        elif isinstance(s, list):
            s = np.array(s)
        else:
            raise Exception()

        if t.__class__.__name__ == 'ndarray':
            pass
        elif isinstance(t, (int, float)):
            t = np.array([t])
        elif isinstance(t, list):
            t = np.array(t)
        else:
            raise Exception()

        assert np.shape(r) == np.shape(s) == np.shape(t), \
            " <Interpolation> : inputs shape dis-match."

        return r, s, t
    
    def __call__(self, r, s, t):
        return self.mapping(r, s, t)

    def mapping(self, r, s, t):
        raise NotImplementedError()

    def mapping_X(self, r, s, t):
        raise NotImplementedError()

    def mapping_Y(self, r, s, t):
        raise NotImplementedError()

    def mapping_Z(self, r, s, t):
        raise NotImplementedError()

    def Jacobian_matrix(self, r, s, t):
        """ 
        r, s, t be in [0, 1].
        
        This is a general Jacobian_matrix using numerical derivative. To avoid 
        this, just overwrite it in the child class.
        
        """
        r, s, t = self.___check_rst___(r, s, t)
        NJ33 = NumericalJacobian_xyz_33(self.mapping)
        return NJ33.scipy_derivative(r, s, t)
    
    def Jacobian(self, r, s, t):
        """ 
        r, s, t be in [0, 1]. The Jacobian is the determinant of the `Jacobian_matrix`.
        
        """
        JM = self.Jacobian_matrix(r, s, t)
        X, Y, Z = JM
        a, b, c = X 
        d, e, f = Y 
        g, h, i = Z
        return a*(e*i-f*h) - b*(d*i-f*g) + c*(d*h-e*g)


    def Jacobian_X_(self, r, s, t):
        N31 = NumericalPartialDerivative_xyz(self.mapping_X, r, s, t)
        return N31.scipy_total
    def Jacobian_Y_(self, r, s, t):
        N31 = NumericalPartialDerivative_xyz(self.mapping_Y, r, s, t)
        return N31.scipy_total
    def Jacobian_Z_(self, r, s, t):
        N31 = NumericalPartialDerivative_xyz(self.mapping_Z, r, s, t)
        return N31.scipy_total


    def Jacobian_Xr(self, r, s, t):
        N31 = NumericalPartialDerivative_xyz(self.mapping_X, r, s, t)
        return N31.scipy_partial('x')
    def Jacobian_Xs(self, r, s, t):
        N31 = NumericalPartialDerivative_xyz(self.mapping_X, r, s, t)
        return N31.scipy_partial('y')
    def Jacobian_Xt(self, r, s, t):
        N31 = NumericalPartialDerivative_xyz(self.mapping_X, r, s, t)
        return N31.scipy_partial('z')

    def Jacobian_Yr(self, r, s, t):
        N31 = NumericalPartialDerivative_xyz(self.mapping_Y, r, s, t)
        return N31.scipy_partial('x')
    def Jacobian_Ys(self, r, s, t):
        N31 = NumericalPartialDerivative_xyz(self.mapping_Y, r, s, t)
        return N31.scipy_partial('y')
    def Jacobian_Yt(self, r, s, t):
        N31 = NumericalPartialDerivative_xyz(self.mapping_Y, r, s, t)
        return N31.scipy_partial('z')

    def Jacobian_Zr(self, r, s, t):
        N31 = NumericalPartialDerivative_xyz(self.mapping_Z, r, s, t)
        return N31.scipy_partial('x')
    def Jacobian_Zs(self, r, s, t):
        N31 = NumericalPartialDerivative_xyz(self.mapping_Z, r, s, t)
        return N31.scipy_partial('y')
    def Jacobian_Zt(self, r, s, t):
        N31 = NumericalPartialDerivative_xyz(self.mapping_Z, r, s, t)
        return N31.scipy_partial('z')



# ----- particular interpolations below ------------------------------------------------------


