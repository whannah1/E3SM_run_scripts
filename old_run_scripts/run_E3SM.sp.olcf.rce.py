#!/usr/bin/env python
import os
import subprocess as sp
newcase,config,build,clean,submit,continue_run,debug = False,False,False,False,False,False,False

top_dir  = '/ccs/home/hannah6/E3SM/'
case_dir = top_dir+'Cases/'

src_dir  = top_dir+'E3SM_SRC3/'

# clean        = True
# debug        = True
# newcase      = True
# config       = True
build        = True
submit       = True
# continue_run = True
queue = 'batch'  # batch or debug on Summit 

ne,npg,num_nodes    = 4,0,1
# ne,npg,num_nodes    = 30,0,15
# num_nodes = 15       # ne4=>1, ne30=>15, ne120=>??
pcols     = 16
arch      = 'CPU'    # GPU / CPU
compset = 'F-EAMv1-RCEMIP'

res = 'ne'+str(ne) if npg==0 else  'ne'+str(ne)+'pg'+str(npg)

# cld = 'SP1'    # ZM / SP1 / SP2
# crm_nx,crm_ny,crm_dx = 64,1,1000
# cldc = cld+'_'+str(crm_nx)+'x'+str(crm_ny)+'_'+str(crm_dx)+'m' if 'SP' in cld else cld
# case = 'E3SM_RCE-TEST_'+cldc+'_'+res+'_'+compset+'_00'  # runs for pg2 paper


case = 'E3SM_RCE-TEST_'+res+'_'+compset+'_00'   # new RCE compset



stop_opt,stop_n,resub = 'ndays',1,0

# if compset=='FC5AV1C-L'   :stop_opt,stop_n,resub = 'ndays',32,0
# if compset=='FSP1V1'      :stop_opt,stop_n,resub = 'ndays',4,0
# if compset=='F-EAMv1-AQP1':stop_opt,stop_n,resub = 'ndays',1,1

# case = case+'_debug-on'
# case = case+'_checks-on'


# Impose wall limits for Summit
if num_nodes==  1: walltime =  '0:30'
if num_nodes>   1: walltime =  '2:00'
if num_nodes>= 46: walltime =  '6:00:00'
if num_nodes>= 92: walltime = '12:00:00'
if num_nodes>=922: walltime = '24:00:00'

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

# num_dyn = ne*ne*6
dtime = 5*60           # use 20 min for SP (default is 30 min for E3SM @ ne30)
ncpl  = 86400 / dtime
#---------------------------------------------------------------------------------------------------
# Create new case
#---------------------------------------------------------------------------------------------------
if newcase :
   grid = res+'_'+res
   cmd = src_dir+'cime/scripts/create_newcase -case '+case_dir+case
   cmd = cmd + ' -compset '+compset+' -res '+grid
   # if arch=='CPU' : cmd = cmd + ' -mach summit-cpu -compiler pgi    -pecount '+str(num_nodes*84)+'x1 '
   if arch=='CPU' : cmd = cmd + ' -mach summit -compiler pgi    -pecount '+str(num_nodes*84)+'x1 '
   if arch=='GPU' : cmd = cmd + ' -mach summit     -compiler pgigpu -pecount '+str(num_nodes*36)+'x1 '
   os.system(cmd)

   #-------------------------------------------------------
   # Change run directory to be next to bld directory
   #-------------------------------------------------------
   os.chdir(case_dir+case+'/')
   os.system('./xmlchange -file env_run.xml   RUNDIR=\'$CIME_OUTPUT_ROOT/$CASE/run\' ' )
#---------------------------------------------------------------------------------------------------
# Configure
#---------------------------------------------------------------------------------------------------
os.chdir(case_dir+case+'/')
if config : 

                   
   # if 'SP' in cld and compset not in ['FSP1V1','FSP2V1'] :
   #    # set options common to all SP setups
   #    nlev_crm = 58
   #    crm_dt   = 5
   #    cam_opt = ' -phys cam5 -use_SPCAM  -rad rrtmg -nlev 72 -microphys mg2 ' \
   #             +' -crm_nz '+str(nlev_crm) +' -crm_adv MPDATA '                \
   #             +' -crm_nx '+str(crm_nx)   +' -crm_ny '+str(crm_ny)            \
   #             +' -crm_dx '+str(crm_dx)   +' -crm_dt '+str(crm_dt)            \
   #             +' -crm_nx_rad 4 -crm_ny_rad 1 '
   #    # 1-moment microphysics
   #    if cld=='SP1': cam_opt = cam_opt + ' -SPCAM_microp_scheme sam1mom -chem none '
   #    # 2-moment microphysics
   #    if cld=='SP2': cam_opt = cam_opt + ' -SPCAM_microp_scheme m2005  '      \
   #                                     +' -chem linoz_mam4_resus_mom_soag '   \
   #                                     +' -rain_evap_to_coarse_aero '         \
   #                                     +' -bc_dep_to_snow_updates '

   #    cpp_opt = ' -DSP_DIR_NS -DSP_MCICA_RAD '
   #    if '-2WT'     in case : cpp_opt = cpp_opt + ' -DFVPG_TEND_MAP '
   #    if '-ALT-DYN' in case : cpp_opt = cpp_opt + ' -DFVPG_ALT_DYN_MAP '

   #    cam_opt = cam_opt+' -cppdefs \''+cpp_opt+'\' '
   #    if 'AQP' in compset : cam_opt = cam_opt+' -aquaplanet '

   #    os.system('./xmlchange -file env_build.xml -id CAM_CONFIG_OPTS  -val  \"'+cam_opt+'\"' )
   
   # Adjust rad columns for SP compsets
   if compset in ['FSP1V1','FSP2V1'] : 
      os.system('./xmlchange --append -file env_build.xml -id CAM_CONFIG_OPTS  -val  \" -crm_nx_rad 4 \" ' )
   
   # Change pcosl for GPU runs
   if arch=='GPU' : os.system('./xmlchange --append -file env_build.xml -id CAM_CONFIG_OPTS  -val  \" -pcols '+str(pcols)+' \" ' )


   ### disable threading for SP
   # if 'SP' in cld : os.system('./xmlchange -file env_mach_pes.xml -id NTHRDS_ATM -val 1 ')
   if ne==4 :
      ntask = 96
      os.system('./xmlchange -file env_mach_pes.xml -id NTASKS_OCN -val '+str(ntask)+' ')
      os.system('./xmlchange -file env_mach_pes.xml -id NTASKS_ICE -val '+str(ntask)+' ')
      os.system('./xmlchange -file env_mach_pes.xml -id NTASKS_LND -val '+str(ntask)+' ')
      os.system('./xmlchange -file env_mach_pes.xml -id NTASKS_GLC -val '+str(ntask)+' ')
      os.system('./xmlchange -file env_mach_pes.xml -id NTASKS_WAV -val '+str(ntask)+' ')
      os.system('./xmlchange -file env_mach_pes.xml -id NTASKS_ESP -val '+str(ntask)+' ')
      os.system('./xmlchange -file env_mach_pes.xml -id NTASKS_IAC -val '+str(ntask)+' ')

   if clean : os.system('./case.setup --clean')
   os.system('./case.setup --reset')

#---------------------------------------------------------------------------------------------------
# Build
#---------------------------------------------------------------------------------------------------
if build : 
   if 'debug-on' in case : os.system('./xmlchange -file env_build.xml -id DEBUG -val TRUE ')
   if debug : os.system('./xmlchange -file env_build.xml -id DEBUG -val TRUE ')
   if clean : os.system('./case.build --clean')
   os.system('./case.build')
#---------------------------------------------------------------------------------------------------
# Write the namelist options and submit the run
#---------------------------------------------------------------------------------------------------
if submit : 
   # Change inputdata from default due to permissions issue
   os.system('./xmlchange -file env_run.xml  DIN_LOC_ROOT=/gpfs/alpine/scratch/hannah6/cli115/inputdata ')
   
   #-------------------------------------------------------
   # First query some stuff about the case
   #-------------------------------------------------------
   (din_loc_root   , err) = sp.Popen('./xmlquery DIN_LOC_ROOT    -value', \
                                     stdout=sp.PIPE, shell=True, \
                                     universal_newlines=True).communicate()
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
   file.write(' mfilt     = 1,8 \n')     
   if npg>0 : file.write(" fincl1    = 'DYN_T','DYN_Q','DYN_U','DYN_OMEGA'")
   file.write(" fincl2    = 'PS','TS'")
   file.write(             ",'PRECT','TMQ'")
   file.write(             ",'LHFLX','SHFLX'")             # surface fluxes
   file.write(             ",'FSNT','FLNT'")               # Net TOM heating rates
   file.write(             ",'FLNS','FSNS'")               # Surface rad for total column heating
   file.write(             ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
   # file.write(             ",'LWCF','SWCF'")               # cloud radiative foricng
   # file.write(             ",'TAUX','TAUY'")               # surface stress
   # file.write(             ",'CLDLOW','CLDMED','CLDHGH','CLDTOT' ")
   # file.write(             ",'CLOUD','CLDLIQ','CLDICE'")   # 3D cloud fields
   file.write(             ",'T','Q','Z3' ")               # 3D thermodynamic budget components
   file.write(             ",'U','V','OMEGA'")             # 3D velocity components
   file.write(             ",'QRL','QRS'")                 # 3D radiative heating profiles
   # file.write(             ",'DYN_T','DYN_Q','DYN_OMEGA'")
   # if 'SP' in cld :
   #    file.write(         ",'SPDT','SPDQ'")               # CRM heating/moistening tendencies
   #    file.write(         ",'SPTLS','SPQTLS' ")           # CRM large-scale forcing
      # file.write(         ",'SPQPEVP','SPMC'")            # CRM rain evap and total mass flux
      # file.write(         ",'SPMCUP','SPMCDN'")           # CRM saturated mass fluxes
      # file.write(         ",'SPMCUUP','SPMCUDN'")         # CRM unsaturated mass fluxes
      # file.write(         ",'SPTKE'")
      # if any(x in cam_config_opts for x in ["SP_ESMT","SP_USE_ESMT","SPMOMTRANS"]) : 
      #    file.write(",'ZMMTU','ZMMTV','uten_Cu','vten_Cu' ")
      # if "SP_USE_ESMT" in cam_config_opts : file.write(",'U_ESMT','V_ESMT'")
      # if "SPMOMTRANS"  in cam_config_opts : 
   # if 'ESMT' in case:
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
   # file.write(' srf_flux_avg = 1 \n')              # Sfc flux smoothing (for SP stability)
   # file.write(' dyn_npes = '+str(num_dyn)+' \n')   # limit dynamics tasks

   # if 'HOPG' in case : 
   #    file.write(' se_fv_phys_remap_alg = 1 \n')
   # else:
   #    file.write(' se_fv_phys_remap_alg = 0 \n')

   if 'checks-on' in case : file.write(' state_debug_checks = .true. \n')
   
   file.close()

   #------------------------------
   # new land initial condition file (not in inputdata yet) 
   #------------------------------
   # nfile = 'user_nl_clm'
   # file = open(nfile,'w') 
   # if res=='ne30' : file.write(' finidat = \'/gpfs/alpine/scratch/hannah6/cli115/init_files/clmi.ICLM45BC.ne30_ne30.d0241119c.clm2.r.nc\' \n')
   # file.close()
   
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
