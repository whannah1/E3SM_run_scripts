#!/bin/bash

user=$(whoami)

if [[ $user == 'hannah6' ]]
then
  CASE_ROOT=${HOME}/E3SM/Cases
  E3SM=${HOME}/E3SM/E3SM_SRC4
  OUTPUT=${MEMBERWORK}/cli115/e3sm_scratch
fi

if [[ $user == 'yuanx' ]]
then
  CASE_ROOT=$(pwd)
  E3SM=/ccs/home/yuanx/e3sm_walter_p3
  OUTPUT=/gpfs/alpine/cli115/scratch/yuanx/ACME_SIMULATIONS
fi

COMPSET=F-MMFXX-P3
RES=ne4pg2_ne4pg2
COMPILER=gnu
MACH=summit
PROJ=cli145
PELAYOUT=42x1

CASE=E3SM.P3-TEST.${RES}.${COMPSET}.01

echo ; echo ${CASE} ; echo

${E3SM}/cime/scripts/create_newcase -case ${CASE_ROOT}/${CASE} \
-compset ${COMPSET} -res ${RES} -mach ${MACH} -compiler ${COMPILER} \
-pecount ${PELAYOUT}  -project ${PROJ} --output-root ${OUTPUT} \
--handle-preexisting-dirs r

cd ${CASE_ROOT}/$CASE

./case.setup
./case.build

# Copy P3 data
DATA_PATH=${E3SM}/components/eam/src/physics/crm/scream/data
CASE_PATH=${OUTPUT}/${CASE}/run/
cp -R ${DATA_PATH} ${CASE_PATH}

./xmlchange STOP_OPTION=nsteps, STOP_N=5, CONTINUE_RUN=FALSE
./xmlchange JOB_WALLCLOCK_TIME=00:30
./xmlchange REST_OPTION=never 
./xmlchange CHARGE_ACCOUNT=$PROJ

./case.submit

echo ; echo ${CASE} ; echo
 