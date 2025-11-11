

```shell
scontrol update qos=debug jobid=
```

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
E3SM_SRC=/global/homes/w/whannah/E3SM/E3SM_SRC3
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

```shell
cd /pscratch/sd/w/whannah/tmp_eamxx_src/components/eamxx
# ./scripts/test-all-eamxx -m pm-cpu -t dbg --baseline-dir AUTO -c EKAT_DISABLE_TPL_WARNINGS=ON
./scripts/test-all-eamxx -m pm-gpu -t dbg --baseline-dir AUTO -c EKAT_DISABLE_TPL_WARNINGS=ON
```

```shell
/pscratch/sd/w/whannah/tmp_eamxx_src
/global/homes/w/whannah/E3SM/E3SM_SRC3

ZM_ROOT_SRC=/global/homes/w/whannah/E3SM/E3SM_SRC3/components/eamxx/src/physics/zm
ZM_ROOT_DST=/pscratch/sd/w/whannah/tmp_eamxx_src/components/eamxx/src/physics/zm
cp ${ZM_ROOT_SRC}/eamxx_zm_process_interface.cpp ${ZM_ROOT_DST}/eamxx_zm_process_interface.cpp ; cp ${ZM_ROOT_SRC}/eamxx_zm_process_interface.hpp ${ZM_ROOT_DST}/eamxx_zm_process_interface.hpp ; cp ${ZM_ROOT_SRC}/zm_functions.hpp ${ZM_ROOT_DST}/zm_functions.hpp

```

--------------------------------------------------------------------------------
# Running in an interactive session

```shell
salloc --nodes 1 --qos interactive --time 04:00:00 --constraint cpu --account=e3sm
# salloc --nodes 8 --qos interactive --time 04:00:00 --constraint cpu --account=e3sm

# /pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/E3SM.2025-ZM-DEV-01.F2010xx-ZM.ne4pg2.NN_1.debug/bld/cmake-bld

# CASE=E3SM.2025-ZM-DEV-01a.F2010xx-ZM.ne4pg2.NT_96.zm_apply_tend_0.debug
# CASE=E3SM.2025-ZM-DEV-04.F2010xx-ZM.ne30pg2.NN_8.zm_apply_tend_1.debug

CASE_ROOT=/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/$CASE

cd $CASE_ROOT
source $CASE_ROOT/case_scripts/.env_mach_specific.sh


cd $CASE_ROOT/bld/cmake-bld/; make -j 256

cd $CASE_ROOT/run
srun --label -n 96 -N 1 -c 2 --cpu_bind=cores -m plane=128 $CASE_ROOT/bld/e3sm.exe &> tmp_log
grep "32:" tmp_log

```

--------------------------------------------------------------------------------
# Running GPU case in interactive session

```shell
salloc --nodes 1 --qos interactive --time 04:00:00 --constraint gpu --account=e3sm

CASE=E3SM.2025-ZM-DEV-00.GPU.NT_4.ne4pg2.F2010xx-ZM.debug

CASE_ROOT=/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/$CASE
# CASE_ROOT=/pscratch/sd/w/whannah/e3sm_scratch/pm-gpu/$CASE
cd $CASE_ROOT
source $CASE_ROOT/case_scripts/.env_mach_specific.sh

cd $CASE_ROOT/bld/cmake-bld/; make -j 256

cd $CASE_ROOT/run; srun  --label  -n 4 -N 1 -c 32 -G4 --cpu_bind=cores -m plane=4 $CASE_ROOT/bld/e3sm.exe  &> tmp_log
grep "1: " tmp_log #| tail 

```

--------------------------------------------------------------------------------
# Running with valgrind

```shell
# salloc --nodes 1 --qos interactive --time 04:00:00 --constraint cpu --account=e3sm
salloc --nodes 1 --qos interactive --time 04:00:00 --constraint gpu --account=e3sm

# CASE=E3SM.2025-ZM-DEV-05a.F2010xx-ZM.ne4pg2.NT_96.zm_apply_tend_0
# CASE=E3SM.2025-ZM-DEV-05.F2010xx-ZM.ne4pg2.NT_96.zm_apply_tend_0.debug
# CASE=E3SM.2025-ZM-DEV-05b.F2010xx-ZM.ne4pg2.NT_1.zm_apply_tend_0.debug
# CASE=E3SM.2025-ZM-DEV-04.F2010xx-ZM.ne4pg2.NT_96.zm_apply_tend_1.debug
CASE=E3SM.2025-ZM-DEV-00.CPU.NT_96.ne4pg2.F2010xx-ZM.debug

CASE_ROOT=/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/$CASE

cd $CASE_ROOT
source $CASE_ROOT/case_scripts/.env_mach_specific.sh

cd $CASE_ROOT/bld/cmake-bld/
make -j 256 &> tmp_log

cd $CASE_ROOT/run
mkdir -p  timing/checkpoints
valgrind srun --label -n 96 -N 1 -c 2 --cpu_bind=cores -m plane=128 $CASE_ROOT/bld/e3sm.exe &> tmp_log

grep "32:" tmp_log

```

--------------------------------------------------------------------------------
# Running with gdb

```shell
CASE=E3SM.2025-ZM-DEV-05.F2010xx-ZM.ne4pg2.NT_96.zm_apply_tend_1.debug
CASE_ROOT=/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/$CASE

echo ; ls -l $CASE_ROOT/run/rpointer* ; echo ; cat $CASE_ROOT/run/rpointer* ; echo

sed -i  's/0001-08-14-00000/0001-07-10-00000/' $CASE_ROOT/run/rpointer*
# sed -i  's/0001-01-06-00000/0001-08-09-00000/' $CASE_ROOT/run/rpointer*

echo "${CASE}.scream.r.INSTANT.ndays_x10.0001-07-10-00000.nc" > $CASE_ROOT/run/rpointer.atm

echo ; ls -l $CASE_ROOT/run/rpointer* ; echo ; cat $CASE_ROOT/run/rpointer* ; echo

```

```shell
salloc --nodes 1 --qos interactive --time 04:00:00 --constraint cpu --account=e3sm
# define case
CASE=E3SM.2025-ZM-DEV-00.F2010xx-ZM.ne4pg2.NT_96.zm_apply_tend_1.debug
CASE_ROOT=/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/$CASE

# move to case directory
cd $CASE_ROOT
source $CASE_ROOT/case_scripts/.env_mach_specific.sh

# update tasks
cd $CASE_ROOT/case_scripts
./xmlchange NTASKS=96
# ./xmlchange NTASKS=1
./case.setup --reset

# update run config
cd $CASE_ROOT/case_scripts
./xmlchange RESUBMIT=0
./xmlchange REST_OPTION=never
# NSTEPS=8
# NSTEPS=24; ./xmlchange REST_OPTION=nsteps,STOP_OPTION=nsteps,REST_N=$NSTEPS,STOP_N=$NSTEPS
NDAYS=1 ; ./xmlchange REST_OPTION=ndays,STOP_OPTION=ndays,REST_N=$NDAYS,STOP_N=$NDAYS
./xmlquery REST_OPTION,STOP_OPTION,REST_N,STOP_N

# build
cd $CASE_ROOT/bld/cmake-bld/
make -j 256
# run
# mkdir -p  $CASE_ROOT/run/timing/checkpoints

cd $CASE_ROOT/run
srun --label -n 96 -N 1 -c 2 --cpu_bind=cores $CASE_ROOT/bld/e3sm.exe

cd $CASE_ROOT/run
srun --label -n 1 -N 1 -c 2 --cpu_bind=cores $CASE_ROOT/bld/e3sm.exe

cd $CASE_ROOT/run
gdb $CASE_ROOT/bld/e3sm.exe
break __cxa_throw
```

--------------------------------------------------------------------------------
# use ncap2 to convert precip

```shell
SRC_FILE=/global/homes/w/whannah/E3SM/scratch_pm-cpu/E3SM.2025-ZM-DEV-01.F2010xx-ZM.ne30pg2.NN_8/run/output.scream.2D.AVERAGE.ndays_x10.0001-01-01-00000.nc

DST_FILE=/global/homes/w/whannah/E3SM/scratch_pm-cpu/E3SM.2025-ZM-DEV-01.F2010xx-ZM.ne30pg2.NN_8/run/output.scream.2D.AVERAGE.ndays_x10.0001-01-01-00000_alt.nc

ncap2 -s 'precip_total_alt=precip_total_surf_mass_flux*86400*1000'  ${SRC_FILE} ${DST_FILE}
```

# create animation

```shell

convert -repage 0x0 -delay 10 -loop 0  ~/E3SM/ncvis_zm_cape_00*.png ~/E3SM/ncvis_zm_cape.gif

```