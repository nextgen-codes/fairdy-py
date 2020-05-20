# FaiRDy-Py

## Introduction

## Class structure

The module is set up so that it has a main class "Simulation" which contains the main functions. All other classes are subclasses of the Simulation class. The Simulation class is not meant to be created and run on its own, but used as an abstract class.

As replication is a special case of a Reed Solomon code, a Reed Solomon code is a special case of a General Pyramid code class the classes are set up in the following manner:

Simulation <-- General Pyramid Code <-- Reed Solomon <-- Replication

## Fault_injection

There are two main modes of fault injection: Random fault, and storage fault

Random fault

    faults for every block based on the p_error which is defined while running the the simulation. For each block it will roll a random number between 0 and 1. If the number is greater or equal to p_error, it will survive. If not, it will fail.

    p_error can be specified as a single float, or as an array of floats the same length as number of loops to run the simulation.

Storage fault

    Storage fault simulates storing multiple blocks on the same storage, and then the storage fails. for each loop in the simulation, one storage will fail, and p_error does not affect the simulation.
    
    Storage failure has two modes: random and equal_shuffle.

    For type random: blocks are randomly divided across the specified number of storages. there is no guarantee for how many or few blocks are place in each storage container.  
    For type equal_shuffle: each storage container contains an equal amount of blocks, to the extent that it is possible.

## Fault_repair

### Generalized pyramid codes

### Reed Solomon codes

## Class parameters:

### Shared parameters:

number of stripes:

* num_of_stripes
  * The number of stripes in the object.

Storage parameters:

* storage_fault_mode
  * "random", "equal_shuffle"
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