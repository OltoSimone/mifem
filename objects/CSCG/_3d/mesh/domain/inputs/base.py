# -*- coding: utf-8 -*-
"""
Hereby, we define a class for defining a domain. Each instance of such a class
define stores the input information for a domain, 2D or 3D. The mesh_generator
will take such a instance as input and then call the correct generator to 
generate a based on the domain.

@author: Yi Zhang, Created on Mon Sep  3 12:13:28 2018
         Aerodynamics, AE
         TU Delft
"""
import inspect
import numpy as np
from typing import Dict
from screws.freeze.main import FrozenOnly
from screws.decorators.classproperty.main import classproperty

class _3dDomainInputBase(FrozenOnly):
    def __init__(self, domain_name='domain without name'):
        self.domain_name = domain_name
        self._ndim_ = 3
        self._region_corner_coordinates_ = None
        self._region_side_types_ = None
        self._boundary_region_sides_ = None
        self._region_interpolators_ = None
        self._boundary_names_ = None
        self._periodic_boundary_pairs_ = dict()
        self._periodic_boundaries_ = set()
        self._region_sequence_ = None
        self._region_type_wr2_metric_ = None
        self._internal_parameters_ = list()

        INSP = inspect.getfullargspec(self.__init__)
        self.__arg_names___ = INSP[0][1:]
        assert INSP[1] is None and INSP[2] is None, "A domain input class can not have *args and **kwargs."
        assert len(INSP[3]) == len(self.__arg_names___), "A domain input class can only have kwargs."

        self._freeze_self_()

    @property
    def internal_parameters(self):
        """Internal parameters only affect internal metric, does not affect the domain shape.

        When we compare two domain, for example, to see if they are equal to each other, we will
        skip all `internal_parameters`.
        """
        return self._internal_parameters_

    @internal_parameters.setter
    def internal_parameters(self, internal_parameters):
        if isinstance(internal_parameters, list):
            pass
        elif isinstance(internal_parameters, str):
            internal_parameters = [internal_parameters,]
        elif isinstance(internal_parameters, (tuple, set)):
            internal_parameters = list(internal_parameters)
        else:
            raise NotImplementedError(f"internal_parameters = {internal_parameters} not acceptable.")

        assert isinstance(internal_parameters, list), \
            f"please put internal_parameters({internal_parameters}) in list."
        if len(internal_parameters) > 0:
            assert all([ip in self.__arg_names___ for ip in internal_parameters])

        self._internal_parameters_ = internal_parameters

    @property
    def domain_name(self):
        """ Mesh name. """
        return self._domain_name_
    
    @domain_name.setter
    def domain_name(self, dn):
        assert isinstance(dn, str), " <DomainInput> : domain name needs to be str."
        self._domain_name_ = dn
    
    @property
    def ndim(self):
        """ dimensions n. """
        return self._ndim_
        
    @property
    def region_interpolators(self):
        return self._region_interpolators_
    
    @region_interpolators.setter
    def region_interpolators(self, rip):
        assert isinstance(rip, (dict, str)), "region_interpolators needs to be str or dict."
        self._region_interpolators_ = rip


    def ___PRIVATE_region_name_requirement_checker___(self, regionDict):
        """
        Requirements:
        1). must be str
        2). != domain name.
        3). length > 2
        4). Starts with 'R:'
        5). can only have letters and _
        """
        for R in regionDict:
            assert isinstance(R, str), f"region name={R} wrong, need be str!"
            assert R != self.domain_name, f"region name == domain.name! wrong!"
            assert len(R) > 2, f"region name = {R} too short, must > 2."
            assert R[0:2] == 'R:', f"regions name = {R} does not start with 'R:'"
            R2 = R[2:].replace('_', '')
            assert R2.isalpha(),f"region_name = {R} wrong, can only have letter and _ (at >2)."


    def ___PRIVATE_boundary_name_requirement_checker___(self, boundaryRegionSidesDict):
        """
        Requirements:
        1). != domain name.
        2). Length > 2
        3). Can not start with 'R:' (So it must be different from regions names).
        4). Only have letters
        """
        for boundary_name in boundaryRegionSidesDict.keys():
            assert boundary_name != self.domain_name
            assert len(boundary_name) > 2, f"boundary_name = {boundary_name} is too short (>2 must)."
            assert boundary_name[0:2] != 'R:', f"boundary_name = {boundary_name} wrong."
            BN = boundary_name.replace('_', '')
            assert BN.isalpha(), f"boundary_name = {boundary_name} wrong, boundary_name can only contain letters and _."



    def ___PRIVATE_periodic_boundary_requirement_checker___(self, pBd):
        """
        Here we only do a simple check. We make sure that the keys are in format of:
        0). boundary_name_1=boundary_name_2.
        1). A boundary name at most appear in one pair.

        """
        assert isinstance(pBd, dict)
        bnPOOL = set()
        for pair in pBd:
            assert '=' in pair
            bn1, bn2 = pair.split('=')
            lengthPOOL = len(bnPOOL)
            assert bn1 in self._boundary_names_ and bn2 in self._boundary_names_
            bnPOOL.add(bn1)
            bnPOOL.add(bn2)
            newLengthPOOL = len(bnPOOL)
            assert newLengthPOOL == lengthPOOL + 2, "Boundary(s) used for multiple periodic pairs!"
        self._periodic_boundaries_ = bnPOOL

    @property
    def periodic_boundary_pairs(self):
        return self._periodic_boundary_pairs_

    @periodic_boundary_pairs.setter
    def periodic_boundary_pairs(self, pBd):
        """ """
        self.___PRIVATE_periodic_boundary_requirement_checker___(pBd)
        self._periodic_boundary_pairs_ = pBd

    @property
    def periodic_boundaries(self):
        """(set) Return a set of all boundary names those involved in the periodic boundary setting."""
        return self._periodic_boundaries_

    @property
    def periodic_boundaries_involved_regions(self):
        """"""
        regions = set()
        for pb in self.periodic_boundaries:
            region_sides = self.boundary_region_sides[pb]
            for rs in region_sides:
                rn = rs.split('-')[0]
                if rn not in regions:
                    regions.add(rn)
        return regions

    @property
    def region_corner_coordinates(self):
        """
        Store the regions 8 corners' coordinates.
        
        Returns
        -------
        region_coordinates : dict
            A dict whose keys represent the regions names, and values represent
            the coordinates of regions corner points.
            
            In 3D: (NWB, SWB, NEB, SEB, NWF, SWF, NEF, SEF).
            S: South, N: North, W: West, E:East, B: Back, F: Front.
            
        """
        return self._region_corner_coordinates_
    
    @region_corner_coordinates.setter
    def region_corner_coordinates(self, _dict_):
        assert isinstance(_dict_, dict), " <DomainInput> : region_coordinates needs to be a dict."
        self.___PRIVATE_region_name_requirement_checker___(_dict_)
        for R in _dict_:
            assert np.shape(_dict_[R])[0] == 8, \
                " <DomainInput> : region_coordinates[{}]={} is wrong.".format(R, _dict_[R])
        self._region_corner_coordinates_ = _dict_

    @property
    def region_side_types(self):
        """
        Store the regions' boundaries' types.
        
        Returns
        -------
        region_boundary_type : dict
            A dict that contains the region boundary info. The keys indicate
            the region boundary, the value indicate the info. value[0] indicate
            the type, value[1:] indicate the rest info which will be parsed
            into full information. The not mentioned regions boundaries will be
            set into default type: ('plane',)
            
            Notice that the value will be sent to side_geometries eventually. And
            if this info (value[1:]) to be parsed, it will be done there in
            side_geometries. And the value is stored in the
            `side_geometries.side_types`.
            
        """
        return self._region_side_types_
    
    @region_side_types.setter
    def region_side_types(self, _dict_):
        assert self.region_corner_coordinates is not None, \
            " <DomainInput> : please first set region_coordinates."
        assert isinstance(_dict_, dict), \
            " <DomainInput> : region_boundary_type needs to be a dict."
        for item in _dict_:
            R, S = item.split('-')
            assert R in self.region_corner_coordinates and S in ('N', 'S', 'W', 'E', 'B', 'F'), \
                " <DomainInput> : region_side_type key {} is wrong.".format(item)
        self._region_side_types_ = _dict_

    @property
    def boundary_region_sides(self):
        """
        Store the domain boundary information.
        
        Returns
        -------
        domain_boundary : dict
            For example:
                {'South': ("Body_center-S", 'Body_back-S', "Body_front-S"), 
                 'West': ("Body_center-W", 'Body_back-W', "Body_front-W", "Body_north-W"),
                 ......}
            This means we have three domain boundaries: South, West and so on.
            The South contains the South side of regions: Body_center, the South
            side of regions: Body_back and the South side of regions: Body_front.
            
        """
        return self._boundary_region_sides_
    
    @boundary_region_sides.setter
    def boundary_region_sides(self, _dict_):
        assert self.region_corner_coordinates is not None, \
            " <DomainInput> : please first set region_coordinates."
        assert isinstance(_dict_, dict), " <DomainInput> : domain_boundary needs to be a dict."

        self.___PRIVATE_boundary_name_requirement_checker___(_dict_)

        for item in _dict_:
            if isinstance(_dict_[item], str):
                _dict_[item] = (_dict_[item],)
            regionSidePool = set()
            if isinstance(_dict_[item], list) or isinstance(_dict_[item], tuple):
                assert len(_dict_[item]) > 0, "<DomainInput> : boundary {} is empty.".format(item)
                for item_i in _dict_[item]:
                    assert item_i not in regionSidePool, f"regionSide:{item_i} appears in multiple boundaries!"
                    regionSidePool.add(item_i)
                    R, S = item_i.split('-')
                    assert R in self.region_corner_coordinates and S in ('N', 'S', 'W', 'E', 'B', 'F'), \
                        " <DomainInput> : domain_boundary[{}]={} is wrong.".format(item, _dict_[item])
            else:
                raise Exception(" <DomainInput> : boundary_region_sides input value accepts" + \
                                " only str, tuple of list.")
        self._boundary_region_sides_ = _dict_
        self._boundary_names_ = list(_dict_.keys())

    @property
    def region_sequence(self):
        """
        This will fix the sequence of regions by fix their names in property
        region_names or regions.names. This is very important for numbering. Sometimes, a bad
        regions sequence can make the numbering wrong.

        """
        return self._region_sequence_

    @region_sequence.setter
    def region_sequence(self, rS: tuple):
        assert len(rS) == len(self.region_corner_coordinates.keys())
        assert all([rSi in self.region_corner_coordinates for rSi in rS]) & \
            all([rSi in rS for rSi in self.region_corner_coordinates.keys()]), \
            f"region_sequence={rS} has invalid regions name(s)."
        self._region_sequence_ = rS

    @property
    def region_type_wr2_metric(self):
        return self._region_type_wr2_metric_

    @region_type_wr2_metric.setter
    def region_type_wr2_metric(self, rTwr2M: Dict[str, str]):
        if isinstance(rTwr2M, str):
            _D_ = dict()
            for region_name in self.region_corner_coordinates:
                _D_[region_name] = rTwr2M
            rTwr2M = _D_
        assert isinstance(rTwr2M, dict), "region_type_wr2_metric needs to be a dictionary."
        for key in rTwr2M:
            assert key in self.region_corner_coordinates, f"Region name={key} not valid."
        self._region_type_wr2_metric_ = rTwr2M







    @classproperty
    def statistic(cls):
        raise NotImplementedError()


    @classproperty
    def random_parameters(cls):
        raise NotImplementedError()
