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
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC0' # branch => whannah/emaxx/add-p3-cld-frac-flags-merge

# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
# continue_run = True

debug_mode = False

queue,stop_opt,stop_n,resub,walltime = 'regular','ndays',1,0,'0:30:00'

arch = 'GPU'

#---------------------------------------------------------------------------------------------------
# specify initialization date

# init_date = datetime.datetime.strptime('2023-09-08 00', '%Y-%m-%d %H')
init_date = datetime.datetime.strptime('2023-06-14 00', '%Y-%m-%d %H')


init_scratch = '/global/cfs/projectdirs/m4842/whannah/HICCUP'
init_file_sst = f'{init_scratch}/HICCUP.sst_noaa.{init_date.strftime("%Y-%m-%d")}.nc'
# init_file_atm = f'{init_scratch}/HICCUP.atm_era5.{init_date.strftime("%Y-%m-%d")}.ne256np4.L256.nc'


init_file_atm = f'{init_scratch}/HICCUP.atm_era5.{init_date.strftime("%Y-%m-%d")}.ne256np4.L256.nc'


#---------------------------------------------------------------------------------------------------
# build list of cases to run

vert_file_L256 = '/global/homes/w/whannah/E3SM/vert_grid_files/SOHIP_L256_v3_c20250414.nc'

# add_case(prefix='2025-SOHIP-00', compset='F2010-SCREAMv1', grid='ne256pg2_ne256pg2', num_nodes=192, init=init_date.strftime('%Y-%m-%d') ) # not enough nodes?
# add_case(prefix='2025-SOHIP-00', compset='F2010-SCREAMv1', grid='ne256pg2_ne256pg2', num_nodes=384, init=init_date.strftime('%Y-%m-%d') )

add_case(prefix='2025-SOHIP-00', compset='F2010-SCREAMv1', grid='ne1024pg2_ne1024pg2', num_nodes=1536, init=init_date.strftime('%Y-%m-%d') )

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def get_grid_name(opts):
   grid_name = opts['grid']
   if 'ne4pg2_'    in opts['grid']: grid_name = 'ne4pg2'
   if 'ne30pg2_'   in opts['grid']: grid_name = 'ne30pg2'
   if 'ne120pg2_'  in opts['grid']: grid_name = 'ne120pg2'
   if 'ne256pg2_'  in opts['grid']: grid_name = 'ne256pg2'
   if 'ne1024pg2_' in opts['grid']: grid_name = 'ne1024pg2'
   return grid_name
#---------------------------------------------------------------------------------------------------
def get_case_name(opts):
   case_list = ['SCREAM']
   for key,val in opts.items(): 
      if key in ['prefix','compset']:
         case_list.append(val)
      elif key in ['grid']: 
         case_list.append(get_grid_name(opts))
      elif key in ['num_nodes']:
         case_list.append(f'NN_{val}')
      else:
         if isinstance(val, str):
            case_list.append(f'{key}_{val}')
         else:
            case_list.append(f'{key}_{val:g}')
   case = '.'.join(case_list)
   # clean up the exponential numbers in the case name
   for i in range(1,9+1): case = case.replace(f'e+0{i}',f'e{i}')
   return case
#---------------------------------------------------------------------------------------------------
def main(opts):

   case = get_case_name(opts)

   print(f'\n  case : {case}\n')

   #------------------------------------------------------------------------------------------------
   # exit()
   #------------------------------------------------------------------------------------------------
   if arch=='GPU': case_root = os.getenv('SCRATCH')+f'/scream_scratch/pm-gpu/{case}'
   if arch=='CPU': case_root = os.getenv('SCRATCH')+f'/scream_scratch/pm-cpu/{case}'

   num_nodes = opts['num_nodes']
   if 'CPU' in arch: max_mpi_per_node,atm_nthrds  = 128,1 ; max_task_per_node = 128
   if 'GPU' in arch: max_mpi_per_node,atm_nthrds  =   4,8 ; max_task_per_node = 32
   atm_ntasks = max_mpi_per_node*num_nodes

   grid    = opts['grid']+'_'+opts['grid']
   compset = opts['compset']
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
      if clean : run_cmd('./case.setup --clean')
      run_cmd('./case.setup --reset')
   #------------------------------------------------------------------------------------------------
   if build : 
      if debug_mode: run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
      if clean : run_cmd('./case.build --clean')
      run_cmd('./case.build')
   #------------------------------------------------------------------------------------------------
   if submit : 
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
      run_cmd(f'./atmchange initial_conditions::filename=\"{init_file_atm}\"')
      run_cmd(f'./atmchange grids_manager::vertical_coordinate_filename=\"{vert_file_L256}\"')
      run_cmd(f'./xmlchange --file env_run.xml  RUN_STARTDATE={init_date.strftime("%Y-%m-%d")}')
      run_cmd(f'./atmchange orbital_year={init_date.strftime("%Y")}')
      run_cmd(f'./xmlchange --file env_run.xml  SSTICE_DATA_FILENAME={init_file_sst}')
      run_cmd(f'./xmlchange --file env_run.xml  SSTICE_YEAR_ALIGN={sst_yr}')
      run_cmd(f'./xmlchange --file env_run.xml  SSTICE_YEAR_START={sst_yr}')
      run_cmd(f'./xmlchange --file env_run.xml  SSTICE_YEAR_END={sst_yr+1}')
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
