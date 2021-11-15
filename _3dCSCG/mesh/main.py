# -*- coding: utf-8 -*-
"""
Our mesh have following structures:

Mesh main structure:
    Mesh -> Domain -> Regions
               |
               ---> DomainInput

Extension structures:
    Mesh -> TraceMesh -> TraceElements -> TraceElement

Components:
    Geometry
    Elements: Mesh -> Elements -> Element
"""
import matplotlib.pyplot as plt
from typing import Dict, Union
from root.config import *
from BASE.CSCG.mesh.main_BASE import CSCG_MESH_BASE
from SCREWS.decorators import accepts, memoize5#, memoize2
from SCREWS.frozen import FrozenOnly
from SCREWS.exceptions import ElementsLayoutError, ElementSidePairError
from SCREWS.miscellaneous import break_list_into_parts
from _3dCSCG.mesh.elements.main import _3dCSCG_Mesh_Elements
from _3dCSCG.mesh.trace import _3dCSCG_Trace
from _3dCSCG.mesh.periodic_setting.main import _3dCSCG_PeriodicDomainSetting
from _3dCSCG.mesh.__DEPRECATED__.coordinate_transformation.transformer import CoordinateTransformation as ___DCT___
from _3dCSCG.mesh.visualize import _3dCSCG_Mesh_Visualize
from _3dCSCG.mesh.boundaries import _3dCSCG_Mesh_Boundaries
from _3dCSCG.mesh.sub_geometry.main import _3dCSCG_Mesh_SubGeometry




from _3dCSCG.mesh.edge import _3dCSCG_Edge
from _3dCSCG.mesh.node import _3dCSCG_Node



class _3dCSCG_Mesh(CSCG_MESH_BASE):
    """The 3dCSCG mesh."""
    def __init__(self, domain, element_layout=None, EDM=None):
        assert domain.ndim == 3, " <Mesh> "
        self._domain_ = domain
        cOmm.barrier() # for safety reason

        self.___chaotic_EGN_cache___ = dict()

        self._DO_ = _3dCSCG_Mesh_DO(self)
        self.___PRIVATE_parse_element_layout___(element_layout)

        self.___PRIVATE_BASE_get_region_elements_distribution_type___()
        self.___PRIVATE_BASE_decide_EDM___(EDM)
        self.___PRIVATE_BASE_parse_element_distribution_method___()
        self.___PRIVATE_BASE_analyze_element_distribution___()

        self.___PRIVATE_generate_element_global_numbering___()
        self.___PRIVATE_optimize_element_distribution___()

        self.___PRIVATE_generate_element_map___()
        self.___PRIVATE_modify_elements_map_wr2_periodic_setting___()
        self.___PRIVATE_generate_boundary_element_sides___()

        self.___DEPRECATED_ct___ = ___DCT___(self) # only for test purpose
        self._elements_ = _3dCSCG_Mesh_Elements(self)
        self._trace_ = _3dCSCG_Trace(self)
        self._edge_ = _3dCSCG_Edge(self)
        self._node_ = _3dCSCG_Node(self)
        self._visualize_ = _3dCSCG_Mesh_Visualize(self)
        self._boundaries_ = _3dCSCG_Mesh_Boundaries(self)
        self._sub_geometry_ = _3dCSCG_Mesh_SubGeometry(self)
        self.___define_parameters___ = None
        self.___TEST_MODE___ = False
        self.DO.RESET_cache()
        self._freeze_self_()



    @accepts('self', (tuple, list, int, dict, "NoneType"))
    def ___PRIVATE_parse_element_layout___(self, element_layout):
        rns = self.domain.regions.names
        # __ prepare the element_layout ...
        if not isinstance(element_layout, dict):
            EL = {}
            for rn in rns:
                EL[rn] = element_layout
        else:
            EL = element_layout

        # We first parse the input ...
        self._element_layout_: Dict[str] = dict()
        self._element_ratio_: Dict[str] = dict()
        self._element_spacing_: Dict[str] = dict()
        self._num_elements_in_region_: Dict[str] = dict()
        for rn in rns:
            self._element_layout_[rn], self._element_ratio_[rn], \
            self._element_spacing_[rn], self._num_elements_in_region_[rn] = \
                self.___PRIVATE_parse_element_layout_each_region___(EL[rn])
        self._num_total_elements_ = 0
        self._num_elements_accumulation_ = dict()
        for rn in rns:
            self._num_total_elements_ += self._num_elements_in_region_[rn]
            self._num_elements_accumulation_[self._num_total_elements_] = rn

    def ___PRIVATE_parse_element_layout_each_region___(self, element_layout):
        """ """

        _el_ = self.___PRIVATE_BASE_analyze_element_layout___(element_layout)

        # __ check _el_, nothing but _el_ goes beyond ......

        assert len(_el_) == 3

        for i in range(self.ndim):
            if isinstance(_el_[i], int):
                pass
            elif _el_[i].__class__.__name__ in ('tuple', 'list', 'ndarray'):
                assert np.ndim(_el_[i]) == 1, \
                    " <Mesh> : elements_layout[{}]={} is wrong.".format(i, _el_[i])
                assert np.min(_el_[i]) > 0, \
                    " <Mesh> : elements_layout[{}]={} is wrong.".format(i, _el_[i])
            else:
                raise ElementsLayoutError(
                    " <Mesh> : elements_layout[{}]={} is wrong.".format(i, _el_[i]))
        # We then parse _element_layout_, _element_ratio_, _element_spacing_ ----------
        _element_layout_: list = [None for _ in range(self.ndim)]
        _element_ratio_: list = [None for _ in range(self.ndim)]
        _element_spacing_: list = [None for _ in range(self.ndim)]
        for i in range(self.ndim):
            if isinstance(_el_[i], int):
                assert _el_[i] >= 1, \
                    " <Mesh> : elements_layout[{}]={} is wrong.".format(i, _el_[i])
                _element_layout_[i] = _el_[i]
                _element_ratio_[i] = 1 / _el_[i] * np.ones(_el_[i])
            elif _el_[i].__class__.__name__ in ('tuple', 'list', 'ndarray'):
                _element_layout_[i] = np.size(_el_[i])
                _element_ratio_[i] = np.array(_el_[i]) / np.sum(np.array(_el_[i]))
            else:
                raise ElementsLayoutError(
                    " <Mesh> : elements_layout[{}]={} is wrong.".format(i, _el_[i]))
            _element_spacing_[i] = np.zeros(_element_layout_[i] + 1)
            _element_spacing_[i][-1] = 1
            for j in range(1, _element_layout_[i]):
                _element_spacing_[i][j] = np.sum(_element_ratio_[i][0:j])
        # Now we some properties ...
        _element_layout_: tuple = tuple(_element_layout_)
        _element_ratio_: tuple = tuple(_element_ratio_)
        _element_spacing_: tuple = tuple(_element_spacing_)
        _num_elements_in_region_ = np.prod(_element_layout_)
        return _element_layout_, _element_ratio_, _element_spacing_, _num_elements_in_region_










    def ___PRIVATE_generate_element_global_numbering___(self, number_what=None):
        """
        IMPORTANT: we can number in whatever sequence within a region, but cross-region, we must number them in the
        sequence : regions.names.

        :param number_what:
        :return:
        """
        EDM = self._EDM_
        rns = self.domain.regions.names

        if number_what is None:
            DO_number_what = self.___USEFUL_regions_and_boundaries___
        elif number_what == 'all regions':
            DO_number_what = rns
        elif isinstance(number_what, str) and number_what in rns:
            DO_number_what = [number_what,]
        else:
            raise Exception()

        ___element_global_numbering___ = dict()

        if EDM is None:
            current_num = 0
            for rn in rns:
                if rn in DO_number_what:
                    ___element_global_numbering___[rn] = \
                        np.arange(current_num,
                                  current_num + self._num_elements_in_region_[rn]).reshape(
                                    self._element_layout_[rn], order='F')
                else:
                    pass
                current_num += self._num_elements_in_region_[rn]

        elif EDM == "chaotic":
            current_num = 0
            for rn in rns:
                if rn in DO_number_what:

                    ___element_global_numbering___[rn] = \
                        np.arange(current_num,
                                  current_num + self._num_elements_in_region_[rn]).reshape(
                                    self._element_layout_[rn], order='C')

                else:
                    pass
                current_num += self._num_elements_in_region_[rn]

        elif EDM == 'cores_no_more_than_regions':
            current_num = 0
            for rn in rns:
                if rn in DO_number_what:
                    ___element_global_numbering___[rn] = \
                        np.arange(current_num,
                                  current_num + self._num_elements_in_region_[rn]).reshape(
                                    self._element_layout_[rn], order='F')
                else:
                    pass
                current_num += self._num_elements_in_region_[rn]

        elif EDM == 'SWV0': # smart way version 0; cores do not contain elements from different regions.

            self.___SWV0_para___ = dict() # once this method will need optimization, we initialize a variable like this.

            current_num = 0

            for rn in rns:
                if rn in DO_number_what:

                    cores_for_this_region = self.___region_cores_dict___[rn]

                    NCR = len(cores_for_this_region)

                    # !-Once we use _element_distribution_, _element_indices_, or _num_local_elements_, wo do this:   !!
                    if not hasattr(self, '___have_empty_core___'):
                        self.___have_empty_core___ = dict()
                    if rn in self.___have_empty_core___:
                        # to make sure that after optimization, character_num_elements does not change
                        have_empty_core = self.___have_empty_core___[rn]
                    else:
                        have_empty_core = False
                        for c_iii in cores_for_this_region:
                            if len(self._element_distribution_[c_iii]) == 0:
                                have_empty_core = True
                                break
                        self.___have_empty_core___[rn] = have_empty_core
                    # !--------------------------------------------------------------------------------------------   !!

                    if NCR == 1 or have_empty_core:

                        EGN = np.arange(current_num,
                                        current_num + self._num_elements_in_region_[rn]).reshape(
                                        self._element_layout_[rn], order='F')

                    else:

                        if NCR < 4: # number of core in this region is 2 or 3.
                            I, J, K = self._element_layout_[rn]
                            A = [I, J, K]
                            A.sort()
                            _E_ = np.arange(current_num,
                                            current_num + self._num_elements_in_region_[rn]).reshape(A, order='F')

                        else:

                            # in this region, the element numbering will be range(start, end).
                            start = current_num
                            end = current_num + self._num_elements_in_region_[rn]



                            #!-Once we use _element_distribution_, _element_indices_, or _num_local_elements_, wo do this
                            if not hasattr(self, '___character_num_elements___'):
                                self.___character_num_elements___ = dict()
                            if rn in self.___character_num_elements___:
                                # to make sure that after optimization, character_num_elements does not change
                                character_num_elements = self.___character_num_elements___[rn]
                            else:
                                character_num_elements = list()
                                for core in cores_for_this_region:
                                    character_num_elements.append(len(self._element_distribution_[core]))
                                character_num_elements = int(np.mean(character_num_elements))
                                if character_num_elements <= 0: character_num_elements = 1
                                assert character_num_elements <= self._num_elements_in_region_[rn]
                                self.___character_num_elements___[rn] = character_num_elements
                            #!------------------------------------------------------------------------------------------!


                            I, J, K = self._element_layout_[rn] # to determine which scheme to do the numbering.

                            if character_num_elements <= 3:

                                _E_ = np.arange(current_num,
                                                current_num + self._num_elements_in_region_[rn]).reshape(
                                                self._element_layout_[rn], order='F')

                            elif I == J == K:
                                # prepare the memory.
                                _E_ = np.empty(self._element_layout_[rn], dtype=int)

                                # same amount elements along all directions
                                for i in range(1, I+2):
                                    if i**3 > character_num_elements:
                                        break
                                # noinspection PyUnboundLocalVariable
                                i -= 1
                                if i == 0: i = 1

                                if character_num_elements >= 4 and i < 2:
                                    i = 2

                                if i > I: i = I
                                # we will number in small block of i*i elements at x-y plain. And go along z-direction.

                                B = I // i # can have B blocks along x and y.
                                R = I % i  # will have R elements resting along x and y.

                                N = start

                                self.___SWV0_para___[rn] = [I,]
                                for n in range(B):
                                    if n != B-1:
                                        for m in range(B):
                                            if m != B-1:
                                                PLUS = i * i * I
                                                pylon = np.arange(N, N + PLUS).reshape((i, i, I), order='F')
                                                N += PLUS
                                                _E_[m*i:(m+1)*i, n*i:(n+1)*i, : ] = pylon
                                                self.___SWV0_para___[rn].append(PLUS)

                                            else:
                                                PLUS = (i+R) * i * I
                                                pylon = np.arange(N, N + PLUS).reshape((i+R, i, I), order='F')
                                                N += PLUS
                                                _E_[m*i:, n*i:(n+1)*i, : ] = pylon
                                                self.___SWV0_para___[rn].append(PLUS)

                                    else:
                                        for m in range(B):
                                            if m != B-1:
                                                PLUS = i * (i+R) * I
                                                pylon = np.arange(N, N + PLUS).reshape((i, i+R, I), order='F')
                                                N += PLUS
                                                _E_[m*i:(m+1)*i, n*i:, : ] = pylon
                                                self.___SWV0_para___[rn].append(PLUS)

                                            else:
                                                PLUS = (i+R) * (i+R) * I
                                                pylon = np.arange(N, N + PLUS).reshape((i+R, i+R, I), order='F')
                                                N += PLUS
                                                _E_[m*i:, n*i:, : ] = pylon
                                                self.___SWV0_para___[rn].append(PLUS)

                                assert N == end, "must be like this!"

                            else: # we end up with a situation we do not know how to do a proper numbering.

                                A = [I, J, K]
                                A.sort()
                                A0, A1, A2 = A

                                if A2 / A1 >= NCR * 0.75: # on A2, we have a lot more elements, so we block the region along A2

                                    _E_ = np.arange(current_num,
                                                    current_num + self._num_elements_in_region_[rn]).reshape(A, order='F')

                                else: # we now define a general numbering rule.

                                    CNE = character_num_elements  # we use this number to decide how to divide the region.

                                    if A0 * A1 * A0 <= CNE: # A0 * A1 is significantly low.
                                        _E_ = np.arange(current_num,
                                                        current_num + self._num_elements_in_region_[rn]).reshape(A, order='F')
                                    else:

                                        _E_ = np.empty([A0, A1, A2], dtype=int)

                                        R01 = A0 / A1
                                        R02 = A0 / A2

                                        Y = (R02 * CNE / R01**2)**(1/3)
                                        X = Y * R01

                                        X, Y = int(X), int(Y)
                                        X = 1 if X == 0 else X
                                        Y = 1 if Y == 0 else Y

                                        if CNE > 4 and A0 >= 2 and A1 >= 2:
                                            if X < 2: X = 2
                                            if Y < 2: Y = 2

                                        X = A0 if X > A0 else X
                                        Y = A1 if Y > A1 else Y

                                        B0 = A0 // X # can have B0 blocks along A0
                                        R0 = A0 % X  # will have R0 elements resting A0
                                        B1 = A1 // Y # can have B1 blocks along A1
                                        R1 = A1 % Y  # will have R1 elements resting A1

                                        N = start

                                        self.___SWV0_para___[rn] = [A2,]
                                        for n in range(B1):
                                            if n != B1 - 1:
                                                for m in range(B0):
                                                    if m != B0 - 1:
                                                        PLUS = X * Y * A2
                                                        pylon = np.arange(N, N + PLUS).reshape((X, Y, A2), order='F')
                                                        N += PLUS
                                                        _E_[m * X:(m + 1) * X, n * Y:(n + 1) * Y, :] = pylon
                                                        self.___SWV0_para___[rn].append(PLUS)

                                                    else:
                                                        PLUS = (X + R0) * Y * A2
                                                        pylon = np.arange(N, N + PLUS).reshape((X + R0, Y, A2), order='F')
                                                        N += PLUS
                                                        _E_[m * X:, n * Y:(n + 1) * Y, :] = pylon
                                                        self.___SWV0_para___[rn].append(PLUS)

                                            else:
                                                for m in range(B0):
                                                    if m != B0 - 1:
                                                        PLUS = X * (Y + R1) * A2
                                                        pylon = np.arange(N, N + PLUS).reshape((X, Y + R1, A2), order='F')
                                                        N += PLUS
                                                        _E_[m * X:(m + 1) * X, n * Y:, :] = pylon
                                                        self.___SWV0_para___[rn].append(PLUS)

                                                    else:
                                                        PLUS = (X + R0) * (Y + R1) * A2
                                                        pylon = np.arange(N, N + PLUS).reshape((X + R0, Y + R1, A2), order='F')
                                                        N += PLUS
                                                        _E_[m * X:, n * Y:, :] = pylon
                                                        self.___SWV0_para___[rn].append(PLUS)

                                        assert N == end, "Something is wrong!, check above lines."

                        # A general scheme to transpose _E_ into EGN ...

                        ESP = _E_.shape                 # shape of _E_
                        DSP = self._element_layout_[rn] # designed shape

                        E0, E1, E2 = ESP

                        if (E0, E1, E2) == DSP:
                            EGN = _E_.transpose((0, 1, 2))
                        elif (E0, E2, E1) == DSP:
                            EGN = _E_.transpose((0, 2, 1))
                        elif (E1, E0, E2) == DSP:
                            EGN = _E_.transpose((1, 0, 2))
                        elif (E1, E2, E0) == DSP:
                            EGN = _E_.transpose((1, 2, 0))
                        elif (E2, E0, E1) == DSP:
                            EGN = _E_.transpose((2, 0, 1))
                        elif (E2, E1, E0) == DSP:
                            EGN = _E_.transpose((2, 1, 0))
                        else:
                            raise Exception("SHOULD NEVER REACH HERE.")

                    # give EGN to dict: ___element_global_numbering___ if this region is numbered.
                    ___element_global_numbering___[rn] = EGN

                else: # this region is not numbered, lets pass.
                    pass

                current_num += self._num_elements_in_region_[rn]

        else:
            raise Exception(f"element_distribution_method: '{EDM}' not coded for "
                            f"<generate_element_global_numbering>.")





        # check element global numbering ......
        current_num = 0
        for rn in rns:

            if rn in ___element_global_numbering___:
                egn_rn = ___element_global_numbering___[rn]
                assert egn_rn.__class__.__name__ == 'ndarray' and np.ndim(egn_rn) == 3, "must be a 3-d array."
                assert np.min(egn_rn) == current_num and \
                       np.max(egn_rn) == current_num + self._num_elements_in_region_[rn] - 1, \
                       f'Element numbering range in region {rn} is wrong. Cross regions, the overall numbering must be increasing.'
                # this means within a region, the element numbering can be anything, but overall, it has to be increasing through rns.

                A = np.shape(egn_rn)
                assert A == self._element_layout_[rn], f"___element_global_numbering___[{rn}] shape wrong!"
                assert self._num_elements_in_region_[rn] == np.prod(A), "A trivial check."
                if self._num_elements_in_region_[rn] < 1000:
                    A = egn_rn.ravel('F')
                    A = set(A)
                    assert len(A) == self._num_elements_in_region_[rn]

            current_num += self._num_elements_in_region_[rn]





        # return or save to self ...
        if number_what is None:
            self.___element_global_numbering___ = ___element_global_numbering___
        elif number_what == 'all regions':
            return ___element_global_numbering___
        elif isinstance(number_what, str) and number_what in rns:
            return ___element_global_numbering___[number_what]
        else:
            raise Exception()



    def ___PRIVATE_generate_element_global_numbering_for_region___(self, region_name):
        """generate element numbering for one region."""
        # rns = self.domain.regions.names
        # current_num = 0
        # for rn in rns:
        #     if rn == region_name:
        #         return np.arange(current_num, current_num + self._num_elements_in_region_[rn]).reshape(
        #                 self._element_layout_[rn], order='F')
        #     else:
        #         pass
        #     current_num += self._num_elements_in_region_[rn]

        return self.___PRIVATE_generate_element_global_numbering___(number_what=region_name)

    def ___PRIVATE_generate_ALL_element_global_numbering___(self):
        # rns = self.domain.regions.names
        # ALL_element_global_numbering = dict()
        # current_num = 0
        # for rn in rns:
        #     ALL_element_global_numbering[rn] = \
        #         np.arange(current_num, current_num + self._num_elements_in_region_[rn]).reshape(
        #         self._element_layout_[rn], order='F')
        #     current_num += self._num_elements_in_region_[rn]
        # return ALL_element_global_numbering

        return self.___PRIVATE_generate_element_global_numbering___(number_what='all regions')

    def ___PRIVATE_element_division_and_numbering_quality___(self):
        """find the quality of element division (to cores) and element (region-wise global) numbering quality.

        :return: A tuple of 2 outputs:

                1. The overall quality (of the whole mesh across all cores.) 1 is best, 0 is worst.
                2. The local quality of this core.
        """
        if sIze == 1: return 1, 1

        INTERNAL = 0
        EXTERNAL = 0
        BOUNDARY = 0

        for i in self.elements:
            for j in range(6):
                W = self.elements.map[i][j]

                if isinstance(W, str):
                    BOUNDARY += 1
                else:
                    if W in self.elements:
                        INTERNAL += 1
                    else:
                        EXTERNAL += 1

        loc_qua = (INTERNAL + BOUNDARY) / (self.elements.num * 6)

        I = cOmm.reduce(INTERNAL, root=mAster_rank, op=MPI.SUM)
        E = cOmm.reduce(EXTERNAL, root=mAster_rank, op=MPI.SUM)
        B = cOmm.reduce(BOUNDARY, root=mAster_rank, op=MPI.SUM)

        if rAnk == mAster_rank:
            ALL_FACES = self.elements.GLOBAL_num * 6
            assert I + E + B == ALL_FACES, "Something is wrong."
            QUALITY = (I + B) / ALL_FACES
        else:
            QUALITY = None

        QUALITY = cOmm.bcast(QUALITY, root=mAster_rank)

        return QUALITY, loc_qua

    def ___PRIVATE_matplot_local_elements___(self):
        """

        :return:
        """
        local_elements = dict() # keys are region name, values are indices of local elements
        for i in self.elements:
            rn, lid = self.___DO_find_region_name_and_local_indices_of_element___(i)
            if rn not in local_elements:
                local_elements[rn] = (list(), list(), list())
            indices = local_elements[rn]
            indices[0].append(lid[0])
            indices[1].append(lid[1])
            indices[2].append(lid[2])

        LOCAL_ELEMENTS = cOmm.gather(local_elements, root=mAster_rank)
        if rAnk == mAster_rank:

            for i, LE in enumerate(LOCAL_ELEMENTS):

                num_regions = len(LE)

                dis = '1' + str(num_regions)

                fig = plt.figure(figsize=(6*num_regions, 6))

                for f, rn in enumerate(LE):
                    plot_num = int(dis + str(f+1))

                    ax = fig.add_subplot(plot_num, projection='3d')
                    indices = LE[rn]

                    ax.scatter(*indices, marker='s')
                    ax.set_xlim3d(0, self._element_layout_[rn][0] - 1)
                    ax.set_ylim3d(0, self._element_layout_[rn][1] - 1)
                    ax.set_zlim3d(0, self._element_layout_[rn][2] - 1)
                    ax.set_xlabel("axis-0")
                    ax.set_ylabel("axis-1")
                    ax.set_zlabel("axis-2")
                    ax.set_title(rn)

                plt.suptitle(f"core #{i}")

                plt.show()
                plt.close()




    def ___PRIVATE_optimize_element_distribution___(self):
        """After generating global element numbering, we can further do a optimization to further reduce the element
        side shearing between cores. This will adjust a bit the element distribution in cores, but should not adjust
        too much.

        :return:
        """
        if self._EDM_ == 'SWV0':

            JUST_PASS = self.___SWV0_para___ == dict()
            JUST_PASS = cOmm.allreduce(JUST_PASS, op=MPI.LAND)

            if JUST_PASS: return

            # we first merge all ___SWV0_para___ to master ...
            _PA_ = cOmm.gather(self.___SWV0_para___, root=mAster_rank)
            if rAnk == mAster_rank:
                PARA = dict()
                for P in _PA_:
                    for pr in P:
                        if pr in PARA:
                            assert P[pr] == PARA[pr], "___SWV0_para___ in different cores must be the same."
                        else:
                            PARA[pr] = P[pr]
                # Now, all ___SWV0_para___ are in PARA ...

                NEW_DIS = dict()

                for rn in self.___region_cores_dict___:

                    if rn in PARA:
                        Loc_Cor = self.___region_cores_dict___[rn]
                        for c in Loc_Cor: assert c not in NEW_DIS, "Safety checker."
                        loc_Par = PARA[rn]
                        layers = loc_Par[0]
                        blocks = loc_Par[1:]

                        num_blocks = len(blocks)
                        num_LocCor = len(Loc_Cor)

                        if num_blocks < 2:
                            pass
                        elif num_LocCor < num_blocks:
                            pass
                        elif layers == 1:
                            pass
                        else:
                            if num_LocCor == num_blocks:
                                for i, c in enumerate(Loc_Cor):
                                    NEW_DIS[c] = blocks[i]
                            else:
                                _d1_ = [num_LocCor // num_blocks + (1 if x < num_LocCor % num_blocks else 0) for x in range(num_blocks)]

                                ___DO___ = True

                                for i, B in enumerate(blocks):

                                    if _d1_[i] > layers:
                                        ___DO___ = False
                                        break

                                if ___DO___:

                                    _d2_ = break_list_into_parts(Loc_Cor, _d1_)

                                    for i, B in enumerate(blocks):

                                        _d3_ = [layers // _d1_[i] + (1 if x < layers % _d1_[i] else 0) for x in range(_d1_[i])][::-1]

                                        num_ele_per_layer = int(B / layers)
                                        assert num_ele_per_layer * layers == B, "Something is wrong."


                                        if mAster_rank in _d2_[i]:

                                            OC = list()

                                            for c, L in zip(_d2_[i], _d3_):
                                                if c == mAster_rank:
                                                    if L <= 2:
                                                        ML = L
                                                    else:
                                                        ML = int(self.___MC_LF___ * L)

                                                    TO_OTHER = L - ML

                                                else:
                                                    OC.append(c)

                                            # noinspection PyUnboundLocalVariable
                                            if TO_OTHER == 0 or len(OC) == 0:
                                                pass
                                            else:
                                                NOC = len(OC)
                                                DIS_D = [TO_OTHER // NOC + (1 if x < TO_OTHER % NOC else 0) for x in range(NOC)]

                                                for j, c in enumerate(_d2_[i]):
                                                    if c == mAster_rank:
                                                        # noinspection PyUnboundLocalVariable
                                                        _d3_[j] = ML
                                                    else:
                                                        _d3_[j] += DIS_D.pop()

                                        if sEcretary_rank in _d2_[i]:
                                            OC = list()
                                            for c, L in zip(_d2_[i], _d3_):
                                                if c == mAster_rank:
                                                    pass

                                                elif c == sEcretary_rank:
                                                    if L <= 2:
                                                        ML = L
                                                    else:
                                                        ML = int(self.___SC_LF___ * L)

                                                    TO_OTHER = L - ML

                                                else:
                                                    OC.append(c)


                                            if TO_OTHER == 0 or len(OC) == 0:
                                                pass
                                            else:
                                                NOC = len(OC)
                                                DIS_D = [TO_OTHER // NOC + (1 if x < TO_OTHER % NOC else 0) for x in range(NOC)]

                                                for j, c in enumerate(_d2_[i]):
                                                    if c == sEcretary_rank:
                                                        _d3_[j] = ML
                                                    elif c == mAster_rank:
                                                        pass
                                                    else:
                                                        _d3_[j] += DIS_D.pop()


                                        for c, L in zip(_d2_[i], _d3_):

                                            NEW_DIS[c] = L * num_ele_per_layer


                for c in self._element_distribution_:
                    if c not in NEW_DIS:
                        NEW_DIS[c] = len(self._element_distribution_[c])

                # do the things: Now, we must have disDict ...
                assert isinstance(NEW_DIS, dict)
                for i in range(sIze): assert i in NEW_DIS, f"NEW_DIS not full, miss distribution for core #{i}."
                ED = dict()
                before_elements = 0
                for i in range(sIze):
                    ED[i] = range(before_elements, before_elements + NEW_DIS[i])
                    before_elements += NEW_DIS[i]

            else:
                ED = None

            ED = cOmm.bcast(ED, root=mAster_rank)
            self._element_distribution_ = ED
            self._element_indices_ = self._element_distribution_[rAnk]
            self._num_local_elements_ = len(self._element_indices_)

        else: # no need to optimize ...
            return

        # has to do another check ...
        self.___PRIVATE_BASE_analyze_element_distribution___()



    def ___PRIVATE_fetch_side_element___(self, region_name, local_indices):
        """
        We try to find the global numbering of the elements or boundary
        attaching to the local element "local_indices" in region
        "region_name".

        Parameters
        ----------
        region_name : str
        local_indices : tuple

        """
        _side_element_ = dict()
        # _N ...
        _side_element_['N'] = None
        if local_indices[0] == 0:
            # then this element's North side is on the region North side.
            what_attached = self.domain.regions.map[region_name][
                self.domain.regions(region_name)._side_name_to_index_('N')]
            if what_attached in self.domain._boundary_names_:
                _side_element_['N'] = what_attached
            else:  # must be another region
                _side_element_['N'] = self._element_global_numbering_[what_attached][
                    -1, local_indices[1], local_indices[2]]
        else:  # then this element's North element another element in this region
            _side_element_['N'] = self._element_global_numbering_[region_name][
                local_indices[0] - 1, local_indices[1], local_indices[2]]

        # _S ...
        _side_element_['S'] = None
        if local_indices[0] == int(self._element_layout_[region_name][0] - 1):
            # then this element's South side is on the region South side.
            what_attached = self.domain.regions.map[region_name][
                self.domain.regions(region_name)._side_name_to_index_('S')]
            if what_attached in self.domain._boundary_names_:
                _side_element_['S'] = what_attached
            else:  # must be another region

                _side_element_['S'] = self._element_global_numbering_[what_attached][
                    0, local_indices[1], local_indices[2]]


        else:  # then this element's South element is another element in this region
            try:
                _side_element_['S'] = self._element_global_numbering_[region_name][
                    local_indices[0] + 1, local_indices[1], local_indices[2]]
            except IndexError:
                # seems to be the problem in memoize1, using memoize 5 or 2 is likely OK.
                em = f"global elements numbering shape: {self._element_global_numbering_[region_name].shape}, " \
                     f"request indices: {local_indices[0] + 1, local_indices[1], local_indices[2]}. " \
                     f"If this error happens again, back here."
                raise Exception(em)

        # _W ...
        _side_element_['W'] = None
        if local_indices[1] == 0:
            # then this element's West side is on the region Left side.
            what_attached = self.domain.regions.map[region_name][
                self.domain.regions(region_name)._side_name_to_index_('W')]
            if what_attached in self.domain._boundary_names_:
                _side_element_['W'] = what_attached
            else:  # must be another region
                _side_element_['W'] = self._element_global_numbering_[what_attached][
                    local_indices[0], -1, local_indices[2]]
        else:  # then this element's West element another element in this region
            _side_element_['W'] = self._element_global_numbering_[region_name][
                local_indices[0], local_indices[1] - 1, local_indices[2]]

        # _E ...
        _side_element_['E'] = None
        if local_indices[1] == self._element_layout_[region_name][1] - 1:
            # then this element's East side is on the region Right side.
            what_attached = self.domain.regions.map[region_name][
                self.domain.regions(region_name)._side_name_to_index_('E')]
            if what_attached in self.domain._boundary_names_:
                _side_element_['E'] = what_attached
            else:  # must be another region
                _side_element_['E'] = self._element_global_numbering_[what_attached][
                    local_indices[0], 0, local_indices[2]]
        else:  # then this element's East element another element in this region
            _side_element_['E'] = self._element_global_numbering_[region_name][
                local_indices[0], local_indices[1] + 1, local_indices[2]]

        # _B ...
        _side_element_['B'] = None
        if local_indices[2] == 0:
            # then this element's Back side is on the region Left side.
            what_attached = self.domain.regions.map[region_name][
                self.domain.regions(region_name)._side_name_to_index_('B')]
            if what_attached in self.domain._boundary_names_:
                _side_element_['B'] = what_attached
            else:  # must be another region
                _side_element_['B'] = self._element_global_numbering_[what_attached][
                    local_indices[0], local_indices[1], -1]
        else:  # then this element's Back element another element in this region
            _side_element_['B'] = self._element_global_numbering_[region_name][
                local_indices[0], local_indices[1], local_indices[2] - 1]

        # _E ...
        _side_element_['F'] = None
        if local_indices[2] == self._element_layout_[region_name][2] - 1:
            # then this element's Front side is on the region Right side.
            what_attached = self.domain.regions.map[region_name][
                self.domain.regions(region_name)._side_name_to_index_('F')]
            if what_attached in self.domain._boundary_names_:
                _side_element_['F'] = what_attached
            else:  # must be another region
                _side_element_['F'] = self._element_global_numbering_[what_attached][
                    local_indices[0], local_indices[1], 0]
        else:  # then this element's Front element another element in this region
            _side_element_['F'] = self._element_global_numbering_[region_name][
                local_indices[0], local_indices[1], local_indices[2] + 1]

        # ...
        _se_ = list()
        for i in range(6):
            side_name = 'NSWEBF'[i]
            _se_.append(_side_element_[side_name])
        return _se_

    def ___PRIVATE_generate_element_map___(self):
        """We now by studying the self.domain.region_map generate element_map which will be the key property of a mesh,
        because it actually records the topology of a mesh.
        """
        self.___element_map___: Dict[int, Union[tuple, list]] = dict()

        RP = []

        for i in self._element_indices_:
            region_name, local_indices = self.___DO_find_region_name_and_local_indices_of_element___(i)
            _em_i_ = self.___PRIVATE_fetch_side_element___(region_name, local_indices)
            self.___element_map___[i] = _em_i_

            if region_name not in RP:
                RP.append(RP)

        self.___involved_regions___ = RP


        if len(self._element_indices_) == 0: # to make sure we initialized the memoize cache.
            self.___DO_find_region_name_and_local_indices_of_element___(-1)

    def ___PRIVATE_initializing_periodic_setting___(self):

        pBPs = self.domain.domain_input.periodic_boundary_pairs

        self._periodic_setting_ = _3dCSCG_PeriodicDomainSetting(self, pBPs)
        CES = list()
        for KEYi in self.periodic_setting.periodic_region_side_pairs.keys():
            CES.extend(self.periodic_setting.periodic_region_side_pairs[KEYi].correspondence_of_element_sides)
        return CES

    def ___PRIVATE_modify_elements_map_wr2_periodic_setting___(self):
        """"""
        ___USEFUL_periodicElementSidePairs___ = self.___PRIVATE_initializing_periodic_setting___()
        self.___useful_periodic_element_side_pairs___ = list() # will be used for example when generating trace elements

        self.___local_periodic_element_sides___ = list()
        self.___local_periodic_elements___ = list()

        sideIndexDict = {'N': 0, 'S': 1, 'W': 2, 'E': 3, 'B': 4, 'F': 5}
        for eachPair in ___USEFUL_periodicElementSidePairs___:
            pairType, elements, sides = self.___DO_parse_element_side_pair___(eachPair)[:3]
            if pairType == 'regular|regular':
                elementOne, elementTwo = elements
                sideOne, sideTwo = sides
                if elementOne in self.___element_map___:
                    self.___element_map___[elementOne][sideIndexDict[sideOne]] = elementTwo
                if elementTwo in self.___element_map___:
                    self.___element_map___[elementTwo][sideIndexDict[sideTwo]] = elementOne

                if elementOne in self.___element_map___ or elementTwo in self.___element_map___:
                    self.___useful_periodic_element_side_pairs___.append(eachPair)

                if elementOne in self.___element_map___:
                    self.___local_periodic_element_sides___.append(str(elementOne)+sideOne)
                    if elementOne not in self.___local_periodic_elements___:
                        self.___local_periodic_elements___.append(elementOne)
                if elementTwo in self.___element_map___:
                    self.___local_periodic_element_sides___.append(str(elementTwo)+sideTwo)
                    if elementTwo not in self.___local_periodic_elements___:
                        self.___local_periodic_elements___.append(elementTwo)

            else:
                raise ElementSidePairError(f"Pair: {pairType} is not understandable.")

        for i in self.___element_map___:
            self.___element_map___[i] = tuple(self.___element_map___[i])

    def ___PRIVATE_generate_boundary_element_sides___(self):
        self.___boundary_element_sides___ = dict()
        for bn in self.domain._boundary_names_:
            self.___boundary_element_sides___[bn] = ()

        for i in self._element_indices_:
            region_name, local_indices = self.___DO_find_region_name_and_local_indices_of_element___(i)
            _em_i_ = self.___element_map___[i]
            for j in range(len(_em_i_)):
                if _em_i_[j] in self.domain._boundary_names_:
                    side_name = self.domain.regions(region_name)._side_index_to_name_(j)
                    self.___boundary_element_sides___[_em_i_[j]] += (str(i) + '-' + side_name,)





    @property
    def ___statistic___(self):
        """
        This is a reserved property. It will be called from property `statistic` which
        is an inherited `property` for any class that inherit `FrozenClass` class.
        """
        _dict_ = dict()
        _dict_['total element number'] = self._num_total_elements_
        return _dict_

    @property
    def ___parameters___(self):
        """
        This `parameters` is used to compare if meshes are the same. Therefore, the
        `___parameters___` should can uniquely identify a mesh. We also use it tor save and restore a mesh.

        So it is mandatory for saving a mesh.
        """
        return self.___define_parameters___

    def __eq__(self, other):
        return self.standard_properties.parameters == other.standard_properties.parameters




    def RESET_cache(self):
        self.trace.RESET_cache()
        if self.trace._elements_ is not None:
            self.trace.elements.RESET_cache()
        self.elements.RESET_cache()
        self.boundaries.RESET_cache()
        self.___element_global_numbering___ = None




    @staticmethod
    def ___DO_parse_element_side_pair___(eP: str):
        """Element side pairs are also used for trace element keys."""
        if eP.count('-') == 1:
            # must be regular pair to domain boundary!
            elementOne = int(eP.split('-')[0])
            sideOne = eP.split('-')[1][0]
            boundaryName = eP.split('|')[1]
            return 'regular|domainBoundary', elementOne, sideOne, boundaryName
        elif eP.count('-') == 2:
            elementOne, pairTypeINFO, elementTwo = eP.split('-')
            elementOne = int(elementOne)
            elementTwo = int(elementTwo)
            if len(pairTypeINFO) == 3 and pairTypeINFO[1] == '|':
                # regular pair; conforming pair; N|S, W|E, B|F and no twist!
                sideOne = pairTypeINFO[0]
                sideTwo = pairTypeINFO[2]
                return 'regular|regular', [elementOne,
                                           elementTwo], sideOne + sideTwo, None  # None for future extension.
                # for all kinds of pair, return has follow this same rule!
            else:
                raise ElementSidePairError(f"Pair: {pairTypeINFO} is not understandable.")
        else:
            raise Exception('elementSidePair format wrong!')

    def ___DO_find_region_name_of_element___(self, i):
        """ Find the region of ith element. """
        region_name = None
        for num_elements_accumulation in self._num_elements_accumulation_:
            if i < num_elements_accumulation:
                region_name = self._num_elements_accumulation_[num_elements_accumulation]
                break
        return region_name

    @memoize5 # must use memoize
    def ___DO_find_region_name_and_local_indices_of_element___(self, i):
        """ Find the region and the local numbering of ith element. """
        if i == -1: return None # to make sure we initialized the memoize cache.
        region_name = None
        for num_elements_accumulation in self._num_elements_accumulation_:
            if i < num_elements_accumulation:
                region_name = self._num_elements_accumulation_[num_elements_accumulation]
                break
        try:
            local_indices = tuple(np.argwhere(self._element_global_numbering_[region_name] == i)[0])
        except TypeError:
            # we have _element_global_numbering_ is None, but still try to use it, must be in TEST MODE
            assert self.___TEST_MODE___, 'This happens only when TEST MODE is ON.'
            if hasattr(self, '___TEST_cache___'):
                local_indices = self.___TEST_cache___[i][1]
            else:
                self._melt_self_()
                self.___TEST_cache___ = dict()
                self._freeze_self_()
                AEGN = self.___PRIVATE_generate_ALL_element_global_numbering___()
                for j in range(self._num_total_elements_):
                    if j not in self._element_indices_:
                        rnj = None
                        for num_elements_accumulation in self._num_elements_accumulation_:
                            if j < num_elements_accumulation:
                                rnj = self._num_elements_accumulation_[num_elements_accumulation]
                                break
                        LIj = tuple(np.argwhere(AEGN[rnj] == j)[0])
                        self.___TEST_cache___[j] = [rnj, LIj]
                return self.___TEST_cache___[i]
        return region_name, local_indices

    def ___DO_find_reference_origin_and_size_of_element_of_given_local_indices___(
        self, region_name, local_indices):
        origin = [None for _ in range(self.ndim)]
        delta = [None for _ in range(self.ndim)]
        for i in range(self.ndim):
            origin[i] = self._element_spacing_[region_name][i][local_indices[i]]
            delta[i] = self._element_ratio_[region_name][i][local_indices[i]]
        return tuple(origin), tuple(delta)

    def ___DO_find_reference_origin_and_size_of_element___(self, i):
        """
        Find the origin, the UL corner(2D), NWB corner (3D), and the size of
        the ith element in the reference region [0,1]^ndim.
        """
        region_name, local_indices = self.___DO_find_region_name_and_local_indices_of_element___(i)
        return self.___DO_find_reference_origin_and_size_of_element_of_given_local_indices___(
            region_name, local_indices)

    def ___DO_find_slave_of_element___(self, i: int) -> int:
        """Find the core rank of mesh element #i."""
        DISTRI = self._element_distribution_
        if isinstance(i, str): i = int(i)
        if sIze <= 6 or not self.___is_occupying_all_cores___:
            for nC in range(sIze):
                if i in DISTRI[nC]: return nC
            raise Exception()
        midCore0 = 0
        midCore1 = sIze // 2
        midCore2 = sIze
        while i not in DISTRI[midCore1] and midCore1 - midCore0 > 2 and midCore2 - midCore1 > 2:
            if i > max(DISTRI[midCore1]):
                midCore0 = midCore1
                midCore1 = (midCore0 + midCore2) // 2
            elif i < min(DISTRI[midCore1]):
                midCore2 = midCore1
                midCore1 = (midCore0 + midCore2) // 2
            else:
                raise Exception
        if i in DISTRI[midCore1]:
            return midCore1
        elif i > np.max(DISTRI[midCore1]):
            for noCore in range(midCore1, midCore2):
                if i in DISTRI[noCore]: return noCore
        elif i < np.min(DISTRI[midCore1]):
            for noCore in range(midCore0, midCore1):
                if i in DISTRI[noCore]: return noCore
        else:
            raise Exception

    def ___DO_regionwsie_stack___(self, *nda_s):
        """
        Wo should only use it in one core (first collect all data to this core).

        We use this method to stack a ndarray region-wise. This function is very useful
        in plotting reconstruction data. Since in a region, the elements are structure,
        we can plot element by element. But if we group data from elements of the same
        region, then we can plot region by region. This very increase the plotting speed
        significantly.

        Parameters
        ----------
        nda_s : ndarray
            The ndarray to be stacked. The ndim of the 'nda' must be self.ndim + 1. and
            np.shape('nda')[0] must == self._num_total_elements_.

        Returns
        -------
        output : tuple
        """
        _SD_ = tuple()
        for nda in nda_s:
            assert np.ndim(nda) == self.ndim + 1
            assert np.shape(nda)[0] == self._num_total_elements_
            _sd_ = dict()
            ijk = np.shape(nda)[1:]
            I, J, K = ijk
            ALL_element_global_numbering_ = \
                self.___PRIVATE_generate_ALL_element_global_numbering___()
            for Rn in ALL_element_global_numbering_:
                region_data_shape = [ijk[i] * self._element_layout_[Rn][i] for i in range(3)]
                _sd_[Rn] = np.zeros(region_data_shape)
                for k in range(self._element_layout_[Rn][2]):
                    for j in range(self._element_layout_[Rn][1]):
                        for i in range(self._element_layout_[Rn][0]):
                            _sd_[Rn][i * I:(i + 1) * I, j * J:(j + 1) * J, k * K:(k + 1) * K] = \
                                nda[ALL_element_global_numbering_[Rn][i, j, k]]
            _SD_ += (_sd_,)
        _SD_ = _SD_[0] if len(nda_s) == 1 else _SD_
        return _SD_





    @property
    def _element_global_numbering_(self):
        return self.___element_global_numbering___




    @property
    def DO(self):
        return self._DO_

    @property
    def elements(self):
        return self._elements_

    @property
    def periodic_setting(self):
        return self._periodic_setting_

    @property
    def domain(self):
        return self._domain_

    @property
    def ndim(self):
        return self.domain.ndim

    @property
    def trace(self):
        """The trace (face) mesh"""
        return self._trace_

    @property
    def edge(self):
        """The edge mesh!"""
        return self._edge_

    @property
    def node(self):
        """The node mesh!"""
        return self._node_

    @property
    def visualize(self):
        return self._visualize_

    @property
    def boundaries(self):
        return self._boundaries_

    @property
    def sub_geometry(self):
        return self._sub_geometry_

    @property
    def quality(self):
        """A factor in [0,1] that reflects the quality of the mesh; 1
        the best, 0 the worst.
        """
        return self.trace.quality['average quality']



class _3dCSCG_Mesh_DO(FrozenOnly):
    def __init__(self, mesh):
        self._mesh_ = mesh
        self._FIND_ = _3dCSCG_Mesh_DO_FIND(self)
        self._freeze_self_()

    def RESET_cache(self):
        self._mesh_.RESET_cache()

    def parse_element_side_pair(self, eP):
        return self._mesh_.___DO_parse_element_side_pair___(eP)



    def FIND_region_name_of_element(self, i):
        return self._mesh_.___DO_find_region_name_of_element___(i)

    def FIND_region_name_and_local_indices_of_element(self, i):
        return self._mesh_.___DO_find_region_name_and_local_indices_of_element___(i)

    def FIND_reference_origin_and_size_of_element_of_given_local_indices(self, region_name, local_indices):
        return self._mesh_.___DO_find_reference_origin_and_size_of_element_of_given_local_indices___(
            region_name, local_indices)

    def FIND_reference_origin_and_size_of_element(self, i):
        return self._mesh_.___DO_find_reference_origin_and_size_of_element___(i)

    def FIND_slave_of_element(self, i):
        """Find the core rank of mesh element #i."""
        return self._mesh_.___DO_find_slave_of_element___(i)

    def FIND_element_attach_to_region_side(self, region, side_name):
        """

        :param str region:
        :param str side_name:
        :return:
        """
        EGN1 = self._mesh_.___PRIVATE_generate_element_global_numbering_for_region___(region)
        if side_name == 'N':
            elements = EGN1[ 0, :, :]
        elif side_name == 'S':
            elements = EGN1[-1, :, :]
        elif side_name == 'W':
            elements = EGN1[ :, 0, :]
        elif side_name == 'E':
            elements = EGN1[ :,-1, :]
        elif side_name == 'B':
            elements = EGN1[ :, :, 0]
        elif side_name == 'F':
            elements = EGN1[ :, :,-1]
        else:
            raise Exception()
        return elements

    @property
    def FIND(self):
        return self._FIND_


    def regionwsie_stack(self, *args):
        return self._mesh_.___DO_regionwsie_stack___(*args)



class _3dCSCG_Mesh_DO_FIND(FrozenOnly):
    def __init__(self, DO):
        self._DO_ = DO
        self._freeze_self_()



    def region_name_of_element(self, i):
        return self._DO_.FIND_region_name_of_element(i)

    def region_name_and_local_indices_of_element(self, i):
        return self._DO_.FIND_region_name_and_local_indices_of_element(i)

    def reference_origin_and_size_of_element_of_given_local_indices(self, region_name, local_indices):
        return self._DO_.FIND_reference_origin_and_size_of_element_of_given_local_indices(
            region_name, local_indices)

    def reference_origin_and_size_of_element(self, i):
        return self._DO_.FIND_reference_origin_and_size_of_element(i)

    def slave_of_element(self, i):
        """Find the core rank of mesh element #i."""
        return self._DO_.FIND_slave_of_element(i)

    def element_attach_to_region_side(self, region, side_name):
        """

        :param str region:
        :param str side_name:
        :return:
        """
        return self._DO_.FIND_element_attach_to_region_side(region, side_name)