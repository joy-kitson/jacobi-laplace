# Jacobi/Laplace2D OpenACC Example Code

Note: These instructions have been tested on Vader. Many of the commands below will not work on Windows,
and the module commands will probably only work on a node of a computing cluster

Compiling
------
In order to build the provided code:
1. Make sure you have PGI and CUDA loaded on your system.

   On Vader, you can do this with the command `module load pgi/19.4 cuda/system`.
   You can verify that these modules were loaded successfully by running `module list`. 
   The output should look something like this:
```
Currently Loaded Modules:
  1) pgi/19.4   2) cuda/system
```

2. `cd` into the src directory
3. Make sure we're compiling for the right GPU
   
   First, run the command `pgaccelinfo`. This will have a lot of output, by you can ignore everything
   besides the last line, which should look something like:
   
```
PGI Default Target:            -ta=tesla:cc60
```

   Make sure to remember that bit after the `-ta=`, in this case `tesla:cc60. Now open up the makefile
   with your editor of choice. Look for line 17:
   
```
GPU_TA=tesla:cc60 
```

   The part after the `=` should match what you saw after the `-ta=` earlier (in this case, both are
   the same, so we don't need to change anything). If it doesn't, change it so that it matches.

4. Finally, it's time to actually build the code. Run
   * `make seq` to build the sequential version of the code
   * `make multi` to build the multi-threaded CPU version of the code
   * `make gpu` to build the GPU version of the code
  
   or just `make` or `make all` to build all three executables

Running
------
Now that you've built the executables, you can run anyone of them with `./<exec> <rows> <cols>`
to test the code with `<rows>` by `<cols>` matrices. (There are other options, but this is the one
we'll be using.)

  ex: `./seq 1024 1024` runs the sequential code on 1024 by 1024 matrices
  
  The output here should look something like:
  
```
Jacobi relaxation Calculation: 1024 x 1024 mesh
    0, 0.250000
  100, 0.002397
  200, 0.001204
  300, 0.000804
  400, 0.000603
  500, 0.000483
  600, 0.000403
  700, 0.000345
  800, 0.000302
  900, 0.000269
 total: 3.278877 s
```

For the multicore version, we have one other option: we can adjust how many cores the system will use
to run the code. We do this by setting the `ACC_NUM_CORES` environment variable right before running.

ex: `ACC_NUM_CORES=6 ./multi 1024 1024` tells the system to run the multicore code with six cores on
1024 by 1024 matrices

It's worth noting that we can also not set this variable, in which case OpenACC will chose how many
threads tp use for us. In order to choose how many cores to use, try running `lscpu`. The output should
look something like this:

```
Architecture:        x86_64
CPU op-mode(s):      32-bit, 64-bit
Byte Order:          Little Endian
CPU(s):              12
On-line CPU(s) list: 0-11
Thread(s) per core:  2
Core(s) per socket:  6
Socket(s):           1
NUMA node(s):        1
Vendor ID:           GenuineIntel
CPU family:          6
Model:               44
Model name:          Intel(R) Core(TM) i7 CPU       X 990  @ 3.47GHz
Stepping:            2
CPU MHz:             1602.766
CPU max MHz:         3468.0000
CPU min MHz:         1600.0000
BogoMIPS:            6950.26
Virtualization:      VT-x
L1d cache:           32K
L1i cache:           32K
L2 cache:            256K
L3 cache:            12288K
NUMA node0 CPU(s):   0-11
Flags:               fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc cpuid aperfmperf pni pclmulqdq dtes64 monitor ds_cpl vmx est tm2 ssse3 cx16 xtpr pdcm pcid sse4_1 sse4_2 popcnt aes lahf_lm pti ssbd ibrs ibpb stibp tpr_shadow vnmi flexpriority ept vpid dtherm ida arat flush_l1d
```

We're only really interested these lines:

```
CPU(s):              12
Thread(s) per core:  2
Core(s) per socket:  6
Socket(s):           1
```

This tells us how many cores our system actually has. `[Sockets(s)] * [Core(s) per socket]` tells us
how many physical cores we have (in this case `1*6 = 6` cores), and `Thread(s) per core` tells us that
we can get at most two logical threads from each physical core (in this case, giving us a total of
`6*2 = 12` total cores). The total number of logical cores is also given by `CPU(s)` (note that it
matches what we just calculated as our total number of cores). As a generally rule, you shouldn't ask
OpenACC to use any more cores than there are available, so you probably shouldn't set `ACC_NUM_CORES`
any higher than this number. 

Note: From tests on Vader, using any more than the number of physical cores doesn't seem to increase 
preformance, so not using anything over 6 cores would also be reasonable.

Collecting Timg Data
-----
While you could time each version of mannually just by running each one a bunch of times and averaging
the times by hand, I've also included a Python script that should make things a bit less painful. Here's
a brief summary of how to use it:

* The simplest way to run the script is with `<path_to_scripts_dir>/time_runs.py <path_to_exec>`.

  ex: From the `src` directory, this look could look like `../scripts/time_runs.py gpu`, which will time
  the GPU version of the code.
  
  By default, the script will run the given command on 1024 by 1024, 2048 by 2048, 4096 by 4096, and
  8192 by 8192 matrices 10 times, and output the average runtimes in a comma seperated value (CSV) file
  called `<exec>_times.csv` in the directory containing the executable. You should be able to open
  CSV files in any spreadsheet software (Excel, Google Sheets, etc), if you want an easier to look at
  output in a prettier format.
  
  It's worth noting that running with default arguments could take a while, especially for the 
  sequential code, and will overwrite the current output file, so be sure to make sure your data is in 
  a safe place if you don't want it to be overwritten.
  
* If you'd like to quickly test to make sure that the script is working properly, I'd suggest running
  something like this instead of using the default arguments:
  
```
../srcipts/time_runs.py seq --iters 1 --size_range 10 10
```

  This will run the sequential code once on a 1024 by 1024 (2^10 by 2^10) matrix and save the results
  to `seq_times.csv`.
  
* One way to prevent your old ouput file from being overwritten is by specifying the output file you
  want to write to, like this:
  
```
../scripts/time_runs.py seq --out_path "{}_data.csv"
```
  
  Which will save the data to `seq_data.csv`. Here the path to `seq` is subsituted in for `{}` to give
  the path to the desired output file.
  
* To specify how many cores to used when running the multicore code, you can specify that the script
  should set `ACC_NUM_CORES`, like this:
  
```
../scripts/time_runs.py multi --env_vars ACC_NUM_CORES=6
```

  which will run the code on six cores.

* You can also run the script with multiple executables by simply passing in the paths to each executable
  you want to run before adding any flags. For example:
  
```
.../scripts/time_runs.py seq multi gpu --iters 1
```
  
  Will run each of the the code versions on the default range of matrix sizes once.

* Any and all of the options I've mentioned above will work together.

* For more help, running `<path_to_scripts_dir>/time_runs.py --help` will bring up more detailed
  information on the arguments you can use. 
  
Timing Data Results
-------
If you'd like to compare your timing results to mine, check out `runtimes.xlsx` in the data directory.
