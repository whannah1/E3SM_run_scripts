#!/usr/bin/env python

## commands for creating ROF map files
# ncremap -a tempest --src_grd=$HOME/Tempest/files_exodus/ne4pg2.g   --dst_grd=/project/projectdirs/e3sm/inputdata/lnd/clm2/mappingdata/grids/SCRIPgrid_0.5x0.5_nomask_c110308.nc --map_file=$SCRATCH/e3sm_scratch/init_files//map_ne4pg2_to_r05_mono.20210817.nc   --wgt_opt='--in_type fv --in_np 1 --out_type fv --out_np 1 --out_format Classic --mono --correct_areas'
# ncremap -a tempest --src_grd=$HOME/Tempest/files_exodus/ne30pg2.g  --dst_grd=/project/projectdirs/e3sm/inputdata/lnd/clm2/mappingdata/grids/SCRIPgrid_0.5x0.5_nomask_c110308.nc --map_file=$SCRATCH/e3sm_scratch/init_files//map_ne30pg2_to_r05_mono.20210817.nc  --wgt_opt='--in_type fv --in_np 1 --out_type fv --out_np 1 --out_format Classic --mono --correct_areas'
# ncremap -a tempest --src_grd=$HOME/Tempest/files_exodus/ne45pg2.g  --dst_grd=/project/projectdirs/e3sm/inputdata/lnd/clm2/mappingdata/grids/SCRIPgrid_0.5x0.5_nomask_c110308.nc --map_file=$SCRATCH/e3sm_scratch/init_files//map_ne45pg2_to_r05_mono.20210817.nc  --wgt_opt='--in_type fv --in_np 1 --out_type fv --out_np 1 --out_format Classic --mono --correct_areas'
# ncremap -a tempest --src_grd=$HOME/Tempest/files_exodus/ne120pg2.g --dst_grd=/project/projectdirs/e3sm/inputdata/lnd/clm2/mappingdata/grids/SCRIPgrid_0.5x0.5_nomask_c110308.nc --map_file=$SCRATCH/e3sm_scratch/init_files//map_ne120pg2_to_r05_mono.20210817.nc --wgt_opt='--in_type fv --in_np 1 --out_type fv --out_np 1 --out_format Classic --mono --correct_areas'

# ncremap -a tempest --src_grd=/project/projectdirs/e3sm/inputdata/lnd/clm2/mappingdata/grids/SCRIPgrid_0.5x0.5_nomask_c110308.nc --dst_grd=$HOME/Tempest/files_exodus/ne4pg2.g   --map_file=$SCRATCH/e3sm_scratch/init_files//map_r05_to_ne4pg2_mono.20210817.nc   --wgt_opt='--in_type fv --in_np 1 --out_type fv --out_np 1 --out_format Classic --mono --correct_areas'
# ncremap -a tempest --src_grd=/project/projectdirs/e3sm/inputdata/lnd/clm2/mappingdata/grids/SCRIPgrid_0.5x0.5_nomask_c110308.nc --dst_grd=$HOME/Tempest/files_exodus/ne30pg2.g  --map_file=$SCRATCH/e3sm_scratch/init_files//map_r05_to_ne30pg2_mono.20210817.nc  --wgt_opt='--in_type fv --in_np 1 --out_type fv --out_np 1 --out_format Classic --mono --correct_areas'
# ncremap -a tempest --src_grd=/project/projectdirs/e3sm/inputdata/lnd/clm2/mappingdata/grids/SCRIPgrid_0.5x0.5_nomask_c110308.nc --dst_grd=$HOME/Tempest/files_exodus/ne45pg2.g  --map_file=$SCRATCH/e3sm_scratch/init_files//map_r05_to_ne45pg2_mono.20210817.nc  --wgt_opt='--in_type fv --in_np 1 --out_type fv --out_np 1 --out_format Classic --mono --correct_areas'
# ncremap -a tempest --src_grd=/project/projectdirs/e3sm/inputdata/lnd/clm2/mappingdata/grids/SCRIPgrid_0.5x0.5_nomask_c110308.nc --dst_grd=$HOME/Tempest/files_exodus/ne120pg2.g --map_file=$SCRATCH/e3sm_scratch/init_files//map_r05_to_ne120pg2_mono.20210817.nc --wgt_opt='--in_type fv --in_np 1 --out_type fv --out_np 1 --out_format Classic --mono --correct_areas'
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
import os
import subprocess as sp
import datetime
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'm4310'    # m3312 / m3305 / m4310

src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC2' # branch => whannah/scidac-2024 (master @ Jul 25)

#clean        = True
#newcase      = True
#config       = True
#build        = True
submit       = True
continue_run = True

disable_bfb = True 


queue = 'regular'  # regular / debug 

# stop_opt,stop_n,resub,walltime = 'nyears',5, 4-1,'4:00:00'
# stop_opt,stop_n,resub,walltime = 'nyears',6, 4-1,'8:00:00'
# stop_opt,stop_n,resub,walltime = 'nyears',6,2-1,'8:00:00'
stop_opt,stop_n,resub,walltime = 'nyears',1,0,'4:00:00'
#walltime = '8:00:00'


compset      = 'ICRUELM-SP' 
compset_long = '2000_DATM%CRU_ELM%SPBCTOP_SICE_SOCN_SROF_SGLC_SWAV'

rest_opt,rest_n = 'nmonths',3

grid = 'ne30pg2_r05_IcoswISC30E3r5'


num_years = 44 # overall years for spin-up
stop_date = datetime.datetime(2024, 1, 1)
start_date = datetime.datetime(stop_date.year-num_years, stop_date.month, stop_date.day)
stop_date_str = stop_date.strftime("%Y-%m-%d")
start_date_str = start_date.strftime("%Y-%m-%d")

# case = f'ELM_spinup.{compset}.{grid}.{num_years}-yr.{stop_date_str}'
case = f'ELM_spinup.2024-SCIDAC.{compset}.{grid}.{num_years}-yr.{stop_date_str}'

# clm_opt = None
# clm_opt = '-bgc bgc -nutrient cnp -nutrient_comp_pathway rd  -soil_decomp ctc -methane -solar_rad_scheme top'
clm_opt = ' -bgc sp -solar_rad_scheme top'

finidat_path = '/global/cfs/cdirs/m4310/data/sims/init_files/v3.LR.amip_0101/archive/rest/1980-01-01-00000/v3.LR.amip_0101.elm.r.1980-01-01-00000.nc'
fsurdat_path = '/global/cfs/cdirs/e3sm/inputdata/lnd/clm2/surfdata_map/surfdata_0.5x0.5_simyr1850_c200609_with_TOP.nc'

#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')
#---------------------------------------------------------------------------------------------------
num_nodes = 22

max_mpi_per_node,nthrds  = 128,1 ; max_task_per_node = 128
ntasks = max_mpi_per_node*num_nodes

case_root = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/{case}'
#---------------------------------------------------------------------------------------------------
def write_namelist():
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   file.write(' empty_htapes = .true. \n') 
   
   nfile = 'user_nl_elm'
   file = open(nfile,'w')
   if 'finidat_path' in locals(): file.write(f' finidat = \'{finidat_path}\' \n')
   if 'fsurdat_path' in locals(): file.write(f' fsurdat = \'{fsurdat_path}\' \n')
   # file.write(f' check_finidat_fsurdat_consistency = .false. \n')
   file.close()
#---------------------------------------------------------------------------------------------------
if newcase:
   # Check if directory already exists   
   if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
   cmd = f'{src_dir}/cime/scripts/create_newcase'
   cmd += f' --case {case}'
   cmd += f' --output-root {case_root} '
   cmd += f' --script-root {case_root}/case_scripts '
   cmd += f' --handle-preexisting-dirs u '
   if compset_long is not None:
      cmd += f' --compset {compset_long}'
   else:
      cmd += f' --compset {compset}'
   cmd += f' --res {grid} '
   cmd += f' -mach pm-cpu -compiler gnu    -pecount {ntasks}x{nthrds} '
   cmd += f' --project {acct} '
   run_cmd(cmd)
#---------------------------------------------------------------------------------------------------
os.chdir(f'{case_root}/case_scripts')
#---------------------------------------------------------------------------------------------------
if config:
   write_namelist()
   run_cmd(f'./xmlchange --file env_run.xml   RUN_STARTDATE={start_date_str}' )
   #-------------------------------------------------------
   # run_cmd('./xmlchange --file env_run.xml   RUNDIR=\'$CIME_OUTPUT_ROOT/$CASE/run\' ' )
   run_cmd(f'./xmlchange EXEROOT={case_root}/bld ')
   run_cmd(f'./xmlchange RUNDIR={case_root}/run ')
   #-------------------------------------------------------
   run_cmd(f'./xmlchange MAX_TASKS_PER_NODE={max_task_per_node} ')
   run_cmd(f'./xmlchange MAX_MPITASKS_PER_NODE={max_mpi_per_node} ')
   #----------------------------------------------------------------------------
   if clm_opt is not None:
      run_cmd(f'./xmlchange --append --file env_run.xml --id ELM_BLDNML_OPTS --val \"{clm_opt}\"' )
   #----------------------------------------------------------------------------
   run_cmd('./case.setup --reset')
#---------------------------------------------------------------------------------------------------
if build : 
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
if submit : 
   #----------------------------------------------------------------------------
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   file.write(' empty_htapes = .true. \n') 
   
   nfile = 'user_nl_elm'
   file = open(nfile,'w')
   file.write(f' fsurdat = \'{fsurdat_path}\' \n')
   file.close()
   #----------------------------------------------------------------------------
   # Restart Frequency
   if 'rest_opt' in locals(): run_cmd(f'./xmlchange --file env_run.xml  REST_OPTION={rest_opt}')
   if 'rest_n'   in locals(): run_cmd(f'./xmlchange --file env_run.xml  REST_N={rest_n}')
   #----------------------------------------------------------------------------
   if 'queue'    in globals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
   if 'walltime' in globals(): run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
   if 'stop_opt' in globals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
   if 'stop_n'   in globals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
   # if 'resub' in globals() and not continue_run: run_cmd(f'./xmlchange RESUBMIT={resub}')
   # if 'resub' in globals() and reset_resub: run_cmd(f'./xmlchange RESUBMIT={resub}')
   if 'resub' in globals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
   run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')
   #----------------------------------------------------------------------------
   if     continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=TRUE ')   
   if not continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=FALSE ')
   #-------------------------------------------------------
   if     disable_bfb: run_cmd('./xmlchange BFBFLAG=FALSE')
   if not disable_bfb: run_cmd('./xmlchange BFBFLAG=TRUE')
   #----------------------------------------------------------------------------
   run_cmd('./case.submit')
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n') 
#---------------------------------------------------------------------------------------------------
