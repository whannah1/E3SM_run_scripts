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
# newcase      = True
# config       = True
# build        = True
submit       = True
# continue_run = True

debug_mode = False

### run duration
# queue,stop_opt,stop_n,resub,walltime = 'debug','ndays',1,0,'2:00'
queue,stop_opt,stop_n,resub,walltime = 'batch','nsteps',4,0,'0:30'

compset        = 'F2010-MMF1'
arch           = 'CRAYGPU' # CRAYGPU / CRAYCPU / FGNUCPU / FGNUGPU / SGNUCPU / SGNUGPU

# if arch=='SGNUGPU':num_nodes = 64
# if arch in ['CRAYCPU','FGNUCPU']:num_nodes = 1#6
if arch in ['CRAYGPU','FGNUGPU']:num_nodes = 48 # 48 / 24 / 12 / 6
# if arch in ['CRAYGPU','FGNUGPU']: num_tasks,num_thrds = 8*1,7

ne,npg         = 4,2 # 30,2
grid           = f'ne{ne}pg{npg}_ne{ne}pg{npg}'
rad_nx         = 4
crm_dx,crm_dt  = 50,0.5   # 2000,10 / 200,2 / 
dtime_min      = 5
gcm_nz,crm_nz  = 276,256 # 60,50 / 276,256
crm_nx,crm_ny  = 128,128 # 128,128 / 256,256 / 512,512
use_vt,use_mf  = True,True # CRM variance transport and momentum feedback
# crm_hv,crm_sed = True,True 



# # use defaults as baseline
# compset        = 'F2010-MMF1'
# arch           = 'CRAYGPU' # CRAYGPU / SGNUGPU
# # num_nodes      = 2 # 1 / 2 / 4
# ne,npg         = 4,2 # 30,2
# grid           = f'ne{ne}pg{npg}_ne{ne}pg{npg}'
# rad_nx         = 4
# crm_dx,crm_dt  = 2000,10
# dtime_min      = 20
# gcm_nz,crm_nz  = 60,50 # 60,50 / 276,256
# crm_nx,crm_ny  = 64,1
# use_vt,use_mf  = True,True
# # crm_hv,crm_sed = False,False 



# case_list = ['E3SM','GB2022-TEST',f'ne{ne}pg{npg}',compset] # initial test 2022
# case_list = ['E3SM','GB2023-TEST-00',f'ne{ne}pg{npg}',compset] # retest after update (jan 2023)
# case_list = ['E3SM','GB2023-TEST-01',arch,f'ne{ne}pg{npg}',compset] # update branch and test Frontier (jan 2023)
# case_list = ['E3SM','GB2023-TEST-01a',arch,f'ne{ne}pg{npg}',compset] # special group to test specific task/thread combinations
# case_list = ['E3SM','GB2023-TEST-02',arch,f'ne{ne}pg{npg}',compset] # new group to test workload sensitivity
# case_list = ['E3SM','GB2023-TEST-03',arch,f'ne{ne}pg{npg}',compset] # n
# case_list = ['E3SM','GB2023-TEST-04',arch,f'ne{ne}pg{npg}',compset] # repeat 03 w/ NTHRDS=6
case_list = ['E3SM','GB2023-TEST-05',arch,f'ne{ne}pg{npg}',compset] # switch to crusher


# num_tasks,num_thrds = 8*1,7
# num_tasks,num_thrds = 12,7
# num_tasks,num_thrds = 16,7
# num_tasks,num_thrds = 16,6
# num_tasks,num_thrds = 16,4
# num_tasks,num_thrds = 16,2
# num_tasks,num_thrds = 16,1

if 'num_nodes' in locals(): case_list.append(f'NN_{num_nodes}')
if 'num_tasks' in locals(): case_list.append(f'NTASK_{num_tasks}')
if 'num_thrds' in locals(): case_list.append(f'NTHRD_{num_thrds}')
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
print('\n  case : '+case+'\n')

dtime = dtime_min*60   # GCM physics time step
# dtime = 5*60   # GCM physics time step

num_dyn = ne*ne*6

# fix walltime for Slurm on Frontier
if 'FGNU' in arch or 'CRAY' in arch: walltime += ':00'

if arch=='SGNUCPU': max_task_per_node,max_mpi_per_node,atm_nthrds  = 42,42,1
if arch=='SGNUGPU': max_task_per_node,max_mpi_per_node,atm_nthrds  = 42,6,7
if arch=='FGNUCPU': max_task_per_node,max_mpi_per_node,atm_nthrds  = 56,56,1 
if arch=='FGNUGPU': max_task_per_node,max_mpi_per_node,atm_nthrds  = 56,8,7 
if arch=='CRAYCPU': max_task_per_node,max_mpi_per_node,atm_nthrds  = 56,56,1
if arch=='CRAYGPU': max_task_per_node,max_mpi_per_node,atm_nthrds  = 56,8,6#7
task_per_node = max_mpi_per_node
if 'num_nodes' in locals():
   atm_ntasks = task_per_node*num_nodes

if 'num_tasks' in locals() and 'num_thrds' in locals():
   atm_ntasks = num_tasks
   atm_nthrds = num_thrds
#---------------------------------------------------------------------------------------------------
if newcase :
   # Check if directory already exists
   if os.path.isdir(f'{case_dir}/{case}'): exit('\n'+clr.RED+'This case already exists!'+clr.END+'\n')
   cmd = f'{src_dir}/cime/scripts/create_newcase -case {case_dir}/{case}'
   cmd = cmd + f' -compset {compset} -res {grid}'
   if arch=='SGNUCPU' : cmd += f' -mach summit   -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='SGNUGPU' : cmd += f' -mach summit   -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='FGNUCPU' : cmd += f' -mach frontier -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='FGNUGPU' : cmd += f' -mach frontier -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
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
   # Change inputdata from default due to permissions issue
   # init_scratch = '/gpfs/alpine/cli115/scratch/hannah6/inputdata'
   init_scratch = '/gpfs/alpine/cli115/world-shared/e3sm/inputdata'
   run_cmd(f'./xmlchange DIN_LOC_ROOT={init_scratch} ')
   #-------------------------------------------------------
   # First query some stuff about the case
   #-------------------------------------------------------
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
   #-------------------------------------------------------
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   #------------------------------
   file.write(' nhtfrq    = 0,-1 \n') 
   file.write(' mfilt     = 1,24 \n') # 1-day files
   file.write(" fincl1    = 'Z3'") # this is for easier use of height axis on profile plots   
   file.write(            ",'CLOUD','CLDLIQ','CLDICE'")
   file.write(            ",'PTTEND','PTEQ'")             # 3D physics tendencies
   file.write(            ",'PTECLDLIQ','PTECLDICE'")     # 3D physics tendencies
   file.write('\n')
   file.write(" fincl2    = 'PS','PSL','TS'")                      # sfc pressure and temperature
   file.write(             ",'PRECT','TMQ'")                       # precip and total column water
   file.write(             ",'LHFLX','SHFLX'")                     # surface fluxes
   file.write(             ",'FSNT','FLNT'")                       # Net TOM heating rates
   file.write(             ",'FLNS','FSNS'")                       # Surface rad for total column heating
   file.write(             ",'FSNTC','FLNTC'")                     # clear sky heating rates for CRE
   file.write(             ",'FLUT','FSNTOA'")                     # more rad fields
   file.write(             ",'LWCF','SWCF'")                       # cloud radiative foricng
   file.write(             ",'TGCLDLWP','TGCLDIWP'")               # liq/ice water path
   file.write(             ",'CLDTOT','CLDLOW','CLDMED','CLDHGH'") # cloud fraction
   file.write(             ",'QREFHT','TREFHT'")                   # reference temperature and humidity
   file.write(             ",'TUQ','TVQ'")                         # vapor transport
   file.write(             ",'TBOT:I','QBOT:I','UBOT:I','VBOT:I'") # lowest model leve
   file.write(             ",'T900:I','Q900:I','U900:I','V900:I'") # 900mb data
   file.write(             ",'T850:I','Q850:I','U850:I','V850:I'") # 850mb data
   file.write(             ",'Z300:I','Z500:I'")                   # height surfaces
   file.write(             ",'OMEGA850:I','OMEGA500:I'")           # omega
   file.write(             ",'U200:I','V200:I'")                   # 200mb winds
   file.write('\n')
   # file.write(" fincl3    = 'PS'")
   # file.write(             ",'T','Q','Z3'")                # 3D thermodynamic budget components
   # file.write(             ",'U','V','OMEGA'")             # 3D velocity components
   # file.write(             ",'CLOUD','CLDLIQ','CLDICE'")   # 3D cloud fields
   # file.write(             ",'QRL','QRS'")                 # 3D radiative heating 
   # file.write(             ",'QRLC','QRSC'")               # 3D clearsky radiative heating 
   # file.write(             ",'PTTEND','PTEQ'")             # 3D physics tendencies
   # file.write(             ",'PTECLDLIQ','PTECLDICE'")     # 3D physics tendencies
   # file.write('\n')
   #------------------------------
   if 'init_file_atm' in locals(): file.write(f' ncdata = \'{init_file_atm}\'\n')
   # file.write(f' crm_accel_factor = 3 \n')         # CRM acceleration factor (default is 2)
   if  crm_ny==1 and use_mf: file.write(' use_mmf_esmt = .true. \n')
   if  crm_ny>1  and use_mf: file.write(' use_mmf_esmt = .false. \n')

   # if num_dyn<ntasks_atm: file.write(' dyn_npes = '+str(num_dyn)+' \n')   # limit dynamics tasks
   if ne==4: file.write(f' dyn_npes = {max_mpi_per_node} \n')
   # if ne==4: file.write(f' dyn_npes = 96 \n')

   file.write(f'se_tstep            = {dtime/4} \n')
   file.write(f'dt_remap_factor     = 1 \n')
   file.write(f'hypervis_subcycle   = 1 \n')
   file.write(f'dt_tracer_factor    = 4 \n')
   file.write(f'hypervis_subcycle_q = 4 \n')

   # file.write(f'disable_diagnostics = .true. \n')

   file.close()
   #-------------------------------------------------------
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
#---------------------------------------------------------------------------------------------------
print(f'\n  case : {case}\n')
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
