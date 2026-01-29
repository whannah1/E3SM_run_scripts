#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
'''
scontrol update qos=debug jobid=
'''
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
opt_list = []
def add_case( **kwargs ):
   case_opts = {}
   for k, val in kwargs.items(): case_opts[k] = val
   opt_list.append(case_opts)
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp
from shutil import copy2
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'E3SM_Dec'
top_dir  = os.getenv('HOME')+'/E3SM/'

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

# queue = 'debug'  # regular / debug

# stop_opt,stop_n,resub,walltime = 'nsteps',10,0,'0:30:00'
# stop_opt,stop_n,resub,walltime = 'nsteps',4,2,'0:30:00'
stop_opt,stop_n,resub,walltime = 'ndays',2,0,'0:30:00'
# stop_opt,stop_n,resub,walltime = 'ndays',10,1,'0:30:00'
# stop_opt,stop_n,resub,walltime = 'ndays',10,0,'1:00:00'
# stop_opt,stop_n,resub,walltime = 'ndays',5,0,'0:30:00'
# stop_opt,stop_n,resub,walltime = 'ndays',73,5-1,'4:00:00'
# stop_opt,stop_n,resub,walltime = 'ndays',365,0,'6:00:00'

#---------------------------------------------------------------------------------------------------
# build list of cases to run


src_dir=f'{top_dir}/E3SM_SRC0'

add_case(prefix='2026-time-step-test-00', arch='GPU', compset='F2010-SCREAMv1', grid='ne256', num_nodes=64, NCPL=120 ) # 12-min
# add_case(prefix='2026-time-step-test-00', arch='GPU', compset='F2010-SCREAMv1', grid='ne256', num_nodes=64, NCPL=144 ) # 10-min
# add_case(prefix='2026-time-step-test-00', arch='GPU', compset='F2010-SCREAMv1', grid='ne256', num_nodes=64, NCPL=240 ) #  6-min
add_case(prefix='2026-time-step-test-00', arch='GPU', compset='F2010-SCREAMv1', grid='ne256', num_nodes=64, NCPL=288 ) #  5-min


#---------------------------------------------------------------------------------------------------
def get_grid(opts):
   grid_short,grid = opts['grid'],None
   if grid_short=='ne256': grid = 'ne256pg2_ne256pg2'
   if grid_short=='ne128': grid = 'ne128pg2_ne128pg2'
   if grid_short=='ne64' : grid = 'ne64pg2_ne64pg2'
   if grid_short=='ne32' : grid = 'ne32pg2_ne32pg2'
   if grid is None: raise ValueError('grid cannot be None!')
   return grid
#---------------------------------------------------------------------------------------------------
def get_case_name(opts):
   # global debug_mode
   #----------------------------------------------------------------------------
   debug_mode = False
   if 'debug' in opts: debug_mode = opts['debug']
   #----------------------------------------------------------------------------
   case_list = ['E3SM']
   for key,val in opts.items(): 
      if key in ['prefix','compset','arch']:
         case_list.append(val)
      elif key in ['grid']: 
         case_list.append(get_grid(opts))
      elif key in ['debug']: 
         continue
      elif key in ['num_nodes']:
         case_list.append(f'NN_{val}')
      elif key in ['num_tasks']:
         case_list.append(f'NT_{val}')
      else:
         if isinstance(val, str):
            case_list.append(f'{key}_{val}')
         else:
            case_list.append(f'{key}_{val:g}')
   if debug_mode: case_list.append('debug')
   case = '.'.join(case_list)
   # clean up the exponential numbers in the case name
   for i in range(1,9+1): case = case.replace(f'e+0{i}',f'e{i}')
   return case
#---------------------------------------------------------------------------------------------------
def main(opts):

   case = get_case_name(opts)

   print(f'\n  case : {case}\n')

   #----------------------------------------------------------------------------
   debug_mode = False
   if 'debug' in opts: debug_mode = opts['debug']
   arch = 'CPU'
   if 'arch' in opts: arch = opts['arch']
   #----------------------------------------------------------------------------
   if 'num_nodes' in opts and 'num_tasks' in opts:
      raise ValueError('cannot specify both num_nodes and num_tasks!')
   if 'num_nodes' not in opts and 'num_tasks' not in opts:
      raise ValueError('you must specify either num_nodes of num_tasks!')
   #----------------------------------------------------------------------------
   # return
   #----------------------------------------------------------------------------
   case_root = f'/lus/flare/projects/E3SM_Dec/whannah/scratch/{case}'
   if 'num_nodes' in opts:
      if arch=='CPU': max_mpi_per_node,atm_nthrds  = 102,1
      if arch=='GPU': max_mpi_per_node,atm_nthrds  =  12,1
      num_nodes = opts['num_nodes']
      atm_ntasks = max_mpi_per_node*num_nodes
   if 'num_tasks' in opts:
      atm_ntasks,atm_nthrds = opts['num_tasks'],1
   #------------------------------------------------------------------------------------------------
   # Create new case
   if newcase :
      if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
      cmd = f'{src_dir}/cime/scripts/create_newcase'
      cmd += f' --case {case} --handle-preexisting-dirs u'
      cmd += f' --output-root {case_root} '
      cmd += f' --script-root {case_root}/case_scripts '
      cmd += f' --compset {opts["compset"]}'
      cmd += f' --res {get_grid(opts)} '
      cmd += f' --pecount {atm_ntasks}x{atm_nthrds} '
      cmd += f' --project {acct} '
      if arch=='CPU': cmd += f' --mach aurora --compiler oneapi-ifx '
      if arch=='GPU': cmd += f' --mach aurora --compiler oneapi-ifxgpu '
      cmd += f' --pecount {atm_ntasks}x{atm_nthrds} '
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
      if 'NCPL' in opts:
         ncpl = opts['NCPL']
         run_cmd(f'./xmlchange ATM_NCPL={ncpl}')
         if ncpl==120: # 12-min
            run_cmd(f'./atmchange -b ctl_nl::se_tstep=30')
            run_cmd(f'./atmchange -b ctl_nl::dt_remap_factor=2')
            run_cmd(f'./atmchange -b ctl_nl::dt_tracer_factor=12')
            run_cmd(f'./atmchange -b ctl_nl::hypervis_subcycle_q=12')
            run_cmd(f'./atmchange -b ctl_nl::semi_lagrange_trajectory_nsubstep=2')
         if ncpl==144: # 10-min
            run_cmd(f'./atmchange -b ctl_nl::se_tstep=30')
            run_cmd(f'./atmchange -b ctl_nl::dt_remap_factor=2')
            run_cmd(f'./atmchange -b ctl_nl::dt_tracer_factor=10')
            run_cmd(f'./atmchange -b ctl_nl::hypervis_subcycle_q=10')
            run_cmd(f'./atmchange -b ctl_nl::semi_lagrange_trajectory_nsubstep=2')
         if ncpl==240: # 6-min
            run_cmd(f'./atmchange -b ctl_nl::se_tstep=30')
            run_cmd(f'./atmchange -b ctl_nl::dt_remap_factor=2')
            run_cmd(f'./atmchange -b ctl_nl::dt_tracer_factor=6')
            run_cmd(f'./atmchange -b ctl_nl::hypervis_subcycle_q=6')
            run_cmd(f'./atmchange -b ctl_nl::semi_lagrange_trajectory_nsubstep=2')
         if ncpl==288: # 5-min
            run_cmd(f'./atmchange -b ctl_nl::se_tstep=30')
            run_cmd(f'./atmchange -b ctl_nl::dt_remap_factor=1')
            run_cmd(f'./atmchange -b ctl_nl::dt_tracer_factor=5')
            run_cmd(f'./atmchange -b ctl_nl::hypervis_subcycle_q=5')
            run_cmd(f'./atmchange -b ctl_nl::semi_lagrange_trajectory_nsubstep=2')
      #----------------------------------------------------------------------
      # run_cmd('./atmchange physics::mac_aero_mic::shoc::compute_tendencies=T_mid,qv,horiz_winds')
      # run_cmd('./atmchange physics::mac_aero_mic::p3::compute_tendencies=T_mid,qv')
      # run_cmd('./atmchange physics::rrtmgp::compute_tendencies=T_mid')
      # run_cmd('./atmchange homme::compute_tendencies=T_mid,qv,horiz_winds')
      #----------------------------------------------------------------------
      hist_file_list = []
      def add_hist_file(hist_file,txt):
         file=open(hist_file,'w'); file.write(txt); file.close()
         hist_file_list.append(hist_file)
      #----------------------------------------------------------------------
      add_hist_file('scream_output_debug_1step_inst.yaml',hist_opts_debug_1step_inst)
      # add_hist_file('scream_output_2D_1step_inst.yaml',hist_opts_2D_1step_inst)
      
      # add_hist_file('scream_output_2D_1hr_avg.yaml', hist_opts_2D_1hr_inst)
      # add_hist_file('scream_output_2D_10dy_avg.yaml',hist_opts_2D_10dy_avg)
      # add_hist_file('scream_output_3D_1dy_avg.yaml', hist_opts_3D_1dy_avg)

      # add_hist_file('scream_output_2D_1dy_avg.yaml', hist_opts_2D_1dy_avg)

      # add_hist_file('scream_output_2D_1mo_avg.yaml', hist_opts_2D_1mo_avg)
      # add_hist_file('scream_output_3D_1mo_avg.yaml', hist_opts_3D_1mo_avg)

      hist_file_list_str = ','.join(hist_file_list)
      run_cmd(f'./atmchange scorpio::output_yaml_files="{hist_file_list_str}"')
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

   # print()
   # print(clr.RED+'WARNING - history output is disabled!'+clr.END)
   # print(clr.RED+'WARNING - restart output is disabled!'+clr.END)
   # print()
#---------------------------------------------------------------------------------------------------
field_txt_2D = '''
      - ps
      - precip_total_surf_mass_flux
      - precip_liq_surf_mass_flux
      - precip_ice_surf_mass_flux
      - LiqWaterPath
      - IceWaterPath
      - U_at_model_bot
      - U_at_850hPa
      - U_at_200hPa
      - omega_at_500hPa
'''
# field_txt_2D += '      - surf_sens_flux'
# field_txt_2D += '      - surf_evap'
# field_txt_2D += '      - surf_mom_flux'

field_txt_3D = '''
      - ps
      - T_mid
      - qv
      - qc
      - qi
      - omega
      - U
'''
# field_txt_3D+='      - rad_heating_pdel \n'
field_txt_3D+='      - cldfrac_tot_for_analysis \n'
field_txt_3D+='      - cldfrac_liq \n'
field_txt_3D+='      - cldfrac_ice_for_analysis \n'
field_txt_3D+='      - z_mid \n'
field_txt_3D+='      - qr \n'
field_txt_3D+='      - qm \n'
field_txt_3D+='      - RelativeHumidity \n'
field_txt_3D+='      - p3_T_mid_tend \n'
field_txt_3D+='      - shoc_T_mid_tend \n'
field_txt_3D+='      - rrtmgp_T_mid_tend \n'
field_txt_3D+='      - homme_T_mid_tend \n'
field_txt_3D+='      - p3_qv_tend \n'
field_txt_3D+='      - shoc_qv_tend \n'
field_txt_3D+='      - homme_qv_tend \n'
field_txt_3D+='      - shoc_horiz_winds_tend \n'
field_txt_3D+='      - homme_horiz_winds_tend \n'
field_txt_3D+='      - zm_T_mid_tend \n'
field_txt_3D+='      - zm_qv_tend \n'
field_txt_3D+='      - zm_u_tend \n'
field_txt_3D+='      - zm_v_tend \n'


hist_opts_2D_1dy_avg = f'''
%YAML 1.1
---
filename_prefix: output.scream.2D
averaging_type: average
max_snapshots_per_file: 1
fields:
   physics_pg2:
      field_names:{field_txt_2D}
output_control:
   frequency: 1
   frequency_units: ndays
restart:
   force_new_file: false
'''

hist_opts_2D_10dy_avg = f'''
%YAML 1.1
---
filename_prefix: output.scream.2D
averaging_type: average
max_snapshots_per_file: 1
fields:
   physics_pg2:
      field_names:{field_txt_2D}
output_control:
   frequency: 10
   frequency_units: ndays
restart:
   force_new_file: false
'''

hist_opts_2D_1hr_inst = f'''
%YAML 1.1
---
filename_prefix: output.scream.2D
averaging_type: instant
max_snapshots_per_file: 24
fields:
   physics_pg2:
      field_names:{field_txt_2D}
output_control:
   frequency: 1
   frequency_units: nhours
restart:
   force_new_file: false
'''

hist_opts_2D_1step_inst = f'''
%YAML 1.1
---
filename_prefix: output.scream.2D
averaging_type: instant
max_snapshots_per_file: 48
fields:
   physics_pg2:
      field_names:{field_txt_2D}
output_control:
   frequency: 1
   frequency_units: nsteps
restart:
   force_new_file: false
'''

hist_opts_3D_1dy_avg = f'''
%YAML 1.1
---
filename_prefix: output.scream.3D
averaging_type: average
max_snapshots_per_file: 1
fields:
   physics_pg2:
      field_names:{field_txt_3D}
output_control:
   frequency: 1
   frequency_units: ndays
restart:
   force_new_file: false
'''

# monthly mean output

hist_opts_2D_1mo_avg = f'''
%YAML 1.1
---
filename_prefix: output.scream.2D
averaging_type: average
max_snapshots_per_file: 1
fields:
   physics_pg2:
      field_names:{field_txt_2D}
output_control:
   frequency: 1
   frequency_units: nmonths
restart:
   force_new_file: false
'''

hist_opts_3D_1mo_avg = f'''
%YAML 1.1
---
filename_prefix: output.scream.3D
averaging_type: average
max_snapshots_per_file: 1
fields:
   physics_pg2:
      field_names:{field_txt_3D}
output_control:
   frequency: 1
   frequency_units: nmonths
restart:
   force_new_file: false
'''


hist_opts_debug_1step_inst = f'''
%YAML 1.1
---
filename_prefix: output.scream.2D
averaging_type: instant
max_snapshots_per_file: 10
fields:
   physics_pg2:
      field_names:
         - ps
         - T_2m
         - precip_total_surf_mass_flux
         - LiqWaterPath
         - IceWaterPath
         - U_at_model_bot
         - V_at_model_bot
         - surf_sens_flux
         - surface_upward_latent_heat_flux
         - surf_mom_flux
         - wind_speed_10m
output_control:
   frequency: 1
   frequency_units: nsteps
restart:
   force_new_file: false
'''

#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':
   for n in range(len(opt_list)):
      main( opt_list[n] )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
