#!/bin/bash -fe

# EAMxx template run script

main() {
#-------------------------------------------------------------------------------
do_create_newcase=false
do_case_setup=false
do_case_build=false
do_case_submit=true
#-------------------------------------------------------------------------------
readonly MACHINE="pm-gpu"
readonly CHECKOUT="260909"
readonly BRANCH="master"
readonly CHERRY=( )
readonly COMPILER="gnugpu"
readonly DEBUG_COMPILE=FALSE

readonly COMPSET="F2010xx-ZM-CICE"
readonly RESOLUTION="ne256pg2_ne256pg2"

# readonly CODE_ROOT="/pscratch/sd/t/terai/E3SM_code/master_260825/" #To change to path of own scratch
readonly CODE_ROOT="/pscratch/sd/w/whannah/E3SM_code/master_260909"
readonly PROJECT="e3sm"                                          #To change to own account

readonly TUNINGSET="splitform_TMSoff_Recipe2_updated_GWD"

readonly CASE_NAME=${RESOLUTION}.${COMPSET}.${CHECKOUT}.${TUNINGSET}

readonly CASE_ROOT="${SCRATCH}/e3sm_scratch/${MACHINE}/${CASE_NAME}"

readonly HIST_OPTION="never"
readonly HIST_N="1"

readonly MODEL_START_TYPE="initial"  # "initial", "continue", "branch", "hybrid"
readonly START_DATE="2010-01-01"     # "" for default, or explicit "0001-01-01"

readonly CASE_BUILD_DIR=${CASE_ROOT}/build
readonly CASE_ARCHIVE_DIR=${CASE_ROOT}/archive

readonly CASE_SCRIPTS_DIR=${CASE_ROOT}/case_scripts
readonly CASE_RUN_DIR=${CASE_ROOT}/run
readonly NUM_PES=128

readonly PEL_SIM=$(( 4 * NUM_PES ))
readonly PELAYOUT=${PEL_SIM}"x1"
#-------------------------------------------------------------------------------
# readonly WALLTIME="18:00:00"
# readonly STOP_OPTION="nmonths"
# readonly STOP_N="12"
# readonly RESUBMIT="4"

readonly REST_OPTION="nmonths"
readonly REST_N="3"
readonly DO_SHORT_TERM_ARCHIVING=false

readonly WALLTIME="00:30:00"
readonly STOP_OPTION="nsteps"
readonly STOP_N="12"
readonly RESUBMIT="0"

#-------------------------------------------------------------------------------
umask 022 # Make directories created by this script world-readable
githash_eamxx=`git --git-dir ${CODE_ROOT}/.git rev-parse HEAD`
create_newcase
copy_script
case_setup
case_build
runtime_options
case_submit
#-------------------------------------------------------------------------------
echo $'\n----- All done -----\n'
}

user_nl() {
    SCO="SCREAM_NP 4 SCREAM_NUM_VERTICAL_LEV 128 SCREAM_NUM_TRACERS 10 \
        SCREAM_SHOC_SMALL_KERNELS TRUE \
        SCREAM_P3_SMALL_KERNELS TRUE \
        SCREAM_ENABLE_MAM OFF"
    echo "+++ Configuring SCREAM with: ${SCO} +++"
    ./xmlchange SCREAM_CMAKE_OPTIONS="${SCO}"
}

#-------------------------------------------------------------------------------
create_newcase() {
    if [ "${do_create_newcase,,}" != "true" ]; then
        echo $'\n----- Skipping create_newcase -----\n'
        return
    fi
    echo $'\n----- Starting create_newcase -----\n'
    # Base arguments
    args=" --case ${CASE_NAME} --handle-preexisting-dirs u --walltime ${WALLTIME} \
        --output-root ${CASE_ROOT} --script-root ${CASE_SCRIPTS_DIR} \
        --compset ${COMPSET} --res ${RESOLUTION} \
        --machine ${MACHINE} --compiler ${COMPILER} --pecount ${PELAYOUT} "
    # Optional arguments
    if [ ! -z "${PROJECT}" ]; then
      args="${args} --project ${PROJECT}"
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

#-------------------------------------------------------------------------------
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
    readonly MPS_NUMBER=4 # No MPS
    ./xmlchange --file env_mach_pes.xml NTHRDS="1"
    ./xmlchange --file env_mach_pes.xml NTHRDS_LND="16"
    ./xmlchange --file env_mach_pes.xml NTHRDS_ICE="16"
    ./xmlchange PIO_NETCDF_FORMAT="64bit_data"
    ./case.setup --reset
    # Save provenance invfo
    echo "branch hash for EAMxx: $githash_eamxx" > GIT_INFO.txt
    popd
}

#-------------------------------------------------------------------------------
case_build() {
    pushd ${CASE_SCRIPTS_DIR}
    # do_case_build = false
    if [ "${do_case_build,,}" == "true" ]; then
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

#-------------------------------------------------------------------------------
runtime_options() {

    echo $'\n----- Starting runtime_options -----\n'
    pushd ${CASE_SCRIPTS_DIR}

    local input_data_dir=`./xmlquery DIN_LOC_ROOT --value`

    # Set simulation start date
    if [ ! -z "${START_DATE}" ]; then
        ./xmlchange RUN_STARTDATE=${START_DATE}
    fi

    # Set temperature cut off in dycore threshold to 180K
    # ./atmchange physics::atm_procs_list="zm,mac_aero_mic,rrtmgp,cosp"
    ./atmchange physics::atm_procs_list="zm,mac_aero_mic,gw,rrtmgp,cosp"
    ./atmchange physics::cosp::cosp_frequency_units="hours"
    ./atmchange physics::cosp::cosp_frequency=1
    # use GHG levels more appropriate for sim
    # Average from 19940101 - 20150101
    ./atmchange co2vmr=377.2e-6
    ./atmchange ch4vmr=1786.6e-9
    ./atmchange n2ovmr=318.6e-9
    ./atmchange orbital_year=-9999
    ./xmlchange CCSM_CO2_PPMV=377.2 # use CO2 the same in land model

    ./atmchange -b tom_sponge_start=15
    ./atmchange theta_advect_form=2
    ./atmchange pgrad_correction=0
    ./atmchange physics::mac_aero_mic::atm_procs_list="shoc,cld_fraction,spa,p3"
    ./atmchange spa_data_file="${input_data_dir}/atm/scream/init/spa_v3.LR.F2010.2011-2025.c_20240405.nc"

    ./atmchange spa_ccn_to_nc_factor=750.0
    ./atmchange length_fac=0.51
    ./atmchange autoconversion_prefactor=2960.0
    ./atmchange autoconversion_qc_exponent=2.42

    # initial condition files
    ./atmchange -b vertical_coordinate_filename="${input_data_dir}/atm/scream/init/vertical_coordinates_L128v4_c20260820.nc"
    ./atmchange -b initial_conditions::filename="${input_data_dir}/atm/scream/init/screami_ne256np4L128v4_ifs-20200120_20260825.nc"

    ./atmchange -b use_gw_orographic=false
    ./atmchange -b use_gw_convect=true
#-------------------------------------------------------------------------------
# Additional settings for land
cat << EOF >> user_nl_elm
  finidat='${input_data_dir}/lnd/clm2/initdata/20240305.I2010CRUELM.ne256pg2.elm.r.2020-01-20-00000.nc'
  ! Override consistency checks since we know our surface data is inconsistent
  hist_dov2xy = .true.,.true.
  hist_mfilt = 1,1
  hist_nhtfrq = 0,-24
  hist_avgflag_pertape = 'A','A'
  hist_fincl1 = 'FIRE', 'FPSN', 'QDRAI', 'QRUNOFF', 'ZWT', 'FSAT', 'H2OSOI', 'EFLX_LH_TOT',
                'QVEGT', 'QVEGE', 'FSH', 'ALBD', 'ALBI', 'TBOT', 'QBOT', 'RAIN', 'SNOW',
                'FSDS', 'FSDSND', 'FSDSNI', 'FSDSVD', 'FSDSVI', 'FLDS'
  hist_fincl2 = 'H2OSNO','SOILWATER_10CM','TG'
EOF
# Coupler settings; new surface flux scheme
cat << EOF >> user_nl_cpl
EOF
# Turn off CICE completely IO completely (yuck)
cat << EOF >> user_nl_cice
 histfreq = 'x','x','x','x','x'
 histfreq_n = 0,0,0,0,0
EOF
    ./xmlchange STOP_OPTION=${STOP_OPTION,,},STOP_N=${STOP_N}
    ./xmlchange REST_OPTION=${REST_OPTION,,},REST_N=${REST_N}
    ./xmlchange HIST_OPTION=${HIST_OPTION,,},HIST_N=${HIST_N}
    ./xmlchange BUDGETS=TRUE # Coupler budgets (always on)
    ./xmlchange RESUBMIT=${RESUBMIT}
    # Start from default of user-specified initial conditions
    if [ "${MODEL_START_TYPE,,}" == "initial" ]; then
        ./xmlchange RUN_TYPE="startup"
        ./xmlchange CONTINUE_RUN="FALSE"
    # Continue existing run
    elif [ "${MODEL_START_TYPE,,}" == "continue" ]; then
        ./xmlchange CONTINUE_RUN="TRUE"
    else
        echo 'ERROR: $MODEL_START_TYPE = '${MODEL_START_TYPE}' is unrecognized. Exiting.'
        exit 380
    fi

#-------------------------------------------------------------------------------
cat <<EOF >> 1ma_ne30pg2.yaml
averaging_type: average
fields:
  physics_pg2:
    field_names:
    # 3D fields
    - T_mid
    - qv
    - RelativeHumidity
    - qc
    - qi
    - qr
    - qm
    - nc
    - ni
    - nr
    - cldfrac_tot_for_analysis
    - cldfrac_ice_for_analysis
    - cldfrac_liq
    - omega
    - U
    - V
    - z_mid
    - p_mid
    - tke
    # 2D fields
    - SW_flux_up_at_model_top
    - SW_flux_dn_at_model_top
    - LW_flux_up_at_model_top
    - SW_clrsky_flux_up_at_model_top
    - SW_clrsky_flux_dn_at_model_top
    - LW_clrsky_flux_up_at_model_top
    - SW_flux_up_at_model_bot
    - SW_flux_dn_at_model_bot
    - LW_flux_up_at_model_bot
    - LW_flux_dn_at_model_bot
    - SW_clrsky_flux_up_at_model_bot
    - SW_clrsky_flux_dn_at_model_bot
    - LW_clrsky_flux_dn_at_model_bot
    - ShortwaveCloudForcing
    - LongwaveCloudForcing
    - ps
    - SeaLevelPressure
    - T_2m
    - qv_2m
    - surf_radiative_T
    - VapWaterPath
    - IceWaterPath
    - LiqWaterPath
    - RainWaterPath
    - ZonalVapFlux
    - MeridionalVapFlux
    - surf_evap
    - surf_sens_flux
    - surface_upward_latent_heat_flux
    - precip_liq_surf_mass_flux
    - precip_ice_surf_mass_flux
    - landfrac
    - ocnfrac
    - PotentialTemperature_at_700hPa
    - PotentialTemperature_at_850hPa
    - PotentialTemperature_at_1000hPa
    - PotentialTemperature_at_2m_above_surface
    - omega_at_500hPa
    - omega_at_700hPa
    - omega_at_850hPa
    - RelativeHumidity_at_700hPa
    - RelativeHumidity_at_1000hPa
    - RelativeHumidity_at_2m_above_surface
    - wind_speed_10m
    - z_mid_at_700hPa
    - z_mid_at_1000hPa
    - T_mid_at_850hPa
    - T_mid_at_700hPa
    # For SST advection
    - U_at_10m_above_surface
    - V_at_10m_above_surface
    # cosp
    - isccp_ctptau
    - modis_ctptau
    - misr_cthtau
    - isccp_cldtot
max_snapshots_per_file: 1
filename_prefix: 1ma_ne30pg2
horiz_remap_file: \${DIN_LOC_ROOT}/atm/scream/maps/map_ne256pg2_to_ne30pg2_traave.20240206.nc
iotype: pnetcdf
output_control:
  frequency: 1
  frequency_units: nmonths
restart:
  force_new_file: true
EOF
#-------------------------------------------------------------------------------
cat <<EOF >> 1da_ne30pg2.yaml
averaging_type: average
fields:
  physics_pg2:
    field_names:
    - ps
    - SeaLevelPressure
    - precip_total_surf_mass_flux
    - precip_liq_surf_mass_flux
    - precip_ice_surf_mass_flux
    - VapWaterPath
    - LiqWaterPath
    - IceWaterPath
    - RainWaterPath
    - T_2m
    - wind_speed_10m
    - snow_depth_land
    - SW_flux_up_at_model_top
    - SW_flux_dn_at_model_top
    - LW_flux_up_at_model_top
    - U_at_850hPa
    - U_at_200hPa
max_snapshots_per_file: 30
filename_prefix: 1da_ne30pg2
horiz_remap_file: \${DIN_LOC_ROOT}/atm/scream/maps/map_ne256pg2_to_ne30pg2_traave.20240206.nc
iotype: pnetcdf
output_control:
  frequency: 1
  frequency_units: ndays
restart:
  force_new_file: true
EOF
#-------------------------------------------------------------------------------
cat <<EOF >> 1hi.yaml
averaging_type: instant
fields:
  physics_pg2:
    field_names:
    - LW_flux_up_at_model_top
    - precip_total_surf_mass_flux
max_snapshots_per_file: 240
filename_prefix: 1hi
iotype: pnetcdf
output_control:
  frequency: 1
  frequency_units: nhours
restart:
  force_new_file: true
EOF
#-------------------------------------------------------------------------------
cat <<EOF >> 3hi.yaml
averaging_type: instant
fields:
  physics_pg2:
    field_names:
    - SeaLevelPressure
    - wind_speed_10m
    - z_mid_at_500hPa
    - z_mid_at_200hPa
    - wind_speed_at_100m_above_surface
    - ZonalVapFlux
    - MeridionalVapFlux
    - omega_at_500hPa
    - omega_at_850hPa
    - surf_sens_flux
    - surf_evap
    - surface_upward_latent_heat_flux
    - precip_liq_surf_mass_flux
    - precip_ice_surf_mass_flux
    - SW_flux_up_at_model_top
    - SW_flux_dn_at_model_top
    - LW_flux_up_at_model_top
    - SW_clrsky_flux_up_at_model_top
    - SW_clrsky_flux_dn_at_model_top
    - LW_clrsky_flux_up_at_model_top
    - LiqWaterPath
    - LiqNumberPath
    - IceWaterPath
max_snapshots_per_file: 80
filename_prefix: 3hi
iotype: pnetcdf
output_control:
  frequency: 3
  frequency_units: nhours
restart:
  force_new_file: true
EOF
#-------------------------------------------------------------------------------
    ./atmchange output_yaml_files="./1ma_ne30pg2.yaml"
    ./atmchange output_yaml_files+="./1da_ne30pg2.yaml"
    ./atmchange output_yaml_files+="./1hi.yaml"
    ./atmchange output_yaml_files+="./3hi.yaml"
    popd
}

#-------------------------------------------------------------------------------
case_submit() {
    if [ "${do_case_submit,,}" != "true" ]; then
        echo $'\n----- Skipping case_submit -----\n'
        return
    fi
    echo $'\n----- Starting case_submit -----\n'
    pushd ${CASE_SCRIPTS_DIR}
    ./case.submit -a="-t ${WALLTIME} --mail-type=ALL --mail-user=hannah6@llnl.gov"
    popd
}

#-------------------------------------------------------------------------------
copy_script() {
    echo $'\n----- Saving run script for provenance -----\n'
    local script_provenance_dir=${CASE_SCRIPTS_DIR}/run_script_provenance
    mkdir -p ${script_provenance_dir}
    local this_script_name=$( basename -- "$0"; )
    local this_script_dir=$( dirname -- "$0"; )
    local script_provenance_name=${this_script_name}.`date +%Y%m%d-%H%M%S`
    cp -vp "${this_script_dir}/${this_script_name}" ${script_provenance_dir}/${script_provenance_name}
}

#-------------------------------------------------------------------------------
# Silent versions of popd and pushd
pushd() {
    command pushd "$@" > /dev/null
}
popd() {
    command popd "$@" > /dev/null
}
#-------------------------------------------------------------------------------
main
