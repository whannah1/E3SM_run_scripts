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

# directory info
case_dir = os.getenv('HOME')+'/E3SM/Cases'
# src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC0' # master as of 2023-01-19
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC2' # branch => whannah/scidac-2024 (master @ Jul 25)
# src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC4' # branch => master @ Aug 7 w/ v3atm/eam/master_MAM5_wetaero_chemdyg
# src_dir  = '/global/cscratch1/sd/whannah/e3sm_scratch/SCREAM_SRC'
# src_dir  = '/global/cfs/projectdirs/m3312/whannah/SCREAM_SRC'
# /global/cfs/projectdirs/m3312/whannah/SCREAM_SRC/components/elm/cime_config/config_compsets.xml

#clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
continue_run = True 

disable_bfb = True

queue = 'regular'  # regular / debug 

# stop_opt,stop_n,resub,walltime = 'ndays',32,0,'4:00:00'
# stop_opt,stop_n,resub,walltime = 'nyears',5, 4-1,'4:00:00'
# stop_opt,stop_n,resub,walltime = 'nyears',1, 10-1,'4:00:00'
# stop_opt,stop_n,resub,walltime = 'ndays',73, 5*10-1,'2:00:00'
# stop_opt,stop_n,resub,walltime = 'nyears',2,10-1,'4:00:00' # for ne120
# if queue=='debug'  : stop_opt,stop_n,resub,walltime = 'ndays',1, 0,'0:10:00'


walltime = '6:00:00'

compset   = 'ICRUELM' 

# ne,npg =   4,2
# ne,npg =  16,2
ne,npg =  30,2
# ne,npg =  45,2
# ne,npg = 120,2
# ne,npg = 256,2

# rest_opt,rest_n = 'nyears',1
rest_opt,rest_n = 'nmonths',3

# res = f'ne{ne}' if npg==0 else  f'ne{ne}pg{npg}'
# grid = f'{res}_EC30to60E2r2'
# grid = f'{res}_r05_oECv3'
# grid = f'{res}_oECv3'
# if ne==4: grid = f'{res}_r05_oQU480'
# grid = f'{res}_{res}'
grid = 'ne30pg2_r05_IcoswISC30E3r5'


num_years = 44 # overall years for spin-up
stop_date = datetime.datetime(2024, 1, 1)
start_date = datetime.datetime(stop_date.year-num_years, stop_date.month, stop_date.day)
stop_date_str = stop_date.strftime("%Y-%m-%d")
start_date_str = start_date.strftime("%Y-%m-%d")

case = f'ELM_spinup.{compset}.{grid}.{num_years}-yr.{stop_date_str}'
# case = f'ELM_spinup.SCREAM.{compset}.{grid}.{num_years}-yr.{stop_date_str}'

# exit(case)

# clm_opt = ' -bgc sp -clm_start_type arb_ic'
clm_opt = '-bgc bgc -nutrient cnp -nutrient_comp_pathway rd  -soil_decomp ctc -methane -solar_rad_scheme top'


finidat_path = '/global/cfs/cdirs/m4310/data/sims/init_files/v3.LR.amip_0101/archive/rest/1980-01-01-00000/v3.LR.amip_0101.elm.r.1980-01-01-00000.nc'
fsurdat_path = '/global/cfs/cdirs/e3sm/inputdata/lnd/clm2/surfdata_map/surfdata_0.5x0.5_simyr1850_c200609_with_TOP.nc'

# fsurdat_path = '/global/cfs/cdirs/e3sm/inputdata/lnd/clm2/surfdata_map/surfdata_ne30pg2_simyr2000_c210402.nc'
# fsurdat_path = '/global/cfs/cdirs/e3sm/inputdata/lnd/clm2/surfdata_map/surfdata_ne30pg2_simyr2010_c210402.nc'
# fsurdat_path = '/global/cfs/cdirs/m3312/whannah/init_files/surfdata_ne16pg2_2010.nc'
# fsurdat_path = '/pscratch/sd/w/whannah/e3sm_scratch/init_scratch/surfdata_ne16pg2_simyr2010_c230130.nc'

# fsurdat_path = '/global/cfs/cdirs/e3sm/inputdata/lnd/clm2/surfdata_map/surfdata_ne256pg2_simyr2010_c230207.nc'

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

# if ne==30 : dtime = 30*60
# if ne==120 : dtime = 5*60
# ncpl = 86400 / dtime
#---------------------------------------------------------------------------------------------------
# Create new case
#---------------------------------------------------------------------------------------------------
if newcase : 
   if os.path.isdir(f'{case_dir}/{case}'): exit('\n'+clr.RED+'This case already exists!'+clr.END+'\n')
   
   cmd = f'{src_dir}/cime/scripts/create_newcase --case {case_dir}/{case}'
   cmd += f' --compset {compset}'
   cmd += f' --res {grid}'
   run_cmd(cmd)

   # Change run directory to be next to bld directory
   os.chdir(f'{case_dir}/{case}')
   run_cmd('./xmlchange --file env_run.xml   RUNDIR=\'$CIME_OUTPUT_ROOT/$CASE/run\' ' )
   run_cmd(f'./xmlchange --file env_run.xml   RUN_STARTDATE={start_date_str}' )

   # if grid == 'ne30pg2_ne30pg2':
   #    map_file_lnd2rof = 'cpl/gridmaps/ne30pg2/map_ne30pg2_to_r05_mono.200220.nc'
   #    map_file_rof2lnd = 'cpl/gridmaps/ne30pg2/map_r05_to_ne30pg2_mono.200220.nc'

   # map_file_lnd2rof = f'/global/cscratch1/sd/whannah/e3sm_scratch/init_files//map_ne{ne}pg{npg}_to_r05_mono.20210817.nc'
   # map_file_rof2lnd = f'/global/cscratch1/sd/whannah/e3sm_scratch/init_files//map_r05_to_ne{ne}pg{npg}_mono.20210817.nc'
   
   # run_cmd(f'./xmlchange --file env_run.xml LND2ROF_FMAPNAME={map_file_lnd2rof}' )
   # run_cmd(f'./xmlchange --file env_run.xml ROF2LND_FMAPNAME={map_file_rof2lnd}' )
   
  
   # Change inputdata from default due to permissions issue
   #run_cmd('./xmlchange --file env_run.xml  DIN_LOC_ROOT=/gpfs/alpine/scratch/jlee1046/cli115/inputdata ')
   #-------------------------------------------------------
   # Namelist options
   #-------------------------------------------------------
   nfile = ''
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
# Configure
#---------------------------------------------------------------------------------------------------
os.chdir(f'{case_dir}/{case}')
if config : 
   #----------------------------------------------------------------------------
   #----------------------------------------------------------------------------   
   #run_cmd('./xmlchange --file env_build.xml --id MOSART_MODE --val NULL')
   run_cmd('./xmlchange --append --file env_run.xml --id ELM_BLDNML_OPTS  --val  \"'+clm_opt+'\"' )

   if '_r05_' in grid: 
      run_cmd(f'./xmlchange --file env_mach_pes.xml --id NTASKS_LND --val 1350 ')
      # run_cmd(f'./xmlchange --file env_mach_pes.xml --id NTASKS_ATM --val 1350 ')
      # run_cmd(f'./xmlchange --file env_mach_pes.xml --id NTASKS_ATM --val 1350 ')
      # run_cmd(f'./xmlchange --file env_mach_pes.xml --id NTASKS_ATM --val 1350 ')
      # run_cmd(f'./xmlchange --file env_mach_pes.xml --id NTASKS_ATM --val 1350 ')
   if 'ne16pg2' in grid:         run_cmd(f'./xmlchange NTASKS_LND=384 ')
   if grid=='ne256pg2_ne256pg2': run_cmd(f'./xmlchange NTASKS_LND=3200 ')
   
   # if clean : run_cmd('./case.setup --clean')
   run_cmd('./case.setup --reset')

#---------------------------------------------------------------------------------------------------
# Build
#---------------------------------------------------------------------------------------------------
if build : 
   # run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')   # enable debug mode
   if clean : run_cmd('./case.build --clean')
   run_cmd('./case.build')
#---------------------------------------------------------------------------------------------------
# Write the namelist options and submit the run
#---------------------------------------------------------------------------------------------------
if submit : 
   
   def xml_check_and_set(file_name,var_name,value):
      if var_name in open(file_name).read(): 
         run_cmd('./xmlchange --file '+file_name+' '+var_name+'='+str(value) )
   #-------------------------------------------------------
   # Namelist options
   #-------------------------------------------------------
   nfile = ''
   nfile = 'user_nl_eam'
   file = open(nfile,'w') 
   file.write(' empty_htapes = .true. \n') 
   
   nfile = 'user_nl_elm'
   file = open(nfile,'w')
   file.write(f' fsurdat = \'{fsurdat_path}\' \n')
   file.close()
   #-------------------------------------------------------
   # Restart Frequency
   if 'rest_opt' in globals(): run_cmd(f'./xmlchange --file env_run.xml  REST_OPTION={rest_opt}')
   if 'rest_n'   in globals(): run_cmd(f'./xmlchange --file env_run.xml  REST_N={rest_n}')

   xml_check_and_set('env_workflow.xml','CHARGE_ACCOUNT',acct)
   xml_check_and_set('env_workflow.xml','PROJECT',acct)

   # An alternate grid checking threshold is needed for ne120pg2 (still not sure why...)
   # if ne==120 and npg==2 : run_cmd('./xmlchange --file env_run.xml  EPS_AGRID=1e-11' )
   # run_cmd('./xmlchange --file env_run.xml EPS_FRAC=3e-2' ) # default=1e-2
   #-------------------------------------------------------
   if 'queue'    in globals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
   if 'walltime' in globals(): run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
   if 'stop_opt' in globals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
   if 'stop_n'   in globals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
   if 'resub'    in globals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
   #-------------------------------------------------------
   if     continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=TRUE ')   
   if not continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=FALSE ')
   #-------------------------------------------------------
   if     disable_bfb: run_cmd('./xmlchange BFBFLAG=FALSE')
   if not disable_bfb: run_cmd('./xmlchange BFBFLAG=TRUE')
   #-------------------------------------------------------
   # Submit the run
   #-------------------------------------------------------
   run_cmd('./case.submit')

#---------------------------------------------------------------------------------------------------
# Print the case name again
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n') 
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
