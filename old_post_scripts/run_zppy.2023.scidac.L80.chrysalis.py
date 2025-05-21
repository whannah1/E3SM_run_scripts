#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
'''
Below are commands to create grid and map files. 
copying and pasting all this into the terminal should work if
 - the directories ~/grids and ~/maps exist
 - NCO is installed in your path or conda environment

NE=30
SRC_GRID=ne${NE}pg2
DST_NY=180
DST_NX=360
DST_GRID=${DST_NY}x${DST_NX}

GRID_FILE_PATH=~/grids
SRC_GRID_FILE=${GRID_FILE_PATH}/${SRC_GRID}_scrip.nc
DST_GRID_FILE=${GRID_FILE_PATH}/${DST_GRID}_scrip.nc
MAP_FILE=~/maps/map_${SRC_GRID}_to_${DST_GRID}_aave.nc

# generate model grid file
GenerateCSMesh --alt --res ${NE} --file ${GRID_FILE_PATH}/ne${NE}.g
GenerateVolumetricMesh --in ${GRID_FILE_PATH}/ne${NE}.g --out ${GRID_FILE_PATH}/ne${NE}pg2.g --np 2 --uniform
ConvertMeshToSCRIP --in ${GRID_FILE_PATH}/ne${NE}pg2.g --out ${GRID_FILE_PATH}/ne${NE}pg2_scrip.nc

# generate lat/lon grid file
ncremap -g ${DST_GRID_FILE} -G ttl="Equi-Angular grid, dimensions ${DST_GRID}, cell edges on Poles/Equator and Prime Meridian/Date Line"#latlon=${DST_NY},${DST_NX}#lat_typ=uni#lon_typ=grn_wst

# generate map file
ncremap -6 --alg_typ=aave --grd_src=$SRC_GRID_FILE --grd_dst=$DST_GRID_FILE --map=$MAP_FILE

'''
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
# unified_env = '/global/common/software/e3sm/anaconda_envs/load_latest_e3sm_unified_pm-cpu.sh'
unified_env = '/lcrc/soft/climate/e3sm-unified/load_latest_e3sm_unified_chrysalis.sh'
def run_cmd(cmd): 
   print('\n'+clr.GREEN+cmd+clr.END);
   os.system(cmd); 
   return
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp, glob
run_zppy,clear_status,st_archive = False,False,False

acct = 'm4310'

st_archive   = True
# clear_status = False
run_zppy     = True

case_list,scratch_list = [],[]

case_list.append('20231002.v3alpha04_bigrid_L80_QBO1.F2010.chrysalis')
scratch_list.append('/lcrc/group/acme/ac.benedict/E3SMv3_dev')

# www_path = '/lcrc/group/e3sm/public_html/diagnostic_output/ac.whannah/E3SMv3_dev'
www_path = '/lcrc/group/e3sm/public_html/diagnostic_output/ac.benedict/E3SMv3_dev'

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def main(case,scratch_path):
   if h is None or c is None or e is None: exit(' one or more arguments not provided?')

   case_root = f'{scratch_path}/{case}'

   # print(case); return

   #------------------------------------------------------------------------------------------------
   #------------------------------------------------------------------------------------------------
   print('\n  case : '+case+'\n')
   #------------------------------------------------------------------------------------------------
   if st_archive:
      os.chdir(f'{case_root}/case_scripts')
      ### this doesn't work for some reason...? 
      ### (it also screws up the alt approach below to move stuff afterwards)
      run_cmd(f'./xmlchange DOUT_S_ROOT={case_root}/archive ')
      # run_cmd(f'./xmlquery DOUT_S_ROOT ')

      run_cmd('./case.st_archive')

      # archive file path is messed up because of default DOUT_S_ROOT
      # so move the files to a more sensible structure
      # run_cmd(f'mv {case_root}/archive/{case}/* {case_root}/archive/ ')

      ### these next lines are for the case where I tried to change DOUT_S_ROOT above
      # run_cmd(f'mv {case_root}/archive/{case}/atm/hist/* {case_root}/archive/atm/hist/ ')
      # run_cmd(f'mv {case_root}/archive/{case}/cpl/hist/* {case_root}/archive/cpl/hist/ ')
      # run_cmd(f'mv {case_root}/archive/{case}/lnd/hist/* {case_root}/archive/lnd/hist/ ')
      # run_cmd(f'mv {case_root}/archive/{case}/ice/hist/* {case_root}/archive/ice/hist/ ')
      # run_cmd(f'mv {case_root}/archive/{case}/ocn/hist/* {case_root}/archive/ocn/hist/ ')
      # run_cmd(f'mv {case_root}/archive/{case}/rof/hist/* {case_root}/archive/rof/hist/ ')
      # run_cmd(f'mv {case_root}/archive/{case}/rest/*     {case_root}/archive/rest/ ')
   #------------------------------------------------------------------------------------------------
   if clear_status:
      status_files = glob.glob(f'{case_root}/post/scripts/*status')
      for file_name in status_files:
         os.remove(file_name)
   #------------------------------------------------------------------------------------------------
   if run_zppy:
      # Clear status files that don't indicate "OK"
      status_files = glob.glob(f'{case_root}/post/scripts/*status')
      for file_name in status_files:
         file_ptr = open(file_name)
         contents = file_ptr.read().split()
         if contents[0]!='OK': os.remove(file_name)

      # dynamically create the zppy config file
      zppy_file_name = os.getenv('HOME')+f'/E3SM/zppy_cfg/post.{case}.cfg'
      file = open(zppy_file_name,'w')
      file.write(get_zppy_config(case,case_root))
      file.close()

      print(f'  zppy cfg => {zppy_file_name}')

      # submit the zppy job
      run_cmd(f'source {unified_env}; zppy -c {zppy_file_name}')
   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {case}\n')
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def get_zppy_config(case_name,case_root):
   short_name = case_name
   grid,map_file = '180x360','/home/ac.zender/data/maps/map_ne30pg2_to_cmip6_180x360_aave.20200201.nc'
   # yr1,yr2,nyr,ts_nyr = 1984,1993,10,10
   # yr1,yr2,nyr,ts_nyr = 1984,2003,20,20
   yr1,yr2,nyr,ts_nyr = 2000,2010,10,10
   return f'''
[default]
account = {acct}
input = {case_root}
output = {case_root}
case = {case_name}
www = {www_path}
partition = compute
environment_commands = "source {unified_env}"

[climo]
active = True
walltime = "1:00:00"
years = "{yr1}:{yr2}:{nyr}",

  [[ atm_monthly_{grid}_aave ]]
  input_subdir = "archive/atm/hist"
  input_files = "eam.h0"
  mapping_file = {map_file}
  grid = "{grid}"
  frequency = "monthly"

[ts]
active = True
walltime = "0:30:00"
years = "{yr1}:{yr2}:{ts_nyr}",

  [[ atm_monthly_{grid}_aave ]]
  input_subdir = "archive/atm/hist"
  input_files = "eam.h0"
  mapping_file = {map_file}
  grid = "{grid}"
  frequency = "monthly"
  vars = "FSNTOA,FLUT,FSNT,FLNT,FSNS,FLNS,SHFLX,QFLX,TAUX,TAUY,PRECC,PRECL,PRECSC,PRECSL,TS,TREFHT,OMEGA,U,V,T,Q,RELHUM,O3,AODALL,AODDUST,AODVIS,PS,SWCF,LWCF,TMQ,TCO"

  [[ atm_monthly_glb ]]
  input_subdir = "archive/atm/hist"
  input_files = "eam.h0"
  mapping_file = "glb"
  frequency = "monthly"
  vars = "FSNTOA,FLUT,FSNT,FLNT,FSNS,FLNS,SHFLX,QFLX,TAUX,TAUY,PRECC,PRECL,PRECSC,PRECSL,TS,TREFHT,AODALL,AODDUST,AODVIS,PS,SWCF,LWCF,TMQ,TCO"

  [[ land_monthly ]]
  input_subdir = "archive/lnd/hist"
  input_files = "elm.h0"
  mapping_file = {map_file}
  grid = "{grid}"
  frequency = "monthly"
  vars = "FSH,RH2M"
  extra_vars = "landfrac"

[e3sm_diags]
active = True
years = "{yr1}:{yr2}:{nyr}",
ts_num_years = {ts_nyr}
ref_start_yr = 1979
ref_final_yr = 2016
walltime = "24:00:00"

  [[ atm_monthly_{grid}_aave ]]
  short_name = '{short_name}'
  grid = '{grid}'
  sets = 'lat_lon','zonal_mean_xy','zonal_mean_2d','polar','cosp_histogram','meridional_mean_2d','enso_diags','qbo','annual_cycle_zonal_mean','zonal_mean_2d_stratosphere'
  vars = "FSNTOA,FLUT,FSNT,FLNT,FSNS,FLNS,SHFLX,QFLX,TAUX,TAUY,PRECC,PRECL,PRECSC,PRECSL,TS,TREFHT,OMEGA,U,V,T,Q,RELHUM,O3,AODALL,AODDUST,AODVIS,PS,SWCF,LWCF,TMQ,TCO"
  reference_data_path = '/lcrc/soft/climate/e3sm_diags_data/obs_for_e3sm_diags/climatology'
  obs_ts = '/lcrc/soft/climate/e3sm_diags_data/obs_for_e3sm_diags/time-series'
  dc_obs_climo = '/lcrc/group/e3sm/public_html/e3sm_diags_test_data/unit_test_complete_run/obs/climatology'
  output_format_subplot = "pdf",

[global_time_series]
active = True
atmosphere_only = True
years = "{yr1}-{yr2}", 
ts_num_years = {ts_nyr}
figstr = "{short_name}"
experiment_name = "{case_name}"
ts_years = "{yr1}-{yr2}",
climo_years = "{yr1}-{yr2}",

'''
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':

   # run_cmd(f'source {unified_env}')

   for c in range(len(case_list)):
      # print('-'*80)
      main( case_list[c], scratch_list[c] )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
