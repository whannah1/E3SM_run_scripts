#!/usr/bin/env python
# script for running E3SM-MMF simulations using the 2022 INICTE allocation (CLI115)
# Branch for this campaign: https://github.com/E3SM-Project/E3SM/tree/whannah/mmf/2022-coupled-historical
#---------------------------------------------------------------------------------------------------
# for hybrid coupled runs we need o remove the "xtime" variable from MPAS restarts
# NCO commands below were suggested by Chris Golaz

# mv v2.LR.piControl.mpaso.rst.0501-01-01_00000.nc tmp.nc
# ncks -O --hdr_pad=10000 tmp.nc v2.LR.piControl.mpaso.rst.0501-01-01_00000.nc
# ncrename -v xtime,xtime.orig v2.LR.piControl.mpaso.rst.0501-01-01_00000.nc
# rm tmp.nc

# mv v2.LR.piControl.mpassi.rst.0501-01-01_00000.nc tmp.nc
# ncks -O --hdr_pad=10000 tmp.nc v2.LR.piControl.mpassi.rst.0501-01-01_00000.nc
# ncrename -v xtime,xtime.orig v2.LR.piControl.mpassi.rst.0501-01-01_00000.nc
# rm tmp.nc

# or just remove the variable entirely
#  ncks -x -v xtime in.nc out.nc 
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
import os, numpy as np, subprocess as sp, datetime
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'cli115'
case_dir = os.getenv('HOME')+'/E3SM/Cases/'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC2/' # branch => whannah/mmf/2022-coupled-historical

### flags to control config/build/submit sections
# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

debug_mode = False

### run duration
# queue,stop_opt,stop_n,resub,walltime = 'debug','ndays',1,0,'0:20'
# queue,stop_opt,stop_n,resub,walltime = 'batch','ndays',1,0,'0:20'
# queue,stop_opt,stop_n,resub,walltime = 'batch','n/days',32,0,'2:00'
# queue,stop_opt,stop_n,resub,walltime = 'batch','ndays',183,5*2-1,'4:00'
queue,stop_opt,stop_n,resub,walltime = 'batch','ndays',365,5-1,'4:00'

### common settings
ne,npg = 30,2
# grid = f'ne{ne}pg{npg}_oECv3'
grid = f'ne{ne}pg{npg}_EC30to60E2r2' # match v2 PI control

# MMF options
use_vt,use_mf = True,True

#---------------------------------------------------------------------------------------------------
# specific case names and settings
#---------------------------------------------------------------------------------------------------
### control simulations to tune and accomodate drift
# compset,arch,num_nodes = 'WCYCL1950-PAERO','GNUCPU',128; nicons='0.0001D6' ; nccons='70.0D6' ; ice_sed='500.0' # default
# compset,arch,num_nodes = 'WCYCL1950-PAERO','GNUCPU',128; nicons='0.001D6' ; nccons='100.0D6'
# compset,arch,num_nodes = 'WCYCL1950-PAERO','GNUCPU',128; nicons='0.01D6' ; nccons='200.0D6'
# compset,arch,num_nodes = 'WCYCL1950-PAERO','GNUCPU',128; nicons='0.01D6' ; nccons='40.0D6'
# compset,arch,num_nodes = 'WCYCL1950-PAERO','GNUCPU',128; nicons='0.01D6' ; nccons='70.0D6'
# compset,arch,num_nodes = 'WCYCL1950-PAERO','GNUCPU',128; do_hetfrz=True
# compset,arch,num_nodes = 'WCYCL1950-PAERO','GNUCPU',128; ice_sed='200.0'
compset,arch,num_nodes = 'WCYCL1950-PAERO','GNUCPU',128; ice_sed='1.0' # use a heavy hammer!
# compset,arch,num_nodes = 'WCYCL1950',      'GNUCPU',128
# compset,arch,num_nodes = 'WCYCL1950-MMF1', 'GNUGPU',128
# compset,arch,num_nodes = 'WCYCL1950-MMF1', 'GNUGPU',128; TMN, TMX, QCI = 240, 260, 3.e-5
# compset,arch,num_nodes = 'WCYCL1950-MMF1', 'GNUGPU',128; TMN, TMX, QCW, QCI = 240, 260, 5.e-4, 3.e-5


### transient simulations using IC from control
# compset,arch,num_nodes = 'WCYCL20TR-MMF1', 'GNUGPU',128
# compset,arch,num_nodes = 'WCYCL20TR-PAERO','GNUCPU',128

#---------------------------------------------------------------------------------------------------
# MMF tuning parameter sets for batch 00 (see samxx_const.h)
#---------------------------------------------------------------------------------------------------
### default values
# TMN, TMX, QCW, QCI, VTM = 253.16, 273.16, 1.e-3, 1.e-4, 0.4 

### change multiple values
# TMN, TMX, QCW, QCI, VTM = 253.16, 273.16, 1.e-4, 1.e-5, 0.4 # -- qcw0 and qci0
# TMN, TMX, QCW, QCI, VTM = 240,    273.16, 1.e-4, 1.e-4, 0.6 # -- Tmin and qcw0, ++ vtimin
# TMN, TMX, QCW, QCI, VTM = 240,    273.16, 1.e-3, 1.e-5, 0.4 # -- qci0 and Tmin (no Tmax change)
# TMN, TMX, QCW, QCI, VTM = 230,    250,    1.e-3, 1.e-5, 0.3 # -- qci0, Tmin/Tmax, and vtice to compensate for qci changes
# TMN, TMX, QCW, QCI, VTM = 240,    260,    1.e-3, 1.e-5, 0.4 # -- qci0 and Tmin/Tmax
# TMN, TMX, QCW, QCI, VTM = 240,    260,    1.e-3, 5.e-5, 0.4 # -- qci0 and Tmin/Tmax

# TMN, TMX, QCI = 240, 260, 2.e-5
# TMN, TMX, QCI = 240, 260, 3.e-5

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
### specify case name based on configuration
case_list = ['E3SM','INCITE2022-CPL-T00',grid,compset]
# case_list = ['E3SM','INCITE2022-CPL-T01',grid,compset] # after merging in other branches

if 'MMF' in compset:
   tuning_params_str = ''
   if 'TMN' in locals(): tuning_params_str += f'_TN_{TMN}'
   if 'TMX' in locals(): tuning_params_str += f'_TX_{TMX}'
   if 'QCW' in locals(): tuning_params_str += f'_QW_{QCW:.0E}'
   if 'QCI' in locals(): tuning_params_str += f'_QI_{QCI:.0E}'
   if 'VTM' in locals(): tuning_params_str += f'_VT_{VTM}'
   if tuning_params_str!='': case_list.append(tuning_params_str[1:])

if 'nicons' in locals(): case_list.append(f'nicons_{nicons}')
if 'nccons' in locals(): case_list.append(f'nccons_{nccons}')
if 'ice_sed' in locals(): case_list.append(f'ice_sed_{ice_sed}')

if 'do_hetfrz' in locals(): 
      if do_hetfrz: case_list.append(f'hetfrz')

# case_list.append('P6x7')
# case_list.append('P6x4')

if debug_mode: case_list.append('debug')

case='.'.join(case_list)

#---------------------------------------------------------------------------------------------------
# specify non-default initial condition and surface data files

# init_file_dir = '/gpfs/alpine/scratch/hannah6/cli115/HICCUP/data'
# init_file_atm = 'cami_mam3_Linoz_ne30np4_L125_c20220627.nc'



land_data_path = '/gpfs/alpine/cli115/world-shared/e3sm/inputdata/lnd/clm2/surfdata_map'
land_data_file = 'surfdata_ne30pg2_simyr1850_c210402.nc'
# land_data_file = 'surfdata_ne30pg2_simyr2010_c210402.nc'


# land_init_path = '/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/init_files'
# land_init_file = 'ELM_spinup.ICRUELM.ne30pg2_oECv3.20-yr.2010-01-01.elm.r.2010-01-01-00000.nc'


if 'WCYCL1950' in compset:
   ic_path = f'/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/init_files/PI_control_v2/archive/rest/0501-01-01-00000'
   land_init_path,land_init_file = ic_path,'v2.LR.piControl.elm.r.0501-01-01-00000.nc'
   if 'MMF' in compset:
      # use files created with ~/HICCUP/incite2022.create_IC_from_v2_PI_control.py
      init_file_dir = '/gpfs/alpine/scratch/hannah6/cli115/HICCUP/data/'
      init_file_atm = 'v2.LR.piControl.eam.i.0501-01-01-00000.L60.c20220712.nc'
# use 1950 control for transient initial conditions
if 'WCYCL20TR' in compset:
   exit(f'ERROR: No initial conditions specified for this compset!')
   # ic_path = f'?????'
   # land_init_path,land_init_file = ic_path,'v2.LR.piControl.eam.r.0501-01-01-00000.nc'

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

# dtime = 20*60   # GCM physics time step
if 'dtime' in locals(): ncpl  = 86400 / dtime

num_dyn = ne*ne*6

max_task_per_node = 42
if 'CPU' in arch : max_mpi_per_node,atm_nthrds  = 42,1
if 'GPU' in arch : max_mpi_per_node,atm_nthrds  = 6,7

# if 'GPU' in arch and 'P6x7' in case: max_mpi_per_node,atm_nthrds  = 6,7
# if 'GPU' in arch and 'P6x4' in case: max_mpi_per_node,atm_nthrds  = 6,4

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
   os.chdir(case_dir+case+'/')
   run_cmd('./xmlchange --file env_run.xml RUNDIR=\'/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/$CASE/run\' ' )

   run_cmd(f'./xmlchange --file env_mach_pes.xml --id MAX_TASKS_PER_NODE    --val {max_task_per_node} ')
   run_cmd(f'./xmlchange --file env_mach_pes.xml --id MAX_MPITASKS_PER_NODE --val {max_mpi_per_node} ')
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
   if 'MMF' in compset:
      # rad_ny = rad_nx if crm_ny>1 else 1
      # run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_nx {crm_nx} -crm_ny {crm_ny} \" ')
      # run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_nx_rad {rad_nx} -crm_ny_rad {rad_ny} \" ')
      if use_vt: run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -use_MMF_VT \" ')
   #-------------------------------------------------------
   # Add special CPP flags for MMF options
   cpp_opt = ''
   if debug_mode: cpp_opt += ' -DYAKL_DEBUG'

   if 'MMF' in compset: 
      if use_mf: cpp_opt += ' -DMMF_ESMT -DMMF_USE_ESMT'
      # if  crm_ny==1 and use_mf: cpp_opt += ' -DMMF_ESMT -DMMF_USE_ESMT'
      # if  crm_ny>1  and use_mf: cpp_opt += ' -DMMF_MOMENTUM_FEEDBACK'

      # set tuning parameter values
      if 'TMN' in locals(): cpp_opt += f' -DMMF_TMN={TMN}'
      if 'TMX' in locals(): cpp_opt += f' -DMMF_TMX={TMX}'
      if 'QCW' in locals(): cpp_opt += f' -DMMF_QCW={QCW}'
      if 'QCI' in locals(): cpp_opt += f' -DMMF_QCI={QCI}'
      if 'VTM' in locals(): cpp_opt += f' -DMMF_VTM={VTM}'


   if cpp_opt != '' :
      cmd  = f'./xmlchange --append --file env_build.xml --id CAM_CONFIG_OPTS'
      cmd += f' --val \" -cppdefs \' {cpp_opt} \'  \" '
      run_cmd(cmd)
   #-------------------------------------------------------
   # Set tasks for all components   
   cmd = './xmlchange --file env_mach_pes.xml '
   if 'CPU' in arch : 
      alt_ntask = 2048; cmd += f'NTASKS_OCN={alt_ntask},NTASKS_ICE={alt_ntask}'
      alt_ntask = 1024; cmd += f',NTASKS_LND={alt_ntask},NTASKS_CPL={alt_ntask}'
      alt_ntask = 256; cmd += f',NTASKS_ROF={alt_ntask}'
      alt_ntask =  64; cmd += f',NTASKS_ROF={alt_ntask}'
   if 'GPU' in arch : 
      alt_ntask = 256; cmd += f'NTASKS_OCN={alt_ntask},NTASKS_ICE={alt_ntask}'
      alt_ntask = 256; cmd += f',NTASKS_LND={alt_ntask},NTASKS_CPL={alt_ntask}'
      alt_ntask =  64; cmd += f',NTASKS_ROF={alt_ntask}'
      alt_nthrds =  7; cmd += f',NTHRDS_OCN={alt_nthrds},NTHRDS_ICE={alt_nthrds}'
      alt_nthrds =  7; cmd += f',NTHRDS_LND={alt_nthrds},NTHRDS_CPL={alt_nthrds}'
      alt_nthrds =  7; cmd += f',NTHRDS_ROF={alt_nthrds}'
   alt_ntask = max_mpi_per_node
   cmd += f',NTASKS_WAV={alt_ntask},NTASKS_GLC={alt_ntask}'
   cmd += f',NTASKS_ESP=1,NTASKS_IAC=1'
   run_cmd(cmd)

   # if 'GPU' in arch and 'P6x7' in case: 
   #    alt_ntask = 512; cmd += f'NTASKS_OCN={alt_ntask},NTASKS_ICE={alt_ntask},NTASKS_LND={alt_ntask},NTASKS_CPL={alt_ntask}'
   #    alt_ntask = 6*10; cmd += f',NTASKS_ROF={alt_ntask}'
   #    alt_nthrds =  7; cmd += f',NTHRDS_OCN={alt_nthrds},NTHRDS_ICE={alt_nthrds},NTHRDS_LND={alt_nthrds},NTHRDS_CPL={alt_nthrds}'
   #    alt_nthrds =  7; cmd += f',NTHRDS_ROF={alt_nthrds}'
   #    alt_ntask = max_mpi_per_node; cmd += f',NTASKS_WAV={alt_ntask},NTASKS_GLC={alt_ntask},NTASKS_ESP=1,NTASKS_IAC=1'
   #    run_cmd(cmd)
   # if 'GPU' in arch and 'P6x4' in case: 
   #    alt_ntask = 512; cmd += f'NTASKS_OCN={alt_ntask},NTASKS_ICE={alt_ntask},NTASKS_LND={alt_ntask},NTASKS_CPL={alt_ntask}'
   #    alt_ntask = 6*10; cmd += f',NTASKS_ROF={alt_ntask}'
   #    alt_nthrds =  4; cmd += f',NTHRDS_OCN={alt_nthrds},NTHRDS_ICE={alt_nthrds},NTHRDS_LND={alt_nthrds},NTHRDS_CPL={alt_nthrds}'
   #    alt_nthrds =  4; cmd += f',NTHRDS_ROF={alt_nthrds}'
   #    alt_ntask = max_mpi_per_node; cmd += f',NTASKS_WAV={alt_ntask},NTASKS_GLC={alt_ntask},NTASKS_ESP=1,NTASKS_IAC=1'
   #    run_cmd(cmd)
   #-------------------------------------------------------
   # 64_data format is needed for large output (i.e. high-res grids or CRM data)
   run_cmd('./xmlchange PIO_NETCDF_FORMAT=\"64bit_data\" ')
   #-------------------------------------------------------
   # Run case setup
   if clean : run_cmd('./case.setup --clean')
   run_cmd('./case.setup --reset')
   #-------------------------------------------------------
   # Set up a hybrid run - all cases start in 1950
   run_cmd('./xmlchange RUN_TYPE=hybrid')
   run_cmd('./xmlchange RUN_STARTDATE=1950-01-01,START_TOD=0')
   run_cmd('./xmlchange GET_REFCASE=FALSE')
   # for WCYCL1950 - use PI control for initial conditions
   if 'WCYCL1950' in compset:   
      run_cmd('./xmlchange RUN_REFCASE=\'v2.LR.piControl\'')
      run_cmd('./xmlchange RUN_REFDATE=0501-01-01')
   # use 1950 control for transient initial conditions
   if 'WCYCL20TR' in compset:
      exit('ERROR: dates and stuff need to be set for WCYCL20TR')
      run_cmd('./xmlchange RUN_REFCASE=\'???????\'')
      run_cmd('./xmlchange RUN_REFDATE=???????')
   #-------------------------------------------------------
   # copy the initialization data files
   run_cmd(f'cp {ic_path}/* /gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/{case}/run/')
#---------------------------------------------------------------------------------------------------
# Build
#---------------------------------------------------------------------------------------------------
if build : 
   if debug_mode: run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
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
   (din_loc_root, err) = sp.Popen('./xmlquery DIN_LOC_ROOT    --value', \
                                     stdout=sp.PIPE, shell=True, universal_newlines=True).communicate()
   (config_opts, err) = sp.Popen('./xmlquery CAM_CONFIG_OPTS --value', \
                                     stdout=sp.PIPE, shell=True, universal_newlines=True).communicate()
   config_opts = ' '.join(config_opts.split())   # remove extra spaces to simplify string query
   ntasks_atm = None
   (ntasks_atm     , err) = sp.Popen('./xmlquery NTASKS_ATM    --value', \
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
   file.write('\n')
   #------------------------------
   # Other namelist stuff
   #------------------------------
   # file.write(f' crm_accel_factor = 3 \n')         # CRM acceleration factor (default is 2)

   if 'nicons' in locals(): file.write(f' micro_nicons = {nicons} \n')
   if 'nccons' in locals(): file.write(f' micro_nccons = {nccons} \n')

   if 'ice_sed' in locals(): file.write(f' ice_sed_ai = {ice_sed} \n')

   if 'do_hetfrz' in locals(): 
      if do_hetfrz: file.write(f' use_hetfrz_classnuc = .true. \n')
   

   if num_dyn<ntasks_atm: file.write(' dyn_npes = '+str(num_dyn)+' \n')   # limit dynamics tasks

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
      file.write(f' finidat = \'{land_init_path}/{land_init_file}\' \n')
      if 'land_data_file' in locals():
         file.write(f' fsurdat = \'{land_data_path}/{land_data_file}\' \n')
      file.close()

   #-------------------------------------------------------
   # OCN namelist
   #-------------------------------------------------------
   if 'MMF' in compset:
      dtime = 20*60
      nfile = 'user_nl_mpaso'
      file = open(nfile,'w')
      nminutes = int(dtime/60)
      file.write(f' config_dt = \'00:{nminutes}:00\' \n')
      file.close()

   #-------------------------------------------------------
   # Set some run-time stuff
   #-------------------------------------------------------
   # if 'ncpl' in locals(): 
   if 'MMF' in compset:
      dtime = 20*60; ncpl  = 86400 / dtime
      run_cmd(f'./xmlchange ATM_NCPL={ncpl},LND_NCPL={ncpl},ICE_NCPL={ncpl},OCN_NCPL={ncpl}')
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n}')
   if 'resub' in locals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
   run_cmd(f'./xmlchange JOB_QUEUE={queue},JOB_WALLCLOCK_TIME={walltime}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')

   # Restart Frequency - make it more frequent in case things go off the rails
   # run_cmd('./xmlchange --file env_run.xml REST_OPTION=nmonths,REST_N=6')
   # run_cmd(f'./xmlchange --file env_run.xml REST_OPTION={stop_opt},REST_N={stop_n}')

   if continue_run :
      run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=TRUE ')   
   else:
      run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=FALSE ')
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
