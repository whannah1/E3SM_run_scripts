#!/usr/bin/env python
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
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

# debug_mode = False

queue = 'debug'  # regular / debug

stop_opt,stop_n,resub,walltime = 'nsteps',6,0,'0:10:00'; queue='debug'
# stop_opt,stop_n,resub,walltime = 'ndays',5,0,'0:30:00'; queue='debug'
# stop_opt,stop_n,resub,walltime = 'ndays',32,0,'1:00:00'
# stop_opt,stop_n,resub,walltime = 'ndays',91,1,'4:00:00'
# stop_opt,stop_n,resub,walltime = 'ndays',365,4-1,'4:00:00'
#---------------------------------------------------------------------------------------------------
# EAM testing for stealth features

# src_dir  = f'{top_dir}/E3SM_SRC1/' # branch => whannah/eam/2026-gwd-updates
# add_case(prefix='2026-GW-DEV-00', compset='F2010', grid='ne4pg2_oQU480', num_nodes=1)

#---------------------------------------------------------------------------------------------------
# EAMxx GWD process testing

init_root = '/lcrc/group/e3sm/ac.whannah/scratch/chrys/HICCUP'
init_file_eam = f'{init_root}/HICCUP.atm_era5.EAM_format.2012-10-01.00.ne30np4.L80.nc'
# init_file_eamxx = f'{init_root}/HICCUP.atm_era5.EAMXX_format.2012-10-01.00.ne30np4.L128.nc'
init_file_eamxx = f'{init_root}/HICCUP.atm_era5.EAMXX_format.2012-10-01.00.ne30np4.L128.20260901.nc' # < separate U/V

src_dir  = f'{top_dir}/E3SM_SRC2/' # branch => whannah/eamxx/enable-conv-gwd
kwargs = {'prefix':'2026-GW-DEV-01', 'compset':'F2010xx-ZM'}

# add_case(**kwargs,grid='ne4pg2_oQU480',num_nodes=1, use_gw=False, gwo=False, gwc=False)
# add_case(**kwargs,grid='ne4pg2_oQU480',num_nodes=1, use_gw=True,  gwo=True,  gwc=False)
# add_case(**kwargs,grid='ne4pg2_oQU480',num_nodes=1, use_gw=True,  gwo=False, gwc=True)
# add_case(**kwargs,grid='ne4pg2_oQU480',num_nodes=1, use_gw=True,  gwo=True,  gwc=True)

# # test what happens when zm is missing
# add_case(prefix='2026-GW-DEV-02',compset='F2010-SCREAMv1',grid='ne4pg2_oQU480',num_nodes=1, use_gw=True,  gwo=True,  gwc=True)

# testing Luca's branch to support separate U/V in IC
add_case(prefix='2026-GW-DEV-02',compset='F2010-SCREAMv1',grid='ne30pg2_r05_IcoswISC30E3r5',num_nodes=8)


# add_case(**kwargs,grid='ne30pg2_r05_IcoswISC30E3r5',num_nodes=2, use_gw=False, gwo=False, gwc=False)
# add_case(**kwargs,grid='ne30pg2_r05_IcoswISC30E3r5',num_nodes=2, use_gw=True,  gwo=True,  gwc=False)
# add_case(**kwargs,grid='ne30pg2_r05_IcoswISC30E3r5',num_nodes=2, use_gw=True,  gwo=False, gwc=True)
# add_case(**kwargs,grid='ne30pg2_r05_IcoswISC30E3r5',num_nodes=2, use_gw=True,  gwo=True,  gwc=True)

# add_case(**kwargs,grid='ne30pg2_r05_IcoswISC30E3r5',num_nodes=8, use_gw=True,  gwo=True,  gwc=True)

# EAM cases for comparison
kwargs_eam = {'prefix':'2026-GW-DEV-01', 'compset':'F2010'}
# add_case(**kwargs_eam,grid='ne30pg2_r05_IcoswISC30E3r5',num_nodes=2, gwo=False, gwc=True)
# add_case(**kwargs_eam,grid='ne30pg2_r05_IcoswISC30E3r5',num_nodes=2, gwo=True,  gwc=True)

# add_case(**kwargs_eam,grid='ne30pg2_r05_IcoswISC30E3r5',num_nodes=8, gwo=True,  gwc=True)

# add_case(prefix='2026-GW-DEV-01', compset='F2010-SCREAMv1', grid='ne4pg2_oQU480', num_nodes=1, use_gw=True, debug=True)
# add_case(prefix='2026-GW-DEV-01', compset='F2010xx-ZM', grid='ne30pg2_r05_IcoswISC30E3r5', num_nodes=4, debug=True)

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
   case_list = ['E3SM']
   for key,val in opts.items(): 
      if key in ['prefix','compset','arch']: case_list.append(val)
      elif key in ['grid']:      case_list.append(get_grid_name(opts))
      elif key in ['debug']:     continue
      elif key in ['num_nodes']: case_list.append(f'NN_{val}')
      elif key in ['num_tasks']: case_list.append(f'NT_{val}')
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
   #------------------------------------------------------------------------------------------------
   # print(f' clean        : {clean}')
   # print(f' newcase      : {newcase}')
   # print(f' config       : {config}')
   # print(f' build        : {build}')
   # print(f' submit       : {submit}')
   # print(f' continue_run : {continue_run}')
   #------------------------------------------------------------------------------------------------
   if 'num_nodes' in opts and 'num_tasks' in opts:
      raise ValueError('cannot specify both num_nodes and num_tasks!')
   if 'num_nodes' not in opts and 'num_tasks' not in opts:
      raise ValueError('you must specify either num_nodes of num_tasks!')
   #------------------------------------------------------------------------------------------------
   debug_mode = False
   if 'debug' in opts: debug_mode = opts['debug']
   #------------------------------------------------------------------------------------------------
   # exit()
   #------------------------------------------------------------------------------------------------
   comp = None
   if opts['compset'] in ['F2010']:
      comp = 'eam'
   else:
      comp = 'eamxx'
   #------------------------------------------------------------------------------------------------
   case_root = f'/lcrc/group/e3sm/ac.whannah/scratch/chrys/{case}'

   if 'num_nodes' in opts:
      num_nodes = opts['num_nodes']
      max_mpi_per_node,atm_nthrds = 64,1 ; max_task_per_node = 64
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
      # cmd += f' --mach chrysalis --compiler gnu'
      cmd += f' --mach chrysalis --compiler intel'
      # cmd += f' --mach bebop --compiler intel'
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
      if clean : run_cmd('./case.setup --clean-all')
      run_cmd('./case.setup --reset')
      #-------------------------------------------------------------------------
      if opts.get('use_gw',False):
         run_cmd(f'./atmchange physics::atm_procs_list+=gw')
   #------------------------------------------------------------------------------------------------
   if build : 
      if debug_mode: run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
      if clean : run_cmd('./case.build --clean-all')
      # run_cmd('./case.build --clean ice')
      run_cmd('./case.build')
      # run_cmd('./case.build --clean ice  && ./case.build')
   #------------------------------------------------------------------------------------------------
   if submit :
      #-------------------------------------------------------------------------
      if comp=='eam':
         file=open('user_nl_eam','w')
         file.write(f'ncdata = \'{init_file_eam}\'\n')
         file.write(f"avgflag_pertape = 'A','A'\n")
         file.write(f"nhtfrq = 0,-24\n")
         file.write(f"mfilt = 1,1\n")
         file.write(f"fincl2 = 'PS', 'PRECT','Z3','CLOUD','CLDLIQ','CLDICE'")
         if opts.get('gwo'): file.write(f",'UTGWORO'")
         if opts.get('gwc'): file.write(f",'BUTGWSPEC'")
         file.write(f'\n')
         if opts.get('gwo'): file.write(f'use_gw_oro = .true.\n')
         if opts.get('gwc'): file.write(f'use_gw_convect = .true.\n')
         if not opts.get('gwo'): file.write(f'use_gw_oro = .false.\n')
         if not opts.get('gwc'): file.write(f'use_gw_convect = .false.\n')
         file.close()
      #-------------------------------------------------------------------------
      if comp=='eamxx':
         run_cmd(f'./atmchange -b initial_conditions::filename=\"{init_file_eamxx}\"')
         # run_cmd(f'./atmchange initial_conditions::nc=0.0')
         # run_cmd(f'./atmchange initial_conditions::ni=0.0')
         # exit()
         # if opts.get('prefix')=='2026-GW-DEV-02':
         #    run_cmd(f'./atmchange -b atmosphere_dag_verbosity_level=3')
         run_cmd(f'./atmchange -b atmosphere_dag_verbosity_level=0')
      #-------------------------------------------------------------------------
      if comp=='eamxx':
         if opts.get('use_gw',False):
            if opts.get('gwo'): run_cmd(f'./atmchange -b use_gw_orographic=true')
            if opts.get('gwc'): run_cmd(f'./atmchange -b use_gw_convect=true')
            if opts.get('gwf'): run_cmd(f'./atmchange -b use_gw_frontal=true')
            if not opts.get('gwo'): run_cmd(f'./atmchange -b use_gw_orographic=false')
            if not opts.get('gwc'): run_cmd(f'./atmchange -b use_gw_convect=false')
            if not opts.get('gwf'): run_cmd(f'./atmchange -b use_gw_frontal=false')
      #-------------------------------------------------------------------------
      # Enable tendency calculation for output
      if comp=='eamxx':
         # run_cmd(f'./atmchange -b physics::mac_aero_mic::shoc::compute_tendencies=T_mid,qv')
         # run_cmd(f'./atmchange -b physics::mac_aero_mic::p3::compute_tendencies=T_mid,qv')
         # run_cmd(f'./atmchange -b physics::rrtmgp::compute_tendencies=T_mid')
         # run_cmd(f'./atmchange -b homme::compute_tendencies=T_mid,qv')
         run_cmd(f'./atmchange -b shoc::compute_tendencies=horiz_winds')
         # run_cmd(f'./atmchange -b homme::compute_tendencies=horiz_winds')
         if 'F2010xx-ZM' in opts['compset']:
            # run_cmd(f'./atmchange -b physics::zm::compute_tendencies=T_mid,qv')
            run_cmd(f'./atmchange -b physics::zm::compute_tendencies=horiz_winds')
         if opts.get('use_gw',False):
            run_cmd(f'./atmchange -b physics::gw::compute_tendencies=T_mid,horiz_winds')
      #-------------------------------------------------------------------------
      hist_file_list = []
      def add_hist_file(hist_file,txt):
         file=open(hist_file,'w'); file.write(txt); file.close()
         hist_file_list.append(hist_file)
      #-------------------------------------------------------------------------
      if comp=='eamxx':
         # # add_hist_file('output_1si.yaml',get_hist_opts_1si(opts))
         # add_hist_file('output_1da.yaml',get_hist_opts_1da(opts))
         # hist_file_list_str = ','.join(hist_file_list)
         # run_cmd(f'./atmchange scorpio::output_yaml_files="{hist_file_list_str}"')
         #----------------------------------------------------------------------
         run_cmd(f'./atmchange scorpio::output_yaml_files=""')
         print();print(f'{clr.RED}WARNING - all output is disabled for debugging!{clr.END}');print()
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
# eam_opts = f'''

# '''
#---------------------------------------------------------------------------------------------------

gw_flds = f'''
         - gw_horiz_winds_tend
         - gw_oro_tend_u
         - gw_conv_tend_u
         - gw_T_mid_tend
         - gw_conv_heating_depth
         - gw_conv_heating_max
'''
def get_hist_opts_1si(opts):
   return f'''
%YAML 1.1
---
filename_prefix: output.1si
averaging_type: Instant
max_snapshots_per_file: 12
fields:
   physics_pg2:
      field_names:
         - ps
         - SeaLevelPressure
         #------------------------------
         - precip_total_surf_mass_flux
         - VapWaterPath
         - LiqWaterPath
         - IceWaterPath
         - RainWaterPath
         #------------------------------
         - z_mid
         - U
         - V
         #------------------------------
         - shoc_horiz_winds_tend
         - zm_horiz_winds_tend
         {gw_flds if opts.get('use_gw',False) else ''}
output_control:
   frequency: 1
   frequency_units: nsteps
'''

def get_hist_opts_1da(opts):
   return f'''
%YAML 1.1
---
filename_prefix: output.1da
averaging_type: Average
max_snapshots_per_file: 1
fields:
   physics_pg2:
      field_names:
         - ps
         - SeaLevelPressure
         #------------------------------
         - precip_total_surf_mass_flux
         - VapWaterPath
         - LiqWaterPath
         - IceWaterPath
         - RainWaterPath
         #------------------------------
         - z_mid
         - U
         - V
         #------------------------------
         - shoc_horiz_winds_tend
         - zm_horiz_winds_tend
         {gw_flds if opts.get('use_gw',False) else ''}
output_control:
   frequency: 1
   frequency_units: ndays
'''

#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':
   for n in range(len(opt_list)):
      main( opt_list[n] )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
