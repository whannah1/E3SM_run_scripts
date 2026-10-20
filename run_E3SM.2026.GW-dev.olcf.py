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
'''
~/E3SM/E3SM_SRC2/components/eamxx/src/physics/gw
export E3SM_ENABLE_KOKKOS_BOUNDS_CHECKING=TRUE
export AMD_LOG_LEVEL=3
export AMD_SERIALIZE_KERNEL=3 # wait before+after every kernel
export AMD_SERIALIZE_COPY=3

resume claude session for these runs here:
~/E3SM/E3SM_SRC0/components/eamxx/src/physics/gw
'''
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp
from shutil import copy2
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'cli115'
top_dir  = os.getenv('HOME')+'/E3SM/'
# src_dir  = f'{top_dir}/E3SM_SRC0/' # branch => master @ Sep 15 152dcd1ccbbbd99a54c9db5b49a261e57016268e
src_dir  = f'{top_dir}/E3SM_SRC0/' # branch =>whannah/eamxx/conv-gw-fix rebased on master @ Sep 23

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

# debug_mode = False

queue = 'debug'  # batch / debug

# stop_opt,stop_n,resub,walltime = 'nsteps',2,0,'0:30:00'
stop_opt,stop_n,resub,walltime = 'ndays',1,0,'0:20:00'
# stop_opt,stop_n,resub,walltime = 'ndays',10,0,'1:00:00'
# stop_opt,stop_n,resub,walltime = 'ndays',32,0,'0:30:00'
# stop_opt,stop_n,resub,walltime = 'ndays',91,1,'4:00:00'
# stop_opt,stop_n,resub,walltime = 'ndays',365,4-1,'4:00:00'
#---------------------------------------------------------------------------------------------------
### EAMxx GWD process testing

# kwargs_common= {'prefix':'2026-GW-DEV-00', 'compset':'F2010xx-ZM-CICE'}
kwargs_ne256 = {'grid':'ne256pg2_ne256pg2', 'num_nodes':128}
kwargs_ne32  = {'grid':'ne32pg2_ne32pg2', 'num_nodes':4}

# add_case(**kwargs_common, **kwargs_ne256, use_gw=True)
# add_case(**kwargs_common, **kwargs_ne256, use_gw=False)

# add_case(**kwargs_common, **kwargs_ne256, use_oro=True, tom_ss=5)
# add_case(**kwargs_common, **kwargs_ne256, use_oro=True, tom_ss=15)
# add_case(**kwargs_common, **kwargs_ne256, use_oro=True, tom_ss=30)

# new test after generating new IC files with ERA5 for L128v4 - also use newer master
kwargs_common= {'prefix':'2026-GW-DEV-01', 'compset':'F2010xx-ZM-CICE'}
# add_case(**kwargs_common, **kwargs_ne256, use_gw=True)

add_case(**kwargs_common, **kwargs_ne32, ic='old')
add_case(**kwargs_common, **kwargs_ne32, ic='new')


#---------------------------------------------------------------------------------------------------
def get_case_name(opts):
   # global debug_mode
   #----------------------------------------------------------------------------
   debug_mode = opts['debug'] if opts.get('debug') else False
   arch       = opts['arch']  if opts.get('arch')  else 'CPU'
   #----------------------------------------------------------------------------
   case_list = ['E3SM']
   for key,val in opts.items(): 
      if key in ['prefix','compset','arch','grid']: case_list.append(val)
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
   print(f' clean        : {clean}')
   print(f' newcase      : {newcase}')
   print(f' config       : {config}')
   print(f' build        : {build}')
   print(f' submit       : {submit}')
   print(f' continue_run : {continue_run}')
   #------------------------------------------------------------------------------------------------
   if 'num_nodes' in opts and 'num_tasks' in opts:
      raise ValueError('cannot specify both num_nodes and num_tasks!')
   if 'num_nodes' not in opts and 'num_tasks' not in opts:
      raise ValueError('you must specify either num_nodes of num_tasks!')
   #----------------------------------------------------------------------------
   debug_mode = opts['debug'] if opts.get('debug') else False
   arch       = opts['arch']  if opts.get('arch')  else 'CPU'
   #----------------------------------------------------------------------------
   # exit()
   #----------------------------------------------------------------------------
   if 'num_nodes' in opts:
      max_task_per_node,max_mpi_per_node,atm_nthrds  = 56,8,1
      # if arch=='GPU': max_mpi_per_node,atm_nthrds =   4,1
      # if arch=='CPU': max_mpi_per_node,atm_nthrds = 128,1
      # if arch=='CPU' and 'ne4pg2' in opts['grid']: max_mpi_per_node,atm_nthrds = 96,1
      atm_ntasks = max_mpi_per_node*opts['num_nodes']
   if 'num_tasks' in opts:
      atm_ntasks,atm_nthrds = opts['num_tasks'],1
   #----------------------------------------------------------------------------
   # if arch=='GPU': case_root = os.getenv('SCRATCH')+f'/scream_scratch/pm-gpu/{case}'
   # if arch=='CPU': case_root = os.getenv('SCRATCH')+f'/scream_scratch/pm-cpu/{case}'
   case_root = f'/lustre/orion/cli115/proj-shared/hannah6/e3sm_scratch/{case}'
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
      # if arch=='GPU': cmd += f' -mach pm-gpu -compiler gnugpu '
      # if arch=='CPU': cmd += f' -mach pm-cpu -compiler gnu '
      cmd += f' --machine=frontier --compiler=craygnu-mphipcc '
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
      # run_cmd('./xmlchange CICE_CPPDEFS="-DCCSMCOUPLED -Dcoupled -Dncdf -DNCAT=1 -DNXGLOB=1791 -DNYGLOB=1 -DNTR_AERO=0 -DMODAL_AER"')
      # run_cmd('./case.build --clean ice')
      run_cmd('./case.build')
   #------------------------------------------------------------------------------------------------
   if submit :
      run_cmd(f'./xmlchange SCREAM_ATMCHANGE_BUFFER=""') # reset the buffer
      #-------------------------------------------------------------------------
      run_cmd(f'./atmchange -b physics::mac_aero_mic::atm_procs_list="shoc,cld_fraction,spa,p3" ')
      if opts.get('use_gw') or opts.get('use_oro'):
         if '-ZM' in opts.get('compset'):
            run_cmd(f'./atmchange -b physics::atm_procs_list=zm,gw,mac_aero_mic,rrtmgp')
         else:   
            run_cmd(f'./atmchange -b physics::atm_procs_list=gw,mac_aero_mic,rrtmgp')
      #-------------------------------------------------------------------------
      if opts.get('use_gw'):
         run_cmd(f'./atmchange -b gw::use_gw_convect=True')
         run_cmd(f'./atmchange -b gw::use_gw_orographic=True')
         run_cmd(f'./atmchange gw::gw_convect_hcf=2')
      if opts.get('use_oro'):
         run_cmd(f'./atmchange -b gw::use_gw_orographic=True')
      #-------------------------------------------------------------------------
      # various v4BETA settings
      input_data_dir = '/lustre/orion/cli115/world-shared/e3sm/inputdata'
      run_cmd(f'./atmchange -b vertical_coordinate_filename="{input_data_dir}/atm/scream/init/vertical_coordinates_L128v4_c20260820.nc" ')
      if opts.get('grid')=='ne256pg2_ne256pg2':
         # run_cmd(f'./atmchange -b initial_conditions::filename="{input_data_dir}/atm/scream/init/screami_ne256np4L128v4_ifs-20200120_20260825.nc" ')
         # run_cmd(f'./atmchange -b initial_conditions::filename="{input_data_dir}/atm/scream/init/screami_ne256np4L128v4_ifs-20200120_20260911.nc" ')
         run_cmd(f'./atmchange -b initial_conditions::filename="/lustre/orion/cli115/proj-shared/hannah6/HICCUP/files_init/eamxxi_ne256np4L128v4_ERA5-20121001_c20260922.nc" ')
         # run_cmd(f'./atmchange -b initial_conditions::filename="/lustre/orion/cli115/proj-shared/hannah6/HICCUP/files_init/eamxxi_ne256np4L128v4_ERA5-20190101_c20260922.nc" ')
      if opts.get('grid')=='ne32pg2_ne32pg2':
         if opts.get('ic')=='new':
            run_cmd(f'./atmchange -b initial_conditions::filename="/lustre/orion/cli115/proj-shared/hannah6/HICCUP/files_init/eamxxi_ne32np4L128v4_ERA5-20121001_c20260922.nc" ')
         if opts.get('ic')=='old':
            run_cmd(f'./atmchange -b initial_conditions::filename="/lustre/orion/cli115/world-shared/e3sm/inputdata/atm/scream/init/eamxxi_ne32np4L128v4_v3.LR.amip_0101.eam.i.2000-01-01-00000.20260911.nc" ')
         # /lustre/orion/cli115/world-shared/e3sm/inputdata/atm/scream/init/*ne32*
      run_cmd(f'./atmchange -b tom_sponge_start=15 ')
      run_cmd(f'./atmchange -b laplace_scaling=1 ')
      run_cmd(f'./atmchange -b nu_top=5e-7 ')
      run_cmd(f'./atmchange -b theta_advect_form=2 ')
      run_cmd(f'./atmchange -b pgrad_correction=0 ')
      run_cmd(f'./atmchange -b spa_data_file="{input_data_dir}/atm/scream/init/spa_v3.LR.F2010.2011-2025.c_20240405.nc" ')
      run_cmd(f'./atmchange -b spa_ccn_to_nc_factor=750.0 ')
      run_cmd(f'./atmchange -b length_fac=0.51 ')
      run_cmd(f'./atmchange -b autoconversion_prefactor=2960.0 ')
      run_cmd(f'./atmchange -b autoconversion_qc_exponent=2.42 ')

      # run_cmd(f'./atmchange gw::enable_postcondition_checks=false')
      #-------------------------------------------------------------------------
      # experimental overrides
      if opts.get('tom_ss') is not None:
         run_cmd(f'./atmchange -b tom_sponge_start={opts.get("tom_ss")} ')
      #-------------------------------------------------------------------------
      # Enable tendency calculation for output
      # run_cmd(f'./atmchange -b shoc::compute_tendencies=T_mid')
      if 'F2010xx-ZM' in opts['compset']:
         run_cmd(f'./atmchange -b physics::zm::compute_tendencies=T_mid')
      #-------------------------------------------------------------------------
      hist_file_list = []
      def add_hist_file(hist_file,txt):
         file=open(hist_file,'w'); file.write(txt); file.close()
         hist_file_list.append(hist_file)
      #----------------------------------------------------------------------
      add_hist_file('output_debug.yaml',get_hist_opts_debug(opts))
      hist_file_list_str = ','.join(hist_file_list)
      run_cmd(f'./atmchange scorpio::output_yaml_files="{hist_file_list_str}"')
      #----------------------------------------------------------------------
      # print()
      # print(clr.RED+'WARNING - all output is disabled for debugging!'+clr.END)
      # print()
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
def get_hist_opts_debug(opts):
   return f'''
%YAML 1.1
---
filename_prefix: output.debug
averaging_type: instant
max_snapshots_per_file: 24
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
         - T_2m
         - U_at_model_bot
         - surf_sens_flux
         - surf_evap
         #------------------------------
         # - gw_oro_tend_u
         # - gw_oro_tend_v
         # - gw_oro_tend_t
         # - gw_conv_tend_u
         # - gw_conv_tend_v
         # - gw_conv_tend_t
         # - gw_conv_heating_depth
         # - gw_conv_heating_max
         #------------------------------
         - z_mid
         - T_mid
         - U
         - V
         #------------------------------
         # - zm_T_mid_tend
         - zm_prec
         #------------------------------
output_control:
   frequency: 1
   frequency_units: nhours
'''

#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':
   for n in range(len(opt_list)):
      main( opt_list[n] )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
