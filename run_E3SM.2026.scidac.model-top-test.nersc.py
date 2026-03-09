#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np
from shutil import copy2
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
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm4310'
src_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC1' # branch => whannah/scidac-2025-multifidelity-rebase

# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
# continue_run = True

queue = 'regular' # regular / debug

# stop_opt,stop_n,resub,walltime = 'ndays',1,0,'0:30:00'
# stop_opt,stop_n,resub,walltime = 'ndays',4,8-1,'0:30:00'
# stop_opt,stop_n,resub,walltime = 'ndays',73,4-1,'1:00:00'
stop_opt,stop_n,resub,walltime = 'ndays',365,5-1,'6:00:00'

#---------------------------------------------------------------------------------------------------
### model top sensitivity tests

prfx = '2026-model-top-test-00'
grid = 'ne30pg2_r05_IcoswISC30E3r5'

# add_case(prefix=prfx,grid=grid,compset='F20TR',num_nodes=8)
add_case(prefix=prfx,grid=grid,compset='F20TR',num_nodes=8,top_km=55)
add_case(prefix=prfx,grid=grid,compset='F20TR',num_nodes=8,top_km=50)
add_case(prefix=prfx,grid=grid,compset='F20TR',num_nodes=8,top_km=45)
add_case(prefix=prfx,grid=grid,compset='F20TR',num_nodes=8,top_km=40)
add_case(prefix=prfx,grid=grid,compset='F20TR',num_nodes=8,top_km=35)
# add_case(prefix=prfx,grid=grid,compset='F20TR',num_nodes=8,top_km=30)
add_case(prefix=prfx,grid=grid,compset='F20TR',num_nodes=8,top_km=25)
add_case(prefix=prfx,grid=grid,compset='F20TR',num_nodes=8,top_km=20)

#---------------------------------------------------------------------------------------------------
def get_atm_init_file(opts):
   atm_init_file = None
   if 'top_km' in opts:
      top_km = opts['top_km']
      atm_init_root = '/pscratch/sd/w/whannah/e3sm_scratch/init_scratch/truncated_L80_initial_conditions'
      atm_init_file = f'{atm_init_root}/eami_mam4_Linoz_ne30np4_L80_c20231010.truncated_top_{top_km}km.nc'
   return atm_init_file
#---------------------------------------------------------------------------------------------------
def get_nlev_mid(opts):
   nlev_mid = None
   if 'top_km' in opts:
      top_km = opts['top_km']
      if top_km==20: nlev_mid = 55
      if top_km==25: nlev_mid = 63
      if top_km==30: nlev_mid = 67
      if top_km==35: nlev_mid = 70
      if top_km==40: nlev_mid = 72
      if top_km==45: nlev_mid = 74
      if top_km==50: nlev_mid = 76
      if top_km==55: nlev_mid = 78
   return nlev_mid
#---------------------------------------------------------------------------------------------------
def write_atm_namelist(opts):
   atm_init_file = get_atm_init_file(opts)
   nfile = 'user_nl_eam'
   file = open(nfile,'w')
   file.write(' nhtfrq    = 0,-6 \n')
   file.write(' mfilt     = 1,20 \n')
   # file.write(" avgflag_pertape = 'A','I' \n")
   file.write(" fincl1 = 'PS','Z3','CLDLIQ','CLDICE','BUTGWSPEC','UTGWORO','UTGWSPEC','FRONTGF'")
   file.write(         ",'Uzm','Vzm','Wzm','THzm','VTHzm','WTHzm','UVzm','UWzm','PSzm'")
   file.write("\n")
   file.write(" fincl2 = 'PS','PRECT','FLUT','U850','U200','U10' ")
   file.write('\n')
   file.write(f' phys_grid_ctem_zm_nbas = 120 \n') # number of TEM basis functions
   file.write(f' phys_grid_ctem_za_nlat = 90 \n') # number of TEM  latitude points
   file.write(f' phys_grid_ctem_nfreq = -1 \n') # freq of TEM diag calcs (neg=>hours)
   if atm_init_file is not None:
      file.write(f' ncdata = \"{atm_init_file}\" \n')
   file.write('\n')
   file.close()
#---------------------------------------------------------------------------------------------------
def main(opts):
   global debug_mode

   compset   = opts['compset']
   grid      = opts['grid']
   num_nodes = opts['num_nodes']

   case_list = ['E3SM']
   for key,val in opts.items(): 
      if key in ['prefix','compset']:  case_list.append(val)
      elif key in ['grid']:            case_list.append(val.split('_')[0])
      elif key in ['num_nodes']:       case_list.append(f'NN_{val}')
      elif key in ['debug']:           case_list.append('debug')
      else:
         if isinstance(val, str):
            case_list.append(f'{key}_{val}')
         else:
            case_list.append(f'{key}_{val:g}')
   case = '.'.join(case_list)

   # clean up the exponential numbers in the case name
   for i in range(1,9+1): case = case.replace(f'e+0{i}',f'e{i}')
   #----------------------------------------------------------------------------
   print(f'\n  case : {case}\n')
   #----------------------------------------------------------------------------
   # exit()
   # return
   #----------------------------------------------------------------------------
   max_mpi_per_node,atm_nthrds  = 128,1 
   atm_ntasks = max_mpi_per_node*num_nodes
   case_root = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/{case}'
   #------------------------------------------------------------------------------------------------
   if newcase :
      if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
      cmd = f'{src_dir}/cime/scripts/create_newcase'
      cmd += f' --mach pm-cpu --pecount {atm_ntasks}x{atm_nthrds} '
      cmd += f' --case {case} --handle-preexisting-dirs u '
      cmd += f' --output-root {case_root} '
      cmd += f' --script-root {case_root}/case_scripts '
      cmd += f' --compset {compset} --res {grid} '
      cmd += f' --project {acct} '
      run_cmd(cmd)
   #------------------------------------------------------------------------------------------------
   os.chdir(f'{case_root}/case_scripts')
   #------------------------------------------------------------------------------------------------
   if config :
      run_cmd(f'./xmlchange EXEROOT={case_root}/bld ')
      run_cmd(f'./xmlchange RUNDIR={case_root}/run ')
      #-------------------------------------------------------------------------
      nlev_mid = get_nlev_mid(opts)
      if nlev_mid is not None:
         run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val=\' -nlev {nlev_mid} \'')
         write_atm_namelist(opts)
      #-------------------------------------------------------------------------
      # run_cmd('./xmlchange --id CAM_CONFIG_OPTS --append --val=\'-cosp\' ')
      #-------------------------------------------------------------------------
      run_cmd('./xmlchange PIO_NETCDF_FORMAT=\"64bit_data\" ')
      run_cmd('./case.setup --reset')
   #------------------------------------------------------------------------------------------------
   if build :
      if 'debug' in opts:
         if opts['debug']: run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
      if clean : run_cmd('./case.build --clean')
      run_cmd('./case.build')
   #------------------------------------------------------------------------------------------------
   if submit :
      #----------------------------------------------------------------------------
      # Namelist options
      write_atm_namelist(opts)
      #----------------------------------------------------------------------------
      # file=open('user_nl_elm','w')
      # file.write(f"finidat = '' \n")
      # file.close()
      #-------------------------------------------------------------------------
      if not continue_run: run_cmd(f'./xmlchange --file env_run.xml RUN_STARTDATE=1995-01-01')
      #-------------------------------------------------------------------------
      # Set some run-time stuff
      if 'stop_opt' in globals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
      if 'stop_n'   in globals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
      if 'queue'    in globals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
      if 'resub'    in globals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
      if 'walltime' in globals(): run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
      #-------------------------------------------------------------------------
      if     continue_run: run_cmd('./xmlchange CONTINUE_RUN=TRUE ')   
      if not continue_run: run_cmd('./xmlchange CONTINUE_RUN=FALSE ')
   #------------------------------------------------------------------------------------------------
   if submit :
      run_cmd('./case.submit')
   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {case}\n') 
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':
   for n in range(len(opt_list)):
      main( opt_list[n] )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
