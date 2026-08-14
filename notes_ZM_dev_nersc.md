

```shell
scontrol update qos=debug jobid=
```

```shell
export E3SM_ENABLE_KOKKOS_BOUNDS_CHECKING=TRUE
```

~/E3SM/E3SM_SRC1/components/eamxx/src/physics/zm

--------------------------------------------------------------------------------

```shell
LOG=
grep "eamxx_zm_process_interface" $LOG -A4 -B4
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

# mach=chrysalis; comp=intel
mach=chrysalis; comp=oneapi

E3SM_SRC=${HOME}/E3SM/E3SM_SRC1
TEST_ROOT=/lcrc/group/e3sm/ac.whannah/scratch/chrys/zm_dev/tests_${comp}

# move in to build dir (note it is printed above)
cd ${TEST_ROOT}/full_debug

# load CIME env
eval $(${E3SM_SRC}/cime/CIME/Tools/get_case_env -c SMS.ne4pg2_ne4pg2.F2010-SCREAMv1.${mach}_${comp}) && export OMP_NUM_THREADS=1 && export CTEST_PARALLEL_LEVEL=128 && export OMP_PROC_BIND=spread;

# configure
${E3SM_SRC}/components/eamxx/scripts/test-all-eamxx -m ${mach} -t dbg --config-only -w ${TEST_ROOT}

# build
cd ${TEST_ROOT}/full_debug/src/physics/zm/tests
make -j128

srun ./zm_tests


```

## alternate verion that also generates baselines

```shell
mach=chrysalis; comp=intel

E3SM_SRC=${HOME}/E3SM/E3SM_SRC1
TEST_ROOT=/lcrc/group/e3sm/ac.whannah/scratch/chrys/zm_dev/tests_${comp}
BASELINE_DIR=${TEST_ROOT}/baselines

# Load environment
mkdir -p ${TEST_ROOT}/full_debug
cd ${TEST_ROOT}/full_debug
eval $(${E3SM_SRC}/cime/CIME/Tools/get_case_env -c SMS.ne4pg2_ne4pg2.F2010-SCREAMv1.${mach}_${comp})
export OMP_NUM_THREADS=1 CTEST_PARALLEL_LEVEL=128 OMP_PROC_BIND=spread

# Configure + build
${E3SM_SRC}/components/eamxx/scripts/test-all-eamxx -m ${mach} -t dbg --config-only -w ${TEST_ROOT}
cd ${TEST_ROOT}/full_debug/src/physics/zm/tests
make -j128

# Generate baselines (runs Fortran, writes reference output)
mkdir -p ${BASELINE_DIR}
srun ./zm_tests --args -g -b ${BASELINE_DIR}

# Compare C++ against baselines
srun ./zm_tests --args -c -b ${BASELINE_DIR}

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
# Unit Tests - Frontier

```shell
salloc -A cli115 -N 1 -t 2:00:00 -p batch
# salloc --nodes 1 --time 4:00:00 --account=cli115
# srun --pty --nodes=1 --time=04:00:00 /bin/bash

mach=frontier; comp=craygnu-mphipcc
E3SM_SRC=~/E3SM/E3SM_SRC2
TEST_ROOT=/lustre/orion/cli115/scratch/hannah6/zm_dev
mkdir -p ${TEST_ROOT}/full_debug
cd ${TEST_ROOT}/full_debug
eval $(${E3SM_SRC}/cime/CIME/Tools/get_case_env -c SMS.ne4pg2_ne4pg2.F2010-SCREAMv1.${mach}_${comp}) && export OMP_NUM_THREADS=1 && export CTEST_PARALLEL_LEVEL=128 && export OMP_PROC_BIND=spread;
${E3SM_SRC}/components/eamxx/scripts/test-all-eamxx -m ${mach} -t dbg --config-only -w ${TEST_ROOT}
cd ${TEST_ROOT}/full_debug/src/physics/zm/tests
make -j128
./zm_tests


E3SM_SRC=/global/homes/w/whannah/E3SM/E3SM_SRC1
TEST_ROOT=/pscratch/sd/w/whannah/zm_dev/tests_gpu
mkdir -p ${TEST_ROOT}/full_debug
cd ${TEST_ROOT}/full_debug
mach=pm-gpu; comp=gnugpu
eval $(${E3SM_SRC}/cime/CIME/Tools/get_case_env -c SMS.ne4pg2_ne4pg2.F2010-SCREAMv1.${mach}_${comp}) && export OMP_NUM_THREADS=1 && export CTEST_PARALLEL_LEVEL=4 && export OMP_PROC_BIND=spread;
${E3SM_SRC}/components/eamxx/scripts/test-all-eamxx -m ${mach} -t dbg --config-only -w ${TEST_ROOT}
cd ${TEST_ROOT}/full_debug/src/physics/zm/tests
make -j4

# run the tests
./zm_tests

OMP_NUM_THREADS=1 gdb ./zm_tests

break __cxa_throw
run

OMP_NUM_THREADS=1 valgrind ./zm_tests


```

--------------------------------------------------------------------------------
# Building Unit Tests - perlmutter

## CPU tests

```shell
salloc --nodes 1 --qos interactive --time 4:00:00 --constraint cpu --account=e3sm

mach=pm-cpu; comp=gnu
# mach=pm-cpu; comp=intel

# E3SM_SRC=/global/homes/w/whannah/E3SM/E3SM_SRC1
E3SM_SRC=/pscratch/sd/w/whannah/tmp_e3sm_src
TEST_ROOT=/pscratch/sd/w/whannah/zm_dev/tests_cpu_${comp}
mkdir -p ${TEST_ROOT}/full_debug
cd ${TEST_ROOT}/full_debug
eval $(${E3SM_SRC}/cime/CIME/Tools/get_case_env -c SMS.ne4pg2_ne4pg2.F2010-SCREAMv1.${mach}_${comp}) && export OMP_NUM_THREADS=1 && export CTEST_PARALLEL_LEVEL=128 && export OMP_PROC_BIND=spread;
${E3SM_SRC}/components/eamxx/scripts/test-all-eamxx -m ${mach} -t dbg --config-only -w ${TEST_ROOT} -b AUTO
cd ${TEST_ROOT}/full_debug/src/physics/zm/tests
make -j128
# run the tests
./zm_tests

```

## GPU tests

```shell
salloc --nodes 1 --qos interactive --time 4:00:00 --constraint gpu --account=e3sm

mach=pm-gpu; comp=gnugpu

# E3SM_SRC=/global/homes/w/whannah/E3SM/E3SM_SRC1
E3SM_SRC=/pscratch/sd/w/whannah/tmp_e3sm_src
TEST_ROOT=/pscratch/sd/w/whannah/zm_dev/tests_gpu
mkdir -p ${TEST_ROOT}/full_debug
cd ${TEST_ROOT}/full_debug
eval $(${E3SM_SRC}/cime/CIME/Tools/get_case_env -c SMS.ne4pg2_ne4pg2.F2010-SCREAMv1.${mach}_${comp}) && export OMP_NUM_THREADS=1 && export CTEST_PARALLEL_LEVEL=4 && export OMP_PROC_BIND=spread;
${E3SM_SRC}/components/eamxx/scripts/test-all-eamxx -m ${mach} -t dbg --config-only -w ${TEST_ROOT}
cd ${TEST_ROOT}/full_debug/src/physics/zm/tests
make -j4
# run the tests
./zm_tests
```

## Debugging

```shell
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


## alternate CPU version that also generates baselines

```shell
cd /pscratch/sd/w/whannah/tmp_e3sm_src
git checkout master-alt-for-baselines
git submodule sync ; git submodule update --init --recursive

salloc --nodes 1 --qos interactive --time 4:00:00 --constraint cpu --account=e3sm

mach=pm-cpu; comp=gnu

# E3SM_SRC=${HOME}/E3SM/E3SM_SRC1
E3SM_SRC=/pscratch/sd/w/whannah/tmp_e3sm_src
TEST_ROOT=/pscratch/sd/w/whannah/zm_dev/tests_cpu_${comp}
TEST_PATH=${TEST_ROOT}/full_debug/src/physics/zm/tests
BASELINE_DIR=${TEST_ROOT}/baselines_cpu

mkdir -p ${TEST_ROOT}/full_debug
mkdir -p ${BASELINE_DIR}

# Load environment
cd ${TEST_ROOT}/full_debug
eval $(${E3SM_SRC}/cime/CIME/Tools/get_case_env -c SMS.ne4pg2_ne4pg2.F2010-SCREAMv1.${mach}_${comp}) && export OMP_NUM_THREADS=1 && export CTEST_PARALLEL_LEVEL=4 && export OMP_PROC_BIND=spread;

# Configure + build
${E3SM_SRC}/components/eamxx/scripts/test-all-eamxx -m ${mach} -t dbg --config-only -w ${TEST_ROOT}
cd ${TEST_PATH}
make -j128

cd ${TEST_PATH}

./zm_tests --rng-seed 23568 --args -g -b ${BASELINE_DIR}; ./zm_tests --args -c -b ${BASELINE_DIR}

# Generate baselines (runs Fortran, writes reference output)

./zm_tests --args -g -b ${BASELINE_DIR}

# Compare C++ against baselines
./zm_tests --args -c -b ${BASELINE_DIR}

```

New CPU test with modified config to mimic GPU

```shell
salloc --nodes 1 --qos interactive --time 4:00:00 --constraint cpu --account=e3sm

mach=pm-cpu; comp=gnu
E3SM_SRC=/pscratch/sd/w/whannah/tmp_e3sm_src
TEST_ROOT=/pscratch/sd/w/whannah/zm_dev/tests_cpu_${comp}_mg
TEST_PATH=${TEST_ROOT}/full_debug/src/physics/zm/tests
BASELINE_DIR=${TEST_ROOT}/baselines_cpu_mg
mkdir -p ${TEST_ROOT}/full_debug ${BASELINE_DIR}

cd ${TEST_ROOT}/full_debug
eval $(${E3SM_SRC}/cime/CIME/Tools/get_case_env -c SMS.ne4pg2_ne4pg2.F2010-SCREAMv1.${mach}_${comp}) && export OMP_NUM_THREADS=1 && export CTEST_PARALLEL_LEVEL=4 && export OMP_PROC_BIND=spread;

${E3SM_SRC}/components/eamxx/scripts/test-all-eamxx -m ${mach} -t dbg --config-only -w ${TEST_ROOT} \
  -c SCREAM_PACK_SIZE=1 \
  -c SCREAM_FPE=OFF

# confirm it took before spending the build
grep -E "^SCREAM_PACK_SIZE:|^SCREAM_FPE:|^Kokkos_ENABLE_CUDA:|^SCREAM_DOUBLE_PRECISION:" \
  ${TEST_ROOT}/full_debug/CMakeCache.txt

cd ${TEST_PATH}
make -j128
./zm_tests --rng-seed 23568 --args -g -b ${BASELINE_DIR}; ./zm_tests --args -c -b ${BASELINE_DIR}

# zm_conv_main_bfb should fail exactly as before, on both — it already failed identically on CPU and GPU, so it's independent of all of this.

# The one to watch is zm_conv_evap_bfb:
# - fails here → pack size, i.e. expression grouping in the C++ port. Not a GPU problem, and debuggable on CPU.
# - passes here → device arithmetic. Next step would be --fmad=false on the ZM device sources to confirm FMA contraction is the source.
```


Manual bisection on CPU

```shell

# git checkout c8f59e154e4c255ebcd0a7370f185c45931b7857 # Aug 12 < FAIL
# git checkout 72ee0570474dd7369a1b471299c007d1f36c2f05 # Aug 12 < ?
# git checkout 23b2ddf2b40c6475d82a5e0fe548ad3a04b52963 # Aug 11 < ?
# git checkout 5b6018bb77f8f282c64f1bdf7f52f85f7bb4fd5b # Aug 11 < ?
# git checkout c9254a6d9f51a60b8efb914151440076de429f29 # Aug 11 < ?
# git checkout 28849b6756ced30d1e418829d28b7d9ca2e2f540 # Aug 10 < ?
# git checkout 49f1ce78bc22a5174a1a2b83a79c7e7b90353ceb # Aug 9  < ?
# git checkout 538e092bafe0f532c645bf5887736e56ddf214d4 # Aug 7  < FAIL
# git checkout a6f518470bd2b1c905eb1aa69dba5f03ab9cd41b # Aug 6  < FAIL   0.0224952577 == Approx( 0.0224694987 )
# git checkout 33c69bee3347d997e9f51bb0150746828edfa2af # Aug 6  < FAIL   0.0224952577 == Approx( 0.0224694987 )
# git checkout 5bace1fdf4de1cd0cef994a178db034a92a4ca31 # Aug 4  < FAIL   0.0224952577 == Approx( 0.0224694987 ) 
# git checkout 24ec260619207a35eb1dfd8af02d63d475807718 # Jul 10 < FAIL   0.0224952577 == Approx( 0.0224694987 )
# git checkout 01130a01361bb6536f9907a3c041f794aceca8b6 # Jul 6  < FAILx2 0.0224952577 == Approx( 0.0224694987 ) + zm_conv_evap_bfb
# git checkout 9b832f00d0582a6fcfc653cab0a463b184f3a15c # Jul 1  < FAILx2 0.0224952577 == Approx( 0.0224694987 ) + zm_conv_evap_bfb
# git checkout b50b9648ff567f66e515e8a34f13acbca8d5720f # Jun 25 < FAILx2 0.0224952577 == Approx( 0.0224694987 ) + zm_conv_evap_bfb
git checkout c314aa6d469d294e7ec40f00dbb4a218ca78c233 # Jun 24 < FAILx2 0.0224952577 == Approx( 0.0224694987 ) + zm_conv_evap_bfb
# git checkout c7285a5c734514fe6f6c88e0df1f41d18df574e7 # Jun 24 < PASS
# git checkout 72d3884fd338c60b4bc00b7e3ce2f5eae3636ab9 # Jun 17 < PASS
git submodule sync ; git submodule update --init --recursive
sed -i '93,96s/REQUIRE(/CHECK(/; 99,103s/REQUIRE(/CHECK(/; 130,141s/REQUIRE(/CHECK(/; 144,145s/REQUIRE(/CHECK(/'     components/eamxx/src/physics/zm/tests/zm_conv_main_tests.cpp

salloc --nodes 1 --qos interactive --time 4:00:00 --constraint cpu --account=e3sm

mach=pm-cpu; comp=gnu
E3SM_SRC=/pscratch/sd/w/whannah/tmp_e3sm_src
TEST_ROOT=/pscratch/sd/w/whannah/zm_dev/tests_cpu_${comp}_bisect
TEST_PATH=${TEST_ROOT}/full_debug/src/physics/zm/tests
BASELINE_DIR=${TEST_ROOT}/baselines_cpu_bisect
mkdir -p ${TEST_ROOT}/full_debug ${BASELINE_DIR}
cd ${TEST_ROOT}/full_debug
eval $(${E3SM_SRC}/cime/CIME/Tools/get_case_env -c SMS.ne4pg2_ne4pg2.F2010-SCREAMv1.${mach}_${comp}) && export OMP_NUM_THREADS=1 && export CTEST_PARALLEL_LEVEL=4 && export OMP_PROC_BIND=spread;
${E3SM_SRC}/components/eamxx/scripts/test-all-eamxx -m ${mach} -t dbg --config-only -w ${TEST_ROOT}
cd ${TEST_PATH}
make -j128
./zm_tests --rng-seed 23568 --args -g -b ${BASELINE_DIR}; ./zm_tests --args -c -b ${BASELINE_DIR}
```

This fix seems to fix the problem

```diff
diff --git a/components/eamxx/src/physics/zm/impl/zm_conv_main_impl.hpp b/components/eamxx/src/physics/zm/impl/zm_conv_main_impl.hpp
index bfbd465390..0ce77a202f 100644
--- a/components/eamxx/src/physics/zm/impl/zm_conv_main_impl.hpp
+++ b/components/eamxx/src/physics/zm/impl/zm_conv_main_impl.hpp
@@ -447,10 +447,10 @@ void Functions<S,D>::zm_conv_main(
         cld_base_mass_flux(i) = Kokkos::max(
           cld_base_mass_flux(i) - omega(i, pbl_top(i)) * ZMC::pa_to_mb, Real(0));
         // reapply limiter from above to protect against instability caused by large omega values
-        if (mflx_up_max_val > 0) {
-          cld_base_mass_flux(i) = Kokkos::min(cld_base_mass_flux(i),
-                                                   1 / (time_step * mflx_up_max_val));
-        }
+       // if (mflx_up_max_val > 0) {
+       //   cld_base_mass_flux(i) = Kokkos::min(cld_base_mass_flux(i),
+       //                                            1 / (time_step * mflx_up_max_val));
+       // }
```

## alternate GPU version that also generates baselines

```shell
salloc --nodes 1 --qos interactive --time 4:00:00 --constraint gpu --account=e3sm

mach=pm-gpu; comp=gnugpu
E3SM_SRC=/pscratch/sd/w/whannah/tmp_e3sm_src
TEST_ROOT=/pscratch/sd/w/whannah/zm_dev/tests_gpu
TEST_PATH=${TEST_ROOT}/full_debug/src/physics/zm/tests
# BASELINE_DIR=${TEST_ROOT}/baselines_gpu
BASELINE_DIR=${TEST_ROOT}/baselines_gpu_mvm

mkdir -p ${TEST_ROOT}/full_debug
mkdir -p ${BASELINE_DIR}

cd ${TEST_ROOT}/full_debug
eval $(${E3SM_SRC}/cime/CIME/Tools/get_case_env -c SMS.ne4pg2_ne4pg2.F2010-SCREAMv1.${mach}_${comp}) && export OMP_NUM_THREADS=1 && export CTEST_PARALLEL_LEVEL=4 && export OMP_PROC_BIND=spread;

${E3SM_SRC}/components/eamxx/scripts/test-all-eamxx -m ${mach} -t dbg --config-only -w ${TEST_ROOT}
cd ${TEST_PATH}
make -j4

cd ${TEST_PATH}

# Generate baselines
./zm_tests --rng-seed 12345 --args -g -b ${BASELINE_DIR}; ./zm_tests --args -c -b ${BASELINE_DIR} # 1 fail
./zm_tests --rng-seed 13579 --args -g -b ${BASELINE_DIR}; ./zm_tests --args -c -b ${BASELINE_DIR} # PASS
./zm_tests --rng-seed 24680 --args -g -b ${BASELINE_DIR}; ./zm_tests --args -c -b ${BASELINE_DIR} # 1 fail
./zm_tests --rng-seed 12457 --args -g -b ${BASELINE_DIR}; ./zm_tests --args -c -b ${BASELINE_DIR} # 1 fail
./zm_tests --rng-seed 23568 --args -g -b ${BASELINE_DIR}; ./zm_tests --args -c -b ${BASELINE_DIR} # 2 fail
./zm_tests --rng-seed 34679 --args -g -b ${BASELINE_DIR}; ./zm_tests --args -c -b ${BASELINE_DIR} # 1 fail
./zm_tests --rng-seed 13467 --args -g -b ${BASELINE_DIR}; ./zm_tests --args -c -b ${BASELINE_DIR} # 1 fail
./zm_tests --rng-seed 98765 --args -g -b ${BASELINE_DIR}; ./zm_tests --args -c -b ${BASELINE_DIR} # 1 fail
./zm_tests --rng-seed 87654 --args -g -b ${BASELINE_DIR}; ./zm_tests --args -c -b ${BASELINE_DIR} # 1 fail
./zm_tests --rng-seed 76543 --args -g -b ${BASELINE_DIR}; ./zm_tests --args -c -b ${BASELINE_DIR} # 1 fail


# Compare C++ against baselines
./zm_tests --args -c -b ${BASELINE_DIR}

```

another targeted test of "FMA contraction" - will zm_conv_evap_bfb pass?

```shell
salloc --nodes 1 --qos interactive --time 4:00:00 --constraint gpu --account=e3sm

mach=pm-gpu; comp=gnugpu
E3SM_SRC=/pscratch/sd/w/whannah/tmp_e3sm_src
TEST_ROOT=/pscratch/sd/w/whannah/zm_dev/tests_gpu_fmachk
TEST_PATH=${TEST_ROOT}/full_debug/src/physics/zm/tests
BASELINE_DIR=${TEST_ROOT}/baselines_gpu_fmachk
mkdir -p ${TEST_ROOT}/full_debug
mkdir -p ${BASELINE_DIR}
cd ${TEST_ROOT}/full_debug
eval $(${E3SM_SRC}/cime/CIME/Tools/get_case_env -c SMS.ne4pg2_ne4pg2.F2010-SCREAMv1.${mach}_${comp}) && export OMP_NUM_THREADS=1 && export CTEST_PARALLEL_LEVEL=4 && export OMP_PROC_BIND=spread;
${E3SM_SRC}/components/eamxx/scripts/test-all-eamxx -m ${mach} -t dbg --config-only -w ${TEST_ROOT} -c CMAKE_CUDA_FLAGS=--fmad=false
cd ${TEST_PATH}
make -j4
./zm_tests --rng-seed 23568 --args -g -b ${BASELINE_DIR}; ./zm_tests --args -c -b ${BASELINE_DIR} # 2 fail
```

Claude's suggestion based on result from above:

  Build the table on the host and copy it down. In `zm_opts_impl.hpp`, replace the parallel_for with:
```
  auto estbl_h = Kokkos::create_mirror_view(estbl);
  for (Int i = 0; i < plenest; ++i) { estbl_h(i) = svp_trans(ZMC::tmin + i); }
  Kokkos::deep_copy(estbl, estbl_h);
```
  svp_trans is KOKKOS_INLINE_FUNCTION, so it's callable on the host. Do the same at `zm_functions.hpp:187`.

  The prediction is falsifiable: since the CPU build already matches Fortran bit-for-bit on evap, a host-built table must already equal the Fortran table — so if this is the cause, zm_conv_evap_bfb should pass on GPU with no other change. If it still fails, the table isn't the source and I'd next dump estbl from both
  builds and cmp them to settle it directly.

  Worth noting this is also the right fix on its merits, not just a diagnostic: plenest is a few hundred entries computed once at init, there's no performance case for putting it on the device, and doing so removes a whole class of host/device non-BFB from ZM.




```shell
# CPU test w/ --rng-seed 23568
/pscratch/sd/w/whannah/tmp_e3sm_src/components/eamxx/src/physics/zm/tests/zm_conv_main_tests.cpp:93: FAILED:
  REQUIRE( d_baseline.prec[k] == Approx(d_test.prec[k]).margin(margin) )
with expansion:
  0.0000224953 == Approx( 0.0000224695 )

# GPU test w/ --rng-seed 23568
-------------------------------------------------------------------------------
zm_conv_main_bfb
-------------------------------------------------------------------------------
/pscratch/sd/w/whannah/tmp_e3sm_src/components/eamxx/src/physics/zm/tests/zm_conv_main_tests.cpp:166
...............................................................................

/pscratch/sd/w/whannah/tmp_e3sm_src/components/eamxx/src/physics/zm/tests/zm_conv_main_tests.cpp:93: FAILED:
  REQUIRE( d_baseline.prec[k] == Approx(d_test.prec[k]).margin(margin) )
with expansion:
  0.0000224953 == Approx( 0.0000224695 )

 For test zm_conv_evap_bfb, using stored seed: 23568
-------------------------------------------------------------------------------
zm_conv_evap_bfb
-------------------------------------------------------------------------------
/pscratch/sd/w/whannah/tmp_e3sm_src/components/eamxx/src/physics/zm/tests/zm_conv_evap_tests.cpp:114
...............................................................................

/pscratch/sd/w/whannah/tmp_e3sm_src/components/eamxx/src/physics/zm/tests/zm_conv_evap_tests.cpp:81: FAILED:
  REQUIRE( d_baseline.tend_s_snwevmlt[k] == d_test.tend_s_snwevmlt[k] )
with expansion:
  -0.0035715274 == -0.0035715274
```

--------------------------------------------------------------------------------
# Running CPU case in interactive session

```shell
salloc --nodes 1 --qos interactive --time 04:00:00 --constraint cpu --account=e3sm
# salloc --nodes 8 --qos interactive --time 04:00:00 --constraint cpu --account=e3sm

# /pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/E3SM.2025-ZM-DEV-01.F2010xx-ZM.ne4pg2.NN_1.debug/bld/cmake-bld

# CASE=E3SM.2025-ZM-DEV-01a.F2010xx-ZM.ne4pg2.NT_96.zm_apply_tend_0.debug
# CASE=E3SM.2025-ZM-DEV-04.F2010xx-ZM.ne30pg2.NN_8.zm_apply_tend_1.debug
CASE=E3SM.2025-GW-DEV-00.CPU.F2010xx-ZM.ne4pg2.NN_1.debug
CASE=E3SM.2025-GW-DEV-00.CPU.F2010xx-ZM.ne4pg2.NN_1.zm_f90.debug/

# CASE_ROOT=/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/$CASE
CASE_ROOT=/pscratch/sd/w/whannah/scream_scratch/pm-cpu/$CASE

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