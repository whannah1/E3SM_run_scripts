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
newcase,config,build,clean,set_opts,submit,continue_run = False,False,False,False,False,False,False

acct = 'e3sm'
src_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC1' # branch => 

# clean        = True
# newcase      = True
# config       = True
# build        = True
set_opts     = True
submit       = True
# continue_run = True

queue = 'regular' # regular / debug

stop_opt,stop_n,resub,walltime = 'ndays',5,0,'0:30:00'
# stop_opt,stop_n,resub,walltime = 'ndays',4,8-1,'0:30:00'
# stop_opt,stop_n,resub,walltime = 'ndays',365,0,'6:00:00'
# stop_opt,stop_n,resub,walltime = 'ndays',365*4,0,'12:00:00' # should work for 10+ sypd

#---------------------------------------------------------------------------------------------------

# add_case(prefix='2025-frnt-gw',grid='ne30pg2_r05_IcoswISC30E3r5',compset='F20TR',num_nodes=32,bugfix=0)
# add_case(prefix='2025-frnt-gw',grid='ne30pg2_r05_IcoswISC30E3r5',compset='F20TR',num_nodes=32,bugfix=1)

add_case(prefix='2025-frnt-gw-01',grid='ne30pg2_r05_IcoswISC30E3r5',compset='F20TR',num_nodes=32,bugfix=0) # time step output
add_case(prefix='2025-frnt-gw-01',grid='ne30pg2_r05_IcoswISC30E3r5',compset='F20TR',num_nodes=32,bugfix=1) # time step output

#---------------------------------------------------------------------------------------------------
def get_case_name(opts):
   case_list = ['E3SM']
   for key,val in opts.items(): 
      if key in ['prefix','compset']:
         case_list.append(val)
      elif key in ['grid']:
         case_list.append(val.split('_')[0])
      elif key in ['num_nodes']:
         case_list.append(f'NN_{val}')
         # continue
      elif key in ['debug']:
         case_list.append('debug')
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
   global debug_mode

   compset   = opts['compset']
   grid      = opts['grid']
   num_nodes = opts['num_nodes']

   case = get_case_name(opts)

   # case_list = ['E3SM']
   # for key,val in opts.items(): 
   #    if key in ['prefix','compset']:
   #       case_list.append(val)
   #    elif key in ['grid']:
   #       case_list.append(val.split('_')[0])
   #    elif key in ['num_nodes']:
   #       case_list.append(f'NN_{val}')
   #       # continue
   #    elif key in ['debug']:
   #       case_list.append('debug')
   #    else:
   #       if isinstance(val, str):
   #          case_list.append(f'{key}_{val}')
   #       else:
   #          case_list.append(f'{key}_{val:g}')
   # case = '.'.join(case_list)

   # # clean up the exponential numbers in the case name
   # for i in range(1,9+1): case = case.replace(f'e+0{i}',f'e{i}')
   #----------------------------------------------------------------------------
   print(f'\n  case : {case}\n')
   #----------------------------------------------------------------------------
   # exit()
   # return
   #----------------------------------------------------------------------------
   max_mpi_per_node,atm_nthrds = 64,1
   atm_ntasks = max_mpi_per_node*num_nodes
   case_root = f'/lcrc/group/e3sm/ac.whannah/scratch/chrys/{case}'
   #------------------------------------------------------------------------------------------------
   if newcase :
      if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
      cmd = f'{src_dir}/cime/scripts/create_newcase'
      cmd += f' --pecount {atm_ntasks}x{atm_nthrds} '
      cmd += f' --case {case} --handle-preexisting-dirs u '
      cmd += f' --output-root {case_root} '
      cmd += f' --script-root {case_root}/case_scripts '
      cmd += f' --compset {compset} --res {grid} '
      cmd += f' --project {acct} '
      cmd += f' --mach chrysalis --compiler gnu'
      run_cmd(cmd)
   #------------------------------------------------------------------------------------------------
   os.chdir(f'{case_root}/case_scripts')
   #------------------------------------------------------------------------------------------------
   if config :
      run_cmd(f'./xmlchange EXEROOT={case_root}/bld ')
      run_cmd(f'./xmlchange RUNDIR={case_root}/run ')
      #-------------------------------------------------------------------------
      if 'bugfix' in opts:
         if opts['bugfix']:
            run_cmd('./xmlchange --id CAM_CONFIG_OPTS --append --val \" -cppdefs \' -DFIX_FRONTAL_BUG \'  \" ')
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
      nfile = 'user_nl_eam'
      file = open(nfile,'w')

      # file.write(f' ncdata = \"{atm_init_file}\"') # no need for this since init files are set by default

      file.write(' nhtfrq    = 0,-3,1 \n')
      file.write(' mfilt     = 1,8,48 \n')
      file.write(" avgflag_pertape = 'A','I' \n")
      # file.write(" avgflag_pertape = 'A','A','I' \n")
      file.write(" fincl1 = 'Z3','CLDLIQ','CLDICE','BUTGWSPEC','UTGWORO','UTGWSPEC','FRONTGF'")
      # file.write(         ",'Uzm','Vzm','Wzm','THzm','VTHzm','WTHzm','UVzm','UWzm','PSzm'")
      file.write("\n")
      file.write(" fincl2 = 'PS','PRECT','FLUT','U850','U200','U600','V600','T600','FRONTGF','UTGWSPEC' ")
      file.write("\n")
      file.write(" fincl3 = 'PS','U','V','FRONTGF','UTGWSPEC', 'VTGWSPEC' ")
      file.write(         ",'TAUNET','TAUE','TAUW','TAUN','TAUS'")  # C&M reynold's stress
      file.write(         ",'UTEND1'") # U tendency   c < -40
      file.write(         ",'UTEND2'") # U tendency  -40 < c < -15
      file.write(         ",'UTEND3'") # U tendency  -15 < c <  15
      file.write(         ",'UTEND4'") # U tendency   15 < c <  40
      file.write(         ",'UTEND5'") # U tendency   40 < c 
      file.write(         ",'EMF','WMF','NMF','SMF'") # C&M momentum fluxes
      file.write('\n')
      # file.write(f' phys_grid_ctem_zm_nbas = 120 \n') # Number of basis functions used for TEM
      # file.write(f' phys_grid_ctem_za_nlat = 90 \n') # Number of latitude points for TEM
      # file.write(f' phys_grid_ctem_nfreq = -1 \n') # Frequency of TEM diagnostic calculations (neg => hours)
      if 'pgrad_correct' in opts:
         if opts['pgrad_correct']:
            file.write(f' use_fgf_pgrad_correction = .true. \n')
      if 'zgrad_correct' in opts:
         if opts['zgrad_correct']:
            file.write(f' use_fgf_zgrad_correction = .true. \n')

      file.write('\n')
      
      file.close()
      #----------------------------------------------------------------------------
      # file=open('user_nl_elm','w')
      # file.write(f"finidat = '' \n")
      # file.close()
      #-------------------------------------------------------------------------
      if not continue_run: run_cmd(f'./xmlchange --file env_run.xml RUN_STARTDATE=1985-01-01')
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
