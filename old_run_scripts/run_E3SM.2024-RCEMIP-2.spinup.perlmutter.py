#!/usr/bin/env python3
#---------------------------------------------------------------------------------------------------
class clr:END,RED,GREEN,MAGENTA,CYAN = '\033[0m','\033[31m','\033[32m','\033[35m','\033[36m'
def run_cmd(cmd): print('\n'+clr.GREEN+cmd+clr.END); os.system(cmd); return
#---------------------------------------------------------------------------------------------------
import os, subprocess as sp
newcase,config,build,clean,submit,continue_run,reset_resub,st_archive = False,False,False,False,False,False,False,False

acct = 'm3312'
src_dir  = os.getenv('HOME')+'/E3SM/E3SM_SRC3' # branch => whannah/atm/rcemip-phase-2

# clean        = True
newcase      = True
config       = True
build        = True
submit       = True
# continue_run = True
### reset_resub  = True

debug_mode = False

queue = 'regular' # regular / debug
# grid,num_nodes = 'ne4pg2_ne4pg2',1 ; queue = 'debug'
grid,num_nodes = 'ne30pg2_ne30pg2',22
# grid,num_nodes = 'ne30pg2_ne30pg2',32

if queue=='debug': 
   # stop_opt,stop_n,resub,walltime = 'nsteps',4,0,'0:10:00' 
   stop_opt,stop_n,resub,walltime = 'ndays',1,0,'0:10:00' 
if queue=='regular': 
   # stop_opt,stop_n,resub,walltime = 'ndays',1,0,'0:10:00' 
   # stop_opt,stop_n,resub,walltime = 'ndays',10,0,'2:00:00' 
   # stop_opt,stop_n,resub,walltime = 'ndays',32,0,'3:00:00'
   stop_opt,stop_n,resub,walltime = 'ndays',42,0,'3:00:00'

compset_list,msst_list,arch_list = [],[],[]
def add_case(compset,msst=None):
   compset_list.append(compset); msst_list.append(msst)
   arch_list.append('GNUGPU' if 'MMF' in compset else 'GNUCPU')

# altered timestep for spin-up
# gcm_dt =  1*60
# gcm_dt = 30*60

add_case('FRCE',295)
# add_case('FRCE',300)
# add_case('FRCE',305)
# add_case('FRCE-MW_295dT1p25')
# add_case('FRCE-MW_300dT0p625')
# add_case('FRCE-MW_300dT1p25')
# add_case('FRCE-MW_300dT2p5')
# add_case('FRCE-MW_305dT1p25')

# add_case('FRCE-MMF1',295)
# add_case('FRCE-MMF1',300)
# add_case('FRCE-MMF1',305)
# add_case('FRCE-MW-MMF1_295dT1p25')
# add_case('FRCE-MW-MMF1_300dT0p625')
# add_case('FRCE-MW-MMF1_300dT1p25')
# add_case('FRCE-MW-MMF1_300dT2p5')
# add_case('FRCE-MW-MMF1_305dT1p25')

use_cosp = False

init_scratch = '/global/cfs/cdirs/m4310/whannah/HICCUP/data/'

# if 'gcm_dt' not in locals(): gcm_dt = None

#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
def main(compset,msst,arch):

   compset_str = compset if msst is None else f'{compset}_{msst}'

   # case_list = ['E3SM','2024-RCEMIP',compset_str]
   # case_list = ['E3SM','2024-RCEMIP-SPINUP',grid,compset_str]
   case_list = ['E3SM','2024-RCEMIP-SPINUP-TEST',grid,compset_str]
   # if gcm_dt is not None: case_list.append(f'GDT_{gcm_dt}')
   if debug_mode: case_list.append('debug')
   case = '.'.join(case_list)

   # print(case); exit()
   #------------------------------------------------------------------------------------------------
   gcm_dt = None
   if grid=='ne4pg2_ne4pg2' and 'MMF' not in compset:
      gcm_dt = 30*60
   #------------------------------------------------------------------------------------------------
   if 'CPU' in arch: max_mpi_per_node,atm_nthrds  = 128,1 ; max_task_per_node = 128
   if 'GPU' in arch: max_mpi_per_node,atm_nthrds  =   4,8 ; max_task_per_node = 32
   atm_ntasks = max_mpi_per_node*num_nodes

   if 'CPU' in arch: case_root = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-cpu/{case}'
   if 'GPU' in arch: case_root = f'/pscratch/sd/w/whannah/e3sm_scratch/pm-gpu/{case}'

   #------------------------------------------------------------------------------------------------
   #------------------------------------------------------------------------------------------------
   print('\n  case : '+case+'\n')
   #------------------------------------------------------------------------------------------------
   # Create new case
   if newcase :
      # Check if directory already exists   
      if os.path.isdir(case_root): exit(f'\n{clr.RED}This case already exists!{clr.END}\n')
      cmd = f'{src_dir}/cime/scripts/create_newcase'
      cmd += f' --case {case}'
      cmd += f' --output-root {case_root} '
      cmd += f' --script-root {case_root}/case_scripts '
      cmd += f' --handle-preexisting-dirs u '
      cmd += f' --compset {compset}'
      cmd += f' --res {grid} '
      if arch=='GNUCPU' : cmd += f' -mach pm-cpu -compiler gnu    -pecount {atm_ntasks}x{atm_nthrds} '
      if arch=='GNUGPU' : cmd += f' -mach pm-gpu -compiler gnugpu -pecount {atm_ntasks}x{atm_nthrds} '
      cmd += f' --project {acct} '
      cmd += f' --walltime {walltime} '
      run_cmd(cmd)
   #------------------------------------------------------------------------------------------------
   os.chdir(f'{case_root}/case_scripts')
   #------------------------------------------------------------------------------------------------
   # Configure
   if config :
      run_cmd(f'./xmlchange EXEROOT={case_root}/bld ')
      run_cmd(f'./xmlchange RUNDIR={case_root}/run ')
      #-------------------------------------------------------
      run_cmd(f'./xmlchange MAX_TASKS_PER_NODE={max_task_per_node} ')
      run_cmd(f'./xmlchange MAX_MPITASKS_PER_NODE={max_mpi_per_node} ')
      #-------------------------------------------------------
      if msst is not None:
         run_cmd(f'./xmlchange DOCN_AQPCONST_VALUE={msst}')
      #-------------------------------------------------------
      # when specifying ncdata, do it here to avoid an error message
      file=open('user_nl_eam','w');file.write(get_atm_nl_opts(compset,gcm_dt));file.close()
      #-------------------------------------------------------
      if use_cosp:
         run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val=\'-cosp\'')
      #-------------------------------------------------------
      # run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -nlev {nlev} \" ')
      # run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val=\'-cosp\'')
      # run_cmd(f'./xmlchange --append --id CAM_CONFIG_OPTS --val \" -crm_nx_rad 1 -crm_ny_rad 1 \" ')
      #-------------------------------------------------------
      run_cmd('./xmlchange PIO_NETCDF_FORMAT=\"64bit_data\" ')
      #-------------------------------------------------------
      if clean : run_cmd('./case.setup --clean')
      run_cmd('./case.setup --reset')
   #------------------------------------------------------------------------------------------------
   # Build
   if build : 
      #-------------------------------------------------------
      if debug_mode: run_cmd('./xmlchange --file env_build.xml --id DEBUG --val TRUE ')
      if clean : run_cmd('./case.build --clean')
      run_cmd('./case.build')
   #------------------------------------------------------------------------------------------------
   # Write the namelist options and submit the run
   if submit : 
      #-------------------------------------------------------
      file=open('user_nl_eam','w');file.write(get_atm_nl_opts(compset,gcm_dt));file.close()
      #-------------------------------------------------------
      if gcm_dt is not None: 
         ncpl = int( 86400 / gcm_dt )
         run_cmd(f'./xmlchange ATM_NCPL={ncpl}')
      if 'queue'    in globals(): run_cmd(f'./xmlchange JOB_QUEUE={queue}')
      if 'walltime' in globals(): run_cmd(f'./xmlchange JOB_WALLCLOCK_TIME={walltime}')
      if 'stop_opt' in globals(): run_cmd(f'./xmlchange STOP_OPTION={stop_opt}')
      if 'stop_n'   in globals(): run_cmd(f'./xmlchange STOP_N={stop_n}')
      # if 'resub' in globals() and not continue_run: run_cmd(f'./xmlchange RESUBMIT={resub}')
      # if 'resub' in globals() and reset_resub: run_cmd(f'./xmlchange RESUBMIT={resub}')
      if 'resub' in globals(): run_cmd(f'./xmlchange RESUBMIT={resub}')
      if 'GPU' in arch: run_cmd(f'./xmlchange CHARGE_ACCOUNT={acct}_g,PROJECT={acct}_g')
      #-------------------------------------------------------
      if     continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=TRUE ')   
      if not continue_run: run_cmd('./xmlchange --file env_run.xml CONTINUE_RUN=FALSE ')
      #-------------------------------------------------------
      run_cmd('./case.submit')
   #------------------------------------------------------------------------------------------------
   # Print the case name again
   print(f'\n  case : {case}\n')
#---------------------------------------------------------------------------------------------------

def get_dt_opts(gcm_dt):
   dt_nl_str = ''
   if gcm_dt is not None: 
      if gcm_dt < 60 :
         dt_nl_str += f'dt_tracer_factor = 1 \n'
         dt_nl_str += f'dt_remap_factor = 1 \n'
         dt_nl_str += f'se_tstep = {gcm_dt} \n'
         dt_nl_str += f'hypervis_subcycle_q = 1 \n'
      if gcm_dt == 1*60 :
         dt_nl_str += f'dt_tracer_factor = 1 \n'
         dt_nl_str += f'dt_remap_factor = 1 \n'
         dt_nl_str += f'se_tstep = 60 \n'
         dt_nl_str += f'hypervis_subcycle_q = 1 \n'
      if gcm_dt == 2*60 :
         dt_nl_str += f'dt_tracer_factor = 1 \n'
         dt_nl_str += f'dt_remap_factor = 1 \n'
         dt_nl_str += f'se_tstep = 60 \n'
         dt_nl_str += f'hypervis_subcycle_q = 1 \n'
      if gcm_dt == 5*60 :
         dt_nl_str += f'dt_tracer_factor = 5 \n'
         dt_nl_str += f'dt_remap_factor = 1 \n'
         dt_nl_str += f'se_tstep = 60 \n'
         dt_nl_str += f'hypervis_subcycle_q = 5 \n'
      if gcm_dt == 10*60 :
         dt_nl_str += f'dt_tracer_factor = 5 \n'
         dt_nl_str += f'dt_remap_factor = 1 \n'
         dt_nl_str += f'se_tstep = 60 \n'
         dt_nl_str += f'hypervis_subcycle_q = 5 \n'
      if gcm_dt == 30*60 :
         dt_nl_str += f'dt_tracer_factor = 6 \n'
         dt_nl_str += f'dt_remap_factor = 1 \n'
         dt_nl_str += f'se_tstep = 300 \n'
         dt_nl_str += f'hypervis_subcycle_q = 6 \n'
      # dt_nl_str += "\n"
   return dt_nl_str
#---------------------------------------------------------------------------------------------------
def get_hist_opts(compset):
   hist_opts = ''
   hist_opts += "empty_htapes = .true. \n"
   hist_opts += "avgflag_pertape = 'A','A','A','I' \n"
   hist_opts += "nhtfrq = 1 \n"
   hist_opts += "mfilt  = 1 \n"
   hist_opts += "nhtfrq = -1,-1,-1,-6 \n"
   hist_opts += "mfilt  = 24,24,24,4 \n"
   # 2D 1 hour average
   hist_opts += "fincl1 = 'TS','PSL','PS'"
   hist_opts +=         ",'PRECT','PRECC','SHFLX','LHFLX'"
   hist_opts +=         ",'TMQ','TMQS','TGCLDLWP','TGCLDIWP'"
   hist_opts +=         ",'FLDS','FLNS'"       # sfc LW
   hist_opts +=         ",'FSDS','FSNS'"       # sfc SW
   hist_opts +=         ",'FLDSC','FLNSC'"     # sfc LW clearsky
   hist_opts +=         ",'FSDSC','FSNSC'"     # sfc SW clearsky
   hist_opts +=         ",'FLUTOA','FLNTOA'"   # toa LW
   hist_opts +=         ",'FSUTOA','FSNTOA'"   # toa SW
   hist_opts +=         ",'FLUTOAC','FLNTOAC'" # toa LW clearsky
   hist_opts +=         ",'FSUTOAC','FSNTOAC'" # toa SW clearsky
   hist_opts +=         ",'CLDTOT','CLDLOW','CLDMED','CLDHGH'"
   hist_opts +=         ",'OMEGA500'"
   hist_opts +=         ",'UBOT','VBOT','TBOT','QBOT'"
   hist_opts +=         ",'U10','TREFHT'"
   hist_opts += "\n"
   # 3D 1 hour average
   hist_opts += "fincl2 = 'PS','T','Q','Z3','RELHUM'"
   hist_opts +=         ",'CLDLIQ','CLDICE','CLOUD'"
   hist_opts +=         ",'U','V','OMEGA'"
   hist_opts +=         ",'QRS','QRL'"
   hist_opts += "\n"
   if use_cosp:
      # 2D 1 hour average (COSP output)
      hist_opts += "fincl3 = 'FISCCP1_COSP','MEANCLDALB_ISCCP','CLDTOT_ISCCP','MEANPTOP_ISCCP'"
      # hist_opts +=         ",'CLD_MISR','CLDTOT_CAL'"
      # hist_opts +=         ",'CLMODIS','CLTMODIS','CLWMODIS','CLIMODIS'"
      # hist_opts +=         ",'CLDHGH_CAL','CLDLOW_CAL','CLDMED_CAL'"
   hist_opts += "\n"
   # 3D 6-hr instant
   hist_opts += "fincl4 = 'PS','T','Q','Z3','RELHUM'"
   hist_opts +=         ",'CLDLIQ','CLDICE','CLOUD'"
   hist_opts +=         ",'U','V','OMEGA'"
   hist_opts +=         ",'QRS','QRL'"
   hist_opts +=         ",'QRSC','QRLC'"
   hist_opts +=         ",'DTCOND'"
   if 'MMF' in compset:
      hist_opts +=      ",'CRM_QPC','CRM_QPI'"
      hist_opts +=      ",'MMF_MCUP'"           # convective mass flux
   else:
      hist_opts +=      ",'CMFMCDZM'"           # convective mass flux
   if use_cosp:
      hist_opts +=      ",'FISCCP1_COSP'"
   hist_opts += "\n"
   return hist_opts

# 'OMEGA','U','V','Z3','T','Q','RELHUM'

# vars = "FSNTOA,FLUT,FSNT,FLNT,FSNS,FLNS,SHFLX,QFLX,TAUX,TAUY,PRECC,PRECL,PRECSC,PRECSL,TS,TREFHT,CLDTOT_CAL,CLDHGH_CAL,CLDMED_CAL,CLDLOW_CAL,U,ICEFRAC,LANDFRAC,OCNFRAC,AODALL,AODDUST,AODVIS,PS"

# vars = "FSNTOA,FLUT,FSNT,FLNT,FSNS,FLNS,SHFLX,QFLX,TAUX,TAUY,PRECC,
# PRECL,PRECSC,PRECSL,TS,TREFHT,CLDTOT,CLDHGH,CLDMED,CLDLOW,U,ICEFRAC,
# LANDFRAC,OCNFRAC,Mass_bc,Mass_dst,Mass_mom,Mass_ncl,Mass_pom,Mass_so4,Mass_soa,
# AODALL,AODBC,AODDUST,AODPOM,AODSO4,AODSOA,AODSS,AODVIS,PS"
#---------------------------------------------------------------------------------------------------
def get_atm_nl_opts(compset,gcm_dt):
   dt_opts   = get_dt_opts(gcm_dt)
   hist_opts = get_hist_opts(compset)
   nl_opts = ''
   if use_cosp:
      nl_opts += "cosp_isccp = .true. \n"
      # nl_opts += "cosp_lite = .true. \n"
   nl_opts += "inithist = 'NONE' \n"
   nl_opts += hist_opts
   nl_opts += dt_opts
   return nl_opts
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
if __name__ == '__main__':

   for n in range(len(compset_list)):
      # print('-'*80)
      main( compset_list[n], msst_list[n], arch_list[n] )
#---------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------
