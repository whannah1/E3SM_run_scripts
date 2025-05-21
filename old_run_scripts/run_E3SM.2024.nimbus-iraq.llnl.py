#!/usr/bin/env python3
import os, datetime
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print(f'\n{clr.GREEN}{cmd}{clr.END}') ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
newcase,config,build,submit,continue_run,clean,debug = False,False,False,False,False,False,False
src_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC1' # branch => whannah/2024-nimbus-iraq

acct = 'nhclilab'

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

queue = 'pbatch' # pbatch / pdebug

# stop_opt,stop_n,resub,walltime = 'nsteps',5,0,'0:10:00'
# stop_opt,stop_n,resub,walltime = 'ndays',1,0,'1:00:00'
# stop_opt,stop_n,resub,walltime = 'ndays',13,0,'2:00:00'
stop_opt,stop_n,resub,walltime = 'ndays',14,0,'8:00:00'

compset = 'F2010'

data_root      = '/p/lustre1/hannah6/2024-nimbus-iraq-data'
case_scratch   = '/p/lustre1/hannah6/e3sm_scratch'
inputdata_root = '/p/lustre1/hannah6/inputdata'
# inputdata_root = '/usr/gdata/e3sm/ccsm3data/inputdata'

#---------------------------------------------------------------------------------------------------
# use this for setting CCSM_CO2_PPMV values
'''
import xarray as xr, numpy as np
co2_file = '/p/lustre1/hannah6/CESMLENS_delta/ghg_rcp85_1765-2500_c100203.nc'
ds = xr.open_dataset(co2_file)
year = ds['time.year']
co2_arr = ds.CO2
for t in range(len(year)):
   yr = year[t].values
   co2 = co2_arr[t].values
   if yr<=2050:
      print(f'{yr}  {co2}')
# print()
exit()
'''
#---------------------------------------------------------------------------------------------------
bne_list = []; date_list = []
atm_nn_list = []; alt_nn_list = []
ndg_on_list = []
pwg_on_list = []; pgw_yr_list = []
dt_phy_list = []; dt_dyn_list = []
debug_list = []
def add_case(bne,date,atm_nn,alt_nn,ndg_on,pwg_on=False,pgw_yr=None,dt_phy=None,dt_dyn=None,debug=False):
   bne_list.append(bne)
   date_list.append(date)
   atm_nn_list.append(atm_nn)
   alt_nn_list.append(alt_nn)
   ndg_on_list.append(ndg_on)
   pwg_on_list.append(pwg_on)
   pgw_yr_list.append(pgw_yr)
   dt_phy_list.append(dt_phy)
   dt_dyn_list.append(dt_dyn)
   debug_list.append(debug)
#---------------------------------------------------------------------------------------------------

# add_case( bne=32,  date='2022-05-14', atm_nn= 64, alt_nn=64, ndg_on=False, dt_phy=5*60, dt_dyn=30)
# add_case( bne=32,  date='2022-05-16', atm_nn= 64, alt_nn=64, ndg_on=False, dt_phy=5*60, dt_dyn=30)
# add_case( bne=32,  date='2022-05-14', atm_nn= 64, alt_nn=64, ndg_on=True,  dt_phy=5*60, dt_dyn=30)
# add_case( bne=32,  date='2022-05-16', atm_nn= 64, alt_nn=64, ndg_on=True,  dt_phy=5*60, dt_dyn=30)

# add_case( bne=64,  date='2022-05-14', atm_nn=128, alt_nn=64, ndg_on=False, dt_phy=2*60, dt_dyn=15)
# add_case( bne=64,  date='2022-05-16', atm_nn=128, alt_nn=64, ndg_on=False, dt_phy=2*60, dt_dyn=15)
# add_case( bne=64,  date='2022-05-14', atm_nn=128, alt_nn=64, ndg_on=True,  dt_phy=2*60, dt_dyn=15)
# add_case( bne=64,  date='2022-05-16', atm_nn=128, alt_nn=64, ndg_on=True,  dt_phy=2*60, dt_dyn=15)

# add_case( bne=128, date='2022-05-14', atm_nn=512, alt_nn=64, ndg_on=False, dt_phy=1*60, dt_dyn= 6)
# add_case( bne=128, date='2022-05-16', atm_nn=512, alt_nn=64, ndg_on=False, dt_phy=1*60, dt_dyn= 6)
# add_case( bne=128, date='2022-05-14', atm_nn=512, alt_nn=64, ndg_on=True,  dt_phy=1*60, dt_dyn= 6)
# add_case( bne=128, date='2022-05-16', atm_nn=512, alt_nn=64, ndg_on=True,  dt_phy=1*60, dt_dyn= 6)



# add_case( bne=32,  date='2022-05-14', atm_nn= 64, alt_nn=64, ndg_on=True,  dt_phy=5*60, dt_dyn=30, pwg_on=True, pgw_yr='2050')
# add_case( bne=128, date='2022-05-14', atm_nn=512, alt_nn=64, ndg_on=True,  dt_phy=1*60, dt_dyn= 6, pwg_on=True, pgw_yr='2050')

# add_case( bne=32,  date='2022-05-14', atm_nn= 64, alt_nn=64, ndg_on=True,  dt_phy=5*60, dt_dyn=30)
# add_case( bne=32,  date='2022-05-14', atm_nn= 64, alt_nn=64, ndg_on=True,  dt_phy=5*60, dt_dyn=30, pwg_on=True, pgw_yr='2025')
# add_case( bne=32,  date='2022-05-14', atm_nn= 64, alt_nn=64, ndg_on=True,  dt_phy=5*60, dt_dyn=30, pwg_on=True, pgw_yr='2030')
# add_case( bne=32,  date='2022-05-14', atm_nn= 64, alt_nn=64, ndg_on=True,  dt_phy=5*60, dt_dyn=30, pwg_on=True, pgw_yr='2035')
# add_case( bne=32,  date='2022-05-14', atm_nn= 64, alt_nn=64, ndg_on=True,  dt_phy=5*60, dt_dyn=30, pwg_on=True, pgw_yr='2040')
# add_case( bne=32,  date='2022-05-14', atm_nn= 64, alt_nn=64, ndg_on=True,  dt_phy=5*60, dt_dyn=30, pwg_on=True, pgw_yr='2045')
# add_case( bne=32,  date='2022-05-14', atm_nn= 64, alt_nn=64, ndg_on=True,  dt_phy=5*60, dt_dyn=30, pwg_on=True, pgw_yr='2050')
# add_case( bne=32,  date='2022-05-14', atm_nn= 64, alt_nn=64, ndg_on=True,  dt_phy=5*60, dt_dyn=30, pwg_on=True, pgw_yr='2055')
# add_case( bne=32,  date='2022-05-14', atm_nn= 64, alt_nn=64, ndg_on=True,  dt_phy=5*60, dt_dyn=30, pwg_on=True, pgw_yr='2060')
# add_case( bne=32,  date='2022-05-14', atm_nn= 64, alt_nn=64, ndg_on=True,  dt_phy=5*60, dt_dyn=30, pwg_on=True, pgw_yr='2065')
# add_case( bne=32,  date='2022-05-14', atm_nn= 64, alt_nn=64, ndg_on=True,  dt_phy=5*60, dt_dyn=30, pwg_on=True, pgw_yr='2070')
# add_case( bne=32,  date='2022-05-14', atm_nn= 64, alt_nn=64, ndg_on=True,  dt_phy=5*60, dt_dyn=30, pwg_on=True, pgw_yr='2075')
# add_case( bne=32,  date='2022-05-14', atm_nn= 64, alt_nn=64, ndg_on=True,  dt_phy=5*60, dt_dyn=30, pwg_on=True, pgw_yr='2080')
# add_case( bne=32,  date='2022-05-14', atm_nn= 64, alt_nn=64, ndg_on=True,  dt_phy=5*60, dt_dyn=30, pwg_on=True, pgw_yr='2085')
# add_case( bne=32,  date='2022-05-14', atm_nn= 64, alt_nn=64, ndg_on=True,  dt_phy=5*60, dt_dyn=30, pwg_on=True, pgw_yr='2090')
# add_case( bne=32,  date='2022-05-14', atm_nn= 64, alt_nn=64, ndg_on=True,  dt_phy=5*60, dt_dyn=30, pwg_on=True, pgw_yr='2095')
# add_case( bne=32,  date='2022-05-14', atm_nn= 64, alt_nn=64, ndg_on=True,  dt_phy=5*60, dt_dyn=30, pwg_on=True, pgw_yr='2100')

# add_case( bne=128, date='2022-05-14', atm_nn=512, alt_nn=64, ndg_on=True,  dt_phy=1*60, dt_dyn= 6)
# add_case( bne=128, date='2022-05-14', atm_nn=512, alt_nn=64, ndg_on=True,  dt_phy=1*60, dt_dyn= 6, pwg_on=True, pgw_yr='2050')

### debug runs
#### add_case( bne=32,  date='2022-05-14', atm_nn= 64, alt_nn=64, ndg_on=True,  dt_phy=5*60, dt_dyn=30,debug=True)
#### add_case( bne=32,  date='2022-05-14', atm_nn= 64, alt_nn=64, ndg_on=True,  dt_phy=5*60, dt_dyn=30, pwg_on=True, pgw_yr='2050',debug=True)
#### add_case( bne=128, date='2022-05-14', atm_nn=512, alt_nn=64, ndg_on=True,  dt_phy=1*60, dt_dyn= 6,debug=True)
#### add_case( bne=128, date='2022-05-14', atm_nn=512, alt_nn=64, ndg_on=True,  dt_phy=1*60, dt_dyn= 6, pwg_on=True, pgw_yr='2050',debug=True)

# add_case( bne=32,  date='2022-05-14', atm_nn=64, alt_nn=64, ndg_on=True,  dt_phy=5*60, dt_dyn=30)
# add_case( bne=32,  date='2022-05-14', atm_nn=64, alt_nn=64, ndg_on=True,  dt_phy=5*60, dt_dyn=30, pwg_on=True, pgw_yr='2050')
# add_case( bne=32,  date='2022-05-14', atm_nn=64, alt_nn=64, ndg_on=True,  dt_phy=5*60, dt_dyn=30, pwg_on=True, pgw_yr='2100')


add_case( bne=64,  date='2022-05-14', atm_nn=256, alt_nn=64, ndg_on=True,  dt_phy=2*60, dt_dyn=15)
add_case( bne=128, date='2022-05-14', atm_nn=512, alt_nn=64, ndg_on=True,  dt_phy=1*60, dt_dyn= 6)

#---------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------
def main(bne,start_date,atm_nn,alt_nn,ndg_on,pwg_on,pgw_yr,dt_phy,dt_dyn,debug):

   grid=f'ne0np4-2024-nimbus-iraq-{bne}x3-pg2'

   # case_list = ['E3SM','2024-NIMBUS-IRAQ-TEST',f'{bne}x3-pg2',compset,start_date]
   # case_list = ['E3SM','2024-NIMBUS-IRAQ',grid,compset]
   # case_list = ['E3SM','2024-NIMBUS-IRAQ',f'{bne}x3-pg2',compset,start_date]
   # case_list = ['E3SM','2024-NIMBUS-IRAQ-00',f'{bne}x3-pg2',compset,start_date] # restart - add more fields - deal with mach changes
   # case_list = ['E3SM','2024-NIMBUS-IRAQ-01',f'{bne}x3-pg2',compset,start_date] # restart - correct namelist bug in 00
   case_list = ['E3SM','2024-NIMBUS-IRAQ-02',f'{bne}x3-pg2',compset,start_date] # new CO2 values
   # case_list = ['E3SM','2024-NIMBUS-IRAQ-03',f'{bne}x3-pg2',compset,start_date] # switch to testing nudging strength
   
   Nudge_Tau = 6 # default for previous ensembles
   # Nudge_Tau = 12
   # Nudge_Tau = 24
   # Nudge_Tau = 48

   # for ensemble #02
   case_list.append(f'NN_{atm_nn}')
   case_list.append(f'DTP_{dt_phy}')
   case_list.append(f'DTD_{dt_dyn}')
   case_list.append( 'NDG_'+('ON' if ndg_on else 'OFF'))
   
   # for ensemble #03
   # case_list.append(f'NDG_TAU_{Nudge_Tau}')
   
   case_list.append( 'PGW_'+(pgw_yr if pwg_on else 'OFF'))

   if debug: case_list.append( 'debug' )

   case = '.'.join(case_list)
   
   case_root = f'{case_scratch}/{case}'
   
   #---------------------------------------------------------------------------------------------------
   print('-'*80); print(f'\n  case : {case}\n')
   #------------------------------------------------------------------------------------------------
   if pwg_on:
      sst_data_file = f'{data_root}/files_init/HICCUP.sst_noaa.{start_date}.PGW.{pgw_yr}.nc'
      # atm_init_file = f'{data_root}/files_init/HICCUP.atm_era5.{start_date}.2024-nimbus-iraq-{bne}x3.L80.PGW.{pgw_yr}.nc'
   else:
      sst_data_file = f'{data_root}/files_init/HICCUP.sst_noaa.{start_date}.nc'
      # atm_init_file = f'{data_root}/files_init/HICCUP.atm_era5.{start_date}.2024-nimbus-iraq-{bne}x3.L80.nc'

   sst_grid_file = f'{data_root}/files_domain/domain.ocn.1800x3600.20240618.nc'
   #------------------------------------------------------------------------------------------------
   nudge_data_root = f'{data_root}/nudging_data'
   #------------------------------------------------------------------------------------------------
   max_mpi_per_node = 112
   atm_ntasks = atm_nn*max_mpi_per_node
   atm_nthrds = 1#2
   #------------------------------------------------------------------------------------------------
   if newcase :
      if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
      cmd = f'{src_dir}/cime/scripts/create_newcase '
      cmd += f' --case {case}'
      cmd += f' --output-root {case_root} '
      cmd += f' --script-root {case_root}/case_scripts '
      cmd += f' --handle-preexisting-dirs u '
      cmd += f' --compset {compset} --res {grid} '
      cmd += f' --project {acct} '
      cmd += f' -mach dane -pecount {atm_ntasks}x{atm_nthrds} '
      run_cmd(cmd)

      os.chdir(f'{case_root}/case_scripts')
      run_cmd(f'./xmlchange EXEROOT={case_root}/bld ')
      run_cmd(f'./xmlchange RUNDIR={case_root}/run ')

      # /p/lustre1/hannah6/2024-nimbus-iraq-data/files_map

      map_file_lnd2rof = f'{data_root}/files_map/map_2024-nimbus-iraq-{bne}x3_to_r0125_traave.20240701.nc'
      map_file_rof2lnd = f'{data_root}/files_map/map_r0125_to_2024-nimbus-iraq-{bne}x3_traave.20240701.nc'
      run_cmd(f'./xmlchange --file env_run.xml LND2ROF_FMAPNAME={map_file_lnd2rof}' )
      run_cmd(f'./xmlchange --file env_run.xml ROF2LND_FMAPNAME={map_file_rof2lnd}' )
      run_cmd(f'./xmlchange --file env_run.xml ATM2ROF_FMAPNAME={map_file_lnd2rof}' )
      run_cmd(f'./xmlchange --file env_run.xml ATM2ROF_SMAPNAME={map_file_lnd2rof}' )

      map_file_rof2ocn = f'{data_root}/files_map/map_r0125_to_ICOS10_smoothed.r50e100.220302.nc'
      run_cmd(f'./xmlchange --file env_run.xml ROF2OCN_LIQ_RMAPNAME={map_file_rof2ocn}' )
      run_cmd(f'./xmlchange --file env_run.xml ROF2OCN_ICE_RMAPNAME={map_file_rof2ocn}' )

      map_file_atm2ocn_blin = f'{data_root}/files_map/map_2024-nimbus-iraq-{bne}x3-pg2_to_ICOS10_trbilin.20240618.nc'
      map_file_ocn2atm_blin = f'{data_root}/files_map/map_ICOS10_to_2024-nimbus-iraq-{bne}x3-pg2_trbilin.20240618.nc'
      map_file_atm2ocn_aave = f'{data_root}/files_map/map_2024-nimbus-iraq-{bne}x3-pg2_to_ICOS10_traave.20240618.nc'
      map_file_ocn2atm_aave = f'{data_root}/files_map/map_ICOS10_to_2024-nimbus-iraq-{bne}x3-pg2_traave.20240618.nc'
      run_cmd(f'./xmlchange --file env_run.xml ATM2OCN_SMAPNAME={map_file_atm2ocn_blin}' )
      run_cmd(f'./xmlchange --file env_run.xml ATM2OCN_VMAPNAME={map_file_atm2ocn_blin}' )
      run_cmd(f'./xmlchange --file env_run.xml ATM2OCN_FMAPNAME={map_file_atm2ocn_aave}' )
      run_cmd(f'./xmlchange --file env_run.xml OCN2ATM_SMAPNAME={map_file_ocn2atm_blin}' )
      # run_cmd(f'./xmlchange --file env_run.xml OCN2ATM_VMAPNAME={map_file_ocn2atm_blin}' )
      run_cmd(f'./xmlchange --file env_run.xml OCN2ATM_FMAPNAME={map_file_ocn2atm_aave}' )

   #------------------------------------------------------------------------------------------------
   os.chdir(f'{case_root}/case_scripts')
   #------------------------------------------------------------------------------------------------
   if config:
      #-------------------------------------------------------------------------
      # when specifying ncdata, do it here to avoid an error message
      write_namelist_all(bne,start_date,pwg_on,dt_phy,dt_dyn,ndg_on,nudge_data_root,pgw_yr,Nudge_Tau)
      #-------------------------------------------------------------------------
      # set nlev due to override of new L80 default for ne0/RRM cases
      run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -nlev 80 \" ')
      #-------------------------------------------------------------------------
      # disable TOP scheme - topo is missing in fsurdat - use "plane parallel" (pp)
      run_cmd(f'./xmlchange --append --id ELM_BLDNML_OPTS --val \" -solar_rad_scheme pp \" ')
      #-------------------------------------------------------------------------
      tmp_ntasks = alt_nn*max_mpi_per_node
      run_cmd(f'./xmlchange --file env_mach_pes.xml NTASKS_ICE="{tmp_ntasks}" ')
      run_cmd(f'./xmlchange --file env_mach_pes.xml NTASKS_OCN="{tmp_ntasks}" ')
      #-------------------------------------------------------------------------
      tmp_nthrds = 1
      run_cmd(f'./xmlchange --file env_mach_pes.xml NTHRDS_ATM="{atm_nthrds}" ')
      run_cmd(f'./xmlchange --file env_mach_pes.xml NTHRDS_LND="{tmp_nthrds}" ')
      run_cmd(f'./xmlchange --file env_mach_pes.xml NTHRDS_ICE="{tmp_nthrds}" ')
      run_cmd(f'./xmlchange --file env_mach_pes.xml NTHRDS_OCN="{tmp_nthrds}" ')
      run_cmd(f'./xmlchange --file env_mach_pes.xml NTHRDS_CPL="1" ')
      run_cmd(f'./xmlchange --file env_mach_pes.xml NTHRDS_GLC="1" ')
      run_cmd(f'./xmlchange --file env_mach_pes.xml NTHRDS_ROF="{tmp_nthrds}" ')
      run_cmd(f'./xmlchange --file env_mach_pes.xml NTHRDS_WAV="1" ')
      #-------------------------------------------------------------------------
      run_cmd(f'./xmlchange PIO_NETCDF_FORMAT="64bit_data"')
      #-------------------------------------------------------------------------
      run_cmd('./case.setup --reset')
   #------------------------------------------------------------------------------------------------
   if build: 
      if debug: run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
      if clean : run_cmd('./case.build --clean-all')
      run_cmd('./case.build')
   #------------------------------------------------------------------------------------------------
   if submit:
      write_namelist_all(bne,start_date,pwg_on,dt_phy,dt_dyn,ndg_on,nudge_data_root,pgw_yr,Nudge_Tau)
      ncpl = 86400/dt_phy
      run_cmd(f'./xmlchange ATM_NCPL={str(ncpl)}')
      #-------------------------------------------------------------------------
      run_cmd(f'./xmlchange DIN_LOC_ROOT=\'{inputdata_root}\' ')
      #-------------------------------------------------------------------------
      start_year = int(start_date.split('-')[0])
      run_cmd(f'./xmlchange --file env_run.xml RUN_STARTDATE={start_date}')
      #-------------------------------------------------------------------------
      sst_data_year = int(start_date.split('-')[0])
      run_cmd(f'./xmlchange --file env_run.xml  SSTICE_DATA_FILENAME={sst_data_file}')
      run_cmd(f'./xmlchange --file env_run.xml  SSTICE_YEAR_ALIGN={sst_data_year}')
      run_cmd(f'./xmlchange --file env_run.xml  SSTICE_YEAR_START={sst_data_year}')
      run_cmd(f'./xmlchange --file env_run.xml  SSTICE_YEAR_END={(sst_data_year+1)}')
      run_cmd(f'./xmlchange --file env_run.xml  SSTICE_GRID_FILENAME={sst_grid_file}')
      #-------------------------------------------------------------------------
      # An alternate grid checking threshold is needed for seq_domain_check_grid
      run_cmd('./xmlchange --file env_run.xml  EPS_AGRID=5e-10' ) # default = 1.0e-12
      #-------------------------------------------------------------------------
      # prescribe CO2 based on RCP8.5 forcing
      if '2024-NIMBUS-IRAQ-00' not in case and '2024-NIMBUS-IRAQ-01' not in case:
         if pwg_on:
            found = False
            if pgw_yr=='2020': run_cmd(f'./xmlchange CCSM_CO2_PPMV=415.780'); found = True
            if pgw_yr=='2025': run_cmd(f'./xmlchange CCSM_CO2_PPMV=431.475'); found = True
            if pgw_yr=='2030': run_cmd(f'./xmlchange CCSM_CO2_PPMV=448.835'); found = True
            if pgw_yr=='2035': run_cmd(f'./xmlchange CCSM_CO2_PPMV=467.850'); found = True
            if pgw_yr=='2040': run_cmd(f'./xmlchange CCSM_CO2_PPMV=489.435'); found = True
            if pgw_yr=='2045': run_cmd(f'./xmlchange CCSM_CO2_PPMV=513.456'); found = True
            if pgw_yr=='2050': run_cmd(f'./xmlchange CCSM_CO2_PPMV=540.543'); found = True
            if pgw_yr=='2055': run_cmd(f'./xmlchange CCSM_CO2_PPMV=570.517'); found = True
            if pgw_yr=='2060': run_cmd(f'./xmlchange CCSM_CO2_PPMV=603.520'); found = True
            if pgw_yr=='2065': run_cmd(f'./xmlchange CCSM_CO2_PPMV=639.291'); found = True
            if pgw_yr=='2070': run_cmd(f'./xmlchange CCSM_CO2_PPMV=677.078'); found = True
            if pgw_yr=='2075': run_cmd(f'./xmlchange CCSM_CO2_PPMV=717.016'); found = True
            if pgw_yr=='2080': run_cmd(f'./xmlchange CCSM_CO2_PPMV=758.182'); found = True
            if pgw_yr=='2085': run_cmd(f'./xmlchange CCSM_CO2_PPMV=801.019'); found = True
            if pgw_yr=='2090': run_cmd(f'./xmlchange CCSM_CO2_PPMV=844.805'); found = True
            if pgw_yr=='2095': run_cmd(f'./xmlchange CCSM_CO2_PPMV=889.982'); found = True
            if pgw_yr=='2100': run_cmd(f'./xmlchange CCSM_CO2_PPMV=935.874'); found = True
            if not found : raise ValueError(f'ERROR: no CO2 value found for pgw_yr: {pgw_yr}')
         else:
            run_cmd(f'./xmlchange CCSM_CO2_PPMV=421.0')
      #-------------------------------------------------------------------------
      run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
      run_cmd(f'./xmlchange STOP_N={stop_n}')
      run_cmd(f'./xmlchange JOB_QUEUE={queue}')
      run_cmd(f'./xmlchange USER_REQUESTED_QUEUE={queue}')
      run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
      run_cmd(f'./xmlchange RESUBMIT={resub}')
      run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')
      # run_cmd(f'./xmlchange REST_OPTION="ndays",REST_N=1')
      run_cmd(f'./xmlchange REST_OPTION={stop_opt}')
      run_cmd(f'./xmlchange REST_N={stop_n}')

      continue_flag = 'TRUE' if continue_run else 'False'
      run_cmd(f'./xmlchange --file env_run.xml CONTINUE_RUN={continue_flag} ')

      run_cmd(f'./case.submit -a="-t {walltime}" ')
   #------------------------------------------------------------------------------------------------
   run_cmd('./preview_run')
   print(f'\n  case : {case}\n'); print('-'*80) # Print the case name again for reference

#---------------------------------------------------------------------------------------------------
def write_namelist_atm(bne,start_date,pwg_on,dt_phy,dt_dyn,ndg_on,nudge_data_root,pgw_yr,Nudge_Tau):
   nfile = 'user_nl_eam'
   file = open(nfile,'w')
   file.write(' nhtfrq = 0,-1,-3 \n')
   file.write(' mfilt  = 1,24,8 \n')
   file.write('\n')
   file.write(" fincl1 = 'Z3','CLOUD','CLDLIQ','CLDICE'\n")
   file.write(" fincl2 = 'PS','PSL','TS'")
   file.write(          ",'PRECT','TMQ'")
   file.write(          ",'LHFLX','SHFLX'")             # surface fluxes
   file.write(          ",'FLDS','FLNS'")               # sfc LW
   file.write(          ",'FSDS','FSNS'")               # sfc SW
   file.write(          ",'FLDSC','FLNSC'")             # sfc LW clearsky
   file.write(          ",'FSDSC','FSNSC'")             # sfc SW clearsky
   # file.write(          ",'FLUTOA','FLNTOA'")           # toa LW           < need code changes to support
   # file.write(          ",'FSUTOA','FSNTOA'")           # toa SW           < need code changes to support
   # file.write(          ",'FLUTOAC','FLNTOAC'")         # toa LW clearsky  < need code changes to support
   # file.write(          ",'FSUTOAC','FSNTOAC'")         # toa SW clearsky  < need code changes to support
   file.write(          ",'FSNT','FLNT'")               # Net TOM rad
   file.write(          ",'FLNS','FSNS'")               # Net Sfc rad
   file.write(          ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
   file.write(          ",'TGCLDLWP','TGCLDIWP'")       # liq & ice water path
   file.write(          ",'CLDTOT','CLDLOW','CLDMED','CLDHGH'")
   file.write(          ",'TUQ','TVQ'")                 # vapor transport for AR tracking
   # variables for tracking stuff like hurricanes
   file.write(          ",'TBOT:I','QBOT:I','UBOT:I','VBOT:I'") # lowest model level
   file.write(          ",'T900:I','Q900:I','U900:I','V900:I'") # 900mb data
   file.write(          ",'T850:I','Q850:I','U850:I','V850:I'") # 850mb data
   file.write(          ",'Z300:I','Z500:I','OMEGA850:I','OMEGA500:I'")
   file.write(          ",'U200:I','V200:I'")
   # file.write(          ",'U10:I','TREFHT:I'")
   # dust analysis
   file.write(          ",'dst_a1SF','dst_a3SF'") # sfc dust emission
   file.write(          ",'AODVIS','AODDUST'")
   file.write(          ",'AODDUST1','AODDUST2','AODDUST3','AODDUST4'")
   file.write(          ",'BURDENDUST','ABURDENDUST'")
   file.write('\n')
   file.write(" fincl3 = 'PS','U','V','OMEGA'")
   file.write(          ",'T','Q','Z3','RELHUM','QRS','QRL'")
   file.write(          ",'dst_a1','dst_a3','Mass_dst'") # dust concentration
   # file.write(          ",'dst_c1','dst_c3'") # cloud-borne
   file.write(          ",'Vdst_a1','Vdst_a3'") #  Meridional dust transport
   file.write('\n')
   if ndg_on:
      start_yr = int(start_date.split('-')[0])
      start_mn = int(start_date.split('-')[1])
      start_dy = int(start_date.split('-')[2])
      file.write(f" Nudge_Model =.true. \n")
      file.write(f" Nudge_Path ='{nudge_data_root}/' \n")
      file.write(f" Nudge_File_Template='HICCUP.nudging_uv_era5.%y-%m-%d.2024-nimbus-iraq-{bne}x3.L80.nc' \n")
      file.write(f" Model_Times_Per_Day = 1152 \n") # Number of times to update the model state
      file.write(f" Nudge_Times_Per_Day = 8 \n") # nudging input data frequency
      # file.write(f" Nudge_Tau           = 6 \n")
      file.write(f" Nudge_Tau           = {Nudge_Tau} \n")
      file.write(f" Nudge_Ucoef         = 1 \n")
      file.write(f" Nudge_Vcoef         = 1 \n")
      file.write(f" Nudge_Uprof         = 1 \n") # uniform nudging
      file.write(f" Nudge_Vprof         = 1 \n") # uniform nudging
      file.write(f" Nudge_Beg_Year      = {start_yr} \n")
      file.write(f" Nudge_Beg_Month     = {start_mn} \n")
      file.write(f" Nudge_Beg_Day       = {start_dy} \n")
      file.write(f" Nudge_End_Year      = {start_yr+1} \n")
      file.write(f" Nudge_End_Month     = {start_mn} \n")
      file.write(f" Nudge_End_Day       = {start_dy} \n")
      # file.write(f" Nudge_Hwin_lo       = 0.1 \n")
      # file.write(f" Nudge_Hwin_hi       = 1.0 \n")
      # file.write(f" Nudge_Hwin_lat0     = 39.9 \n")
      # file.write(f" Nudge_Hwin_latWidth = 4. \n")
      # file.write(f" Nudge_Hwin_latDelta = 0.1 \n")
      # file.write(f" Nudge_Hwin_lon0     = 116.4 \n")
      # file.write(f" Nudge_Hwin_lonWidth = 4. \n")
      # file.write(f" Nudge_Hwin_lonDelta = 0.1 \n")
      # file.write(f" Nudge_Vwin_lo       = 0.0 \n")
      # file.write(f" Nudge_Vwin_hi       = 1.0 \n")
      # file.write(f" Nudge_Vwin_Hindex   = 127.0 \n")
      # file.write(f" Nudge_Vwin_Hdelta   = 10. \n")
      # file.write(f" Nudge_Vwin_Lindex   = 0.0 \n")
      # file.write(f" Nudge_Vwin_Ldelta   = 0.1  \n") # cannot be < 0
      file.write(f" Nudge_File_Ntime = 1 \n") # Number of time slices per nudging data file
      file.write(f" Nudge_Loc_PhysOut =.true. \n") # whether nudging tendency is calculated at the same location where the model state variables are written out
      file.write(f" Nudge_CurrentStep =.true. \n") # .true. if linearly interpolated to current model time step
   file.write('\n')
   
   if pwg_on:
      atm_init_file = f'{data_root}/files_init/HICCUP.atm_era5.{start_date}.2024-nimbus-iraq-{bne}x3.L80.PGW.{pgw_yr}.nc'
   else:
      atm_init_file = f'{data_root}/files_init/HICCUP.atm_era5.{start_date}.2024-nimbus-iraq-{bne}x3.L80.nc'
   file.write(f" ncdata  = '{atm_init_file}' \n")
   topo_file = f'{data_root}/files_topo/USGS-topo_2024-nimbus-iraq-{bne}x3-np4_smoothedx6t_20240618.nc'
   dryd_file = f'{data_root}/files_atmsrf/atm_srf_2024-nimbus-iraq-{bne}x3-pg2_20240618.nc'
   file.write(f" bnd_topo  = '{topo_file}' \n")
   file.write(f" drydep_srf_file  = '{dryd_file}' \n")
   file.write(f" mesh_file = \'{data_root}/files_grid/2024-nimbus-iraq-{bne}x3.g\' \n")
   factor = int(dt_phy/dt_dyn)
   file.write(f' se_tstep = {dt_dyn} \n')
   file.write(f' hypervis_subcycle_q = {factor} \n')
   file.write(f' dt_tracer_factor = {factor} \n')
   file.write(f' dt_remap_factor = 1 \n')
   file.write(f' nu_top = 1e4 \n')
   file.write(f' tom_sponge_start = 10 \n')
   file.close()
#-------------------------------------------------------------------------------
def write_namelist_lnd(bne,start_date):
   lnd_init_case = f'ELM_spinup.ICRUELM.ne0np4-2024-nimbus-iraq-{bne}x3-pg2.20-yr.2015-10-01'
   if bne== 32: lnd_init_date = '0021-01-01'
   if bne== 64: lnd_init_date = '0021-01-01'
   if bne==128: lnd_init_date = '0021-01-01'
   # lnd_init_file = f'/p/lustre2/hannah6/e3sm_scratch/{lnd_init_case}/run/{lnd_init_case}.elm.r.{lnd_init_date}-00000.nc'
   lnd_init_file = f'{data_root}/files_finidat/{lnd_init_case}.elm.r.{lnd_init_date}-00000.nc'
   lnd_data_file = f'{data_root}/files_fsurdat_ne{bne}/surfdata_2024-nimbus-iraq-{bne}x3-pg2_simyr2010_c240701.nc'
   nfile = 'user_nl_elm'
   file = open(nfile,'w') 
   file.write(f'fsurdat = \'{lnd_data_file}\' \n')
   file.write(f'finidat = \'{lnd_init_file}\' \n')
   # file.write(f'use_top_solar_rad = .false. \n')
   file.close()
#-------------------------------------------------------------------------------
def write_namelist_all(bne,start_date,pwg_on,dt_phy,dt_dyn,ndg_on,nudge_data_root,pgw_yr,Nudge_Tau):
   write_namelist_atm(bne,start_date,pwg_on,dt_phy,dt_dyn,ndg_on,nudge_data_root,pgw_yr,Nudge_Tau)
   write_namelist_lnd(bne,start_date)
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':

   for n in range(len(bne_list)):
      print('-'*80)
      main( bne_list[n], \
            date_list[n], \
            atm_nn_list[n], \
            alt_nn_list[n], \
            ndg_on_list[n], \
            pwg_on_list[n], \
            pgw_yr_list[n], \
            dt_phy_list[n], \
            dt_dyn_list[n], \
            debug_list[n], \
           )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
