# FaiRDy-Py

FaiRDy-Py is a python implementation, and accompanying website for running cellular automata style erasure and repair simulations of storage devices as created by Veronica Estrada Galiñanes.



## Class structure

The module is set up so that it has a main class "Simulation" which contains the main functions. All other classes are subclasses of the Simulation class. The Simulation class is not meant to be created and run on its own, but used as an abstract class.

As replication is a special case of a Reed Solomon code, a Reed Solomon code is a special case of a General Pyramid code class the classes are set up in the following manner:

Simulation <-- General Pyramid Code <-- Reed Solomon <-- Replication

## Fault_injection

There are three main modes of fault injection: Random fault, and storage fault

Random fault

```
faults for every block based on the p_error which is defined while running the the simulation. For each block it will roll a random number between 0 and 1. If the number is greater or equal to p_error, it will survive. If not, it will fail.

p_error can be specified as a single float, or as an array of floats the same length as number of loops to run the simulation.
```

Storage fault

```
instead of failing each individual block, as if each block is stored on an individual storage device. Multiple blocks are stored in the same location, and for each step in the simulation every storage device has a chance to fail. If it fails, every block on that device becomes unavailable.

Storage failure has four modes for allocating blocks to storage: random, equal_shuffle, hash_block_index, and custom.

For type random: blocks are randomly divided across the specified number of storages. there is no guarantee for how many or few blocks are place in each storage container.  
For type equal_shuffle: each storage container contains an equal amount of blocks, to the extent that it is possible.
For hash_block_index: the index of each blocks is converted to string, hashed and modulo number of storage locations to distribute blocks.
for custom: a block distribution is not set by the object, but can be created by the user and set via <object>.storage_fault_array
```

## Fault_repair

Fault repair is done by looking at one Reed-Solomon stripe at a time. For Generalized Pyramid Codess, this is done first for vertical stripes and then for horizontal stripes. for Reed Solomon and Replication it is done only vertically, as they are one dimensional. Healing is performed when the number of missing blocks in a stripe exceeds or is equal to the lazy_heal_threshold, it will attemt to heal the stripe. A stripe will heal if the number of blocks left in the stripe are more than the original amount of wordblocks. If there is less blocks left than the original amount of wordblocks, the stripe is dead, and will continue to decay over the next simulations.

### Generalized pyramid codes
The Generalized Pyramid codes implemented by FaiRDy are composed of maximum distance separable (MDS) codes, such as ReedSolomon stripes, where data blocks belong to two stripes. one in the vertical direction and one in the horizontal direction. This provides
an extra layer of protection since each data block is a member of two different Reed-Solomon stripes, with each providing a possibility
for repair. Two different Generalized Pyramid code stripe constructions are possible in FaiRDy, a standard non-overlapping with the
blocks arranged in an L-shaped polygon, and an overlapping construction with the blocks arrange in the shape of a rectangle. The
overlapping construction adds an additional dimension of redundancy, with the overlapping redundancy blocks computed using the
vertically redundant as data input blocks.
Repair Rules:

In a Generalized Pyramid stripe, the vertical and horizontal Reed-Solomon stripes are repaired individually in accordance with the rules
for this erasure code. If all blocks in theGeneralized Pyramid stripe are able to be repaired in this way, the stripe is considered
completely repaired.

Non-overlapping:
The number of horizontal stripes is equal to the number of DATA blocks in the vertical stripes, and correspondingly, the number of
vertical stripes is equal to the number of DATA blocks in horizontal stripes.

Overlapping:
The number of horizontal stripes is equal to the TOTAL number of blocks in the vertical stripe, and correspondingly, the number of
vertical stripes is equal to the TOTAL number of blocks in the horizontal stripe. The overlapping redundancy blocks are computed using
the vertical redundancy blocks as the input data blocks, and thereby provide second degree redundancy.


### Reed Solomon codes
Reed-Solomon (RS) codes are optimal erasure codes, such codes are also called maximum distance separable (MDS) codes. RS codes
tolerate a number of block erasures equal to the number of redundancy blocks in the stripe. In real storage systems the contents of the
redundancy blocks are computed and decoded using advanced linear algebra, this is however ignored in FaiRDy and a stripe will be
repaired as long as enough active blocks remain to allow this.
Repair Rules:
A Reed-Solomon stripe is considered repairable as long as the number of erased blocks does not exceed the number of redundancy
blocks.

## Class parameters:

### Shared parameters:

number of stripes:

* num_of_stripes
  * The number of stripes in the object.

Heal parameters:
* Generalized Pyramid Codes
  * lazy_heal_threshold_hor
  * lazy_heal_threshold_vert
* Reed Solomon and Replication
  * lazy_heal_threshold


Storage parameters:

* storage_fault_mode
  * "random", "equal_shuffle", "hash_block_index", "custom"
  * disabled when set to None (Default)
* num_of_storage
  * amount of storage location to divide blocks into

Simulation history parameters:

These parameters store historic steps of the module if enabled. This is disabled as default. With very large object definitions, storing the history may use quite a bit of ram.

* include_history: True or False (Default)
* include_fault_history: True or False (Default)

verbose printing:

* verbose
  * True or False (Defualt)
  * output will print while running the simulation to show progress.

### Generalized pyramid code parameters

* gpc
  * full gpc definition
  * example: gpc=(30, 8)
* horizontal_rs
  * horizontal reed solomon
  * example: horizontal_rs=(4, 1)
* vertical_rs
  * vertical reed solomon
  * example: vertical_rs=(2, 4)

### Reed solomon parameters

* word_blocks
  * number of word blocks in the reed solomon code
* extra_blocks
  * number of extra blocks in the reed solomon code

### loop_simulation parameters

* loops 
  * number of loops to run in the simulation
* baf_limit
  * the cutoff limit for the simulation. If this is reached, the simulation stops.
* p_error
  * the chance for each block to fail during a failure injection.
  * this is not used if storage_fault_mode is defined.

### Information after running simulations
After simulations have been run, some information is stored on the object:

* baf_history
  * the block availability factor for the whole storage object over time.
* blocks_died_history
  * how many blocks became unavailable at every step in the simulations.
* blocks_healed_history
  * how many blocks were healed at every step in the simulation.

## Examples

To create a an object. Call the class and specify parameters:

``` python

#Generalized Pyramid Code
GPC = Generalized_pyramid_code(
    gpc_definition=(16, 8),
    horizontal_rs=(4, 2),
    vertical_rs=(2, 1),
    num_of_stripes=20,
    heal_passes=2
)

#Reed Solomon code
RS = Reed_solomon(
    word_blocks=8,
    extra_blocks=2,
    num_of_stripes=20,
    storage_fault_mode='random',
    num_of_storage=4
)
```


To run simulation. Call the loop_simulation method on the class. 

``` python
GPC.loop_simulation(
    loops=200,
    baf_limit=0.2,
    p_error=0.2
)
```
If you have specified storage_mode, p_error is not needed. Default baf_limit is 0.

``` python
RS.loop_simulation(
    loops=200
)
```

You can also pass inn an array the same size of loops for p_error
specifying the p_error for each step. 
``` python
p_error_array = np.empty(200, dtype=float)
for i in range(len(p_error)):
    p_error[i] = 0.1 + (0.002 * i)

#
RS.loop_simulation(
    loops = 200,
    baf_limit=0.2,
    p_error = p_error_array
)

```

after the simulation has finished running, the BAF is stored in the baf_history parameter.

``` python
print(GPC.baf_history)
```