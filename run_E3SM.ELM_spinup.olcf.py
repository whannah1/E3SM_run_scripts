#!/usr/bin/env python3

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
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp, datetime
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'cli115' # cli115 / cli145

case_dir = os.getenv('HOME')+'/E3SM/Cases/'
# src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC5/' # master @ Oct 18, 2022
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC2' # branch => whannah/mmf/2022-coupled-historical

# clean        = True
# newcase      = True
# config       = True
# build        = True
submit       = True
# continue_run = True


# stop_opt,stop_n,resub,walltime = 'nyears',5, 0,'2:00'
# stop_opt,stop_n,resub,walltime = 'nyears',1, 9-1,'2:00'
stop_opt,stop_n,resub,walltime = 'nyears',1, 10-1,'2:00'


compset   = 'ICRUELM' 

rest_opt,rest_n = 'nyears',1


# ne,npg =  30,2; grid = f'ne{ne}pg{npg}_oECv3'
# res = f'ne{ne}' if npg==0 else  f'ne{ne}pg{npg}'
# grid   = f'{res}_r0125_oRRS18to6v3'
# grid = f'{res}_oECv3'
# grid = f'{res}_r05_oECv3'
ne,npg = 30,2; grid = f'ne{ne}pg{npg}_EC30to60E2r2' # for 01 to match v2 PI control
# if ne==4: grid = f'{res}_r05_oQU480'
# grid = f'{res}_{res}'

# grid = 'r0125_r0125_oRRS18to6v3'
# grid = 'ne120pg2_ne120pg2'


num_years = 20
# stop_date = datetime.datetime(2010, 10, 1)
# stop_date = datetime.datetime(1950, 1, 1)
stop_date = datetime.datetime(1850, 1, 1)
start_date = datetime.datetime(stop_date.year-num_years, stop_date.month, stop_date.day)
stop_date_str = stop_date.strftime("%Y-%m-%d")
start_date_str = start_date.strftime("%Y-%m-%d")

case = f'ELM_spinup.{compset}.{grid}.{num_years}-yr.{stop_date_str}'

clm_opt = ' -bgc sp -clm_start_type arb_ic'

# init_scratch = '/gpfs/alpine/cli115/scratch/hannah6/inputdata'
init_scratch = '/gpfs/alpine/cli115/world-shared/e3sm/inputdata'

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
print('\n  case : '+case+'\n')

# if ne==30 : dtime = 30*60
# if ne==120 : dtime = 5*60
# ncpl = 86400 / dtime


num_nodes = 32
ntasks,nthrds = num_nodes*42,2

#-------------------------------------------------------------------------------
# Namelist setting routine
#-------------------------------------------------------------------------------
def set_namelist_stuff():
   nfile = ''
   nfile = 'user_nl_cam'
   file = open(nfile,'w') 
   file.write(' empty_htapes = .true. \n') 
   
   nfile = 'user_nl_elm'
   file = open(nfile,'w')
   
   file.write(f' fsurdat = \'{init_scratch}/lnd/clm2/surfdata_map/surfdata_ne30pg2_simyr1850_c210402.nc\' \n')
   # file.write(f' check_finidat_fsurdat_consistency = .false. \n')
   # if 'ne' in locals() and 'npg' in locals():
   #    if ne==30 and npg==2: 
   #       file.write(f' fsurdat = \'{init_scratch}/lnd/clm2/surfdata_map/surfdata_ne30pg2_simyr2010_c210402.nc\' \n')
   # if grid=='r0125_r0125_oRRS18to6v3' and '1950' in stop_date_str:
   #    file.write(f' fsurdat = \'{init_scratch}/lnd/clm2/surfdata_map/surfdata_0.125x0.125_simyr1950_c210924.nc\' \n')

   file.close()

#---------------------------------------------------------------------------------------------------
# Create new case
#---------------------------------------------------------------------------------------------------
if newcase : 
   cmd = f'{src_dir}/cime/scripts/create_newcase --case {case_dir}/{case}'
   cmd += f' --compset {compset} --res {grid}'
   cmd += f' --compiler gnu  --pecount {ntasks}x{nthrds} '
   run_cmd(cmd)

   # Change run directory to be next to bld directory
   os.chdir(case_dir+case+'/')
   run_cmd('./xmlchange --file env_run.xml   RUNDIR=\'$CIME_OUTPUT_ROOT/$CASE/run\' ' )
   run_cmd(f'./xmlchange --file env_run.xml   RUN_STARTDATE={start_date_str}' )

   # if grid == 'ne30pg2_ne30pg2':
   #    map_file_lnd2rof = 'cpl/gridmaps/ne30pg2/map_ne30pg2_to_r05_mono.200220.nc'
   #    map_file_rof2lnd = 'cpl/gridmaps/ne30pg2/map_r05_to_ne30pg2_mono.200220.nc'

   # map_file_lnd2rof = f'/global/cscratch1/sd/whannah/e3sm_scratch/init_files//map_ne{ne}pg{npg}_to_r05_mono.20210817.nc'
   # map_file_rof2lnd = f'/global/cscratch1/sd/whannah/e3sm_scratch/init_files//map_r05_to_ne{ne}pg{npg}_mono.20210817.nc'
   
   # run_cmd(f'./xmlchange --file env_run.xml LND2ROF_FMAPNAME={map_file_lnd2rof}' )
   # run_cmd(f'./xmlchange --file env_run.xml ROF2LND_FMAPNAME={map_file_rof2lnd}' )

#---------------------------------------------------------------------------------------------------
# Configure
#---------------------------------------------------------------------------------------------------
os.chdir(case_dir+case+'/')
if config : 
   set_namelist_stuff()
   #----------------------------------------------------------------------------   
   #run_cmd('./xmlchange --file env_build.xml --id MOSART_MODE --val NULL')
   run_cmd(f'./xmlchange --append --file env_run.xml --id ELM_BLDNML_OPTS  --val  \"{clm_opt}\"' )

   #----------------------------------------------------------------------------
   # Set tasks for non-land components   
   cmd = './xmlchange --file env_mach_pes.xml '
   alt_ntask = 42*16
   cmd += f'NTASKS_OCN={alt_ntask},NTASKS_ICE={alt_ntask}'
   cmd += f',NTASKS_ATM={alt_ntask},NTASKS_CPL={alt_ntask}'
   alt_ntask = 42
   cmd += f',NTASKS_ROF={alt_ntask},NTASKS_WAV={alt_ntask},NTASKS_GLC={alt_ntask}'
   cmd += f',NTASKS_ESP=1,NTASKS_IAC=1'
   run_cmd(cmd)

   # Set threads for non-land components
   cmd = './xmlchange --file env_mach_pes.xml '
   alt_nthrds = 1
   cmd += f'NTHRDS_OCN={alt_nthrds},NTHRDS_ICE={alt_nthrds}'
   cmd += f',NTHRDS_ATM={alt_nthrds},NTHRDS_CPL={alt_nthrds}'
   cmd += f',NTHRDS_ROF=1,NTHRDS_WAV=1,NTASKS_GLC=1'
   cmd += f',NTHRDS_ESP=1,NTHRDS_IAC=1'
   run_cmd(cmd)
   #----------------------------------------------------------------------------
   if clean : run_cmd('./case.setup --clean')
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

   # ### Change inputdata from default due to permissions issue
   # if 'init_scratch' in locals(): run_cmd(f'./xmlchange DIN_LOC_ROOT={init_scratch} ')

   set_namelist_stuff()
   #-------------------------------------------------------
   #-------------------------------------------------------
   def xml_check_and_set(file_name,var_name,value):
      if var_name in open(file_name).read(): 
         run_cmd('./xmlchange --file '+file_name+' '+var_name+'='+str(value) )
   #-------------------------------------------------------
   # Set some run-time stuff
   #-------------------------------------------------------
   # if 'ncpl' in locals(): run_cmd(f'./xmlchange ATM_NCPL={str(ncpl)}')
   if 'queue'    in globals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
   if 'stop_opt' in globals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
   if 'stop_n'   in globals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
   if 'resub'    in globals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
   if 'walltime' in globals(): run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
   
   # Restart Frequency
   run_cmd(f'./xmlchange --file env_run.xml  REST_OPTION={rest_opt}')
   run_cmd(f'./xmlchange --file env_run.xml  REST_N={rest_n}')

   xml_check_and_set('env_workflow.xml','CHARGE_ACCOUNT',acct)
   xml_check_and_set('env_workflow.xml','PROJECT',acct)

   # An alternate grid checking threshold is needed for ne120pg2 (still not sure why...)
   # if ne==120 and npg==2 : run_cmd('./xmlchange --file env_run.xml  EPS_AGRID=1e-11' )
   # run_cmd('./xmlchange --file env_run.xml EPS_FRAC=3e-2' ) # default=1e-2

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
print('\n  case : '+case+'\n') 
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
