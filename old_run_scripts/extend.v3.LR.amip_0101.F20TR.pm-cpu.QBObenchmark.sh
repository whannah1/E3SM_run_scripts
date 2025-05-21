# Wuyin's method to extend an exisitng AMIP (F20TR compset) simulation beyond the standard end year of 2014
#
# * See:  https://acme-climate.atlassian.net/wiki/spaces/CM/pages/4290281655/v3.LR.amip+simulations#Run-script
# * This script must be run within the "case_scripts" (or equivalent) directory of the existing simulation
#   (the one that ended in 2014)
# * This script will add updated entries for aerosol, GHG, and SSTICE files to the bottom of a copy of the existing 
#     user_nl_eam, as well as an updated LULC file to the bottom of a copy of the exisitng user_nl_eam.  It is
#     expected that these updated entries will supersede the existing entries.  User should check that these files
#     have been updated by running ./preview_namelists, as recommended at the bottom of this script. 

# Exit script immediately if any command returns a non-zero status -- this provides a measure of safety if, e.g.,
#   any copy command fails
set -e

# Save a copy of namelist settings for the standard historical config
# Run the following command from case_scripts directory
cp -p user_nl_eam user_nl_eam.std; cp -p user_nl_elm user_nl_elm.std
cp -rp CaseDocs CaseDocs.std

# Copy user_nl_eam and user_nl_elm from /lcrc/group/e3sm2/ac.wlin/E3SMv3/AMIP/v3.LR.amip_0101/case_scripts,
# Or Using the following to append to user_nl_eam.
# Note that if done manually by copying/pasting, need to remove the back slash before $DIN_LOC_ROOT. 
cat >> user_nl_eam <<EOF
 ! -- replace historical forcings with SSP245 to extend the AMIP --

  chlorine_loading_file         = '\$DIN_LOC_ROOT/atm/cam/chem/trop_mozart/ub/Linoz_Chlorine_Loading_CMIP6_Hist_SSP245_0003-2503_c20200808.nc'
  linoz_data_file               = 'linv3_1849-2101_CMIP6_Hist_SSP245_10deg_58km_c20230705.nc'
  ext_frc_specifier             = 'NO2         -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/CMIP6_SSP245_ne30/emissions-cmip6_ssp245_e3sm_NO2_aircraft_vertical_2015-2100_1.9x2.5_c20240219.nc',
          'SO2         -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/CMIP6_SSP245_ne30/cmip6_ssp245_mam4_so2_volc_elev_2015-2100_c240331.nc',
          'SOAG0       -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/CMIP6_SSP245_ne30/emissions-cmip6_ssp245_e3sm_SOAG0_elev_2015-2100_1.9x2.5_c20240219.nc',
          'bc_a4       -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/CMIP6_SSP245_ne30/cmip6_ssp245_mam4_bc_a4_elev_2015-2100_c200716.nc',
          'num_a1      -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/CMIP6_SSP245_ne30/cmip6_ssp245_mam4_num_a1_elev_2015-2100_c200716.nc',
          'num_a2      -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/CMIP6_SSP245_ne30/cmip6_ssp245_mam4_num_a2_elev_2015-2100_c200716.nc',
          'num_a4      -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/CMIP6_SSP245_ne30/cmip6_ssp245_mam4_num_a4_elev_2015-2100_c200716.nc',
          'pom_a4      -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/CMIP6_SSP245_ne30/cmip6_ssp245_mam4_pom_a4_elev_2015-2100_c200716.nc',
          'so4_a1      -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/CMIP6_SSP245_ne30/cmip6_ssp245_mam4_so4_a1_elev_2015-2100_c200716.nc',
          'so4_a2      -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/CMIP6_SSP245_ne30/cmip6_ssp245_mam4_so4_a2_elev_2015-2100_c200716.nc'
  
  srf_emis_specifier            = 'C10H16 -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/CMIP6_SSP245_ne30/emissions-cmip6_ssp245_e3sm_MTERP_surface_2015-2100_1.9x2.5_c20240219.nc',
          'C2H4      -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/CMIP6_SSP245_ne30/emissions-cmip6_ssp245_e3sm_C2H4_surface_2015-2100_1.9x2.5_c20240219.nc',
          'C2H6      -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/CMIP6_SSP245_ne30/emissions-cmip6_ssp245_e3sm_C2H6_surface_2015-2100_1.9x2.5_c20240219.nc',
          'C3H8      -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/CMIP6_SSP245_ne30/emissions-cmip6_ssp245_e3sm_C3H8_surface_2015-2100_1.9x2.5_c20240219.nc',
          'CH2O   -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/CMIP6_SSP245_ne30/emissions-cmip6_ssp245_e3sm_CH2O_surface_2015-2100_1.9x2.5_c20240219.nc',
          'CH3CHO    -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/CMIP6_SSP245_ne30/emissions-cmip6_ssp245_e3sm_CH3CHO_surface_2015-2100_1.9x2.5_c20240219.nc',
          'CH3COCH3  -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/CMIP6_SSP245_ne30/emissions-cmip6_ssp245_e3sm_CH3COCH3_surface_2015-2100_1.9x2.5_c20240219.nc',
          'CO     -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/CMIP6_SSP245_ne30/emissions-cmip6_ssp245_e3sm_CO_surface_2015-2100_1.9x2.5_c20240219.nc',
          'DMS    -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/DMSflux.1850-2100.1deg_latlon_conserv.POPmonthlyClimFromACES4BGC_c20160727.nc',
          'E90       -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart/ub/emissions_E90_surface_1750-2101_1.9x2.5_c20231222.nc',
          'ISOP   -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/CMIP6_SSP245_ne30/emissions-cmip6_ssp245_e3sm_ISOP_surface_2015-2100_1.9x2.5_c20240219.nc',
          'ISOP_VBS -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/CMIP6_SSP245_ne30/emissions-cmip6_ssp245_e3sm_ISOP_surface_2015-2100_1.9x2.5_c20240219.nc',
          'NO     -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/CMIP6_SSP245_ne30/emissions-cmip6_ssp245_e3sm_NO_surface_2015-2100_1.9x2.5_c20240219.nc',
          'SO2    -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/CMIP6_SSP245_ne30/cmip6_ssp245_mam4_so2_surf_2015-2100_c200716.nc',
          'SOAG0  -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/CMIP6_SSP245_ne30/emissions-cmip6_ssp245_e3sm_SOAG0_surf_2015-2100_1.9x2.5_c20240219.nc',
          'bc_a4  -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/CMIP6_SSP245_ne30/cmip6_ssp245_mam4_bc_a4_surf_2015-2100_c200716.nc',
          'num_a1 -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/CMIP6_SSP245_ne30/cmip6_ssp245_mam4_num_a1_surf_2015-2100_c200716.nc',
          'num_a2 -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/CMIP6_SSP245_ne30/cmip6_ssp245_mam4_num_a2_surf_2015-2100_c200716.nc',
          'num_a4 -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/CMIP6_SSP245_ne30/cmip6_ssp245_mam4_num_a4_surf_2015-2100_c200716.nc',
          'pom_a4 -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/CMIP6_SSP245_ne30/cmip6_ssp245_mam4_pom_a4_surf_2015-2100_c200716.nc',
          'so4_a1 -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/CMIP6_SSP245_ne30/cmip6_ssp245_mam4_so4_a1_surf_2015-2100_c200716.nc',
          'so4_a2 -> \$DIN_LOC_ROOT/atm/cam/chem/trop_mozart_aero/emis/CMIP6_SSP245_ne30/cmip6_ssp245_mam4_so4_a2_surf_2015-2100_c200716.nc'
  tracer_cnst_file              = 'oxid_SSP245_1.9x2.5_L70_1849-2101_c20240228.nc'
  bndtvghg              = '\$DIN_LOC_ROOT/atm/cam/ggas/GHG_CMIP_SSP245-1-2-1_Annual_Global_2015-2500_c20200807.nc'
EOF
# and similarly with user_nl_elm
cat >> user_nl_elm <<EOF
 ! -- replace historical landuse.timeseries with SSP245 to extend the AMIP --
 flanduse_timeseries = '\${DIN_LOC_ROOT}/lnd/clm2/surfdata_map/landuse.timeseries_0.5x0.5_ssp2_rcp45_simyr2015-2100_c240408.nc'
EOF
# change to use a new SSTICE data (the file below has data through end of 2022)
#./xmlchange SSTICE_DATA_FILENAME=/lcrc/group/e3sm2/ac.wlin/E3SMv3/AMIP/sstice-ext/sst_ice_CMIP6_DECK_E3SM_1x1_c20221024.nc
./xmlchange SSTICE_DATA_FILENAME=/global/cfs/cdirs/e3sm/benedict/e3sm_v3_inputs/AMIP/sstice-ext/sst_ice_CMIP6_DECK_E3SM_1x1_c20221024.nc
./xmlchange SSTICE_YEAR_END=2022
# Here on, can submit the job to continue the run as usual, run ./preview_namelists to confirm before submission.
