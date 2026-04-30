--------------------------------------------------------------------------------

--------------------------------------------------------------------------------
# LCRC

```shell
salloc --nodes 1 --qos interactive --time 4:00:00 --constraint cpu --account=e3sm

salloc --nodes 1 --qos interactive --time 4:00:00 --account=e3sm
srun --pty --nodes=1 --time=04:00:00 /bin/bash

# CASE=E3SM.2025-GW-DEV-00.F2010-SCREAMv1.ne4pg2.NN_1.use_gw_1
CASE=E3SM.2025-GW-DEV-00.CPU.F2010-SCREAMv1.ne4pg2.NN_1.use_gw_1.debug

CASE_ROOT=/lcrc/group/e3sm/ac.whannah/scratch/chrys/$CASE
cd $CASE_ROOT
source $CASE_ROOT/case_scripts/.env_mach_specific.sh

cd $CASE_ROOT/bld/cmake-bld/
make -j 256

cd $CASE_ROOT/run
# mkdir -p  timing/checkpoints
# srun --mpi=pmi2 -l -n 96 -N 2 --kill-on-bad-exit --cpu_bind=cores  -c 2 -m plane=64 $CASE_ROOT/bld/e3sm.exe
valgrind srun --mpi=pmi2 -l -n 96 -N 1 --kill-on-bad-exit --cpu_bind=cores  -c 2 -m plane=64 $CASE_ROOT/bld/e3sm.exe  &> tmp_log

```

--------------------------------------------------------------------------------
# NERSC

```shell
salloc --nodes 1 --qos interactive --time 4:00:00 --constraint cpu --account=e3sm

# CASE=E3SM.2025-GW-DEV-00.F2010-SCREAMv1.ne4pg2.NN_1.use_gw_1
CASE=E3SM.2025-GW-DEV-00.CPU.F2010-SCREAMv1.ne4pg2.NN_1.use_gw_1.debug
# CASE=E3SM.2025-GW-DEV-00.CPU.F2010-SCREAMv1.ne4pg2.NT_1.use_gw_1.debug

CASE_ROOT=/pscratch/sd/w/whannah/scream_scratch/pm-cpu/$CASE
# CASE_ROOT=/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/$CASE
cd $CASE_ROOT
source $CASE_ROOT/case_scripts/.env_mach_specific.sh

cd $CASE_ROOT/bld/cmake-bld/ ; make -j 256

cd $CASE_ROOT/run
srun --label -n 96 -N 1 -c 2 --cpu_bind=cores $CASE_ROOT/bld/e3sm.exe

cd $CASE_ROOT/run ; srun --label -n 96 -N 1 -c 2 --cpu_bind=cores $CASE_ROOT/bld/e3sm.exe > tmp_log 2>&1

# cd $CASE_ROOT/run
# srun --label -n 1 -N 1 -c 2 --cpu_bind=cores $CASE_ROOT/bld/e3sm.exe

cd $CASE_ROOT/run
gdb $CASE_ROOT/bld/e3sm.exe
break __cxa_throw

cd $CASE_ROOT/run
# mkdir -p  timing/checkpoints
# srun --mpi=pmi2 -l -n 96 -N 2 --kill-on-bad-exit --cpu_bind=cores  -c 2 -m plane=64 $CASE_ROOT/bld/e3sm.exe

# cd $CASE_ROOT/run
# valgrind srun --mpi=pmi2 -l -n 96 -N 1 --kill-on-bad-exit --cpu_bind=cores  -c 2 -m plane=64 $CASE_ROOT/bld/e3sm.exe  &> tmp_log

cd $CASE_ROOT/run
valgrind srun --mpi=pmi2 -l -n 1 -N 1 --kill-on-bad-exit --cpu_bind=cores  -c 2 -m plane=64 $CASE_ROOT/bld/e3sm.exe  &> tmp_log

```

--------------------------------------------------------------------------------
# Unit Tests - NERSC

```shell
E3SM_SRC=/global/homes/w/whannah/E3SM/E3SM_SRC2
TEST_ROOT=/pscratch/sd/w/whannah/gw_dev/tests
mach=pm-cpu
comp=gnu

cd ${TEST_ROOT}/full_debug

eval $(${E3SM_SRC}/cime/CIME/Tools/get_case_env -c SMS.ne4pg2_ne4pg2.F2010-SCREAMv1.${mach}_${comp}) && export OMP_NUM_THREADS=1 && export CTEST_PARALLEL_LEVEL=128 && export OMP_PROC_BIND=spread;

${E3SM_SRC}/components/eamxx/scripts/test-all-eamxx -m ${mach} -t dbg --config-only -w ${TEST_ROOT}

cd ${TEST_ROOT}/full_debug/src/physics/gw/tests
make -j128

./gw_tests

OMP_NUM_THREADS=1 gdb ./gw_tests

break __cxa_throw
run

OMP_NUM_THREADS=1 valgrind ./gw_tests


```

--------------------------------------------------------------------------------
