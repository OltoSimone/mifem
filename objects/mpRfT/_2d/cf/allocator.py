



from screws.freeze.base import FrozenOnly


class _2nCSCG_RF2_FieldsAllocator(FrozenOnly):
    """"""



    @classmethod
    def ___form_name___(cls):
        return {'scalar': "mpRfT2_Scalar",
                }

    @classmethod
    def ___form_path___(cls):
        base_path = '.'.join(str(cls).split(' ')[1][1:-2].split('.')[:-2]) + '.'
        return {'scalar': base_path + "scalar.main",
                }