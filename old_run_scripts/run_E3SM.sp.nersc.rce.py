#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
import os
import subprocess as sp
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True
queue = 'debug'  # regular / debug

ne,npg = 30,0 
compset = 'F-EAMv1-RCEMIP'

if queue=='debug' : 
   stop_opt,stop_n,resub,walltime = 'ndays',5,0,'0:30:00'
   # stop_opt,stop_n,resub,walltime = 'nstep',60,0,'0:30:00'
else:
   stop_opt,stop_n,resub,walltime = 'ndays',73*2,2,'4:00:00'

res = 'ne'+str(ne) if npg==0 else  'ne'+str(ne)+'pg'+str(npg)

# case = 'E3SM_RCE-TEST_'+res+'_'+compset+'_00'   # new RCE compset
case = 'E3SM_RCE-TEST_'+res+'_'+compset+'_01'   # new RCE compset w/ new IC file

# case = case+'_debug-on'
# case = case+'_checks-on'

top_dir  = '/global/homes/w/whannah/E3SM/'
case_dir = top_dir+'Cases/'

# src_dir  = top_dir+'E3SM_SRC1/'
# src_dir  = top_dir+'E3SM_SRC2/'
src_dir  = top_dir+'E3SM_SRC3/'

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

dtime = 30*60           # use 20 min for SP (default is 30 min for E3SM @ ne30)
if ne==120: dtime = 5*60
ncpl  = 86400 / dtime

num_dyn = ne*ne*6
# Enforce max node limit on debug queue
if queue=='debug' and num_dyn>(64*32) : num_dyn = 64*32

cld = 'ZM'
if compset == 'FSP1V1' : cmd = 'SP1'
if compset == 'FSP2V1' : cmd = 'SP2'
#---------------------------------------------------------------------------------------------------
# Create new case
#---------------------------------------------------------------------------------------------------
if newcase :
   grid = res+'_'+res
   cmd = src_dir+'cime/scripts/create_newcase -case '+case_dir+case
   cmd = cmd + ' -compset '+compset+' -res '+grid#+' --pecount '+str(num_dyn)+'x1'
   if '_gnu_' in case : cmd = cmd + ' --compiler gnu '
   os.system(cmd)
#---------------------------------------------------------------------------------------------------
# Configure
#---------------------------------------------------------------------------------------------------
os.chdir(case_dir+case+'/')
if config : 

   if compset in ['FSP1V1','FSP2V1'] : 
      os.system('./xmlchange --append -file env_build.xml -id CAM_CONFIG_OPTS  -val  \" -crm_nx_rad 4 \" ' )

   # if 'ESMT' in case :
   #    cpp_opt = ' -DSP_DIR_NS -DSP_MCICA_RAD '
   #    cpp_opt = cpp_opt+' -DSP_ESMT -DSP_USE_ESMT '
   #    os.system('./xmlchange --append -file env_build.xml -id CAM_CONFIG_OPTS  -val  \" -cppdefs \''+cpp_opt+'\'  \" ' )

   #-------------------------------------------------------
   # Set tasks and threads - disable threading for SP
   #-------------------------------------------------------
   os.system('./xmlchange -file env_mach_pes.xml -id NTASKS_ATM -val '+str(num_dyn)+' ')
   # if compset in ['FSP1V1','FSP2V1'] : os.system('./xmlchange -file env_mach_pes.xml -id NTHRDS_ATM -val 1 ')

   os.system('./xmlchange -file env_mach_pes.xml -id NTASKS_CPL -val 1 ')
   os.system('./xmlchange -file env_mach_pes.xml -id NTASKS_OCN -val 1 ')
   os.system('./xmlchange -file env_mach_pes.xml -id NTASKS_ICE -val 1 ')
   os.system('./xmlchange -file env_mach_pes.xml -id NTASKS_LND -val 1 ')
   os.system('./xmlchange -file env_mach_pes.xml -id NTASKS_ROF -val 1 ')
   os.system('./xmlchange -file env_mach_pes.xml -id NTASKS_WAV -val 1 ')
   os.system('./xmlchange -file env_mach_pes.xml -id NTASKS_GLC -val 1 ')
   
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
   file.write(' nhtfrq    = 0,-3 \n mfilt     = 1,8 \n')   # 3-hour output / 1 file per day
   # file.write(' nhtfrq    = 0,1 \n mfilt     = 1,1000 \n')      # timestep output for debugging

   file.write(" fincl2    = 'PS','TS'")
   file.write(             ",'PRECT','TMQ'")
   file.write(             ",'LHFLX','SHFLX'")             # surface fluxes
   file.write(             ",'FSNT','FLNT'")               # Net TOM heating rates
   file.write(             ",'FLNS','FSNS'")               # Surface rad for total column heating
   file.write(             ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
   file.write(             ",'CLDLOW','CLDMED','CLDHGH','CLDTOT' ")
   # file.write(             ",'LWCF','SWCF'")               # cloud radiative foricng
   # file.write(             ",'TAUX','TAUY'")               # surface stress
   file.write(             ",'T','Q','Z3' ")               # 3D thermodynamic budget components
   file.write(             ",'U','V','OMEGA'")             # 3D velocity components
   # file.write(             ",'CLOUD','CLDLIQ','CLDICE'")   # 3D cloud fields
   file.write(             ",'QRL','QRS'")                 # 3D radiative heating profiles
   # file.write(             ",'COSZRS','SOLIN','SW_ALBEDO_DIR','SW_ALBEDO_DIF'")
   # if npg>0 : 
   #    file.write(          ",'T','Q','U' ")
   #    file.write(          ",'DYN_T','DYN_Q','DYN_U'")
   # if 'SP' in cld :
      # file.write(         ",'SPDT','SPDQ'")               # CRM heating/moistening tendencies
      # file.write(         ",'SPTLS','SPQTLS' ")           # CRM large-scale forcing
      # file.write(         ",'SPQPEVP','SPMC'")            # CRM rain evap and total mass flux
      # file.write(         ",'SPMCUP','SPMCDN'")           # CRM saturated mass fluxes
      # file.write(         ",'SPMCUUP','SPMCUDN'")         # CRM unsaturated mass fluxes
      # file.write(         ",'SPTKE'")
      # if any(x in cam_config_opts for x in ["SP_ESMT","SP_USE_ESMT","SPMOMTRANS"]) : 
      #    file.write(",'ZMMTU','ZMMTV','uten_Cu','vten_Cu' ")
      # if "SP_USE_ESMT" in cam_config_opts : file.write(",'U_ESMT','V_ESMT'")
      # if "SPMOMTRANS"  in cam_config_opts : 
   # if 'ESMT' in case:
   #    file.write(         ",'SPDT','SPDQ'")
   #    file.write(",'ZMMTU','ZMMTV','uten_Cu','vten_Cu' ")
   #    file.write(",'U_ESMT','V_ESMT'")
   #    file.write(",'UCONVMOM','VCONVMOM'")
   file.write('\n')

   #------------------------------
   # Prescribed aerosol settings
   #------------------------------
   if 'chem none' in cam_config_opts and compset not in ['FSP1V1','FSP2V1'] :
      prescribed_aero_path = '/atm/cam/chem/trop_mam/aero'
      prescribed_aero_file = 'mam4_0.9x1.2_L72_2000clim_c170323.nc'
      file.write(' use_hetfrz_classnuc = .false. \n')
      file.write(' aerodep_flx_type = \'CYCLICAL\' \n')
      file.write(' aerodep_flx_datapath = \''+din_loc_root+prescribed_aero_path+'\' \n')
      file.write(' aerodep_flx_file = \''+prescribed_aero_file+'\' \n')
      file.write(' aerodep_flx_cycle_yr = 01 \n')
      file.write(' prescribed_aero_type = \'CYCLICAL\' \n')
      file.write(' prescribed_aero_datapath=\''+din_loc_root+prescribed_aero_path+'\' \n')
      file.write(' prescribed_aero_file = \''+prescribed_aero_file+'\' \n')
      file.write(' prescribed_aero_cycle_yr = 01 \n')
   #------------------------------
   # Other namelist stuff
   #------------------------------
   # if 'F-EAMv1-RCEMIP' in compset : 
   #    file.write(' prescribed_ozone_type     = \'CYCLICAL\' \n')
   #    file.write(' prescribed_ozone_cycle_yr = 2000 \n')
   #    file.write(' prescribed_ozone_name     = \'O3\' \n')
   #    file.write(' prescribed_ozone_datapath = \'/global/cscratch1/sd/whannah/acme_scratch/init_files/\' \n')
   #    file.write(' prescribed_ozone_file     = \'RCEMIP_ozone.v1.nc\' \n')
   
   # file.write(' srf_flux_avg = 1 \n')              # Sfc flux smoothing (for SP stability)
   file.write(' dyn_npes = '+str(num_dyn)+' \n')   # limit dynamics tasks


   # if ne==30 : file.write(' ncdata = \'/global/cscratch1/sd/whannah/acme_scratch/init_files/cami_ne30np4_L72_RCEMIP.nc\' \n')   
   # if ne==4 : file.write(' ncdata = \'/global/cscratch1/sd/whannah/acme_scratch/init_files/cami_ne4np4_L72_RCEMIP.nc\' \n')   

   # se_nsplit,rsplit = 20,3
   # file.write(" rsplit    = "+str(   rsplit)+" \n")
   # file.write(" se_nsplit = "+str(se_nsplit)+" \n")

   if 'checks-on' in case : file.write(' state_debug_checks = .true. \n')

   file.write(" inithist = \'MONTHLY\' \n")
   
   file.close()
   #-------------------------------------------------------
   # Set some run-time stuff
   #-------------------------------------------------------
   os.system('./xmlchange -file env_run.xml      ATM_NCPL='   +str(ncpl)   )
   os.system('./xmlchange -file env_run.xml      STOP_OPTION='+stop_opt    )
   os.system('./xmlchange -file env_run.xml      STOP_N='     +str(stop_n) )
   os.system('./xmlchange -file env_run.xml      RESUBMIT='   +str(resub)  )
   os.system('./xmlchange -file env_workflow.xml JOB_QUEUE='           +queue )
   os.system('./xmlchange -file env_batch.xml    JOB_QUEUE='           +queue )
   os.system('./xmlchange -file env_batch.xml    USER_REQUESTED_QUEUE='+queue )
   os.system('./xmlchange -file env_workflow.xml JOB_WALLCLOCK_TIME='     +walltime )
   os.system('./xmlchange -file env_batch.xml    JOB_WALLCLOCK_TIME='     +walltime )
   os.system('./xmlchange -file env_batch.xml    USER_REQUESTED_WALLTIME='+walltime )

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
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
