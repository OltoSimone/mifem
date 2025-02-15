

from objects.CSCG._3d.mesh.domain.inputs.base import _3dDomainInputBase
from screws.decorators.classproperty.main import classproperty

class Periodic_Square_Channel(_3dDomainInputBase):
    """A periodic square channel domain.

    The domain is periodic along x-direction. The other four sides are normal boundaries.

    ^ y
    |                           l
    |_____________________________________________________________
    |                                                            |
    |                                                            |
    |w                                                           |w
    |------------------------------------------------------------|----------> x
    |                                                            |
    |                                                            |
    |                                                            |
    ——————————————————————————————————————————————————————————————
                                l
    """

    def __init__(self, l=2, w=1, h=1, domain_name="Periodic-Square-Channel"):
        assert l > 0 and w > 0 and h > 0, f"l, w, h = {l}, {w}, {h} is wrong."

        self._lwh_ = [l, w, h]

        super().__init__(domain_name=domain_name)

        x0 = 0
        x1 = l
        y0 = - w / 2
        y1 = + w / 2
        z0 = - h / 2
        z1 = + h / 2

        self.region_corner_coordinates = {'R:R': ((x0, y0, z0), (x1, y0, z0), (x0, y1, z0), (x1, y1, z0),
                                                  (x0, y0, z1), (x1, y0, z1), (x0, y1, z1), (x1, y1, z1))}
        self.region_side_types = dict() # all plane
        self.boundary_region_sides = {'wXm': "R:R-N", 'wXp': "R:R-S",
                                      'wYm': "R:R-W", 'wYp': "R:R-E",
                                      'wZm': "R:R-B", 'wZp': "R:R-F"}
        self.region_interpolators = {'R:R': 'transfinite'}
        self.periodic_boundary_pairs = {'wXm=wXp': 'regular',}
        self.region_type_wr2_metric = {'R:R': 'transfinite'}
        self.internal_parameters = list()  # has to be defined after the super().__init__

    @property
    def lwh(self):
        return self._lwh_



    @classproperty
    def statistic(cls):
        raise NotImplementedError()


    @classproperty
    def random_parameters(cls):
        raise NotImplementedError()
