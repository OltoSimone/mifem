# -*- coding: utf-8 -*-
"""
Here, we store all visualize methods of a runner. The ploters will take use of the data
in property `rdf` (Result DataFrame) to make sure they are general for future serial_runners.

Yi Zhang (C)
Created on Fri Apr 12 11:17:07 2019
Aerodynamics, AE
TU Delft
"""
import matplotlib.pyplot as plt
from screws.miscellaneous.timer import MyTimer
from screws.freeze.main import FrozenOnly
from tools.deprecated.serial_runners.COMPONENTS.data.COMPONENTS.MODULES.m_tir_visualize import M_TIR_Visualize




class DFWVisualize(FrozenOnly):
    """
    A visualizer for DFW data. The data can be a `DFW` or a child of `DFW`. Normally
    it is a child of `DFW` cause `DFW` basically serves as a parent to normalize all
    potential `DataFrame` data.

    """
    def __init__(self, dfw):
        """
        Parameters
        ----------
        dfw :
            `DataFrameWrapper` or its child.

        """
        self._dfw_ = dfw
        self._quick_ = DFWQuickVisualization(self)
        self._freeze_self_()

    @property
    def quick(self):
        """ Access to the quick visualization methods."""
        return self._quick_

    @property
    def _data_(self):
        """ The data."""
        assert self._dfw_() is not None, " <RunnerPloter> : no `ResultDataFrame` to access."
        return self._dfw_()

    def plot(self, *args, **kwargs):
        """ """
        # noinspection PyUnresolvedReferences
        return self.___plot___('plot', *args, **kwargs)

    def semilogx(self, *args, **kwargs):
        """ """
        # noinspection PyUnresolvedReferences
        return self.___plot___('semilogx', *args, **kwargs)

    def semilogy(self, *args, **kwargs):
        """ """
        # noinspection PyUnresolvedReferences
        return self.___plot___('semilogy', *args, **kwargs)

    def loglog(self, *args, **kwargs):
        """ """
        # noinspection PyUnresolvedReferences
        return self.___plot___('loglog', *args, **kwargs)




class DFWQuickVisualization(FrozenOnly):
    """
    Here we store some method to give quick visualizations. They are usually not
    suitable for using in papers and so on.

    """
    def __init__(self, dfwv):
        """ """
        self._dfwv_ = dfwv
        self._freeze_self_()

    @property
    def _data_(self):
        return self._dfwv_._data_

    def scatter(self, x, y=None):
        """
        Scatter plot. `x` and `y` are column names. If `y` is None, then we ploy `x`
        against index. Otherwise, we plot `y` against `x`.

        when `x` or `y` is one of 'ITC', 'TTC' and 'ERT', we have to convert them into
        seconds first of course.

        """
        plt.figure()
        plt.rc('text', usetex=False)
        if y is None:
            if x in ('TTC', 'ITC', 'ERT'):
                data = [MyTimer.hms2seconds(i) for i in self._data_[x]]
                x += '(seconds)'
            else:
                data = self._data_[x]
            plt.scatter(self._data_.index, data, c=data, marker='x', alpha=1, cmap='cool')
            plt.xlabel(r'index')
            plt.ylabel(x)
        else:
            if x in ('TTC', 'ITC', 'ERT'):
                x_data = [MyTimer.hms2seconds(i) for i in self._data_[x]]
                x += '(seconds)'
            else:
                x_data = self._data_[x]
            if y in ('TTC', 'ITC', 'ERT'):
                y_data = [MyTimer.hms2seconds(i) for i in self._data_[y]]
                y += '(seconds)'
            else:
                y_data = self._data_[y]
            plt.scatter(x_data, y_data, c=y_data, marker='x', alpha=1, cmap='cool')
            plt.xlabel(x)
            plt.ylabel(y)
        plt.title(self._dfwv_._dfw_.__class__.__name__)
        plt.show()





class RunnerDataVisualize(DFWVisualize, M_TIR_Visualize):
    """ """
    def __init__(self, rd):
        """ 
        Parameters
        ----------
        rd : RunnerData
            
        """
        super().__init__(rd)
        
    def ___plot___(self, plot_type, *args, **kwargs):
        """ 
        Here we wrap `plot`, `semilogx`, `semilogy`, `loglog`.
        
        We get `args` and `kwargs` from methods `plot`, `semilogx`, `semilogy` and 
        `loglog` from parent `DFWVisualize`.
        
        """
        if self._dfw_._runner_.__class__.__name__ in ('Matrix3dInputRunner', 'ThreeInputsRunner'):
            return self.___plot_MTIR___(plot_type, *args, **kwargs)
        else:
            raise Exception(" <> : no `___plot___` for class {}.".format(
                    self._dfw_._runner_.__class__.__name__))