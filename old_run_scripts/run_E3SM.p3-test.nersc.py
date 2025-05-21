#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp#, numpy as np
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm3312'

top_dir  = os.getenv('HOME')+'/E3SM'
case_dir = f'{top_dir}/Cases'
src_dir  = f'{top_dir}/E3SM_SRC1'

print_commands_only = False

# clean        = True
newcase      = True
config       = True
# build        = True
# submit       = True
# continue_run = True

# compset = 'F-MMFXX'
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


ne,npg,num_nodes,stop_opt,stop_n,resub,walltime = 4,2,1,'nsteps',5,0,'0:10'


res = 'ne'+str(ne) if npg==0 else  'ne'+str(ne)+'pg'+str(npg)
# grid = f'{res}_r05_oECv3'
grid = f'{res}_{res}'


# case = '.'.join(['E3SM','P3-TEST',arch,grid,compset,'00']) # baseline


# compset='F-MMFXX'   ;case='.'.join(['E3SM','P3-TIMING',grid,'F-MMFXX-1M','00'])
compset='F-MMFXX-P3';case='.'.join(['E3SM','P3-TIMING',grid,'F-MMFXX-P3','00'])


if 'SCM' in compset: 
   stop_opt,stop_n,walltime = 'ndays',10,'01:00'
   npg = 0; grid = 'ne4_ne4'
   num_nodes = 1
   case = '.'.join(['E3SM','P3-TEST',compset,'00'])


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

task_per_node = 64
atm_ntasks = num_nodes*task_per_node
atm_nthrds = 1


if 'SCM' in compset:
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
   cmd = cmd + f' -compset {compset} -res {grid} -mach cori-knl '
   cmd += f' -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
   run_cmd(cmd)
   #-------------------------------------------------------
   #-------------------------------------------------------

if not print_commands_only: 
   os.chdir(f'{case_dir}/{case}')
else:
   print(tcolor.GREEN+f'cd {case_dir}/{case}/'+tcolor.ENDC)
#---------------------------------------------------------------------------------------------------
# Configure
#---------------------------------------------------------------------------------------------------
if config :
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
      # nfile = 'user_nl_eam'
      # file = open(nfile,'w') 
      # #------------------------------
      # # Specify history output frequency and variables
      # #------------------------------
      # file.write( ' nhtfrq    = 0,1 \n') 
      # file.write(f' mfilt     = 1,{ncpl} \n')
      # # if stop_opt=='nsteps' or stop_opt=='nstep' :
      # #    file.write( ' nhtfrq    = 0,1 \n') 
      # #    file.write(f' mfilt     = 1,{stop_n} \n')
      # # else:
      # #    file.write(' nhtfrq    = 0,-3 \n')
      # #    file.write(' mfilt     = 1, 8 \n')
      # file.write('\n')
      # file.write(" fincl2    = 'PS','TS','PSL'")
      # file.write(             ",'PRECT','TMQ'")
      # file.write(             ",'PRECC','PRECSC'")
      # file.write(             ",'PRECL','PRECSL'")
      # file.write(             ",'LHFLX','SHFLX'")             # surface fluxes
      # file.write(             ",'FSNT','FLNT'")               # Net TOM heating rates
      # file.write(             ",'FLNS','FSNS'")               # Surface rad for total column heating
      # file.write(             ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
      # # file.write(             ",'LWCF','SWCF'")               # cloud radiative foricng
      # file.write(             ",'TGCLDLWP','TGCLDIWP'")       # cloud water path
      # # file.write(             ",'TGPRCLWP','TGPRCIWP'")       # precipitating water path
      # # file.write(             ",'CLDLOW','CLDMED','CLDHGH','CLDTOT' ")
      # # file.write(             ",'TAUX','TAUY'")               # surface stress
      # # file.write(             ",'UBOT','VBOT'")
      # # file.write(             ",'TBOT','QBOT'")
      # # file.write(             ",'OMEGA850','OMEGA500'")
      # file.write(             ",'T850','Q850'")
      # # file.write(             ",'U200','U850'")
      # # file.write(             ",'V200','V850'")
      
      # if 'MMF' in compset: file.write(",'MMF_SUBCYCLE_FAC'")

      # if 'SCM' in compset:
      #    file.write(             ",'T','Q','Z3' ")              # 3D thermodynamic budget components
      #    file.write(             ",'U','V','OMEGA'")            # 3D velocity components
      #    file.write(             ",'CLOUD','CLDLIQ','CLDICE'")  # 3D cloud fields
      #    file.write(             ",'QRL','QRS'")                # 3D radiative heating profiles

      # if 'SCM' in compset:
      #    file.write(            ",'CRM_QV','CRM_QC','CRM_QI'")
      #    file.write(            ",'CRM_T','CRM_U','CRM_W'")
      #    file.write(            ",'CRM_PREC'")
      #    file.write(         ",'MMF_QC','MMF_QI','MMF_QR'")
      #    if 'MMFXX-P3' in compset:
      #       file.write(         ",'NUMLIQ','NUMICE'")
      #       file.write(         ",'CRM_NC','CRM_NI'")
      #       file.write(         ",'CRM_QR','CRM_NR'")
      #       file.write(         ",'MMF_NC','MMF_NI'")

      # file.write('\n')
      #------------------------------
      # Other namelist stuff
      #------------------------------
      # # if 'init_file_atm' in locals(): file.write(f' ncdata = \'{init_file_dir}/{init_file_atm}\'\n')
      # if 'init_file_atm' in locals(): file.write(f' ncdata = \'{init_file_atm}\'\n')

      # if num_dyn>0 and num_dyn<atm_ntasks: 
      #    file.write(' dyn_npes = '+str(num_dyn)+' \n')   # limit dynamics tasks

      # if 'checks-on' in case : file.write(' state_debug_checks = .true. \n')

      # # file.write(" inithist = \'ENDOFRUN\' \n") # ENDOFRUN / NONE

      # file.close()

      if 'P3-TIMING' in case:
         nfile = 'user_nl_eam'
         file = open(nfile,'w') 
         file.write('\n')
         file.close()
         # Disable restart file write for timing
         run_cmd('./xmlchange -file env_run.xml -id REST_OPTION -val never')

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
