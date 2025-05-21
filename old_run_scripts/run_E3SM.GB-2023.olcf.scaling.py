#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
import os, numpy as np, subprocess as sp, datetime
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

# cd /gpfs/alpine/cli133/proj-shared/hannah6/e3sm_scratch/frontier/E3SM_SRC
# COMPILER_OPT=crayclanggpu; cime/scripts/create_newcase --machine frontier --compiler ${COMPILER_OPT} --compset F2010-MMF1 --res ne4pg2_ne4pg2 --case test_${COMPILER_OPT}; cd test_${COMPILER_OPT} ; ./case.setup ; ./case.build

scratch_frontier = '/gpfs/alpine/cli133/proj-shared/hannah6/e3sm_scratch/frontier' 

acct = 'cli133_crusher'
case_dir = os.getenv('HOME')+'/E3SM/Cases'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC5' # branch => master + sarats/machines/frontier

# case_dir = scratch_frontier
# src_dir  = f'{scratch_frontier}/E3SM_SRC' # whannah/Gordon-Bell-2023 = master + sarats/machines/frontier
# case_dir = src_dir

### flags to control config/build/submit sections
# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

debug_mode = True

### run duration
# queue,stop_opt,stop_n,resub,walltime = 'regular','ndays',1,0,'1:00:00'
queue,stop_opt,stop_n,resub,walltime = 'regular','steps',5,0,'1:00:00'

compset        = 'F2010-MMF1'
arch           = 'CRAYCPU'
ne,npg         = 4,2 # 30,2
grid           = f'ne{ne}pg{npg}_ne{ne}pg{npg}'

rad_nx         = 4
crm_dx,crm_dt  = 50,0.5   # 2000,10 / 200,2 / 
dtime_min      = 5
gcm_nz,crm_nz  = 276,256 # 60,50 / 276,256
crm_nx,crm_ny  = 256,256 # 128,128 / 256,256 / 512,512
use_vt,use_mf  = True,True # CRM variance transport and momentum feedback
# crm_hv,crm_sed = True,True 

# use defaults as baseline
# rad_nx         = 4
# crm_dx,crm_dt  = 2000,10
# dtime_min      = 20
# gcm_nz,crm_nz  = 60,50 # 60,50 / 276,256
# crm_nx,crm_ny  = 16,16
# use_vt,use_mf  = True,True


num_nodes = 24 # 48 / 24 / 12 / 8 / 6 / 4 / 3 / 2 / 1

case_list = ['E3SM','GB2023-TIMING-00',arch,f'ne{ne}pg{npg}',compset] # don't set dyn_npes - use 6 threads


if 'num_nodes' in locals(): case_list.append(f'NN_{num_nodes}')
case_list.append(f'L{gcm_nz}_{crm_nz}')
case_list.append(f'NXY_{crm_nx}x{crm_ny}')
case_list.append(f'DXT_{crm_dx}x{crm_dt}')
case_list.append(f'DTM_{dtime_min}')

if debug_mode: case_list.append('debug')

case='.'.join(case_list)

# exit(case)

hiccup_scratch = '/gpfs/alpine/scratch/hannah6/cli115/HICCUP/data'
if gcm_nz==276: 
   if ne==4: init_file_atm = f'{hiccup_scratch}/HICCUP.atm_era5.2008-10-01.ne4np4.L276.nc'

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print(f'\n  case : {case}\n')

dtime = dtime_min*60   # GCM physics time step
# dtime = 5*60   # GCM physics time step

num_dyn = ne*ne*6

if arch=='CRAYCPU': max_task_per_node,max_mpi_per_node,atm_nthrds  = 56,56,1
if arch=='CRAYGPU': max_task_per_node,max_mpi_per_node,atm_nthrds  = 56,8,6#7
task_per_node = max_mpi_per_node
if 'num_nodes' in locals():atm_ntasks = task_per_node*num_nodes

#---------------------------------------------------------------------------------------------------
if newcase :
   # Check if directory already exists
   if os.path.isdir(f'{case_dir}/{case}'): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
   cmd = f'{src_dir}/cime/scripts/create_newcase -case {case_dir}/{case}'
   cmd = cmd + f' -compset {compset} -res {grid}'
   # if arch=='CRAYCPU' : cmd += f' -mach frontier -compiler crayclang -pecount {atm_ntasks}x{atm_nthrds} '
   # if arch=='CRAYGPU' : cmd += f' -mach frontier -compiler crayclanggpu -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='CRAYCPU' : cmd += f' -mach crusher -compiler crayclang -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='CRAYGPU' : cmd += f' -mach crusher -compiler crayclanggpu -pecount {atm_ntasks}x{atm_nthrds} '
   run_cmd(cmd)
   #-------------------------------------------------------
   os.chdir(f'{case_dir}/{case}/')
   run_cmd(f'./xmlchange --file env_mach_pes.xml --id MAX_TASKS_PER_NODE    --val {max_task_per_node} ')
   run_cmd(f'./xmlchange --file env_mach_pes.xml --id MAX_MPITASKS_PER_NODE --val {max_mpi_per_node} ')
else:
   os.chdir(f'{case_dir}/{case}/')
#---------------------------------------------------------------------------------------------------
if config : 
   #-------------------------------------------------------
   if 'init_file_atm' in locals():
      file = open('user_nl_eam','w')
      file.write(f' ncdata = \'{init_file_atm}\'\n')
      file.close()
   #-------------------------------------------------------
   run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -nlev {gcm_nz} \" ')
   run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_nz {crm_nz} \" ')
   run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_dt {crm_dt} \" ')
   run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_dx {crm_dx}  \" ')
   run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_nx {crm_nx} -crm_ny {crm_ny} \" ')
   rad_ny = rad_nx if crm_ny>1 else 1
   run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_nx_rad {rad_nx} -crm_ny_rad {rad_ny} \" ')
   #-------------------------------------------------------
   cpp_opt = ''
   if debug_mode: cpp_opt += ' -DYAKL_DEBUG'
   if crm_ny>1  and use_mf: cpp_opt += ' -DMMF_MOMENTUM_FEEDBACK'
   # if crm_hv : cpp_opt += ' -DMMF_HYPERVISCOSITY'
   # if crm_sed: cpp_opt += ' -DMMF_SEDIMENTATION'
   if cpp_opt != '' :
      cmd  = f'./xmlchange --append --file env_build.xml --id CAM_CONFIG_OPTS'
      cmd += f' --val \" -cppdefs \' {cpp_opt} \'  \" '
      run_cmd(cmd)
   #-------------------------------------------------------
   # 64_data format is needed for large output (i.e. high-res grids or CRM data)
   run_cmd('./xmlchange PIO_NETCDF_FORMAT=\"64bit_data\" ')
   #-------------------------------------------------------
   # Set tasks for all components
   if ne==4:
      cmd = './xmlchange --file env_mach_pes.xml '
      alt_ntask = max_mpi_per_node
      cmd += f'NTASKS_OCN={alt_ntask},NTASKS_ICE={alt_ntask}'
      cmd += f',NTASKS_LND={alt_ntask},NTASKS_CPL={alt_ntask}'
      cmd += f',NTASKS_ROF={alt_ntask},NTASKS_WAV={alt_ntask},NTASKS_GLC={alt_ntask}'
      cmd += f',NTASKS_ESP=1,NTASKS_IAC=1'
      run_cmd(cmd)
   #-------------------------------------------------------
   # Run case setup
   if clean : run_cmd('./case.setup --clean')
   run_cmd('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
if build : 
   if debug_mode: run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
if submit : 
   init_scratch = '/gpfs/alpine/cli115/world-shared/e3sm/inputdata'
   run_cmd(f'./xmlchange DIN_LOC_ROOT={init_scratch} ')
   #-------------------------------------------------------
   # Query some stuff about the case
   (din_loc_root, err) = sp.Popen('./xmlquery DIN_LOC_ROOT    --value', \
                                     stdout=sp.PIPE, shell=True, universal_newlines=True).communicate()
   (config_opts, err) = sp.Popen('./xmlquery CAM_CONFIG_OPTS --value', \
                                     stdout=sp.PIPE, shell=True, universal_newlines=True).communicate()
   config_opts = ' '.join(config_opts.split())   # remove extra spaces to simplify string query
   ntasks_atm = None
   (ntasks_atm     , err) = sp.Popen('./xmlquery NTASKS_ATM    --value', \
                                     stdout=sp.PIPE, shell=True, universal_newlines=True).communicate()
   ntasks_atm = float(ntasks_atm)
   #-------------------------------------------------------
   # Namelist options
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   if 'init_file_atm' in locals(): file.write(f' ncdata = \'{init_file_atm}\'\n')
   # file.write(f' crm_accel_factor = 3 \n')         # CRM acceleration factor (default is 2)
   if  crm_ny==1 and use_mf: file.write(' use_mmf_esmt = .true. \n')
   if  crm_ny>1  and use_mf: file.write(' use_mmf_esmt = .false. \n')
   # if num_dyn<ntasks_atm: file.write(' dyn_npes = '+str(num_dyn)+' \n')   # limit dynamics tasks
   if 'GB2023-TIMING-01' in case:
      if ne==4: file.write(f' dyn_npes = {max_mpi_per_node} \n')
   file.write(f'se_tstep            = {dtime/4} \n')
   file.write(f'dt_remap_factor     = 1 \n')
   file.write(f'hypervis_subcycle   = 1 \n')
   file.write(f'dt_tracer_factor    = 4 \n')
   file.write(f'hypervis_subcycle_q = 4 \n')
   # file.write(f'disable_diagnostics = .true. \n')
   file.close()
   #-------------------------------------------------------
   run_cmd('./xmlchange REST_OPTION=never') # Disable restart file write for timing
   if 'dtime' in locals(): ncpl=86400/dtime ; run_cmd(f'./xmlchange ATM_NCPL={str(ncpl)}')
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
   run_cmd(f'./xmlchange JOB_QUEUE={queue},JOB_WALLCLOCK_TIME={walltime}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')
   continue_flag = 'TRUE' if continue_run else 'False'
   run_cmd(f'./xmlchange --file env_run.xml CONTINUE_RUN={continue_flag} ')   
   #-------------------------------------------------------
   run_cmd('./case.submit')
#---------------------------------------------------------------------------------------------------
# Print the case name again
print(f'\n  case : {case}\n')
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
