--------------------------------------------------------------------------------
# fast turnaround debug build

```shell
salloc --nodes 2 --qos interactive --time 4:00:00 --account=e3sm
srun --pty --nodes=1 --time=04:00:00 /bin/bash

CASE=E3SM.2025-GW-DEV-00.F2010-SCREAMv1.ne4pg2.NN_1.use_gw_1
CASE_ROOT=/lcrc/group/e3sm/ac.whannah/scratch/chrys/$CASE
cd $CASE_ROOT
source $CASE_ROOT/case_scripts/.env_mach_specific.sh

cd $CASE_ROOT/bld/cmake-bld/
make -j 256

cd $CASE_ROOT/run
# mkdir -p  timing/checkpoints
# srun --mpi=pmi2 -l -n 96 -N 2 --kill-on-bad-exit --cpu_bind=cores  -c 2 -m plane=64 $CASE_ROOT/bld/e3sm.exe
valgrind srun --mpi=pmi2 -l -n 96 -N 2 --kill-on-bad-exit --cpu_bind=cores  -c 2 -m plane=64 $CASE_ROOT/bld/e3sm.exe  &> tmp_log

```