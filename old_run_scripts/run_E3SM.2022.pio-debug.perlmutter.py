#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp, numpy as np
from shutil import copy2
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm3312'    # m3312 / m3305

top_dir  = os.getenv('HOME')+'/E3SM'
case_dir = top_dir+'/Cases/'
# src_dir  = top_dir+'/E3SM_SRC2/' # master as of Nov 7, 2022

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

debug_mode = False

# queue = 'regular'  # regular / debug 

# stop_opt,stop_n,resub,walltime = 'nsteps',10, 0,'0:05:00'
# stop_opt,stop_n,resub,walltime = 'ndays',1, 0,'0:30:00'
# stop_opt,stop_n,resub,walltime = 'ndays',5, 0,'0:30:00'
stop_opt,stop_n,resub,walltime = 'ndays',32, 0,'0:45:00'

# ne,npg = 4,2; num_nodes = 2 ; grid = f'ne{ne}pg{npg}_ne{ne}pg{npg}'

# ne,npg = 30,2; num_nodes = 16  ; grid = f'ne{ne}pg{npg}_oECv3' # match v2 PI control
ne,npg = 30,2; num_nodes = 32  ; grid = f'ne{ne}pg{npg}_oECv3' # match v2 PI control
# ne,npg = 30,2; num_nodes = 64  ; grid = f'ne{ne}pg{npg}_oECv3' # match v2 PI control
# ne,npg = 30,2; num_nodes = 128 ; grid = f'ne{ne}pg{npg}_oECv3' # match v2 PI control


compset,arch   = 'F2010-MMF1', 'GNUGPU'
# compset,arch   = 'F20TR-MMF1', 'GNUGPU'
# compset,arch   = 'F2010-MMF1', 'GNUCPU'
# compset,arch   = 'FAQP-MMF1',  'GNUGPU'
# compset,arch   = 'F2010',      'GNUCPU'
# compset,arch   = 'WCYCL1850',  'GNUCPU'


# case_list=['E3SM','PIO-DEBUG-50',arch,compset,grid,f'NN_{num_nodes}']; src_dir=top_dir+'/E3SM_SRC1' # MPICH_COLL_SYNC=MPI_Bcast
# case_list=['E3SM','PIO-DEBUG-51',arch,compset,grid,f'NN_{num_nodes}']; src_dir=top_dir+'/E3SM_SRC2' # Noel's libfabric env vars
# case_list=['E3SM','PIO-DEBUG-52',arch,compset,grid,f'NN_{num_nodes}']; src_dir=top_dir+'/E3SM_SRC0' # dqwu/simplify_PIOc_inq_type_pnetcdf 
# case_list=['E3SM','PIO-DEBUG-53',arch,compset,grid,f'NN_{num_nodes}']; src_dir=top_dir+'/E3SM_SRC0' # dqwu/simplify_PIOc_inq_type_pnetcdf + MPICH_COLL_SYNC=MPI_Bcast
case_list=['E3SM','PIO-DEBUG-54',arch,compset,grid,f'NN_{num_nodes}']; src_dir=top_dir+'/E3SM_SRC0' # dqwu/simplify_PIOc_inq_type_pnetcdf + libfabric env vars



if debug_mode: case_list.append('debug')

case='.'.join(case_list)

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

if 'CPU' in arch : max_mpi_per_node,atm_nthrds  = 64,1 ; max_task_per_node = 64
if 'GPU' in arch : max_mpi_per_node,atm_nthrds  =  4,8 ; max_task_per_node = 32
# if 'GPU' in arch : max_mpi_per_node,atm_nthrds  =  4,1 ; max_task_per_node = 4
atm_ntasks = max_mpi_per_node*num_nodes

#---------------------------------------------------------------------------------------------------
if newcase :
   if os.path.isdir(f'{case_dir}/{case}'): exit('\n'+clr.RED+'This case already exists!'+clr.END+'\n')
   cmd = f'{src_dir}/cime/scripts/create_newcase -case {case_dir}/{case} -compset {compset} -res {grid}  '
   if arch=='GNUCPU' : cmd += f' -mach pm-cpu -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='GNUGPU' : cmd += f' -mach pm-gpu -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
   run_cmd(cmd)
os.chdir(f'{case_dir}/{case}/')
if newcase :
   if 'max_mpi_per_node'  in locals(): run_cmd(f'./xmlchange MAX_MPITASKS_PER_NODE={max_mpi_per_node} ')
   if 'max_task_per_node' in locals(): run_cmd(f'./xmlchange MAX_TASKS_PER_NODE={max_task_per_node} ')
#---------------------------------------------------------------------------------------------------
if config : 
   if debug_mode: 
      run_cmd('./xmlchange --append --id CAM_CONFIG_OPTS --val \" -cppdefs \' -DPIO_ENABLE_LOGGING=OFF \'  \"')
   if clean : run_cmd('./case.setup --clean')
   run_cmd('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
if build : 
   
   if 'PIO-DEBUG-24' in case: run_cmd('./xmlchange PIO_VERSION=1 ')

   # run_cmd('./xmlchange PIO_TYPENAME=pnetcdf ')

   if 'PIO-DEBUG-11' in case: 
      run_cmd('./xmlchange PIO_NUMTASKS=1 ')
      run_cmd('./xmlchange PIO_STRIDE=-99 ')
   if 'PIO-DEBUG-12' in case: 
      run_cmd('./xmlchange PIO_TYPENAME=netcdf ')
   

   if debug_mode: run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
if submit : 
   if 'queue' in locals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
   run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
   if 'GPU' in arch: run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct}_g,PROJECT={acct}_g')
   if 'CPU' in arch: run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')
   continue_flag = 'TRUE' if continue_run else 'False'
   run_cmd(f'./xmlchange --file env_run.xml CONTINUE_RUN={continue_flag} ')   
   #-------------------------------------------------------
   run_cmd('./case.submit')
#---------------------------------------------------------------------------------------------------
# Print the case name again
print(f'\n  case : {case}\n') 
#---------------------------------------------------------------------------------------------------

# case_list = ['E3SM','PIO-DEBUG-00',arch,compset,grid,f'NN_{num_nodes}'] # initial version to reproduce error
# case_list = ['E3SM','PIO-DEBUG-01',arch,compset,grid,f'NN_{num_nodes}'] # add setting for MAX_TASKS_PER_NODE
# case_list = ['E3SM','PIO-DEBUG-02',arch,compset,grid,f'NN_{num_nodes}'] # try single thread
# case_list = ['E3SM','PIO-DEBUG-10',arch,compset,grid,f'NN_{num_nodes}'] # still single thread, after updating scorpio to latest master
# case_list = ['E3SM','PIO-DEBUG-11',arch,compset,grid,f'NN_{num_nodes}'] # Try setting PIO_NUMTASKS=1 and PIO_STRIDE=-99
# case_list = ['E3SM','PIO-DEBUG-12',arch,compset,grid,f'NN_{num_nodes}'] # Try setting PIO_TYPENAME=netcdf
# case_list = ['E3SM','PIO-DEBUG-13',arch,compset,grid,f'NN_{num_nodes}'] # add mpi_barrier to ???
# case_list = ['E3SM','PIO-DEBUG-20',arch,compset,grid,f'NN_{num_nodes}'] # fresh master branch with mpi_barrier fix in surfalb_vars%restart
# case_list = ['E3SM','PIO-DEBUG-21',arch,compset,grid,f'NN_{num_nodes}'] # switch to cray-mpich/8.1.17
# case_list = ['E3SM','PIO-DEBUG-22',arch,compset,grid,f'NN_{num_nodes}'] # add MPICH_COLL_SYNC=1
# case_list = ['E3SM','PIO-DEBUG-23',arch,compset,grid,f'NN_{num_nodes}'] # add MPICH_COLL_OPT_OFF=1 & MPICH_SHARED_MEM_COLL_OPT=0
# case_list = ['E3SM','PIO-DEBUG-24',arch,compset,grid,f'NN_{num_nodes}'] # redo "old" fix with scorpio classic to compare throughput
# case_list = ['E3SM','PIO-DEBUG-25',arch,compset,grid,f'NN_{num_nodes}'] # Noel's suggested fix
# case_list = ['E3SM','PIO-DEBUG-26',arch,compset,grid,f'NN_{num_nodes}'] # update scorpio branch => dqwu/barrier_inq_dim
# case_list = ['E3SM','PIO-DEBUG-27',arch,compset,grid,f'NN_{num_nodes}'] # MPICH_COLL_SYNC=MPI_Bcast
# case_list = ['E3SM','PIO-DEBUG-28',arch,compset,grid,f'NN_{num_nodes}'] # MPICH_COLL_SYNC=MPI_Reduce
# case_list = ['E3SM','PIO-DEBUG-29',arch,compset,grid,f'NN_{num_nodes}'] # retry MPICH_COLL_SYNC=MPI_Bcast
# case_list = ['E3SM','PIO-DEBUG-30',arch,compset,grid,f'NN_{num_nodes}'] # add MPICH_COLL_SYNC=MPI_Bcast to updated master (Nov 7)

# case_list = ['E3SM','PIO-DEBUG-40',arch,compset,grid,f'NN_{num_nodes}'] # bisection - c1465081f0c4222d3f176ff9e8b51dbb5c937e60
# case_list = ['E3SM','PIO-DEBUG-41',arch,compset,grid,f'NN_{num_nodes}'] # bisection - fa5cfdb8a6d3c94da7d0d6071f618b3b138c8b72 
# case_list = ['E3SM','PIO-DEBUG-42',arch,compset,grid,f'NN_{num_nodes}'] # 41 + MPICH_COLL_SYNC=MPI_Bcast
# case_list = ['E3SM','PIO-DEBUG-43',arch,compset,grid,f'NN_{num_nodes}'] # back to current master (Nov 7) no change to env vars
# case_list = ['E3SM','PIO-DEBUG-44',arch,compset,grid,f'NN_{num_nodes}'] # master + dqwu/simplify_PIOc_inq_type_pnetcdf 
# case_list = ['E3SM','PIO-DEBUG-45',arch,compset,grid,f'NN_{num_nodes}'] # Noel's libfabric env vars
