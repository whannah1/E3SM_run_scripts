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
src_dir = os.getenv('HOME')+'/E3SM/E3SM_SRC4' # master @ March 12 2025 + 5e1580a0912dbe2ea019b525ed9df57fd1982ebf

# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
continue_run = True

# stop_opt,stop_n,resub,walltime = 'ndays',1,0,'0:30:00'
# stop_opt,stop_n,resub,walltime = 'ndays',10,0,'0:30:00'
stop_opt,stop_n,resub,walltime = 'ndays',365,5-1,'4:00:00'

compset='F2010'
grid = f'ne30pg2_r05_IcoswISC30E3r5'
num_nodes = 32


add_case(prefix='2025-SCIDAC-SL-test-00',grid=grid,compset=compset,SL='0') # 
add_case(prefix='2025-SCIDAC-SL-test-00',grid=grid,compset=compset,SL='1') # 

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def main(opts):
   global compset, grid, num_nodes

   case_list = ['E3SM']
   for key,val in opts.items(): 
      if key in ['prefix','compset','grid']:
         case_list.append(val)
      # elif key in ['num_nodes']:
      #    continue
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
   # exit()
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
      # run_cmd('./xmlchange --id CAM_CONFIG_OPTS --append --val=\'-cosp\' ')
      #-------------------------------------------------------------------------
      run_cmd('./xmlchange PIO_NETCDF_FORMAT=\"64bit_data\" ')
      run_cmd('./case.setup --reset')
   #------------------------------------------------------------------------------------------------
   if build : 
      if clean : run_cmd('./case.build --clean')
      run_cmd('./case.build')
   #------------------------------------------------------------------------------------------------
   if submit :
      #----------------------------------------------------------------------------
      # Namelist options
      nfile = 'user_nl_eam'
      file = open(nfile,'w') 
      file.write(' nhtfrq    = 0,-3,-3 \n')
      file.write(' mfilt     = 1,8,8 \n')
      file.write(" avgflag_pertape = 'A','A','I' \n")
      file.write(" fincl1 = 'Z3','CLDLIQ','CLDICE'")
      file.write(         ",'UTGWSPEC','BUTGWSPEC'")
      file.write(         ",'Uzm','Vzm','Wzm','THzm','VTHzm','WTHzm','UVzm','UWzm','THphys','PSzm'")
      file.write("\n")
      file.write(f' phys_grid_ctem_zm_nbas = 120 \n') # Number of basis functions used for TEM
      file.write(f' phys_grid_ctem_za_nlat = 90 \n') # Number of latitude points for TEM
      file.write(f' phys_grid_ctem_nfreq = -1 \n') # Frequency of TEM diagnostic calculations (neg => hours)
      if 'SL' in opts.keys():
         if opts['SL']=='0': file.write(f' semi_lagrange_trajectory_nsubstep = 0 \n')
         if opts['SL']=='1': file.write(f' semi_lagrange_trajectory_nsubstep = 1 \n')
      if 'beres' in opts.keys():
         if opts['beres']=='old':    file.write(f' use_gw_convect_old           = .true. \n')
         if opts['beres']=='new':    file.write(f' use_gw_convect_old           = .false. \n')
      if 'gweff'     in opts.keys(): file.write(f' effgw_beres                  = {opts["gweff"]} \n')
      if 'cfrac'     in opts.keys(): file.write(f' gw_convect_hcf               = {opts["cfrac"]} \n')
      if 'hdpth'     in opts.keys(): file.write(f' hdepth_scaling_factor        = {opts["hdpth"]} \n')
      # if 'hdpth_min' in opts.keys(): file.write(f' gw_convect_hdepth_min        = {opts["hdpth_min"]} \n')
      # if 'stspd_min' in opts.keys(): file.write(f' gw_convect_storm_speed_min   = {opts["stspd_min"]} \n')
      # if 'plev_srcw' in opts.keys(): file.write(f' gw_convect_plev_src_wind     = {opts["plev_srcw"]*1e2} \n')
      file.close()
      #----------------------------------------------------------------------------
      # file=open('user_nl_elm','w')
      # file.write(v3HR_lnd_opts)
      # file.close()
      #-------------------------------------------------------------------------
      run_cmd(f'./xmlchange --file env_run.xml RUN_STARTDATE=1985-01-01')
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
      #-------------------------------------------------------------------------
      # Submit the run
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
