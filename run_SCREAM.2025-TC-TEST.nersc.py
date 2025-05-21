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

acct = 'm3312'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC0' # branch => whannah/emaxx/add-p3-cld-frac-flags-merge

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

debug_mode = False

queue,stop_opt,stop_n,resub,walltime = 'regular','ndays',40,0,'4:00:00'

arch = 'GPU'

#---------------------------------------------------------------------------------------------------
# build list of cases to run

add_case(prefix='2025-PC-00', compset='F2010-SCREAMv1', grid='ne256pg2', num_nodes=192) # control

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def main(opts):

   case_list = ['SCREAM']
   for key,val in opts.items(): 
      if key in ['prefix','grid','compset']:
         case_list.append(val)
      elif key in ['num_nodes']:
         continue
      else:
         case_list.append(f'{key}_{val:g}')
         # case_list.append(f'{key}_{val}')
   case = '.'.join(case_list)

   # clean up the exponential numbers in the case name
   for i in range(1,9+1): case = case.replace(f'e+0{i}',f'e{i}')

   print(f'\n  case : {case}\n')

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
      # if init_file is not None: run_cmd(f'./atmchange initial_conditions::Filename=\"{init_file}\"')
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
      add_hist_file('scream_output_2D_1hr_inst.yaml',hist_opts_2D_1hr_inst)
      add_hist_file('scream_output_3D_1dy_mean.yaml',hist_opts_3D_1dy_mean)
      hist_file_list_str = ','.join(hist_file_list)
      run_cmd(f'./atmchange Scorpio::output_yaml_files="{hist_file_list_str}"')
      #-----------------------------------------------------------------------------
      if compset == 'F2010-SCREAMv1-DYAMOND1':
         start_date = '2016-08-01'
         start_year = int(start_date.split('-')[0])
         run_cmd(f'./xmlchange --file env_run.xml RUN_STARTDATE={start_date}')
         run_cmd(f'./atmchange orbital_year={start_year}')
      #-------------------------------------------------------------------------
      # if init_file is not None: 
      #    run_cmd(f'./atmchange initial_conditions::Filename=\"{init_file}\"')
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
field_txt_2D = '''
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
'''

# field_txt_2D = '''
#       - ps
#       - precip_total_surf_mass_flux
#       - VapWaterPath
#       - LiqWaterPath
#       - IceWaterPath
#       - surf_sens_flux
#       - surf_evap
#       - surface_upward_latent_heat_flux
#       - surf_mom_flux
#       - wind_speed_10m
#       - horiz_winds_at_model_bot
#       - SW_flux_dn_at_model_bot
#       - SW_flux_up_at_model_bot
#       - LW_flux_dn_at_model_bot
#       - LW_flux_up_at_model_bot
#       - SW_flux_up_at_model_top
#       - SW_flux_dn_at_model_top
#       - LW_flux_up_at_model_top
# '''

field_txt_3D = '''
      - ps
      - omega
      - horiz_winds
      - qv
      - qc
      - qr
      - qi
      - qm
      - nc
      - nr
      - ni
      - bm
      - T_mid
      - z_mid
      - RelativeHumidity
      - rad_heating_pdel
'''

# the P3 process tendency fields were not available in this branch
# P3_qr2qv_evap

hist_opts_2D_15min_inst = f'''
%YAML 1.1
---
filename_prefix: output.scream.2D.15min
Averaging Type: Instant
Max Snapshots Per File: 96
Fields:
   Physics PG2:
      Field Names:{field_txt_2D}
output_control:
   Frequency: 1
   frequency_units: nhours
   MPI Ranks in Filename: false
Restart:
   force_new_file: true
'''

# hist_opts_2D_1hr_inst = f'''
# %YAML 1.1
# ---
# filename_prefix: output.scream.2D.1hr
# Averaging Type: Instant
# Max Snapshots Per File: 24
# Fields:
#    Physics PG2:
#       Field Names:{field_txt_2D}
# output_control:
#    Frequency: 1
#    frequency_units: nhours
#    MPI Ranks in Filename: false
# Restart:
#    force_new_file: true
# '''

# hist_opts_3D_1dy_mean = f'''
# %YAML 1.1
# ---
# filename_prefix: output.scream.3D.1dy
# Averaging Type: Average
# Max Snapshots Per File: 1
# Fields:
#    Physics PG2:
#       Field Names:{field_txt_3D}
# output_control:
#    Frequency: 1
#    frequency_units: ndays
#    MPI Ranks in Filename: false
# Restart:
#    force_new_file: true
# '''
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':
   for n in range(len(opt_list)):
      main( opt_list[n] )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
