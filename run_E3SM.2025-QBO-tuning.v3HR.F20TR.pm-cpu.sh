#!/bin/bash -fe

# adapted from:
# /global/cfs/cdirs/e3sm/ndk/tmpdata/20250313.v3HR.F20TR-ORO-GWD.wSLtraj.tuning.ni14_p3rain20.c12-apr8.alvarez-cpu/case_scripts/run_script_provenance/my-run.v3HR.F20TR.test4.oldSL.newsnow_shape.alvarez-cpu.sh.20250417-121523

main() {

do_ftch_cde=false;do_new_case=false;do_case_cfg=false;do_case_bld=false;do_case_sub=false
clean_build=false
# --- Toggle flags for what to do ----
### do_ftch_cde=true

# do_new_case=true
# do_case_cfg=true
# do_case_bld=true
do_case_sub=true

# clean_build=true

readonly MODEL_START_TYPE="continue"  # 'initial', 'continue', 'branch', 'hybrid'

# ==================================================================================================

# fgfc => frontgfc
# tsps => tom_sponge_start

### round #1
# fgfc=5E-14 ; tsps=5
# fgfc=2E-14 ; tsps=5
# fgfc=5E-14 ; tsps=2
# fgfc=2E-14 ; tsps=2

### round #2
fgfc=2E-14 ; tsps=2
# fgfc=2E-14 ; tsps=1 # default sponge layer

# readonly CASE_NAME="E3SM.v3HR.QBO-tuning-00.F20TR.fgfc_${fgfc}.tsps_${tsps}.pm-cpu" # Initial tests
readonly CASE_NAME="E3SM.v3HR.QBO-tuning-01.F20TR.fgfc_${fgfc}.tsps_${tsps}.pm-cpu" # revert Beres defaults


# ==================================================================================================

readonly WALLTIME="8:00:00"; STOP_OPTION="nmonths"; STOP_N="12"; RESUBMIT="0"

readonly REST_OPTION="nmonths"; REST_N="6"
# ./xmlchange REST_N=1


readonly MACHINE=pm-cpu
# NOTE: The command below will return your default project on SLURM-based systems.
# If you are not using SLURM or need a different project, remove the command and set it directly
# readonly PROJECT="$(sacctmgr show user $USER format=DefaultAccount | tail -n1 | tr -d ' ')"

readonly PROJECT=m4310 # m4310 / e3sm
readonly QUEUE=regular # regular / premium

# Simulation
readonly COMPSET="F20TR"
readonly RESOLUTION="ne120pg2_r025_RRSwISC6to18E3r5"
readonly CASE_GROUP=""

# readonly CHECKOUT="c12-apr8"
# readonly BRANCH="master"
# readonly CHERRY=()
readonly DEBUG_COMPILE=false

# Run options
readonly START_DATE="1985-01-01"

# # Additional options for 'branch' and 'hybrid'
# readonly GET_REFCASE=true
# readonly RUN_REFDIR="/dvs_ro/cfs/cdirs/e3sm/terai/E3SM_restarts/20250114.v3HR.F2010-ORO-GWD.tuning.SLtransportNewTrajectoryMethod/1996-01-01-00000/"
# readonly RUN_REFCASE="20250114.v3HR.F2010-ORO-GWD.tuning.SLtransportNewTrajectoryMethod"
# readonly RUN_REFDATE="1996-01-01"

# Set paths
# readonly CODE_ROOT="/pscratch/sd/w/whannah/tmp_v3HR_src" # master checkout @ May 21 (a987dd0305dc8c0fd55f2df12350860012462346)
readonly CODE_ROOT="/pscratch/sd/w/whannah/tmp_v3HR_src" # master checkout @ Apr 29 (d633bd7e454c3cd1c48f92a1d4c9a5d7d57ec2e1)
readonly CASE_ROOT="$SCRATCH/e3sm_scratch/${MACHINE}/${CASE_NAME}"

# Sub-directories
readonly CASE_BUILD_DIR=${CASE_ROOT}/build
readonly CASE_ARCHIVE_DIR=${CASE_ROOT}/archive

# Production simulation
readonly CASE_SCRIPTS_DIR=${CASE_ROOT}/case_scripts
readonly CASE_RUN_DIR=${CASE_ROOT}/run
# readonly PELAYOUT="custom-240"
readonly PELAYOUT="custom-256"
readonly DO_SHORT_TERM_ARCHIVING=false

# Coupler history
readonly HIST_OPTION="nyears"
readonly HIST_N="1"

# Leave empty (unless you understand what it does)
readonly OLD_EXECUTABLE=""

# ==================================================================================================
# --- Now, do the work ---

# Make directories created by this script world-readable
umask 022

echo $'\n  case: '${CASE_NAME}$'\n'

# fetch_code      # Fetch code from Github
create_newcase  # Create case
copy_script     # Copy script into case_script directory for provenance
custom_pelayout # Custom PE layout
case_setup      # Setup
case_build      # Build
runtime_options # Configure runtime options
case_submit     # Submit

echo $'\n----- All done -----\n'
echo $'  case: '${CASE_NAME}$'\n'

}

# ==================================================================================================
# atmos namelist

user_nl() {

cat << EOF >> user_nl_eam

 cosp_lite = .true.

 empty_htapes = .true.

 avgflag_pertape = 'A','A','A','I','I','I'
 nhtfrq = 0,-24,-6,-3,-1,0
 mfilt  = 1,30,120,240,720,1

 fincl1 = 'AODALL','AODBC','AODDUST','AODPOM','AODSO4','AODSOA','AODSS','AODVIS',
          'CLDLOW','CLDMED','CLDHGH','CLDTOT',
          'CLDHGH_CAL','CLDLOW_CAL','CLDMED_CAL','CLD_MISR','CLDTOT_CAL',
          'CLMODIS','FISCCP1_COSP','FLDS','FLNS','FLNSC','FLNT','FLUT',
          'FLUTC','FSDS','FSDSC','FSNS','FSNSC','FSNT','FSNTOA','FSNTOAC','FSNTC',
          'ICEFRAC','LANDFRAC','LWCF','OCNFRAC','OMEGA','PRECC','PRECL','PRECSC','PRECSL','PS','PSL','Q',
          'QFLX','QREFHT','RELHUM','SCO','SHFLX','SOLIN','SWCF','T','TAUX','TAUY','TCO',
          'TGCLDLWP','TMQ','TREFHT','TREFMNAV','TREFMXAV','TS','U','U10','V','Z3',
          'dst_a1DDF','dst_a3DDF','dst_c1DDF','dst_c3DDF','dst_a1SFWET','dst_a3SFWET','dst_c1SFWET','dst_c3SFWET',
          'O3','LHFLX',
          'O3_2DTDA_trop','O3_2DTDB_trop','O3_2DTDD_trop','O3_2DTDE_trop','O3_2DTDI_trop','O3_2DTDL_trop',
          'O3_2DTDN_trop','O3_2DTDO_trop','O3_2DTDS_trop','O3_2DTDU_trop','O3_2DTRE_trop','O3_2DTRI_trop',
          'O3_SRF','NO_2DTDS','NO_TDLgt','NO2_2DTDD','NO2_2DTDS','NO2_TDAcf','CO_SRF','TROPE3D_P','TROP_P',
          'CDNUMC','SFDMS','so4_a1_sfgaex1','so4_a2_sfgaex1','so4_a3_sfgaex1','so4_a5_sfgaex1','soa_a1_sfgaex1',
          'soa_a2_sfgaex1','soa_a3_sfgaex1','GS_soa_a1','GS_soa_a2','GS_soa_a3','AQSO4_H2O2','AQSO4_O3',
          'SFSO2','SO2_CLXF','SO2','DF_SO2','AQ_SO2','GS_SO2','WD_SO2','ABURDENSO4_STR','ABURDENSO4_TRO',
          'ABURDENSO4','ABURDENBC','ABURDENDUST','ABURDENMOM','ABURDENPOM','ABURDENSEASALT',
          'ABURDENSOA','AODSO4_STR','AODSO4_TRO',
          'EXTINCT','AODABS','AODABSBC','CLDICE','CLDLIQ','CLD_CAL_TMPLIQ','CLD_CAL_TMPICE','Mass_bc_srf',
          'Mass_dst_srf','Mass_mom_srf','Mass_ncl_srf','Mass_pom_srf','Mass_so4_srf','Mass_soa_srf','Mass_bc_850',
          'Mass_dst_850','Mass_mom_850','Mass_ncl_850','Mass_pom_850','Mass_so4_850','Mass_soa_850','Mass_bc_500',
          'Mass_dst_500','Mass_mom_500','Mass_ncl_500','Mass_pom_500','Mass_so4_500','Mass_soa_500','Mass_bc_330',
          'Mass_dst_330','Mass_mom_330','Mass_ncl_330','Mass_pom_330','Mass_so4_330','Mass_soa_330','Mass_bc_200',
          'Mass_dst_200','Mass_mom_200','Mass_ncl_200','Mass_pom_200','Mass_so4_200','Mass_soa_200',
          'O3_2DTDD','O3_2DCIP','O3_2DCIL','CO_2DTDS','CO_2DTDD','CO_2DCEP','CO_2DCEL','NO_2DTDD',
          'FLNTC','SAODVIS',
          'H2OLNZ',
          'dst_a1SF','dst_a3SF',
          'PHIS','CLOUD','TGCLDIWP','TGCLDCWP','AREL',
          'FSUTOA','FSUTOAC','PBLH',
          'CLDTOT_ISCCP','MEANCLDALB_ISCCP','MEANPTOP_ISCCP','CLD_CAL',
          'CLDTOT_CAL_LIQ','CLDTOT_CAL_ICE','CLDTOT_CAL_UN',
          'CLDHGH_CAL_LIQ','CLDHGH_CAL_ICE','CLDHGH_CAL_UN',
          'CLDMED_CAL_LIQ','CLDMED_CAL_ICE','CLDMED_CAL_UN',
          'CLDLOW_CAL_LIQ','CLDLOW_CAL_ICE','CLDLOW_CAL_UN',
          'CLWMODIS','CLIMODIS',
          'BUTGWSPEC','UTGWORO','UTGWSPEC'
          'Uzm','Vzm','Wzm','THzm','VTHzm','WTHzm','UVzm','UWzm','THphys','PSzm'

 fincl2 = 'PS', 'FLUT','PRECT','U200','V200','U850','V850','TCO','SCO','TREFHTMN:M','TREFHTMX:X','TREFHT','QREFHT'
 fincl3 = 'PS', 'PSL','PRECT','TUQ','TVQ','UBOT','VBOT','TREFHT','FLUT','OMEGA500','TBOT','U850','V850','U200','V200','T200','T500','Z700'
 fincl4 = 'PRECT'
 fincl5 = 'O3_SRF'
 fincl6 = 'CO_2DMSD','NO2_2DMSD','NO_2DMSD','O3_2DMSD','O3_2DMSD_trop'

 !------------------------------------------------------------------------------
 ! enable zonal mean diagnostics
 phys_grid_ctem_zm_nbas = 120
 phys_grid_ctem_za_nlat = 90
 phys_grid_ctem_nfreq = -1

 !------------------------------------------------------------------------------
 ! chemUCI settings
 history_chemdyg_summary = .true.
 history_gaschmbudget_2D = .false.
 history_gaschmbudget_2D_levels = .false.
 history_gaschmbudget_num = 6 !! no impact if  history_gaschmbudget_2D = .false.

 !------------------------------------------------------------------------------
 ! MAM5 settings
 is_output_interactive_volc = .true.

 !------------------------------------------------------------------------------
 ! misc tuning parameter changes for HR

 cld_macmic_num_steps =  3

 ! gravity wave parameters perturbed
 effgw_oro = 0.25
 ! gw_convect_hcf = 2.5
 ! effgw_beres = 0.1

 ! Sea salt emissions
 seasalt_emis_scale = 0.72

 ! Raise dust emission from original
 dust_emis_fact = 9.2

 ! Turn off mass flux adjustment
 zmconv_clos_dyn_adj = .false.

 ! lightning NOx emissions
 lght_no_prd_factor = 0.31D0

 ! oro GWD - enable new schemes
 use_gw_oro=.false.
 use_od_ls=.true.
 use_od_bl=.true.
 use_od_ss=.true.
 use_od_fd=.true.
 bnd_topo='/dvs_ro/cfs/cdirs/e3sm/inputdata/atm/cam/topo/USGS-gtopo30_ne120np4pg2_x6t_forOroDrag.c20241019.nc'

 ! oro GWD - tuning parameters
 od_ls_ncleff = 2
 od_bl_ncd = 3 !(FBD)
 od_ss_sncleff = 1 !(sGWD).

 ! frontal GWD tuning
 frontgfc = ${fgfc}
 tom_sponge_start = ${tsps}

 ! Dust emission cap
 dstemislimitswitch = .true.

 ! Cloud tuning parameter changes
 nucleate_ice_subgrid = 1.40
 p3_embryonic_rain_size = 0.000020D0

EOF

# ==================================================================================================
# land namelist

cat << EOF >> user_nl_elm
 hist_dov2xy = .true.,.true.
 hist_fexcl1 ='AGWDNPP','ALTMAX_LASTYEAR','AVAIL_RETRANSP','AVAILC','BAF_CROP',
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
              'SMINP_TO_SOIL3P_L3','SMINP_TO_SOIL3P_S2','SMINP_TO_SOIL4P_S3','SMINP_vr','SOIL1_HR','SOIL1C_TO_SOIL2C','SOIL1C_vr','SOIL1N_TNDNCY_VERT_TRANS','SOIL1N_TO_SOIL2N','SOIL1N_vr',
              'SOIL1P_TNDNCY_VERT_TRANS','SOIL1P_TO_SOIL2P','SOIL1P_vr','SOIL2_HR','SOIL2C_TO_SOIL3C',
              'SOIL2C_vr','SOIL2N_TNDNCY_VERT_TRANS','SOIL2N_TO_SOIL3N','SOIL2N_vr','SOIL2P_TNDNCY_VERT_TRANS',
              'SOIL2P_TO_SOIL3P','SOIL2P_vr','SOIL3_HR','SOIL3C_TO_SOIL4C','SOIL3C_vr',
              'SOIL3N_TNDNCY_VERT_TRANS','SOIL3N_TO_SOIL4N','SOIL3N_vr','SOIL3P_TNDNCY_VERT_TRANS','SOIL3P_TO_SOIL4P',
              'SOIL3P_vr','SOIL4_HR','SOIL4C_vr','SOIL4N_TNDNCY_VERT_TRANS','SOIL4N_TO_SMINN',
              'SOIL4N_vr','SOIL4P_TNDNCY_VERT_TRANS','SOIL4P_TO_SMINP','SOIL4P_vr','SOLUTIONP_vr',
              'TCS_MONTH_BEGIN','TCS_MONTH_END','TOTCOLCH4','water_scalar','WF',
              'wlim_m','WOODC_LOSS','WTGQ'
 hist_fincl1 = 'SNOWDP','COL_FIRE_CLOSS','NPOOL','PPOOL','TOTPRODC'
 hist_mfilt = 1
 hist_nhtfrq = 0
 hist_avgflag_pertape = 'A'

 check_finidat_year_consistency = .false.
 check_finidat_fsurdat_consistency = .false.

 ! if finidat from a different period is specified
 ! check_finidat_pct_consistency   = .false.

 !--- land BGC spin-up initial conditions ---, pending
 finidat='/dvs_ro/cfs/cdirs/e3sm/inputdata/lnd/clm2/initdata_map/elmi.CNPRDCTCBCTOP.r025_RRSwISC6to18E3r5.1985.nc'
 ! finidat="/global/cfs/cdirs/e3sm/inputdata/lnd/clm2/initdata_map/elmi.CNPRDCTCBCTOP.ne120pg2_r025_RRSwISC6to18E3r5.1985.nc"
 ! finidat='/dvs_ro/cfs/cdirs/e3sm/inputdata/lnd/clm2/initdata_map/elmi.CNPRDCTCBCTOP.r025_RRSwISC6to18E3r5.1850.c20250325.nc'
 
 ! New snow grain shape for the ice-sheet warm bias
 snow_shape = 'hexagonal_plate'
EOF

}

patch_mpas_streams() {

echo

}

# ==================================================================================================
# fetch_code() {
#     if [ "${do_ftch_cde,,}" != "true" ]; then
#         echo $'\n----- Skipping fetch_code -----\n'
#         return
#     fi
#     echo $'\n----- Starting fetch_code -----\n'
#     local path=${CODE_ROOT}
#     local repo=e3sm
#     echo "Cloning $repo repository branch $BRANCH under $path"
#     if [ -d "${path}" ]; then
#         echo "ERROR: Directory already exists. Not overwriting"
#         exit 20
#     fi
#     mkdir -p ${path}
#     pushd ${path}
#     # This will put repository, with all code
#     git clone git@github.com:E3SM-Project/${repo}.git .
#     # Setup git hooks
#     rm -rf .git/hooks
#     git clone git@github.com:E3SM-Project/E3SM-Hooks.git .git/hooks
#     git config commit.template .git/hooks/commit.template
#     # Check out desired branch
#     git checkout ${BRANCH}
#     # Custom addition
#     if [ "${CHERRY}" != "" ]; then
#         echo ----- WARNING: adding git cherry-pick -----
#         for commit in "${CHERRY[@]}"
#         do
#             echo ${commit}
#             git cherry-pick ${commit}
#         done
#         echo -------------------------------------------
#     fi
#     # Bring in all submodule components
#     git submodule update --init --recursive
#     popd
# }
# ==================================================================================================
create_newcase() {
    if [ "${do_new_case,,}" != "true" ]; then
        echo $'\n----- Skipping create_newcase -----\n'
        return
    fi
    echo $'\n----- Starting create_newcase -----\n'
    if [[ ${PELAYOUT} == custom-* ]];
    then
        layout="M" # temporary placeholder for create_newcase
    else
        layout=${PELAYOUT}
    fi
        if [[ -z "$CASE_GROUP" ]]; then
                ${CODE_ROOT}/cime/scripts/create_newcase \
                        --case ${CASE_NAME} \
                        --output-root ${CASE_ROOT} --script-root ${CASE_SCRIPTS_DIR} \
                        --handle-preexisting-dirs u \
                        --compset ${COMPSET} --res ${RESOLUTION} \
                        --machine ${MACHINE} --project ${PROJECT} \
                        --walltime ${WALLTIME} --pecount ${layout}
        else
                ${CODE_ROOT}/cime/scripts/create_newcase \
                        --case ${CASE_NAME} --case-group ${CASE_GROUP} --handle-preexisting-dirs u \
                        --output-root ${CASE_ROOT} --script-root ${CASE_SCRIPTS_DIR} \
                        --compset ${COMPSET} --res ${RESOLUTION} \
                        --machine ${MACHINE} --project ${PROJECT} \
                        --walltime ${WALLTIME} --pecount ${layout}
        fi
    if [ $? != 0 ]; then
      echo $'\nNote: if create_newcase failed because sub-directory already exists:'
      echo $'  * delete old case_script sub-directory'
      echo $'  * or set do_newcase=false\n'
      exit 35
    fi
}
# ==================================================================================================
case_setup() {
    if [ "${do_case_cfg,,}" != "true" ]; then
        echo $'\n----- Skipping case_setup -----\n'
        return
    fi
    echo $'\n----- Starting case_setup -----\n'
    pushd ${CASE_SCRIPTS_DIR}
    ./xmlchange EXEROOT=${CASE_BUILD_DIR}               # Setup CIME EXE directory
    ./xmlchange RUNDIR=${CASE_RUN_DIR}                  # Setup CIME RUN directory
    ./xmlchange DOUT_S=${DO_SHORT_TERM_ARCHIVING^^}     # Short term archiving flag
    ./xmlchange DOUT_S_ROOT=${CASE_ARCHIVE_DIR}         # Short term archiving root

    # Build with COSP, except for a data atmosphere (datm)
    if [ `./xmlquery --value COMP_ATM` == "datm"  ]; then
      echo $'\nThe specified configuration uses a data atmosphere, so cannot activate COSP simulator\n'
    else
      echo $'\nConfiguring E3SM to use the COSP simulator\n'
      ./xmlchange --id CAM_CONFIG_OPTS --append --val='-cosp'
    fi
    # Extracts input_data_dir in case it is needed for user edits to the namelist later
    ./xmlchange DIN_LOC_ROOT="/dvs_ro/cfs/cdirs/e3sm/inputdata"
    ./xmlchange DIN_LOC_ROOT_CLMFORC="/dvs_ro/cfs/cdirs/e3sm/inputdata/atm/datm7"
    local input_data_dir=`./xmlquery DIN_LOC_ROOT --value`
    user_nl                 # setup custom user_nl
    ./case.setup --reset    # Finally, run CIME case.setup
    popd
}
# ==================================================================================================
custom_pelayout() {
    pushd ${CASE_SCRIPTS_DIR}
    ./xmlchange NTHRDS=1
    ./xmlchange ROOTPE=0

    # ./xmlchange MAX_MPITASKS_PER_NODE=120
    # ./xmlchange MAX_TASKS_PER_NODE=120

    # echo "Using custom 240 nodes layout with coilr strid4"

    # LOC_ATM_NTASK=28800
    # LOC_OTH_NTASK=7200
    # LOC_ALL_PSTRD=4

    # ./xmlchange ATM_NTASKS=${LOC_ATM_NTASK}
    # ./xmlchange CPL_NTASKS=${LOC_OTH_NTASK},ICE_NTASKS=${LOC_OTH_NTASK},LND_NTASKS=${LOC_OTH_NTASK},ROF_NTASKS=${LOC_OTH_NTASK},OCN_NTASKS=${LOC_OTH_NTASK}
    # ./xmlchange CPL_PSTRID=${LOC_ALL_PSTRD},ICE_PSTRID=${LOC_ALL_PSTRD},LND_PSTRID=${LOC_ALL_PSTRD},ROF_PSTRID=${LOC_ALL_PSTRD},OCN_PSTRID=${LOC_ALL_PSTRD}


    echo "Using custom 256 nodes layout"
    ./xmlchange MAX_MPITASKS_PER_NODE=120
    ./xmlchange MAX_TASKS_PER_NODE=120

    ./xmlchange ATM_NTASKS=30720
    ./xmlchange CPL_NTASKS=7680
    ./xmlchange ICE_NTASKS=7680
    ./xmlchange LND_NTASKS=7680
    ./xmlchange ROF_NTASKS=7680
    ./xmlchange OCN_NTASKS=7680

    ./xmlchange CPL_PSTRID=4
    ./xmlchange ICE_PSTRID=4
    ./xmlchange LND_PSTRID=4
    ./xmlchange ROF_PSTRID=4
    ./xmlchange OCN_PSTRID=4


    popd
}
# ==================================================================================================
case_build() {
    pushd ${CASE_SCRIPTS_DIR}
    if [ "${do_case_bld,,}" != "true" ]; then
        echo $'\n----- case_build -----\n'
        if [ "${OLD_EXECUTABLE}" == "" ]; then
            # Ues previously built executable, make sure it exists
            if [ -x ${CASE_BUILD_DIR}/e3sm.exe ]; then
                echo 'Skipping build because $do_case_bld = '${do_case_bld}
            else
                echo 'ERROR: $do_case_bld = '${do_case_bld}' but no executable exists for this case.'
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
    else
        if [ "${clean_build,,}" == "true" ]; then
            echo $'\n----- Cleaning previous build -----\n'
            ./case.build --clean-all
        fi

        echo $'\n----- Starting case_build -----\n'
        if [ "${DEBUG_COMPILE^^}" == "TRUE" ]; then
            ./xmlchange DEBUG=${DEBUG_COMPILE^^} # Turn on debug compilation option if requested
        fi

        ./case.build # Run CIME case.build
        # Some user_nl settings won't be updated to *_in files under the run directory
        # Call preview_namelists to make sure *_in and user_nl files are consistent.
         echo $'\n----- Preview namelists -----\n'
        ./preview_namelists
    fi
    popd
}
# ==================================================================================================
runtime_options() {
    echo $'\n----- Starting runtime_options -----\n'
    pushd ${CASE_SCRIPTS_DIR}

    ./xmlchange RUN_STARTDATE=${START_DATE}                     # Set simulation start date
    ./xmlchange STOP_OPTION=${STOP_OPTION,,},STOP_N=${STOP_N}   # Segment length
    ./xmlchange REST_OPTION=${REST_OPTION,,},REST_N=${REST_N}   # Restart frequency
    ./xmlchange HIST_OPTION=${HIST_OPTION,,},HIST_N=${HIST_N}   # Coupler history
    ./xmlchange BUDGETS=TRUE                                    # Coupler budgets (always on)
    # Set resubmissions
    if (( RESUBMIT > 0 )); then
        ./xmlchange RESUBMIT=${RESUBMIT}
    fi

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
    patch_mpas_streams # Patch mpas streams files
    popd
}
# ==================================================================================================
case_submit() {
    if [ "${do_case_sub,,}" != "true" ]; then
        echo $'\n----- Skipping case_submit -----\n'
        return
    fi
    echo $'\n----- Starting case_submit -----\n'
    pushd ${CASE_SCRIPTS_DIR}
    ./xmlchange CHARGE_ACCOUNT=${PROJECT},PROJECT=${PROJECT} --force
    ./xmlchange JOB_QUEUE=${QUEUE} --force
    ./case.submit
    popd
}
# ==================================================================================================
copy_script() {
    echo $'\n----- Saving run script for provenance -----\n'
    local script_provenance_dir=${CASE_SCRIPTS_DIR}/run_script_provenance
    mkdir -p ${script_provenance_dir}
    local this_script_name=$( basename -- "$0"; )
    local this_script_dir=$( dirname -- "$0"; )
    local script_provenance_name=${this_script_name}.`date +%Y%m%d-%H%M%S`
    cp -vp "${this_script_dir}/${this_script_name}" ${script_provenance_dir}/${script_provenance_name}
}
# ==================================================================================================
# Silent versions of popd and pushd
pushd() {
    command pushd "$@" > /dev/null
}
popd() {
    command popd "$@" > /dev/null
}

# Now, actually run the script
# ==================================================================================================
main
