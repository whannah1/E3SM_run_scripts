#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'e3sm'

top_dir  = os.getenv('HOME')+'/E3SM'
case_dir = f'{top_dir}/Cases/'

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

stop_opt,stop_n,resub,walltime = 'ndays',31,0,'1:00:00'

src_dir,compset,grid = f'{top_dir}/E3SMv1/','A_WCYCL1850S_CMIP6','ne30_oECv3'
# src_dir,compset,grid = f'{top_dir}/E3SMv2/','WCYCL1850','ne30pg2_EC30to60E2r2'

# ntasks,nthrds =  10*64,1
# ntasks,nthrds =  20*64,1
ntasks,nthrds =  40*64,1
# ntasks,nthrds =  80*64,1
# ntasks,nthrds = 160*64,1

# ntasks,nthrds==  675,1 # ~ 10.5 nodes
# ntasks,nthrds== 1350,1 # ~ 21.1 nodes
# ntasks,nthrds== 5400,1 # ~ 84.4 nodes
# ntasks,nthrds==10800,1 # ~168.8 nodes

case = '.'.join(['E3SM','perf-test',grid,compset,f'NTASKS_{ntasks}',f'NTHRDS_{nthrds}','00'])

# pelayout='S';case = '.'.join(['E3SM','perf-test',grid,compset,f'PELAYOUT_{pelayout}','00'])
# pelayout='M';case = '.'.join(['E3SM','perf-test',grid,compset,f'PELAYOUT_{pelayout}','00'])
# pelayout='L';case = '.'.join(['E3SM','perf-test',grid,compset,f'PELAYOUT_{pelayout}','00'])

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

#-------------------------------------------------------------------------------
# Define run command
#-------------------------------------------------------------------------------
# Set up terminal colors
class tcolor:
   ENDC,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd,suppress_output=False,execute=True):
   if suppress_output : cmd = cmd + ' > /dev/null'
   msg = tcolor.GREEN + cmd + tcolor.ENDC
   print(f'\n{msg}')
   if execute: os.system(cmd)
   return
def xml_check_and_set(file_name,var_name,value):
   if var_name in open(file_name).read(): 
      run_cmd('./xmlchange -file '+file_name+' '+var_name+'='+str(value) )
#---------------------------------------------------------------------------------------------------
# Create new case
#---------------------------------------------------------------------------------------------------
if newcase :
   cmd  = f'{src_dir}/cime/scripts/create_newcase -case {case_dir}/{case} '
   cmd += f' -compset {compset} -res {grid} '
   # if 'NTASKS'   in case: cmd += f' -pecount {ntasks}x{nthrds}'
   if 'NTASKS'   in case: cmd += f' -pecount {ntasks}x1'
   if 'PELAYOUT' in case: cmd += f' -pecount {pelayout}'
   run_cmd(cmd)
#---------------------------------------------------------------------------------------------------
# Configure
#---------------------------------------------------------------------------------------------------
os.chdir(case_dir+case+'/')
if config :
   # S =~21 nodes; ['CPL:1408', 'ATM:1350', 'LND:64', 'ICE:1344', 'OCN:384', 'ROF:64', 'GLC:1', 'WAV:1', 'IAC:1', 'ESP:1']
   # M = 43 nodes; ['CPL:2752', 'ATM:2752', 'LND:192', 'ICE:2560', 'OCN:640', 'ROF:192', 'GLC:1', 'WAV:1', 'IAC:1', 'ESP:1']
   # L =~84 nodes; ['CPL:5440', 'ATM:5400', 'LND:320', 'ICE:5120', 'OCN:1280', 'ROF:320', 'GLC:1', 'WAV:1', 'IAC:1', 'ESP:1']
   #-------------------------------------------------------
   # Set tasks for all components
   
   # if ntasks==  10*64: alt_ntask =  150
   # if ntasks==  20*64: alt_ntask =  300
   # if ntasks==  40*64: alt_ntask =  600
   # if ntasks==  80*64: alt_ntask = 1200
   # if ntasks== 160*64: alt_ntask = 2400

   if ntasks==  10*64: alt_ntask =  2*64 #  128
   if ntasks==  20*64: alt_ntask =  4*64 #  256
   if ntasks==  40*64: alt_ntask =  8*64 #  512
   if ntasks==  80*64: alt_ntask = 16*64 # 1024
   if ntasks== 160*64: alt_ntask = 32*64 # 2048

   # if ntasks==   675: alt_ntask =  150
   # if ntasks==  1350: alt_ntask =  300
   # if ntasks==  5400: alt_ntask = 1200
   # if ntasks== 10800: alt_ntask = 2400

   cmd = './xmlchange -file env_mach_pes.xml '
   cmd += f'NTASKS_ATM={ntasks}'
   cmd += f',NTASKS_LND={alt_ntask},NTASKS_CPL={ntasks}'
   cmd += f',NTASKS_OCN={alt_ntask},NTASKS_ICE={alt_ntask}'
   cmd += f',NTASKS_ROF=64,NTASKS_WAV=1,NTASKS_GLC=1'
   cmd += f',NTASKS_ESP=1,NTASKS_IAC=1'
   run_cmd(cmd)
   #-------------------------------------------------------
   # Set thread count
   cmd = f'./xmlchange -file env_mach_pes.xml '
   cmd += f'NTHRDS_CPL={nthrds},NTHRDS_ATM={nthrds},'
   cmd += f'NTHRDS_OCN={nthrds},NTHRDS_ICE={nthrds}'
   run_cmd(cmd)
   #-------------------------------------------------------
   if clean : run_cmd('./case.setup --clean')
   run_cmd('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
# Build
#---------------------------------------------------------------------------------------------------
if build : 
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
# Write the namelist options and submit the run
#---------------------------------------------------------------------------------------------------
if submit : 
   #-------------------------------------------------------
   # Namelist options
   #-------------------------------------------------------
   # nfile = 'user_nl_eam'
   # file = open(nfile,'w') 
   #------------------------------
   # Specify history output frequency and variables
   #------------------------------   
   # file.write(' nhtfrq    = 0,-3 \n')
   # file.write(' mfilt     = 1,8 \n')
   # file.write('\n')
   # file.write(" fincl2    = 'PS','TS'")
   # file.write(             ",'PRECT','TMQ'")
   # file.write(             ",'LHFLX','SHFLX'")             # surface fluxes
   # file.write(             ",'TAUX','TAUY'")               # surface stress
   # file.write(             ",'TBOT','QBOT'")
   # file.write(             ",'UBOT','VBOT'")
   # file.write(             ",'U200','V200'")
   # file.write(             ",'U850','V850'")
   # file.write(             ",'OMEGA850','OMEGA500'")
   # file.write(             ",'TGCLDLWP','TGCLDIWP'")       # liquid and ice water paths
   # file.write(             ",'FSNT','FLNT'")               # Net TOM heating rates
   # file.write(             ",'FLNS','FSNS'")               # Surface rad for total column heating
   # file.write(             ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
   # file.write(             ",'LWCF','SWCF'")               # cloud radiative foricng
   # file.write(             ",'VOR','DIV'")
   # file.write(             ",'CLDLOW','CLDMED','CLDHGH','CLDTOT' ")
   # file.write('\n')
   # file.close()
   #-------------------------------------------------------
   # Set some run-time stuff
   #-------------------------------------------------------
   # run_cmd('./xmlchange -file env_run.xml      ATM_NCPL='   +str(ncpl)   )
   run_cmd('./xmlchange -file env_run.xml      STOP_OPTION='+stop_opt    )
   run_cmd('./xmlchange -file env_run.xml      STOP_N='     +str(stop_n) )
   run_cmd('./xmlchange -file env_run.xml      RESUBMIT='   +str(resub)  )

   # xml_check_and_set('env_workflow.xml','JOB_QUEUE',           queue)
   # xml_check_and_set('env_batch.xml',   'USER_REQUESTED_QUEUE',queue)
   # xml_check_and_set('env_workflow.xml','JOB_WALLCLOCK_TIME',     walltime)
   xml_check_and_set('env_batch.xml',   'USER_REQUESTED_WALLTIME',walltime)
   
   # xml_check_and_set('env_batch.xml','CHARGE_ACCOUNT',acct)
   # xml_check_and_set('env_batch.xml','PROJECT',acct)

   if continue_run :
      run_cmd('./xmlchange -file env_run.xml CONTINUE_RUN=TRUE ')   
   else:
      run_cmd('./xmlchange -file env_run.xml CONTINUE_RUN=FALSE ')
   #-------------------------------------------------------
   # Submit the run
   #-------------------------------------------------------
   run_cmd('./case.submit')

#---------------------------------------------------------------------------------------------------
# Done!
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n') # Print the case name again
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
