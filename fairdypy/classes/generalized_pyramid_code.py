import numpy as np
from .simulation import Simulation
class Generalized_pyramid_code(Simulation):
    """Creates a Generalized pyramid code object to run simulations on.

    gpc_defition (int, int): gpc total blocks and wordblocks in the gpc (total blocks, word blocks)
    horizontal_rs (int, int): word blocks and extra blocks in horizontal RS stripes in the gpc (word blocks, extra blocks)
    vertical_rs (int, int): word blocks and extra blocks in vertical RS stripes in the gpc (word blocks, extra blocks)
    num_of_stripes (int): number of stripes in the gpc
    lazy_heal_threshold_hor (int): number of blocks who have to fail in a stripe before healing horizontally
    lazy_heal_threshold_vert (int): number of blocks who have to fail in a stripe before healing vertically
    repair_cycle (int): how many repair cycle to run over the gpc
    storage_fault_mode (["random", "equal_shuffle", "hash_block_index", "custom"]): choses the storage fault mode
    num_of_storage (int): number of storage locations
    include_history (bool): True if you want to include all history after each heal
    include_fault_history (bool): Ture if you want to include all fault history after each fault injection
    verbose (bool): True if printouts while running
    """
    def __init__(
            self,
            # block definitions
            gpc_definition, # full gpc i.e. (30, 8)
            horizontal_rs, # horizontal RS i.e. (4, 6)
            vertical_rs, # Vertizal RS i.e. (2, 1)
            num_of_stripes,
            lazy_heal_threshold_hor=1,
            lazy_heal_threshold_vert=1,
            repair_cycle=1,
            storage_fault_mode=None,
            num_of_storage=None,
            include_history=False,
            include_fault_history=False,
            verbose=False):

        self.horizontal_length = sum(horizontal_rs)
        self.vertical_length = sum(vertical_rs)
        super().__init__(
            blocks=(self.horizontal_length * self.vertical_length),
            num_of_stripes=num_of_stripes,
            storage_fault_mode=storage_fault_mode,
            num_of_storage=num_of_storage,
            lazy_heal_threshold_hor=lazy_heal_threshold_hor,
            lazy_heal_threshold_vert=lazy_heal_threshold_vert,
            include_history=include_history,
            include_fault_history=include_fault_history,
            repair_cycle=repair_cycle,
            verbose=verbose)
        self.horizontal_wordblocks = horizontal_rs[0]
        self.horizontal_extrablocks = horizontal_rs[1]
        self.vertical_wordblocks = vertical_rs[0]
        self.vertical_extrablocks = vertical_rs[1]
        self.gpc_totalblocks = gpc_definition[0]
        self.gpc_wordblocks = gpc_definition[1]
        self.square_size = self.horizontal_length * self.vertical_length
        self.is_fully_overlapping = True if (self.gpc_totalblocks == (self.horizontal_length * self.vertical_length)) else False
        self.empty_blocks = 0 if self.is_fully_overlapping else self.square_size - self.gpc_totalblocks
        self.non_empty_blocks = self.gpc_totalblocks if self.is_fully_overlapping else self.gpc_totalblocks - self.empty_blocks
        self._type = "generalized_pyramid_code"
        self._check_overlap()
        self._self_test_gpc()
        self._initiate_empty_blocks()
        self._gpc_threshold_check()

    def _check_overlap(self):
        # if the GPC total blocks is equal to the full square (horizontal times vertical) then there is full overlap.
        # if GPC total blocks is is equal to only wordblocks, horizontal RS_blocks and vertical RS_blocks there is no overlap.
        # if GPC total blocks is between then there is partial
        if self.gpc_totalblocks == (self.horizontal_length * self.vertical_length):
            if self.vertical_length == 1:
                self.overlap_type = "full"
                if self.verbose:
                    print("overlap_type is always full for ReedSolomon")
            else:
                self.overlap_type = "full"
                if self.verbose:
                    print("overlap_type is full")
        elif self.gpc_totalblocks == self.square_size - (self.horizontal_extrablocks * self.vertical_extrablocks):
            self.overlap_type = "no"
            if self.verbose:
                print("overlap_type is no overlap")
        else:
            self.overlap_type = "partial"
            if self.verbose:
                print("overlap_type is partial")

    def _self_test_gpc(self):
        if self.vertical_wordblocks <= 0:
            raise ValueError("Vertical_wrodblocks cannot be less than or equal to 0")

        if self.horizontal_wordblocks <= 0:
            raise ValueError("Horizontal_wordblocks cannot be less than or equal to 0")

        if  self.gpc_wordblocks > self.gpc_totalblocks:
            raise ValueError((
                "gpc_wordblocks ({gpc_word}) cannot be larger than "
                "gpc_totalblocks({gpc_total})"
            ).format(
                gpc_word=self.gpc_wordblocks,
                gpc_total=self.gpc_totalblocks))

        if self.gpc_totalblocks == self.gpc_wordblocks:
            if self.horizontal_extrablocks != 0 or self.vertical_extrablocks != 0:
                raise ValueError((
                    "When total_blocks ({tot_blk}) is equal to word_blocks ({wrd_blk}) "
                    "horizontal extrablocks ({hor_ex}) or vertical extrablocks ({vert_ex}) "
                    "can not be more than 0"
                ).format(
                    tot_blk=self.gpc_totalblocks,
                    wrd_blk=self.gpc_wordblocks,
                    hor_ex=self.horizontal_extrablocks,
                    vert_ex=self.vertical_extrablocks))

        if self.gpc_wordblocks != (self.horizontal_wordblocks * self.vertical_wordblocks):
            raise ValueError((
                "gpc_worblocks ({gpc_word}) not equal to product "
                "of horizontal and vertical wordblocks ({rs_product})"
                ).format(
                    gpc_word=self.gpc_wordblocks,
                    rs_product=(self.horizontal_wordblocks * self.vertical_wordblocks)))

        if self.gpc_totalblocks > (self.horizontal_length * self.vertical_length):
            raise ValueError((
                "gpc_totalblocks ({gpc_tot}) cannot be larger than "
                "product of horizontal and vertical length ({rs_tot})"
                ).format(
                    gpc_tot=self.gpc_totalblocks,
                    rs_tot=(self.horizontal_length * self.vertical_length)))

        if self.vertical_extrablocks != 0 and self.overlap_type != 'full':
            if (self.gpc_totalblocks - (self.horizontal_length * self.vertical_wordblocks)) % self.vertical_extrablocks != 0:
                raise ValueError("Can only add full vertical RS for partial overlaps")

    def _gpc_threshold_check(self):
        if self.horizontal_extrablocks != 0:
            if self.lazy_heal_threshold_hor > self.horizontal_extrablocks:
                raise ValueError((
                    "Lazy heal horizontal threshold ({h_thresh}) "
                    "can not be larger than the number of extra blocks ({h_extr})"
                    ).format(
                        h_thresh=self.lazy_heal_threshold_hor,
                        h_extr=self.horizontal_extrablocks))
        if self.vertical_extrablocks != 0:
            if self.lazy_heal_threshold_vert > self.vertical_extrablocks:
                raise ValueError((
                    "Lazy heal vertical threshold ({v_thresh}) "
                    "can not be larger than the number of extra blocks ({v_extr})"
                    ).format(
                        v_thresh=self.lazy_heal_threshold_vert,
                        v_extr=self.vertical_extrablocks
                    ))
    
    def __str__(self):
        return str(np.reshape(self.array, (self.num_of_stripes, self.vertical_length, self.horizontal_length)))


    
    def _update_baf(self):
        """Updates BAF for GPC"""
        # accounting for empty blocks
        self.baf = np.sum(np.multiply(self.array, (self.array == 1))) / (self.gpc_totalblocks * self.num_of_stripes)

    def _initiate_empty_blocks(self):
        """Initiates empty blocks for none-overlapping GPC"""
        if self.overlap_type == "full":
            return
        arranged = np.reshape(self.array, (self.num_of_stripes, self.vertical_length, self.horizontal_length))
        #object references self.array, values are initiated under.
        arranged[
            :, # slice all stripes
            -int(self.vertical_extrablocks):,
            -int(((self.square_size - self.gpc_totalblocks) / self.vertical_extrablocks)):
            ] = -(self.horizontal_length + self.vertical_length)
 
    def _self_vertical_heal(self):
        """Heals for vertical stripes"""
        for i, stripe in enumerate(self.array):
            #one stripe at a time, reshape it for easy access
            structured_stripe = np.reshape(stripe, (self.vertical_length, self.horizontal_length))
            #create reverse where 1 is 0 and 0 is 1 (this is a full repair matrix)
            anti_structured_stripe = 1 - (structured_stripe != 0)
            #array of vertical sums
            sum_vertical_stripe = np.sum(structured_stripe, axis=0)
            for j, v_sum in enumerate(sum_vertical_stripe):
                #Perform three checks when not to heal:
                #1. Don't heal when v_sum is less than  vertical wordblocks
                #2. Don't heal when threshold amount of blocks missing is not met
                #3. Don't heal empty blocks:
                if(v_sum < self.vertical_wordblocks or
                   v_sum > self.vertical_length - self.lazy_heal_threshold_vert or
                   v_sum <= 0
                   ):
                    anti_structured_stripe[:, j] = 0
            #update self.array
            self.array[i] = (structured_stripe + anti_structured_stripe).ravel()

    def _self_horizontal_heal(self):
        """Heals for horizontal stripes"""
        for i, stripe in enumerate(self.array):
            structured_stripe = np.reshape(stripe, (self.vertical_length, self.horizontal_length))
            anti_structured_stripe = 1 - (structured_stripe != 0)
            sum_horizontal_stripe = np.sum(structured_stripe, axis=1)
            for j, h_sum in enumerate(sum_horizontal_stripe):
                #Perform three checks when not to heal:
                #1. cannot heal is h_sum is less than horizontal wordblocks
                #2. don't heal horizontally below vertical wordblocks
                #3. at lest threshold number of blocks must be missing to heal
                if(h_sum < self.horizontal_wordblocks or
                   j > self.vertical_wordblocks - 1 or
                   h_sum > self.horizontal_length - self.lazy_heal_threshold_hor
                   ):
                    anti_structured_stripe[j, :] = 0
            self.array[i] = (structured_stripe + anti_structured_stripe).ravel()
