#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'cli115'
case_dir = os.getenv('HOME')+'/E3SM/Cases'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC2' # branch => whannah/mmf/2022-coupled-historical
# src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC4' # branch => whannah/mmf/2023-4xCO2


# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
continue_run = True

debug_mode = False

queue = 'batch' # batch / debug


# stop_opt,stop_n,resub,walltime = 'ndays',1,0,'0:10'
# stop_opt,stop_n,resub,walltime = 'ndays',32,0,'2:00'
stop_opt,stop_n,resub,walltime = 'ndays',365,40-1,'6:00'

compset,num_nodes,arch = 'WCYCL1850-MMF1',160,'GNUGPU'
# compset,num_nodes,arch = 'WCYCL1850'     ,128,'GNUCPU'

# ne = 30; grid = f'ne{ne}pg2_oECv3' # for 00
ne,npg = 30,2; grid = f'ne{ne}pg{npg}_EC30to60E2r2' # for 01 to match v2 PI control

### previous test kept failing, so 00 = use branch for coupled historical runs

# case = '.'.join(['E3SM','2023-CO2-TEST-00',arch,grid,compset,f'1xCO2'])
# case = '.'.join(['E3SM','2023-CO2-TEST-00',arch,grid,compset,f'4xCO2'])
### use tuning from historical run
# case = '.'.join(['E3SM','2023-CO2-TEST-01',arch,grid,compset,f'1xCO2'])
# case = '.'.join(['E3SM','2023-CO2-TEST-01',arch,grid,compset,f'2xCO2'])
case = '.'.join(['E3SM','2023-CO2-TEST-01',arch,grid,compset,f'4xCO2'])

if debug_mode: case = case+'.debug'

### specify land initial condition file for 00
# land_init_path = '/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/init_files'
# land_init_file = 'ELM_spinup.ICRUELM.ne30pg2_oECv3.20-yr.2010-01-01.elm.r.2010-01-01-00000.nc'
# land_data_path = '/gpfs/alpine/cli115/world-shared/e3sm/inputdata/lnd/clm2/surfdata_map'
# land_data_file = 'surfdata_ne30pg2_simyr2010_c210402.nc'

### specify land initial condition file for 01
land_init_path = '/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/init_files'
# land_init_file = 'E3SM.INCITE2023-CPL.ne30pg2_EC30to60E2r2.WCYCL20TR-MMF1.elm.r.1951-01-01-00000.nc'
land_init_file = 'ELM_spinup.ICRUELM.ne30pg2_EC30to60E2r2.20-yr.1850-01-01.elm.r.1840-01-01-00000.nc'
land_data_path = '/gpfs/alpine/cli115/world-shared/e3sm/inputdata/lnd/clm2/surfdata_map'
land_data_file = 'surfdata_ne30pg2_simyr1850_c210402.nc'

# Tuning adjustments
if 'MMF'   in compset: TMN, TMX, QCW, QCI = 240, 260, 5.e-4, 3.e-5
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

max_task_per_node = 42
if 'CPU' in arch : max_mpi_per_node,atm_nthrds  = 42,1
if 'GPU' in arch : max_mpi_per_node,atm_nthrds  = 6,7
atm_ntasks = max_mpi_per_node*num_nodes

# LB6/LB8 from load balancing tests
cpl_ntasks,rof_ntasks = atm_ntasks,atm_ntasks
if 'GPU' in arch : 
   ocn_ntasks,ice_ntasks=480,atm_ntasks 
   ice_nthrds,ocn_nthrds=2,2 
   lnd_ntasks=atm_ntasks 
   rootpe_ice=0
if 'CPU' in arch : 
   ocn_ntasks,ice_ntasks=640,atm_ntasks
   ice_nthrds,ocn_nthrds=1,1
   lnd_ntasks=atm_ntasks
   rootpe_ice=0

diff_ocn_nodes = True
#---------------------------------------------------------------------------------------------------
if newcase :
   if os.path.isdir(f'{case_dir}/{case}'): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
   cmd = f'{src_dir}/cime/scripts/create_newcase -case {case_dir}/{case}'
   cmd = cmd + f' -compset {compset} -res {grid}  '
   if arch=='GNUCPU' : cmd += f' -mach summit -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
   if arch=='GNUGPU' : cmd += f' -mach summit -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
   run_cmd(cmd)
os.chdir(f'{case_dir}/{case}/')
if newcase :
   if 'max_mpi_per_node'  in locals(): run_cmd(f'./xmlchange MAX_MPITASKS_PER_NODE={max_mpi_per_node} ')
   if 'max_task_per_node' in locals(): run_cmd(f'./xmlchange MAX_TASKS_PER_NODE={max_task_per_node} ')
#---------------------------------------------------------------------------------------------------
if config :
   #----------------------------------------------------------------------------
   # cpp_opt = ''
   # cpp_opt += f' -D'
   # if cpp_opt != '' :
   #    cmd  = f'./xmlchange --append --file env_build.xml --id CAM_CONFIG_OPTS'
   #    cmd += f' --val \" -cppdefs \' {cpp_opt} \'  \" '
   #    run_cmd(cmd)
   #----------------------------------------------------------------------------
   # enable COSP for all runs
   run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -cosp \" ')
   #-------------------------------------------------------
   # Add special options for MMF
   cpp_opt = ''
   # set tuning parameter values      
   if 'MMF' in compset and 'TMN' in locals(): cpp_opt += f' -DMMF_TMN={TMN}'
   if 'MMF' in compset and 'TMX' in locals(): cpp_opt += f' -DMMF_TMX={TMX}'
   if 'MMF' in compset and 'QCW' in locals(): cpp_opt += f' -DMMF_QCW={QCW}'
   if 'MMF' in compset and 'QCI' in locals(): cpp_opt += f' -DMMF_QCI={QCI}'
   if cpp_opt != '' :
      cmd  = f'./xmlchange --append --file env_build.xml --id CAM_CONFIG_OPTS'
      cmd += f' --val \" -cppdefs \' {cpp_opt} \'  \" '
      run_cmd(cmd)
   #----------------------------------------------------------------------------
   if '1xCO2' in case: run_cmd(f'./xmlchange CCSM_CO2_PPMV=284.317') # pre-industrial - matches 1850 compset
   if '2xCO2' in case: run_cmd(f'./xmlchange CCSM_CO2_PPMV=568.634')
   if '4xCO2' in case: run_cmd(f'./xmlchange CCSM_CO2_PPMV=1137.268')
   #----------------------------------------------------------------------------
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
   #----------------------------------------------------------------------------
   run_cmd('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
if build : 
   if debug_mode: run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
if submit : 
   #----------------------------------------------------------------------------
   # ATM namelist
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   file.write(' nhtfrq = 0,-3,-3 \n')
   file.write(' mfilt  = 1,8,8 \n')
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
   file.write(" fincl2 = 'PS','TS','PSL'")
   file.write(          ",'PRECT','TMQ'")
   file.write(          ",'LHFLX','SHFLX'")             # surface fluxes
   file.write(          ",'FSNT','FLNT','FLUT'")        # TOM heating rates
   file.write(          ",'FLNS','FSNS'")               # SFC rad for total column heating
   file.write(          ",'FSNTC','FLNTC'")             # clear sky heating rates for CRE
   file.write(          ",'TGCLDLWP','TGCLDIWP'")
   file.write(          ",'TAUX','TAUY'")               # surface stress
   file.write(          ",'TUQ','TVQ'")                         # vapor transport
   file.write(          ",'TBOT:I','QBOT:I','UBOT:I','VBOT:I'") # lowest model leve
   file.write(          ",'T900:I','Q900:I','U900:I','V900:I'") # 900mb data
   file.write(          ",'T850:I','Q850:I','U850:I','V850:I'") # 850mb data
   file.write(          ",'Z300:I','Z500:I'")
   file.write(          ",'OMEGA850:I','OMEGA500:I'")
   file.write(          ",'TREFHTMN','TREFHTMX'")
   file.write(          ",'TREFHT','QREFHT'")
   file.write('\n')
   # file.write(" fincl3 =  'PS','PSL'")
   # file.write(          ",'T','Q','Z3' ")               # 3D thermodynamic budget components
   # file.write(          ",'U','V','OMEGA'")             # 3D velocity components
   # file.write(          ",'CLOUD','CLDLIQ','CLDICE'")   # 3D cloud fields
   # file.write(          ",'QRL','QRS'")                 # 3D radiative heating profiles
   # file.write('\n')
   file.write(f' cosp_lite = .true. \n')
   file.write(" inithist = \'YEARLY\' \n") # ENDOFRUN / NONE / YEARLY
   # if 'atm_init_file' in locals(): file.write(f' ncdata = \'{atm_init_path}/{atm_init_file}\'\n')

   # # switch to 1950 compset default for prescribed aero to see if it fixes aerosol optical depth error
   # file.write(" prescribed_aero_file     = \'mam4_0.9x1.2_L72_2000clim_c170323.nc\' \n")
   # file.write(" prescribed_aero_cycle_yr = 01 \n")

   file.close()
   #----------------------------------------------------------------------------
   # ELM namelist
   nfile = 'user_nl_elm'
   file = open(nfile,'w')
   if 'land_data_file' in locals(): file.write(f' fsurdat = \'{land_data_path}/{land_data_file}\' \n')
   if 'land_init_file' in locals(): file.write(f' finidat = \'{land_init_path}/{land_init_file}\' \n')
   file.close()
   #-------------------------------------------------------
   # Set the time step parameters
   if 'MMF' in compset: dtime = 20*60
   if 'dtime' in locals(): 
      ncpl  = 86400 / dtime
      run_cmd(f'./xmlchange ATM_NCPL={ncpl},LND_NCPL={ncpl},ICE_NCPL={ncpl},OCN_NCPL={ncpl}')
   #-------------------------------------------------------
   # OCN namelist
   nfile = 'user_nl_mpaso'
   file = open(nfile,'w')
   if 'dtime' in locals():
      nminutes = int(dtime/60)
      file.write(f' config_dt = \'00:{nminutes}:00\' \n')
   file.write(f' config_am_globalstats_enable = .false. \n')
   file.write(f' config_am_timeseriesstatsmonthly_enable = .false. \n')
   file.write(f' config_am_timeseriesstatsmonthlymax_enable = .false. \n')
   file.write(f' config_am_timeseriesstatsmonthlymin_enable = .false. \n')
   file.close()
   #-------------------------------------------------------
   # ICE namelist
   nfile = 'user_nl_mpassi'
   file = open(nfile,'w')
   file.write(f' config_am_timeseriesstatsdaily_enable = false \n')
   file.write(f' config_am_timeseriesstatsmonthly_enable = false \n')
   file.close()
   #-------------------------------------------------------
   # other run-time stuff
   if 'queue'    in globals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
   if 'stop_opt' in globals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
   if 'stop_n'   in globals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
   if 'resub'    in globals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
   if 'walltime' in globals(): run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')

   if     continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=TRUE ')   
   if not continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=FALSE ')
   #----------------------------------------------------------------------------
   # Submit the run
   run_cmd('./case.submit')
#-------------------------------------------------------------------------------
# Print the case name again
print(f'\n  case : {case}\n')
#-------------------------------------------------------------------------------

