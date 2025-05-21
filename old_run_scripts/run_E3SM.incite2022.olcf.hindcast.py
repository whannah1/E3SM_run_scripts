#!/usr/bin/env python
# script for running E3SM-MMF simulations using the 2020 INICTE allocation (CLI115)
# Branch for this campaign: https://github.com/E3SM-Project/E3SM/tree/whannah/incite-2020
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
import os, numpy as np, subprocess as sp, datetime
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'cli115'
case_dir = os.getenv('HOME')+'/E3SM/Cases/'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC3/' # branch => whannah/mmf/2022-low-cloud-exp

### flags to control config/build/submit sections
# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
continue_run = True

queue = 'batch' # batch / debug

debug_mode = False

### run duration
queue,stop_opt,stop_n,resub,walltime = 'debug','ndays',4,0,'0:15'
# queue,stop_opt,stop_n,resub,walltime = 'batch','ndays',1,0,'0:30'
# queue,stop_opt,stop_n,resub,walltime = 'batch','ndays',32,1,'2:00'

### default settings
compset       = 'F2010-MMF1'
arch          = 'GNUGPU'
num_nodes     = 128
ne,npg        = 30,2
grid          = f'ne{ne}pg{npg}_oECv3'
rad_nx        = 4
crm_dt,crm_dx = 10,2000
gcm_nz,crm_nz = 60,50
crm_nx,crm_ny = 64,1   # note momentum FB enabled when crm_ny>1
use_vt,use_mf = True,True # CRM variance transport and momentum feedback

#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# simple setup for testing output
# stop_opt,stop_n,resub = 'ndays',1,0
# crm_ny = 4
# walltime = '2:00'
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

iyr,imn,idy = 2008,10,1
init_date = f'{iyr}-{imn:02d}-{idy:02d}'

#---------------------------------------------------------------------------------------------------
# specific case names and settings
#---------------------------------------------------------------------------------------------------
# gcm_nz,crm_nz,crm_nx,crm_ny,crm_dx,crm_dt,crm_hv,crm_sed = 125,115,128,1,200,5,False,False
# gcm_nz,crm_nz,crm_nx,crm_ny,crm_dx,crm_dt,crm_hv,crm_sed = 125,115,128,1,200,5,True, False
# gcm_nz,crm_nz,crm_nx,crm_ny,crm_dx,crm_dt,crm_hv,crm_sed = 125,115,128,1,200,5,True, True
# gcm_nz,crm_nz,crm_nx,crm_ny,crm_dx,crm_dt,crm_hv,crm_sed = 125,115,128,1,200,5,False, True

### new set with default coarse CRM
# num_nodes,crm_hv,crm_sed = 32,False,False
num_nodes,crm_hv,crm_sed = 32,False, True

# if crm_sed: exit('ERROR: CRM sedimention mod has not been implented yet!')
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

### specify case name based on configuration
case_list = ['E3SM','INCITE2022-HC-00',grid,compset,init_date]
case_list.append(f'L_{gcm_nz}_{crm_nz}')
case_list.append(f'NXY_{crm_nx}x{crm_ny}')
if crm_hv : case_list.append(f'HV') 
if crm_sed: case_list.append(f'SED')
if debug_mode: case_list.append('debug')

case='.'.join(case_list)

#---------------------------------------------------------------------------------------------------
# specify initial condition files

# init_file_dir = '/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/init_files'
init_file_dir = '/gpfs/alpine/scratch/hannah6/cli115/HICCUP/data'
init_file_sst = f'HICCUP.sst_noaa.{init_date}.c20220610.nc'
params = [p.split('_') for p in case.split('.')]
for p in params:
   if p[0]=='L': init_file_atm = f'HICCUP.atm_era5.{init_date}.ne{ne}np4.L{p[1]}.c20220610.nc'

land_init_path = '/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/init_files'
land_init_file = 'ELM_spinup.ICRUELM.ne30pg2_oECv3.20-yr.2010-01-01.elm.r.2010-01-01-00000.nc'
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

# dtime = 20*60   # GCM physics time step
if 'dtime' in locals(): ncpl  = 86400 / dtime

num_dyn = ne*ne*6

max_task_per_node = 42
if 'CPU' in arch : max_mpi_per_node,atm_nthrds  = 42,1
if 'GPU' in arch : max_mpi_per_node,atm_nthrds  = 6,7
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
   run_cmd('./xmlchange -file env_run.xml RUNDIR=\'/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/$CASE/run\' ' )

   run_cmd(f'./xmlchange -file env_mach_pes.xml -id MAX_TASKS_PER_NODE    -val {max_task_per_node} ')
   run_cmd(f'./xmlchange -file env_mach_pes.xml -id MAX_MPITASKS_PER_NODE -val {max_mpi_per_node} ')
else:
   os.chdir(case_dir+case+'/')
#---------------------------------------------------------------------------------------------------
if config : 
   #-------------------------------------------------------
   if 'init_file_atm' in locals():
      file = open('user_nl_eam','w')
      file.write(f' ncdata = \'{init_file_dir}/{init_file_atm}\'\n')
      file.close()
   #-------------------------------------------------------
   # Set some non-default stuff for all MMF experiments here
   run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -nlev {gcm_nz} \" ')
   if 'MMF' in compset:
      rad_ny = rad_nx if crm_ny>1 else 1
      run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_dt {crm_dt} \" ')
      run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_dx {crm_dx}  \" ')
      run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx {crm_nx} -crm_ny {crm_ny} \" ')
      run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx_rad {rad_nx} -crm_ny_rad {rad_ny} \" ')
      if use_vt: run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -use_MMF_VT \" ')
      run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nz {crm_nz} \" ')
   #-------------------------------------------------------
   # Add special CPP flags for MMF options
   cpp_opt = ''
   if debug_mode: cpp_opt += ' -DYAKL_DEBUG'

   if 'MMF' in compset: 
      if  crm_ny==1 and use_mf: cpp_opt += ' -DMMF_ESMT -DMMF_USE_ESMT'
      if  crm_ny>1  and use_mf: cpp_opt += ' -DMMF_MOMENTUM_FEEDBACK'

   if crm_hv : cpp_opt += ' -DMMF_HYPERVISCOSITY'
   if crm_sed: cpp_opt += ' -DMMF_SEDIMENTATION'

   if cpp_opt != '' :
      cmd  = f'./xmlchange --append -file env_build.xml -id CAM_CONFIG_OPTS'
      cmd += f' -val \" -cppdefs \' {cpp_opt} \'  \" '
      run_cmd(cmd)
   #-------------------------------------------------------
   # Set tasks for all components
   if num_nodes>800:
      cmd = './xmlchange -file env_mach_pes.xml '
      alt_ntask = 600; cmd += f'NTASKS_OCN={alt_ntask},NTASKS_ICE={alt_ntask}'
      alt_ntask = 675; cmd += f',NTASKS_LND={alt_ntask},NTASKS_CPL={alt_ntask}'
      alt_ntask = max_mpi_per_node
      cmd += f',NTASKS_ROF={alt_ntask},NTASKS_WAV={alt_ntask},NTASKS_GLC={alt_ntask}'
      cmd += f',NTASKS_ESP=1,NTASKS_IAC=1'
      run_cmd(cmd)
   #-------------------------------------------------------
   # 64_data format is needed for large output (i.e. high-res grids or CRM data)
   run_cmd('./xmlchange PIO_NETCDF_FORMAT=\"64bit_data\" ')
   #-------------------------------------------------------
   # Run case setup
   if clean : run_cmd('./case.setup --clean')
   run_cmd('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
# Build
#---------------------------------------------------------------------------------------------------
if build : 
   if debug_mode: run_cmd('./xmlchange -file env_build.xml -id DEBUG -val TRUE ')
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
# Write the namelist options and submit the run
#---------------------------------------------------------------------------------------------------
if submit : 
   # Change inputdata from default due to permissions issue
   # init_scratch = '/gpfs/alpine/cli115/scratch/hannah6/inputdata'
   init_scratch = '/gpfs/alpine/cli115/world-shared/e3sm/inputdata'
   run_cmd(f'./xmlchange DIN_LOC_ROOT={init_scratch} ')
   #-------------------------------------------------------
   # First query some stuff about the case
   #-------------------------------------------------------
   (din_loc_root, err) = sp.Popen('./xmlquery DIN_LOC_ROOT    -value', \
                                     stdout=sp.PIPE, shell=True, universal_newlines=True).communicate()
   (config_opts, err) = sp.Popen('./xmlquery CAM_CONFIG_OPTS -value', \
                                     stdout=sp.PIPE, shell=True, universal_newlines=True).communicate()
   config_opts = ' '.join(config_opts.split())   # remove extra spaces to simplify string query
   ntasks_atm = None
   (ntasks_atm     , err) = sp.Popen('./xmlquery NTASKS_ATM    -value', \
                                     stdout=sp.PIPE, shell=True, universal_newlines=True).communicate()
   ntasks_atm = float(ntasks_atm)
   #-------------------------------------------------------
   # Namelist options
   #-------------------------------------------------------
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   #------------------------------
   # Specify history output frequency and variables
   #------------------------------   
   file.write(' nhtfrq    = 0,-1 \n') 
   file.write(' mfilt     = 1, 24 \n') # 1-day files
   file.write(" fincl1 = 'Z3'") # this is for easier use of height axis on profile plots   
   file.write(         ",'CLOUD','CLDLIQ','CLDICE'")
   file.write('\n')
   file.write(" fincl2    = 'PS','PSL','TS'")
   file.write(             ",'PRECT','TMQ'")
   file.write(             ",'LHFLX','SHFLX'")             # surface fluxes
   file.write(             ",'FSNT','FLNT'")               # Net TOM heating rates
   file.write(             ",'FLNS','FSNS'")               # Surface rad for total column heating
   file.write(             ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
   file.write(             ",'FLUT','FSNTOA'")
   file.write(             ",'LWCF','SWCF'")               # cloud radiative foricng
   file.write(             ",'TGCLDLWP','TGCLDIWP'")       # liq/ice water path
   file.write(             ",'TAUX','TAUY'")               # surface stress
   
   file.write(             ",'TUQ','TVQ'")                         # vapor transport
   file.write(             ",'TBOT:I','QBOT:I','UBOT:I','VBOT:I'") # lowest model leve
   file.write(             ",'T900:I','Q900:I','U900:I','V900:I'") # 900mb data
   file.write(             ",'T850:I','Q850:I','U850:I','V850:I'") # 850mb data
   file.write(             ",'Z300:I','Z500:I'")
   file.write(             ",'OMEGA850:I','OMEGA500:I'")

   # file.write(             ",'T','Q','Z3'")                # 3D thermodynamic budget components
   # file.write(             ",'U','V','OMEGA'")             # 3D velocity components
   # file.write(             ",'CLOUD','CLDLIQ','CLDICE'")   # 3D cloud fields
   # file.write(             ",'QRL','QRS'")                 # 3D radiative heating 
   # file.write(             ",'QRLC','QRSC'")               # 3D clearsky radiative heating 

   # file.write(             ",'PTTEND','PTEQ'")             # 3D physics tendencies
   # file.write(             ",'PTECLDLIQ','PTECLDICE'")     # 3D physics tendencies
   # file.write(             ",'TOT_DU','TOT_DV'")          # total momentum tendencies
   # file.write(             ",'DYN_DU','DYN_DV'")          # Dynamics momentum tendencies
   # file.write(             ",'GWD_DU','GWD_DV'")          # 3D gravity wave tendencies
   # file.write(             ",'DUV','DVV'")                # 3D PBL tendencies
   # if 'use_MMF' in config_opts :
      # file.write(          ",'MMF_TK','MMF_TKE','MMF_TKES','MMF_TKEW'")
      # file.write(          ",'MMF_PFLX','MMF_QTFLX'")
      # file.write(          ",'MMF_TVFLUX'")  # output is all zeroes!
      # if 'MMF_MOMENTUM_FEEDBACK' in config_opts  :
         # file.write(       ",'MMF_UFLX','MMF_VFLX'")
         # file.write(       ",'MMF_DU','MMF_DV'")
   file.write('\n')
   #------------------------------
   # Other namelist stuff
   #------------------------------
   # file.write(f' crm_accel_factor = 3 \n')         # CRM acceleration factor (default is 2)

   if num_dyn<ntasks_atm: file.write(' dyn_npes = '+str(num_dyn)+' \n')   # limit dynamics tasks

   file.write(" inithist = \'NONE\' \n") # ENDOFRUN / NONE

   # if 'L_250' in case: 
   #    file.write(' se_tstep = 120 \n')
   #    file.write(' dt_remap_factor = 2 \n')
   #    file.write(' dt_tracer_factor = 10 \n')
   #    file.write(' hypervis_subcycle_q = 10 \n')

   # if 'init_file_atm' in locals():
   #    file.write(f' ncdata = \'{init_file_dir}/{init_file_atm}\'\n')

   file.close()
   #-------------------------------------------------------
   # ELM namelist
   #-------------------------------------------------------
   if 'land_init_file' in locals():
      nfile = 'user_nl_elm'
      file = open(nfile,'w')
      fsurdat_root = f'{init_scratch}/lnd/clm2/surfdata_map'
      if ne==30 and npg==2: file.write(f' fsurdat = \'{fsurdat_root}/surfdata_ne30pg2_simyr2010_c210402.nc\' \n')
      file.write(f' finidat = \'{land_init_path}/{land_init_file}\' \n')
      file.close()

   #-------------------------------------------------------
   # Special stuff for hindcast mode
   #-------------------------------------------------------
   os.system(f'./xmlchange -file env_run.xml      RUN_STARTDATE={init_date}')
   os.system(f'./xmlchange -file env_run.xml      SSTICE_DATA_FILENAME={init_file_dir}/{init_file_sst}')
   os.system(f'./xmlchange -file env_run.xml      SSTICE_YEAR_ALIGN={iyr}')
   os.system(f'./xmlchange -file env_run.xml      SSTICE_YEAR_START={iyr}')
   os.system(f'./xmlchange -file env_run.xml      SSTICE_YEAR_END={iyr+1}')
   # os.system('./xmlchange -file env_build.xml    CALENDAR=GREGORIAN)

   file = open('user_nl_eam','a')
   file.write(f' ncdata = \'{init_file_dir}/{init_file_atm}\'\n')
   file.close()

   #-------------------------------------------------------
   # Set some run-time stuff
   #-------------------------------------------------------
   if 'ncpl' in locals(): run_cmd(f'./xmlchange ATM_NCPL={str(ncpl)}')
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
   run_cmd(f'./xmlchange JOB_QUEUE={queue},JOB_WALLCLOCK_TIME={walltime}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')

   # Restart Frequency
   run_cmd(f'./xmlchange -file env_run.xml REST_OPTION={stop_opt},REST_N={stop_n}')
   # run_cmd('./xmlchange -file env_run.xml REST_OPTION=nmonths,REST_N=2')

   if continue_run :
      run_cmd('./xmlchange -file env_run.xml CONTINUE_RUN=TRUE ')   
   else:
      run_cmd('./xmlchange -file env_run.xml CONTINUE_RUN=FALSE ')
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
