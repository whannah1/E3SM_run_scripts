#!/bin/bash -fe

main() {

do_fetch_code=false
do_create_newcase=true
do_case_setup=true
do_case_build=false
do_case_submit=false

module load python

readonly MACHINE="pm-gpu"
readonly CHECKOUT="20261019"
readonly BRANCH="master"   #  PR #8691, lake evap cap
readonly CHERRY=( )  #
readonly COMPILER="gnugpu"
readonly DEBUG_COMPILE=FALSE
readonly QUEUE=regular

#readonly COMPSET="1850SOI%CMIP7_EAMXX%BETA_ELM%CNPRDCTCBCPHSWFMCROP_MPASSI_MPASO_MOSART_SGLC_SWAV"  # With new land physics
#readonly COMPSET="1850SOI%CMIP7_EAMXX%BETA_ELM%CNPRDCTCBCTOP_MPASSI_MPASO_MOSART_SGLC_SWAV"    # longname for WCYCLXX1850
readonly COMPSET="WCYCLXX1850"
                                               
readonly RESOLUTION="ne256pg2_u01-oi6to18-lr6to10"

# readonly CODE_ROOT="${PSCRATCH}/codes/E3SM.20261019" 
readonly CODE_ROOT="/pscratch/sd/w/whannah/E3SM_code/master_261019"
readonly PROJECT="e3sm_g"

githash_eamxx=`git --git-dir ${CODE_ROOT}/.git rev-parse HEAD`

readonly CASE_NAME=v4dev.20261019.ne256_u01.WCYCLXX1850

# readonly CASE_ROOT="${PSCRATCH}/E3SM_testings/${CASE_NAME}"
readonly CASE_ROOT=/pscratch/sd/w/whannah/e3sm_scratch/pm-gpu/${CASE_NAME}

readonly CASE_GROUP="v4dev.ne256.wcyclxx"

# History file frequency (if using default above)
readonly HIST_OPTION="nyears"
readonly HIST_N="1"

# Run options
readonly MODEL_START_TYPE="initial"  # "initial", "continue", "branch", "hybrid"
readonly START_DATE="0001-01-01"     # "" for default, or explicit "0001-01-01"

# Additional options for 'branch' and 'hybrid'
readonly GET_REFCASE=true
readonly RUN_REFDIR="/pscratch/sd/w/wlin/E3SM_testings/20260911.ne256.WCYCLXX1850.EAMXX-BETA.hybrid-xla/init/0191-01-01-00000"
readonly RUN_REFCASE="20251107.v3.HR.piControl-Spinup"
readonly RUN_REFDATE="0191-01-01" 

readonly CASE_BUILD_DIR=${CASE_ROOT}/build
readonly CASE_ARCHIVE_DIR=${CASE_ROOT}/archive

readonly CASE_SCRIPTS_DIR=${CASE_ROOT}/case_scripts
readonly CASE_RUN_DIR=${CASE_ROOT}/run
readonly PELAYOUT="512x1" # 128 nodes 4 ppn
readonly WALLTIME="2:00:00"
readonly STOP_OPTION="ndays"
readonly STOP_N="3"
readonly REST_OPTION="ndays"
readonly REST_N="2"
readonly RESUBMIT="1"
readonly DO_SHORT_TERM_ARCHIVING=false

# Leave empty (unless you understand what it does)
readonly OLD_EXECUTABLE=""

# Make directories created by this script world-readable
umask 022

# Fetch code from Github
fetch_code

# Create case
create_newcase

# # Copy script into case_script directory for provenance
# copy_script

# Setup
case_setup

# Build
case_build

# Configure runtime options
runtime_options

# Submit
case_submit

# All done
echo $'\n----- All done -----\n'

}

# =======================
# Custom user_nl settings
# =======================

user_nl() {

    #echo "+++ Configuring SCREAM for 128 vertical levels +++"
    #./xmlchange SCREAM_CMAKE_OPTIONS="SCREAM_NP 4 SCREAM_NUM_VERTICAL_LEV 128 SCREAM_NUM_TRACERS 10"

    #SCO="SCREAM_NP 4 SCREAM_NUM_VERTICAL_LEV 128 SCREAM_NUM_TRACERS 10"
    # SCO="SCREAM_NP 4 SCREAM_NUM_VERTICAL_LEV 128 SCREAM_NUM_TRACERS 10 SCREAM_SHOC_SMALL_KERNELS TRUE SCREAM_P3_SMALL_KERNELS TRUE"
    # Vertical level now set via EAMXX_VGRID
    #
    SCO="SCREAM_NP 4 SCREAM_NUM_TRACERS 10 SCREAM_SHOC_SMALL_KERNELS TRUE SCREAM_P3_SMALL_KERNELS TRUE"

    echo "+++ Configuring SCREAM with: ${SCO}  +++"
    echo "+++ Any changes needed for the configuration option  +++"
    ./xmlchange SCREAM_CMAKE_OPTIONS="${SCO}"
}

######################################################
### Most users won't need to change anything below ###
######################################################

#-----------------------------------------------------
fetch_code() {

    if [ "${do_fetch_code,,}" != "true" ]; then
        echo $'\n----- Skipping fetch_code -----\n'
        return
    fi

    echo $'\n----- Starting fetch_code -----\n'
    local path=${CODE_ROOT}
    local repo=E3SM

    echo "Cloning $repo repository branch $BRANCH under $path"
    if [ -d "${path}" ]; then
        echo "ERROR: Directory already exists. Not overwriting"
        exit 20
    fi
    mkdir -p ${path}
    pushd ${path}

    # This will put repository, with all code
    git clone git@github.com:E3SM-Project/${repo}.git .

    # Q: DO WE NEED THIS FOR EAMXX?
    # Setup git hooks
    rm -rf .git/hooks
    git clone git@github.com:E3SM-Project/E3SM-Hooks.git .git/hooks
    git config commit.template .git/hooks/commit.template

    # Check out desired branch
    git checkout ${BRANCH}

    # Custom addition
    if [ "${CHERRY}" != "" ]; then
        echo ----- WARNING: adding git cherry-pick -----
        for commit in "${CHERRY[@]}"
        do
            echo ${commit}
            git cherry-pick ${commit}
        done
        echo -------------------------------------------
    fi

    # Bring in all submodule components
    git submodule update --init --recursive

    popd
}

#-----------------------------------------------------
create_newcase() {

    if [ "${do_create_newcase,,}" != "true" ]; then
        echo $'\n----- Skipping create_newcase -----\n'
        return
    fi

    echo $'\n----- Starting create_newcase -----\n'

    # Base arguments
    args=" --case ${CASE_NAME} \
        --output-root ${CASE_ROOT} \
        --script-root ${CASE_SCRIPTS_DIR} \
        --handle-preexisting-dirs u \
        --compset ${COMPSET} \
        --res ${RESOLUTION} \
        --machine ${MACHINE} \
        --compiler ${COMPILER} \
        --walltime ${WALLTIME} \
        --pecount ${PELAYOUT}"

    # Oprional arguments
    if [ ! -z "${PROJECT}" ]; then
      args="${args} --project ${PROJECT}"
    fi
    if [ ! -z "${CASE_GROUP}" ]; then
      args="${args} --case-group ${CASE_GROUP}"
    fi
    if [ ! -z "${QUEUE}" ]; then
      args="${args} --queue ${QUEUE}"
    fi

    ${CODE_ROOT}/cime/scripts/create_newcase ${args}

    if [ $? != 0 ]; then
      echo $'\nNote: if create_newcase failed because sub-directory already exists:'
      echo $'  * delete old case_script sub-directory'
      echo $'  * or set do_newcase=false\n'
      exit 35
    fi

}

#-----------------------------------------------------
case_setup() {

    if [ "${do_case_setup,,}" != "true" ]; then
        echo $'\n----- Skipping case_setup -----\n'
        return
    fi

    echo $'\n----- Starting case_setup -----\n'
    pushd ${CASE_SCRIPTS_DIR}

    # Setup some CIME directories
    ./xmlchange EXEROOT=${CASE_BUILD_DIR}
    ./xmlchange RUNDIR=${CASE_RUN_DIR}

    # Short term archiving
    ./xmlchange DOUT_S=${DO_SHORT_TERM_ARCHIVING}
    ./xmlchange DOUT_S_ROOT=${CASE_ARCHIVE_DIR}

    # Extracts input_data_dir in case it is needed for user edits to the namelist later
    local input_data_dir=`./xmlquery DIN_LOC_ROOT --value`

    # Custom user_nl
    user_nl

    #./xmlchange --file env_mach_pes.xml NTHRDS="1"
    ./xmlchange SAVE_TIMING=TRUE
    ./xmlchange MAX_MPITASKS_PER_NODE=64
    ./xmlchange NTASKS_ATM=512,NTASKS_CPL=-128,NTASKS_OCN=-128,NTASKS_ICE=-128,NTASKS_LND=-128,NTASKS_ROF=-128
    ./xmlchange NTASKS_WAV=1,NTASKS_GLC=1,NTASKS_ESP=1,NTASKS_IAC=1
    ./xmlchange ROOTPE_WAV=1,ROOTPE_GLC=1,ROOTPE_ESP=1,ROOTPE_IAC=1
    ./xmlchange PSTRID_ATM=16,EXCL_STRIDE_ATM=16    # number_of_CPU_cores_per_mode / number_of_GPUs
    ./xmlchange PIO_STRIDE_ATM=4
    ./xmlchange INFO_MPROF=2 # e3sm.log will show components running on each task

    #./xmlchange PIO_NETCDF_FORMAT="64bit_data"
    #./xmlchange PIO_STRIDE="2"

   # Use RASM_OPTION2, which is not yet default for u01 mesh
    ./xmlchange CPL_SEQ_OPTION="RASM_OPTION2"

    # # current default remains L128v1
    # ./xmlchange EAMXX_VGRID="L128v4"

    # Finally, run CIME case.setup
    ./case.setup --reset

    # Save provenance invfo
    echo "branch hash for EAMxx: $githash_eamxx" > GIT_INFO.txt

    popd
}

#-----------------------------------------------------
case_build() {

    pushd ${CASE_SCRIPTS_DIR}

    # do_case_build = false
    if [ "${do_case_build,,}" != "true" ]; then

        echo $'\n----- case_build -----\n'

        if [ "${OLD_EXECUTABLE}" == "" ]; then
            # Ues previously built executable, make sure it exists
            if [ -x ${CASE_BUILD_DIR}/e3sm.exe ]; then
                echo 'Skipping build because $do_case_build = '${do_case_build}
            else
                echo 'ERROR: $do_case_build = '${do_case_build}' but no executable exists for this case.'
                exit 297
            fi
        else
            # If absolute pathname exists and is executable, reuse pre-exiting executable
            if [ -x ${OLD_EXECUTABLE} ]; then
                echo 'Using $OLD_EXECUTABLE = '${OLD_EXECUTABLE}
                cp -fp ${OLD_EXECUTABLE} ${CASE_BUILD_DIR}/
            else
                echo 'ERROR: $OLD_EXECUTABLE = '$OLD_EXECUTABLE' does not exist or is not an executable file.'
                exit 297
            fi
        fi
        echo 'WARNING: Setting BUILD_COMPLETE = TRUE.  This is a little risky, but trusting the user.'
        ./xmlchange BUILD_COMPLETE=TRUE

    # do_case_build = true
    else

        echo $'\n----- Starting case_build -----\n'

        # Turn on debug compilation option if requested
        if [ "${DEBUG_COMPILE}" == "TRUE" ]; then
            ./xmlchange DEBUG=${DEBUG_COMPILE}
        fi

        # Run CIME case.build
        ./case.build

        # Some user_nl settings won't be updated to *_in files under the run directory
        # Call preview_namelists to make sure *_in and user_nl files are consistent.
        ./preview_namelists

    fi

    popd
}

#-----------------------------------------------------
patch_mpas_streams() {

echo
#echo 'Modifying MPAS streams files'
echo 'No mpas patching is needed for hybrid run, but double check the stream file'

pushd ../run

popd

}

#-----------------------------------------------------
runtime_options() {

    echo $'\n----- Starting runtime_options -----\n'
    pushd ${CASE_SCRIPTS_DIR}

    local input_data_dir=`./xmlquery DIN_LOC_ROOT --value`

    # Set simulation start date
    if [ ! -z "${START_DATE}" ]; then
        ./xmlchange RUN_STARTDATE=${START_DATE}
    fi
    # Set temperature cut off in dycore threshold to 180K
    ./atmchange vtheta_thresh=180
    ./atmquery vtheta_thresh

    # default atm initial_conditions::filename=eamxxi_ne256np4L128v4_ERA5-20190101_c20260922.nc, an Oct start also available

    # append cosp, which is not on by default.
    ./atmchange physics::atm_procs_list+="cosp"
    #
    # Set cosp default frequency
    #./atmchange physics::cosp::cosp_frequency_units="hours"
    #./atmchange physics::cosp::cosp_frequency=1
    # is there an option to set default # of sub-columns?
    # Set atmos IC file
    echo "check which initial condition is used"

    # use 1850 GHG constants: co2vmr, ch4vmr, n2ovmr and CCSM_CO2_PPMV

    #write out DAG
    #./atmchange atmosphere_dag_verbosity_level=5

    # Lower spa_ccn_to_nc_factor = 800 from 1000 (as done in atm-alone simulation)
    # Below not set default
    ./atmchange spa_ccn_to_nc_factor=800.0

cat << EOF >> user_nl_elm
!Specify a lnd IC when not using hybrid or cold start

! Use interpolated elm.i originally spun up for v3HR development
finidat='/global/cfs/cdirs/e3sm/wlin/inputdata/u01.lr6to10/CMIP7.elm.i.CNPRDCTCBCTOP.u01.oi6to18.lr6to10.1850.interpinic-mpi.nc'

! fsurdat below by default
! fsurdat='/lustre/orion/cli115/world-shared/e3sm/inputdata/lnd/clm2/surfdata_map/surfdata_u01.oi6to18.lr6to10_simyr1850_c260829.nc'

! Default: clm_params_c211124.nc. c251006 version for config with new landphys
! paramfile = '/lustre/orion/cli115/world-shared/e3sm/inputdata/lnd/clm2/paramdata/clm_params_c251006.nc'

! Turn on lake evaporation cap. See PR #8691
 lake_evap_cap_method = 'rain_snow_h2osno'

 hist_dov2xy = .true.,.true.
 hist_fexcl1 = 'AGWDNPP','ALTMAX_LASTYEAR','AVAIL_RETRANSP','AVAILC','BAF_CROP',
               'BAF_PEATF','BIOCHEM_PMIN_TO_PLANT','CH4_SURF_AERE_SAT','CH4_SURF_AERE_UNSAT','CH4_SURF_DIFF_SAT',
               'CH4_SURF_DIFF_UNSAT','CH4_SURF_EBUL_SAT','CH4_SURF_EBUL_UNSAT','CMASS_BALANCE_ERROR','cn_scalar',
               'COL_PTRUNC','CONC_CH4_SAT','CONC_CH4_UNSAT','CONC_O2_SAT','CONC_O2_UNSAT',
               'cp_scalar','CWDC_HR','CWDC_LOSS','CWDC_TO_LITR2C','CWDC_TO_LITR3C',
               'CWDC_vr','CWDN_TO_LITR2N','CWDN_TO_LITR3N','CWDN_vr','CWDP_TO_LITR2P',
               'CWDP_TO_LITR3P','CWDP_vr','DWT_CONV_CFLUX_DRIBBLED','F_CO2_SOIL','F_CO2_SOIL_vr',
               'F_DENIT_vr','F_N2O_DENIT','F_N2O_NIT','F_NIT_vr','FCH4_DFSAT',
               'FINUNDATED_LAG','FPI_P_vr','FPI_vr','FROOTC_LOSS','HR_vr',
               'LABILEP_TO_SECONDP','LABILEP_vr','LAND_UPTAKE','LEAF_MR','leaf_npimbalance',
               'LEAFC_LOSS','LEAFC_TO_LITTER','LFC2','LITR1_HR','LITR1C_TO_SOIL1C',
               'LITR1C_vr','LITR1N_TNDNCY_VERT_TRANS','LITR1N_TO_SOIL1N','LITR1N_vr','LITR1P_TNDNCY_VERT_TRANS',
               'LITR1P_TO_SOIL1P','LITR1P_vr','LITR2_HR','LITR2C_TO_SOIL2C','LITR2C_vr',
               'LITR2N_TNDNCY_VERT_TRANS','LITR2N_TO_SOIL2N','LITR2N_vr','LITR2P_TNDNCY_VERT_TRANS','LITR2P_TO_SOIL2P',
               'LITR2P_vr','LITR3_HR','LITR3C_TO_SOIL3C','LITR3C_vr','LITR3N_TNDNCY_VERT_TRANS',
               'LITR3N_TO_SOIL3N','LITR3N_vr','LITR3P_TNDNCY_VERT_TRANS','LITR3P_TO_SOIL3P','LITR3P_vr',
               'M_LITR1C_TO_LEACHING','M_LITR2C_TO_LEACHING','M_LITR3C_TO_LEACHING','M_SOIL1C_TO_LEACHING','M_SOIL2C_TO_LEACHING',
               'M_SOIL3C_TO_LEACHING','M_SOIL4C_TO_LEACHING','NDEPLOY','NEM','nlim_m',
               'o2_decomp_depth_unsat','OCCLP_vr','PDEPLOY','PLANT_CALLOC','PLANT_NDEMAND',
               'PLANT_NDEMAND_COL','PLANT_PALLOC','PLANT_PDEMAND','PLANT_PDEMAND_COL','plim_m',
               'POT_F_DENIT','POT_F_NIT','POTENTIAL_IMMOB','POTENTIAL_IMMOB_P','PRIMP_TO_LABILEP',
               'PRIMP_vr','PROD1P_LOSS','QOVER_LAG','RETRANSN_TO_NPOOL','RETRANSP_TO_PPOOL',
               'SCALARAVG_vr','SECONDP_TO_LABILEP','SECONDP_TO_OCCLP','SECONDP_vr','SMIN_NH4_vr',
               'SMIN_NO3_vr','SMINN_TO_SOIL1N_L1','SMINN_TO_SOIL2N_L2','SMINN_TO_SOIL2N_S1','SMINN_TO_SOIL3N_L3',
               'SMINN_TO_SOIL3N_S2','SMINN_TO_SOIL4N_S3','SMINP_TO_SOIL1P_L1','SMINP_TO_SOIL2P_L2','SMINP_TO_SOIL2P_S1',
               'SMINP_TO_SOIL3P_L3','SMINP_TO_SOIL3P_S2','SMINP_TO_SOIL4P_S3','SMINP_vr','SOIL1_HR',
               'SOIL1C_TO_SOIL2C','SOIL1C_vr','SOIL1N_TNDNCY_VERT_TRANS','SOIL1N_TO_SOIL2N','SOIL1N_vr',
               'SOIL1P_TNDNCY_VERT_TRANS','SOIL1P_TO_SOIL2P','SOIL1P_vr','SOIL2_HR','SOIL2C_TO_SOIL3C',
               'SOIL2C_vr','SOIL2N_TNDNCY_VERT_TRANS','SOIL2N_TO_SOIL3N','SOIL2N_vr','SOIL2P_TNDNCY_VERT_TRANS',
               'SOIL2P_TO_SOIL3P','SOIL2P_vr','SOIL3_HR','SOIL3C_TO_SOIL4C','SOIL3C_vr',
               'SOIL3N_TNDNCY_VERT_TRANS','SOIL3N_TO_SOIL4N','SOIL3N_vr','SOIL3P_TNDNCY_VERT_TRANS','SOIL3P_TO_SOIL4P',
               'SOIL3P_vr','SOIL4_HR','SOIL4C_vr','SOIL4N_TNDNCY_VERT_TRANS','SOIL4N_TO_SMINN',
               'SOIL4N_vr','SOIL4P_TNDNCY_VERT_TRANS','SOIL4P_TO_SMINP','SOIL4P_vr','SOLUTIONP_vr',
               'TCS_MONTH_BEGIN','TCS_MONTH_END','TOTCOLCH4','water_scalar','WF',
               'wlim_m','WOODC_LOSS','WTGQ'
 hist_fincl1 = 'SNOWDP','COL_FIRE_CLOSS','NPOOL','PPOOL','TOTPRODC'
 hist_fincl2 = 'H2OSNO', 'FSNO', 'QRUNOFF', 'QSNOMELT', 'FSNO_EFF', 'SNORDSL', 'SNOW', 'FSDS', 'FSR', 'FLDS', 'FIRE', 'FIRA'
 hist_mfilt = 1,30
 hist_nhtfrq = 0,-24
 hist_avgflag_pertape = 'A','A'

!do_budgets = .true.
!budget_inst  = 1

EOF

cat << EOF >> user_nl_mosart
 rtmhist_fincl2 = 'RIVER_DISCHARGE_OVER_LAND_LIQ','RIVER_DISCHARGE_TO_OCEAN_LIQ','DIRECT_DISCHARGE_TO_OCEAN_LIQ'
 rtmhist_mfilt = 1,1
 rtmhist_ndens = 2
 rtmhist_nhtfrq = 0, 1
 rtmhist_ndens = 2

! default appears to be US_reservoir_8th_NLDAS3_c20161220_updated_20170314.nc
paraFile = '/global/cfs/cdirs/e3sm/inputdata/rof/mosart/global_reservoir_u01.oi6to18.lr6to10_20260920_r05radius.nc'

! Default is MOSART_u01-oi6to18-lr6to10_20260811.nc, need to use the updated one
frivinp_rtm = '/global/cfs/cdirs/e3sm/inputdata/rof/mosart/MOSART_u01-oi6to18-lr6to10_20260925.nc'

!inundflag = .true.
EOF

cat << EOF >> user_nl_cpl
nlmaps_atm2srf_conserve = .true.
nlmaps_exclude_fields = "", "", "", ""
EOF

# 6min->5min OCN time-step
cat << EOF >> user_nl_mpaso
config_dt='00:05:00'
config_cvmix_background_scheme = 'latitude-dependent'
config_cvmix_background_diffusion = 3.0e-5
config_cvmix_background_diffusion_max_latitude = -50
config_cvmix_kpp_langmuir_mixing_opt = 'NONE'
config_cvmix_kpp_langmuir_entrainment_opt = 'NONE'

! if needed for stability, reduce from 5s
! config_btr_dt = '0000_00:00:05'
EOF

cat << EOF >> user_nl_mpassi
config_elastic_subcycle_number = 240

! reduce dynamics_subcycle to 1 from 2 can reduce ICE_RUN by nearly 50%
config_dynamics_subcycle_number = 1

EOF

    ./xmlchange OCN_NCPL=144 # 30min->10min coupling

    # Segment length
    ./xmlchange STOP_OPTION=${STOP_OPTION,,},STOP_N=${STOP_N}

    # Restart frequency
    ./xmlchange REST_OPTION=${REST_OPTION,,},REST_N=${REST_N}

    # Coupler history
    ./xmlchange HIST_OPTION=${HIST_OPTION,,},HIST_N=${HIST_N}

    # Coupler budgets (always on)
    ./xmlchange BUDGETS=TRUE

    # Set resubmissions
    if (( RESUBMIT > 0 )); then
        ./xmlchange RESUBMIT=${RESUBMIT}
    fi

    # Run type
    # Start from default of user-specified initial conditions
    if [ "${MODEL_START_TYPE,,}" == "initial" ]; then
        ./xmlchange RUN_TYPE="startup"
        ./xmlchange CONTINUE_RUN="FALSE"

    # Continue existing run
    elif [ "${MODEL_START_TYPE,,}" == "continue" ]; then
        ./xmlchange CONTINUE_RUN="TRUE"

    elif [ "${MODEL_START_TYPE,,}" == "branch" ] || [ "${MODEL_START_TYPE,,}" == "hybrid" ]; then
        ./xmlchange RUN_TYPE=${MODEL_START_TYPE,,}
        ./xmlchange GET_REFCASE=${GET_REFCASE}
        ./xmlchange RUN_REFDIR=${RUN_REFDIR}
        ./xmlchange RUN_REFCASE=${RUN_REFCASE}
        ./xmlchange RUN_REFDATE=${RUN_REFDATE}
        echo 'Warning: $MODEL_START_TYPE = '${MODEL_START_TYPE}
        echo '$RUN_REFDIR = '${RUN_REFDIR}
        echo '$RUN_REFCASE = '${RUN_REFCASE}
        echo '$RUN_REFDATE = '${START_DATE}

    else
        echo 'ERROR: $MODEL_START_TYPE = '${MODEL_START_TYPE}' is unrecognized. Exiting.'
        exit 380
    fi

    eamxx_scripts=/global/cfs/cdirs/e3sm/wlin/eamxx_scripts # adjust path here
    cp -p ${eamxx_scripts}/scream_output.ne256_coupled.1dailyAVG.yaml .
    cp -p ${eamxx_scripts}/scream_output.ne256_coupled.3hourlyAVG_ne120pg2.yaml .
    cp -p ${eamxx_scripts}/scream_output.ne256_coupled.6hourlyAVG_ne120pg2.yaml .
    cp -p ${eamxx_scripts}/scream_output.ne256_coupled.monthlyAVG_ne120pg2.yaml .

    # Disable instantaneous output
    #cp -p ${eamxx_scripts}/scream_output.ne256_coupled.timestepINST.yaml .

    ./atmchange output_yaml_files="./scream_output.ne256_coupled.1dailyAVG.yaml"
    ./atmchange output_yaml_files+="./scream_output.ne256_coupled.3hourlyAVG_ne120pg2.yaml"
    ./atmchange output_yaml_files+="./scream_output.ne256_coupled.6hourlyAVG_ne120pg2.yaml"
    ./atmchange output_yaml_files+="./scream_output.ne256_coupled.monthlyAVG_ne120pg2.yaml"

    # replace default spa_data_file -- using eamv3 based file for PI condition, use updated SPA fix file
    # Change to 1850 SPA file and SPC file
    # Current defaults are  spa_from_v3LRamip_CMIP6_2010_clim_ne30pg2_c20260928.nc, spc_from_v3LRamip_2010_clim_ne30pg2_c20260206.nc
    ./atmchange spa_data_file="/lustre/orion/cli115/world-shared/e3sm/inputdata/atm/scream/init/spa_from_v3LRamip_CMIP6_1850_clim_ne30pg2_c20261015.nc"
    ./atmchange spc_data_file="/lustre/orion/cli115/world-shared/e3sm/inputdata/atm/scream/init/spc_from_v3LRhistorical_CMIP6_1850_clim_ne30pg2_c20261015.nc"

    # Patch mpas streams files
    patch_mpas_streams

    popd
}

#-----------------------------------------------------
case_submit() {

    if [ "${do_case_submit,,}" != "true" ]; then
        echo $'\n----- Skipping case_submit -----\n'
        return
    fi

    echo $'\n----- Starting case_submit -----\n'
    pushd ${CASE_SCRIPTS_DIR}

    # Run CIME case.submit
    ./case.submit

    popd
}

#-----------------------------------------------------
copy_script() {

    echo $'\n----- Saving run script for provenance -----\n'

    local script_provenance_dir=${CASE_SCRIPTS_DIR}/run_script_provenance
    mkdir -p ${script_provenance_dir}
    local this_script_name=`basename $0`
    local script_provenance_name=${this_script_name}.`date +%Y%m%d-%H%M%S`
    cp -vp ${this_script_name} ${script_provenance_dir}/${script_provenance_name}

}

#-----------------------------------------------------
# Silent versions of popd and pushd
pushd() {
    command pushd "$@" > /dev/null
}
popd() {
    command popd "$@" > /dev/null
}

# Now, actually run the script
#-----------------------------------------------------
main
