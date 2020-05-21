import numpy as np
from .generalized_pyramid_code import Generalized_pyramid_code


class Reed_solomon(Generalized_pyramid_code):
    """Creates a Reed solomon code object for running simulations

    word_blocks (int): number of word blocks
    extra_blocks (int): number of extra blocks
    num_of_stripes (int): number of stripes
    lazy_heal_threshold (int): number of blocks who have to fail in a stripe before healing
    storage_fault_mode (["random", "equal_shuffle", "hash_block_index", "custom"]): choses the storage fault mode
    num_of_storage (int): number of storage locations
    include_history (bool): True if you want to include all history after each heal
    include_fault_history (bool): Ture if you want to include all fault history after each fault injection
    verbose (bool): True if printouts while running
    """
    def __init__(
            self,
            word_blocks,
            extra_blocks,
            num_of_stripes,
            lazy_heal_threshold=1,
            storage_fault_mode=None,
            num_of_storage=None,
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
        """Checks lazy_heal_threshold has to be less than extra_blocks"""
        if self.lazy_heal_threshold > self.extra_blocks:
            raise ValueError((
                "Lazy heal threshold ({thresh}) can not be "
                "larger than extra blocks ({exblocks})"
            ).format(
                thresh=self.lazy_heal_threshold,
                exblocks=self.extra_blocks))
    
    def _update_baf(self):
        """Updates the BAF"""
        self.baf = np.sum(self.array) / (self.blocks * self.num_of_stripes)

    def __str__(self):
        #Standard Stringer
        return str(self.array)

    def _self_horizontal_heal(self):
        """Simpler horizontal heal implementaiton for RS"""
        #two checks must be true to heal:
        #1. sum of stripe must be larger than wordblocks
        #2. sum of stripe must be less than or equal to heal_thresh_hold
        for stripe in self.array:
            if((np.sum(stripe) >= self.word_blocks) and
               (np.sum(stripe) <= (self.blocks - self.lazy_heal_threshold))
               ):
                stripe += 1-stripe
