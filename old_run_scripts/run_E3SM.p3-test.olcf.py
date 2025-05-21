#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp#, numpy as np
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'cli145'

top_dir  = os.getenv('HOME')+'/E3SM'
case_dir = f'{top_dir}/Cases'
src_dir  = f'{top_dir}/E3SM_SRC4'

print_commands_only = False

# clean        = True
# newcase      = True
# config       = True
build        = True
submit       = True
# continue_run = True

compset = 'F2010-MMF1'

# compset = 'F-MMFXX-AQP1'
# compset = 'F-MMFXX-P3'
# compset = 'F-MMFXX-P3_SHOC'
# compset = 'F-MMFXX-P3-AQP1'
# compset = 'F-MMFXX-P3-SHOC-AQP1'

# compset = 'F-MMF1-SCM-ARM97'
# compset = 'F-MMF2-SCM-ARM97'
# compset = 'F-MMFXX-SCM-ARM97'
# compset = 'F-MMFXX-P3-SCM-ARM97'
# compset = 'F-MMFXX-P3-SHOC-SCM-ARM97'


ne,npg,arch,num_nodes,stop_opt,stop_n,resub,walltime = 4,2,'GNUCPU',2,'nsteps',5,0,'1:00'
# ne,npg,arch,num_nodes,stop_opt,stop_n,resub,walltime = 4,2,'GNUCPU',2,'ndays',5,0,'2:00'
# ne,npg,arch,num_nodes,stop_opt,stop_n,resub,walltime = 4,2,'GNUCPU',2,'ndays',1,0,'1:00'

# ne,npg,arch,num_nodes,stop_opt,stop_n,resub,walltime = 30,2,'GNUCPU',128,'ndays',1,0,'2:00'
# ne,npg,arch,num_nodes,stop_opt,stop_n,resub,walltime = 30,2,'GNUGPU',128,'ndays',2,0,'4:00'

# ne,npg,arch,num_nodes,stop_opt,stop_n,resub,walltime = 4,2,'GNUCPU',1,'nsteps',5,0,'0:30'

# ne,npg,arch,num_nodes,stop_opt,stop_n,resub,walltime = 4,2,'GNUCPU',1,'ndays',1,0,'1:00'
# ne,npg,arch,num_nodes,stop_opt,stop_n,resub,walltime = 4,2,'GNUGPU',1,'ndays',1,0,'1:00'



res = 'ne'+str(ne) if npg==0 else  'ne'+str(ne)+'pg'+str(npg)
# grid = f'{res}_r05_oECv3'
grid = f'{res}_{res}'


case = '.'.join(['E3SM','P3-TEST',arch,grid,compset,'00']) # baseline
# case = '.'.join(['E3SM','P3-TEST',arch,grid,compset,'01']) # after switching from qt to qv for P3
# case = '.'.join(['E3SM','P3-TEST',arch,grid,compset,'NO-MSA','00']) # baseline

# compset,arch='F-MMFXX'   ,'GNUCPU';case='.'.join(['E3SM','P3-TIMING','CPU',grid,'F-MMFXX-1M','00'])
# compset,arch='F-MMFXX-P3','GNUCPU';case='.'.join(['E3SM','P3-TIMING','CPU',grid,'F-MMFXX-P3','00'])
# compset,arch='F-MMFXX'   ,'GNUGPU';case='.'.join(['E3SM','P3-TIMING','GPU',grid,'F-MMFXX-1M','00'])
# compset,arch='F-MMFXX-P3','GNUGPU';case='.'.join(['E3SM','P3-TIMING','GPU',grid,'F-MMFXX-P3','00'])

# compset,arch='F-MMFXX-P3','GNUGPU';case='.'.join(['E3SM','P3-TIMING','GPU',grid,'F-MMFXX-P3','03']) # test moving lookup table init
# compset,arch='F-MMFXX-P3','GNUGPU';case='.'.join(['E3SM','P3-TIMING','GPU',grid,'F-MMFXX-P3','MSA','03']) # test enabling MSA and QT=>QV

# compset,arch='F-MMFXX-P3','GNUCPU';case='.'.join(['E3SM','P3-TIMING','CPU',grid,'F-MMFXX-P3','03']) # test QT=>QV
# compset,arch='F-MMFXX-P3','GNUCPU';case='.'.join(['E3SM','P3-TIMING','CPU',grid,'F-MMFXX-P3','MSA','03']) # test enabling MSA and QT=>QV

# compset,arch='F-MMFXX-P3','GNUGPU';case='.'.join(['E3SM','P3-TIMING','GPU',grid,'F-MMFXX-P3','01']) # add -DNDEBUG
# compset,arch='F-MMFXX-P3','ALTGPU';case='.'.join(['E3SM','P3-TIMING','ALTGPU',grid,'F-MMFXX-P3','00'])
# compset,arch='F-MMFXX-P3','ALTGPU';case='.'.join(['E3SM','P3-TIMING','ALTGPU',grid,'F-MMFXX-P3','01']) # 1x1


# src_dir  = f'{top_dir}/E3SM_SRC1'; case = '.'.join(['E3SM','P3-TEST',arch,grid,compset,'BVT','VT_QT_CHK','00']) # QT sum chk


if 'SCM' in compset: 
   arch = 'GNUCPU'
   stop_opt,stop_n,walltime = 'ndays',10,'01:00'
   npg = 0; grid = 'ne4_ne4'
   num_nodes = 1
   case = '.'.join(['E3SM','P3-TEST',arch,compset,'00'])
   # case = '.'.join(['E3SM','P3-TEST',arch,compset,'GCMDT_1','CRMDT_1','00'])
   # case = '.'.join(['E3SM','P3-TEST',arch,compset,'GCMDT_1','CRMDT_10','00'])


case = case+'.debug-on'
# case = case+'.checks-on'
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

# Impose wall limits for Summit
if 'walltime' not in locals():
   if num_nodes>=  1: walltime =  '2:00'
   if num_nodes>= 46: walltime =  '6:00'
   if num_nodes>= 92: walltime = '12:00'
   if num_nodes>=922: walltime = '24:00'


### specify atmos initial condition file
# # init_file_dir = '/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/init_files'
# init_file_dir = '/gpfs/alpine/scratch/hannah6/cli115/HICCUP/data/'
# params = [p.split('_') for p in case.split('.')]
# for p in params:
#    if p[0]=='NLEV': 
#       if p[1]!='72': 
#          if p[1]=='50': init_file_atm = f'HICCUP.cami_mam3_Linoz_ne{ne}np4.L{p[1]}_c20210623.nc'
#          if p[1]=='60': init_file_atm = f'HICCUP.cami_mam3_Linoz_ne{ne}np4.L{p[1]}.nc'

# if 'alt_vgrid' in case:
#    init_file_atm = 'HICCUP.cami_mam3_Linoz_ne30np4_L72_alt_c160214.nc'

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print(f'\n  case : {case}\n')

num_dyn = ne*ne*6

params = [p.split('_') for p in case.split('.')]
for p in params: 
   if p[0]=='GCMDT': dtime =  int(p[1])*60

# dtime = 20*60
if 'dtime' in locals(): ncpl  = 86400 / dtime  # comment to disable setting time step

max_task_per_node = 42
if 'CPU' in arch : max_mpi_per_node,atm_nthrds  = 42,1
if 'GPU' in arch : max_mpi_per_node,atm_nthrds  = 6,7
if arch=='ALTGPU' : max_task_per_node,max_mpi_per_node,atm_nthrds  = 1,1,1
task_per_node = max_mpi_per_node
atm_ntasks = task_per_node*num_nodes

if 'SCM' in compset:
   max_task_per_node = 1
   max_mpi_per_node  = 1
   atm_nthrds        = 1
   atm_ntasks        = 1

#-------------------------------------------------------------------------------
# Define run command
#-------------------------------------------------------------------------------
# Set up terminal colors
class tcolor:
   ENDC,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd,suppress_output=False,execute=True):
   if suppress_output : cmd = cmd + ' > /dev/null'
   msg = tcolor.GREEN + cmd + tcolor.ENDC
   if print_commands_only: 
      print(f'{msg}')
   else:
      print(f'\n{msg}')
      if execute: 
         os.system(cmd)
         # os.system(f'/bin/bash -c {cmd}')
         # sp.call(cmd.split(), shell=False)
         # sp.Popen(cmd, shell=True, executable='/bin/bash')
         # sp.Popen(['/bin/bash', '-c', cmd])
   return
#---------------------------------------------------------------------------------------------------
# Create new case
#---------------------------------------------------------------------------------------------------
if newcase :

   # Check if directory already exists
   if not print_commands_only:
      if os.path.isdir(f'{case_dir}/{case}'): 
         exit(tcolor.RED+"\nThis case already exists! Are you sure you know what you're doing?\n"+tcolor.ENDC)

   cmd = src_dir+f'/cime/scripts/create_newcase -case {case_dir}/{case}'
   cmd = cmd + f' -compset {compset} -res {grid} -mach summit '
   if arch=='GNUCPU' : cmd += f' -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='GNUGPU' : cmd += f' -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='ALTGPU' : cmd += f' -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='IBMGPU' : cmd += f' -compiler ibmgpu -pecount {atm_ntasks}x{atm_nthrds} '
   run_cmd(cmd)
   #-------------------------------------------------------
   # Change run directory to be next to bld directory
   #-------------------------------------------------------
   if not print_commands_only: 
      os.chdir(f'{case_dir}/{case}')
   else:
      print(tcolor.GREEN+f'cd {case_dir}/{case}/'+tcolor.ENDC)
   # run_cmd('./xmlchange -file env_run.xml RUNDIR=\'$CIME_OUTPUT_ROOT/$CASE/run\' ' )
   run_cmd('./xmlchange -file env_run.xml RUNDIR=\'/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/$CASE/run\' ' )
   #-------------------------------------------------------
   #-------------------------------------------------------
   run_cmd(f'./xmlchange -file env_mach_pes.xml -id MAX_TASKS_PER_NODE    -val {max_task_per_node} ')
   run_cmd(f'./xmlchange -file env_mach_pes.xml -id MAX_MPITASKS_PER_NODE -val {max_mpi_per_node} ')
else:
   if not print_commands_only: 
      os.chdir(f'{case_dir}/{case}')
   else:
      print(tcolor.GREEN+f'cd {case_dir}/{case}/'+tcolor.ENDC)
#---------------------------------------------------------------------------------------------------
# Configure
#---------------------------------------------------------------------------------------------------
if config :
   #-------------------------------------------------------
   if 'init_file_atm' in locals():
      file = open('user_nl_eam','w')
      # file.write(f' ncdata = \'{init_file_dir}/{init_file_atm}\'\n')
      file.write(f' ncdata = \'{init_file_atm}\'\n')
      file.close()
   #-------------------------------------------------------
   # # explicitly specify rad option
   # if '.RRTMG.'    in case: run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS  -val  \" -rad rrtmg \"')
   # if '.RRTMGP.'   in case: run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS  -val  \" -rad rrtmgp \"')
   # if '.RRTMGPXX.'   in case: run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS  -val  \" -rad rrtmgp -rrtmgpxx \"')

   # run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS  -val  \" -nlev  72  -crm_nz 64 \"')
   
   params = [p.split('_') for p in case.split('.')]
   for p in params: 
      if p[0]=='RADNX': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx_rad {p[1]} \" ')
      if p[0]=='CRMNX': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx {p[1]} \" ')
      if p[0]=='CRMNY': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_ny {p[1]} \" ')
      if p[0]=='CRMDX': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_dx {p[1]} \" ')
      if p[0]=='CRMNZ': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nz {p[1]} \" ')
      if p[0]=='CRMDT': run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_dt {p[1]} \" ')

   #-------------------------------------------------------
   # Add special MMF options based on case name
   cpp_opt = ''
   # cpp_opt = '-DNDEBUG'

   if 'VT_QT_CHK' in case: cpp_opt += ' -DVT_QT_CHK '

   # convective variance transport
   if any(x in case for x in ['.BVT.']): 
      run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -use_MMF_VT \" ')
   
   if 'debug-on' in case : cpp_opt += ' -DYAKL_DEBUG -DCMAKE_BUILD_TYPE=Debug '

   if cpp_opt != '' :
      cmd  = f'./xmlchange --append -file env_build.xml -id CAM_CONFIG_OPTS'
      cmd += f' -val \" -cppdefs \'{cpp_opt} \'  \" '
      run_cmd(cmd)

   #-------------------------------------------------------
   # Run case setup
   if clean : run_cmd('./case.setup --clean')
   run_cmd('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
# Build
#---------------------------------------------------------------------------------------------------
if build : 
   if 'debug-on' in case : run_cmd('./xmlchange -file env_build.xml -id DEBUG -val TRUE ')
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
# Write the namelist options and submit the run
#---------------------------------------------------------------------------------------------------
if submit : 
   #-------------------------------------------------------
   # Set some run-time stuff
   #-------------------------------------------------------
   if 'ncpl' in locals(): 
      run_cmd(f'./xmlchange ATM_NCPL={str(ncpl)},LND_NCPL={str(ncpl)},ICE_NCPL={str(ncpl)},OCN_NCPL={str(ncpl)}')
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
   run_cmd(f'./xmlchange JOB_QUEUE=batch,JOB_WALLCLOCK_TIME={walltime}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')

   if continue_run :
      run_cmd('./xmlchange -file env_run.xml CONTINUE_RUN=TRUE ')   
   else:
      run_cmd('./xmlchange -file env_run.xml CONTINUE_RUN=FALSE ')

   #-------------------------------------------------------
   # ATM namelist
   #-------------------------------------------------------
   if not print_commands_only: 
      # Change inputdata from default due to permissions issue
      # run_cmd('./xmlchange DIN_LOC_ROOT=/gpfs/alpine/cli115/scratch/hannah6/inputdata ')
      run_cmd('./xmlchange DIN_LOC_ROOT=/gpfs/alpine/cli115/world-shared/e3sm/inputdata ')
      
      #-------------------------------------------------------
      # First query some stuff about the case
      #-------------------------------------------------------
      (ncpl        ,err) = sp.Popen('./xmlquery ATM_NCPL        -value',stdout=sp.PIPE,shell=True,universal_newlines=True).communicate()
      (din_loc_root,err) = sp.Popen('./xmlquery DIN_LOC_ROOT    -value',stdout=sp.PIPE,shell=True,universal_newlines=True).communicate()
      (config_opts ,err) = sp.Popen('./xmlquery CAM_CONFIG_OPTS -value',stdout=sp.PIPE,shell=True,universal_newlines=True).communicate()
      config_opts = ' '.join(config_opts.split())   # remove extra spaces to simplify string query
      #-------------------------------------------------------
      # Namelist options
      #-------------------------------------------------------
      nfile = 'user_nl_eam'
      file = open(nfile,'w') 
      #------------------------------
      # Specify history output frequency and variables
      #------------------------------
      file.write( ' nhtfrq    = 0,1 \n') 
      file.write(f' mfilt     = 1,{ncpl} \n')
      # if stop_opt=='nsteps' or stop_opt=='nstep' :
      #    file.write( ' nhtfrq    = 0,1 \n') 
      #    file.write(f' mfilt     = 1,{stop_n} \n')
      # else:
      #    file.write(' nhtfrq    = 0,-3 \n')
      #    file.write(' mfilt     = 1, 8 \n')
      file.write('\n')
      file.write(" fincl2    = 'PS','TS','PSL'")
      file.write(             ",'PRECT','TMQ'")
      file.write(             ",'PRECC','PRECSC'")
      file.write(             ",'PRECL','PRECSL'")
      file.write(             ",'LHFLX','SHFLX'")             # surface fluxes
      file.write(             ",'FSNT','FLNT'")               # Net TOM heating rates
      file.write(             ",'FLNS','FSNS'")               # Surface rad for total column heating
      file.write(             ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
      # file.write(             ",'LWCF','SWCF'")               # cloud radiative foricng
      file.write(             ",'TGCLDLWP','TGCLDIWP'")       # cloud water path
      # file.write(             ",'TGPRCLWP','TGPRCIWP'")       # precipitating water path
      # file.write(             ",'CLDLOW','CLDMED','CLDHGH','CLDTOT' ")
      # file.write(             ",'TAUX','TAUY'")               # surface stress
      # file.write(             ",'UBOT','VBOT'")
      # file.write(             ",'TBOT','QBOT'")
      # file.write(             ",'OMEGA850','OMEGA500'")
      file.write(             ",'T850','Q850'")
      # file.write(             ",'U200','U850'")
      # file.write(             ",'V200','V850'")
      
      if 'MMF' in compset: file.write(",'MMF_SUBCYCLE_FAC'")

      if 'SCM' in compset:
         file.write(             ",'T','Q','Z3' ")              # 3D thermodynamic budget components
         file.write(             ",'U','V','OMEGA'")            # 3D velocity components
         file.write(             ",'CLOUD','CLDLIQ','CLDICE'")  # 3D cloud fields
         file.write(             ",'QRL','QRS'")                # 3D radiative heating profiles

      if 'SCM' in compset:
         file.write(            ",'CRM_QV','CRM_QC','CRM_QI'")
         file.write(            ",'CRM_T','CRM_U','CRM_W'")
         file.write(            ",'CRM_PREC'")
         file.write(         ",'MMF_QC','MMF_QI','MMF_QR'")
         if 'MMFXX-P3' in compset:
            file.write(         ",'NUMLIQ','NUMICE'")
            file.write(         ",'CRM_NC','CRM_NI'")
            file.write(         ",'CRM_QR','CRM_NR'")
            file.write(         ",'MMF_NC','MMF_NI'")

      file.write('\n')
      #------------------------------
      # Other namelist stuff
      #------------------------------
      # if 'init_file_atm' in locals(): file.write(f' ncdata = \'{init_file_dir}/{init_file_atm}\'\n')
      if 'init_file_atm' in locals(): file.write(f' ncdata = \'{init_file_atm}\'\n')

      if num_dyn>0 and num_dyn<atm_ntasks: 
         file.write(' dyn_npes = '+str(num_dyn)+' \n')   # limit dynamics tasks

      if 'checks-on' in case : file.write(' state_debug_checks = .true. \n')

      # file.write(" inithist = \'ENDOFRUN\' \n") # ENDOFRUN / NONE

      file.close()

      if 'P3-TIMING' in case:
         nfile = 'user_nl_eam'
         file = open(nfile,'w') 
         file.write('\n')
         file.close()
         # Disable restart file write for timing
         run_cmd('./xmlchange -file env_run.xml -id REST_OPTION -val never')


      if '.NO-MSA.' in case: 
         nfile = 'user_nl_eam'
         file = open(nfile,'a') 
         file.write(' use_crm_accel = .false.\n')
         file.close()
      if '.MSA.' in case: 
         nfile = 'user_nl_eam'
         file = open(nfile,'a') 
         file.write(' use_crm_accel = .true.\n')
         file.write(' crm_accel_uv = .true.\n')
         # file.write(' use_crm_accel = .false.\n') # temporary sanity check
         # file.write(' crm_accel_uv = .false.\n')
         file.close()

   #-------------------------------------------------------
   # Copy the P3 data directory to the run directory
   #-------------------------------------------------------
   if 'P3' in compset:
      data_dir = f'{src_dir}/components/eam/src/physics/crm/scream/data'
      # run_dir  = f'/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/{case}/run/'
      run_dir  = f'{top_dir}/scratch/{case}/run/'
      run_cmd(f'cp -R {data_dir} {run_dir}')

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
