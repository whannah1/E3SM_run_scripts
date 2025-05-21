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
class clr:END,RED,GREEN,YELLOW,MAGENTA,CYAN,BOLD = '\033[0m','\033[31m','\033[32m','\033[33m','\033[35m','\033[36m','\033[1m'
unified_env = '/global/common/software/e3sm/anaconda_envs/load_latest_e3sm_unified_pm-cpu.sh'
def print_line():print(' '*2+'-'*80)
def run_cmd(cmd): 
   print('\n'+clr.GREEN+cmd+clr.END);
   os.system(cmd); 
   return
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp, glob, datetime
run_zppy,clear_zppy_status,check_zppy_status,st_archive,lt_archive_create,lt_archive_update,cp_post_to_cfs = False,False,False,False,False,False,False

acct = 'm4310'

# st_archive        = True
# clear_zppy_status = True
# check_zppy_status = True
# run_zppy          = True
# lt_archive_create = True
# lt_archive_update = True
# cp_post_to_cfs    = True
delete_data       = True

gweff_list = []
cfrac_list = []
hdpth_list = []

gweff_list.append(0.35); cfrac_list.append(10); hdpth_list.append(1.00) #  0 - use defaults
gweff_list.append(0.10); cfrac_list.append(10); hdpth_list.append(1.50) #  2 L72-run # 16
gweff_list.append(0.35); cfrac_list.append(20); hdpth_list.append(1.00) #  3 L72-run #  3
gweff_list.append(0.20); cfrac_list.append(20); hdpth_list.append(1.50) #  4 L72-run # 17
gweff_list.append(0.10); cfrac_list.append(25); hdpth_list.append(0.25) #  5 L72-run # 25

gweff_list.append(0.20); cfrac_list.append(25); hdpth_list.append(0.50) #  6 L72-run # 22
gweff_list.append(0.35); cfrac_list.append(10); hdpth_list.append(0.50) #  7 L72-run #  5 <<< new v3 default
gweff_list.append(0.35); cfrac_list.append(10); hdpth_list.append(0.25) #  8 L72-run #  2
gweff_list.append(0.20); cfrac_list.append(10); hdpth_list.append(1.00) #  9 L72-run #  4
gweff_list.append(0.20); cfrac_list.append(15); hdpth_list.append(0.50) # 10 L72-run #  7

gweff_list.append(0.09); cfrac_list.append(20); hdpth_list.append(0.25) # 11 L72-run # 10  
gweff_list.append(0.20); cfrac_list.append(20); hdpth_list.append(1.25) # 12 L72-run # 18  
gweff_list.append(0.05); cfrac_list.append(25); hdpth_list.append(0.50) # 13 L72-run # 12  
gweff_list.append(0.80); cfrac_list.append( 1); hdpth_list.append(1.15) # 14 L72-run # 31  
gweff_list.append(0.90); cfrac_list.append(20); hdpth_list.append(0.25) # 15 L72-run # 14 

gweff_list.append(0.59); cfrac_list.append(41); hdpth_list.append(0.55) # 16 L72-run # 40  
gweff_list.append(0.01); cfrac_list.append( 1); hdpth_list.append(0.70) # 17 L72-run # 28  
gweff_list.append(0.40); cfrac_list.append(10); hdpth_list.append(1.00) # 18 L72-run #  1  
gweff_list.append(0.70); cfrac_list.append(25); hdpth_list.append(0.90) # 19 L72-run # 30  
gweff_list.append(0.60); cfrac_list.append( 7); hdpth_list.append(1.35) # 20 L72-run # 38  

gweff_list.append(0.10); cfrac_list.append(30); hdpth_list.append(0.63) #  1 L72-run # 44 - outlier - can't finish?

### additional 6 cases following initial ensemble
gweff_list.append(0.18); cfrac_list.append(14); hdpth_list.append(0.52)
gweff_list.append(0.35); cfrac_list.append(11); hdpth_list.append(0.66)
gweff_list.append(0.06); cfrac_list.append(13); hdpth_list.append(0.59)
gweff_list.append(0.22); cfrac_list.append( 8); hdpth_list.append(0.48)
gweff_list.append(0.52); cfrac_list.append(16); hdpth_list.append(0.89)
gweff_list.append(0.13); cfrac_list.append(10); hdpth_list.append(0.82)

### new runs to extend ensemble (2024)
gweff_list.append(0.79); cfrac_list.append(12); hdpth_list.append(0.72)
gweff_list.append(0.78); cfrac_list.append(13); hdpth_list.append(0.67)
gweff_list.append(0.77); cfrac_list.append( 9); hdpth_list.append(0.94)
gweff_list.append(0.55); cfrac_list.append(10); hdpth_list.append(0.38)
gweff_list.append(0.63); cfrac_list.append( 8); hdpth_list.append(0.62)
gweff_list.append(0.14); cfrac_list.append(10); hdpth_list.append(1.37)
gweff_list.append(0.13); cfrac_list.append(22); hdpth_list.append(0.56)

### new runs to extend ensemble - 2024-05-02
gweff_list.append(0.31); cfrac_list.append(0.11); hdpth_list.append(1.39)
gweff_list.append(0.70); cfrac_list.append(0.21); hdpth_list.append(0.31)
gweff_list.append(0.81); cfrac_list.append(0.20); hdpth_list.append(0.39)
gweff_list.append(0.11); cfrac_list.append(0.18); hdpth_list.append(0.87)
gweff_list.append(0.11); cfrac_list.append(0.23); hdpth_list.append(0.86)
gweff_list.append(0.13); cfrac_list.append(0.16); hdpth_list.append(1.22)
gweff_list.append(0.33); cfrac_list.append(0.17); hdpth_list.append(0.72)
gweff_list.append(0.40); cfrac_list.append(0.15); hdpth_list.append(1.17)
gweff_list.append(0.43); cfrac_list.append(0.23); hdpth_list.append(0.60)
gweff_list.append(0.45); cfrac_list.append(0.20); hdpth_list.append(1.40)
gweff_list.append(0.47); cfrac_list.append(0.17); hdpth_list.append(0.46)
gweff_list.append(0.60); cfrac_list.append(0.12); hdpth_list.append(1.03)
gweff_list.append(0.60); cfrac_list.append(0.15); hdpth_list.append(1.35)
gweff_list.append(0.63); cfrac_list.append(0.22); hdpth_list.append(0.78)
gweff_list.append(0.67); cfrac_list.append(0.22); hdpth_list.append(1.18)
gweff_list.append(0.69); cfrac_list.append(0.17); hdpth_list.append(0.64)
gweff_list.append(0.77); cfrac_list.append(0.18); hdpth_list.append(0.93)
gweff_list.append(0.86); cfrac_list.append(0.17); hdpth_list.append(0.29)

### relaunch after noticing error in CF values

gweff_list.append(0.31); cfrac_list.append(11); hdpth_list.append(1.39)
gweff_list.append(0.70); cfrac_list.append(21); hdpth_list.append(0.31)
gweff_list.append(0.81); cfrac_list.append(20); hdpth_list.append(0.39)
gweff_list.append(0.11); cfrac_list.append(18); hdpth_list.append(0.87)
gweff_list.append(0.11); cfrac_list.append(23); hdpth_list.append(0.86)

gweff_list.append(0.13); cfrac_list.append(16); hdpth_list.append(1.22)
gweff_list.append(0.33); cfrac_list.append(17); hdpth_list.append(0.72)
gweff_list.append(0.40); cfrac_list.append(15); hdpth_list.append(1.17)
gweff_list.append(0.43); cfrac_list.append(23); hdpth_list.append(0.60)
gweff_list.append(0.47); cfrac_list.append(17); hdpth_list.append(0.46)

gweff_list.append(0.60); cfrac_list.append(15); hdpth_list.append(1.35)
gweff_list.append(0.63); cfrac_list.append(22); hdpth_list.append(0.78)
gweff_list.append(0.67); cfrac_list.append(22); hdpth_list.append(1.18)
gweff_list.append(0.69); cfrac_list.append(17); hdpth_list.append(0.64)
gweff_list.append(0.77); cfrac_list.append(18); hdpth_list.append(0.93)

gweff_list.append(0.86); cfrac_list.append(17); hdpth_list.append(0.29)
gweff_list.append(0.45); cfrac_list.append(20); hdpth_list.append(1.40)
gweff_list.append(0.60); cfrac_list.append(12); hdpth_list.append(1.03)

### new ensemble extension - 2024-07-09
gweff_list.append(0.12); cfrac_list.append(16); hdpth_list.append(0.48)
gweff_list.append(0.04); cfrac_list.append(20); hdpth_list.append(0.75)


#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def main(e=None,c=None,h=None):
   if h is None or c is None or e is None: exit(' one or more arguments not provided?')

   case = '.'.join(['E3SM','2023-SCIDAC','ne30pg2_EC30to60E2r2','AMIP',f'EF_{e:0.2f}',f'CF_{c:02.0f}',f'HD_{h:0.2f}'])
   case_root = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/{case}'

   # print(case); return

   #------------------------------------------------------------------------------------------------
   #------------------------------------------------------------------------------------------------
   print_line()
   print(f'  case : {clr.BOLD}{case}{clr.END} \n')
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
   if clear_zppy_status:
      status_files = glob.glob(f'{case_root}/post/scripts/*status')
      for file_name in status_files:
         os.remove(file_name)
   #------------------------------------------------------------------------------------------------
   if check_zppy_status:
      status_path = f'{case_root}/post/scripts'
      print(' '*4+clr.END+status_path+clr.END)
      status_files = glob.glob(f'{status_path}/*status')
      max_len = 0
      for file_path in status_files:
         file_name = file_path.replace(f'{status_path}/','')
         max_len = max(len(file_name),max_len)
      for file_path in status_files:
         file_name = file_path.replace(f'{status_path}/','')
         cmd = f'tail {file_path} '
         proc = sp.Popen([cmd], stdout=sp.PIPE, shell=True, universal_newlines=True)
         (msg, err) = proc.communicate()
         msg = msg.strip()
         msg = msg.replace('ERROR',f'{clr.RED}ERROR{clr.END}')
         msg = msg.replace('WAITING',f'{clr.YELLOW}WAITING{clr.END}')
         msg = msg.replace('RUNNING',f'{clr.YELLOW}RUNNING{clr.END}')
         msg = msg.replace('OK',f'{clr.GREEN}OK{clr.END}')
         print(' '*6+f'{clr.CYAN}{file_name:{max_len}}{clr.END} : {msg}')
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
   if lt_archive_create:
      os.chdir(f'{case_root}')
      timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
      # Create the HPSS archive
      run_cmd(f'source {unified_env}; zstash create --hpss=E3SM/2023-SciDAC-L80/{case} . 2>&1 | tee zstash_create_{case}_{timestamp}.log')
   #------------------------------------------------------------------------------------------------
   if lt_archive_update:
      print(f'\n{clr.GREEN}cd {case_root}{clr.END}');
      os.chdir(f'{case_root}')
      timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
      run_cmd(f'source {unified_env}; zstash update --hpss=E3SM/2023-SciDAC-L80/{case}  2>&1 | tee zstash_update_{case}_{timestamp}.log')
   #------------------------------------------------------------------------------------------------
   if cp_post_to_cfs:
      # os.umask(511)
      dst_root = '/global/cfs/cdirs/m4310/whannah/E3SM/2023-SciDAC-L80'
      src_dir = f'{case_root}/post/atm/180x360/ts/monthly/10yr'
      dst_dir = f'{dst_root}/{case}'
      if not os.path.exists(dst_root): os.mkdir(dst_root)
      if not os.path.exists(dst_dir):  os.mkdir(dst_dir)
      run_cmd(f'cp {src_dir}/U_* {dst_dir}/')
   #------------------------------------------------------------------------------------------------
   if delete_data:
      file_list = []
      file_list += glob.glob(f'{case_root}/post/atm/180x360/ts/monthly/10yr/*.nc')
      file_list += glob.glob(f'{case_root}/post/atm/180x360/clim/monthly/10yr/*.nc')
      file_list += glob.glob(f'{case_root}/post/atm/180x360/clim/10yr/*.nc')
      file_list += glob.glob(f'{case_root}/post/atm/90x180/ts/monthly/10yr/*.nc')
      file_list += glob.glob(f'{case_root}/post/atm/90x180/clim/monthly/10yr/*.nc')
      file_list += glob.glob(f'{case_root}/post/atm/90x180/clim/10yr/*.nc')
      file_list += glob.glob(f'{case_root}/post/atm/glb/ts/monthly/10yr/*.nc')
      file_list += glob.glob(f'{case_root}/archive/*/hist/*.nc')
      file_list += glob.glob(f'{case_root}/archive/rest/*/*.nc')
      file_list += glob.glob(f'{case_root}/run/*.nc')
      # if len(file_list)>10:
      #    print()
      #    for f in file_list: print(f)
      #    print()
      #    exit()
      if len(file_list)>0: 
         print(f'  {clr.RED}deleting {(len(file_list))} files{clr.END}')
         for f in file_list:
            os.remove(f)
   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {clr.BOLD}{case}{clr.END} ')
#---------------------------------------------------------------------------------------------------

#---------------------------------------------------------------------------------------------------
def get_zppy_config(case_name,case_root):
   short_name = case_name
   # grid,map_file = '90x180','/global/homes/w/whannah/maps/map_ne30pg2_to_90x180_aave.nc'
   grid,map_file = '180x360','/global/homes/w/whannah/maps/map_ne30pg2_to_180x360_aave.nc'
   # grid,map_file = '180x360','/global/homes/z/zender/data/maps/map_ne30pg2_to_cmip6_180x360_aave.20200201.nc'
   yr1,yr2,nyr,ts_nyr = 1984,1993,10,10
   # yr1,yr2,nyr,ts_nyr = 1984,2003,20,20
   return f'''
[default]
account = {acct}
input = {case_root}
output = {case_root}
case = {case_name}
www = /global/cfs/cdirs/e3sm/www/whannah/2023-SciDAC
machine = "pm-cpu"
partition = batch
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
  reference_data_path = '/global/cfs/cdirs/e3sm/diagnostics/observations/Atm/climatology'
  obs_ts = '/global/cfs/cdirs/e3sm/diagnostics/observations/Atm/time-series'
  dc_obs_climo = '/global/cfs/cdirs/e3sm/e3sm_diags/test_model_data_for_acme_diags/climatology/'
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

   for n in range(len(hdpth_list)):
      # print('-'*80)
      main( e=gweff_list[n], c=cfrac_list[n], h=hdpth_list[n] )
   print_line()
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
