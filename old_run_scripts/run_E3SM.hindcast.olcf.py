#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
import os
import subprocess as sp
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'CLI115'

top_dir  = '/ccs/home/hannah6/E3SM/'
case_dir = top_dir+'Cases/'

src_dir  = top_dir+'E3SM_SRC3/'

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True
queue = 'batch'  # batch or debug on Summit 

ne,npg    = 30,2
num_nodes = 15        # ne4=>1, ne30=>15, ne120=>??
arch      = 'CPU'    # GPU / CPU
# compset   = 'F2010SC5-CMIP6'   # FC5AV1C-L / FC5AV1C-H01A / F-MMF1 / F2010S-MMF1 / F2010SC5-CMIP6
arch,compset = 'CPU','FC5AV1C-L'
# arch,compset = 'CPU','F2010SC5-CMIP6'
# arch,compset = 'GPU','F2010S-MMF1'

stop_opt,stop_n,resub = 'ndays',10,0
   
res = 'ne'+str(ne) if npg==0 else  'ne'+str(ne)+'pg'+str(npg)
grid = f'{res}_{res}'
# grid = f'{res}_r05_oECv3'

iyr,imn,idy = 2016,8,1
init_date = f'{iyr}-{imn:02d}-{idy:02d}'
init_file_dir = '/gpfs/alpine/scratch/hannah6/cli115/init_files/'
init_file_atm = f'HICCUP.atm_era5.{init_date}.ne30np4.L72.nc'
init_file_sst = f'HICCUP.sst_noaa.{init_date}.nc'

case = f'E3SM_HINDCAST-TEST_{init_date}_{arch}_{grid}_{compset}_00'   # control

# case = case.replace(f'{compset}',f'{compset}_ESMT')   # enable ESMT
# case = case.replace(f'{compset}',f'{compset}_FLUX-BYPASS')   # enable flux bypss

# case = case+'_debug-on'
# case = case+'_checks-on'


# Impose wall limits for Summit
if num_nodes>=  1: walltime =  '2:00'
if num_nodes>= 46: walltime =  '6:00'
if num_nodes>= 92: walltime = '12:00'
if num_nodes>=922: walltime = '24:00'

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

# num_dyn = ne*ne*6
# dtime = 20*60
# if ne==120: dtime = 5*60
# ncpl  = 86400 / dtime

# Enforce max node limit on debug queue
# if queue=='debug' and num_dyn>(64*32) : num_dyn = 64*32
# if num_dyn==0 : num_dyn = 4000

#---------------------------------------------------------------------------------------------------
# Create new case
#---------------------------------------------------------------------------------------------------
if newcase :
   cmd = src_dir+'cime/scripts/create_newcase -case '+case_dir+case
   cmd += ' -compset '+compset
   cmd += ' -res '+grid
   if arch=='CPU' : cmd = cmd + ' -mach summit-cpu -compiler pgi    -pecount '+str(num_nodes*64)+'x1 '
   if arch=='GPU' : cmd = cmd + ' -mach summit     -compiler pgigpu -pecount '+str(num_nodes*18)+'x1 '   
   os.system(cmd)
#---------------------------------------------------------------------------------------------------
# Configure
#---------------------------------------------------------------------------------------------------
os.chdir(case_dir+case+'/')
if config : 

   pcols = 16
   if arch=='GPU' : pcols = 32
   if arch=='CPU' and npg>0 : pcols = npg*npg*2
   os.system(f'./xmlchange --append -file env_build.xml -id CAM_CONFIG_OPTS -val \" -pcols {pcols} \"')

   if compset in ['FSP1V1','FSP2V1','F-MMF1'] : 
      os.system('./xmlchange --append -file env_build.xml -id CAM_CONFIG_OPTS  -val  \" -crm_nx_rad 8 \" ' )

   cam_config_cmd = f'./xmlchange --append -file env_build.xml -id CAM_CONFIG_OPTS'
   if '_FLUX-BYPASS_' in case: os.system(cam_config_cmd + f' -val \" -cppdefs \'-DMMF_DIR_NS -DMMF_FLUX_BYPASS\'  \" ')
   if '_ESMT_'        in case: os.system(cam_config_cmd + f' -val \" -cppdefs \'-DMMF_DIR_NS -DMMF_ESMT\'  \" ')
   #-------------------------------------------------------
   # Set tasks and threads - disable threading for SP
   #-------------------------------------------------------
   # if ne!=120 and num_dyn!=0 : 
   #    os.system('./xmlchange -file env_mach_pes.xml -id NTASKS_ATM -val '+str(num_dyn)+' ')

   if compset in ['FSP1V1','FSP2V1'] : os.system('./xmlchange -file env_mach_pes.xml -id NTHRDS_ATM -val 1 ')
   
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
   file.write(' mfilt     = 1,8 \n')
   # file.write(' nhtfrq    = 0,1 \n')
   # file.write(' mfilt     = 1,500 \n')
   file.write(" fincl1    = 'TSMX:X','TSMN:M','TREFHT','QREFHT'")
   # file.write(             ",'DYN_T','DYN_Q','DYN_U','DYN_OMEGA','DYN_PS'")
   # if 'use_SPCAM' in cam_config_opts :
   #    file.write(          ",'SPQPEVP','SPMC','SPMCUP','SPMCDN','SPMCUUP','SPMCUDN'")
   file.write('\n')
   file.write(" fincl2    = 'PS','TS'")
   file.write(             ",'PRECT','TMQ'")
   file.write(             ",'LHFLX','SHFLX'")             # surface fluxes
   file.write(             ",'FSNT','FLNT'")               # Net TOM heating rates
   file.write(             ",'FLNS','FSNS'")               # Surface rad for total column heating
   # file.write(             ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
   # file.write(             ",'LWCF','SWCF'")               # cloud radiative foricng
   file.write(             ",'TGCLDLWP','TGCLDIWP'")    
   # file.write(             ",'CLDLOW','CLDMED','CLDHGH','CLDTOT' ")
   # file.write(             ",'TAUX','TAUY'")               # surface stress
   file.write(             ",'UBOT','VBOT'")
   file.write(             ",'TBOT','QBOT'")
   file.write(             ",'OMEGA850','OMEGA500'")
   file.write(             "'Z100','Z500','Z700'")
   file.write(             ",'T500','T850','Q850'")
   file.write(             ",'U200','U850'")
   # file.write(             ",'T','Q','Z3' ")               # 3D thermodynamic budget components
   # file.write(             ",'U','V','OMEGA'")             # 3D velocity components
   # file.write(             ",'CLOUD','CLDLIQ','CLDICE'")   # 3D cloud fields
   # file.write(             ",'QRL','QRS'")                 # 3D radiative heating profiles
   # if 'use_SPCAM' in cam_config_opts or 'use_MMF' in cam_config_opts :
   #    file.write(         ",'CRM_PREC'")
   #    file.write(         ",'CRM_QRAD'")
   #    file.write(         ",'SPDT','SPDQ'")               # CRM heating/moistening tendencies
   #    file.write(         ",'SPTLS','SPQTLS' ")           # CRM large-scale forcing
   #    file.write(         ",'SPQPEVP','SPMC'")            # CRM rain evap and total mass flux
   #    file.write(         ",'SPMCUP','SPMCDN'")           # CRM saturated mass fluxes
   #    file.write(         ",'SPMCUUP','SPMCUDN'")         # CRM unsaturated mass fluxes
   #    file.write(         ",'SPTKE','SPTKES'")
   #    file.write(         ",'CRM_T','CRM_U'")
   #    file.write(         ",'SPMC','MU_CRM'")
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
   # Other namelist stuff
   #------------------------------
   # if compset=='F-EAMv1-RCEMIP' : 
   # if 'F-EAMv1-RCEMIP' in compset : 
   #    file.write(' prescribed_ozone_type     = \'CYCLICAL\' \n')
   #    file.write(' prescribed_ozone_cycle_yr = 2000 \n')
   #    file.write(' prescribed_ozone_name     = \'O3\' \n')
   #    file.write(' prescribed_ozone_datapath = \'/global/cscratch1/sd/whannah/acme_scratch/init_files/\' \n')
   #    file.write(' prescribed_ozone_file     = \'RCEMIP_ozone.v1.nc\' \n')
   
   # file.write(' srf_flux_avg = 1 \n')              # Sfc flux smoothing (for SP stability)
   # file.write(' dyn_npes = '+str(num_dyn)+' \n')   # limit dynamics tasks

   # se_nsplit,rsplit = 20,3
   # file.write(" rsplit    = "+str(   rsplit)+" \n")
   # file.write(" se_nsplit = "+str(se_nsplit)+" \n")

   file.write(' se_fv_phys_remap_alg = 1 \n')

   # file.write(" inithist = \'MONTHLY\' \n")
   file.write(' inithist = \'ENDOFRUN\' \n')

   if 'checks-on' in case : file.write(' state_debug_checks = .true. \n')

   file.close()


   if ne==120 and npg==2 : os.system('./xmlchange -file env_run.xml      EPS_AGRID=1e-11' )

   # if ne==120 and npg==2 : 
   #    file = open('user_nl_cpl','w') 
   #    file.write(' eps_agrid = 1e-11 \n')
   #    file.close()
   if ne==120 and npg==2 : 
      nfile = 'user_nl_clm'
      file = open(nfile,'w')
      file.write(' finidat = \'/global/cscratch1/sd/whannah/acme_scratch/cori-knl/E3SM_PG-LAND-SPINUP_ne120pg2_FC5AV1C-H01A_00/run/E3SM_PG-LAND-SPINUP_ne120pg2_FC5AV1C-H01A_00.clm2.r.0004-02-25-00000.nc\' \n')
      file.close()
   #-------------------------------------------------------
   # Special stuff for hindcast mode
   #-------------------------------------------------------
   os.system(f'./xmlchange -file env_run.xml      RUN_STARTDATE={init_date}')
   os.system(f'./xmlchange -file env_run.xml      SSTICE_DATA_FILENAME={init_file_dir}{init_file_sst}')
   os.system(f'./xmlchange -file env_run.xml      SSTICE_YEAR_ALIGN={iyr}')
   os.system(f'./xmlchange -file env_run.xml      SSTICE_YEAR_START={iyr}')
   os.system(f'./xmlchange -file env_run.xml      SSTICE_YEAR_END={iyr+1}')
   # os.system('./xmlchange -file env_build.xml    CALENDAR=GREGORIAN)


   file = open(nfile,'a') 
   file.write(f' ncdata = \'{init_file_dir}{init_file_atm}\'\n')
   file.close()
   
   #-------------------------------------------------------
   # Set some run-time stuff
   #-------------------------------------------------------
   # os.system('./xmlchange -file env_run.xml      ATM_NCPL='   +str(ncpl)   )
   os.system('./xmlchange -file env_run.xml      STOP_OPTION='+stop_opt    )
   os.system('./xmlchange -file env_run.xml      STOP_N='     +str(stop_n) )
   os.system('./xmlchange -file env_run.xml      RESUBMIT='   +str(resub)  )

   def xml_check_and_set(file_name,var_name,value):
      if var_name in open(file_name).read(): 
         os.system('./xmlchange -file '+file_name+' '+var_name+'='+str(value) )
   
   xml_check_and_set('env_workflow.xml','JOB_QUEUE',           queue)
   xml_check_and_set('env_batch.xml',   'USER_REQUESTED_QUEUE',queue)
   xml_check_and_set('env_workflow.xml','JOB_WALLCLOCK_TIME',     walltime)
   xml_check_and_set('env_batch.xml',   'USER_REQUESTED_WALLTIME',walltime)
   
   # os.system('./xmlchange -file env_workflow.xml JOB_QUEUE='           +queue )
   # os.system('./xmlchange -file env_batch.xml    JOB_QUEUE='           +queue )
   # os.system('./xmlchange -file env_batch.xml    USER_REQUESTED_QUEUE='+queue )
   # os.system('./xmlchange -file env_workflow.xml JOB_WALLCLOCK_TIME='     +walltime )
   # os.system('./xmlchange -file env_batch.xml    JOB_WALLCLOCK_TIME='     +walltime )
   # os.system('./xmlchange -file env_batch.xml    USER_REQUESTED_WALLTIME='+walltime )

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
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
