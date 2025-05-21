#!/usr/bin/env python3
import os, datetime, subprocess as sp
#---------------------------------------------------------------------------------------------------
class tcolor: END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
#---------------------------------------------------------------------------------------------------
def run_cmd(cmd,suppress_output=False):
   if suppress_output : cmd = cmd + ' > /dev/null'
   msg = tcolor.GREEN + cmd + tcolor.END ; print(f'\n{msg}')
   os.system(cmd); return
#---------------------------------------------------------------------------------------------------
def xmlquery(xmlvar):
   ( value, err) = sp.Popen(f'./xmlquery {xmlvar} --value', stdout=sp.PIPE, shell=True, universal_newlines=True).communicate()
   return value
#---------------------------------------------------------------------------------------------------
'''
Hassan's new recipe:

./atmchange autoconversion_prefactor=0.0011111

./atmchange autoconversion_qc_exponent=1.0
./atmchange autoconversion_nc_exponent=0.0
./atmchange accretion_prefactor=10.0
./atmchange rain_selfcollection_prefactor=0.0

./atmchange cldliq_to_ice_collection_factor=0.00001
./atmchange rain_to_ice_collection_factor=0.00001
./atmchange max_total_ni=74000000
'''  
#---------------------------------------------------------------------------------------------------
opt_list = []
def add_case( **kwargs ):
   case_opts = {}
   for k, val in kwargs.items(): case_opts[k] = val
   opt_list.append(case_opts)
#---------------------------------------------------------------------------------------------------
newcase,config,build,submit = False,False,False,False

acct = 'cli200'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC1' # master @ Jan 15 2025

newcase      = True
config       = True
build        = True
submit       = True

debug_mode = False

# queue,stop_opt,stop_n,resub,walltime = 'batch','ndays',10,0,'1:00:00'
queue,stop_opt,stop_n,resub,walltime = 'batch','ndays',1,0,'1:00:00'
# queue,stop_opt,stop_n,resub,walltime = 'batch','nhours',1,0,'0:10:00'

arch = 'GPU'
#---------------------------------------------------------------------------------------------------
#  8.33 / 16.66 / 50    / 100     12 / 2 /  6 / 1 (default )
#  8.33 / 16.66 / 100   / 100     12 / 2 / 12 / 2 
#  7.5  /  7.5  / 37.5  / 75      10 / 1 /  5 / 1
#  8.33 /  8.33 / 75    / 75       9 / 1 /  9 / 2
#  9.37 / 18.75 / 75    / 75       8 / 2 /  8 / 2
#  9.37 / 18.75 / 18.75 / 75       8 / 2 /  4 / 1
#  8.57 /  8.57 / 60    / 60       7 / 1 /  7 / 2
#  7.5  / 15    / 60    / 60       8 / 2 /  8 / 2
#  7.5  / 15    / 30    / 60       8 / 2 /  4 / 1
# 10.0  / 20    / 60    / 60       6 / 2 /  6 / 1
# 10.0  / 30    / 60    / 60       6 / 3 /  6 / 1
# 10.0  / 20    / 60    / 60       6 / 2 /  6 / 2
# 10.0  / 30    / 60    / 60       6 / 3 /  6 / 2
#---------------------------------------------------------------------------------------------------
# build list of cases to run

# add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne4pg2', num_nodes=1, dt_phy=100, dyn_fac=12, rmp_fac=2, trc_fac= 6, trc_ss=1 )
# add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne4pg2', num_nodes=1, dt_phy=100, dyn_fac=12, rmp_fac=2, trc_fac=12, trc_ss=2 )
# add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne4pg2', num_nodes=1, dt_phy= 75, dyn_fac=10, rmp_fac=1, trc_fac= 5, trc_ss=1 )
# add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne4pg2', num_nodes=1, dt_phy= 75, dyn_fac= 9, rmp_fac=1, trc_fac= 9, trc_ss=2 )
# add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne4pg2', num_nodes=1, dt_phy= 75, dyn_fac= 8, rmp_fac=2, trc_fac= 8, trc_ss=2 )
# add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne4pg2', num_nodes=1, dt_phy= 75, dyn_fac= 8, rmp_fac=2, trc_fac= 4, trc_ss=1 )
# add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne4pg2', num_nodes=1, dt_phy= 60, dyn_fac= 7, rmp_fac=1, trc_fac= 7, trc_ss=2 )
# add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne4pg2', num_nodes=1, dt_phy= 60, dyn_fac= 8, rmp_fac=2, trc_fac= 8, trc_ss=2 )
# add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne4pg2', num_nodes=1, dt_phy= 60, dyn_fac= 8, rmp_fac=2, trc_fac= 4, trc_ss=1 )
# add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne4pg2', num_nodes=1, dt_phy= 60, dyn_fac= 6, rmp_fac=2, trc_fac= 6, trc_ss=1 )
# add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne4pg2', num_nodes=1, dt_phy= 60, dyn_fac= 6, rmp_fac=3, trc_fac= 6, trc_ss=1 )
# add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne4pg2', num_nodes=1, dt_phy= 60, dyn_fac= 6, rmp_fac=2, trc_fac= 6, trc_ss=2 )
# add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne4pg2', num_nodes=1, dt_phy= 60, dyn_fac= 6, rmp_fac=3, trc_fac= 6, trc_ss=2 )

# add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne30pg2', num_nodes=8, dt_phy=100, dyn_fac=12, rmp_fac=2, trc_fac= 6, trc_ss=1 )
# add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne30pg2', num_nodes=8, dt_phy=100, dyn_fac=12, rmp_fac=2, trc_fac=12, trc_ss=2 )
# add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne30pg2', num_nodes=8, dt_phy= 75, dyn_fac=10, rmp_fac=1, trc_fac= 5, trc_ss=1 )
# add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne30pg2', num_nodes=8, dt_phy= 75, dyn_fac= 9, rmp_fac=1, trc_fac= 9, trc_ss=2 )
# add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne30pg2', num_nodes=8, dt_phy= 75, dyn_fac= 8, rmp_fac=2, trc_fac= 8, trc_ss=2 )
# add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne30pg2', num_nodes=8, dt_phy= 75, dyn_fac= 8, rmp_fac=2, trc_fac= 4, trc_ss=1 )
# add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne30pg2', num_nodes=8, dt_phy= 60, dyn_fac= 7, rmp_fac=1, trc_fac= 7, trc_ss=2 )
# add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne30pg2', num_nodes=8, dt_phy= 60, dyn_fac= 8, rmp_fac=2, trc_fac= 8, trc_ss=2 )
# add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne30pg2', num_nodes=8, dt_phy= 60, dyn_fac= 8, rmp_fac=2, trc_fac= 4, trc_ss=1 )
# add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne30pg2', num_nodes=8, dt_phy= 60, dyn_fac= 6, rmp_fac=2, trc_fac= 6, trc_ss=1 )
# add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne30pg2', num_nodes=8, dt_phy= 60, dyn_fac= 6, rmp_fac=3, trc_fac= 6, trc_ss=1 )
# add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne30pg2', num_nodes=8, dt_phy= 60, dyn_fac= 6, rmp_fac=2, trc_fac= 6, trc_ss=2 )
# add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne30pg2', num_nodes=8, dt_phy= 60, dyn_fac= 6, rmp_fac=3, trc_fac= 6, trc_ss=2 )

# tmp_num_nodes = 192
# add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne256pg2', num_nodes=tmp_num_nodes, dt_phy=100, dyn_fac=12, rmp_fac=2, trc_fac= 6, trc_ss=1 )
# add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne256pg2', num_nodes=tmp_num_nodes, dt_phy=100, dyn_fac=12, rmp_fac=2, trc_fac=12, trc_ss=2 )
# add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne256pg2', num_nodes=tmp_num_nodes, dt_phy= 75, dyn_fac=10, rmp_fac=1, trc_fac= 5, trc_ss=1 )
# add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne256pg2', num_nodes=tmp_num_nodes, dt_phy= 75, dyn_fac= 9, rmp_fac=1, trc_fac= 9, trc_ss=2 )
# add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne256pg2', num_nodes=tmp_num_nodes, dt_phy= 75, dyn_fac= 8, rmp_fac=2, trc_fac= 8, trc_ss=2 )
# add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne256pg2', num_nodes=tmp_num_nodes, dt_phy= 75, dyn_fac= 8, rmp_fac=2, trc_fac= 4, trc_ss=1 )
# add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne256pg2', num_nodes=tmp_num_nodes, dt_phy= 60, dyn_fac= 8, rmp_fac=2, trc_fac= 8, trc_ss=2 )
# add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne256pg2', num_nodes=tmp_num_nodes, dt_phy= 60, dyn_fac= 8, rmp_fac=2, trc_fac= 4, trc_ss=1 )
# add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne256pg2', num_nodes=tmp_num_nodes, dt_phy= 60, dyn_fac= 7, rmp_fac=1, trc_fac= 7, trc_ss=2 )

# tmp_num_nodes = 2048
# add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne1024pg2', num_nodes=tmp_num_nodes, dt_phy=100, dyn_fac=12, rmp_fac=2, trc_fac= 6, trc_ss=1 )
# add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne1024pg2', num_nodes=tmp_num_nodes, dt_phy=100, dyn_fac=12, rmp_fac=2, trc_fac=12, trc_ss=2 )
# add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne1024pg2', num_nodes=tmp_num_nodes, dt_phy= 75, dyn_fac=10, rmp_fac=1, trc_fac= 5, trc_ss=1 )
# add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne1024pg2', num_nodes=tmp_num_nodes, dt_phy= 75, dyn_fac= 9, rmp_fac=1, trc_fac= 9, trc_ss=2 )
# add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne1024pg2', num_nodes=tmp_num_nodes, dt_phy= 75, dyn_fac= 8, rmp_fac=2, trc_fac= 8, trc_ss=2 )
# add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne1024pg2', num_nodes=tmp_num_nodes, dt_phy= 75, dyn_fac= 8, rmp_fac=2, trc_fac= 4, trc_ss=1 )
# add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne1024pg2', num_nodes=tmp_num_nodes, dt_phy= 60, dyn_fac= 8, rmp_fac=2, trc_fac= 8, trc_ss=2 )
# add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne1024pg2', num_nodes=tmp_num_nodes, dt_phy= 60, dyn_fac= 8, rmp_fac=2, trc_fac= 4, trc_ss=1 )
# add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne1024pg2', num_nodes=tmp_num_nodes, dt_phy= 60, dyn_fac= 7, rmp_fac=1, trc_fac= 7, trc_ss=2 )
### add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne1024pg2', num_nodes=tmp_num_nodes, dt_phy= 60, dyn_fac= 6, rmp_fac=2, trc_fac= 6, trc_ss=1 )
### add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne1024pg2', num_nodes=tmp_num_nodes, dt_phy= 60, dyn_fac= 6, rmp_fac=3, trc_fac= 6, trc_ss=1 )
### add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne1024pg2', num_nodes=tmp_num_nodes, dt_phy= 60, dyn_fac= 6, rmp_fac=2, trc_fac= 6, trc_ss=2 )
### add_case(prefix='2025-DT-00', compset='F2010-SCREAMv1', grid='ne1024pg2', num_nodes=tmp_num_nodes, dt_phy= 60, dyn_fac= 6, rmp_fac=3, trc_fac= 6, trc_ss=2 )


# # for 2025-DT-01 enable restarts and time-step history output
# tmp_num_nodes = 2048
# add_case(prefix='2025-DT-01', compset='F2010-SCREAMv1', grid='ne1024pg2', num_nodes=tmp_num_nodes, dt_phy=100, dyn_fac=12, rmp_fac=2, trc_fac= 6, trc_ss=1 )
# add_case(prefix='2025-DT-01', compset='F2010-SCREAMv1', grid='ne1024pg2', num_nodes=tmp_num_nodes, dt_phy=100, dyn_fac=12, rmp_fac=2, trc_fac=12, trc_ss=2 )
# add_case(prefix='2025-DT-01', compset='F2010-SCREAMv1', grid='ne1024pg2', num_nodes=tmp_num_nodes, dt_phy= 75, dyn_fac=10, rmp_fac=1, trc_fac= 5, trc_ss=1 )
# add_case(prefix='2025-DT-01', compset='F2010-SCREAMv1', grid='ne1024pg2', num_nodes=tmp_num_nodes, dt_phy= 75, dyn_fac= 9, rmp_fac=1, trc_fac= 9, trc_ss=2 )
# add_case(prefix='2025-DT-01', compset='F2010-SCREAMv1', grid='ne1024pg2', num_nodes=tmp_num_nodes, dt_phy= 75, dyn_fac= 8, rmp_fac=2, trc_fac= 8, trc_ss=2 )
# add_case(prefix='2025-DT-01', compset='F2010-SCREAMv1', grid='ne1024pg2', num_nodes=tmp_num_nodes, dt_phy= 75, dyn_fac= 8, rmp_fac=2, trc_fac= 4, trc_ss=1 )
# add_case(prefix='2025-DT-01', compset='F2010-SCREAMv1', grid='ne1024pg2', num_nodes=tmp_num_nodes, dt_phy= 60, dyn_fac= 8, rmp_fac=2, trc_fac= 8, trc_ss=2 )
# add_case(prefix='2025-DT-01', compset='F2010-SCREAMv1', grid='ne1024pg2', num_nodes=tmp_num_nodes, dt_phy= 60, dyn_fac= 8, rmp_fac=2, trc_fac= 4, trc_ss=1 )
# add_case(prefix='2025-DT-01', compset='F2010-SCREAMv1', grid='ne1024pg2', num_nodes=tmp_num_nodes, dt_phy= 60, dyn_fac= 7, rmp_fac=1, trc_fac= 7, trc_ss=2 )

# for 2025-DT-02 use special low-res output to make analysis more tractable
tmp_num_nodes = 2048
add_case(prefix='2025-DT-02', compset='F2010-SCREAMv1', grid='ne1024pg2', num_nodes=tmp_num_nodes, dt_phy=100, dyn_fac=12, rmp_fac=2, trc_fac= 6, trc_ss=1 )
# add_case(prefix='2025-DT-02', compset='F2010-SCREAMv1', grid='ne1024pg2', num_nodes=tmp_num_nodes, dt_phy=100, dyn_fac=12, rmp_fac=2, trc_fac=12, trc_ss=2 )
# add_case(prefix='2025-DT-02', compset='F2010-SCREAMv1', grid='ne1024pg2', num_nodes=tmp_num_nodes, dt_phy= 75, dyn_fac=10, rmp_fac=1, trc_fac= 5, trc_ss=1 )
# add_case(prefix='2025-DT-02', compset='F2010-SCREAMv1', grid='ne1024pg2', num_nodes=tmp_num_nodes, dt_phy= 75, dyn_fac= 9, rmp_fac=1, trc_fac= 9, trc_ss=2 )
# add_case(prefix='2025-DT-02', compset='F2010-SCREAMv1', grid='ne1024pg2', num_nodes=tmp_num_nodes, dt_phy= 75, dyn_fac= 8, rmp_fac=2, trc_fac= 8, trc_ss=2 )
# add_case(prefix='2025-DT-02', compset='F2010-SCREAMv1', grid='ne1024pg2', num_nodes=tmp_num_nodes, dt_phy= 75, dyn_fac= 8, rmp_fac=2, trc_fac= 4, trc_ss=1 )
# add_case(prefix='2025-DT-02', compset='F2010-SCREAMv1', grid='ne1024pg2', num_nodes=tmp_num_nodes, dt_phy= 60, dyn_fac= 8, rmp_fac=2, trc_fac= 8, trc_ss=2 )
# add_case(prefix='2025-DT-02', compset='F2010-SCREAMv1', grid='ne1024pg2', num_nodes=tmp_num_nodes, dt_phy= 60, dyn_fac= 8, rmp_fac=2, trc_fac= 4, trc_ss=1 )
# add_case(prefix='2025-DT-02', compset='F2010-SCREAMv1', grid='ne1024pg2', num_nodes=tmp_num_nodes, dt_phy= 60, dyn_fac= 7, rmp_fac=1, trc_fac= 7, trc_ss=2 )


native_res,remap_res = 'ne1024pg2','ne30pg2'
hist_map = '/lustre/orion/cli115/world-shared/e3sm/inputdata/atm/scream/maps/map_ne1024pg2_to_ne30pg2_traave.20240206.nc'

# native_res,remap_res = 'ne256pg2','ne30pg2'
# hist_map = '/lustre/orion/cli115/world-shared/e3sm/inputdata/atm/scream/maps/map_ne256pg2_to_ne30pg2_traave.20240206.cdf5.nc'

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

   if debug_mode: case = case+'.debug'

   print(f'\n  case : {case}\n')

   # exit()

   #------------------------------------------------------------------------------------------------
   case_root = f'/lustre/orion/cli115/proj-shared/hannah6/e3sm_scratch/{case}'

   num_nodes = opts['num_nodes']
   # if arch=='CPU': max_mpi_per_node,atm_nthrds  = 128,1 ; max_task_per_node = 128
   # if arch=='GPU': max_mpi_per_node,atm_nthrds  =   4,8 ; max_task_per_node = 32
   if arch=='CPU': max_task_per_node,max_mpi_per_node,atm_nthrds  = 56,56,1
   if arch=='GPU': max_task_per_node,max_mpi_per_node,atm_nthrds  = 56,8,1
   atm_ntasks = max_mpi_per_node*num_nodes

   grid    = opts['grid']+'_'+opts['grid']
   compset = opts['compset']
   #------------------------------------------------------------------------------------------------
   # Create new case
   if newcase:
      if os.path.isdir(case_root): exit(f'\n{tcolor.RED}This case already exists!{tcolor.END}\n')
      cmd = f'{src_dir}/cime/scripts/create_newcase'
      cmd += f' --case {case}'
      cmd += f' --output-root {case_root} '
      cmd += f' --script-root {case_root}/case_scripts '
      cmd += f' --handle-preexisting-dirs u '
      cmd += f' --compset {compset}'
      cmd += f' --res {grid} '
      cmd += f' --project {acct} '
      if arch=='CPU': cmd+=f' -mach frontier -compiler crayclang'
      if arch=='GPU': cmd+=f' -mach frontier-scream-gpu -compiler crayclang-scream'
      cmd += f' -pecount {atm_ntasks}x{atm_nthrds} '
      run_cmd(cmd)
      #----------------------------------------------------------------------------
      # # Copy this run script into the case directory
      # timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%d.%H%M%S')
      # run_cmd(f'cp {os.path.realpath(__file__)} {case_dir}/{case}/run_script.{timestamp}.py')
   #------------------------------------------------------------------------------------------------
   os.chdir(f'{case_root}/case_scripts')
   #------------------------------------------------------------------------------------------------
   if config:
      run_cmd(f'./xmlchange EXEROOT={case_root}/bld ')
      run_cmd(f'./xmlchange RUNDIR={case_root}/run ')
      #-------------------------------------------------------------------------
      run_cmd(f'./xmlchange PIO_NETCDF_FORMAT="64bit_data"')
      run_cmd(f'./xmlchange PIO_TYPENAME=pnetcdf') #adios #,PIO_TYPENAME_ATM=adios
      run_cmd(f'./xmlchange PIO_REARRANGER=1')  # use PIO_REARRANGER=3, for ADIOS; PIO_REARRANGER=1 for pnetcdf
      #-------------------------------------------------------------------------
      # if init_file is not None: run_cmd(f'./atmchange initial_conditions::Filename=\"{init_file}\"')
      #-------------------------------------------------------------------------
      # if clean : run_cmd('./case.setup --clean')
      run_cmd('./case.setup --reset')

   #------------------------------------------------------------------------------------------------
   if build:
      if debug_mode: run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
      # if clean : run_cmd('./case.build --clean')
      run_cmd('./case.build')
   #------------------------------------------------------------------------------------------------
   if submit:
      #-------------------------------------------------------------------------
      dt_phy  = opts['dt_phy']
      dyn_fac = opts['dyn_fac']
      rmp_fac = opts['rmp_fac']
      trc_fac = opts['trc_fac']
      trc_ss  = opts['trc_ss']

      ncpl = int(24*60*60/dt_phy)
      dt_dyn = dt_phy / dyn_fac

      run_cmd(f'./xmlchange ATM_NCPL'                             +f'={ncpl}')
      run_cmd(f'./atmchange -b se_tstep'                          +f'={dt_dyn}')
      run_cmd(f'./atmchange -b dt_remap_factor'                   +f'={rmp_fac}')
      run_cmd(f'./atmchange -b dt_tracer_factor'                  +f'={trc_fac}')
      run_cmd(f'./atmchange -b hypervis_subcycle_q'               +f'={trc_fac}')
      run_cmd(f'./atmchange -b semi_lagrange_trajectory_nsubstep' +f'={trc_ss}')

      run_cmd(f'./atmchange -b semi_lagrange_halo=-1')

      # need to set this in low-res grids to emulate ne1024 configuration
      run_cmd(f'./atmchange -b physics::mac_aero_mic::number_of_subcycles=1')
      
      #-------------------------------------------------------------------------
      hist_file_list = []
      def add_hist_file(hist_file,txt):
         file=open(hist_file,'w'); file.write(txt); file.close()
         hist_file_list.append(hist_file)
      #-------------------------------------------------------------------------
#       hist_opts_2D = f'''
# %YAML 1.1
# ---
# filename_prefix: output.scream.2D
# Averaging Type: Instant
# Max Snapshots Per File: {ncpl}
# Fields:
#    Physics PG2:
#       Field Names:{field_txt_2D}
# output_control:
#    Frequency: 1
#    frequency_units: nsteps
#    MPI Ranks in Filename: false
# Restart:
#    force_new_file: true
# '''
      #-------------------------------------------------------------------------
      def get_hist_yaml_txt(ncpl,hvar):
         return f'''
%YAML 1.1
---
filename_prefix: output.scream.2D
Averaging Type: Instant
Max Snapshots Per File: {ncpl}
Fields:
   Physics PG2:
      Field Names: 
      - {hvar}
output_control:
   Frequency: 1
   frequency_units: nsteps
   MPI Ranks in Filename: false
Restart:
   force_new_file: true
'''
      #-------------------------------------------------------------------------
      hvar_list = []
      hvar_list.append('precip_total_surf_mass_flux')
      hvar_list.append('LiqWaterPath')
      hvar_list.append('surf_sens_flux')
      hvar_list.append('surf_evap')
      hvar_list.append('surf_mom_flux_U')
      hvar_list.append('surf_mom_flux_V')
      hvar_list.append('U_at_model_bot')
      hvar_list.append('V_at_model_bot')
      if opts['prefix']=='2025-DT-02':
         for hvar in hvar_list:
            add_hist_file(f'scream_output_2D_1step_inst_{hvar}.yaml',get_hist_yaml_txt(ncpl,hvar))
         hist_file_list_str = ','.join(hist_file_list)
         run_cmd(f'./atmchange Scorpio::output_yaml_files="{hist_file_list_str}"')
      #-------------------------------------------------------------------------
      if opts['prefix']=='2025-DT-01':
         add_hist_file('scream_output_2D_1step_inst.yaml',hist_opts_2D)
         # add_hist_file('scream_output_2D_1hr_inst.yaml',hist_opts_2D_1hr_inst)
         # add_hist_file('scream_output_3D_1dy_mean.yaml',hist_opts_3D_1dy_mean)
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
      #-------------------------------------------------------------------------
      # disable restarts for timing
      if opts['prefix']=='2025-DT-00':
         run_cmd('./xmlchange --file env_run.xml --id REST_OPTION --val never')
      #-------------------------------------------------------------------------
      # run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')
      # if     continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=TRUE ')   
      # if not continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=FALSE ')
      #-------------------------------------------------------------------------
      # Submit the run
      # run_cmd('./case.submit')
      run_cmd(f'./case.submit -a=" -x frontier08656 " ')
   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {case}\n') 
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
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

# field_txt_2D = '''
#       - precip_total_surf_mass_flux
#       - LiqWaterPath
#       - surf_sens_flux
#       - surf_evap
#       - surf_mom_flux
#       - U_at_model_bot
#       - V_at_model_bot
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


hist_opts_3D_1dy_mean = f'''
%YAML 1.1
---
filename_prefix: output.scream.3D.1dy
Averaging Type: Average
Max Snapshots Per File: 1
Fields:
   Physics PG2:
      Field Names:{field_txt_3D}
output_control:
   Frequency: 1
   frequency_units: ndays
   MPI Ranks in Filename: false
Restart:
   force_new_file: true
'''
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':
   for n in range(len(opt_list)):
      main( opt_list[n] )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
