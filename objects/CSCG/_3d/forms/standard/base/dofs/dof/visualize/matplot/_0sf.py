
from root.config.main import *

import matplotlib.pyplot as plt

from screws.freeze.main import FrozenOnly


class _3dCSCG_SF_DOF_VISUALIZE_matplot_0SF(FrozenOnly):
    """"""
    def __init__(self, dof):
        """"""
        self._dof_ = dof
        self._mesh_ = dof._sf_.mesh
        self._sf_ = dof._sf_
        self._freeze_self_()

    def __call__(self, *args, **kwargs):
        """We plot this dof of a standard 0-form."""
        if self._sf_.IS.hybrid:
            return self.___PRIVATE_matplot_dof_k_form_IS_hybrid__(*args, **kwargs)
        else:
            return self.___PRIVATE_matplot_dof_0form_IS_NOT_hybrid__(*args, **kwargs)

    def ___PRIVATE_matplot_dof_0form_IS_NOT_hybrid__(self, density=20, saveto=None, linewidth=0.6, title=None):
        """"""
        positions = self._dof_.positions
        EF = dict()
        for E_I in positions:
            E, I = E_I
            EF[E] = self._sf_.___PRIVATE_element_grid_data_generator_1___(E, density=density)
        GPs = self._dof_.GLOBAL_positions
        Element_Frames = cOmm.gather(EF, root=mAster_rank)
        if rAnk == mAster_rank:
            #------------ prepare figure -----------------------------------------------------------------
            fig = plt.figure(figsize=(12, 8))
            ax = fig.add_subplot(111, projection='3d')
            # make the panes transparent
            ax.xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
            ax.yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
            ax.zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
            # make the grid lines transparent
            ax.xaxis._axinfo["grid"]['color'] =  (1,1,1,0)
            ax.yaxis._axinfo["grid"]['color'] =  (1,1,1,0)
            ax.zaxis._axinfo["grid"]['color'] =  (1,1,1,0)
            ax.tick_params(labelsize=12)
            ax.set_xlabel(r'$x$', fontsize=15)
            ax.set_ylabel(r'$y$', fontsize=15)
            ax.set_zlabel(r'$z$', fontsize=15)
            #------ plot element frame -----------------------------------------------------------------
            Element_Frame = dict()
            for ef in Element_Frames:
                Element_Frame.update(ef)
            for e in Element_Frame:
                if 'xLines_x' in Element_Frame[e]:
                    X, Y, Z = Element_Frame[e]['xLines_x'], Element_Frame[e]['xLines_y'], Element_Frame[e]['xLines_z']
                    for x, y, z in zip(X, Y, Z):
                        plt.plot(x, y, z, 'gray', linewidth=linewidth)

                if 'yLines_x' in Element_Frame[e]:
                    X, Y, Z = Element_Frame[e]['yLines_x'], Element_Frame[e]['yLines_y'], Element_Frame[e]['yLines_z']
                    for x, y, z in zip(X, Y, Z):
                        plt.plot(x, y, z, 'gray', linewidth=linewidth)

                if 'zLines_x' in Element_Frame[e]:
                    X, Y, Z = Element_Frame[e]['zLines_x'], Element_Frame[e]['zLines_y'], Element_Frame[e]['zLines_z']
                    for x, y, z in zip(X, Y, Z):
                        plt.plot(x, y, z, 'gray', linewidth=linewidth)

                X, Y, Z = Element_Frame[e]['xLines_x_B'], Element_Frame[e]['xLines_y_B'], Element_Frame[e]['xLines_z_B']
                for x, y, z in zip(X, Y, Z):
                    plt.plot(x, y, z, 'green', linewidth=linewidth)
                X, Y, Z = Element_Frame[e]['yLines_x_B'], Element_Frame[e]['yLines_y_B'], Element_Frame[e]['yLines_z_B']
                for x, y, z in zip(X, Y, Z):
                    plt.plot(x, y, z, 'green', linewidth=linewidth)
                X, Y, Z = Element_Frame[e]['zLines_x_B'], Element_Frame[e]['zLines_y_B'], Element_Frame[e]['zLines_z_B']
                for x, y, z in zip(X, Y, Z):
                    plt.plot(x, y, z, 'green', linewidth=linewidth)

                x, y, z = Element_Frame[e]['center']['coordinate']
                x, y, z = x[0], y[0], z[0]
                num = Element_Frame[e]['center']['number']
                ax.text(x, y, z,  num, color='red', ha='center', va='center', ma='center')

            #------ plot the dof of 0-form ----------------------------------------------------------------
            pos = GPs[0]
            element, index = pos
            i, j, k = np.where(self._sf_.numbering.local[0]==index)
            i, j, k = i[0], j[0], k[0]
            nodes = self._sf_.space.nodes
            x, y, z = nodes[0][i], nodes[1][j], nodes[2][k]
            x = np.array([x])
            y = np.array([y])
            z = np.array([z])
            xyz = x, y, z
        else:
            element = None
            xyz = None
        xyz, element = cOmm.bcast([xyz, element], root=mAster_rank)

        if element in self._mesh_.elements:
            xyz = self._mesh_.elements[element].coordinate_transformation.mapping(*xyz)
        else:
            xyz = None

        xyz = cOmm.gather(xyz, root=mAster_rank)

        if rAnk == mAster_rank:
            for ___ in xyz:
                if ___ is not None:
                    x, y, z = ___
                    break

            ax.scatter(x[0], y[0], z[0], marker='s', color='b')

            #--------- title ------------------------------------------------------------------------------
            if title is None:
                plt.title(f"dof#{self._dof_._i_} of {self._sf_.k}-form: {self._sf_.standard_properties.name}.")
            else:
                plt.title(title)

            #---------- SAVE TO ---------------------------------------------------------------------------
            plt.tight_layout()
            if saveto is not None and saveto != '':
                plt.savefig(saveto, bbox_inches='tight')
                plt.close()
            else:
                plt.show()
            #================================================================================

            return fig

    def ___PRIVATE_matplot_dof_k_form_IS_hybrid__(self, *args, **kwargs):
        """"""
        f_kwargs = self._sf_.___define_parameters___['kwargs']
        f_kwargs['is_hybrid'] = False
        non_hybrid_form = self._sf_.__class__(self._sf_.mesh, self._sf_.space, **f_kwargs)
        dofs = non_hybrid_form.dofs
        hy_i = self._dof_._i_

        GPs = self._dof_.GLOBAL_positions
        assert len(GPs) == 1, f"trivial check!"

        pos = GPs[0]
        if pos in self._dof_.positions:
            Ele, index = pos
            nhy_i = non_hybrid_form.numbering.gathering[Ele][index]
        else:
            nhy_i = None

        nhy_i = cOmm.gather(nhy_i, root=mAster_rank)
        if rAnk == mAster_rank:
            I = 0
            for _ in nhy_i:
                if _ is not None:
                    I += 1
                    NHY_I = _
            assert I == 1, "only find one position."

            nhy_i = NHY_I
        else:
            pass

        nhy_i = cOmm.bcast(nhy_i, root=mAster_rank)
        DI = dofs[nhy_i]

        assert len(GPs) == 1, f"A hybrid dof must appear only at 1 place."
        GPs = GPs[0]
        position = 'in hybrid ME-' + str(GPs[0])
        if 'title' not in kwargs:
            kwargs['title'] = f"dof#{hy_i} of {self._sf_.k}-form: {self._sf_.standard_properties.name}, " + position

        DI.visualize.matplot(*args, **kwargs)