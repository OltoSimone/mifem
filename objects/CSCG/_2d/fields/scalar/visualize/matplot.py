

from root.config.main import *
import matplotlib.pyplot as plt
from screws.freeze.main import FrozenOnly


class _2dCSCG_ScalarField_Visualize_matplot(FrozenOnly):
    def __init__(self, cf):
        self._cf_ = cf
        self._mesh_ = self._cf_.mesh
        self._freeze_self_()

    @staticmethod
    def ___set_contour_levels___(v, num_levels):
        """ We set the `num_levels` according to the values `v` to be plotted. """
        MINv = np.min(v)
        MAXv = np.max(v)
        if MINv == MAXv:
            if MINv == 0:
                MAXv = 0.1
            else:
                if MINv > 0:
                    MAXv = MINv * 1.01
                else:
                    MAXv = MINv * 0.99
            num_levels = 2
        levels = np.linspace(MINv, MAXv, num_levels)
        return levels



    def __call__(self, ptype='contourf', **kwargs):
        return getattr(self, '_plot__2dCSCG_ScalarField' + f'_{ptype}')(**kwargs)

    def _plot__2dCSCG_ScalarField_contourf(self, time=None, density=10000, usetex=False, colormap='coolwarm',
        show_colorbar=True, levels=None, num_levels=20, title=True,
        show_boundaries=True, domain_boundary_linewidth=3, boundary_name_fontsize=12,
        minor_tick_length=0, major_tick_length=0, tick_pad=5, tick_size=12):
        """

        :param time:
        :param density:
        :param usetex:
        :param colormap:
        :param show_colorbar:
        :param levels:
        :param num_levels:
        :param title:
        :param show_boundaries:
        :param domain_boundary_linewidth:
        :param boundary_name_fontsize:
        :param minor_tick_length:
        :param major_tick_length:
        :param tick_pad:
        :param tick_size:
        :return:
        """
        density = int(np.ceil(np.sqrt(density / self._mesh_.elements.GLOBAL_num)))
        rs = [np.linspace(-1, 1, density) for _ in range(self._cf_.ndim)]
        rs = np.meshgrid(*rs, indexing='ij')
        xy, v = self._cf_.reconstruct(*rs, time=time)

        xy = cOmm.gather(xy, root=sEcretary_rank)
        v = cOmm.gather(v, root=sEcretary_rank)

        if rAnk != sEcretary_rank:
            pass
        else:
            XY = dict()
            VV = dict()
            for _ in xy: XY.update(_)
            for _ in v: VV.update(_)

            x = list()
            y = list()
            v = list()
            for i in XY:
                x.append(XY[i][0])
                y.append(XY[i][1])
                v.append(VV[i][0])
            v = np.array(v)
            if levels is None:
                levels = self.___set_contour_levels___(v, num_levels)
            else:
                pass

            x, y, v = self._mesh_.do.regionwsie_stack(x, y, v)

            plt.rc('text', usetex=usetex)
            if colormap is not None: plt.rcParams['image.cmap'] = colormap
            fig, ax = plt.subplots()
            ax.set_aspect('equal')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(True)
            ax.spines['bottom'].set_visible(True)

            for rn in self._cf_.mesh.domain.regions.names:
                plt.contourf(x[rn], y[rn], v[rn], levels=levels)

            if show_boundaries:
                RB, RBN, boundary_name_color_dict, pb_text = \
                    self._mesh_.visualize.matplot.___PRIVATE_DO_generate_boundary_data___(
                        50, usetex=usetex)[0:4]

                reo_db = self._mesh_.domain.regions.edges_on_domain_boundaries

                for rn in self._mesh_.domain.regions.names:
                    for ei in range(4):
                        if reo_db[rn][ei] == 1:
                            bn = self._mesh_.domain.regions.map[rn][ei]
                            # noinspection PyUnresolvedReferences
                            ax.plot(RB[rn][ei][0], RB[rn][ei][1], color=boundary_name_color_dict[bn],
                                    linewidth=domain_boundary_linewidth)
                            # noinspection PyUnresolvedReferences
                            ax.plot(RB[rn][ei][0], RB[rn][ei][1], color='k',
                                    linewidth=0.25*domain_boundary_linewidth)

                        if RBN[rn][ei] is None:
                            pass
                        else:
                            bn = self._mesh_.domain.regions.map[rn][ei]
                            if bn in pb_text:
                                # noinspection PyUnresolvedReferences
                                ax.text(RBN[rn][ei][0], RBN[rn][ei][1],
                                        '$<' + pb_text[bn] + '>$', fontsize=boundary_name_fontsize,
                                        c=boundary_name_color_dict[bn], ha='center', va='center')
                            else:
                                # noinspection PyUnresolvedReferences
                                ax.text(RBN[rn][ei][0], RBN[rn][ei][1],
                                        '$<$' + bn + '$>$', fontsize=boundary_name_fontsize,
                                        c=boundary_name_color_dict[bn], ha='center', va='center')

            plt.tick_params(which='both', labeltop=False, labelright=False, top=False, right=False)
            if minor_tick_length != 0:
                plt.tick_params(axis='both', which='minor', direction='in', length=minor_tick_length)
            if major_tick_length != 0:
                plt.tick_params(axis='both', which='major', direction='in', length=major_tick_length)
            plt.tick_params(axis='both', which='both', labelsize=tick_size)
            plt.tick_params(axis='x', which='both', pad=tick_pad)
            plt.tick_params(axis='y', which='both', pad=tick_pad)

            plt.xlabel('$x$')
            plt.ylabel('$y$')

            if title is True:
                plt.title(f"Scalar field: {self._cf_.standard_properties.name} @ time={self._cf_.current_time}")


            if show_colorbar:
                plt.colorbar()
            plt.show()
            return fig

