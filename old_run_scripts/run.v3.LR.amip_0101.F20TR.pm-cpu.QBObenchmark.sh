#!/bin/bash -fe

# E3SM Coupled Model Group run_e3sm script template.
#
# Bash coding style inspired by:
# http://kfirlavi.herokuapp.com/blog/2012/11/14/defensive-bash-programming

main() {

# For debugging, uncomment libe below
#set -x

# --- Configuration flags ----

# Machine and project
readonly MACHINE=pm-cpu
readonly PROJECT="m4310"

# Simulation
readonly COMPSET="F20TR"
readonly RESOLUTION="ne30pg2_r05_IcoswISC30E3r5"
#readonly CASE_NAME="v3.LR.amip_0101.F20TR.pm-cpu.QBObenchmark"
readonly CASE_NAME="v3.LR.amip_0101.QBObenchmark.20240725"
# If this is part of a simulation campaign, ask your group lead about using a case_group label
# otherwise, comment out
#readonly CASE_GROUP="Tutorials-2024"

# Code and compilation
readonly CHECKOUT="20240705"
readonly BRANCH="master"   # branch is 'jjbenedict/2024-scidac-benchmark' on github
readonly CHERRY=( )
readonly DEBUG_COMPILE=false

# Run options
readonly MODEL_START_TYPE="hybrid"  # 'initial', 'continue', 'branch', 'hybrid'
readonly START_DATE="1978-01-01"

# Additional options for 'branch' and 'hybrid'
readonly GET_REFCASE=TRUE
# Reference init can be placed under case directory for better provenence. Here a pre-defined one is used
#readonly RUN_REFDIR="$PSCRATCH/E3SMv3/${CASE_NAME}/init/0101-01-01-00000"
readonly RUN_REFDIR="/global/cfs/cdirs/m4310/data/sims/init_files/v3.LR.amip_0101/archive/rest/1978-01-01-00000"
readonly RUN_REFCASE="v3.LR.amip_0101"
readonly RUN_REFDATE="1978-01-01"

# Set paths
readonly CODE_ROOT="${HOME}/E3SM/E3SM_SRC0"
readonly CASE_ROOT="/pscratch/sd/j/${USER}/E3SMv3_SciDAC_20240705/${CASE_NAME}"

# Sub-directories
readonly CASE_BUILD_DIR=${CASE_ROOT}/build
readonly CASE_ARCHIVE_DIR=${CASE_ROOT}/archive

# Define type of run
#  short tests: 'XS_1x10_ndays', 'XS_2x5_ndays', 'S_1x10_ndays', 'M_1x10_ndays', 'L_1x10_ndays'
#  or 'production' for full simulation

#readonly run='L_1x10_ndays'   
#readonly run='custom-2_1x10_ndays'
#readonly run='custom-1_1x3_nhours'
#readonly run='custom-1_1x2_nsteps'
#readonly run='custom-1_1x10_ndays'
#readonly run='S_1x10_ndays'
#readonly run='S_2x5_ndays'
#readonly run='M_1x10_ndays'

readonly run='production' # 'production', 'shortTestRegQ', 'shortTestDebugQ', short-test example:  'XS_2x5_ndays'

if [[ ! "${run}" =~ "production" ]]; then
  
  echo 'Setting options for SHORT TEST ${run}...'
  
  if [[ ${run} == "shortTestRegQ" ]]; then
  
    echo 'run is: ${run}'
    readonly CASE_SCRIPTS_DIR=${CASE_ROOT}/tests/${run}/case_scripts
    readonly CASE_RUN_DIR=${CASE_ROOT}/tests/${run}/run
    readonly PELAYOUT="shortTestRegQ"
    readonly WALLTIME="02:00:00"
    readonly STOP_OPTION="nmonths"
    readonly STOP_N="1"
    readonly REST_OPTION="nmonths"
    readonly REST_N="1"
    readonly RESUBMIT="0"
    readonly DO_SHORT_TERM_ARCHIVING=false
  
  elif [[ ${run} == "shortTestDebugQ" ]]; then
  
    echo 'run is: ${run}'
    readonly CASE_SCRIPTS_DIR=${CASE_ROOT}/tests/${run}/case_scripts
    readonly CASE_RUN_DIR=${CASE_ROOT}/tests/${run}/run
    readonly PELAYOUT="shortTestDebugQ"
    readonly WALLTIME="00:30:00"
    readonly STOP_OPTION="ndays"
    readonly STOP_N="2"
    readonly REST_OPTION="nyears"
    readonly REST_N="9999"
    readonly RESUBMIT="0"
    readonly DO_SHORT_TERM_ARCHIVING=false
    
  else     # default test run setup
  
    # Short test simulations
    echo 'run is: ${run}'
    tmp=($(echo $run | tr "_" " "))
    layout=${tmp[0]}
    units=${tmp[2]}
    resubmit=$(( ${tmp[1]%%x*} -1 ))
    length=${tmp[1]##*x}

    readonly CASE_SCRIPTS_DIR=${CASE_ROOT}/tests/${run}/case_scripts
    readonly CASE_RUN_DIR=${CASE_ROOT}/tests/${run}/run
    readonly PELAYOUT=${layout}
    readonly WALLTIME="00:30:00"
    readonly STOP_OPTION=${units}
    readonly STOP_N=${length}
    readonly REST_OPTION=${STOP_OPTION}
    readonly REST_N=${STOP_N}
    readonly RESUBMIT=${resubmit}
    readonly DO_SHORT_TERM_ARCHIVING=false
  
    #readonly CASE_SCRIPTS_DIR=${CASE_ROOT}/case_scripts
    #readonly CASE_RUN_DIR=${CASE_ROOT}/run
    #readonly PELAYOUT="debug_test"
    #readonly WALLTIME="00:30:00"
    #readonly STOP_OPTION="ndays"
    #readonly STOP_N="2"
    #readonly REST_OPTION="nyears"
    #readonly REST_N="999"
    #readonly RESUBMIT="0"
    #readonly DO_SHORT_TERM_ARCHIVING=false
    
  fi

else       # production run

  echo 'run is: ${run}'
  # Wuyin's original settings:
  ## Production simulation
  #readonly CASE_SCRIPTS_DIR=${CASE_ROOT}/case_scripts
  #readonly CASE_RUN_DIR=${CASE_ROOT}/run
  #readonly PELAYOUT="S"
  #readonly WALLTIME="24:00:00"
  #readonly STOP_OPTION="nyears"
  #readonly STOP_N="2"
  #readonly REST_OPTION="nmonths"
  #readonly REST_N="3"
  #readonly RESUBMIT="0"
  #readonly DO_SHORT_TERM_ARCHIVING=false
  
  # Production simulation
  readonly CASE_SCRIPTS_DIR=${CASE_ROOT}/case_scripts
  readonly CASE_RUN_DIR=${CASE_ROOT}/run
  readonly PELAYOUT="custom-22"
  readonly WALLTIME="03:00:00"
  readonly STOP_OPTION="nyears"
  readonly STOP_N="1"
  readonly REST_OPTION="nyears"
  readonly REST_N="1"
  readonly RESUBMIT="0"
  readonly DO_SHORT_TERM_ARCHIVING=false
  
fi

# Coupler history 
readonly HIST_OPTION="nyears"
readonly HIST_N="999"

# Leave empty (unless you understand what it does)
readonly OLD_EXECUTABLE=""

# --- Toggle flags for what to do ----
do_fetch_code=false
do_create_newcase=true
do_case_setup=true
do_case_build=true      # can toggle this as needed between test and production runs
do_case_submit=false    # can toggle this as needed between test and production runs

# --- Now, do the work ---

# Make directories created by this script world-readable
umask 022

# Fetch code from Github
fetch_code

# Create case
create_newcase

# Custom PE layout
custom_pelayout

# Setup
case_setup

# Build
case_build

# Configure runtime options
runtime_options

# Copy script into case_script directory for provenance
copy_script

# Submit
case_submit

# All done
echo $'\n----- All done -----\n'

}

# =======================
# Custom user_nl settings
# =======================

user_nl() {

cat << EOF >> user_nl_eam
 
 !! COSP settings
 cosp_lite = .true.        ! Note: if not explicitly set to .false. here, will be .true. in atm_in!
 !!cosp_runall = .false.     ! Do not run every simulator, only the ones specified below...
 !!cosp_lmodis_sim = .true.
 !!cosp_lisccp_sim = .true.
 !!cosp_histfile_num = 7     ! -Should- correspond to "fincl" number (if "7", COSP output written to h6 stream)

 empty_htapes = .false.    ! We decided to write out default history fields.  Redundancies
                           !   in fields specified below will not be written twice in output file(s).

 phys_grid_ctem_zm_nbas = 120  ! Number of basis functions used for TEM
 phys_grid_ctem_za_nlat = 90   ! Number of latitude points for TEM
 phys_grid_ctem_nfreq = -1     ! Frequency of TEM diagnostic calculations (neg => hours)

 !! EAM output history file frequency and file-chunking 
 !! ================
 !! fincl         = f1,    f2,    f3,    f4,    f5,    f6,    f7,    f8,    f9,    f10
 !! hX            = h0,    h1,    h2,    h3,    h4,    h5,    h6,    h7,    h8,     h9
 nhtfrq           =  0,   -24,   -24,    -6,    -6,    -1,    -6,    -6,     -1,     0
 mfilt            =  1,    30,     5,   120,   120,   120,   120,    20,    720,     1
 avgflag_pertape  = 'A',  'A',   'A',   'I',   'I',   'A',   'A',   'I',    'I',   'I'
 !! ================

 ! h0:  Comprehensive monthly averages (note:  TROP_P is in upper block)
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
          'CLDTOT_ISCCP','MEANCLDALB_ISCCP','MEANPTOP_ISCCP','CLD_CAL',
          'CLDTOT_CAL_LIQ','CLDTOT_CAL_ICE','CLDTOT_CAL_UN',
          'CLDHGH_CAL_LIQ','CLDHGH_CAL_ICE','CLDHGH_CAL_UN',
          'CLDMED_CAL_LIQ','CLDMED_CAL_ICE','CLDMED_CAL_UN',
          'CLDLOW_CAL_LIQ','CLDLOW_CAL_ICE','CLDLOW_CAL_UN',
          'CLWMODIS','CLIMODIS',
          'AODALL','AODBC','AODDUST','AODPOM','AODSO4','AODSOA','AODSS','AODVIS','CLDLOW','CLDMED','CLDHGH','CLDTOT',
          'CLDHGH_CAL','CLDLOW_CAL','CLDMED_CAL','CLD_MISR','CLDTOT_CAL','CLMODIS','FISCCP1_COSP',
          'FLDS','FLNS','FLNSC','FLNT','FLUT','FLUTC','FSDS','FSDSC','FSNS','FSNSC','FSNT','FSNTOA','FSNTOAC','FSNTC',
          'ICEFRAC','LANDFRAC','LWCF','OCNFRAC','OMEGA','PRECC','PRECL','PRECSC','PRECSL','PS','PSL',
          'Q','QFLX','QREFHT','RELHUM','SCO','SHFLX','SOLIN','SWCF','T','TAUX','TAUY','TCO','TGCLDLWP','TMQ',
          'TREFHT','TREFMNAV','TREFMXAV','TS','U','U10','V','Z3',
          'dst_a1DDF','dst_a3DDF','dst_c1DDF','dst_c3DDF','dst_a1SFWET','dst_a3SFWET','dst_c1SFWET','dst_c3SFWET',
          'O3','LHFLX',
          'O3_2DTDA_trop','O3_2DTDB_trop','O3_2DTDD_trop','O3_2DTDE_trop','O3_2DTDI_trop','O3_2DTDL_trop',
          'O3_2DTDN_trop','O3_2DTDO_trop','O3_2DTDS_trop','O3_2DTDU_trop','O3_2DTRE_trop','O3_2DTRI_trop',
          'O3_SRF','NO_2DTDS','NO_TDLgt','NO2_2DTDD','NO2_2DTDS','NO2_TDAcf','CO_SRF','TROPE3D_P','TROP_P',
          'CDNUMC','SFDMS','so4_a1_sfgaex1','so4_a2_sfgaex1','so4_a3_sfgaex1','so4_a5_sfgaex1','soa_a1_sfgaex1',
          'soa_a2_sfgaex1','soa_a3_sfgaex1','GS_soa_a1','GS_soa_a2','GS_soa_a3','AQSO4_H2O2','AQSO4_O3',
          'SFSO2','SO2_CLXF','SO2','DF_SO2','AQ_SO2','GS_SO2','WD_SO2',
          'ABURDENSO4_STR','ABURDENSO4_TRO','ABURDENSO4','ABURDENBC','ABURDENDUST','ABURDENMOM','ABURDENPOM','ABURDENSEASALT','ABURDENSOA',
          'AODSO4_STR','AODSO4_TRO','EXTINCT','AODABS','AODABSBC',
          'CLDICE','CLDLIQ','CLD_CAL_TMPLIQ','CLD_CAL_TMPICE',
          'Mass_bc_srf','Mass_dst_srf','Mass_mom_srf','Mass_ncl_srf','Mass_pom_srf','Mass_so4_srf','Mass_soa_srf',
          'Mass_bc_850','Mass_dst_850','Mass_mom_850','Mass_ncl_850','Mass_pom_850','Mass_so4_850','Mass_soa_850',
          'Mass_bc_500','Mass_dst_500','Mass_mom_500','Mass_ncl_500','Mass_pom_500','Mass_so4_500','Mass_soa_500',
          'Mass_bc_330','Mass_dst_330','Mass_mom_330','Mass_ncl_330','Mass_pom_330','Mass_so4_330','Mass_soa_330',
          'Mass_bc_200','Mass_dst_200','Mass_mom_200','Mass_ncl_200','Mass_pom_200','Mass_so4_200','Mass_soa_200',
          'O3_2DTDD','O3_2DCIP','O3_2DCIL','CO_2DTDS','CO_2DTDD','CO_2DCEP','CO_2DCEL','NO_2DTDD','FLNTC','SAODVIS','H2OLNZ',
          'dst_a1SF','dst_a3SF','PHIS','CLOUD','TGCLDIWP','TGCLDCWP',
          'AREL','CLDTOT_ISCCP','MEANCLDALB_ISCCP','MEANPTOP_ISCCP','CLD_CAL','CLDTOT_CAL_LIQ','CLDTOT_CAL_ICE',
          'CLDTOT_CAL_UN','CLDHGH_CAL_LIQ','CLDHGH_CAL_ICE','CLDHGH_CAL_UN','CLDMED_CAL_LIQ','CLDMED_CAL_ICE',
          'CLDMED_CAL_UN','CLDLOW_CAL_LIQ','CLDLOW_CAL_ICE','CLDLOW_CAL_UN','CLWMODIS','CLIMODIS',
          'Uzm','Vzm','Wzm','THzm','VTHzm','WTHzm','UVzm','UWzm','THphys','PSzm',
          'BUTGWSPEC','UTGWSPEC','UTGWORO','BTAUE','BTAUW','U050','T100','TROP_T','TROP_Z','AREA','BUTGWSPEC','BVTGWSPEC'

 
 ! h1:  Daily averages (single-level)
 fincl2 = 'PS', 'FLUT','PRECT','U200','V200','U850','V850',
          'TCO','SCO','TREFHTMN:M','TREFHTMX:X','TREFHT','QREFHT',
          'CAPE','CLDTOT','FLNS','FLNT','FLUT','FSNS','FSNT','LHFLX','LWCF','OMEGA500','PBLH','PCONVT',
          'PRECC','PRECL','PRECZ','PS','PSL','QREFHT','RHREFHT','SHFLX','SWCF','TAUGWX','TAUGWY','TAUX',
          'TAUY','TGCLDIWP','TGCLDLWP','TMQ','TREFHT','TS','U050','U10','U200','U850','UBOT','V200','V850','VBOT','TCO','SCO'
 
 
 ! h2:  Daily averages (multi-level)
 fincl3 = 'CLDICE','CLDLIQ','CLOUD','DTCOND','OMEGA','PS','Q','QRL','QRS','T','U','V','Z3','ZMDQ','ZMDT','BUTGWSPEC'
 
 
 ! h3:  6-hour instantaneous fields for ARs (single-level)
 fincl4 = 'TTQ','TUQ','TVQ','TMQ','U850','U200','V850','V200','Z200','Z500','PSL','PS','T900','Q900','U900','V900'
 
 
 ! h4:  6-hour instantaneous fields for *direct* TEM zonal wind zonal momentum budget equations
 fincl5 = 'Uzm','Vzm','Wzm','THzm','VTHzm','WTHzm','UVzm','UWzm','THphys','PSzm'
 
 
 ! h5:  1-hour instantaneous fields for precipitation diurnal cycle
 fincl6 = 'PRECC','PRECT'
 
 
 !!!! h6:  Selected COSP outputs
 !!!fincl7 = 'CLDTOT_ISCCP','CLHMODIS','CLIMODIS','CLIMODISIC','CLLMODIS','CLMMODIS','CLTMODIS','CLTMODISIC',
 !!!         'CLWMODIS','CLWMODISIC','IWPMODIS','LWPMODIS','MEANPTOP_ISCCP','MEANTAU_ISCCP','MEANTBCLR_ISCCP',
 !!!         'MEANTB_ISCCP','PCTMODIS','TAUTLOGMODIS','TAUTMODIS','CLMODIS','FISCCP1_COSP'
  
 
 ! h6:  Directly from v3 AMIP DECK:  6-hourly averages -- looks like some fields for ARs, others maybe for MJO...?
 fincl7 = 'PS', 'PSL','PRECT','TUQ','TVQ','UBOT','VBOT','TREFHT','FLUT','OMEGA500','TBOT','U850','V850','U200','V200','T200','T500','Z700'
 
 
 ! h7:  6-hour instantaneous fields for *post-processing* TEM zonal wind zonal momentum budget equations
 fincl8 = 'OMEGA','PS','Q','T','U','V','Z3'
 
 
 ! h8:  Directly from v3 AMIP DECK:  1-hour instantaneous
 fincl9 = 'O3_SRF'
 
 
 ! h9:  Directly from v3 AMIP DECK:  Monthly instantaneous
 fincl10 = 'CO_2DMSD','NO2_2DMSD','NO_2DMSD','O3_2DMSD','O3_2DMSD_trop'


 ! -- chemUCI settings ------------------
 history_chemdyg_summary = .true.
 history_gaschmbudget_2D = .false.
 history_gaschmbudget_2D_levels = .false.
 history_gaschmbudget_num = 6 !! no impact if  history_gaschmbudget_2D = .false.

 ! -- MAM5 settings ------------------    
 is_output_interactive_volc = .true.        

EOF

cat << EOF >> user_nl_elm

 ! default landuse.timeseries file below probably was created using CMIP5 raw land data. Use the updated one.
 ! flanduse_timeseries = '\${DIN_LOC_ROOT}/lnd/clm2/surfdata_map/landuse.timeseries_0.5x0.5_hist_simyr1850-2015_c191004.nc'
 flanduse_timeseries = '\${DIN_LOC_ROOT}/lnd/clm2/surfdata_map/landuse.timeseries_0.5x0.5_hist_simyr1850-2015_c240308.nc'

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
 hist_fincl2 = 'H2OSNO', 'FSNO', 'QRUNOFF', 'QSNOMELT', 'FSNO_EFF', 'SNORDSL', 'SNOW', 'FSDS', 'FSR', 'FLDS', 'FIRE', 'FIRA'
 hist_mfilt = 1,365
 hist_nhtfrq = 0,-24
 hist_avgflag_pertape = 'A','A'

EOF

# 
cat << EOF >> user_nl_mosart
 rtmhist_fincl2 = 'RIVER_DISCHARGE_OVER_LAND_LIQ'
 rtmhist_mfilt = 1,365
 rtmhist_ndens = 2
 rtmhist_nhtfrq = 0,-24
EOF

}

# =====================================
# Customize MPAS stream files if needed
# =====================================

patch_mpas_streams() {

echo

}

# =====================================================
# Custom PE layout: custom-N where N is number of nodes
# =====================================================

custom_pelayout(){

if [[ ${PELAYOUT} == custom-* ]];
then
    echo $'\n CUSTOMIZE PROCESSOR CONFIGURATION for' ${PELAYOUT}':'
    
    # Customize - - - - - - - - - - - - - - - - -
    pushd ${CASE_SCRIPTS_DIR}
    
    # preset NTASKS for all comp to 1 (stub comps)
    ./xmlchange NTASKS=1
    
    # pm-cpu PE count recommendation from Jon Wolfe for F20TR case:
    #   From 4/22/2024 email:
    #   Jon: For ne30, I would say 5400 or 2700 tasks for all? There are some things you could
    #   do to run ice concurrently with lnd/rof, but that's rarely necessary for F-cases
    #   Me:  I noted that 2700 tasks does not fit "nicely" into Perlmutter node structure...
    #   i.e., 2700/128 = 21.09, assuming 128 tasks per node.
    #   Jon:  You could (but don't have to) round up and use 2816 tasks (22 nodes x 128 tasks/node),
    #   though this could be a little wasteful (if 2816 tasks) or weird (don't round DOWN to
    #   21 nodes!)
    ./xmlchange ATM_NTASKS=2700
    ./xmlchange CPL_NTASKS=2700
    ./xmlchange OCN_NTASKS=2700
    ./xmlchange WAV_NTASKS=-1
    ./xmlchange GLC_NTASKS=-1
    ./xmlchange ICE_NTASKS=2700
    ./xmlchange ROF_NTASKS=2700
    ./xmlchange LND_NTASKS=2700
    ./xmlchange ESP_NTASKS=1
    ./xmlchange IAC_NTASKS=1
    
    # pm-cpu PE settings per Jon -- this was for an E3SM B case on pm-cpu (short test)
    #./xmlchange ATM_NTASKS=3456
    #./xmlchange CPL_NTASKS=3456
    #./xmlchange OCN_NTASKS=3456
    #./xmlchange WAV_NTASKS=-1
    #./xmlchange GLC_NTASKS=-1
    #./xmlchange ICE_NTASKS=3456
    #./xmlchange ROF_NTASKS=3456
    #./xmlchange LND_NTASKS=3456
    #./xmlchange ESP_NTASKS=1
    #./xmlchange IAC_NTASKS=1
    
    popd

#    # Number of cores per node (machine specific)
#    if [ "${MACHINE}" == "chrysalis" ]; then
#        ncore=64
#        hthrd=1  # hyper-threading, default to non-threading
#    elif [ "${MACHINE}" == "pm-cpu" ]; then
#        ncore=128
#        hthrd=1  # including pm-cpu
#    fi
#
#    # Extract number of nodes
#    tmp=($(echo ${PELAYOUT} | tr "-" " "))
#    nnodes=${tmp[1]}
#
#    # Applicable to all custom layouts
#    pushd ${CASE_SCRIPTS_DIR}
#    ./xmlchange NTASKS=1
#    ./xmlchange NTHRDS=1
#    ./xmlchange ROOTPE=0
#    ./xmlchange MAX_MPITASKS_PER_NODE=$ncore
#    ./xmlchange MAX_TASKS_PER_NODE=$(( $ncore * $hthrd))
#
#    # Layout-specific customization
#    if [ "${nnodes}" == "104" ]; then
#
#       echo Using custom 104 nodes layout on chrysalis
#
#       ### Current defaults for L
#      ./xmlchange CPL_NTASKS=5440
#      ./xmlchange ATM_NTASKS=5440
#      ./xmlchange OCN_NTASKS=1216
#      ./xmlchange OCN_ROOTPE=5440
#
#      ./xmlchange LND_NTASKS=1088
#      ./xmlchange ROF_NTASKS=1088
#      ./xmlchange ICE_NTASKS=4352
#      ./xmlchange LND_ROOTPE=4352
#      ./xmlchange ROF_ROOTPE=4352
#
#    elif [ "${nnodes}" == "52" ]; then
#
#       echo Using custom 52 nodes layout on chrysalis
#
#      ./xmlchange CPL_NTASKS=2720
#      ./xmlchange ATM_NTASKS=2720
#      ./xmlchange OCN_NTASKS=608
#      ./xmlchange OCN_ROOTPE=2720
#
#      ./xmlchange LND_NTASKS=544
#      ./xmlchange ROF_NTASKS=544
#      ./xmlchange ICE_NTASKS=2176
#      ./xmlchange LND_ROOTPE=2176
#      ./xmlchange ROF_ROOTPE=2176
#
#    elif [ "${nnodes}" == "1" ]; then
#
#       echo Using custom 1 nodes layout with pm-cpu
#
#      ./xmlchange CPL_NTASKS=128
#      ./xmlchange ATM_NTASKS=128
#      ./xmlchange OCN_NTASKS=128
#      ./xmlchange OCN_ROOTPE=0
#
#      ./xmlchange LND_NTASKS=128
#      ./xmlchange ROF_NTASKS=128
#      ./xmlchange ICE_NTASKS=128
#      ./xmlchange LND_ROOTPE=0
#      ./xmlchange ROF_ROOTPE=0
#
#    elif [ "${nnodes}" == "2" ]; then
#
#       echo Using custom 2 nodes layout with pm-cpu
#
#      ./xmlchange CPL_NTASKS=256
#      ./xmlchange ATM_NTASKS=256
#      ./xmlchange OCN_NTASKS=256
#      ./xmlchange OCN_ROOTPE=0
#
#      ./xmlchange LND_NTASKS=256
#      ./xmlchange ROF_NTASKS=256
#      ./xmlchange ICE_NTASKS=256
#      ./xmlchange LND_ROOTPE=0
#      ./xmlchange ROF_ROOTPE=0
#
#    else
#
#       echo 'ERRROR: unsupported layout '${PELAYOUT}
#       exit 401
#
#    fi
#
#    popd

fi



if [[ ${PELAYOUT} == shortTestRegQ ]];
then
    echo $'\n CUSTOMIZE PROCESSOR CONFIGURATION for' ${PELAYOUT}':'

    # Customize - - - - - - - - - - - - - - - - -
    pushd ${CASE_SCRIPTS_DIR}
    
    # preset NTASKS for all comp to 1 (stub comps)
    ./xmlchange NTASKS=1
    
    # pm-cpu PE count recommendation from Jon Wolfe for F20TR case:
    #   From 4/22/2024 email:
    #   Jon: For ne30, I would say 5400 or 2700 tasks for all? There are some things you could
    #   do to run ice concurrently with lnd/rof, but that's rarely necessary for F-cases
    #   Me:  I noted that 2700 tasks does not fit "nicely" into Perlmutter node structure...
    #   i.e., 2700/128 = 21.09, assuming 128 tasks per node.
    #   Jon:  You could (but don't have to) round up and use 2816 tasks (22 nodes x 128 tasks/node),
    #   though this could be a little wasteful (if 2816 tasks) or weird (don't round DOWN to
    #   21 nodes!)
    ./xmlchange ATM_NTASKS=2700
    ./xmlchange CPL_NTASKS=2700
    ./xmlchange OCN_NTASKS=2700
    ./xmlchange WAV_NTASKS=-1
    ./xmlchange GLC_NTASKS=-1
    ./xmlchange ICE_NTASKS=2700
    ./xmlchange ROF_NTASKS=2700
    ./xmlchange LND_NTASKS=2700
    ./xmlchange ESP_NTASKS=1
    ./xmlchange IAC_NTASKS=1
    
    # Set job queue to debug
    ./xmlchange JOB_QUEUE=regular
    
    popd

fi



if [[ ${PELAYOUT} == shortTestDebugQ ]];
then
    echo $'\n CUSTOMIZE PROCESSOR CONFIGURATION for' ${PELAYOUT}':'

    # Customize - - - - - - - - - - - - - - - - -
    pushd ${CASE_SCRIPTS_DIR}
    
    # preset NTASKS for all comp to 1 (stub comps)
    ./xmlchange NTASKS=1
    
    # pm-cpu layout for 8 nodes (debug queue max nodes is 8, and 128 tasks per node)
    ./xmlchange ATM_NTASKS=1024
    ./xmlchange CPL_NTASKS=1024
    ./xmlchange OCN_NTASKS=1024
    ./xmlchange WAV_NTASKS=-1
    ./xmlchange GLC_NTASKS=-1
    ./xmlchange ICE_NTASKS=1024
    ./xmlchange ROF_NTASKS=1024
    ./xmlchange LND_NTASKS=1024
    ./xmlchange ESP_NTASKS=1
    ./xmlchange IAC_NTASKS=1
    
    # Set job queue to debug
    ./xmlchange JOB_QUEUE=debug
    
    popd

fi



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

    if [[ ${PELAYOUT} == custom-* ]];
    then
        layout="M" # temporary placeholder for create_newcase
    else
        layout=${PELAYOUT}

    fi

    # Base arguments
    args=" --case ${CASE_NAME} \
        --output-root ${CASE_ROOT} \
        --script-root ${CASE_SCRIPTS_DIR} \
        --handle-preexisting-dirs u \
        --compset ${COMPSET} \
        --res ${RESOLUTION} \
        --machine ${MACHINE} \
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
    ./xmlchange DOUT_S=${DO_SHORT_TERM_ARCHIVING^^}
    ./xmlchange DOUT_S_ROOT=${CASE_ARCHIVE_DIR}

    # Build with COSP, except for a data atmosphere (datm)
    if [ `./xmlquery --value COMP_ATM` == "datm"  ]; then 
      echo $'\nThe specified configuration uses a data atmosphere, so cannot activate COSP simulator\n'
    else
      echo $'\nConfiguring E3SM to use the COSP simulator\n'
      ./xmlchange --id CAM_CONFIG_OPTS --append --val='-cosp'
    fi

    # Extracts input_data_dir in case it is needed for user edits to the namelist later
    local input_data_dir=`./xmlquery DIN_LOC_ROOT --value`

    # Custom user_nl
    user_nl

    # Finally, run CIME case.setup
    ./case.setup --reset

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
        if [ "${DEBUG_COMPILE^^}" == "TRUE" ]; then
            ./xmlchange DEBUG=${DEBUG_COMPILE^^}
        fi

        # Run CIME case.build
        ./case.build

    fi

    # Some user_nl settings won't be updated to *_in files under the run directory
    # Call preview_namelists to make sure *_in and user_nl files are consistent.
    echo $'\n----- Preview namelists -----\n'
    ./preview_namelists

    popd
}

#-----------------------------------------------------
runtime_options() {

    echo $'\n----- Starting runtime_options -----\n'
    pushd ${CASE_SCRIPTS_DIR}

    # Set simulation start date
    ./xmlchange RUN_STARTDATE=${START_DATE}

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
	echo "Prepare the restart files - copy restart-point files over to ../run for the relocated case"

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


