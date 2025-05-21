#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
import os, numpy as np, subprocess as sp, datetime, shutil
import xml.etree.ElementTree as ET
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'cli115'
case_dir = os.getenv('HOME')+'/E3SM/Cases/'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC1/' # branch => whannah/mmf/KPP

### flags to control config/build/submit sections
# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

debug_mode = False

queue = 'debug' # batch / debug

# stop_opt,stop_n,resub,walltime = 'ndays',1,0,'0:30'
stop_opt,stop_n,resub,walltime = 'nstep',10,0,'0:30'

ne,npg = 120,2; grid = f'ne{ne}pg{npg}_r0125_oRRS18to6v3'

# dtime = 15*60
# dtime = 5*60
# dtime = 1*60
# dtime = 30; crm_dt=1
# dtime = 5; crm_dt=1
# dtime = 1; crm_dt=0.2

#---------------------------------------------------------------------------------------------------
# specific case names and settings
#---------------------------------------------------------------------------------------------------
# compset,arch,num_nodes,disable_output = 'WCYCL1950-MMF1','GNUGPU',128, True   # 
# compset,arch,num_nodes,disable_output = 'WCYCL1950-MMF1','GNUCPU',128, True   # 

# compset,arch,num_nodes,disable_output = 'WCYCL1950',     'GNUCPU', 512, False # non-MMF companion case

### try specifying tasks instead of nodes
compset,arch,num_tasks,disable_output = 'WCYCL1950-MMF1','GNUGPU', 2048, False # non-MMF companion case
# compset,arch,num_tasks,disable_output = 'WCYCL1950-MMF1','GNUGPU', 1024, False # non-MMF companion case
# compset,arch,num_tasks,disable_output = 'WCYCL1950-MMF1','GNUCPU', 1024, False # non-MMF companion case
# compset,arch,num_tasks,disable_output = 'WCYCL1950',     'GNUCPU', 512, False # non-MMF companion case

use_L60 = True
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------

diff_ocn_nodes = False

case_list = ['E3SM','2022-KPP-B-v2-SPINUP',arch.replace('GNU',''),f'ne{ne}pg{npg}',compset]

if 'num_tasks' in locals(): case_list.append(f'NT_{num_tasks}')
if 'num_nodes' in locals(): case_list.append(f'NN_{num_nodes}')
# if not diff_ocn_nodes: case_list.append(f'OCN_SAME_NODES')
# if disable_output: case_list.append('NO-HIST')

if 'dtime'  in locals(): case_list.append(f'GDT_{dtime}')
if 'crm_dt' in locals(): case_list.append(f'CDT_{crm_dt}')

if 'MMF' not in compset and use_L60: case_list.append(f'L60')

if debug_mode: case_list.append('debug')

timestamp = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')
# timestamp = '20221024150747'
# timestamp = '20221026175003'
# timestamp = '20221027162620'
# timestamp = '20221031170841'
# timestamp = '20221031181816'
timestamp = '20221031190227'
case_list.append(timestamp)

case = '.'.join(case_list)

# exit(case)

#---------------------------------------------------------------------------------------------------
# land initial condition and surface data files
if 'r0125' in grid:
   lnd_data_path = '/gpfs/alpine/cli115/world-shared/e3sm/inputdata/lnd/clm2/surfdata_map'
   lnd_data_file = 'surfdata_0.125x0.125_simyr1950_c210924.nc'
   # lnd_data_file = 'surfdata_0.125x0.125_simyr2000_c190730.nc'
   lnd_init_path = '/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/init_files'
   # lnd_init_file = 'ELM_spinup.ICRUELM.r0125_r0125_oRRS18to6v3.20-yr.2010-01-01.elm.r.2010-01-01-00000.nc'
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print(f'\n  case : {case}\n')

num_dyn = ne*ne*6

max_task_per_node = 42
# if 'CPU' in arch : max_mpi_per_node,atm_nthrds  = 42,1
if 'CPU' in arch : max_mpi_per_node,atm_nthrds  = 6,7
if 'GPU' in arch : max_mpi_per_node,atm_nthrds  = 6,7


if 'num_nodes' in locals():
   task_per_node = max_mpi_per_node
   atm_ntasks = task_per_node*num_nodes

   if arch=='GNUGPU':
      if num_nodes> 512:ocn_ntasks,ice_ntasks,cpl_ntasks,rof_ntasks = 4096,4096,atm_ntasks,atm_ntasks
      if num_nodes==512:ocn_ntasks,ice_ntasks,cpl_ntasks,rof_ntasks = 2048,2048,atm_ntasks,atm_ntasks
      if num_nodes==256:ocn_ntasks,ice_ntasks,cpl_ntasks,rof_ntasks = 1024,1024,atm_ntasks,atm_ntasks
      # if num_nodes==128:ocn_ntasks,ice_ntasks,cpl_ntasks,rof_ntasks =  512, 512,atm_ntasks,atm_ntasks
      # if num_nodes==128:ocn_ntasks,ice_ntasks,cpl_ntasks,rof_ntasks =  512, 512,atm_ntasks,atm_ntasks; rootpe_ice,rootpe_lnd=0,ice_ntasks
      if num_nodes==128:diff_ocn_nodes=False;ocn_ntasks,ice_ntasks =  256, 640; rootpe_ice,rootpe_lnd=0,0
      # if num_nodes==128:diff_ocn_nodes=True;ocn_ntasks,ice_ntasks=1024,512; rootpe_ice,rootpe_lnd=0,ice_ntasks
   if arch=='GNUCPU':
      # if num_nodes> 512:
      if num_nodes==512:ocn_ntasks,ice_ntasks,cpl_ntasks,rof_ntasks = atm_ntasks,atm_ntasks,atm_ntasks,atm_ntasks; lnd_ntasks=atm_ntasks; rootpe_ice=0
      # if num_nodes==512:ocn_ntasks,ice_ntasks,cpl_ntasks,rof_ntasks = 4096,8192,atm_ntasks,atm_ntasks
      # if num_nodes==256:ocn_ntasks,ice_ntasks,cpl_ntasks,rof_ntasks = 4096,8192,atm_ntasks,atm_ntasks
      # if num_nodes==256:ocn_ntasks,ice_ntasks,cpl_ntasks,rof_ntasks = 4096,4096,atm_ntasks,atm_ntasks
      if num_nodes==256:ocn_ntasks,ice_ntasks,cpl_ntasks,rof_ntasks = 4096,4096,atm_ntasks,atm_ntasks; lnd_ntasks=4096; rootpe_ice=0
      if num_nodes==128:ocn_ntasks,ice_ntasks,cpl_ntasks,rof_ntasks = 2048,4096,atm_ntasks,atm_ntasks

   if 'cpl_ntasks' not in locals(): cpl_ntasks = atm_ntasks
   if 'rof_ntasks' not in locals(): rof_ntasks = atm_ntasks

   if 'lnd_ntasks' not in locals(): lnd_ntasks = atm_ntasks-ice_ntasks
   if lnd_ntasks<=0: lnd_ntasks = atm_ntasks

   # always default to ice on different root PE so it runs in parallel with land
   if 'rootpe_ice' not in locals(): rootpe_ice = lnd_ntasks

   total_ntasks, total_nthrds = atm_ntasks, atm_nthrds
   # if diff_ocn_nodes: total_ntasks = total_ntasks + ocn_ntasks

if 'num_tasks' in locals():
   task_per_node = max_mpi_per_node
   atm_ntasks = num_tasks
   lnd_ntasks = num_tasks
   ocn_ntasks = num_tasks
   ice_ntasks = num_tasks
   cpl_ntasks = num_tasks
   rof_ntasks = num_tasks
   rootpe_ice = 0
   total_ntasks, total_nthrds = atm_ntasks, atm_nthrds

#---------------------------------------------------------------------------------------------------
if newcase :
   if os.path.isdir(f'{case_dir}/{case}'): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
   #-------------------------------------------------------
   cmd = f'{src_dir}/cime/scripts/create_newcase -case {case_dir}/{case} '
   cmd = cmd + f' -mach summit  -compset {compset} -res {grid}'
   if arch=='GNUCPU' : cmd += f' -compiler gnu    -pecount {total_ntasks}x{total_nthrds} '
   if arch=='GNUGPU' : cmd += f' -compiler gnugpu -pecount {total_ntasks}x{total_nthrds} '
   run_cmd(cmd)
os.chdir(f'{case_dir}/{case}/')
#---------------------------------------------------------------------------------------------------
if config : 
   if 'MMF' in compset:
      
      if 'crm_dt' in locals(): run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_dt {crm_dt} \" ')

   else:

      if use_L60:
         run_cmd(f'./xmlchange --append -id CAM_CONFIG_OPTS -val \" -nlev 60 \" ')

   #-------------------------------------------------------
   # Set tasks for each component
   run_cmd(f'./xmlchange --file env_mach_pes.xml NTASKS_CPL={cpl_ntasks}')
   run_cmd(f'./xmlchange --file env_mach_pes.xml NTASKS_LND={lnd_ntasks}')
   run_cmd(f'./xmlchange --file env_mach_pes.xml NTASKS_OCN={ocn_ntasks}')
   run_cmd(f'./xmlchange --file env_mach_pes.xml NTASKS_ICE={ice_ntasks}')
   run_cmd(f'./xmlchange --file env_mach_pes.xml NTASKS_ROF={rof_ntasks}')

   run_cmd(f'./xmlchange --file env_mach_pes.xml ROOTPE_ICE={rootpe_ice}')
   if 'rootpe_lnd' in locals(): run_cmd(f'./xmlchange --file env_mach_pes.xml ROOTPE_LND={rootpe_lnd}')
   #-------------------------------------------------------
   # set root PE for putting ocean/ice on separate nodes
   if diff_ocn_nodes: run_cmd(f'./xmlchange --file env_mach_pes.xml ROOTPE_OCN={atm_ntasks}')
   #-------------------------------------------------------
   # 64_data format is needed for large output (i.e. high-res grids or CRM data)
   run_cmd('./xmlchange PIO_NETCDF_FORMAT=\"64bit_data\" ')
   #-------------------------------------------------------
   if clean : run_cmd('./case.setup --clean')
   run_cmd('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
if build : 
   #-------------------------------------------------------
   # use alternate ocean/ice initial condition
   #-------------------------------------------------------
   # rundir = f'/gpfs/alpine/cli115/proj-shared/hannah6/e3sm_scratch/{case}/run'

   # ocn_init_path = '/gpfs/alpine/scratch/hannah6/cli115/e3sm_scratch/init_files/v1.HR.piControl.advection-bug-fix'
   # ocn_init_file = 'mpaso.rst.0089-03-01_00000.nc'
   # ice_init_file = 'mpascice.rst.0089-03-01_00000.nc'

   # # Make sure NCO commands are available
   # if shutil.which('ncks') is None: 
   #    exec(open('/sw/summit/lmod/lmod/init/env_modules_python.py').read())
   #    module('load','nco')
   # if shutil.which('ncks') is None: raise OSError(f'ncks is not in system path! (you need to use "module load nco")')
   
   # # copy over on/ice initial condition files
   # if 'ocn_init_file' in locals() and not os.path.isfile(f'{rundir}/{ocn_init_file}'):
   #    run_cmd(f'ncks -x -v xtime {ocn_init_path}/{ocn_init_file} {rundir}/{ocn_init_file}')
   # if 'ice_init_file' in locals() and not os.path.isfile(f'{rundir}/{ice_init_file}'): 
   #    run_cmd(f'ncks -x -v xtime {ocn_init_path}/{ice_init_file} {rundir}/{ice_init_file}')

   # # copy the ocn/ice streams files to the SourceMods folder
   # run_cmd(f'cp {rundir}/streams.ocean  {case_dir}/{case}/SourceMods/src.mpaso/')
   # run_cmd(f'cp {rundir}/streams.seaice {case_dir}/{case}/SourceMods/src.mpassi/')
   # ocn_streams_file = f'{case_dir}/{case}/SourceMods/src.mpaso/streams.ocean'
   # ice_streams_file = f'{case_dir}/{case}/SourceMods/src.mpassi/streams.seaice'

   # # Edit OCN streams to specify alternate initial condition
   # tree = ET.parse(ocn_streams_file)
   # root = tree.getroot()
   # for stream in root.iter('immutable_stream'):
   #    if stream.get('name')=='mesh' : stream.set('filename_template',f'{rundir}/{ocn_init_file}')
   #    if stream.get('name')=='input': stream.set('filename_template',f'{rundir}/{ocn_init_file}')
   # tree.write(ocn_streams_file)


   # # Edit ICE streams to specify alternate initial condition
   # tree = ET.parse(ice_streams_file)
   # root = tree.getroot()
   # for stream in root.iter('immutable_stream'):
   #    if stream.get('name')=='restart_ic':
   #       stream.set('filename_template',f'{rundir}/{ice_init_file}')
   # tree.write(ice_streams_file)
   
   #-------------------------------------------------------
   # check if debug mode is already set before setting to avoid error when rebuilding a debug case
   if debug_mode: 
      (debug_flag, err) = sp.Popen('./xmlquery DEBUG --value', stdout=sp.PIPE, shell=True, \
                                   universal_newlines=True).communicate()
      if debug_flag=='FALSE': run_cmd('./xmlchange DEBUG=TRUE ')
      run_cmd('./xmlchange --append --id CAM_CONFIG_OPTS --val \" -cppdefs \' -DPIO_ENABLE_LOGGING=OFF \'  \"')
   #-------------------------------------------------------
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
if submit : 
   #-------------------------------------------------------
   # Namelist options
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   #------------------------------
   # Specify history output frequency and variables
   if not disable_output:
      file.write(' nhtfrq    = 0,-1,-24 \n') 
      file.write(' mfilt     = 1, 24,1 \n') # 1-day files
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
      file.write(             ",'T','Q','Z3'")                # 3D thermodynamic budget components
      file.write(             ",'U','V','OMEGA'")             # 3D velocity components
      file.write(             ",'CLOUD','CLDLIQ','CLDICE'")   # 3D cloud fields
      file.write(             ",'QRL','QRS'")                 # 3D radiative heating 
      file.write(             ",'QRLC','QRSC'")               # 3D clearsky radiative heating 
      file.write('\n')
   #------------------------------
   # Other namelist stuff
   # file.write(f' crm_accel_factor = 3 \n')         # CRM acceleration factor (default is 2)
   # file.write(" inithist = \'NONE\' \n") # ENDOFRUN / NONE
   # file.write(f' do_tms = .false. \n')
   file.write(f' use_hetfrz_classnuc = .false.\n ') 

   if 'MMF' not in compset and use_L60: 
      file.write(f' ncdata = \'/gpfs/alpine/cli115/world-shared/e3sm/inputdata/atm/cam/inic/homme/eam_i_mam3_Linoz_ne120np4_L60_c20210917.nc\' \n') 
      

   if 'dtime' in locals():
      if dtime < 60 :
         file.write(f'use_crm_accel = .false. \n')
         # file.write(f'dt_tracer_factor = 1 \n')
         # file.write(f'dt_remap_factor = 1 \n')
         # file.write(f'se_tstep = {dtime} \n')
         # file.write(f'hypervis_subcycle_q = 1 \n')
      if dtime == 5 :
         file.write(f'dt_tracer_factor = 5 \n')
         file.write(f'dt_remap_factor = 5 \n')
         file.write(f'se_tstep = 1 \n')
         file.write(f'hypervis_subcycle_q = 5 \n')
      if dtime == 30 :
         file.write(f'dt_tracer_factor = 6 \n')
         file.write(f'dt_remap_factor = 6 \n')
         file.write(f'se_tstep = 5 \n')
         file.write(f'hypervis_subcycle_q = 6 \n')
      if dtime == 60 :
         file.write(f'dt_tracer_factor = 1 \n')
         file.write(f'dt_remap_factor = 1 \n')
         file.write(f'se_tstep = 60 \n')
         file.write(f'hypervis_subcycle_q = 1 \n')
      if dtime == 5*60 :
         file.write(f'dt_tracer_factor = 5 \n')
         file.write(f'dt_remap_factor = 1 \n')
         file.write(f'se_tstep = 60 \n')
         file.write(f'hypervis_subcycle_q = 5 \n')
      if dtime == 10*60 :
         file.write(f'dt_tracer_factor = 5 \n')
         file.write(f'dt_remap_factor = 1 \n')
         file.write(f'se_tstep = 60 \n')
         file.write(f'hypervis_subcycle_q = 5 \n')

   file.close()
   #-------------------------------------------------------
   # ELM namelist
   if 'lnd_init_file' in locals() or 'lnd_data_file' in locals():
      nfile = 'user_nl_elm'
      file = open(nfile,'w')
      if 'lnd_data_file' in locals(): file.write(f' fsurdat = \'{lnd_data_path}/{lnd_data_file}\' \n')
      if 'lnd_init_file' in locals(): file.write(f' finidat = \'{lnd_init_path}/{lnd_init_file}\' \n')
      file.close()
   #-------------------------------------------------------
   file = open('user_nl_mpassi','w')
   file.write(f'config_reuse_halo_exch = true\n')
   if 'dtime' in locals(): file.write(f'config_dt = {dtime}\n')
   file.write(f'config_am_regionalstatistics_enable = false\n')
   file.write(f'config_am_timeseriesstatsdaily_enable = false\n')
   # file.write('config_initial_condition_type = \'restart\'\n')
   # file.write('config_nSnowLayers = 1\n') # use 5 for default IC
   file.close()
   #-------------------------------------------------------
   # make sure the time step is consistent
   if 'dtime' in locals():
      ncpl = int( 86400 / dtime )
      run_cmd(f'./xmlchange ATM_NCPL={ncpl},LND_NCPL={ncpl},ICE_NCPL={ncpl},OCN_NCPL={ncpl}')
   #-------------------------------------------------------
   file = open('user_nl_mpaso','w')
   file.write(f'config_am_timeseriesstatsdaily_write_on_startup = .true.\n')
   if 'dtime' in locals():
      if dtime<60:
         nminutes,nseconds = '00',int(dtime)
      else:
         nminutes,nseconds = int(dtime/60),'00'
      file.write(f' config_dt = \'00:{nminutes}:{nseconds}\' \n')
      # file.write(f' config_btr_dt = \'0000_00:{nminutes}:{nseconds}\' \n')
      # file.write(f' config_btr_dt = \'0000_00:00:12\' \n')
      file.write(f' config_btr_dt = \'0000_00:00:01\' \n')
   file.close()
   #-------------------------------------------------------
   run_cmd(f'./xmlchange STOP_OPTION={stop_opt},STOP_N={stop_n},RESUBMIT={resub}')
   run_cmd(f'./xmlchange JOB_QUEUE={queue},JOB_WALLCLOCK_TIME={walltime}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')
   continue_flag = 'TRUE' if continue_run else 'False'
   run_cmd(f'./xmlchange --file env_run.xml CONTINUE_RUN={continue_flag} ')   
   #-------------------------------------------------------
   run_cmd('./case.submit')
#---------------------------------------------------------------------------------------------------
# Print the case name again
print(f'\n  case : {case}\n')
#---------------------------------------------------------------------------------------------------
