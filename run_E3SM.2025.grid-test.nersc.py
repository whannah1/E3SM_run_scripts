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

acct = 'e3sm'
top_dir  = os.getenv('HOME')+'/E3SM/'

# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
# continue_run = True

queue = 'regular'  # regular / debug

# stop_opt,stop_n,resub,walltime = 'nsteps',10,0,'0:30:00'
# stop_opt,stop_n,resub,walltime = 'nsteps',4,2,'0:30:00'
stop_opt,stop_n,resub,walltime = 'ndays',1,0,'0:30:00'
# stop_opt,stop_n,resub,walltime = 'ndays',10,1,'0:30:00'
# stop_opt,stop_n,resub,walltime = 'ndays',10,0,'1:00:00'
# stop_opt,stop_n,resub,walltime = 'ndays',5,10,'0:30:00'
# stop_opt,stop_n,resub,walltime = 'ndays',73,5-1,'4:00:00'
# stop_opt,stop_n,resub,walltime = 'ndays',365,0,'6:00:00'

#---------------------------------------------------------------------------------------------------
# build list of cases to run

# src_dir=f'{top_dir}/E3SM_SRC0'; add_case(prefix='2025-grid-test-00', arch='CPU', num_nodes=8, grid='ne30pg2_r05_IcoswISC30E3r5', compset='F2010')
# src_dir=f'{top_dir}/E3SM_SRC0'; add_case(prefix='2025-grid-test-00', arch='CPU', num_nodes=96, grid='ne32pg2_r025_RRSwISC6to18E3r5', compset='F2010')

# src_dir=f'{top_dir}/E3SM_SRC4'; add_case(prefix='2025-grid-test-00', arch='GPU', num_nodes=2, compset='F2010-SCREAMv1', grid='ne32pg2_r025_RRSwISC6to18E3r5' )
# src_dir=f'{top_dir}/E3SM_SRC4'; add_case(prefix='2025-grid-test-00', arch='GPU', num_nodes=4, compset='F2010-SCREAMv1', grid='ne32pg2_r025_RRSwISC6to18E3r5' )
# src_dir=f'{top_dir}/E3SM_SRC4'; add_case(prefix='2025-grid-test-00', arch='GPU', num_nodes=8, compset='F2010-SCREAMv1', grid='ne32pg2_r025_RRSwISC6to18E3r5' )
# src_dir=f'{top_dir}/E3SM_SRC4'; add_case(prefix='2025-grid-test-00', arch='GPU', num_nodes=16, compset='F2010-SCREAMv1', grid='ne32pg2_r025_RRSwISC6to18E3r5' )
# src_dir=f'{top_dir}/E3SM_SRC4'; add_case(prefix='2025-grid-test-00', arch='GPU', num_nodes=32, compset='F2010-SCREAMv1', grid='ne32pg2_r025_RRSwISC6to18E3r5' )

src_dir=f'{top_dir}/E3SM_SRC4'; add_case(prefix='2025-grid-test-00', arch='GPU', num_nodes=32, compset='F2010-SCREAMv1', grid='ne64pg2_r025_RRSwISC6to18E3r5' )
# src_dir=f'{top_dir}/E3SM_SRC4'; add_case(prefix='2025-grid-test-00', arch='GPU', num_nodes=64, compset='F2010-SCREAMv1', grid='ne128pg2_r025_RRSwISC6to18E3r5' )

# src_dir=f'{top_dir}/E3SM_SRC4'; add_case(prefix='2025-grid-test-00', arch='GPU', num_nodes=1, compset='F2010-SCREAMv1', grid='ne32pg2_r025_RRSwISC6to18E3r5' )
# src_dir=f'{top_dir}/E3SM_SRC4'; add_case(prefix='2025-grid-test-00', arch='GPU', num_nodes=4, compset='F2010-SCREAMv1', grid='ne64pg2_r025_RRSwISC6to18E3r5' )
# src_dir=f'{top_dir}/E3SM_SRC4'; add_case(prefix='2025-grid-test-00', arch='GPU', num_nodes=16, compset='F2010-SCREAMv1', grid='ne128pg2_r025_RRSwISC6to18E3r5' )



# src_dir=f'{top_dir}/E3SM_SRC3'; add_case(prefix='2025-grid-test-00', arch='GPU', num_tasks= 4, grid='ne4pg2_oQU480', compset='F2010xx-ZM', debug=True)



#---------------------------------------------------------------------------------------------------
def get_grid_name(opts):
   grid_name = opts['grid']
   if 'ne4pg2_'   in opts['grid']: grid_name = 'ne4pg2'
   if 'ne30pg2_'  in opts['grid']: grid_name = 'ne30pg2'
   if 'ne32pg2_'  in opts['grid']: grid_name = 'ne32pg2'
   if 'ne64pg2_'  in opts['grid']: grid_name = 'ne64pg2'
   if 'ne120pg2_' in opts['grid']: grid_name = 'ne120pg2'
   if 'ne128pg2_' in opts['grid']: grid_name = 'ne128pg2'
   return grid_name
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
         case_list.append(get_grid_name(opts))
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
   case_root = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-gpu/{case}'
   if 'num_nodes' in opts:
      if arch=='CPU': max_mpi_per_node,atm_nthrds  = 128,1
      if arch=='GPU': max_mpi_per_node,atm_nthrds  =   4,1
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
      cmd += f' --res {opts["grid"]} '
      cmd += f' --pecount {atm_ntasks}x{atm_nthrds} '
      cmd += f' --project {acct} '
      # if arch=='CPU': cmd += f' --mach aurora --compiler oneapi-ifx '
      # if arch=='GPU': cmd += f' --mach aurora --compiler oneapi-ifxgpu '
      if arch=='GPU': cmd += f' -mach pm-gpu -compiler gnugpu '
      if arch=='CPU': cmd += f' -mach pm-cpu -compiler gnu '
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
      # if 'SCREAM' in opts["compset"]: run_cmd(f'./atmchange mac_aero_mic::atm_procs_list+=zm')
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
      if 'SCREAM' in opts['compset'] or 'F2010xx' in opts['compset']:
         #----------------------------------------------------------------------
         run_cmd('./atmchange physics::mac_aero_mic::shoc::compute_tendencies=T_mid,qv,horiz_winds')
         run_cmd('./atmchange physics::mac_aero_mic::p3::compute_tendencies=T_mid,qv')
         run_cmd('./atmchange physics::rrtmgp::compute_tendencies=T_mid')
         run_cmd('./atmchange homme::compute_tendencies=T_mid,qv,horiz_winds')
         #----------------------------------------------------------------------
         hist_file_list = []
         def add_hist_file(hist_file,txt):
            file=open(hist_file,'w'); file.write(txt); file.close()
            hist_file_list.append(hist_file)
         #----------------------------------------------------------------------
         # add_hist_file('scream_output_debug_1step_inst.yaml',hist_opts_debug_1step_inst)
         # add_hist_file('scream_output_2D_1step_inst.yaml',hist_opts_2D_1step_inst)
         
         # add_hist_file('scream_output_2D_1hr_avg.yaml', hist_opts_2D_1hr_inst)
         # add_hist_file('scream_output_2D_10dy_avg.yaml',hist_opts_2D_10dy_avg)
         # add_hist_file('scream_output_3D_1dy_avg.yaml', hist_opts_3D_1dy_avg)

         add_hist_file('scream_output_2D_1dy_avg.yaml', hist_opts_2D_1dy_avg)

         # add_hist_file('scream_output_2D_1mo_avg.yaml', hist_opts_2D_1mo_avg)
         # add_hist_file('scream_output_3D_1mo_avg.yaml', hist_opts_3D_1mo_avg)

         hist_file_list_str = ','.join(hist_file_list)
         run_cmd(f'./atmchange scorpio::output_yaml_files="{hist_file_list_str}"')
      else:
         # EAM namelist options
         nfile = 'user_nl_eam'
         file = open(nfile,'w') 
         file.write(eam_opts)
         file.close()
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
      # print()
      # print(clr.MAGENTA+'WARNING - manually setting restart freq to 2 steps'+clr.END)
      # print()
      # run_cmd(f'./xmlchange REST_OPTION=nsteps,REST_N=2')
      # run_cmd(f'./xmlchange REST_OPTION=ndays,REST_N=1')
      # run_cmd(f'./xmlchange REST_OPTION={stop_opt},REST_N={stop_n}')
      # run_cmd(f'./xmlchange REST_OPTION=never')
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
eam_opts = f'''
 avgflag_pertape = 'A','A'
 nhtfrq = 0,-1
 mfilt  = 1,24
 fincl1 = 'PRECT','Z3','CAPE_ZM','PREC_zmc','PRECC'
'''
# 'CLOUD','CLDLIQ','CLDICE'
#---------------------------------------------------------------------------------------------------
field_txt_2D = '\n'
field_txt_2D += '      - ps\n'
field_txt_2D += '      - precip_total_surf_mass_flux\n'
field_txt_2D += '      - VapWaterPath\n'
field_txt_2D += '      - LiqWaterPath\n'
field_txt_2D += '      - IceWaterPath\n'
field_txt_2D += '      - surf_sens_flux\n'
field_txt_2D += '      - surface_upward_latent_heat_flux\n'
field_txt_2D += '      - wind_speed_10m\n'
field_txt_2D += '      - U_at_model_bot\n'
field_txt_2D += '      - V_at_model_bot\n'
field_txt_2D += '      - U_at_850hPa\n'
field_txt_2D += '      - U_at_200hPa\n'
field_txt_2D += '      - omega_at_500hPa\n'
field_txt_2D += '      - SW_flux_up_at_model_top\n'
field_txt_2D += '      - SW_flux_dn_at_model_top\n'
field_txt_2D += '      - LW_flux_up_at_model_top\n'
# field_txt_2D += '      - surf_evap\n'
# field_txt_2D += '      - surf_mom_flux\n'
# field_txt_2D += '      - horiz_winds_at_model_bot\n'
# field_txt_2D += '      - SW_flux_dn_at_model_bot\n'
# field_txt_2D += '      - SW_flux_up_at_model_bot\n'
# field_txt_2D += '      - LW_flux_dn_at_model_bot\n'
# field_txt_2D += '      - LW_flux_up_at_model_bot\n'
# field_txt_2D += '      - SW_flux_up_at_model_top\n'
# field_txt_2D += '      - SW_flux_dn_at_model_top\n'
# field_txt_2D += '      - LW_flux_up_at_model_top\n'

field_txt_3D = '\n'
field_txt_3D += '      - ps\n'
field_txt_3D += '      - z_mid\n'
field_txt_3D += '      - T_mid\n'
field_txt_3D += '      - qv\n'
field_txt_3D += '      - U\n'
field_txt_3D += '      - V\n'
field_txt_3D += '      - omega\n'
# field_txt_3D += '      - qc\n'
# field_txt_3D += '      - qr\n'
# field_txt_3D += '      - qi\n'
# field_txt_3D += '      - qm\n'
# field_txt_3D += '      - nc\n'
# field_txt_3D += '      - nr\n'
# field_txt_3D += '      - ni\n'
# field_txt_3D += '      - bm\n'
# field_txt_3D += '      - RelativeHumidity\n'
# field_txt_3D += '      - rad_heating_pdel\n'
field_txt_3D+='      - qr \n'
field_txt_3D+='      - qm \n'
# field_txt_3D+='      - cldfrac_tot_for_analysis \n'
# field_txt_3D+='      - cldfrac_liq \n'
# field_txt_3D+='      - cldfrac_ice_for_analysis \n'
# field_txt_3D+='      - RelativeHumidity \n'
# field_txt_3D+='      - p3_T_mid_tend \n'
# field_txt_3D+='      - shoc_T_mid_tend \n'
# field_txt_3D+='      - rrtmgp_T_mid_tend \n'
# field_txt_3D+='      - homme_T_mid_tend \n'
# field_txt_3D+='      - p3_qv_tend \n'
# field_txt_3D+='      - shoc_qv_tend \n'
# field_txt_3D+='      - homme_qv_tend \n'
# field_txt_3D+='      - shoc_horiz_winds_tend \n'
# field_txt_3D+='      - homme_horiz_winds_tend \n'


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
   force_new_file: true
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
   force_new_file: true
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
   force_new_file: true
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
   force_new_file: true
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
   force_new_file: true
'''


hist_opts_debug_1step_inst = f'''
%YAML 1.1
---
filename_prefix: output.scream.2D
averaging_type: instant
max_snapshots_per_file: 48
fields:
   physics_pg2:
      field_names:
         - precip_total_surf_mass_flux
         - LiqWaterPath
         - IceWaterPath
         - zm_prec
         - zm_cape
         - zm_activity
         - ps
         - p_mid
         - T_mid
         - qv
         - omega
         - U
output_control:
   frequency: 1
   frequency_units: nsteps
restart:
   force_new_file: true
'''

#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':
   for n in range(len(opt_list)):
      main( opt_list[n] )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
