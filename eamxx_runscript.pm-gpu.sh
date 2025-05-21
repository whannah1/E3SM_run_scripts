#!/bin/bash
#-------------------------------------------------------------------------------
export CODE_ROOT=/pscratch/sd/w/whannah/tmp_e3sm_src
export TUTORIAL_ROOT=/global/cfs/cdirs/e3sm/eamxx-tutorial-2025
export COMPSET=F2010-SCREAMv1
export RES=ne4pg2_ne4pg2
export PECOUNT=4x1
export CASE_NAME=${COMPSET}.${RES}.${PECOUNT}.tutorial.gpu
export QUEUE=debug
export WALLTIME=00:30:00
export COMPILER=gnugpu
export MACHINE=pm-gpu
#-------------------------------------------------------------------------------
# mkdir -p $SCRATCH/e3sm_scratch/EAMxx_Simulations
cd $SCRATCH/e3sm_scratch/EAMxx_Simulations
#-------------------------------------------------------------------------------
${CODE_ROOT}/cime/scripts/create_newcase  --case ${CASE_NAME} \
                                          --compset ${COMPSET} \
                                          --res ${RES} \
                                          --pecount ${PECOUNT} \
                                          --compiler ${COMPILER} \
                                          --walltime ${WALLTIME} \
                                          --queue ${QUEUE} \
                                          --machine ${MACHINE}
#-------------------------------------------------------------------------------
cd $SCRATCH/e3sm_scratch/EAMxx_Simulations/$CASE_NAME
./xmlchange STOP_N=1,STOP_OPTION=ndays #how long to run for
./xmlchange HIST_N=5,HIST_OPTION=never #how often to write cpl.hi files
./xmlchange REST_N=1,REST_OPTION=ndays
./xmlchange SCREAM_CMAKE_OPTIONS="SCREAM_NP 4 SCREAM_NUM_VERTICAL_LEV 128 SCREAM_NUM_TRACERS 10"
# Special XML change to use the tutorial reservation.  Delete if doing a run on your own
./xmlchange --subgroup case.run --append BATCH_COMMAND_FLAGS='--reservation=eamxx_tutorial'
#-------------------------------------------------------------------------------
cp ${TUTORIAL_ROOT}"/runscript/tutorial_output.yaml" .
./atmchange output_yaml_files="./tutorial_output.yaml"
./case.setup # -> create namelist_scream.xml
#-------------------------------------------------------------------------------
./case.build
#-------------------------------------------------------------------------------
./case.submit
#-------------------------------------------------------------------------------
