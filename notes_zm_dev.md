
--------------------------------------------------------------------------------
# Interactive Job

```shell
# Perlmutter
salloc --nodes 1 --qos interactive --time 4:00:00 --constraint cpu --account=e3sm
salloc --nodes 1 --qos interactive --time 4:00:00 --constraint gpu --account=e3sm

# chrysalis
salloc --nodes 1 --qos interactive --time 4:00:00 --account=e3sm
srun --pty --nodes=1 --time=04:00:00 /bin/bash
```


--------------------------------------------------------------------------------
# Running with valgrind

```shell
salloc --nodes 2 --qos interactive --time 4:00:00 --account=e3sm
srun --pty --nodes=1 --time=04:00:00 /bin/bash

CASE=E3SM.2025-ZM-DEV-00.F2010xx-ZM.ne4pg2.NT_96.debug
CASE_ROOT=/lcrc/group/e3sm/ac.whannah/scratch/chrys/$CASE
cd $CASE_ROOT
source $CASE_ROOT/case_scripts/.env_mach_specific.sh

# cd $CASE_ROOT/bld/cmake-bld/
# make -j 256

cd $CASE_ROOT/run
# mkdir -p  timing/checkpoints
# srun --mpi=pmi2 -l -n 96 -N 2 --kill-on-bad-exit --cpu_bind=cores  -c 2 -m plane=64 $CASE_ROOT/bld/e3sm.exe
valgrind srun --mpi=pmi2 -l -n 96 -N 2 --kill-on-bad-exit --cpu_bind=cores  -c 2 -m plane=64 $CASE_ROOT/bld/e3sm.exe  &> tmp_log

```

--------------------------------------------------------------------------------
# Running with GDB

```shell
salloc --nodes 1 --qos interactive --time 4:00:00 --account=e3sm
srun --pty --nodes=1 --time=04:00:00 /bin/bash

CASE=E3SM.2025-ZM-DEV-00.F2010xx-ZM.ne4pg2.NT_1.debug
CASE_ROOT=/lcrc/group/e3sm/ac.whannah/scratch/chrys/$CASE
cd $CASE_ROOT
source $CASE_ROOT/case_scripts/.env_mach_specific.sh

# cd $CASE_ROOT/bld/cmake-bld/
# make -j 256

# cd $CASE_ROOT/run
# # mkdir -p  timing/checkpoints
# srun --mpi=pmi2 -l -n 96 -N 2 --kill-on-bad-exit --cpu_bind=cores  -c 2 -m plane=64 $CASE_ROOT/bld/e3sm.exe
# valgrind srun --mpi=pmi2 -l -n 96 -N 2 --kill-on-bad-exit --cpu_bind=cores  -c 2 -m plane=64 $CASE_ROOT/bld/e3sm.exe  &> tmp_log

module load gcc/9.2.0-ugetvbp
module load gdb

cd $CASE_ROOT/run

gdb $CASE_ROOT/bld/e3sm.exe

/gpfs/fs1/soft/chrysalis/spack/opt/spack/linux-centos8-x86_64/gcc-9.2.0/gdb-12.1-2ip75al/bin/gdb $CASE_ROOT/bld/e3sm.exe

break __cxa_throw

```

--------------------------------------------------------------------------------
# Building Unit Tests - chrysalis

```shell
E3SM_SRC=${HOME}/E3SM/E3SM_SRC3
TEST_ROOT=/lcrc/group/e3sm/ac.whannah/scratch/chrys/zm_dev/tests
mach=chrysalis
comp=intel

# move in to build dir (note it is printed above)
cd ${TEST_ROOT}/full_debug

# load CIME env
eval $(${E3SM_SRC}/cime/CIME/Tools/get_case_env -c SMS.ne4pg2_ne4pg2.F2010-SCREAMv1.${mach}_${comp}) && export OMP_NUM_THREADS=1 && export CTEST_PARALLEL_LEVEL=128 && export OMP_PROC_BIND=spread;

# configure
${E3SM_SRC}/components/eamxx/scripts/test-all-eamxx -m ${mach} -t dbg --config-only -w ${TEST_ROOT}

# build
cd ${TEST_ROOT}/full_debug/src/physics/zm/tests
make -j128


```

you'd need to go inside the dir after -w and add the type of test:
`cd /lcrc/group/e3sm/ac.whannah/scratch/chrys/zm_dev/tests/TYPE`
where TYPE is determined by the option after -t
```
dbg ==> full_debug
sp  ==> full_sp_debug
opt ==> release
```

--------------------------------------------------------------------------------
# Building Unit Tests - perlmutter

```shell
# E3SM_SRC=/pscratch/sd/w/whannah/tmp_eamxx_src
E3SM_SRC=/global/homes/w/whannah/E3SM/E3SM_SRC4
TEST_ROOT=/pscratch/sd/w/whannah/zm_dev/tests
mach=pm-cpu
comp=gnu

cd ${TEST_ROOT}/full_debug

eval $(${E3SM_SRC}/cime/CIME/Tools/get_case_env -c SMS.ne4pg2_ne4pg2.F2010-SCREAMv1.${mach}_${comp}) && export OMP_NUM_THREADS=1 && export CTEST_PARALLEL_LEVEL=128 && export OMP_PROC_BIND=spread;

${E3SM_SRC}/components/eamxx/scripts/test-all-eamxx -m ${mach} -t dbg --config-only -w ${TEST_ROOT}

cd ${TEST_ROOT}/full_debug/src/physics/zm/tests
make -j128


OMP_NUM_THREADS=1 gdb ./zm_tests

break __cxa_throw
run

OMP_NUM_THREADS=1 valgrind ./zm_tests


```

--------------------------------------------------------------------------------
