

# OLCF Andes 

```shell
# use this claude-written script to build interpinic
cd /lustre/orion/cli115/proj-shared/hannah6/e3sm_src/components/elm/tools/interpinic
./build_andes_taos.sh

# run a dummy land spin-up case to produce a template finidat
./run_E3SM.ELM_spinup.olcf.py

```

```shell
salloc --time 24:00:00 --account=cli115 --nodes=1

# copy the ELM restart file
TMP_FILE=/lustre/orion/cli115/proj-shared/hannah6/e3sm_scratch/ELM_spinup.IERA5ELM.ne128pg2_ne128pg2.dummy.2010/run/ELM_spinup.IERA5ELM.ne128pg2_ne128pg2.dummy.2010.elm.r.0001-01-02-00000.nc
DST_FILE=/lustre/orion/cli115/world-shared/e3sm/inputdata/lnd/clm2/initdata/20260728.I2010CRUELM.ne128pg2.elm.r.2016-08-01-00000.nc

# cp ${TMP_FILE} ${DST_FILE}

# use interpinic to remap
INTERPINIC=/lustre/orion/cli115/proj-shared/hannah6/e3sm_src/components/elm/tools/interpinic/interpinic
SRC_FILE=/lustre/orion/cli115/world-shared/e3sm/inputdata/lnd/clm2/initdata/20240104.I2010CRUELM.ne256pg2.elm.r.2016-08-01-00000.nc

nohup ${INTERPINIC} -i ${SRC_FILE} -o ${DST_FILE}

exit

```

## INCITE 2026 CONUS

```shell
salloc --time 24:00:00 --account=cli115 --nodes=1 -p gpu
# micromamba activate toas_env

INTERPINIC=/lustre/orion/cli115/proj-shared/hannah6/e3sm_src/components/elm/tools/interpinic/interpinic
SRC_ROOT=/lustre/orion/cli115/world-shared/e3sm/inputdata/lnd/clm2/initdata
SRC_FILE=${SRC_ROOT}/20221218.F2010-CICE.ne30pg2_ne1024pg2.elm.r.2020-01-20-00000.nc
TMP_ROOT=/lustre/orion/cli115/proj-shared/brhillman/e3sm_scratch/
TMP_CASE=conus1024x2v1pg2_RRSwISC6to18E3r5.F2010-SCREAMv1.20260803c
TMP_FILE=${TMP_ROOT}/${TMP_CASE}/run/${TMP_CASE}.elm.r.2020-01-27-00000.nc
DST_ROOT=/lustre/orion/cli115/world-shared/e3sm/2026-INCITE-CONUS-RRM/files_init
DST_FILE=${DST_ROOT}/conus1024x2v1pg2_RRSwISC6to18E3r5.elm.r.2020-01-20-00000.nc

cp ${TMP_FILE} ${DST_FILE}

nohup ${INTERPINIC} -i ${SRC_FILE} -o ${DST_FILE}

```
