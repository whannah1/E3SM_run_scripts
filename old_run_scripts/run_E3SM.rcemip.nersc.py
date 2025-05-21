#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
import os
import subprocess as sp
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm3312'    # m3312 / m3305

top_dir  = os.getenv('HOME')+'/E3SM/'
case_dir = top_dir+'Cases/'
src_dir  = top_dir+'E3SM_SRC4/'

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

queue = 'debug'  # regular / debug

ne,npg = 30,2        # use ne = 4 or 30, leave npg=0 for now
# compset = 'F-EAMv1-RCEMIP'
# compset = 'F-MMFXX-RCEMIP'
compset = 'F-MMFXX-RCEROT'

if queue=='debug' : 
   stop_opt,stop_n,resub,walltime = 'ndays',1,0,'0:30:00'
   # stop_opt,stop_n,resub,walltime = 'nsteps',3,0,'0:30:00'
else:
   # stop_opt,stop_n,resub,walltime = 'ndays',73,4,'2:00:00'
   stop_opt,stop_n,resub,walltime = 'ndays',31,6,'3:00:00'
   # stop_opt,stop_n,resub,walltime = 'ndays',15,0,'2:00:00'

# Set grid string
res = 'ne'+str(ne) if npg==0 else 'ne'+str(ne)+'pg'+str(npg)

# # Retreive current git hash for case name
# git_hash = sp.check_output(f'cd {src_dir}; git log -n1 --format=format:"%H"',
#                            shell=True,universal_newlines=True)
# case = f'E3SM_{compset}_{res}_master-{git_hash[-6:]}'   # control

# case = '.'.join(['E3SM',res,compset,'00'])
# case = '.'.join(['E3SM',res,compset,'BVT','00'])
case = '.'.join(['E3SM',res,compset,'BVT','01']) # includes MSE budget terms

# case = case+'_debug-on'
# case = case+'_checks-on'

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

num_dyn = ne*ne*6
dtime = 20*60           # use 20 min for SP (default is 30 min for E3SM @ ne30)
if ne==120: dtime = 5*60
ncpl  = 86400 / dtime

# Enforce max node limit on debug queue
# if queue=='debug' and num_dyn>(64*32) : num_dyn = 64*32
# if num_dyn==0 : num_dyn = 4000

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

#---------------------------------------------------------------------------------------------------
# Create new case
#---------------------------------------------------------------------------------------------------
if newcase :
   grid = res+'_'+res
   cmd  = src_dir+'cime/scripts/create_newcase -case '+case_dir+case
   cmd += ' -compset '+compset
   cmd += ' -res '+grid
   # cmd += ' --pecount 2720x1'
   cmd = cmd +' --pecount '+str(num_dyn)+'x1'
   run_cmd(cmd)
#---------------------------------------------------------------------------------------------------
# Configure
#---------------------------------------------------------------------------------------------------
os.chdir(case_dir+case+'/')
if config : 

   # Add special MMF options based on case name
   cpp_opt = ''
   if '.FLUX-BYPASS.' in case: cpp_opt += ' -DMMF_FLUX_BYPASS '
   if '.ESMT.'        in case: cpp_opt += ' -DMMF_ESMT -DMMF_USE_ESMT'
   if '.SGS.'         in case: cpp_opt += ' -DMMF_SGS_TUNE '
   if '.SFC.'         in case: cpp_opt += ' -DMMF_DO_SURFACE'
   
   # CRM variance transport
   if any(x in case for x in ['.BVT.','.FVT']): 
      run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -use_MMF_VT \" ')

   if cpp_opt != '' :
      cmd  = f'./xmlchange --append -file env_build.xml -id CAM_CONFIG_OPTS'
      cmd += f' -val \" -cppdefs \'-DMMF_DIR_NS {cpp_opt} \'  \" '
      run_cmd(cmd)

   # 64_data format is needed for large output files
   run_cmd('./xmlchange PIO_NETCDF_FORMAT=\"64bit_data\" ')
   
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
   # First query some stuff about the case
   #-------------------------------------------------------
   (din_loc_root   , err) = sp.Popen('./xmlquery DIN_LOC_ROOT    -value', \
                                     stdout=sp.PIPE, shell=True).communicate()
   (cam_config_opts, err) = sp.Popen('./xmlquery CAM_CONFIG_OPTS -value', \
                                     stdout=sp.PIPE, shell=True, \
                                     universal_newlines=True).communicate()
   cam_config_opts = ' '.join(cam_config_opts.split())   # remove extra spaces to simplify string query
   #-------------------------------------------------------
   # Namelist options
   #-------------------------------------------------------
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   #------------------------------
   # Specify history output frequency and variables
   #------------------------------   
   file.write(' nhtfrq    = 0,-3,-24 \n')
   file.write(' mfilt     = 1,8,1 \n')
   file.write('\n')
   file.write(" fincl1    = 'Z3'")
   file.write(             ",'DDSE_TOT','DQLV_TOT'") # Total Eulerian MSE tendencies
   file.write(             ",'DDSE_DYN','DQLV_DYN'") # Dynamics MSE tendencies
   file.write(             ",'DDSE_CRM','DQLV_CRM'") # 
   file.write(             ",'DDSE_QRS','DDSE_QRL'") # 
   file.write(             ",'DDSE_CEF','DQLV_CEF'") # 
   file.write(             ",'DDSE_PBL','DQLV_PBL'") # 
   file.write(             ",'DDSE_GWD'")            #  
   file.write('\n')

   file.write(" fincl2    = 'PS','TS'")
   file.write(             ",'PRECT','TMQ'")
   file.write(             ",'LHFLX','SHFLX'")             # surface fluxes
   file.write(             ",'TAUX','TAUY'")               # surface stress
   file.write(             ",'TBOT','QBOT'")
   file.write(             ",'UBOT','VBOT'")
   file.write(             ",'U200','V200'")
   file.write(             ",'U850','V850'")
   file.write(             ",'OMEGA850','OMEGA500'")
   file.write(             ",'TGCLDLWP','TGCLDIWP'")       # liquid and ice water paths
   file.write(             ",'FSNT','FLNT'")               # Net TOM heating rates
   file.write(             ",'FLNS','FSNS'")               # Surface rad for total column heating
   file.write(             ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
   file.write('\n')
   
   file.write(" fincl3    = ,'T','Q','Z3' ")               # 3D thermodynamic budget components
   file.write(             ",'U','V','OMEGA'")             # 3D velocity components
   file.write(             ",'CLDLIQ','CLDICE'")           # 3D cloud fields
   # file.write(             ",'QRL','QRS'")                 # 3D radiative heating profiles
   file.write(             ",'DDSE_TOT','DQLV_TOT'") # Total Eulerian MSE tendencies
   file.write(             ",'DDSE_DYN','DQLV_DYN'") # Dynamics MSE tendencies
   file.write(             ",'DDSE_CRM','DQLV_CRM'") # 
   file.write(             ",'DDSE_QRS','DDSE_QRL'") # 
   file.write(             ",'DDSE_CEF','DQLV_CEF'") # 
   file.write(             ",'DDSE_PBL','DQLV_PBL'") # 
   file.write(             ",'DDSE_GWD'")            # 
   
   file.write('\n')
   #------------------------------
   # Other namelist stuff
   #------------------------------
   # file.write(' srf_flux_avg = 1 \n')              # Sfc flux smoothing (for SP stability)
   # file.write(' dyn_npes = '+str(num_dyn)+' \n')   # limit dynamics tasks

   # file.write(' use_crm_accel = .false. \n')

   # se_nsplit,rsplit = 20,3
   # file.write(" rsplit    = "+str(   rsplit)+" \n")
   # file.write(" se_nsplit = "+str(se_nsplit)+" \n")

   # file.write(" inithist = \'MONTHLY\' \n")
   # file.write(' inithist = \'ENDOFRUN\' \n')

   if 'checks-on' in case : file.write(' state_debug_checks = .true. \n')

   file.close()


   if ne==120 and npg==2 : run_cmd('./xmlchange -file env_run.xml      EPS_AGRID=1e-11' )
         
   #-------------------------------------------------------
   # Set some run-time stuff
   #-------------------------------------------------------
   run_cmd('./xmlchange -file env_run.xml      ATM_NCPL='   +str(ncpl)   )
   run_cmd('./xmlchange -file env_run.xml      STOP_OPTION='+stop_opt    )
   run_cmd('./xmlchange -file env_run.xml      STOP_N='     +str(stop_n) )
   run_cmd('./xmlchange -file env_run.xml      RESUBMIT='   +str(resub)  )

   def xml_check_and_set(file_name,var_name,value):
      if var_name in open(file_name).read(): 
         run_cmd('./xmlchange -file '+file_name+' '+var_name+'='+str(value) )
   
   xml_check_and_set('env_workflow.xml','JOB_QUEUE',           queue)
   xml_check_and_set('env_batch.xml',   'USER_REQUESTED_QUEUE',queue)
   xml_check_and_set('env_workflow.xml','JOB_WALLCLOCK_TIME',     walltime)
   xml_check_and_set('env_batch.xml',   'USER_REQUESTED_WALLTIME',walltime)
   
   xml_check_and_set('env_workflow.xml','CHARGE_ACCOUNT',acct)
   xml_check_and_set('env_workflow.xml','PROJECT',acct)

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
