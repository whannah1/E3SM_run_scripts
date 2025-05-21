
#!/bin/bash
 
E3SM_HOME=~/E3SM/E3SM_SRC_master
COMPILER=pgigpu
MACH=summit
PES=36x1
RES=ne4_ne4
PROJ=cli115
 
CASE=sp1vfast3d_05

echo
echo $CASE
echo

cd $E3SM_HOME

$E3SM_HOME/cime/scripts/create_newcase \
-compset FSP1FAST -case ~/E3SM/Cases/$CASE  -compiler $COMPILER \
-mach $MACH \
-project $PROJ \
-pecount $PES \
-res $RES \
--handle-preexisting-dirs r || exit -1

cd ~/E3SM/Cases/$CASE

./xmlchange ATM_NCPL=144,STOP_N=1
./xmlchange CHARGE_ACCOUNT=$PROJ

# ./xmlchange -file env_build.xml -id DEBUG -val TRUE

cat > user_nl_cam << 'eof'
prescribed_aero_cycle_yr = 01   
prescribed_aero_file = 'mam4_0.9x1.2_L72_2000clim_c170323.nc'
prescribed_aero_datapath = '/gpfs/alpine/world-shared/csc190/e3sm/cesm/inputdata/atm/cam/chem/trop_mam/aero'
use_hetfrz_classnuc = .false.
prescribed_aero_type = 'CYCLICAL'
aerodep_flx_type = 'CYCLICAL'
aerodep_flx_datapath = '/gpfs/alpine/world-shared/csc190/e3sm/cesm/inputdata/atm/cam/chem/trop_mam/aero'
aerodep_flx_file = 'mam4_0.9x1.2_L72_2000clim_c170323.nc'
aerodep_flx_cycle_yr = 01
srf_flux_avg = 1
state_debug_checks = .false.
eof

./case.setup --reset

# sed -i 's/-Mstack_arrays/ /' Macros.make

# ./case.build --clean-all
./case.build 
./case.submit


echo
echo $CASE
echo