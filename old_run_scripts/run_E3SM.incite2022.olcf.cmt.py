#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False
acct = 'cli115'
case_dir = os.getenv('HOME')+'/E3SM/Cases/'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC2/' # whannah/incite2021/momentum-transport-updated

# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
# continue_run = True

ne,npg = 45,2
rad_nx = 4
crm_dx = 2000
crm_nx,crm_ny = 32,32
use_vt,use_momfb = False, False

### old configs
# compset,num_nodes,arch,crm_nx,crm_ny,use_vt,use_momfb = 'F-MMFXX',   128,'GNUGPU',32, 1,True,False
# compset,num_nodes,arch,crm_nx,crm_ny,use_vt,use_momfb = 'F-MMFXX',   128,'GNUGPU',32, 1,True,True
# compset,num_nodes,arch,crm_nx,crm_ny,use_vt,use_momfb = 'F-MMFXX',  1000,'GNUGPU',32,32,True,False 
# compset,num_nodes,arch,crm_nx,crm_ny,use_vt,use_momfb = 'F-MMFXX',  1000,'GNUGPU',32,32,True,True
# compset,num_nodes,arch = 'F2010-CICE', 128,'GNUCPU'

### new sensitivity configs
# compset,num_nodes,arch,crm_nx,crm_ny,use_vt,use_momfb = 'F-MMFXX', 128,'GNUGPU', 32, 1,True,True
# compset,num_nodes,arch,crm_nx,crm_ny,use_vt,use_momfb = 'F-MMFXX', 128,'GNUGPU',128, 1,True,True
# compset,num_nodes,arch,crm_nx,crm_ny,use_vt,use_momfb = 'F-MMFXX', 512,'GNUGPU', 32,4,True,True 
compset,num_nodes,arch,crm_nx,crm_ny,use_vt,use_momfb = 'F-MMFXX',1000,'GNUGPU', 32,32,True,True


stop_opt,stop_n,resub,walltime = 'ndays',5,0,'2:00'


res = 'ne'+str(ne) if npg==0 else  'ne'+str(ne)+'pg'+str(npg)
grid = f'{res}_r05_oECv3'


case_list = ['E3SM','INCITE2022-CMT',arch,grid,compset]


if 'MMF' in compset:
   case_list.append(f'NXY_{crm_nx}x{crm_ny}')
   # if use_vt   : case_list.append('BVT')
   if use_momfb: case_list.append('MOMFB')
   # case_list.append(f'NODES_{num_nodes}')
   # case_list.append(f'DT_{crm_dt}')

### batch/version number
case_list.append('00') # initial runs with old L50 grid

case='.'.join(case_list)

# case = case+'.debug-on'

#---------------------------------------------------------------------------------------------------
# specify land initial condition file
#---------------------------------------------------------------------------------------------------
land_init_path = '/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/init_files'
land_data_path = '/gpfs/alpine/cli115/world-shared/e3sm/inputdata/lnd/clm2/surfdata_map'
if ne==45: 
   land_init_file = 'CLM_spinup.ICRUELM.ne45pg2_r05_oECv3.20-yr.2010-10-01.elm.r.2006-01-01-00000.nc'
   land_data_file = 'surfdata_0.5x0.5_simyr2000_c200624.nc'
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

num_dyn = ne*ne*6

max_task_per_node = 42
if 'CPU' in arch : max_mpi_per_node,tmp_atm_nthrds  = 42,1
if 'GPU' in arch : max_mpi_per_node,tmp_atm_nthrds  = 6,7
# if 'GPU' in arch : max_mpi_per_node,tmp_atm_nthrds  = 6,4

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
   # run_cmd('./xmlchange -file env_run.xml RUNDIR=\'$CIME_OUTPUT_ROOT/$CASE/run\' ' )
   run_cmd('./xmlchange -file env_run.xml RUNDIR=\'/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/$CASE/run\' ' )

   run_cmd(f'./xmlchange -file env_mach_pes.xml -id MAX_TASKS_PER_NODE    -val {max_task_per_node} ')
   run_cmd(f'./xmlchange -file env_mach_pes.xml -id MAX_MPITASKS_PER_NODE -val {max_mpi_per_node} ')
else:
   os.chdir(case_dir+case+'/')
#---------------------------------------------------------------------------------------------------
if config :
   #-------------------------------------------------------
   # if 'init_file_atm' in locals():
   #    file = open('user_nl_eam','w')
   #    file.write(f' ncdata = \'{init_file_dir}/{init_file_atm}\'\n')
   #    file.close()
   #-------------------------------------------------------
   # Set some non-default stuff for all MMF experiments here
   if 'MMF' in compset:
      rad_ny = rad_nx if crm_ny>1 else 1
      # run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_dt {crm_dt} -crm_dx {crm_dx}  \" ')
      run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_dx {crm_dx}  \" ')
      run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx {crm_nx} -crm_ny {crm_ny} \" ')
      run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx_rad {rad_nx} -crm_ny_rad {rad_ny} \" ')
      if use_vt: run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -use_MMF_VT \" ')
   #-------------------------------------------------------
   # Add special MMF options based on case name
   cpp_opt = ''
   if 'debug-on' in case : cpp_opt += ' -DYAKL_DEBUG'

   # if  crm_ny==1: cpp_opt += ' -DMMF_DIR_NS' # no longer needed
   if  crm_ny==1 and use_momfb: cpp_opt += ' -DMMF_ESMT -DMMF_USE_ESMT'
   if  crm_ny>1  and use_momfb: cpp_opt += ' -DMMF_MOMENTUM_FEEDBACK'

   if cpp_opt != '' :
      cmd  = f'./xmlchange --append -file env_build.xml -id CAM_CONFIG_OPTS'
      cmd += f' -val \" -cppdefs \' {cpp_opt} \'  \" '
      run_cmd(cmd)
   #-------------------------------------------------------
   # Set tasks for all components
   cmd = './xmlchange -file env_mach_pes.xml '
   alt_ntask = 600
   cmd += f'NTASKS_OCN={alt_ntask},NTASKS_ICE={alt_ntask}'
   alt_ntask = 675
   cmd += f',NTASKS_LND={alt_ntask},NTASKS_CPL={alt_ntask}'
   alt_ntask = max_mpi_per_node
   cmd += f',NTASKS_ROF={alt_ntask},NTASKS_WAV={alt_ntask},NTASKS_GLC={alt_ntask}'
   cmd += f',NTASKS_ESP=1,NTASKS_IAC=1'
   run_cmd(cmd)
   #-------------------------------------------------------
   # 64_data format is needed for large numbers of columns (GCM or CRM)
   run_cmd('./xmlchange PIO_NETCDF_FORMAT=\"64bit_data\" ')
   #-------------------------------------------------------
   # Run case setup
   if clean : run_cmd('./case.setup --clean')
   run_cmd('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
if build : 
   if 'debug-on' in case : run_cmd('./xmlchange -file env_build.xml -id DEBUG -val TRUE ')
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
if submit : 
   #-------------------------------------------------------
   # Set some run-time stuff
   #-------------------------------------------------------
   if 'ncpl' in locals(): run_cmd(f'./xmlchange ATM_NCPL={str(ncpl)}')
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
   run_cmd(f'./xmlchange JOB_QUEUE=batch,JOB_WALLCLOCK_TIME={walltime}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')
   if continue_run :
      run_cmd('./xmlchange -file env_run.xml CONTINUE_RUN=TRUE ')   
   else:
      run_cmd('./xmlchange -file env_run.xml CONTINUE_RUN=FALSE ')
   #-------------------------------------------------------
   # Change inputdata from default due to permissions issue
   #-------------------------------------------------------
   # run_cmd('./xmlchange DIN_LOC_ROOT=/gpfs/alpine/cli115/scratch/hannah6/inputdata ')
   run_cmd('./xmlchange DIN_LOC_ROOT=/gpfs/alpine/cli115/world-shared/e3sm/inputdata ')
   #-------------------------------------------------------
   # ATM namelist
   #-------------------------------------------------------
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   #------------------------------
   # Specify history output frequency and variables
   #------------------------------
   file.write(' nhtfrq = 0,-1,-1,-1 \n')
   file.write(' mfilt  = 1,24,24,24 \n')
   file.write(" fincl1 = 'Z3','CLDLIQ','CLDICE'\n")
   file.write(" fincl2 = 'PS','TS','PSL'")
   file.write(          ",'PRECT','TMQ'")
   file.write(          ",'LHFLX','SHFLX'")             # surface fluxes
   file.write(          ",'FSNT','FLNT'")               # Net TOM heating rates
   file.write(          ",'FLNS','FSNS'")               # Surface rad for total column heating
   file.write(          ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
   file.write(          ",'TGCLDLWP','TGCLDIWP'")
   file.write(          ",'TAUX','TAUY'")               # surface stress
   file.write(          ",'TUQ','TVQ'")                 # vapor transport for AR tracking 
   file.write('\n')
   file.write(" fincl3 =  'PS','PSL'")
   file.write(          ",'T','Q','Z3' ")               # 3D thermodynamic budget components
   file.write(          ",'U','V','OMEGA'")             # 3D velocity components
   file.write(          ",'CLOUD','CLDLIQ','CLDICE'")   # 3D cloud fields
   file.write(          ",'QRL','QRS'")                 # 3D radiative heating profiles
   file.write('\n')
   if 'MMF' in compset:
      file.write(    " fincl4 = 'PS','PSL'")
      file.write(              ",'CRM_T','CRM_QV','CRM_QC','CRM_QI'")
      file.write(              ",'CRM_U','CRM_V','CRM_W'")
      file.write(              ",'CRM_PREC'")
      file.write(              ",'MMF_MCUP','MMF_MCDN'")
      file.write(              ",'MMF_MCUUP','MMF_MCUDN'")
      if use_momfb: file.write(",'MMF_DU','MMF_DV'")
      file.write('\n')

   #------------------------------
   # Other ATM namelist stuff
   #------------------------------
   ### limit dynamics tasks
   ntask_dyn = int( num_dyn / atm_nthrds )
   file.write(f' dyn_npes = {ntask_dyn} \n')
   # file.write(" inithist = \'ENDOFRUN\' \n") # ENDOFRUN / NONE
   # if 'init_file_atm' in locals():file.write(f' ncdata = \'{init_file_dir}/{init_file_atm}\'\n')
   file.close()
   #-------------------------------------------------------
   # LND namelist
   #-------------------------------------------------------
   if 'land_init_file' in locals():
      nfile = 'user_nl_elm'
      file = open(nfile,'w')
      file.write(f' finidat = \'{land_init_path}/{land_init_file}\' \n')
      file.write(f' fsurdat = \'{land_data_path}/{land_data_file}\' \n')
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
