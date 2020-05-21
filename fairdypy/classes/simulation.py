import time
import numpy as np
import random


class Simulation():
    def __init__(
            self,
            #block settings
            blocks,
            num_of_stripes,
            #Storage settings
            storage_fault_mode=None,
            num_of_storage=None,
            #heal/repair settings
            lazy_heal_threshold_hor=None,
            lazy_heal_threshold_vert=None,
            repair_cycle=1,
            #history storage settings
            include_history=False,
            include_fault_history=False,
            #other settings
            verbose=False
        ):
        #Block definition variable:
        self.blocks = blocks
        self.horizontal_wordblocks = None
        self.horizontal_extrablocks = None
        self.vertical_wordblocks = None
        self.vertical_extrablocks = None
        self.num_of_stripes = num_of_stripes
        # Stripes initiated as healthy stripe * blocks numpy array (y * x)
        self.array = np.ones((self.num_of_stripes, self.blocks), dtype=int)
        self.empty_blocks = None

        #History variables
        self.history = None
        self.fault_history = None
        self.baf_history = None
        self.blocks_failed_history = None
        self.blocks_healed_history = None
        self.include_history = include_history
        self.include_fault_history = include_fault_history

        #Heal settings
        self.repair_cycle = repair_cycle
        self.lazy_heal_threshold_hor = lazy_heal_threshold_hor
        self.lazy_heal_threshold_vert = lazy_heal_threshold_vert

        #Storage fault setting variables
        self.storage_fault_mode = None if storage_fault_mode is None else storage_fault_mode.lower()
        self.num_of_storage = num_of_storage
        self._storage_check()
        self._create_storage_fault_array()

        # Other setting variables:
        self.baf = 1
        self.verbose = verbose
        self._type = None
        self.start_time = time.process_time()

    def __str__(self):
        #Standard Stringer
        return str(self.array)

    def _storage_check(self):
        if self.storage_fault_mode is not None:
            if not (self.storage_fault_mode in ["random", "equal_shuffle", "hash_block_index", "custom"]):
                raise ValueError("storage_fault_mode must be \"random\", \"equal_shuffle\", \"hash_block_index\" or \"custom\"")
        if self.storage_fault_mode is None and self.num_of_storage is not None:
            raise ValueError("storage_fault_mode must be set to enable num_of_storage")
        if self.storage_fault_mode is not None and self.num_of_storage is None:
            raise ValueError("num_of_storage must be set if storage_fault_mode is chosen")

    def _create_storage_fault_array(self):
        if self.storage_fault_mode == "random":
            # places the blocks randomly into storages
            # storages can be of varying sizes
            fault_array = [
                random.randint(1, self.num_of_storage)
                for block in range(self.num_of_stripes * self.blocks)
                ]
            self.storage_fault_array = np.reshape(fault_array, (self.num_of_stripes, self.blocks))
            return
        if self.storage_fault_mode == "equal_shuffle":
            # Places the blocks randomly in equally large (if possible) storages
            # for 100 blocks in 10 storages you get 10 blocks per storage.
            # does not account for empty blocks
            fault_array = np.array([
                (block % self.num_of_storage) + 1
                for block in range(self.num_of_stripes * self.blocks)
                ], dtype=int)
            np.random.shuffle(fault_array)
            self.storage_fault_array = np.reshape(fault_array, (self.num_of_stripes, self.blocks))
            return
        if self.storage_fault_mode == "hash_block_index":
            # Apply hash function to the string value of the index of the block
            # modulo hashvalue with number of storage locations
            # add 1 to get a storage placement
            fault_array = np.array([
                (hash(str(block)) % self.num_of_storage) +1
                for block in range(self.num_of_stripes * self.blocks)
                ], dtype=int)
            self.storage_fault_array = np.reshape(fault_array, (self.num_of_stripes, self.blocks))
            return
        if self.storage_fault_mode == "custom":
            # if storage_fault_mode is set to custom then a custom fault_Array
            # can be provided after initiating the simulation object.
            return

    def _fault_injection(self, p_error):
        #Fault only for valid blocks
        if self.num_of_storage is not None and self.storage_fault_mode is not None:
            # create empty fault array
            fault_array = np.zeros(self.array.shape)

            # roll chances to survive per storage
            chance_to_survive = np.random.rand(self.num_of_storage)

            # Create fault_array
            for i, survival in enumerate(chance_to_survive):
                fault_array = fault_array + np.multiply((self.storage_fault_array == i+1), survival)

            # Fail blocks in storages where survival_chance is below p_error.
            # In cace of non-overlapping GPC, preserver empty blocks
            fault_array = np.multiply(self.array, fault_array)
            fault_array = (fault_array > p_error) + (fault_array < 0)
            self.array = np.multiply(self.array, fault_array)
        else:
            fault_array = np.multiply(self.array, np.random.rand(self.num_of_stripes, self.blocks))
            # if arrays are empty they are set to a negative number.
            # since the fault_array >= p_error is mutually exclusive
            # to fault_array < 0 these can be added, and empty blocks will never be altered
            fault_array = (fault_array > p_error) + (fault_array < 0)
            self.array = np.multiply(self.array, fault_array)

    def _self_vertical_heal(self):
        pass

    def _self_horizontal_heal(self):
        pass

    def _update_baf(self):
        pass



    def loop_simulation(self, loops, baf_limit=0.0, p_error=0.2):
        # initialize and check p_error array
        if isinstance(p_error, float):
            p_error = np.full(loops, p_error, dtype=np.float64)
        if len(p_error) != loops:
            raise ValueError((
                "p_error ({len_p_error}) must be same length "
                "as number of loops ({loops})"
                ).format(
                    len_p_error=len(p_error),
                    loops=loops))
        
        #check that p_error is between 0 and 1
        _p_error_check(p_error=p_error)

        if self.verbose:
            print("loop simulation started with:\n\tloops: ", loops)
            if self.lazy_heal_threshold_vert is not None:
                print("\tVertical lazy heal threshold is set at: ", self.lazy_heal_threshold_hor)
            else:
                print("\tVertical eager heal")

            if self.lazy_heal_threshold_hor is not None:
                print("\tHorizontal lazy heal threshold is set at: ", self.lazy_heal_threshold_hor)
            else:
                print("\tHorizontal eager heal")

        # initialize history and fault_history
        if self.include_history:
            self.history = np.empty(loops + 1, dtype=object)
            self.history[0] = self.array
        if self.include_fault_history:
            self.fault_history = np.empty(loops + 1, dtype=object)
            self.fault_history[0] = np.zeros((self.num_of_stripes, self.blocks), dtype=int)

        # initialize baf-history and heals and failures
        self.baf_history = np.empty(loops + 1, dtype=np.float64)
        self.baf_history[0] = self.baf
        self.blocks_failed_history = np.empty(loops + 1, dtype=int)
        self.blocks_failed_history[0] = 0
        self.blocks_healed_history = np.empty(loops + 1, dtype=int)
        self.blocks_healed_history[0] = 0

        for i in range(loops):
            if i % 10 == 0 and self.verbose:
                print("Number of loops done: ", i)
                print("\tbaf: ", self.baf)
                print("\tprocess time: ", time.process_time() - self.start_time)
                print()

            healthy_before_fault = np.sum(self.array == 1)
            self._fault_injection(p_error[i])
            self.blocks_failed_history[i+1] = healthy_before_fault - np.sum(self.array == 1)

            if self.include_fault_history:
                self.fault_history[i+1] = np.array(self.array)

            healthy_before_heal = np.sum(self.array == 1)

            for _ in range(self.repair_cycle):
                if self.horizontal_wordblocks == 1 and self.horizontal_extrablocks == 0:
                    #If Reed Solomon, no vertical heal.
                    pass
                else:
                    self._self_vertical_heal()
                self._self_horizontal_heal()

            self.blocks_healed_history[i+1] = np.sum(self.array == 1) - healthy_before_heal
            # update history
            if self.include_history:
                self.history[i+1] = np.array(self.array)

            # update baf and baf-history
            self._update_baf()
            self.baf_history[i+1] = self.baf

            #Check if baf-limit has been reached.
            if self.baf <= baf_limit:
                if self.verbose:
                    print((
                        "BAF-limit of {baf_limit} reached after "
                        "{i} loops with BAF at : {baf}").format(
                            baf_limit=baf_limit, i=i+1, baf=self.baf
                        ))

                #if break because of baf limit, set history only to actually used
                if self.include_history:
                    self.history = self.history[0:i+2]
                if self.include_fault_history:
                    self.fault_history = self.fault_history[0:i+2]
                self.baf_history = self.baf_history[0:i+2]
                self.blocks_failed_history = self.blocks_failed_history[0:i+2]
                self.blocks_healed_history = self.blocks_healed_history[0:i+2]
                return

        if self.verbose:
            print("Finished ", loops, " loops")


def _p_error_check(p_error):
    for i, _ in enumerate(p_error):
        if(p_error[i] < 0 or
           p_error[i] > 1):
            raise ValueError((
                "p_error ({p_err} at index {index}) can not be larger "
                "than 1 or smaller than zero"
                ).format(
                    p_err=p_error[i],
                    index=i))
