#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp, numpy as np
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'cli115'
top_dir  = os.getenv('HOME')+'/E3SM/'
case_dir = top_dir+'Cases/'
# src_dir  = top_dir+'E3SM_SRC4/' # branch = whannah/mmf/samxx-p3-shoc-alt
# src_dir  = top_dir+'E3SM_SRC0/' # branch = master @ june 7, 2022
src_dir  = top_dir+'E3SM_SRC2/' # branch = whannah/mmf/2023-coupled-historical - just for ne30pg2 test for Liran's paper - branch doesn't matter
# clean        = True
# newcase      = True
# config       = True
build        = True
submit       = True
# continue_run = True

queue = 'batch' # batch / debug

debug_mode = False

# model configuration parameters
rad_nx = 4
crm_dx = 2000
crm_dt = 10
use_vt = True # CRM variance transport
use_mf = True # CRM momentum feedback
# ne,npg = 120,2
ne,npg = 30,2

# run length and number of resubmissions
# stop_opt,stop_n,resub,walltime = 'ndays',5,0,'2:00'
stop_opt,stop_n,resub,walltime = 'ndays',32,0,'2:00'

#-------------------------------------------------------------------------------
# MMF 1/ 1-mom
# arch,walltime,compset,crm_nx,crm_ny,num_nodes = 'GNUCPU','1:00','F2010-MMF1',32, 1, 500
# arch,walltime,compset,crm_nx,crm_ny,num_nodes = 'GNUCPU','1:00','F2010-MMF1',32, 1,1000
# arch,walltime,compset,crm_nx,crm_ny,num_nodes = 'GNUCPU','2:00','F2010-MMF1',32,32, 500
# arch,walltime,compset,crm_nx,crm_ny,num_nodes = 'GNUCPU','2:00','F2010-MMF1',32,32,1000

# arch,compset,crm_nx,crm_ny,num_nodes = 'GNUGPU','F2010-MMF1',32, 1, 250
# arch,compset,crm_nx,crm_ny,num_nodes = 'GNUGPU','F2010-MMF1',32, 1, 500
# arch,compset,crm_nx,crm_ny,num_nodes = 'GNUGPU','F2010-MMF1',32, 1,1000
# arch,compset,crm_nx,crm_ny,num_nodes = 'GNUGPU','F2010-MMF1',32, 1,2000

# arch,compset,crm_nx,crm_ny,num_nodes = 'GNUGPU','F2010-MMF1',256, 1, 250; crm_dx,crm_dt = 200,5
# arch,compset,crm_nx,crm_ny,num_nodes = 'GNUGPU','F2010-MMF1',256, 1, 500; crm_dx,crm_dt = 200,5
# arch,compset,crm_nx,crm_ny,num_nodes = 'GNUGPU','F2010-MMF1',256, 1,1000; crm_dx,crm_dt = 200,5
# arch,compset,crm_nx,crm_ny,num_nodes = 'GNUGPU','F2010-MMF1',256, 1,2000; crm_dx,crm_dt = 200,5


# arch,compset,crm_nx,crm_ny,num_nodes = 'GNUGPU','F2010-MMF1',32,32, 250
# arch,compset,crm_nx,crm_ny,num_nodes = 'GNUGPU','F2010-MMF1',32,32, 500
# arch,compset,crm_nx,crm_ny,num_nodes = 'GNUGPU','F2010-MMF1',32,32,1000
# arch,compset,crm_nx,crm_ny,num_nodes = 'GNUGPU','F2010-MMF1',32,32,2000
#-------------------------------------------------------------------------------
# MMF w/ P3
# arch,compset,crm_nx,crm_ny,num_nodes = 'GNUGPU','F2010-MMF2',32, 1, 500
# arch,compset,crm_nx,crm_ny,num_nodes = 'GNUGPU','F2010-MMF2',32, 1,1000
# arch,compset,crm_nx,crm_ny,num_nodes = 'GNUGPU','F2010-MMF2',32,32, 500
# arch,compset,crm_nx,crm_ny,num_nodes = 'GNUGPU','F2010-MMF2',32,32,1000
#-------------------------------------------------------------------------------
# non-MMF cases
# arch,compset,num_nodes = 'GNUCPU','F2010-CICE', 64
arch,compset,num_nodes = 'GNUCPU','F2010-CICE', 128
#-------------------------------------------------------------------------------

stop_opt,stop_n,resub,walltime = 'ndays',1,0,'1:00'

res = 'ne'+str(ne) if npg==0 else  'ne'+str(ne)+'pg'+str(npg)
grid = f'{res}_r05_oECv3'

# Set the case name
case_list = ['E3SM','INCITE2023-TIMING-00',arch,grid,compset,f'NODES_{num_nodes}']
if 'MMF' in compset: case_list.append(f'NXY_{crm_nx}x{crm_ny}')
if debug_mode: case_list.append('debug')
case='.'.join(case_list)


#---------------------------------------------------------------------------------------------------
# specify atmos/land initial condition file for non-standard grids
# land_init_path = '/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/init_files'
# land_data_path = '/gpfs/alpine/cli115/world-shared/e3sm/inputdata/lnd/clm2/surfdata_map'
# if ne==45: 
#    land_init_file = 'CLM_spinup.ICRUELM.ne45pg2_r05_oECv3.20-yr.2010-10-01.elm.r.2006-01-01-00000.nc'
#    land_data_file = 'surfdata_0.5x0.5_simyr2000_c200624.nc'
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

num_dyn = ne*ne*6

if ne==120: dtime = 5*60
if 'dtime' in locals(): ncpl  = 86400 / dtime

max_task_per_node = 42
if 'CPU' in arch : max_mpi_per_node,tmp_atm_nthrds  = 42,1
if 'GPU' in arch : max_mpi_per_node,tmp_atm_nthrds  = 6,7

if 'atm_nthrds' not in locals(): atm_nthrds = tmp_atm_nthrds

task_per_node = max_mpi_per_node
atm_ntasks = task_per_node*num_nodes

#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
if newcase :
   # Check if directory already exists
   if os.path.isdir(f'{case_dir}/{case}'): exit('\n'+clr.RED+'This case already exists!'+clr.END+'\n')
   cmd = src_dir+'cime/scripts/create_newcase -case '+case_dir+case
   cmd = cmd + f' -mach summit  -compset {compset} -res {grid}'
   if arch=='GNUCPU' : cmd += f' -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='GNUGPU' : cmd += f' -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
   run_cmd(cmd)
   #-------------------------------------------------------
   # Change run directory to be next to bld directory
   #-------------------------------------------------------
   os.chdir(case_dir+case+'/')
   run_cmd('./xmlchange --file env_run.xml RUNDIR=\'/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/$CASE/run\' ' )

   run_cmd(f'./xmlchange --file env_mach_pes.xml --id MAX_TASKS_PER_NODE    --val {max_task_per_node} ')
   run_cmd(f'./xmlchange --file env_mach_pes.xml --id MAX_MPITASKS_PER_NODE --val {max_mpi_per_node} ')
else:
   os.chdir(case_dir+case+'/')
#---------------------------------------------------------------------------------------------------
# Configure
#---------------------------------------------------------------------------------------------------
if config :
   #-------------------------------------------------------
   # with non-default vertical grid we need to set the 
   # initial condition file here to avoid an error
   if 'init_file_atm' in locals():
      run_cmd(f'echo \"ncdata = \'{init_file_dir}/{init_file_atm}\'\n\" > user_nl_eam')
   #-------------------------------------------------------
   # Set some non-default stuff for all MMF experiments here
   if 'MMF' in compset:
      rad_ny = rad_nx if crm_ny>1 else 1
      run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_dt {crm_dt} \" ')
      run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_dx {crm_dx} \" ')
      run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_nx {crm_nx} -crm_ny {crm_ny} \" ')
      run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_nx_rad {rad_nx} -crm_ny_rad {rad_ny} \" ')
      if use_vt: run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -use_MMF_VT \" ')
   #-------------------------------------------------------
   # Add special CPP flags for MMF options
   cpp_opt = ''
   if debug_mode: cpp_opt += ' -DYAKL_DEBUG'

   if 'MMF' in compset: 
      if  crm_ny==1 and use_mf: cpp_opt += ' -DMMF_ESMT -DMMF_USE_ESMT'
      if  crm_ny>1  and use_mf: cpp_opt += ' -DMMF_MOMENTUM_FEEDBACK'

   if cpp_opt != '' :
      cmd  = f'./xmlchange --append --file env_build.xml --id CAM_CONFIG_OPTS'
      cmd += f' --val \" -cppdefs \' {cpp_opt} \'  \" '
      run_cmd(cmd)
   #-------------------------------------------------------
   # Set tasks for all components
   if num_nodes>800:
      cmd = './xmlchange --file env_mach_pes.xml '
      alt_ntask = 600; cmd += f'NTASKS_OCN={alt_ntask},NTASKS_ICE={alt_ntask}'
      alt_ntask = 675; cmd += f',NTASKS_LND={alt_ntask},NTASKS_CPL={alt_ntask}'
      alt_ntask = max_mpi_per_node
      cmd += f',NTASKS_ROF={alt_ntask},NTASKS_WAV={alt_ntask},NTASKS_GLC={alt_ntask}'
      cmd += f',NTASKS_ESP=1,NTASKS_IAC=1'
      run_cmd(cmd)
   #-------------------------------------------------------
   # 64_data format is needed for large output (i.e. high-res grids or CRM data)
   run_cmd('./xmlchange PIO_NETCDF_FORMAT=\"64bit_data\" ')
   #-------------------------------------------------------
   # configure the case
   if clean : run_cmd('./case.setup --clean')
   run_cmd('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
# Build
#---------------------------------------------------------------------------------------------------
if build : 
   if debug_mode: run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
# Write the namelist options and submit the run
#---------------------------------------------------------------------------------------------------
if submit : 
   #-------------------------------------------------------
   # Set some run-time stuff
   #-------------------------------------------------------
   if 'ncpl' in locals(): run_cmd(f'./xmlchange ATM_NCPL={str(ncpl)}')
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
   run_cmd(f'./xmlchange JOB_QUEUE=batch,JOB_WALLCLOCK_TIME={walltime}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')
   run_cmd(f'./xmlchange JOB_QUEUE={queue}')

   if continue_run :
      run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=TRUE ')   
   else:
      run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=FALSE ')

   ### Disable restart file write for timing
   run_cmd('./xmlchange --file env_run.xml --id REST_OPTION --val never')

   #-------------------------------------------------------
   # ATM namelist
   #-------------------------------------------------------
   # Change inputdata from default due to permissions issue
   run_cmd('./xmlchange DIN_LOC_ROOT=/gpfs/alpine/cli115/world-shared/e3sm/inputdata ')
   # run_cmd('./xmlchange DIN_LOC_ROOT=/gpfs/alpine/cli115/scratch/hannah6/inputdata ')
   #-------------------------------------------------------
   # Namelist options
   #-------------------------------------------------------
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 

   if 'dtime' in locals():
      if dtime == 5*60 :
         file.write(f'dt_tracer_factor = 5 \n')
         file.write(f'dt_remap_factor = 1 \n')
         file.write(f'se_tstep = 60 \n')

   # limit dynamics tasks
   if num_dyn<atm_ntasks: file.write(f' dyn_npes = {num_dyn} \n')

   # file.write(" inithist = \'ENDOFRUN\' \n") # ENDOFRUN / NONE

   if 'init_file_atm' in locals():
      file.write(f' ncdata = \'{init_file_dir}/{init_file_atm}\'\n')

   file.close()
   #-------------------------------------------------------
   # Submit the run
   #-------------------------------------------------------
   run_cmd('./case.submit')

#---------------------------------------------------------------------------------------------------
# Print the case name again
#---------------------------------------------------------------------------------------------------
print(f'\n  case : {case}\n')
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
