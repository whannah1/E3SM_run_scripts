#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
import os
import subprocess as sp
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'e3sm'    # m3312 / m3305 / e3sm
top_dir  = '/global/homes/w/whannah/E3SM/'
case_dir = top_dir+'Cases/'

# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
# continue_run = True
queue = 'regular'  # regular / debug

src_dir  = top_dir+'E3SM_SRC1/'      # master


compset = 'F-EAMv1-AQP1'

ne = 120
grid = f'ne{ne}_ne{ne}'
# grid = 'conusx4v1_conusx4v1'

if queue=='debug'  : stop_opt,stop_n,resub,walltime = 'ndays',5,0,'0:30:00'
if queue=='regular': 
   if ne==16:  stop_opt,stop_n,resub,walltime = 'ndays',60,0,'4:00:00'
   if ne==120: stop_opt,stop_n,resub,walltime = 'ndays',30,1,'8:00:00'


# hv_scaling = 2.0
# hv_scaling = 2.4
# hv_scaling = 2.8
hv_scaling = 3.2
# hv_scaling = 3.6


case = '.'.join(['E3SM','HVS',grid,compset,f'hvs_{hv_scaling}'])

if ne==120: ncdata = '/global/cscratch1/sd/whannah/e3sm_scratch/init_files/cami_aquaplanet_ne120np4_L72_c200514.nc'

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

dtime = 15*60
ncpl  = 86400 / dtime
#---------------------------------------------------------------------------------------------------
# Create new case
#---------------------------------------------------------------------------------------------------
if newcase :
   cmd = src_dir+'cime/scripts/create_newcase -case '+case_dir+case
   cmd += f' -compset {compset}'
   cmd += f' -res {grid}'
   # Set consistent pecount for all cases with new 2010 compset
   # cmd += f' --pecount 2720x1'
   os.system(cmd)
#---------------------------------------------------------------------------------------------------
# Configure
#---------------------------------------------------------------------------------------------------
os.chdir(case_dir+case+'/')
if config : 
   
   if ne==30: 
      os.system('./xmlchange -file env_mach_pes.xml -id NTASKS_ATM -val 2720 ')
      os.system('./xmlchange -file env_mach_pes.xml -id NTASKS_CPL -val 1350 ')
      os.system('./xmlchange -file env_mach_pes.xml -id NTASKS_OCN -val 1200 ')
      os.system('./xmlchange -file env_mach_pes.xml -id NTASKS_WAV -val 32 ')
      os.system('./xmlchange -file env_mach_pes.xml -id NTASKS_GLC -val 32 ')
      os.system('./xmlchange -file env_mach_pes.xml -id NTASKS_ICE -val 1350 ')
      os.system('./xmlchange -file env_mach_pes.xml -id NTASKS_ROF -val 32 ')

      os.system('./xmlchange -file env_mach_pes.xml -id NTHRDS_ATM -val 2 ')
      os.system('./xmlchange -file env_mach_pes.xml -id NTHRDS_CPL -val 2 ')

   if clean : os.system('./case.setup --clean')
   os.system('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
# Build
#---------------------------------------------------------------------------------------------------
if build : 
   if 'debug-on' in case : os.system('./xmlchange -file env_build.xml -id DEBUG -val TRUE ')
   if clean : os.system('./case.build --clean')
   os.system('./case.build')
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
   nfile = 'user_nl_cam'
   file = open(nfile,'w') 
   #------------------------------
   # Specify history output frequency and variables
   #------------------------------
   file.write(' nhtfrq    = 0,-3 \n')
   file.write(' mfilt     = 1,40 \n')
   file.write('\n')
   file.write(" fincl2    = 'PS','TS'")
   file.write(             ",'PRECT','TMQ'")
   file.write(             ",'LHFLX','SHFLX'")             # surface fluxes
   file.write(             ",'FSNT','FLNT'")               # Net TOM heating rates
   file.write(             ",'FLNS','FSNS'")               # Surface rad for total column heating
   file.write(             ",'TGCLDLWP','TGCLDIWP'")    
   file.write(             ",'TBOT','QBOT','T500','T850','Q850'")
   file.write(             ",'OMEGA850:I','OMEGA500:I'")
   file.write(             ",'U200:I','U850:I','UBOT:I'")
   file.write(             ",'V200:I','V850:I','VBOT:I'")
   # if npg>0: file.write(   ",'DYN_T','DYN_Q','DYN_U','DYN_OMEGA','DYN_PS'")
   file.write('\n')
   #------------------------------
   # Other namelist stuff
   #------------------------------
   # file.write(f' hypervis_scaling = {hv_scaling} \n')
   # file.write(' hypervis_subcycle = 7 \n')
   # file.write(' nu       = 1e15 \n')
   # file.write(' nu_div   = 20.0e-8 \n')
   # file.write(' qsplit    = 1 \n')
   # file.write(' rsplit    = 3 \n')
   # file.write(' se_nsplit = 4 \n')

   nu = 1e15*(ne/30.)**(-1.*hv_scaling)

   file.write(f' nu       = {nu:.2E} \n')
   file.write(f' nu_div   = {nu:.2E} \n')
   # file.write(f' nu_div   = {2.5*nu} \n')

   if 'ncdata' in locals(): file.write(f' ncdata = \'{ncdata}\' \n')

   # if npg>0 : file.write(' se_fv_phys_remap_alg = 1 \n')
   # file.write(" inithist = \'YEARLY\' \n") # ENDOFRUN
   file.close()

   os.system('./xmlchange -file env_run.xml EPS_FRAC=3e-2' ) # default=1e-2
   #-------------------------------------------------------
   # Set some run-time stuff
   #-------------------------------------------------------
   os.system('./xmlchange -file env_run.xml  ATM_NCPL='   +str(ncpl)   )
   os.system('./xmlchange -file env_run.xml STOP_OPTION='+stop_opt    )
   os.system('./xmlchange -file env_run.xml STOP_N='     +str(stop_n) )
   os.system('./xmlchange -file env_run.xml RESUBMIT='   +str(resub)  )

   def xml_check_and_set(file_name,var_name,value):
      if var_name in open(file_name).read(): 
         os.system('./xmlchange -file '+file_name+' '+var_name+'='+str(value) )
   
   xml_check_and_set('env_workflow.xml','JOB_QUEUE',           queue)
   xml_check_and_set('env_batch.xml',   'USER_REQUESTED_QUEUE',queue)
   xml_check_and_set('env_workflow.xml','JOB_WALLCLOCK_TIME',     walltime)
   xml_check_and_set('env_batch.xml',   'USER_REQUESTED_WALLTIME',walltime)
   xml_check_and_set('env_workflow.xml','CHARGE_ACCOUNT',acct)
   xml_check_and_set('env_workflow.xml','PROJECT',acct)
   
   if continue_run :
      os.system('./xmlchange -file env_run.xml CONTINUE_RUN=TRUE ')   
   else:
      os.system('./xmlchange -file env_run.xml CONTINUE_RUN=FALSE ')
   #-------------------------------------------------------
   # Submit the run
   #-------------------------------------------------------
   os.system('./case.submit')

#---------------------------------------------------------------------------------------------------
# Done!
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n') # Print the case name again