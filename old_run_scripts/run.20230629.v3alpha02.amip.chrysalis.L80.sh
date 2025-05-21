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
readonly MACHINE=chrysalis
readonly PROJECT="e3sm"

# Simulation
readonly COMPSET="F20TR_chemUCI-Linozv3-mam5"
readonly RESOLUTION="ne30pg2_EC30to60E2r2"
readonly CASE_NAME="20230629.v3alpha02.amip.chrysalis.L80"

# Code and compilation
readonly CHECKOUT="20230629"
readonly BRANCH="v3atm/eam/master_MAM5_wetaero_chemdyg"  # 3b3a9531234e41c16d37022bff23fffe3125c9ba
readonly CHERRY=( )
readonly DEBUG_COMPILE=false

# Run options
readonly MODEL_START_TYPE="hybrid"  # 'initial', 'continue', 'branch', 'hybrid'
readonly START_DATE="1984-01-01"

# Additional options for 'branch' and 'hybrid'
readonly GET_REFCASE=TRUE
readonly RUN_REFDIR="/lcrc/group/e3sm/ac.mwu/archive/20220504.v2.LR.bi-grid.amip.chemMZT.chrysalis/archive/rest/1984-01-01-00000"
readonly RUN_REFCASE="20220504.v2.LR.bi-grid.amip.chemMZT.chrysalis"
readonly RUN_REFDATE="1984-01-01"

# Set paths
readonly CODE_ROOT="/lcrc/group/e3sm/${USER}/E3SMv3_dev/${CASE_NAME}/code"
readonly CASE_ROOT="/lcrc/group/e3sm/${USER}/E3SMv3_dev/${CASE_NAME}"

# Sub-directories
readonly CASE_BUILD_DIR=${CASE_ROOT}/build
readonly CASE_ARCHIVE_DIR=${CASE_ROOT}/archive

# Define type of run
#  short tests: 'S_2x5_ndays', 'M_1x10_ndays', 'M80_1x10_ndays'
#  or 'production' for full simulation

readonly run='production'
#readonly run='custom-43_1x10_ndays'
#readonly run='custom-30_1x10_ndays'
#readonly run='custom-10_2x5_ndays'

if [ "${run}" != "production" ]; then

  # Short test simulations
  tmp=($(echo $run | tr "_" " "))
  layout=${tmp[0]}
  units=${tmp[2]}
  resubmit=$(( ${tmp[1]%%x*} -1 ))
  length=${tmp[1]##*x}

  readonly CASE_SCRIPTS_DIR=${CASE_ROOT}/tests/${run}/case_scripts
  readonly CASE_RUN_DIR=${CASE_ROOT}/tests/${run}/run
  readonly PELAYOUT=${layout}
  readonly WALLTIME="2:00:00"
  readonly STOP_OPTION=${units}
  readonly STOP_N=${length}
  readonly REST_OPTION=${STOP_OPTION}
  readonly REST_N=${STOP_N}
  readonly RESUBMIT=${resubmit}
  readonly DO_SHORT_TERM_ARCHIVING=false

else

  # Production simulation
  readonly CASE_SCRIPTS_DIR=${CASE_ROOT}/case_scripts
  readonly CASE_RUN_DIR=${CASE_ROOT}/run
  readonly PELAYOUT="custom-43"
  readonly WALLTIME="48:00:00"
  readonly STOP_OPTION="nyears"
  readonly STOP_N="31"
  readonly REST_OPTION="nyears"
  readonly REST_N="1"
  readonly RESUBMIT="0"
  readonly DO_SHORT_TERM_ARCHIVING=false
fi

# Coupler history 
readonly HIST_OPTION="nyears"
readonly HIST_N="1"

# Leave empty (unless you understand what it does)
readonly OLD_EXECUTABLE=""

# --- Toggle flags for what to do ----
do_fetch_code=false
do_create_newcase=false
do_case_setup=false
do_case_build=true
do_case_submit=true

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
 cosp_lite = .true.

 empty_htapes = .true.

 avgflag_pertape = 'A','A','A','A','I','I'
 !nhtfrq = 0,-24,-6,-3,-1,0
 !mfilt  = 1,30,120,240,720,1
 nhtfrq = 0,-24
 mfilt  = 1,30

 fincl1 = 'AODALL','AODBC','AODDUST','AODPOM','AODSO4','AODSOA','AODSS','AODVIS',
          'CLDLOW','CLDMED','CLDHGH','CLDTOT',
          'CLDHGH_CAL','CLDLOW_CAL','CLDMED_CAL','CLD_MISR','CLDTOT_CAL',
          'CLMODIS','FISCCP1_COSP','FLDS','FLNS','FLNSC','FLNT','FLUT',
          'FLUTC','FSDS','FSDSC','FSNS','FSNSC','FSNT','FSNTOA','FSNTOAC',
          'FSNTC','FLNTC','FSNT_d1','FLNT_d1','FSNTC_d1','FLNTC_d1','FSNS_d1','FLNS_d1','FSNSC_d1','FLNSC_d1'
          'ICEFRAC','LANDFRAC','LWCF','OCNFRAC','OMEGA','PRECC','PRECL','PRECSC','PRECSL','PS','PSL','Q',
          'QFLX','QREFHT','RELHUM','SCO','SHFLX','SOLIN','SWCF','T','TAUX','TAUY','TCO',
          'TGCLDLWP','TMQ','TREFHT','TREFMNAV','TREFMXAV','TS','U','U10','V','Z3'
          'SFbc_a1','SFbc_a3','SFbc_a4',
          'SFdst_a1','SFdst_a3',
          'SFmom_a1','SFmom_a2','SFmom_a3','SFmom_a4',
          'SFncl_a1','SFncl_a2','SFncl_a3',
          'SFpom_a1','SFpom_a3','SFpom_a4',
          'SFso4_a1','SFso4_a2','SFso4_a3','SFso4_a5',
          'SFsoa_a1','SFsoa_a2','SFsoa_a3',
          'bc_a4_CLXF','pom_a4_CLXF','so4_a1_CLXF','so4_a2_CLXF',
          'bc_a1DDF','bc_a3DDF','bc_a4DDF','bc_c1DDF','bc_c3DDF','bc_c4DDF',
          'dst_a1DDF','dst_a3DDF','dst_c1DDF','dst_c3DDF',
          'mom_a1DDF','mom_a2DDF','mom_a3DDF','mom_a4DDF','mom_c1DDF','mom_c2DDF','mom_c3DDF','mom_c4DDF',
          'ncl_a1DDF','ncl_a2DDF','ncl_a3DDF','ncl_c1DDF','ncl_c2DDF','ncl_c3DDF'
          'pom_a1DDF','pom_a3DDF','pom_a4DDF','pom_c1DDF','pom_c3DDF','pom_c4DDF',
          'so4_a1DDF','so4_a2DDF','so4_a3DDF','so4_a5DDF','so4_c1DDF','so4_c2DDF','so4_c3DDF','so4_c5DDF',
          'soa_a1DDF','soa_a2DDF','soa_a3DDF','soa_c1DDF','soa_c2DDF','soa_c3DDF',
          'bc_a1SFWET','bc_a3SFWET','bc_a4SFWET','bc_c1SFWET','bc_c3SFWET','bc_c4SFWET',
          'dst_a1SFWET','dst_a3SFWET','dst_c1SFWET','dst_c3SFWET',
          'mom_a1SFWET','mom_a2SFWET','mom_a3SFWET','mom_a4SFWET','mom_c1SFWET','mom_c2SFWET','mom_c3SFWET','mom_c4SFWET',
          'ncl_a1SFWET','ncl_a2SFWET','ncl_a3SFWET','ncl_c1SFWET','ncl_c2SFWET','ncl_c3SFWET'
          'pom_a1SFWET','pom_a3SFWET','pom_a4SFWET','pom_c1SFWET','pom_c3SFWET','pom_c4SFWET',
          'so4_a1SFWET','so4_a2SFWET','so4_a3SFWET','so4_a5SFWET','so4_c1SFWET','so4_c2SFWET','so4_c3SFWET','so4_c5SFWET',
          'soa_a1SFWET','soa_a2SFWET','soa_a3SFWET','soa_c1SFWET','soa_c2SFWET','soa_c3SFWET',
          'Mass_bc','Mass_dst','Mass_mom','Mass_ncl','Mass_pom','Mass_so4','Mass_soa',
          'SCO','TCO','O3',
          'O3_2DTDA_trop','O3_2DTDB_trop','O3_2DTDD_trop','O3_2DTDE_trop','O3_2DTDI_trop','O3_2DTDL_trop',
          'O3_2DTDN_trop','O3_2DTDO_trop','O3_2DTDS_trop','O3_2DTDU_trop','O3_2DTRE_trop','O3_2DTRI_trop',
          'O3_SRF','NO_2DTDS','NO_TDLgt','NO2_2DTDD','NO2_2DTDS','NO2_TDAcf','CO_SRF','TROPE3D_P','TROP_P'
 fincl2 = 'PS', 'FLUT','PRECT','U200','V200','U850','V850','TCO','SCO','T'
 !fincl3 = 'PS', 'PSL','PRECT','TUQ','TVQ','UBOT','VBOT','TREFHT','FLUT','OMEGA500','TBOT','U850','V850','U200','V200','T200','T500','Z700'
 !fincl4 = 'PRECT'
 !fincl5 = 'O3_SRF'
 !fincl6 = 'CO_2DMSD','NO2_2DMSD','NO_2DMSD','O3_2DMSD','O3_2DMSD_trop'

 ncdata = '/lcrc/group/e3sm/ac.whannah/HICCUP/data/20220504.v2.LR.bi-grid.amip.chemMZT.chrysalis.eam.i.1985-01-01-00000.L80_c20230629.nc'

 ! -- process coupling namelist -- --                                                                          
 cflx_cpl_opt = 2                                                                                                 
 ! --------------------------------------                                                                      
                
                                                                                                               
 !--- Namelist flags for ZM and P3 ----                                                                        
 zmconv_microp = .true.
 zmconv_clos_dyn_adj = .true.
 zmconv_MCSP_heat_coeff = 0.3
 zmconv_tpert_fix = .true.
 zmconv_ke = 2.5e-6
 zmconv_c0_lnd = 0.0020D0   !Update: when ZMmicrophysics is used, this should have no effect
 
 sscav_tuning = .false.
 p3_wbf_coeff = 1.0
 p3_mincdnc=20.D6     ! set minimum drop # conc to 20 cc-1
 p3_nc_autocon_expon = -1.20D0
 nucleate_ice_subgrid   =  1.35                                                                                         
 !--------------------------------------  


 ! -- dust and sea salt emission tunings --                                                                    
 dust_emis_fact         =  12.8D0
 seasalt_emis_scale     =  0.55D0                                                                                               

 ! -- Ozone hole ------------------------
 linoz_psc_t = 198.0

 ! --------------------------------------                                                                      

  
 ! -- chemUCI settings ------------------   
 history_gaschmbudget_num = 6
 tropopause_e90_thrd    = 80.0e-9
 history_chemdyg_summary = .true.
 
 history_gaschmbudget_2D = .false.
 history_gaschmbudget_2D_levels = .false.

 rad_climate            = 'A:H2OLNZ:H2O', 'N:O2:O2', 'N:CO2:CO2',
         'A:O3:O3', 'A:N2OLNZ:N2O', 'A:CH4LNZ:CH4',
         'N:CFC11:CFC11', 'N:CFC12:CFC12',
         'M:mam5_mode1:\$DIN_LOC_ROOT/atm/cam/physprops/mam4_mode1_rrtmg_aeronetdust_c141106.nc',
         'M:mam5_mode2:\$DIN_LOC_ROOT/atm/cam/physprops/mam4_mode2_rrtmg_c130628.nc',
         'M:mam5_mode3:\$DIN_LOC_ROOT/atm/cam/physprops/mam4_mode3_rrtmg_aeronetdust_c141106.nc',
         'M:mam5_mode4:\$DIN_LOC_ROOT/atm/cam/physprops/mam4_mode4_rrtmg_c130628.nc',
         'M:mam5_mode5:\$DIN_LOC_ROOT/atm/cam/physprops/mam5_mode5_rrtmg_sig1.2_dgnl.40_c03072023.nc'
 rad_diag_1 = 'A:H2OLNZ:H2O','N:O2:O2','N:CO2:CO2','A:O3:O3','A:N2OLNZ:N2O','A:CH4LNZ:CH4','N:CFC11:CFC11','N:CFC12:CFC12'

 !will be used when new linoz v2/v3 vertical interpolation and IO setup are used
 !linoz_data_file = 'linv3_1849-2101_CMIP6_Hist_SSP370_10deg_58km_c20230430.nc'
 !linoz_data_path = '\$DIN_LOC_ROOT/atm/cam/chem/trop_mozart/ub' !on chrysalis
                                                                  
                                                                                                               
 ! --------------------------------------    

 ! -- VBS SOA settings ------------------                                                                      
 tracer_cnst_cycle_yr           = 1995
 tracer_cnst_datapath           = '\$DIN_LOC_ROOT/atm/cam/chem/methane/'
 tracer_cnst_file               = 'ch4_oxid_1.9x2.5_L26_1990-1999clim.c090804.nc'
 tracer_cnst_filelist           = ''
 tracer_cnst_specifier          = 'CH4', 'prsd_O3:O3', 'prsd_NO3:NO3', 'prsd_OH:OH'
 tracer_cnst_type               = 'CYCLICAL' 
 
 drydep_list = 'O3','H2O2','CH2O','CH3OOH','NO','NO2','HNO3','HO2NO2','PAN','CO','CH3COCH3','C2H5OOH','CH3CHO','H2SO4','SO2','NO3','N2O5'

 gas_wetdep_list                = 'C2H5OOH','CH2O','CH3CHO','CH3OOH','H2O2','H2SO4','HNO3','HO2NO2','SO2','SOAG0','SOAG15','SOAG24','SOAG35','SOAG34','SOAG33','SOAG32','SOAG31'
 gas_wetdep_method              = 'NEU'
 
 ext_frc_specifier              = 'NO2    -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/chem_gases/2degrees/emissions-cmip6_NO2_aircraft_vertical_1750-2015_1.9x2.5_c20170608.nc',
         'SO2    -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/DECK_ne30/cmip6_mam4_so2_elev_1850-2014_c180205_kzm_1850_2014_volcano.nc',
         'SOAG0  -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/DECK_ne30/emissions-cmip6_e3sm_SOAG0_elev_1850-2014_1.9x2.5_c20230201.nc',
         'bc_a4  -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/DECK_ne30/cmip6_mam4_bc_a4_elev_1850-2014_c180205.nc',
         'num_a1 -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/DECK_ne30/cmip6_mam4_num_a1_elev_1850-2014_c180205.nc',
         'num_a2 -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/DECK_ne30/cmip6_mam4_num_a2_elev_1850-2014_c180205.nc',
         'num_a4 -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/DECK_ne30/cmip6_mam4_num_a4_elev_1850-2014_c180205.nc',
         'pom_a4 -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/DECK_ne30/cmip6_mam4_pom_a4_elev_1850-2014_c180205.nc',
         'so4_a1 -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/DECK_ne30/cmip6_mam4_so4_a1_elev_1850-2014_c180205.nc',
         'so4_a2 -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/DECK_ne30/cmip6_mam4_so4_a2_elev_1850-2014_c180205.nc' 
 ext_frc_type           = 'INTERP_MISSING_MONTHS'
 srf_emis_specifier             = 'C2H4     -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/chem_gases/2degrees/emissions-cmip6_e3sm_C2H4_surface_1850-2014_1.9x2.5_c20210323.nc', 
         'C2H6     -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/chem_gases/2degrees/emissions-cmip6_e3sm_C2H6_surface_1850-2014_1.9x2.5_c20210323.nc', 
         'C3H8     -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/chem_gases/2degrees/emissions-cmip6_e3sm_C3H8_surface_1850-2014_1.9x2.5_c20210323.nc',
         'CH2O     -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/chem_gases/2degrees/emissions-cmip6_e3sm_CH2O_surface_1850-2014_1.9x2.5_c20210323.nc',
         'CH3CHO   -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/chem_gases/2degrees/emissions-cmip6_e3sm_CH3CHO_surface_1850-2014_1.9x2.5_c20210323.nc',
         'CH3COCH3 -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/chem_gases/2degrees/emissions-cmip6_e3sm_CH3COCH3_surface_1850-2014_1.9x2.5_c20210323.nc',
         'CO       -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/chem_gases/2degrees/emissions-cmip6_e3sm_CO_surface_1850-2014_1.9x2.5_c20210323.nc',       
         'ISOP     -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/chem_gases/2degrees/emissions-cmip6_e3sm_ISOP_surface_1850-2014_1.9x2.5_c20210323.nc',
         'ISOP_VBS -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/chem_gases/2degrees/emissions-cmip6_e3sm_ISOP_surface_1850-2014_1.9x2.5_c20210323.nc',
         'C10H16   -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/chem_gases/2degrees/emissions-cmip6_e3sm_MTERP_surface_1850-2014_1.9x2.5_c20230126.nc',         
         'SOAG0    -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/DECK_ne30/emissions-cmip6_e3sm_SOAG0_surf_1850-2014_1.9x2.5_c20230201.nc',
         'NO       -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/chem_gases/2degrees/emissions-cmip6_e3sm_NO_surface_1850-2014_1.9x2.5_c20220425.nc',    
         'DMS      -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/DMSflux.1850-2100.1deg_latlon_conserv.POPmonthlyClimFromACES4BGC_c20160727.nc',
         'SO2      -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/DECK_ne30/cmip6_mam4_so2_surf_1850-2014_c180205.nc',
         'bc_a4    -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/DECK_ne30/cmip6_mam4_bc_a4_surf_1850-2014_c180205.nc',
         'num_a1   -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/DECK_ne30/cmip6_mam4_num_a1_surf_1850-2014_c180205.nc',
         'num_a2   -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/DECK_ne30/cmip6_mam4_num_a2_surf_1850-2014_c180205.nc',
         'num_a4   -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/DECK_ne30/cmip6_mam4_num_a4_surf_1850-2014_c180205.nc',
         'pom_a4   -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/DECK_ne30/cmip6_mam4_pom_a4_surf_1850-2014_c180205.nc',
         'so4_a1   -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/DECK_ne30/cmip6_mam4_so4_a1_surf_1850-2014_c180205.nc',
         'so4_a2   -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/DECK_ne30/cmip6_mam4_so4_a2_surf_1850-2014_c180205.nc',
         'E90      -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/chem_gases/2degrees/emissions_E90_surface_1750-2015_1.9x2.5_c20210408.nc'
 srf_emis_type          = 'INTERP_MISSING_MONTHS'
 ! --------------------------------------                                                                      
          
                                                                                                               
 ! -- MAM5 settings ------------------    
 is_output_interactive_volc = .true.                                                                     
                                                                                                               
 ! --------------------------------------   

EOF

cat << EOF >> user_nl_elm
 hist_dov2xy = .true.,.true.
 hist_fincl1 = 'SNOWDP'
 hist_fincl2 = 'H2OSNO', 'FSNO', 'QRUNOFF', 'QSNOMELT', 'FSNO_EFF', 'SNORDSL', 'SNOW', 'FSDS', 'FSR', 'FLDS', 'FIRE', 'FIRA'
 hist_mfilt = 1,365
 hist_nhtfrq = 0,-24
 hist_avgflag_pertape = 'A','A'
 check_finidat_year_consistency = .false.
 check_dynpft_consistency = .false.
 fsurdat = '${input_data_dir}/lnd/clm2/surfdata_map/surfdata_ne30pg2_simyr1850_c210402.nc'
 flanduse_timeseries = '${input_data_dir}/lnd/clm2/surfdata_map/landuse.timeseries_ne30np4.pg2_hist_simyr1850-2015_c210113.nc'
EOF

cat << EOF >> user_nl_cpl

 dust_emis_scheme = 2
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

custom_pelayout() {

if [[ ${PELAYOUT} == custom-* ]];
then
    echo $'\n CUSTOMIZE PROCESSOR CONFIGURATION:'

    # Number of cores per node (machine specific)
    if [ "${MACHINE}" == "chrysalis" ]; then
        ncore=64
    elif [ "${MACHINE}" == "compy" ]; then
        ncore=40
    else
        echo 'ERROR: MACHINE = '${MACHINE}' is not supported for custom PE layout.' 
        exit 400
    fi

    # Extract number of nodes
    tmp=($(echo ${PELAYOUT} | tr "-" " "))
    nnodes=${tmp[1]}

    # Customize
    pushd ${CASE_SCRIPTS_DIR}
    ./xmlchange NTASKS=$(( $nnodes * $ncore ))
    ./xmlchange NTHRDS=1
    ./xmlchange ROOTPE=0
    ./xmlchange MAX_MPITASKS_PER_NODE=$ncore
    ./xmlchange MAX_TASKS_PER_NODE=$ncore
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
    ${CODE_ROOT}/cime/scripts/create_newcase \
        --case ${CASE_NAME} \
        --output-root ${CASE_ROOT} \
        --script-root ${CASE_SCRIPTS_DIR} \
        --handle-preexisting-dirs u \
        --compset ${COMPSET} \
        --res ${RESOLUTION} \
        --machine ${MACHINE} \
        --project ${PROJECT} \
        --walltime ${WALLTIME} \
        --pecount ${layout}

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

    # changing chemistry mechanism
    local codepath=${CODE_ROOT}
    local usr_mech_infile="${codepath}/components/eam/chem_proc/inputs/pp_chemUCI_linozv3_mam5_vbs.in"
    echo 'Changing chemistry to :'${usr_mech_infile} 
    ./xmlchange --id CAM_CONFIG_OPTS --append --val='-microphys p3 -chem superfast_mam5_resus_mom_soag -vbs -usr_mech_infile '${usr_mech_infile}

    ./xmlchange --id CAM_CONFIG_OPTS --append --val=' -nlev 80 '

    # Custom user_nl
    user_nl

    # Finally, run CIME case.setup
    ./case.setup --reset

    popd
}

#-----------------------------------------------------
case_build() {

    pushd ${CASE_SCRIPTS_DIR}

        ./xmlchange RUN_TYPE=${MODEL_START_TYPE,,}
        ./xmlchange GET_REFCASE=${GET_REFCASE}
        ./xmlchange RUN_REFDIR=${RUN_REFDIR}
        ./xmlchange RUN_REFCASE=${RUN_REFCASE}
        ./xmlchange RUN_REFDATE=${RUN_REFDATE}
        echo 'Warning: $MODEL_START_TYPE = '${MODEL_START_TYPE} 
        echo '$RUN_REFDIR = '${RUN_REFDIR}
        echo '$RUN_REFCASE = '${RUN_REFCASE}
        echo '$RUN_REFDATE = '${START_DATE}

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

        # Increase parallelism on compute nodes
        if [ -z "${SLURMD_NODENAME}" ]
        then 
            echo $'\nCompiling on login node: GMAKE_J=8\n' 
            ./xmlchange GMAKE_J=8
        else 
            echo $'\nCompiling on compute node: GMAKE_J=64\n' 
            ./xmlchange GMAKE_J=64
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
