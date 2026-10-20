#!/usr/bin/env python
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END) ; os.system(cmd); return
#---------------------------------------------------------------------------------------------------
opt_list = []
def add_case( **kwargs ):
   case_opts = {}
   for k, val in kwargs.items(): case_opts[k] = val
   opt_list.append(case_opts)
#---------------------------------------------------------------------------------------------------
''' Notes
# interpolating land IC
LND_IC_ROOT=/lustre/orion/cli115/world-shared/e3sm/inputdata/lnd/clm2/initdata
LND_IC_SRC=${LND_IC_ROOT}/20240104.I2010CRUELM.ne256pg2.elm.r.2016-08-01-00000.nc
LND_IC_DST=${LND_IC_ROOT}/20240104.I2010CRUELM.ne128pg2.elm.r.2016-08-01-00000.nc
interpinic -i 

#-------------------------------------------------------------------------------
# vertical remap
DST_VERT=/lustre/orion/cli115/proj-shared/hannah6/files_vert/SCREAM_L128_v3.6_c20251112.cdf5.nc
INIT_ROOT=/lustre/orion/cli115/world-shared/e3sm/inputdata/atm/scream/init
SRC_FILE=${INIT_ROOT}/screami_ne256np4L128_ifs-20200120_20220914.nc
DST_FILE=${INIT_ROOT}/screami_ne256np4L128_ifs-20200120_20220914.L128_v3.6.nc

SRC_FILE=${INIT_ROOT}/screami_ne256np4L128_era5-20190801-topoadjx6t_20230620.nc
DST_FILE=${INIT_ROOT}/screami_ne256np4L128_era5-20190801-topoadjx6t_20230620.L128_v3.6.nc

ncremap -4 --ps_nm=ps --vrt_fl=${DST_VERT} --in_fl=${SRC_FILE} --out_fl=${DST_FILE}

# # This doesn't work - same error as above without the -4 option
# ncatted -O -a _FillValue,,o,d,1.0e36 ${DST_FILE} ${DST_FILE}.tmp
# ncks -5 ${DST_FILE}.tmp ${DST_FILE}.tmp.cdf5
# mv ${DST_FILE}.cdf5 ${DST_FILE}

ncatted -O -a _FillValue,ps,d,, ${DST_FILE} ${DST_FILE}.tmp
ncks -5 ${DST_FILE}.tmp ${DST_FILE}.tmp.cdf5
mv ${DST_FILE}.tmp.cdf5 ${DST_FILE}
rm ${DST_FILE}.tmp

'''
#---------------------------------------------------------------------------------------------------
import os, datetime, subprocess as sp
from shutil import copy2
newcase,config,build,clean,submit,continue_run = False,False,False,False,False,False

acct = 'cli115'
top_dir  = os.getenv('HOME')+'/E3SM/'
# src_dir  = f'{top_dir}/E3SM_SRC1/' # branch => master @ Jul 21 2026 - 656bc155a9f990052e4b60b7f73a786ad978cdea
# src_dir  = f'{top_dir}/E3SM_SRC0/' # branch => master @ Aug 18 2026 - 11d24263fbe8326820c1ffb4f9673578163b7c9b
src_dir  = f'{top_dir}/E3SM_SRC2/' # branch => whannah/eamxx/support-new-L128

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True

# stop_opt,stop_n,resub,walltime = 'nsteps',10,0,'0:30:00'
stop_opt,stop_n,resub,walltime = 'ndays',10,0,'1:00:00'

#---------------------------------------------------------------------------------------------------

# kwargs = {'prefix':'2026-L128-TEST-00','compset':'F2010-SCREAMv1'}
# add_case(**kwargs, num_nodes=1,   grid='ne4pg2_ne4pg2')
# add_case(**kwargs, num_nodes=2,   grid='ne30pg2_ne30pg2')
# add_case(**kwargs, num_nodes=2,   grid='ne32pg2_ne32pg2')
# add_case(**kwargs, num_nodes=8,   grid='ne64pg2_ne64pg2')
# add_case(**kwargs, num_nodes=16,  grid='ne120pg2_ne120pg2')
# add_case(**kwargs, num_nodes=16,  grid='ne128pg2_ne128pg2')
# add_case(**kwargs, num_nodes=64,  grid='ne256pg2_ne256pg2')
# add_case(**kwargs, num_nodes=128, grid='ne512pg2_ne512pg2')
# add_case(**kwargs, num_nodes=256, grid='ne1024pg2_ne1024pg2')

kwargs = {'prefix':'2026-L128-TEST-00','compset':'F2010xx-ZM-CICE'}
add_case(**kwargs, num_nodes=16,  grid='ne128pg2_ne128pg2')
add_case(**kwargs, num_nodes=64,  grid='ne256pg2_ne256pg2')

#---------------------------------------------------------------------------------------------------
def get_grid_name(opts):
   grid_name = opts['grid']
   for ne in [4,30,32,64,128,256,512,1024]:
      if f'ne{ne}pg2_' in opts['grid']:
         grid_name = f'ne{ne}pg2'
   return grid_name
#---------------------------------------------------------------------------------------------------
def get_case_name(opts):
   case_list = ['E3SM']
   for key,val in opts.items(): 
      if key in ['prefix','compset','arch']: case_list.append(val)
      elif key in ['grid']:         case_list.append(get_grid_name(opts))
      elif key in ['debug']:        continue
      elif key in ['num_nodes']:    case_list.append(f'NN_{val}')
      elif key in ['num_tasks']:    case_list.append(f'NT_{val}')
      elif key=='cosp' and opts.get('cosp',False):  case_list.append('COSP')
      elif key in ['vgrid_name']:   case_list.append(f'{val}')
      elif key in ['vgrid_file']:   continue
      elif key in ['init_file']:    continue
      else:
         if isinstance(val, str):
            case_list.append(f'{key}_{val}')
         else:
            case_list.append(f'{key}_{val:g}')
   if opts.get('debug',False): case_list.append('debug')
   case = '.'.join(case_list)
   # clean up the exponential numbers in the case name
   for i in range(1,9+1): case = case.replace(f'e+0{i}',f'e{i}')
   return case
#---------------------------------------------------------------------------------------------------
def main(opts):

   case = get_case_name(opts)

   print(f'\n  case : {case}\n')
   #------------------------------------------------------------------------------------------------
   # return
   #------------------------------------------------------------------------------------------------
   print(f' clean        : {clean}')
   print(f' newcase      : {newcase}')
   print(f' config       : {config}')
   print(f' build        : {build}')
   print(f' submit       : {submit}')
   print(f' continue_run : {continue_run}')
   #------------------------------------------------------------------------------------------------
   if 'num_nodes' in opts and 'num_tasks' in opts:
      raise ValueError('cannot specify both num_nodes and num_tasks!')
   if 'num_nodes' not in opts and 'num_tasks' not in opts:
      raise ValueError('you must specify either num_nodes of num_tasks!')
   #----------------------------------------------------------------------------
   machine,compiler = 'frontier','craygnu-mphipcc'
   case_root = f'/lustre/orion/cli115/proj-shared/hannah6/e3sm_scratch/{case}'
   atm_ntasks = 8*opts['num_nodes'] # 8 GPU per node
   #------------------------------------------------------------------------------------------------
   # Create new case
   if newcase :
      if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
      cmd = f'{src_dir}/cime/scripts/create_newcase --case {case} --project {acct}'
      cmd += f' --output-root {case_root} --script-root {case_root}/case_scripts'
      cmd += f' --compset {opts["compset"]} --res {opts["grid"]} --handle-preexisting-dirs u'
      cmd += f' --pecount {atm_ntasks}x1 --machine={machine} --compiler={compiler} '
      run_cmd(cmd)
   #------------------------------------------------------------------------------------------------
   os.chdir(f'{case_root}/case_scripts')
   #------------------------------------------------------------------------------------------------
   if config : 
      run_cmd(f'./xmlchange EXEROOT={case_root}/bld ')
      run_cmd(f'./xmlchange RUNDIR={case_root}/run ')
      run_cmd('./case.setup --reset')
   #------------------------------------------------------------------------------------------------
   if build : 
      if opts.get('debug',False): run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
      # if clean : 
      #    run_cmd('./case.build --clean')
      #    run_cmd('./case.build --clean ice')
      run_cmd('./case.build')
   #------------------------------------------------------------------------------------------------
   if submit :
      if 'ne128pg2' in opts['grid']:
         run_cmd(f'./atmchange -b se_tstep=56.25 ')
         run_cmd(f'./atmchange -b dt_tracer_factor=8 ')
         run_cmd(f'./atmchange -b hypervis_subcycle_q=8 ')
         run_cmd(f'./atmchange -b semi_lagrange_trajectory_nsubstep=2 ')
      #-------------------------------------------------------------------------
      # use updated SPA data file
      DIN_LOC_ROOT = '/lustre/orion/cli115/world-shared/e3sm/inputdata'
      run_cmd(f'./atmchange -b spa_data_file="{DIN_LOC_ROOT}/atm/scream/init/spa_v3.LR.F2010.2011-2025.c_20240405.nc"')
      #-------------------------------------------------------------------------
      # run_cmd(f'./xmlchange ATM_NCPL={int(86400/dtime)}')
      if 'stop_opt' in globals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
      if 'stop_n'   in globals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
      if 'resub'    in globals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
      if 'queue'    in globals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
      if 'walltime' in globals(): run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
      run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct},PROJECT={acct}')
      if     continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=TRUE ')   
      if not continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=FALSE ')
      #-------------------------------------------------------------------------
      run_cmd('./case.submit')
   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {case}\n') 
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':
   for n in range(len(opt_list)):
      main( opt_list[n] )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
