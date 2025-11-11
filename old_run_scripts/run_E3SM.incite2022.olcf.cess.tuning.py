#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
import os, numpy as np, subprocess as sp, datetime
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'cli115'
case_dir = os.getenv('HOME')+'/E3SM/Cases/'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC4/' # branch => whannah/mmf/2022-cess

### flags to control config/build/submit sections
# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
continue_run = True

debug_mode = False

queue = 'debug' # batch / debug

### run duration
stop_opt,stop_n,resub,walltime = 'ndays',1,0,'0:10'
# stop_opt,stop_n,resub,walltime = 'ndays',91,2,'3:00'
# stop_opt,stop_n,resub,walltime = 'ndays',32,0,'2:00'
# stop_opt,stop_n,resub,walltime = 'ndays',60,0,'2:00'

### common settings
ne,npg = 45,2
grid   = f'ne{ne}pg{npg}_r05_oECv3'


# MMF options
rad_nx        = 4 
use_vt,use_mf = True,True

crm_sed = False

#---------------------------------------------------------------------------------------------------
# specific case names and settings
#---------------------------------------------------------------------------------------------------
compset,arch,num_nodes,sst_pert,crm_nx,crm_ny = 'F2010-MMF1','GNUGPU',1000,0,32,32
# compset,arch,num_nodes,sst_pert,crm_nx,crm_ny = 'F2010-MMF1','GNUGPU',128,0,32,1
# compset,arch,num_nodes,sst_pert               = 'F2010',     'GNUCPU',128,0

################################################################################
################################################################################
# # override stuff for quick debug
# ne,npg = 4,2
# grid   = f'ne{ne}pg{npg}_ne{ne}pg{npg}'
# compset,arch,num_nodes,sst_pert,crm_nx,crm_ny = 'F2010-MMF1','GNUGPU',1,0,32,32
################################################################################
################################################################################

#---------------------------------------------------------------------------------------------------
# MMF tuning parameter sets for batch 00 (see samxx_const.h)
#---------------------------------------------------------------------------------------------------
### default values
# TMN, TMX, QCW, QCI, VTM = 253.16, 273.16, 1.e-3, 1.e-4, 0.4 

### only change single parameter/process at a time
# TMN, TMX, QCW, QCI, VTM = 240,    273.16, 1.e-3, 1.e-4, 0.4 # -- Tmin
# TMN, TMX, QCW, QCI, VTM = 240,    260,    1.e-3, 1.e-4, 0.4 # -- Tmin and Tmax
# TMN, TMX, QCW, QCI, VTM = 253.16, 273.16, 1.e-4, 1.e-4, 0.4 # -- qcw0
# TMN, TMX, QCW, QCI, VTM = 253.16, 273.16, 1.e-3, 1.e-5, 0.4 # -- qci0
# TMN, TMX, QCW, QCI, VTM = 253.16, 273.16, 1.e-3, 1.e-6, 0.4 # -- qci0
# TMN, TMX, QCW, QCI, VTM = 253.16, 273.16, 1.e-3, 1.e-4, 0.6 # ++ vtimin

### change multiple values
# TMN, TMX, QCW, QCI, VTM = 253.16, 273.16, 1.e-4, 1.e-5, 0.4 # -- qcw0 and qci0
# TMN, TMX, QCW, QCI, VTM = 240,    273.16, 1.e-4, 1.e-4, 0.6 # -- Tmin and qcw0, ++ vtimin
# TMN, TMX, QCW, QCI, VTM = 240,    273.16, 1.e-3, 1.e-5, 0.4 # -- qci0 and Tmin (no Tmax change)
# TMN, TMX, QCW, QCI, VTM = 230,    250,    1.e-3, 1.e-5, 0.3 # -- qci0, Tmin/Tmax, and vtice to compensate for qci changes
# TMN, TMX, QCW, QCI, VTM = 240,    260,    1.e-3, 1.e-5, 0.4 # -- qci0 and Tmin/Tmax
# TMN, TMX, QCW, QCI, VTM = 240,    260,    1.e-3, 5.e-5, 0.4 # -- qci0 and Tmin/Tmax

TMN, TMX, QCW, QCI, VTM = 240,    260,    1.e-3, 2.e-5, 0.4 # -- qci0 and Tmin/Tmax
# TMN, TMX, QCW, QCI, VTM = 240,    260,    1.e-3, 3.e-5, 0.4 # -- qci0 and Tmin/Tmax

# TMN, TMX, QCW, QCI, VTM = 240,    260,    1.e-4, 3.e-5, 0.4 # -- qci0, qcw0, and Tmin/Tmax - need much smaller qcw change to be useful!

# crm_sed=True; TMN, TMX, QCW, QCI, VTM = 240,    260,    1.e-3, 3.e-5, 0.4 # -- qci0 and Tmin/Tmax
# crm_sed=True; TMN, TMX, QCW, QCI, VTM = 240,    260,    1.e-4, 3.e-5, 0.4 # -- qci0, qcw0, and Tmin/Tmax

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

### specify case name based on configuration
case_list = ['E3SM','INCITE2022-CESS-T00',f'ne{ne}pg{npg}',f'SSTP_{sst_pert}K',compset]
if 'MMF' in compset:
   case_list.append(f'NXY_{crm_nx}x{crm_ny}')
   
   if crm_sed: case_list.append(f'SED')

   tuning_params_str = ''
   tuning_params_str += f'_TN_{TMN}'
   tuning_params_str += f'_TX_{TMX}'
   tuning_params_str += f'_QW_{QCW:.0E}'
   tuning_params_str += f'_QI_{QCI:.0E}'
   tuning_params_str += f'_VT_{VTM}'
   case_list.append(tuning_params_str[1:])

   # alt_atm_nthrds = 1
   # alt_atm_nthrds = 2
   # alt_atm_nthrds = 4
   # case_list.append('MACH_TEST')
   # case_list.append(f'NTHRDS_{alt_atm_nthrds}')


if debug_mode: case_list.append('debug')

case='.'.join(case_list)

# exit(case)

#---------------------------------------------------------------------------------------------------
# specify non-default initial condition and surface data files
if '_r05_' in grid:
   land_data_path = '/gpfs/alpine/cli115/world-shared/e3sm/inputdata/lnd/clm2/surfdata_map'
   land_data_file = 'surfdata_0.5x0.5_simyr2000_c200624.nc'

   land_init_path = '/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/init_files'
   land_init_file = 'CLM_spinup.ICRUELM.ne45pg2_r05_oECv3.20-yr.2010-10-01.elm.r.2006-01-01-00000.nc'
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print(f'\n  case : {case}\n')

# dtime = 20*60   # GCM physics time step
if 'dtime' in locals(): ncpl  = 86400 / dtime

num_dyn = ne*ne*6

max_task_per_node = 42
if 'CPU' in arch : max_mpi_per_node,atm_nthrds  = 42,1
if 'GPU' in arch : max_mpi_per_node,atm_nthrds  = 6,4

atm_nthrds = 2 # this is temporary to run something before I can get nthrds=4 to work

if 'alt_atm_nthrds' in locals(): atm_nthrds = alt_atm_nthrds

task_per_node = max_mpi_per_node
atm_ntasks = task_per_node*num_nodes
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
   os.chdir(f'{case_dir}/{case}/')
   run_cmd('./xmlchange -file env_run.xml RUNDIR=\'/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/$CASE/run\' ' )

   run_cmd(f'./xmlchange -file env_mach_pes.xml -id MAX_TASKS_PER_NODE    -val {max_task_per_node} ')
   run_cmd(f'./xmlchange -file env_mach_pes.xml -id MAX_MPITASKS_PER_NODE -val {max_mpi_per_node} ')
else:
   os.chdir(f'{case_dir}/{case}/')
#---------------------------------------------------------------------------------------------------
if config : 
   #-------------------------------------------------------
   if 'init_file_atm' in locals():
      file = open('user_nl_eam','w')
      file.write(f' ncdata = \'{init_file_dir}/{init_file_atm}\'\n')
      file.close()
   #-------------------------------------------------------
   # Set some non-default stuff for all MMF experiments here
   if 'MMF' in compset:
      rad_ny = rad_nx if crm_ny>1 else 1
      run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx {crm_nx} -crm_ny {crm_ny} \" ')
      run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_nx_rad {rad_nx} -crm_ny_rad {rad_ny} \" ')
      if use_vt: run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -use_MMF_VT \" ')
   #-------------------------------------------------------
   # Add special CPP flags for MMF options
   cpp_opt = ''
   if debug_mode: cpp_opt += ' -DYAKL_DEBUG'

   if 'MMF' in compset: 
      if  crm_ny==1 and use_mf: cpp_opt += ' -DMMF_ESMT -DMMF_USE_ESMT'
      if  crm_ny>1  and use_mf: cpp_opt += ' -DMMF_MOMENTUM_FEEDBACK'

      if crm_sed: cpp_opt += ' -DMMF_SEDIMENTATION'
      
      # set tuning parameter values
      if 'TMN' in locals(): cpp_opt += f' -DMMF_TMN={TMN}'
      if 'TMX' in locals(): cpp_opt += f' -DMMF_TMX={TMX}'
      if 'QCW' in locals(): cpp_opt += f' -DMMF_QCW={QCW}'
      if 'QCI' in locals(): cpp_opt += f' -DMMF_QCI={QCI}'
      if 'VTM' in locals(): cpp_opt += f' -DMMF_VTM={VTM}'

   if cpp_opt != '' :
      cmd  = f'./xmlchange --append -file env_build.xml -id CAM_CONFIG_OPTS'
      cmd += f' -val \" -cppdefs \' {cpp_opt} \'  \" '
      run_cmd(cmd)
   #-------------------------------------------------------
   # Set tasks for all components
   cmd = './xmlchange -file env_mach_pes.xml '
   if num_nodes>200:
      if 'GPU' in arch:
         alt_ntask = int(2048/atm_nthrds)
         cmd += f'NTASKS_OCN={alt_ntask},NTASKS_ICE={alt_ntask}'
         alt_ntask = int(1024/atm_nthrds)
         cmd += f',NTASKS_LND={alt_ntask},NTASKS_CPL={alt_ntask}'
      if 'CPU' in arch:
         exit('\nERROR: what are you doing?!? You need to set the NTASK settings for this case. \n')
   if num_nodes<200:
      alt_ntask = 768; cmd += f'NTASKS_OCN={alt_ntask},NTASKS_ICE={alt_ntask}'
      alt_ntask = 768; cmd += f',NTASKS_LND={alt_ntask},NTASKS_CPL={alt_ntask}'
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
   # file.write(" fincl2    = 'PS','PSL','TS'")
   # file.write(             ",'PRECT','TMQ'")
   # file.write(             ",'LHFLX','SHFLX'")             # surface fluxes
   # file.write(             ",'FSNT','FLNT'")               # Net TOM heating rates
   # file.write(             ",'FLNS','FSNS'")               # Surface rad for total column heating
   # file.write(             ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
   # file.write(             ",'FLUT','FSNTOA'")
   # file.write(             ",'LWCF','SWCF'")               # cloud radiative foricng
   # file.write(             ",'TGCLDLWP','TGCLDIWP'")       # liq/ice water path
   # file.write(             ",'TAUX','TAUY'")               # surface stress
   
   # file.write(             ",'TUQ','TVQ'")                         # vapor transport
   # file.write(             ",'TBOT:I','QBOT:I','UBOT:I','VBOT:I'") # lowest model leve
   # file.write(             ",'T900:I','Q900:I','U900:I','V900:I'") # 900mb data
   # file.write(             ",'T850:I','Q850:I','U850:I','V850:I'") # 850mb data
   # file.write(             ",'Z300:I','Z500:I'")
   # file.write(             ",'OMEGA850:I','OMEGA500:I'")

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
   # file.write('\n')
   #------------------------------
   # Other namelist stuff
   #------------------------------
   # file.write(f' crm_accel_factor = 3 \n')         # CRM acceleration factor (default is 2)

   # if num_dyn<ntasks_atm: file.write(f' dyn_npes = {num_dyn} \n')
   if num_dyn<(ntasks_atm*atm_nthrds): 
      file.write(f' dyn_npes = {int(num_dyn/atm_nthrds)} \n')

   file.write(" inithist = \'NONE\' \n") # ENDOFRUN / NONE

   if 'init_file_atm' in locals():
      file.write(f' ncdata = \'{init_file_dir}/{init_file_atm}\'\n')

   file.close()
   #-------------------------------------------------------
   # ELM namelist
   #-------------------------------------------------------
   if 'land_init_file' in locals():
      nfile = 'user_nl_elm'
      file = open(nfile,'w')
      file.write(f' fsurdat = \'{land_data_path}/{land_data_file}\' \n')
      file.write(f' finidat = \'{land_init_path}/{land_init_file}\' \n')
      file.close()

   #-------------------------------------------------------
   # Modified SST file
   #-------------------------------------------------------
   # os.system(f'./xmlchange -file env_run.xml      SSTICE_DATA_FILENAME={init_file_dir}/{init_file_sst}')

   #-------------------------------------------------------
   # Set some run-time stuff
   #-------------------------------------------------------
   if 'ncpl' in locals(): run_cmd(f'./xmlchange ATM_NCPL={str(ncpl)}')
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
   run_cmd(f'./xmlchange JOB_QUEUE={queue},JOB_WALLCLOCK_TIME={walltime}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')

   # Restart Frequency
   # run_cmd(f'./xmlchange -file env_run.xml REST_OPTION={stop_opt},REST_N={stop_n}')
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
