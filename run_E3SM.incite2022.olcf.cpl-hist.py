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
import os, numpy as np, subprocess as sp, datetime, glob
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'cli115'
case_dir = os.getenv('HOME')+'/E3SM/Cases/'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC2/' # branch => whannah/mmf/2022-coupled-historical

### flags to control config/build/submit sections
# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
continue_run = True

debug_mode = False

### run duration
# queue,stop_opt,stop_n,resub,walltime = 'batch','ndays',5,0,'0:30'
# queue,stop_opt,stop_n,resub,walltime = 'batch','ndays',73,0,'2:00'
queue,stop_opt,stop_n,resub,walltime = 'batch','ndays',365,20-1,'4:00'

ne,npg = 30,2; grid = f'ne{ne}pg{npg}_EC30to60E2r2' # match v2 PI control

#---------------------------------------------------------------------------------------------------
# specific case names and settings
#---------------------------------------------------------------------------------------------------
### control simulations to accomodate initial adjustment
# compset,arch,num_nodes = 'WCYCL1950-MMF1', 'GNUGPU', 160
# compset,arch,num_nodes = 'WCYCL1950',      'GNUCPU', 128
# compset,arch,num_nodes = 'WCYCL1950-PAERO','GNUCPU', 128


### transient simulations using IC from control
# compset,arch,num_nodes = 'WCYCL20TR-MMF1', 'GNUGPU',160
compset,arch,num_nodes = 'WCYCL20TR',      'GNUCPU',128
# compset,arch,num_nodes = 'WCYCL20TR-PAERO','GNUCPU',128

# Tuning adjustments
if 'MMF'   in compset: TMN, TMX, QCW, QCI = 240, 260, 5.e-4, 3.e-5
if 'PAERO' in compset: nicons='0.001D6' ; nccons='40.0D6'
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
### specify case name based on configuration
case_list = ['E3SM','INCITE2022-CPL',grid,compset]

if debug_mode: case_list.append('debug')

case='.'.join(case_list)

#---------------------------------------------------------------------------------------------------
# specify non-default initial condition and surface data files

lnd_data_path = '/gpfs/alpine/cli115/world-shared/e3sm/inputdata/lnd/clm2/surfdata_map'
lnd_data_file = 'surfdata_ne30pg2_simyr1850_c210402.nc'
# lnd_data_file = 'surfdata_ne30pg2_simyr2010_c210402.nc'

# perpetual 1950 for initial adjustment
if 'WCYCL1950' in compset:
   ic_path = f'/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/init_files/PI_control_v2/archive/rest/0501-01-01-00000'
   lnd_init_path,lnd_init_file = ic_path,'v2.LR.piControl.elm.r.0501-01-01-00000.nc'
   if 'MMF' in compset:
      # use files created with ~/HICCUP/incite2022.create_IC_from_v2_PI_control.py
      atm_init_path = '/gpfs/alpine/scratch/hannah6/cli115/HICCUP/data/'
      atm_init_file = 'v2.LR.piControl.eam.i.0501-01-01-00000.L60.c20220712.nc'

# use 1950 control for transient initial conditions
if 'WCYCL20TR' in compset:
   if 'MMF' in compset:
      ic_case = 'E3SM.INCITE2022-CPL.ne30pg2_EC30to60E2r2.WCYCL1950-MMF1'
      ic_date = '1960-01-01'
      ic_path = f'/ccs/home/hannah6/E3SM/scratch2/{ic_case}/run/'
      # lnd_init_path,lnd_init_file = ic_path,f'E3SM.INCITE2022-CPL.ne30pg2_EC30to60E2r2.WCYCL1950-MMF1.elm.r.{ic_date}-00000.nc'
      # atm_init_path,atm_init_file = ic_path,f'E3SM.INCITE2022-CPL.ne30pg2_EC30to60E2r2.WCYCL1950-MMF1.eam.r.{ic_date}-00000.nc'
   else:
      ic_case = 'E3SM.INCITE2022-CPL.ne30pg2_EC30to60E2r2.WCYCL1950'
      ic_date = '1960-01-01'
      ic_path = f'/ccs/home/hannah6/E3SM/scratch2/{ic_case}/run/'

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

if 'MMF' in compset: dtime = 20*60 ; ncpl = 86400/dtime

num_dyn = ne*ne*6

max_task_per_node = 42
if 'CPU' in arch : max_mpi_per_node,atm_nthrds  = 42,1
if 'GPU' in arch : max_mpi_per_node,atm_nthrds  = 6,7

task_per_node = max_mpi_per_node
atm_ntasks = task_per_node*num_nodes
cpl_ntasks,rof_ntasks = atm_ntasks,atm_ntasks

# LB6/LB8 from load balancing tests
if 'GPU' in arch : ocn_ntasks,ice_ntasks=480,atm_ntasks ; ice_nthrds,ocn_nthrds=2,2 ; lnd_ntasks=atm_ntasks ; rootpe_ice=0
if 'CPU' in arch : ocn_ntasks,ice_ntasks=640,atm_ntasks ; ice_nthrds,ocn_nthrds=1,1 ; lnd_ntasks=atm_ntasks ; rootpe_ice=0

total_ntasks, total_nthrds = atm_ntasks, atm_nthrds
diff_ocn_nodes = True
if diff_ocn_nodes: total_ntasks = total_ntasks + ocn_ntasks
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
   os.chdir(case_dir+case+'/')
   run_cmd(f'./xmlchange --file env_mach_pes.xml --id MAX_TASKS_PER_NODE    --val {max_task_per_node} ')
   run_cmd(f'./xmlchange --file env_mach_pes.xml --id MAX_MPITASKS_PER_NODE --val {max_mpi_per_node} ')
else:
   os.chdir(case_dir+case+'/')
#---------------------------------------------------------------------------------------------------
if config : 
   #-------------------------------------------------------
   if 'atm_init_file' in locals(): 
      file = open('user_nl_eam','w')
      file.write(f' ncdata = \'{atm_init_path}/{atm_init_file}\'\n')
      file.close()
   #-------------------------------------------------------
   # enable COSP for all runs
   run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -cosp \" ')
   #-------------------------------------------------------
   # Add special options for MMF

   if 'crm_dt' in locals(): run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -crm_dt {crm_dt} \" ')

   cpp_opt = ''
   if debug_mode: cpp_opt += ' -DYAKL_DEBUG'

   # set tuning parameter values      
   if 'MMF' in compset and 'TMN' in locals(): cpp_opt += f' -DMMF_TMN={TMN}'
   if 'MMF' in compset and 'TMX' in locals(): cpp_opt += f' -DMMF_TMX={TMX}'
   if 'MMF' in compset and 'QCW' in locals(): cpp_opt += f' -DMMF_QCW={QCW}'
   if 'MMF' in compset and 'QCI' in locals(): cpp_opt += f' -DMMF_QCI={QCI}'

   if cpp_opt != '' :
      cmd  = f'./xmlchange --append --file env_build.xml --id CAM_CONFIG_OPTS'
      cmd += f' --val \" -cppdefs \' {cpp_opt} \'  \" '
      run_cmd(cmd)
   #-------------------------------------------------------
   # Set tasks for each component
   run_cmd(f'./xmlchange --file env_mach_pes.xml NTASKS_CPL={cpl_ntasks}')
   run_cmd(f'./xmlchange --file env_mach_pes.xml NTASKS_LND={lnd_ntasks}')
   run_cmd(f'./xmlchange --file env_mach_pes.xml NTASKS_OCN={ocn_ntasks}')
   run_cmd(f'./xmlchange --file env_mach_pes.xml NTASKS_ICE={ice_ntasks}')
   run_cmd(f'./xmlchange --file env_mach_pes.xml NTASKS_ROF={rof_ntasks}')

   if 'ice_nthrds' in locals(): run_cmd(f'./xmlchange --file env_mach_pes.xml NTHRDS_ICE={ice_nthrds}')
   if 'ocn_nthrds' in locals(): run_cmd(f'./xmlchange --file env_mach_pes.xml NTHRDS_OCN={ocn_nthrds}')

   if diff_ocn_nodes: run_cmd(f'./xmlchange --file env_mach_pes.xml ROOTPE_OCN={atm_ntasks}')
   run_cmd(f'./xmlchange --file env_mach_pes.xml ROOTPE_ICE={rootpe_ice}')

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
      run_cmd(f'./xmlchange RUN_REFCASE=\'{ic_case}\'')
      run_cmd(f'./xmlchange RUN_REFDATE={ic_date}')
   #-------------------------------------------------------
   # copy the initialization data files
   run_dir = f'/gpfs/alpine/cli115/proj-shared/hannah6/e3sm_scratch/{case}/run'
   if 'WCYCL1950' in compset:
      run_cmd(f'cp {ic_path}/* {run_dir}/')
   if 'WCYCL20TR' in compset:
      run_cmd(f'cp {ic_path}/*{ic_date}* {run_dir}/')
      run_cmd('module load nco')
      mpaso_rst = f'{run_dir}/{ic_case}.mpaso.rst.{ic_date}_00000.nc' 
      mpasi_rst = f'{run_dir}/{ic_case}.mpassi.rst.{ic_date}_00000.nc'
      run_cmd(f'ncks -x -v xtime -O {mpaso_rst} {mpaso_rst}')
      run_cmd(f'ncks -x -v xtime -O {mpasi_rst} {mpasi_rst}')
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
   #-------------------------------------------------------
   # Namelist options
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   #------------------------------
   # Specify history output frequency and variables
   file.write(' nhtfrq     = 0,-1,-24 \n') 
   file.write(' mfilt      = 1,24,1 \n') # 1-day files
   file.write(" fincl1    = 'Z3'") # this is for easier use of height axis on profile plots   
   file.write(            ",'CLOUD','CLDLIQ','CLDICE'")
   file.write(            ",'PTTEND','PTEQ'")             # 3D physics tendencies
   file.write(            ",'PTECLDLIQ','PTECLDICE'")     # 3D physics tendencies
   file.write('\n')
   file.write(" fincl1     = 'Z3'") # this is for easier use of height axis on profile plots   
   file.write(             ",'CLOUD','CLDLIQ','CLDICE'")
   file.write(             ",'CLDTOT_ISCCP','FISCCP1_COSP','CLDPTOP_ISCCP','MEANCLDALB_ISCCP'")
   file.write(             ",'MEANPTOP_ISCCP','MEANTAU_ISCCP','MEANTB_ISCCP','MEANTBCLR_ISCCP'")
   file.write(             ",'FSNS','FSNT'")               # probably default but add to be safe
   file.write(             ",'FSNTOA','FSUTOA'")           # probably default but add to be safe
   file.write(             ",'FSNTOAC','FSUTOAC'")         # probably default but add to be safe
   file.write(             ",'FSNTC','FSNSC'")             # probably default but add to be safe
   file.write(             ",'FSDSC','FSDS'")              # probably default but add to be safe
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
   file.write(             ",'TUQ','TVQ'")                         # vapor transport
   file.write(             ",'TBOT:I','QBOT:I','UBOT:I','VBOT:I'") # lowest model leve
   file.write(             ",'T900:I','Q900:I','U900:I','V900:I'") # 900mb data
   file.write(             ",'T850:I','Q850:I','U850:I','V850:I'") # 850mb data
   file.write(             ",'Z300:I','Z500:I'")
   file.write(             ",'OMEGA850:I','OMEGA500:I'")
   file.write(             ",'U200:I','V200:I'")                   # 200mb winds
   file.write('\n')
   # file.write(" fincl3    = 'PS','T','Q','Z3'")            # 3D thermodynamic fields
   # file.write(             ",'U','V','OMEGA'")             # 3D velocity components
   # file.write(             ",'CLOUD','CLDLIQ','CLDICE'")   # 3D cloud fields
   # file.write(             ",'QRL','QRS'")                 # 3D radiative heating 
   # file.write(             ",'QRLC','QRSC'")               # 3D clearsky radiative heating 
   # file.write(             ",'PTTEND','PTEQ'")             # 3D physics tendencies
   # file.write(             ",'PTECLDLIQ','PTECLDICE'")     # 3D physics tendencies
   # file.write('\n')
   #------------------------------
   # Other namelist stuff
   if 'nicons' in locals(): file.write(f' micro_nicons = {nicons} \n')
   if 'nccons' in locals(): file.write(f' micro_nccons = {nccons} \n')
   file.write(f' cosp_lite = .true. \n')
   # file.write(f' crm_accel_factor = 3 \n') # CRM acceleration factor (default is 2)
   file.write(" inithist = \'YEARLY\' \n") # ENDOFRUN / NONE / YEARLY
   if 'atm_init_file' in locals(): file.write(f' ncdata = \'{atm_init_path}/{atm_init_file}\'\n')
   file.close()
   #-------------------------------------------------------
   # ELM namelist
   if 'lnd_init_file' in locals() or 'lnd_data_file' in locals():
      nfile = 'user_nl_elm'
      file = open(nfile,'w')
      if 'lnd_init_file' in locals():file.write(f' finidat = \'{lnd_init_path}/{lnd_init_file}\' \n')
      if 'lnd_data_file' in locals():file.write(f' fsurdat = \'{lnd_data_path}/{lnd_data_file}\' \n')
      file.close()
   #-------------------------------------------------------
   # OCN namelist
   if 'dtime' in locals():
      nfile = 'user_nl_mpaso'
      file = open(nfile,'w')
      nminutes = int(dtime/60)
      file.write(f' config_dt = \'00:{nminutes}:00\' \n')
      file.close()
   #-------------------------------------------------------
   # Set some run-time stuff
   if not continue_run:
      if 'dtime' in locals():
         run_cmd(f'./xmlchange ATM_NCPL={ncpl},LND_NCPL={ncpl},ICE_NCPL={ncpl},OCN_NCPL={ncpl}')
      run_cmd(f'./xmlchange JOB_QUEUE={queue},JOB_WALLCLOCK_TIME={walltime}')
      run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')

   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n}')
   if 'resub' in locals(): run_cmd(f'./xmlchange RESUBMIT={resub}')

   continue_flag = 'TRUE' if continue_run else 'FALSE'
   run_cmd(f'./xmlchange --file env_run.xml CONTINUE_RUN={continue_flag} ')
   #-------------------------------------------------------
   # Submit the run
   run_cmd('./case.submit')
#---------------------------------------------------------------------------------------------------
# Print the case name again
print(f'\n  case : {case}\n')
#---------------------------------------------------------------------------------------------------
