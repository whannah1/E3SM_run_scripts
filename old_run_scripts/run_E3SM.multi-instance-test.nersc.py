#!/usr/bin/env python3
# salloc -N 1 -C knl -q interactive -t 02:00:00 --account=m3312
#===============================================================================
import os, optparse, time, subprocess as sp
from multiprocessing import Process
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False
#-------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd,log=None): 
   if log is None:
      print(f'\n{clr.GREEN}{cmd}{clr.END}')
      os.system(cmd)
   else:
      with open(log,'a') as f: print(f'\n{clr.GREEN}{cmd}{clr.END}', file=f)
      os.system(f'{cmd} > {log}')
   return
def chk_cmd(cmd,log=None): 
   print(f'\n{clr.CYAN}{cmd}{clr.END}')
   return sp.run(cmd,shell=True,universal_newlines=True,capture_output=True)
#-------------------------------------------------------------------------------
# Parse the command line options
parser = optparse.OptionParser()
# parser.add_option('--hgrid',    dest='horz_grid',default=None,help='Sets the output horizontal grid')
# parser.add_option('--vgrid',    dest='vert_grid',default=None,help='Sets the output vertical grid')
# parser.add_option('--init_date',dest='init_date',default=None,help='Sets the initialization date')
(opts, args) = parser.parse_args()
#---------------------------------------------------------------------------------------------------

acct = 'm3312'    # m3312 / m3305
case_dir = os.getenv('HOME')+'/E3SM/Cases'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC1' # branch => whannah/mmf/reduced-rad-sensitivity

# clean        = True
# newcase      = True
# config       = True
# build        = True
# submit       = True
# continue_run = True

compset,grid,num_nodes,arch = 'F2010-MMF1','ne4pg2_ne4pg2',1,'CORI'

stop_opt,stop_n = 'nsteps',5

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
bld_log_list = []
run_log_list = []
case_name_list = []
def launch_job(compset,grid,num_nodes,arch,stop_opt,stop_n,rootpe):
   # global bld_log_list, run_log_list, case_name_list
   case = '.'.join(['E3SM',f'MI-TEST-00',arch,grid,compset,f'RPE_{rootpe:02d}'])
   # bld_log = None
   bld_log = os.getenv('HOME')+f'/E3SM/MI-logs/bld_log.{case}'
   run_log = f'{case_dir}/{case}/tmp_run_log.{case}'
   case_name_list.append(case)
   bld_log_list.append(bld_log)
   run_log_list.append(run_log)

   return 

   #------------------------------------------------------------------------------------------------
   # print(f'\n  case : {case}\n')
   if arch=='CORI'  : max_mpi_per_node,atm_nthrds  = 64,1
   if 'CPU' in arch : max_mpi_per_node,atm_nthrds  = 64,1
   if 'GPU' in arch : max_mpi_per_node,atm_nthrds  =  4,8
   atm_ntasks = max_mpi_per_node*num_nodes
   #------------------------------------------------------------------------------------------------
   if newcase :
      if os.path.isdir(f'{case_dir}/{case}'): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
      cmd = f'{src_dir}/cime/scripts/create_newcase -case {case_dir}/{case} -compset {compset} -res {grid}  '
      if arch=='GNUCPU' : cmd += f' -mach pm-cpu -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
      if arch=='GNUGPU' : cmd += f' -mach pm-gpu -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
      if arch=='CORI'   : cmd += f' -mach cori-knl -pecount {atm_ntasks}x{atm_nthrds} '
      run_cmd(cmd,log=bld_log)
   os.chdir(f'{case_dir}/{case}/')
   if newcase :run_cmd(f'./xmlchange -file env_mach_pes.xml -id MAX_MPITASKS_PER_NODE -val {max_mpi_per_node} ',log=bld_log)
   #------------------------------------------------------------------------------------------------
   if config:
      run_cmd(f'./xmlchange TOTALPES={atm_ntasks}',log=bld_log)
      run_cmd(f'./xmlchange COST_PES={atm_ntasks}',log=bld_log)
      run_cmd(f'./xmlchange ATM_ROOTPE={rootpe}',log=bld_log)
      run_cmd(f'./xmlchange CPL_ROOTPE={rootpe}',log=bld_log)
      run_cmd(f'./xmlchange OCN_ROOTPE={rootpe}',log=bld_log)
      run_cmd(f'./xmlchange WAV_ROOTPE={rootpe}',log=bld_log)
      run_cmd(f'./xmlchange GLC_ROOTPE={rootpe}',log=bld_log)
      run_cmd(f'./xmlchange ICE_ROOTPE={rootpe}',log=bld_log)
      run_cmd(f'./xmlchange ROF_ROOTPE={rootpe}',log=bld_log)
      run_cmd(f'./xmlchange LND_ROOTPE={rootpe}',log=bld_log)
      run_cmd(f'./xmlchange ESP_ROOTPE={rootpe}',log=bld_log)
      run_cmd(f'./xmlchange IAC_ROOTPE={rootpe}',log=bld_log)
      run_cmd('./case.setup --reset',log=bld_log)
   #------------------------------------------------------------------------------------------------
   if build: 
      run_cmd('./case.build',log=bld_log)
   #------------------------------------------------------------------------------------------------
   if submit: 
      #-------------------------------------------------------
      nfile = 'user_nl_eam'
      file = open(nfile,'w') 
      file.write(' nhtfrq = 0,-1 \n')
      file.write(' mfilt  = 1,24 \n')
      file.write(" fincl2 = 'PS','TS','PRECT','TMQ'")
      file.write(          ",'FSNT','FLNT','FLNS','FSNS'")
      file.write(          ",'TGCLDLWP','TGCLDIWP'")
      file.write('\n')
      file.close()
      #-------------------------------------------------------
      init_scratch = '/global/cfs/cdirs/e3sm/inputdata'
      run_cmd(f'./xmlchange DIN_LOC_ROOT={init_scratch}',log=bld_log)
      run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n}',log=bld_log)
      alt_run_script = f'.run.{case}'
      run_cmd(f'cp .case.run {alt_run_script}',log=bld_log)
      run_cmd(f'nohup ./{alt_run_script} > {run_log} & ',log=bld_log)
   #------------------------------------------------------------------------------------------------
   print(f'\n  case : {case}\n')

#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':

   print('-'*80)

   #-------------------------------------------------------
   # Launch a group of jobs

   proc_list = []
   proc_list.append( Process(target=launch_job,args=(compset,grid,num_nodes,arch,stop_opt,stop_n, 0)) )
   proc_list.append( Process(target=launch_job,args=(compset,grid,num_nodes,arch,stop_opt,stop_n,64)) )
   
   for proc in proc_list: proc.start()
   for proc in proc_list: proc.join(timeout=0)

   time.sleep(5)

   # need a different way of building case_name_list, 
   # probably needs to happen before calling 'launch_job'

   print(case_name_list)
   exit()

   # for t in range(4):
   any_still_alive = True
   cnt = 0
   while any_still_alive:
      print()
      if cnt>0: print(f'cnt: {cnt}')
      cnt += 1
      time.sleep(5)
      any_still_alive = False
      for p,proc in enumerate(proc_list):
         proc.join(timeout=0)
         if proc.is_alive():
            any_still_alive = True
            tcase = case_name_list[p]
            print(f'  Job #{p} is not finished! ({tcase})')

   # exit()

   #-------------------------------------------------------
   # print case names and associated log file paths
   print(); print('run_log_list:')
   for c in range(len(case_name_list)): 
      print(f'  {clr.MAGENTA}{case_name_list[c]}{clr.END}  {run_log_list[c]}')
   print()

   #-------------------------------------------------------
   # Monitor the job status
   for t in range(4):

      if t>0: time.sleep(10)

      print('-'*80)

      # check current srun processes
      try:
         msg = chk_cmd('ps -fC srun')
         for line in msg.split('\n'): print(f'    {line}')
      except sp.CalledProcessError:
         print('No srun processes running')

      # check current python3 processes
      try:
         msg = chk_cmd('ps -fC python3')
         for line in msg.split('\n'): print(f'    {line}')
      except sp.CalledProcessError:
         print('No python3 processes running')

      # read tail of log files
      for l in run_log_list:
         msg = chk_cmd(f'tail {l} -n 4')
         for line in msg.split('\n'): print(f'    {line}')


#---------------------------------------------------------------------------------------------------
