import numpy as np
from .generalized_pyramid_code import Generalized_pyramid_code


class Reed_solomon(Generalized_pyramid_code):
    #TODO class hints
    def __init__(
            self,
            word_blocks,
            extra_blocks,
            num_of_stripes,
            lazy_heal_threshold=1,
            num_of_storage=None,
            storage_fault_mode=None,
            include_history=False,
            include_fault_history=False,
            verbose=False):
        super().__init__(
            gpc_definition=(word_blocks + extra_blocks, word_blocks),
            horizontal_rs=(word_blocks, extra_blocks),
            vertical_rs=(1, 0), # only 1 vertical block for Reed Solomon
            num_of_stripes=num_of_stripes,
            lazy_heal_threshold_hor=lazy_heal_threshold,
            num_of_storage=num_of_storage,
            storage_fault_mode=storage_fault_mode,
            include_history=include_history,
            include_fault_history=include_fault_history,
            repair_cycle=1, #Only one heal pass for reed_solomon
            verbose=verbose)
        self.lazy_heal_threshold = lazy_heal_threshold
        self.word_blocks = word_blocks
        self.extra_blocks = extra_blocks
        self._rs_threshold_check()
        self._type = "reed_solomon"
  
    def _rs_threshold_check(self):
        #this should be a reference to self.lazy_heal_threshold, but python throws an error
            if self.lazy_heal_threshold > self.extra_blocks:
                raise ValueError((
                    "Lazy heal threshold ({thresh}) can not be "
                    "larger than or equal to extra blocks ({exblocks})"
                ).format(
                    thresh=self.lazy_heal_threshold,
                    exblocks=self.extra_blocks))
    
    def _update_baf(self):
        self.baf = np.sum(self.array) / (self.blocks * self.num_of_stripes)

    def __str__(self):
        #Standard Stringer
        return str(self.array)

    def _self_horizontal_heal(self):
        #two checks must be true to heal:
        #1. sum of stripe must be larger than wordblocks
        #2. sum of stripe must be less than or equal to heal_thresh_hold
        for stripe in self.array:
            if((np.sum(stripe) >= self.word_blocks) and
               (np.sum(stripe) <= (self.blocks - self.lazy_heal_threshold))
               ):
                stripe += 1-stripe
