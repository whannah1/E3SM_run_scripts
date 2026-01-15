#!/usr/bin/env python
import os, datetime, subprocess as sp
#---------------------------------------------------------------------------------------------------
class tcolor: END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
#---------------------------------------------------------------------------------------------------
def run_cmd(cmd,suppress_output=False):
   if suppress_output : cmd = cmd + ' > /dev/null'
   msg = tcolor.GREEN + cmd + tcolor.END ; print(f'\n{msg}')
   os.system(cmd); return
#---------------------------------------------------------------------------------------------------
opt_list = []
def add_case( **kwargs ):
   case_opts = {}
   for k, val in kwargs.items(): case_opts[k] = val
   opt_list.append(case_opts)
#---------------------------------------------------------------------------------------------------
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm4842'
# src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC0' # branch => whannah/emaxx/add-p3-cld-frac-flags-merge
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC0' # branch => whannah/2025-SOHIP (master @ 2025-7-1)

# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
# continue_run = True

queue,stop_opt,stop_n,resub,walltime = 'regular','ndays',1,0,'1:00:00'

arch = 'GPU'
compset = 'F2010-SCREAMv1'

#---------------------------------------------------------------------------------------------------
# specify initialization date

init_scratch = '/global/cfs/projectdirs/m4842/whannah/HICCUP'
init_file_sst = f'{init_scratch}/HICCUP.sst_noaa.2023.nc'

#---------------------------------------------------------------------------------------------------
# build list of cases to run

vert_file_L256 = '/global/homes/w/whannah/E3SM/vert_grid_files/SOHIP_L256_v3_c20250414.nc'

# add_case(prefix='2025-SOHIP-RRM-00', grid='2025-sohip-256x2-ptgnia-v1', init_date='2023-06-13', init_hour='19' )
# add_case(prefix='2025-SOHIP-RRM-00', grid='2025-sohip-256x2-sw-ind-v1', init_date='2023-06-12', init_hour='06' )
# add_case(prefix='2025-SOHIP-RRM-00', grid='2025-sohip-256x2-se-pac-v1', init_date='2023-06-12', init_hour='16' )
# add_case(prefix='2025-SOHIP-RRM-00', grid='2025-sohip-256x2-sc-pac-v1', init_date='2023-06-14', init_hour='15' )
add_case(prefix='2025-SOHIP-RRM-00', grid='2025-sohip-256x2-eq-ind-v1', init_date='2023-06-19', init_hour='09', num_nodes=420 )
add_case(prefix='2025-SOHIP-RRM-00', grid='2025-sohip-256x2-eq-ind-v1', init_date='2023-06-21', init_hour='02', num_nodes=420 )
# add_case(prefix='2025-SOHIP-RRM-00', grid='2025-sohip-256x2-sc-ind-v1', init_date='2023-06-21', init_hour='09' )

# add_case(prefix='2025-SOHIP-RRM-00', grid='2025-sohip-256x3-ptgnia-v1', init_date='2023-06-13', init_hour='19' )
# add_case(prefix='2025-SOHIP-RRM-00', grid='2025-sohip-256x3-sw-ind-v1', init_date='2023-06-12', init_hour='06' )
# add_case(prefix='2025-SOHIP-RRM-00', grid='2025-sohip-256x3-se-pac-v1', init_date='2023-06-12', init_hour='16' )
# add_case(prefix='2025-SOHIP-RRM-00', grid='2025-sohip-256x3-sc-pac-v1', init_date='2023-06-14', init_hour='15' )
# add_case(prefix='2025-SOHIP-RRM-00', grid='2025-sohip-256x3-eq-ind-v1', init_date='2023-06-19', init_hour='09' )
# add_case(prefix='2025-SOHIP-RRM-00', grid='2025-sohip-256x3-eq-ind-v1', init_date='2023-06-21', init_hour='02' )
# add_case(prefix='2025-SOHIP-RRM-00', grid='2025-sohip-256x3-sc-ind-v1', init_date='2023-06-21', init_hour='09' )

#---------------------------------------------------------------------------------------------------
''' available init files:
/global/cfs/cdirs/m4842/whannah/files_init/HICCUP.atm_era5.2023-06-13.19.2025-sohip-256x3-ptgnia-v1.L256.nc
/global/cfs/cdirs/m4842/whannah/files_init/HICCUP.atm_era5.2023-06-12.06.2025-sohip-256x3-sw-ind-v1.L256.nc
/global/cfs/cdirs/m4842/whannah/files_init/HICCUP.atm_era5.2023-06-12.16.2025-sohip-256x3-se-pac-v1.L256.nc
/global/cfs/cdirs/m4842/whannah/files_init/HICCUP.atm_era5.2023-06-14.15.2025-sohip-256x3-sc-pac-v1.L256.nc
/global/cfs/cdirs/m4842/whannah/files_init/HICCUP.atm_era5.2023-06-19.09.2025-sohip-256x3-eq-ind-v1.L256.nc
/global/cfs/cdirs/m4842/whannah/files_init/HICCUP.atm_era5.2023-06-21.02.2025-sohip-256x3-eq-ind-v1.L256.nc
/global/cfs/cdirs/m4842/whannah/files_init/HICCUP.atm_era5.2023-06-21.09.2025-sohip-256x3-sc-ind-v1.L256.nc
'''
#---------------------------------------------------------------------------------------------------
# init_file_atm = f'{init_scratch}/HICCUP.atm_era5.{init_date.strftime("%Y-%m-%d")}.ne256np4.L256.nc'
def get_init_file_atm(opts):
   global init_scratch#,init_date
   init_file_atm = None
   # if 'ne256pg2_'  in opts['grid']: init_file_atm = f'{init_scratch}/HICCUP.atm_era5.{init_date.strftime("%Y-%m-%d")}.ne256np4.L256.nc'
   # if 'ne1024pg2_' in opts['grid']: init_file_atm = f'{init_scratch}/HICCUP.atm_era5.{init_date.strftime("%Y-%m-%d")}.ne1024np4.L256.nc'
   init_root = '/global/cfs/cdirs/m4842/whannah/files_init'
   init_file_atm = f'{init_root}/HICCUP.atm_era5.{opts["init_date"]}.{opts["init_hour"]}.{opts["grid"]}.L256.nc'
   if init_file_atm is None: raise ValueError(f'ERROR: get_init_file_atm: init_file_atm not found for grid {opts["grid"]} ')
   return init_file_atm
#---------------------------------------------------------------------------------------------------
def get_grid_name(opts):
   grid_name = opts['grid']
   if 'ne4pg2_'    in opts['grid']: grid_name = 'ne4pg2'
   if 'ne30pg2_'   in opts['grid']: grid_name = 'ne30pg2'
   if 'ne120pg2_'  in opts['grid']: grid_name = 'ne120pg2'
   if 'ne256pg2_'  in opts['grid']: grid_name = 'ne256pg2'
   if 'ne1024pg2_' in opts['grid']: grid_name = 'ne1024pg2'
   if '2025-sohip' in opts['grid']: grid_name = opts['grid'].replace('2025-sohip-','')
   return grid_name
#---------------------------------------------------------------------------------------------------
def get_case_name(opts):
   case_list = []
   for key,val in opts.items(): 
      if   key in ['prefix']:    case_list.append(val)
      elif key in ['compset']:   case_list.append(val)
      elif key in ['grid']:      case_list.append(get_grid_name(opts))
      elif key in ['init_date']: case_list.append(val)
      elif key in ['init_hour']: case_list.append(val)
      elif key in ['num_nodes']: case_list.append(f'NN_{val}')
      else:
         if isinstance(val,str): case_list.append(f'{key}_{val}')
         else:                   case_list.append(f'{key}_{val:g}')
   case = '.'.join(case_list)
   for i in range(1,9+1): case = case.replace(f'e+0{i}',f'e{i}') # clean up the exponential numbers
   return case
#---------------------------------------------------------------------------------------------------
def main(opts):

   case = get_case_name(opts)

   print(f'\n  case : {case}\n')

   #------------------------------------------------------------------------------------------------
   # return
   #------------------------------------------------------------------------------------------------
   grid    = opts['grid']
   # compset = opts['compset']
   init_date = datetime.datetime.strptime(opts['init_date']+' '+opts['init_hour'], '%Y-%m-%d %H')
   init_time_of_day = int(opts['init_hour'])*3600.
   #------------------------------------------------------------------------------------------------
   if 'num_nodes' in opts:
      num_nodes = opts['num_nodes']
   else:
      if '256x2' in opts['grid']: num_nodes = 384
      if '256x3' in opts['grid']: num_nodes = 512
   #------------------------------------------------------------------------------------------------
   debug_mode = False
   if 'debug' in opts: debug_mode = opts['debug']

   if arch=='GPU': case_root = os.getenv('SCRATCH')+f'/scream_scratch/pm-gpu/{case}'
   if arch=='CPU': case_root = os.getenv('SCRATCH')+f'/scream_scratch/pm-cpu/{case}'
   
   if 'CPU' in arch: max_mpi_per_node,atm_nthrds  = 128,1 ; max_task_per_node = 128
   if 'GPU' in arch: max_mpi_per_node,atm_nthrds  =   4,8 ; max_task_per_node = 32
   atm_ntasks = max_mpi_per_node*num_nodes
   #------------------------------------------------------------------------------------------------
   # Create new case
   if newcase :
      if os.path.isdir(case_root): exit(f'\n{tcolor.RED}This case already exists!{tcolor.END}\n')
      cmd = f'{src_dir}/cime/scripts/create_newcase'
      cmd += f' --case {case}'
      cmd += f' --output-root {case_root} '
      cmd += f' --script-root {case_root}/case_scripts '
      cmd += f' --handle-preexisting-dirs u '
      cmd += f' --compset {compset}'
      cmd += f' --res {grid} '
      cmd += f' --project {acct} '
      if arch=='GPU': cmd += f' -mach pm-gpu -compiler gnugpu '
      if arch=='CPU': cmd += f' -mach pm-cpu -compiler gnu '
      cmd += f' -pecount {atm_ntasks}x{atm_nthrds} '
      run_cmd(cmd)
      #----------------------------------------------------------------------------
      # # Copy this run script into the case directory
      # timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
      # run_cmd(f'cp {os.path.realpath(__file__)} {case_dir}/{case}/run_script.{timestamp}.py')
   #------------------------------------------------------------------------------------------------
   os.chdir(f'{case_root}/case_scripts')
   #------------------------------------------------------------------------------------------------
   if config : 
      run_cmd(f'./xmlchange EXEROOT={case_root}/bld ')
      run_cmd(f'./xmlchange RUNDIR={case_root}/run ')
      #-------------------------------------------------------------------------
      # run_cmd(f'./xmlchange SCREAM_CMAKE_OPTIONS="SCREAM_NUM_VERTICAL_LEV 256" ')
      run_cmd(f'./xmlchange --append --id SCREAM_CMAKE_OPTIONS --val \" SCREAM_NUM_VERTICAL_LEV 256 \"')
      #-------------------------------------------------------------------------
      # if clean : run_cmd('./case.setup --clean')
      run_cmd('./case.setup --reset')
   #------------------------------------------------------------------------------------------------
   if build : 
      if debug_mode: run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
      if clean : run_cmd('./case.build --clean-all')
      run_cmd('./case.build')
   #------------------------------------------------------------------------------------------------
   if submit:
      #-------------------------------------------------------------------------
      if 'rfrac_fix' in opts:
         if opts['rfrac_fix']:
            run_cmd('./atmchange set_cld_frac_r_to_one=true')
         else:
            run_cmd('./atmchange set_cld_frac_r_to_one=false')

      #-------------------------------------------------------------------------
      hist_file_list = []
      def add_hist_file(hist_file,txt):
         file=open(hist_file,'w'); file.write(txt); file.close()
         hist_file_list.append(hist_file)
      #-------------------------------------------------------------------------
      add_hist_file(f'{case_root}/case_scripts/scream_output_2D_10min_inst.yaml',hist_opts_2D_10min_inst)
      add_hist_file(f'{case_root}/case_scripts/scream_output_3D_10min_inst.yaml',hist_opts_3D_10min_inst)
      hist_file_list_str = ','.join(hist_file_list)
      run_cmd(f'./atmchange scorpio::output_yaml_files="{hist_file_list_str}"')
      #----------------------------------------------------------------------------
      # Specify start date and SST file for hindcast
      sst_yr = int(init_date.strftime('%Y'))
      init_file_atm = get_init_file_atm(opts)
      run_cmd(f'./atmchange initial_conditions::filename=\"{init_file_atm}\"')
      run_cmd(f'./atmchange grids_manager::vertical_coordinate_filename=\"{vert_file_L256}\"')
      run_cmd(f'./xmlchange --file env_run.xml  RUN_STARTDATE={init_date.strftime("%Y-%m-%d")}')
      run_cmd(f'./xmlchange --file env_run.xml  START_TOD={init_time_of_day}')
      run_cmd(f'./atmchange orbital_year={init_date.strftime("%Y")}')
      run_cmd(f'./xmlchange --file env_run.xml  SSTICE_DATA_FILENAME={init_file_sst}')
      run_cmd(f'./xmlchange --file env_run.xml  SSTICE_YEAR_ALIGN={sst_yr}')
      run_cmd(f'./xmlchange --file env_run.xml  SSTICE_YEAR_START={sst_yr}')
      run_cmd(f'./xmlchange --file env_run.xml  SSTICE_YEAR_END={sst_yr+1}')
      #-------------------------------------------------------------------------
      sst_grid_file = '/global/cfs/cdirs/e3sm/inputdata/ocn/docn7/domain.ocn.1440x720.250319.nc'
      run_cmd(f'./xmlchange --file env_run.xml --id SSTICE_GRID_FILENAME --val {sst_grid_file}')
      #-------------------------------------------------------------------------
      # Set some run-time stuff
      # run_cmd(f'./xmlchange ATM_NCPL={int(86400/dtime)}')
      if 'stop_opt' in globals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
      if 'stop_n'   in globals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
      if 'resub'    in globals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
      if 'queue'    in globals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
      if 'walltime' in globals(): run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
      run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')
      if     continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=TRUE ')   
      if not continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=FALSE ')
      #-------------------------------------------------------------------------
      # Submit the run
      run_cmd('./case.submit')
   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {case}\n') 
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

hist_opts_2D_10min_inst = f'''
%YAML 1.1
---
filename_prefix: output.scream.2D.10min
averaging_type: instant
max_snapshots_per_file: 12
fields:
   physics_pg2:
      field_names:
         - ps
         - precip_total_surf_mass_flux
         - VapWaterPath
         - LiqWaterPath
         - IceWaterPath
         - surf_sens_flux
         - surface_upward_latent_heat_flux
         - wind_speed_10m
         - SW_flux_up_at_model_top
         - SW_flux_dn_at_model_top
         - LW_flux_up_at_model_top
output_control:
   frequency: 10
   frequency_units: nmins
restart:
   force_new_file: true
'''


#       - surf_evap
#       - surf_mom_flux
#       - horiz_winds_at_model_bot
#       - SW_flux_dn_at_model_bot
#       - SW_flux_up_at_model_bot
#       - LW_flux_dn_at_model_bot
#       - LW_flux_up_at_model_bot
#       - SW_flux_up_at_model_top
#       - SW_flux_dn_at_model_top
#       - LW_flux_up_at_model_top


hist_opts_3D_10min_inst = f'''
%YAML 1.1
---
filename_prefix: output.scream.3D.10min
averaging_type: instant
max_snapshots_per_file: 12
fields:
   physics_pg2:
      field_names:
         - ps
         - omega
         - horiz_winds
         - qv
         - T_mid
         - z_mid
output_control:
   frequency: 10
   frequency_units: nmins
restart:
   force_new_file: true
'''

# - qc
# - qr
# - qi
# - qm
# - nc
# - nr
# - ni
# - bm
# - RelativeHumidity
# - rad_heating_pdel

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':
   for n in range(len(opt_list)):
      main( opt_list[n] )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
