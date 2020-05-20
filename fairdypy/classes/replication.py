import numpy as np
from .reed_solomon_code import Reed_solomon


class Replication(Reed_solomon):
    def __init__(
            self,
            replications,
            num_of_stripes,
            lazy_heal_threshold=None,
            num_of_storage=None,
            storage_fault_mode=None,
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