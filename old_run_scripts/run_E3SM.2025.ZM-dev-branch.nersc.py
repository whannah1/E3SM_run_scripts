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
# src_dir  = f'{top_dir}/E3SM_SRC1/' # branch => 
# src_dir  = f'{top_dir}/E3SM_SRC2/' # branch => whannah/eam/zm-bridge-00

# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
continue_run = True

queue = 'debug'  # regular / debug

# stop_opt,stop_n,resub,walltime = 'nsteps',23,0,'0:30:00'
# stop_opt,stop_n,resub,walltime = 'nsteps',20,0,'0:30:00'
# stop_opt,stop_n,resub,walltime = 'ndays',1,0,'0:30:00'
stop_opt,stop_n,resub,walltime = 'ndays',1,0,'2:00:00'
# stop_opt,stop_n,resub,walltime = 'ndays',10,0,'1:00:00'
# stop_opt,stop_n,resub,walltime = 'ndays',5,11,'0:30:00'
# stop_opt,stop_n,resub,walltime = 'ndays',91,1,'4:00:00'
# stop_opt,stop_n,resub,walltime = 'ndays',365,0,'3:00:00'
#---------------------------------------------------------------------------------------------------
# build list of cases to run

# ref_date = '0001-02-05'
# ref_case = 'E3SM.2025-ZM-DEV-04.F2010xx-ZM.ne30pg2.NN_8.zm_apply_tend_1.debug'

# src_dir=f'{top_dir}/E3SM_SRC3'; add_case(prefix='2025-ZM-DEV-04', compset='F2010xx-ZM', grid='ne30pg2_r05_IcoswISC30E3r5', num_nodes=4, zm_apply_tend=True, debug=True)
# src_dir=f'{top_dir}/E3SM_SRC3'; add_case(prefix='2025-ZM-DEV-04', compset='F2010xx-ZM', grid='ne30pg2_r05_IcoswISC30E3r5', num_tasks=1, zm_apply_tend=True, debug=True)

ref_date = '0001-08-12'
ref_case = 'E3SM.2025-ZM-DEV-04.F2010xx-ZM.ne4pg2.NT_96.zm_apply_tend_1.debug'

src_dir=f'{top_dir}/E3SM_SRC3'; add_case(prefix='2025-ZM-DEV-04-branch', compset='F2010xx-ZM', grid='ne4pg2_oQU480', num_tasks=1, zm_apply_tend=True, debug=True)

#---------------------------------------------------------------------------------------------------
# old cases prior to creating add_case() method

# compset,grid,num_nodes='F2010', f'ne4pg2_oQU480', 1
# case_list = ['E3SM','2025-ZM-DEV-00',grid,compset]

# compset,grid,num_nodes='F2010', f'ne30pg2_r05_IcoswISC30E3r5', 16
# src_dir=f'{top_dir}/E3SM_SRC0/'; case_list=['E3SM','2025-ZM-DEV-02','MCSP_OLD',grid,compset]
# src_dir=f'{top_dir}/E3SM_SRC1/'; case_list=['E3SM','2025-ZM-DEV-02','MCSP_NEW',grid,compset]
# src_dir=f'{top_dir}/E3SM_SRC1'; case_list=['E3SM','2025-ZM-DEV-02','MCSP_NEW_REBASE',grid,compset]

# EAMxx-ZM bridge testing
# compset,grid,num_nodes='F2010-SCREAMv1', f'ne4pg2_oQU480', 1
# compset,grid,num_nodes='F2010-SCREAMv1-MPASSI', f'ne4pg2_oQU480', 1
# src_dir=f'{top_dir}/E3SM_SRC2'; case_list = ['E3SM','2025-ZM-DEV-01',grid,compset]


# if debug_mode: case_list.append('debug')

# case='.'.join(case_list)

#---------------------------------------------------------------------------------------------------
def get_grid_name(opts):
   grid_name = opts['grid']
   if 'ne4pg2_'   in opts['grid']: grid_name = 'ne4pg2'
   if 'ne30pg2_'  in opts['grid']: grid_name = 'ne30pg2'
   if 'ne120pg2_' in opts['grid']: grid_name = 'ne120pg2'
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
def set_branch_stuff(case_root):
   global ref_date, ref_case
   run_cmd(f'./xmlchange RUN_TYPE=branch')
   run_cmd(f'./xmlchange GET_REFCASE=FALSE')
   run_cmd(f'./xmlchange RUN_REFCASE=\'{ref_case}\'')
   run_cmd(f'./xmlchange RUN_REFDATE={ref_date}')
   scratch = '/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu'
   run_cmd(f'cp {scratch}/{ref_case}/run/*{ref_date}* {case_root}/run/')
   run_cmd(f'cp {scratch}/{ref_case}/run/rpointer* {case_root}/run/')
#---------------------------------------------------------------------------------------------------
def main(opts):

   case = get_case_name(opts)

   print(f'\n  case : {case}\n')

   #----------------------------------------------------------------------------
   debug_mode = False
   if 'debug' in opts: debug_mode = opts['debug']
   if 'arch' in opts:
      arch = opts['arch']
   else:
      arch = 'CPU'
   #----------------------------------------------------------------------------
   if 'num_nodes' in opts and 'num_tasks' in opts:
      raise ValueError('cannot specify both num_nodes and num_tasks!')
   if 'num_nodes' not in opts and 'num_tasks' not in opts:
      raise ValueError('you must specify either num_nodes of num_tasks!')
   #----------------------------------------------------------------------------
   # return
   #----------------------------------------------------------------------------
   case_root = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/{case}'
   if 'num_nodes' in opts:
      if arch=='CPU': max_mpi_per_node,atm_nthrds  = 128,1
      if arch=='GPU': max_mpi_per_node,atm_nthrds  =   4,8
      num_nodes = opts['num_nodes']
      atm_ntasks = max_mpi_per_node*num_nodes
   if 'num_tasks' in opts:
      atm_ntasks,atm_nthrds = opts['num_tasks'],1
   #----------------------------------------------------------------------------
   # if 'ne4pg2' in opts['grid']:
   #    # max_mpi_per_node,atm_nthrds  = 96,1 # need this for single node ne4 tests
   #    # max_mpi_per_node,atm_nthrds  = 90,1 # force uneven column counts
   #    # smaller NTASK for debugging weird column swapping issue
   #    max_mpi_per_node,atm_nthrds  = 20,1
   # else:
   #    max_mpi_per_node,atm_nthrds  = 128,1
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
      if arch=='CPU': cmd += f' --mach pm-cpu --compiler gnu'
      if arch=='GPU': cmd += f' --mach pm-gpu --compiler gnugpu'
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
      #-------------------------------------------------------------------------
      set_branch_stuff(case_root)
   #------------------------------------------------------------------------------------------------
   if build : 
      if debug_mode: run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
      if clean : run_cmd('./case.build --clean')
      run_cmd('./case.build')
   #------------------------------------------------------------------------------------------------
   if submit :
      #-------------------------------------------------------------------------
      # set_branch_stuff(case_root)
      #-------------------------------------------------------------------------
      if 'SCREAM' in opts['compset'] or 'F2010xx' in opts['compset']:

         #----------------------------------------------------------------------
         if 'zm_apply_tend' in opts:
            if opts['zm_apply_tend']:
               run_cmd('./atmchange physics::zm::apply_tendencies=true')
            else:
               run_cmd('./atmchange physics::zm::apply_tendencies=false')
         #----------------------------------------------------------------------
         # run_cmd('./atmchange physics::mac_aero_mic::shoc::compute_tendencies=T_mid,qv,horiz_winds')
         # run_cmd('./atmchange physics::mac_aero_mic::p3::compute_tendencies=T_mid,qv')
         # run_cmd('./atmchange physics::rrtmgp::compute_tendencies=T_mid')
         # run_cmd('./atmchange homme::compute_tendencies=T_mid,qv,horiz_winds')
         # #----------------------------------------------------------------------
         # hist_file_list = []
         # def add_hist_file(hist_file,txt):
         #    file=open(hist_file,'w'); file.write(txt); file.close()
         #    hist_file_list.append(hist_file)
         # #----------------------------------------------------------------------
         # # add_hist_file('scream_output_debug_1step_inst.yaml',hist_opts_debug_1step_inst)
         # # add_hist_file('scream_output_2D_1step_inst.yaml',hist_opts_2D_1step_inst)
         
         # # add_hist_file('scream_output_2D_1hr_avg.yaml', hist_opts_2D_1hr_inst)
         # # add_hist_file('scream_output_2D_10dy_avg.yaml',hist_opts_2D_10dy_avg)
         # # add_hist_file('scream_output_3D_1dy_avg.yaml', hist_opts_3D_1dy_avg)

         # add_hist_file('scream_output_2D_1dy_avg.yaml', hist_opts_2D_1dy_avg)
         # add_hist_file('scream_output_2D_1mo_avg.yaml', hist_opts_2D_1mo_avg)
         # add_hist_file('scream_output_3D_1mo_avg.yaml', hist_opts_3D_1mo_avg)

         # hist_file_list_str = ','.join(hist_file_list)
         # run_cmd(f'./atmchange scorpio::output_yaml_files="{hist_file_list_str}"')
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
      # Submit the run
      run_cmd('./case.submit')

   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {case}\n') 

   print()
   print(clr.RED+'WARNING - all output is disabled for debugging!'+clr.END)
   print()
#---------------------------------------------------------------------------------------------------
eam_opts = f'''
 avgflag_pertape = 'A','A'
 nhtfrq = 0,-1
 mfilt  = 1,24
 fincl1 = 'PRECT','Z3','CAPE_ZM','PREC_zmc','PRECC'
'''
# 'CLOUD','CLDLIQ','CLDICE'
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
      - zm_prec
      - zm_snow
      - zm_cape
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
   force_new_file: true
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
