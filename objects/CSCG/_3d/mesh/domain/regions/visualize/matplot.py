

from screws.freeze.main import FrozenOnly
import matplotlib.pyplot as plt


from root.config.main import np, rAnk, mAster_rank

class _3dCSCG_Regions_Visualize_Matplot_(FrozenOnly):
    def __init__(self, visualize):
        self._regions_ = visualize._regions_
        self._domain_ = self._regions_._domain_
        self._freeze_self_()


    def __call__(self, *args, **kwargs):
        """"""
        return self.connection(*args, **kwargs)



    def connection(self, density=5000,):
        """"""
        # we can do everything in the master core.
        if rAnk != mAster_rank: return

        density = int( np.ceil( np.sqrt(density / (self._regions_.num * 6)) ) )
        r = np.linspace(0, 1, density)
        O = np.zeros(density)
        I = np.ones(density)
        FH = np.linspace(0, 0.5, int(density/2))
        SH = np.linspace(0.5, 1, int(density/2))
        H = np.ones(int(density/2)) * 0.5

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

        for rn in self._regions_:
            region = self._regions_[rn]

            xyz = region.interpolation.mapping(O, O, r)
            ax.plot(*xyz, color='gray', linewidth=0.75)
            xyz = region.interpolation.mapping(O, I, r)
            ax.plot(*xyz, color='gray', linewidth=0.75)
            xyz = region.interpolation.mapping(I, O, r)
            ax.plot(*xyz, color='gray', linewidth=0.75)
            xyz = region.interpolation.mapping(I, I, r)
            ax.plot(*xyz, color='gray', linewidth=0.75)
            xyz = region.interpolation.mapping(r, O, O)
            ax.plot(*xyz, color='gray', linewidth=0.75)
            xyz = region.interpolation.mapping(r, I, O)
            ax.plot(*xyz, color='gray', linewidth=0.75)
            xyz = region.interpolation.mapping(r, O, I)
            ax.plot(*xyz, color='gray', linewidth=0.75)
            xyz = region.interpolation.mapping(r, I, I)
            ax.plot(*xyz, color='gray', linewidth=0.75)
            xyz = region.interpolation.mapping(I, r, O)
            ax.plot(*xyz, color='gray', linewidth=0.75)
            xyz = region.interpolation.mapping(O, r, O)
            ax.plot(*xyz, color='gray', linewidth=0.75)
            xyz = region.interpolation.mapping(O, r, I)
            ax.plot(*xyz, color='gray', linewidth=0.75)
            xyz = region.interpolation.mapping(I, r, I)
            ax.plot(*xyz, color='gray', linewidth=0.75)

            center = region.interpolation.mapping(0.5, 0.5, 0.5)
            ax.scatter(*center, marker='s', color='b')


        # ---- now we plot the connection of region centers ---------------------------
        MAP = self._regions_.map
        for rn in MAP:   # go through all regions

            region = self._regions_[rn]

            for i, side in enumerate('NSWEBF'):

                object_at_this_side = MAP[rn][i]

                if object_at_this_side in self._regions_: # we find a region at this side

                    if side == 'N':
                        xyz = region.interpolation.mapping(FH, H, H)
                        ax.plot(*xyz, '--', color='r', linewidth=0.75)
                    elif side == 'S':
                        xyz = region.interpolation.mapping(SH, H, H)
                        ax.plot(*xyz, '--', color='r', linewidth=0.75)
                    elif side == 'W':
                        xyz = region.interpolation.mapping(H, FH, H)
                        ax.plot(*xyz, '--', color='r', linewidth=0.75)
                    elif side == 'E':
                        xyz = region.interpolation.mapping(H, SH, H)
                        ax.plot(*xyz, '--', color='r', linewidth=0.75)
                    elif side == 'B':
                        xyz = region.interpolation.mapping(H, H, FH)
                        ax.plot(*xyz, '--', color='r', linewidth=0.75)
                    elif side == 'F':
                        xyz = region.interpolation.mapping(H, H, SH)
                        ax.plot(*xyz, '--', color='r', linewidth=0.75)
                    else:
                        raise Exception()

                else: # it must be the domain boundary, not the mesh boundary by the way.

                    assert object_at_this_side in self._domain_.boundaries.names

        ax.tick_params(labelsize=12)
        ax.set_xlabel(r'$x$', fontsize=15)
        ax.set_ylabel(r'$y$', fontsize=15)
        ax.set_zlabel(r'$z$', fontsize=15)
        plt.title(self._domain_.name + ', ID: '+ self._domain_.parameters['ID'] + ', <regions-connection>')

        fig.tight_layout()
        plt.show()
        plt.close()
        return fig