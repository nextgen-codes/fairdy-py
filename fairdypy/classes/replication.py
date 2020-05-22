import numpy as np
from .reed_solomon_code import Reed_solomon


class Replication(Reed_solomon):
    """Creates a Replication object for running simulations
    
    replications (int): number of replications
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
            replications,
            num_of_stripes,
            lazy_heal_threshold=1,
            storage_fault_mode=None,
            num_of_storage=None,
            include_history=False,
            include_fault_history=False,
            verbose=False
            ):
        super().__init__(
            word_blocks=1, # only 1 wordblock in replication, all others are replications
            extra_blocks=replications,
            num_of_stripes=num_of_stripes,
            lazy_heal_threshold=lazy_heal_threshold,
            num_of_storage=num_of_storage,
            storage_fault_mode=storage_fault_mode,
            include_history=include_history,
            include_fault_history=include_fault_history,
            verbose=verbose
        )
        self._type = "replication"