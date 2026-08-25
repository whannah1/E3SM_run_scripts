#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
''' notes on ROF mapping file
DIN_LOC_ROOT=/lustre/orion/cli115/world-shared/e3sm/inputdata
${DIN_LOC_ROOT}/lnd/clm2/mappingdata/grids/SCRIPgrid_0.5x0.5_nomask_c110308.nc


salloc --time 6:00:00 --account=cli115 --nodes=1

micromamba activate taos_env

# export SLURM_MPI_TYPE=pmix

GRID_ROOT=/global/cfs/cdirs/e3sm/2026-INCITE-CONUS-RRM/files_grid
MAP_ROOT=/global/cfs/cdirs/e3sm/2026-INCITE-CONUS-RRM/files_map

# GRID_ROOT=/lustre/orion/cli115/world-shared/e3sm/2026-INCITE-CONUS-RRM/files_grid
# MAP_ROOT=/lustre/orion/cli115/world-shared/e3sm/2026-INCITE-CONUS-RRM/files_map

LND_GRID=${GRID_ROOT}/2026-incite-conus-1024x2-pg2_scrip.cdf5.nc
ROF_GRID=${DIN_LOC_ROOT}/lnd/clm2/mappingdata/grids/MOSART_global_8th.scrip.20180211c.nc

MAP_FILE_LND2ROF=${MAP_ROOT}/map_conus1024x2v1pg2_to_r0125_traave.20260810.nc
MAP_FILE_ROF2LND=${MAP_ROOT}/map_r0125_to_conus1024x2v1pg2_traave.20260810.nc

time ncremap --mpi_nbr=128 -a traave --src_grd=${LND_GRID} --dst_grd=${ROF_GRID} --map_file=${MAP_FILE_LND2ROF}

# ncremap --mpi_nbr=8 -a esmfaave --src_grd=${LND_GRID} --dst_grd=${ROF_GRID} --map_file=${MAP_FILE_LND2ROF}

ncremap -a traave --src_grd=${LND_GRID} --dst_grd=${ROF_GRID} --map_file=${MAP_FILE_LND2ROF}
ncremap -a traave --src_grd=${ROF_GRID} --dst_grd=${LND_GRID} --map_file=${MAP_FILE_ROF2LND}

MAP_FILE_ATM2ROF_2=${MAP_ROOT}/map_conus1024x2v1pg2_to_r0125_trfv2.20260810.nc
MAP_FILE_ATM2ROF_3=${MAP_ROOT}/map_conus1024x2v1pg2_to_r0125_trbilin.20260810.nc

ncremap -a trfv2   --src_grd=${ATM_GRID} --dst_grd=${ROF_GRID} --map_file=${MAP_FILE_ATM2ROF_2}
ncremap -a trbilin --src_grd=${ATM_GRID} --dst_grd=${ROF_GRID} --map_file=${MAP_FILE_ATM2ROF_3}

/lustre/orion/cli115/world-shared/e3sm/inputdata/cpl/gridmaps/conus1024x2v1pg2
'''
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp, datetime
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'cli115'
top_dir  = os.getenv('HOME')+'/E3SM/'
src_dir  = f'{top_dir}/E3SM_SRC1/' # branch => whannah/2026-INCITE-CONUS-RRM
DIN_LOC_ROOT = '/lustre/orion/cli115/world-shared/e3sm/inputdata'

# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
continue_run = True


# stop_opt,stop_n,resub,walltime = 'ndays',1, 0,'0:30:00'
# stop_opt,stop_n,resub,walltime = 'nmonths',1, 0,'2:00:00'
# stop_opt,stop_n,resub,walltime = 'nmonths',6, 1,'12:00:00'
stop_opt,stop_n,resub,walltime = 'nyears',1, 0,'4:00:00'
# stop_opt,stop_n,resub,walltime = 'nyears',1, 10-1,'2:00'

# rest_opt,rest_n = 'nyears',1
rest_opt,rest_n = 'nmonths',1

compset   = 'IERA5ELM' # ICRUELM / IERA5ELM

grid = 'conus1024x2v1pg2_RRSwISC6to18E3r5'
num_nodes = 256
# fsurdat = f'{DIN_LOC_ROOT}/lnd/clm2/surfdata_map/surfdata_ne128pg2_simyr2010_c260116.nc'
fsurdat_root = '/lustre/orion/cli115/world-shared/e3sm/2026-INCITE-CONUS-RRM/files_land'
fsurdat_file = f'{fsurdat_root}/surfdata_2026-incite-conus-1024x2-pg2_simyr2010_c260325_updated.nc'

finidat_root = '/lustre/orion/cli115/world-shared/e3sm/2026-INCITE-CONUS-RRM/files_init'
finidat_file = f'{finidat_root}/conus1024x2v1pg2_RRSwISC6to18E3r5.elm.r.2020-01-20-00000.nc'

maps_root = '/lustre/orion/cli115/world-shared/e3sm/2026-INCITE-CONUS-RRM/files_map'
map_file_lnd2rof = f'{maps_root}/map_conus1024x2v1pg2_to_r0125_traave.20260529.nc'
# map_file_lnd2rof = 'cpl/gridmaps/conus1024x2v1pg2/map_conus1024x2v1pg2_to_r0125_traave.20260529.nc'
# map_file_lnd2rof = 'cpl/gridmaps/conus1024x2v1pg2/map_conus1024x2v1pg2_to_r0125_traave.20260810.nc'
# map_file_rof2lnd = 'cpl/gridmaps/conus1024x2v1pg2/map_r0125_to_conus1024x2v1pg2_traave.20260810.nc'

num_years = 1
stop_date = datetime.datetime(2012, 1, 1)
start_date = datetime.datetime(stop_date.year-num_years, stop_date.month, stop_date.day)
stop_date_str = stop_date.strftime("%Y-%m-%d")
start_date_str = start_date.strftime("%Y-%m-%d")

case = f'ELM_spinup.2026-INCITE-CONUS-RRM.{compset}.{grid}';         use_fineTOP = False
# case = f'ELM_spinup.2026-INCITE-CONUS-RRM.{compset}.{grid}.fineTOP'; use_fineTOP = True

#---------------------------------------------------------------------------------------------------
# rof_namelist_txt = f'''
#  &mosart_inparm
#   do_rtm = .false.
#  /
# '''
#---------------------------------------------------------------------------------------------------
def set_namelist(fsurdat_file,finidat_file):
   #----------------------------------------------------------------------------
   # file = open('user_nl_mosart','w') 
   # file.write(rof_namelist_txt) 
   # file.close()
   #----------------------------------------------------------------------------
   # file = open('user_nl_eam','w') 
   # file.write(' empty_htapes = .true. \n') 
   # file.close()
   #----------------------------------------------------------------------------
   file = open('user_nl_elm','w')
   file.write(f' fsurdat = \'{fsurdat_file}\'\n')
   if finidat_file is not None:
      file.write(f' finidat = \'{finidat_file}\'\n')
      # file.write(f' check_finidat_fsurdat_consistency=.false.')
   else:
      file.write(f' finidat = \'\'\n') # this need to be blank to force cold-start mode
   if use_fineTOP:
      file.write(f" use_finetop_rad    = .true.")
      file.write(f" use_top_solar_rad  = .false.")
   else:
      file.write(f" use_finetop_rad    = .false.")
      file.write(f" use_top_solar_rad  = .true.")
   file.write(f" hist_empty_htapes  = .true.")
   file.write(f" hist_fincl1 = 'FSDS','FSA','FSR','FIRE','Rnet','EFLX_LH_TOT','FSH'")
   # file.write(f" hist_nhtfrq = -1")
   # file.write(f" hist_mfilt  = 24")
   file.write(f" hist_nhtfrq = 0")
   file.write(f" hist_mfilt  = 1")
   file.close()
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

machine,compiler = 'frontier','craygnu-mphipcc'
case_root = f'/lustre/orion/cli115/proj-shared/hannah6/e3sm_scratch/{case}'

max_task_per_node,max_mpi_per_node,atm_nthrds  = 56,8,7
atm_ntasks = max_mpi_per_node*num_nodes
#---------------------------------------------------------------------------------------------------
if newcase:
   if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
   cmd = f'{src_dir}/cime/scripts/create_newcase --case {case} --project {acct}'
   cmd += f' --output-root {case_root} --script-root {case_root}/case_scripts'
   cmd += f' --compset {compset} --handle-preexisting-dirs u'
   # cmd += f' --res {grid}'
   cmd += f' --res ELM_USRDAT'
   cmd += f' --pecount {atm_ntasks}x{atm_nthrds} --machine={machine} --compiler={compiler} '
   run_cmd(cmd)
#---------------------------------------------------------------------------------------------------
os.chdir(f'{case_root}/case_scripts')
#---------------------------------------------------------------------------------------------------
if config:
   run_cmd(f'./xmlchange EXEROOT={case_root}/bld ')
   run_cmd(f'./xmlchange RUNDIR={case_root}/run ')
   run_cmd(f'./xmlchange MAX_MPITASKS_PER_NODE={max_mpi_per_node}')
   run_cmd(f'./xmlchange MAX_TASKS_PER_NODE={max_task_per_node}')
   # run_cmd(f'./xmlchange MAX_TASKS_PER_NODE={(max_mpi_per_node*atm_nthrds)}')
   #----------------------------------------------------------------------------
   set_namelist(fsurdat_file,finidat_file)
   #----------------------------------------------------------------------------
   # changes needed for ELM_USRDAT
   domain_root = '/lustre/orion/cli115/world-shared/e3sm/2026-INCITE-CONUS-RRM/files_domain'
   run_cmd(f'./xmlchange ATM_DOMAIN_PATH={domain_root}')
   run_cmd(f'./xmlchange LND_DOMAIN_PATH={domain_root}')
   run_cmd(f'./xmlchange ATM_DOMAIN_FILE=domain.lnd.2026-incite-conus-1024x2_RRSwISC6to18E3r5.20260610.nc')
   run_cmd(f'./xmlchange LND_DOMAIN_FILE=domain.lnd.2026-incite-conus-1024x2_RRSwISC6to18E3r5.20260610.nc')
   #----------------------------------------------------------------------------
   if 'map_file_lnd2rof' in globals(): run_cmd(f'./xmlchange --file env_run.xml LND2ROF_FMAPNAME={map_file_lnd2rof}' )
   if 'map_file_rof2lnd' in globals(): run_cmd(f'./xmlchange --file env_run.xml ROF2LND_FMAPNAME={map_file_rof2lnd}' )
   #----------------------------------------------------------------------------
   # map_file_atm2rof1 = 'cpl/gridmaps/conus1024x2v1pg2/map_conus1024x2v1pg2_to_r0125_traave.20260810.nc'
   # map_file_atm2rof2 = 'cpl/gridmaps/conus1024x2v1pg2/map_conus1024x2v1pg2_to_r0125_trfv2.20260810.nc'
   # map_file_atm2rof3 = 'cpl/gridmaps/conus1024x2v1pg2/map_conus1024x2v1pg2_to_r0125_trbilin.20260810.nc'
   # if 'map_file_atm2rof1' in globals(): run_cmd(f'./xmlchange --file env_run.xml ATM2ROF_FMAPNAME={map_file_atm2rof1}')
   # if 'map_file_atm2rof2' in globals(): run_cmd(f'./xmlchange --file env_run.xml ATM2ROF_FMAPNAME_NONLINEAR={map_file_atm2rof2}')
   # if 'map_file_atm2rof3' in globals(): run_cmd(f'./xmlchange --file env_run.xml ATM2ROF_SMAPNAME={map_file_atm2rof3}')
   #----------------------------------------------------------------------------
   if clean : run_cmd('./case.setup --clean')
   run_cmd('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
if build:
   # run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')   # enable debug mode
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
if submit:
   #----------------------------------------------------------------------------
   set_namelist(fsurdat_file,finidat_file)
   #----------------------------------------------------------------------------
   # if 'ncpl' in locals(): run_cmd(f'./xmlchange ATM_NCPL={str(ncpl)}')
   if 'queue'    in globals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
   if 'stop_opt' in globals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
   if 'stop_n'   in globals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
   if 'resub'    in globals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
   if 'walltime' in globals(): run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
   if 'rest_opt' in globals(): run_cmd(f'./xmlchange --file env_run.xml  REST_OPTION={rest_opt}')
   if 'rest_n'   in globals(): run_cmd(f'./xmlchange --file env_run.xml  REST_N={rest_n}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')
   if     continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=TRUE ')
   if not continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=FALSE ')
   #----------------------------------------------------------------------------
   # An alternate grid checking threshold is needed for ne120pg2 (still not sure why...)
   # if ne==120 and npg==2 : run_cmd('./xmlchange --file env_run.xml  EPS_AGRID=1e-11' )
   # run_cmd('./xmlchange --file env_run.xml EPS_FRAC=3e-2' ) # default=1e-2
   #----------------------------------------------------------------------------
   run_cmd('./case.submit')

#---------------------------------------------------------------------------------------------------
# Print the case name again
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n') 
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
